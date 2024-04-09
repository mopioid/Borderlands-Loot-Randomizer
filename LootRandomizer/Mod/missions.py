from __future__ import annotations

from unrealsdk import Log, FindObject, FindAll, GetEngine, KeepAlive #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct #type: ignore

from . import defines, options, items, locations
from .defines import Tag, get_pawns, get_missiontracker
from .defines import construct_object, construct_behaviorsequence_behavior
from .locations import Location, Dropper, MapDropper, RegistrantDropper

from typing import Callable, Dict, Generator, List, Optional, Sequence, Set


_mission_registry: Dict[str, Set[Mission]] = dict()

def _all_missions() -> Generator[Mission, None, None]:
    for registry in _mission_registry.values():
        for mission in registry:
            if not (mission.tags & Tag.Excluded):
                yield mission


playthrough: int = -1

def PlaythroughChanged() -> None:
    global playthrough

    new_playthrough = defines.get_pc().GetCurrentPlaythrough()
    if playthrough == new_playthrough:
        return
    
    Log("PlaythroughChanged (actually)")

    playthrough = new_playthrough

    if playthrough == 2:
        for mission in _all_missions():
            mission.reward.ExperienceRewardPercentage.BaseValueScaleConstant = mission.reward_xp_scale
    else:
        for mission in _all_missions():
            mission.reward.ExperienceRewardPercentage.BaseValueScaleConstant = 0
    

def _SetPawnLocation(caller: UObject, function: UFunction, params: FStruct) -> bool:
    PlaythroughChanged()
    return True


def Enable() -> None:
    PlaythroughChanged()

    RunHook("WillowGame.WillowPlayerController.TryPromptForFastForward", "LootRandomizer", lambda c,f,p: False)

    RunHook("WillowGame.WillowPlayerController.AcceptMission", "LootRandomizer", _AcceptMission)
    RunHook("WillowGame.WillowPlayerController.ServerCompleteMission", "LootRandomizer", _CompleteMission)

    RunHook("WillowGame.WillowMissionItem.MissionDenyPickup", "LootRandomizer", _MissionDenyPickup)
    RunHook("Engine.WillowInventory.PickupAssociated", "LootRandomizer", _PickupAssociated)

    RunHook("WillowGame.WillowPlayerController.ClientSetPawnLocation", "LootRandomizer.missions", _SetPawnLocation)


def Disable() -> None:
    global playthrough
    playthrough = -1

    RemoveHook("WillowGame.WillowPlayerController.TryPromptForFastForward", "LootRandomizer")

    RemoveHook("WillowGame.WillowPlayerController.AcceptMission", "LootRandomizer")
    RemoveHook("WillowGame.WillowPlayerController.ServerCompleteMission", "LootRandomizer")

    RemoveHook("Engine.WillowInventory.PickupAssociated", "LootRandomizer")
    RemoveHook("WillowGame.WillowMissionItem.MissionDenyPickup", "LootRandomizer")

    RemoveHook("WillowGame.WillowPlayerController.ClientSetPawnLocation", "LootRandomizer.missions")


def _AcceptMission(caller: UObject, function: UFunction, params: FStruct) -> bool:
    missiondef = params.Mission
    registry = _mission_registry.get(UObject.PathName(missiondef))
    if not registry:
        return True

    delegates: List[Callable[[], None]] = []
    for mission in registry:
        for dropper in mission.droppers:
            if isinstance(dropper, MissionStatusDelegate):
                delegates.append(dropper.accepted)

    def play_kickoff(missiondef=missiondef):
        tracker = get_missiontracker()
        tracker.PlayKickoff(missiondef)
        tracker.SetKickoffHeard(missiondef)

    defines.do_next_tick(play_kickoff, *delegates)
    return True


def _CompleteMission(caller: UObject, function: UFunction, params: FStruct) -> bool:
    missiondef = params.Mission
    registry = _mission_registry.get(UObject.PathName(missiondef))
    if not registry:
        return True

    pc = defines.get_pc()

    playthrough = pc.GetCurrentPlaythrough()
    mission_index = pc.NativeGetMissionIndex(missiondef)
    mission_data = pc.MissionPlaythroughs[playthrough].MissionList[mission_index]
    mission_level = mission_data.GameStage
    alt_reward, _ = missiondef.ShouldGrantAlternateReward(tuple(mission_data.ObjectivesProgress))

    def revert():
        mission.reward.RewardItemPools = ()

    delegates = [revert]
    mission: Optional[Mission] = None

    for registered_mission in registry:
        for dropper in registered_mission.droppers:
            if isinstance(dropper, MissionStatusDelegate):
                delegates.append(dropper.completed)

        if registered_mission.alt == alt_reward:
            mission = registered_mission

    defines.do_next_tick(*delegates)

    if not (mission and mission.item):
        return True

    pool = mission.prepare_pools(1)[0]
    mission.reward.RewardItemPools = (pool,)

    if mission.item == items.DudItem:
        return True

    for pri in GetEngine().GetCurrentWorldInfo().GRI.PRIArray:
        pc = pri.Owner

        bonuses = len(mission.rarities)
        if pc is defines.get_pc():
            bonuses -= 1
        if not bonuses:
            continue

        if (pc is defines.get_pc()) and (not options.RewardsTrainingSeen.CurrentValue):
            def training() -> None:
                defines.show_dialog("Multiple Rewards", (
                    "The mission you just completed takes longer than average to complete. As a "
                    "reward, a bonus instance of its loot item has been added to your backpack."
                ), 5)
                options.RewardsTrainingSeen.CurrentValue = True
                options.SaveSettings()
            defines.do_next_tick(training)

        def loot_callback(item: UObject, pc=pc) -> None:
            definition_data = item.DefinitionData
            definition_data.ManufacturerGradeIndex = mission_level
            definition_data.GameStage = mission_level
            definition_data = defines.convert_struct(definition_data)

            if definition_data[0].Class.Name == "WeaponTypeDefinition":
                pc.GetPawnInventoryManager().ClientAddWeaponToBackpack(definition_data, 1)
            else:
                pc.GetPawnInventoryManager().ClientAddItemToBackpack(definition_data, 1, 1)

        for _ in range(bonuses):
            defines.spawn_item(mission.item.pool, pc, loot_callback)

    return True


def _MissionDenyPickup(caller: UObject, function: UFunction, params: FStruct) -> bool:
    itemdef = caller.GetInventoryDefinition()
    if not itemdef:
        return True

    inventories = MissionInventory.Registries.get(UObject.PathName(itemdef))
    if not inventories:
        return True

    mission = next(iter(inventories)).location
    if not isinstance(mission, Mission):
        raise Exception(f"Found mission inventory dropper for non-mission {mission}")

    if get_missiontracker().GetMissionStatus(mission.uobject) not in (0, 4):
        return True

    # Don't judge me; this is literally how the game does it.
    for pickup in FindAll("WillowPickup"):
        if pickup.Inventory and pickup.Inventory.GetInventoryDefinition() == itemdef:
            return True

    return False


def _PickupAssociated(caller: UObject, function: UFunction, params: FStruct) -> bool:
    itemdef = caller.GetInventoryDefinition()
    if not (itemdef and UObject.PathName(itemdef) in MissionInventory.Registries):
        return True
    
    def enable_pickup(pickup = params.Pickup):
        pickup.SetPickupability(True)
        GetEngine().GetCurrentWorldInfo().GRI.MissionTracker.RegisterMissionDirector(pickup)
    defines.do_next_tick(enable_pickup)
    return True


class Mission(Location):
    path: str
    alt: bool
    block_weapon: bool

    uobject: UObject

    repeatable: bool
    mission_weapon: UObject

    reward_items: Sequence[UObject]
    reward_pools: Sequence[UObject]
    reward_xp_scale: Optional[int] = None

    def __init__(
        self,
        name: str,
        path: str,
        *droppers: Dropper,
        alt: bool = False,
        block_weapon: bool = True,
        tags: Tag = Tag(0),
        rarities: Optional[Sequence[int]] = None
    ) -> None:
        self.path = path; self.alt = alt; self.block_weapon = block_weapon

        if not tags & defines.MissionTags:
            tags |= Tag.ShortMission
        if not tags & defines.ContentTags:
            tags |= Tag.BaseGame

        if not rarities:
            rarities = [100]
            if tags & Tag.LongMission:     rarities += (100,)
            if tags & Tag.VeryLongMission: rarities += (100,100,100)
            if tags & Tag.RaidEnemy:       rarities += (100,100,100)

        super().__init__(name, *droppers, tags=tags, rarities=rarities)

    @property
    def reward(self) -> FStruct:
        return self.uobject.AlternativeReward if self.alt else self.uobject.Reward

    def enable(self) -> None:
        super().enable()

        registry = _mission_registry.setdefault(self.path, set())
        registry.add(self)

        self.uobject = FindObject("MissionDefinition", self.path)

        self.reward_items = tuple(self.reward.RewardItems)
        for item in self.reward_items:
            KeepAlive(item)
        self.reward.RewardItems = ()

        self.reward_pools = tuple(self.reward.RewardItemPools)
        for pool in self.reward_pools:
            KeepAlive(pool)
        self.reward.RewardItemPools = ()

        if self.block_weapon:
            self.mission_weapon = self.uobject.MissionWeapon
            KeepAlive(self.mission_weapon)
            self.uobject.MissionWeapon = None

        if self.tags & Tag.Excluded:
            return

        if not self.alt:
            self.repeatable = self.uobject.bRepeatable
            self.uobject.bRepeatable = True

        self.reward_xp_scale = self.reward.ExperienceRewardPercentage.BaseValueScaleConstant


    def disable(self) -> None:
        super().disable()

        registry = _mission_registry.get(self.path)
        if registry:
            registry.discard(self)
            if not registry:
                del _mission_registry[self.path]

        self.reward.RewardItems = self.reward_items
        self.reward.RewardItemPools = self.reward_pools

        if self.block_weapon:
            self.uobject.MissionWeapon = self.mission_weapon

        if self.tags & Tag.Excluded:
            return

        if not self.alt:
            self.uobject.bRepeatable = self.repeatable

        self.reward.ExperienceRewardPercentage.BaseValueScaleConstant = self.reward_xp_scale


    def __str__(self) -> str:
        return f"Mission: {self.name}"


class MissionInventory(RegistrantDropper):
    Registries = dict()


class MissionStatusDelegate:
    def accepted(self) -> None:
        pass

    def completed(self) -> None:
        pass


class MissionObject(MissionStatusDelegate, MapDropper):
    location: Mission

    path: str

    def __init__(self, path: str, *map_names: str) -> None:
        self.path = path
        super().__init__(*map_names)

    def apply(self) -> UObject:
        obj = FindObject("WillowInteractiveObject", self.path)
        if obj:
            obj.SetUsability(True, 0)
            obj.SetMissionDirectivesUsability(1)
            get_missiontracker().RegisterMissionDirector(obj)
        return obj
    
    def entered_map(self) -> None:
        if get_missiontracker().GetMissionStatus(self.location.uobject) != 0:
            self.apply()

    def completed(self) -> None:
        self.apply()


class MissionPickup(MissionObject):
    def apply(self) -> UObject:
        spawner = FindObject("WillowMissionPickupSpawner", self.path)
        # TODO: tick until successful when client
        if spawner:
            spawner.SetPickupStatus(True)
            if spawner.MissionPickup:
                spawner.MissionPickup.SetPickupability(True)
                get_missiontracker().RegisterMissionDirector(spawner.MissionPickup)
        return spawner


class MissionGiver(MissionObject):
    path: str
    begins: bool
    ends: bool
    mission: Optional[str]

    def __init__(self, path: str, begins: bool, ends: bool, *map_names: str) -> None:
        self.begins = begins; self.ends = ends
        super().__init__(path, *map_names)

    def apply(self) -> UObject:
        giver = FindObject("MissionDirectivesDefinition", self.path)
        if not giver:
            return

        matched_directive = False
        for directive in giver.MissionDirectives:
            if directive.MissionDefinition == self.location.uobject:
                directive.bBeginsMission = self.begins
                directive.bEndsMission = self.ends
                matched_directive = True
                break

        if not matched_directive:
            directives = defines.convert_struct(giver.MissionDirectives)
            directives.append((self.location.uobject, self.begins, self.ends, 0))
            giver.MissionDirectives = directives

        get_missiontracker().RegisterMissionDirector(giver)
        return giver


class DocMercy(MissionGiver):
    def __init__(self) -> None:
        super().__init__("Frost_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_413.MissionDirectivesDefinition_0", False, False, "Frost_P")
    
    def apply(self) -> UObject:
        giver = super().apply()
        get_missiontracker().UnregisterMissionDirector(giver)
        return giver


class Loader1340(MapDropper):
    location: Mission

    def __init__(self) -> None:
        super().__init__("dam_p")

    def entered_map(self) -> None:
        if get_missiontracker().GetMissionStatus(self.location.uobject) == 0:
            return

        toggle = FindObject("SeqAct_Toggle", "Dam_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Loader1340.SeqAct_Toggle_1")

        loaded0 = FindObject("SeqEvent_LevelLoaded", "Dam_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Loader1340.SeqEvent_LevelLoaded_0")
        loaded0.OutputLinks[0].Links[0].LinkedOp = toggle

        loaded1 = FindObject("SeqEvent_LevelLoaded", "Dam_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Loader1340.SeqEvent_LevelLoaded_1")
        loaded1.OutputLinks[0].Links[0].LinkedOp = toggle


class WillTheBandit(MapDropper):
    def __init__(self) -> None:
        super().__init__("tundraexpress_p")

    def entered_map(self) -> None:
        toggle = FindObject("SeqAct_Toggle", "TundraExpress_Combat.TheWorld:PersistentLevel.Main_Sequence.NoHardFeelings.SeqAct_Toggle_0")

        loaded0 = FindObject("SeqEvent_LevelLoaded", "TundraExpress_Combat.TheWorld:PersistentLevel.Main_Sequence.NoHardFeelings.SeqEvent_LevelLoaded_0")
        loaded0.OutputLinks[0].Links[0].LinkedOp = toggle
        loaded0.OutputLinks[0].Links[0].InputLinkIdx = 0

        loaded1 = FindObject("SeqEvent_LevelLoaded", "TundraExpress_Combat.TheWorld:PersistentLevel.Main_Sequence.NoHardFeelings.SeqEvent_LevelLoaded_1")
        loaded1.OutputLinks[0].Links[0].LinkedOp = toggle
        loaded1.OutputLinks[0].Links[0].InputLinkIdx = 0


class McShooty(MissionStatusDelegate, MapDropper):
    location: Mission

    def __init__(self) -> None:
        super().__init__("Grass_Cliffs_P")

    def accepted(self) -> None:
        for pawn in get_pawns():
            if pawn.bIsDead and pawn.AIClass and pawn.AIClass.Name == "CharClass_Shootyface":
                pawn.bHidden = True
                pawn.CollisionType = 1

    def entered_map(self) -> None:
        destroyreal = FindObject("WillowSeqEvent_MissionRemoteEvent", "Grass_Cliffs_Dynamic.TheWorld:PersistentLevel.Main_Sequence.ShootMeInTheFace.WillowSeqEvent_MissionRemoteEvent_2")
        destroyreal.OutputLinks[0].Links = ()

        shooty_bpd = FindObject("BehaviorProviderDefinition", "GD_Shootyface.Character.CharClass_Shootyface:BehaviorProviderDefinition_0")
        shooty_bpd.BehaviorSequences[1].EventData2[0].OutputLinks.ArrayIndexAndLength = 327681
        shooty_bpd.BehaviorSequences[2].EventData2[0].OutputLinks.ArrayIndexAndLength = 0
# TODO: prevent mcshooty from despawning after completion?

class BFFs(MapDropper):
    def __init__(self) -> None:
        super().__init__("SanctuaryAir_P")

    def entered_map(self) -> None:
        toggle0 = FindObject("SeqAct_Toggle", "SanctuaryAir_Side.TheWorld:PersistentLevel.Main_Sequence.BFFs.SeqAct_Toggle_0")
        toggle1 = FindObject("SeqAct_Toggle", "SanctuaryAir_Side.TheWorld:PersistentLevel.Main_Sequence.BFFs.SeqAct_Toggle_1")

        loaded1 = FindObject("SeqEvent_LevelLoaded", "SanctuaryAir_Side.TheWorld:PersistentLevel.Main_Sequence.BFFs.SeqEvent_LevelLoaded_1")
        loaded1.OutputLinks[0].Links[0].LinkedOp = toggle1
        loaded1.OutputLinks[0].Links[1].LinkedOp = toggle0

        loaded2 = FindObject("SeqEvent_LevelLoaded", "SanctuaryAir_Side.TheWorld:PersistentLevel.Main_Sequence.BFFs.SeqEvent_LevelLoaded_2")
        loaded2.OutputLinks[0].Links[0].LinkedOp = toggle1

        loaded3 = FindObject("SeqEvent_LevelLoaded", "SanctuaryAir_Side.TheWorld:PersistentLevel.Main_Sequence.BFFs.SeqEvent_LevelLoaded_3")
        loaded3.OutputLinks[0].Links[0].LinkedOp = toggle0

        aiscripted = FindObject("WillowSeqAct_AIScripted", "SanctuaryAir_Side.TheWorld:PersistentLevel.Main_Sequence.BFFs.WillowSeqAct_AIScripted_0")
        aiscripted.InputLinks[0].bDisabled = True

        gamestage_region = FindObject("WillowRegionDefinition", "GD_GameStages.Zone3.Sanctuary_C")
        for path in (
            "SanctuaryAir_Side.TheWorld:PersistentLevel.WillowPopulationOpportunityPoint_1",
            "SanctuaryAir_Side.TheWorld:PersistentLevel.WillowPopulationOpportunityPoint_6",
            "SanctuaryAir_Side.TheWorld:PersistentLevel.WillowPopulationOpportunityPoint_7",
            "SanctuaryAir_Side.TheWorld:PersistentLevel.WillowPopulationOpportunityPoint_8",
        ):
            FindObject("WillowPopulationOpportunityPoint", path).GameStageRegion = gamestage_region


class PoeticLicense(MapDropper):
    def __init__(self) -> None:
        super().__init__("SanctuaryAir_P")

    def entered_map(self) -> None:
        daisy_den = FindObject("PopulationOpportunityDen", "SanctuaryAir_Dynamic.TheWorld:PersistentLevel.PopulationOpportunityDen_2")
        if not daisy_den:
            return
        daisy_den.GameStageRegion = FindObject("WillowRegionDefinition", "GD_GameStages.Zone2.Cliffs_A")

        daisy_ai = FindObject("AIBehaviorProviderDefinition", "GD_Daisy.Character.AIDef_Daisy:AIBehaviorProviderDefinition_1")
        daisy_ai.BehaviorSequences[2].BehaviorData2[11].Behavior = construct_object("Behavior_Kill", daisy_ai)
        daisy_ai.BehaviorSequences[5].BehaviorData2[2].OutputLinks.ArrayIndexAndLength = 1

        seq_objective = FindObject("SeqAct_ApplyBehavior", "SanctuaryAir_Dynamic.TheWorld:PersistentLevel.Main_Sequence.PoeticLicense.SeqAct_ApplyBehavior_1")
        timetodie = FindObject("SeqEvent_RemoteEvent", "SanctuaryAir_Dynamic.TheWorld:PersistentLevel.Main_Sequence.PoeticLicense.SeqEvent_RemoteEvent_2")
        timetodie.OutputLinks[0].Links = ((seq_objective, 0),)


class WrittenByTheVictor(MapDropper):
    def __init__(self) -> None:
        super().__init__("HyperionCity_P")

    def entered_map(self) -> None:
        missionevent = FindObject("WillowSeqEvent_MissionRemoteEvent", "HyperionCity_Dynamic.TheWorld:PersistentLevel.Main_Sequence.WrittenByVictor.WillowSeqEvent_MissionRemoteEvent_1")
        missionevent.OutputLinks[0].Links = ()


class ARealBoy(MapDropper):
    def __init__(self) -> None:
        super().__init__("Ash_P")

    def entered_map(self) -> None:
        mal_ai = FindObject("BehaviorProviderDefinition", "GD_PinocchioBot.Character.CharClass_PinocchioBot:BehaviorProviderDefinition_84")
        mal_ai.BehaviorSequences[12].EventData2[0].OutputLinks.ArrayIndexAndLength = 0


class GreatEscape(MissionStatusDelegate, MapDropper):
    location: Mission

    def __init__(self) -> None:
        super().__init__("CraterLake_P")

    def completed(self) -> None:
        self.location.uobject.bRepeatable = False

    def entered_map(self) -> None:
        self.location.uobject.bRepeatable = True

        pawn = GetEngine().GetCurrentWorldInfo().PawnList
        while pawn:
            if pawn.AIClass and pawn.AIClass.Name == "CharClass_Ulysses":
                get_missiontracker().RegisterMissionDirector(pawn)
                break
            pawn = pawn.NextPawn

        ulysses_loaded = FindObject("SeqEvent_LevelLoaded", "CraterLake_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Ulysess.SeqEvent_LevelLoaded_0")
        ulysses_loaded.OutputLinks[0].Links = ()

        ulysses_savestate = FindObject("SeqEvent_RemoteEvent", "CraterLake_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Ulysess.SeqEvent_RemoteEvent_1")
        ulysses_savestate.OutputLinks[0].Links = ()


class MessageInABottle(MapDropper, MissionStatusDelegate):
    location: Mission

    path: Optional[str]

    def __init__(self, path: Optional[str], map_name: str) -> None:
        self.path = path
        super().__init__(map_name)

    def accepted(self) -> None:
        for chest in FindAll("WillowInteractiveObject"):
            if UObject.PathName(chest.InteractiveObjectDefinition) == "GD_Orchid_SM_Message_Data.MO_Orchid_XMarksTheSpot":
                directive = (self.location.uobject, False, True)
                chest.AddMissionDirective(directive, True)


    def entered_map(self) -> None:
        bottle_bpd = FindObject("BehaviorProviderDefinition", "GD_Orchid_SM_Message_Data.MessageBottle.MO_Orchid_MessageBottle:BehaviorProviderDefinition_3")
        bottle_active = FindObject("Behavior_ChangeRemoteBehaviorSequenceState", "GD_Orchid_Plot.M_Orchid_PlotMission01:Behavior_ChangeRemoteBehaviorSequenceState_6")

        bottle_bpd.BehaviorSequences[1].BehaviorData2[0].Behavior = bottle_active
        bottle_bpd.BehaviorSequences[1].BehaviorData2[0].OutputLinks.ArrayIndexAndLength = 0

        if self.path:
            chest_state = FindObject("BehaviorSequenceEnableByMission", self.path)
            chest_state.MissionStatesToLinkTo.bComplete = False


class RollInsight(MissionGiver):
    def apply(self) -> UObject:
        directives = super().apply()

        die = FindObject("WillowInteractiveObject", "Village_Mission.TheWorld:PersistentLevel.WillowInteractiveObject_297")
        handle = (die.ConsumerHandle.PID,)
        bpd = die.InteractiveObjectDefinition.BehaviorProviderDefinition

        kernel = FindObject("BehaviorKernel", "GearboxFramework.Default__BehaviorKernel")
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Complete", 2)
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "TurnIn", 1)

        die.SetMissionDirectivesUsability(1)
        get_missiontracker().RegisterMissionDirector(die)

        return directives


class TreeHugger(MapDropper):
    def __init__(self) -> None:
        super().__init__("Dark_Forest_P")

    def entered_map(self) -> None:
        for pawn in get_pawns():
            if pawn.AIClass and pawn.AIClass.Name == "CharClass_Aster_Treant_TreeHuggerNPC":
                handle = (pawn.ConsumerHandle.PID,)
                bpd = pawn.AIClass.BehaviorProviderDefinition
                kernel = FindObject("BehaviorKernel", "GearboxFramework.Default__BehaviorKernel")

                enable = bpd.BehaviorSequences[1].CustomEnableCondition
                enable.EnableConditions = (enable.EnableConditions[0],)
                kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "DuringMission", 2)
                break


class LostSouls(MissionGiver):
    def apply(self) -> UObject:
        directives = super().apply()
        for pawn in get_pawns():
            if pawn.MissionDirectives == directives:
                handle = (pawn.ConsumerHandle.PID,)
                bpd = pawn.AIClass.AIDef.BehaviorProviderDefinition
                kernel = FindObject("BehaviorKernel", "GearboxFramework.Default__BehaviorKernel")
                kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Mission", 1)
                pawn.SetUsable(True, None, 0)
                get_missiontracker().RegisterMissionDirector(pawn)

    def entered_map(self) -> None:
        if get_missiontracker().GetMissionStatus(self.location.uobject) == 4:
            skel_den = FindObject("PopulationOpportunityDen", "Dead_Forest_Mission.TheWorld:PersistentLevel.PopulationOpportunityDen_19")
            skel_den.IsEnabled = True
            knight_den = FindObject("PopulationOpportunityDen", "Dead_Forest_Mission.TheWorld:PersistentLevel.PopulationOpportunityDen_13")
            knight_den.IsEnabled = False


class MyDeadBrother(MapDropper):
    location: Mission

    def __init__(self) -> None:
        super().__init__("Dungeon_P")

    def entered_map(self) -> None:
        if get_missiontracker().GetMissionStatus(self.location.uobject) != 4:
            return

        simon_enabled = FindObject("BehaviorSequenceEnableByMission", "GD_Wizard_DeadBrotherSimon_Proto2.Character.CharClass_Wizard_DeadBrotherSimon_Proto2:BehaviorProviderDefinition_5.BehaviorSequenceEnableByMission_9")
        simon_enabled.MissionStatesToLinkTo.bComplete = True

        simon_talking = FindObject("BehaviorSequenceEnableByMission", "GD_Wizard_DeadBrotherSimon_Proto2.Character.CharClass_Wizard_DeadBrotherSimon_Proto2:BehaviorProviderDefinition_5.BehaviorSequenceEnableByMission_7")
        simon_talking.MissionStatesToLinkTo.bComplete = False

        simon_bpd = FindObject("BehaviorProviderDefinition", "GD_Wizard_DeadBrotherSimon_Proto2.Character.CharClass_Wizard_DeadBrotherSimon_Proto2:BehaviorProviderDefinition_5")

        simon_bpd.BehaviorSequences[4].BehaviorData2[1].Behavior = construct_behaviorsequence_behavior(
            "GD_Wizard_DeadBrotherSimon_Proto2", "Character", "CharClass_Wizard_DeadBrotherSimon_Proto2", "BehaviorProviderDefinition_5",
            sequence="TurnInSimon", outer=simon_bpd
        )

        simon_den = FindObject("PopulationOpportunityDen", "Dungeon_Mission.TheWorld:PersistentLevel.PopulationOpportunityDen_68")
        simon_den.IsEnabled = True


class OddestCouple(MissionObject):
    def apply(self) -> UObject:
        door = super().apply()
        handle = (door.ConsumerHandle.PID,)
        bpd = door.InteractiveObjectDefinition.BehaviorProviderDefinition

        kernel = FindObject("BehaviorKernel", "GearboxFramework.Default__BehaviorKernel")
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "S020_Brain", 1)
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "S020_TurnIn", 1)


class Sirentology(MapDropper):
    def __init__(self) -> None:
        super().__init__("BackBurner_P")

    def entered_map(self) -> None:
        for pawn in get_pawns():
            if pawn.AIClass and pawn.AIClass.Name == "CharClass_mone_GD_Lilith":
                handle = (pawn.ConsumerHandle.PID,)
                ai_bpd = pawn.AIClass.AIDef.BehaviorProviderDefinition
                kernel = FindObject("BehaviorKernel", "GearboxFramework.Default__BehaviorKernel")

                ai_bpd.BehaviorSequences[23].CustomEnableCondition.bComplete = True
                kernel.ChangeBehaviorSequenceActivationStatus(handle, ai_bpd, "S050_GiveMission", 1)
                break


class EchoesOfThePast(MissionObject):
    def apply(self) -> UObject:
        echo = super().apply()
        handle = (echo.ConsumerHandle.PID,)
        bpd = echo.InteractiveObjectDefinition.BehaviorProviderDefinition

        kernel = FindObject("BehaviorKernel", "GearboxFramework.Default__BehaviorKernel")
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "S080_MissionGiver", 1)


class GrandmaStoryRaid(MapDropper):
    def __init__(self) -> None:
        super().__init__("Hunger_P")

    def entered_map(self) -> None:
        granma_ai = FindObject("AIBehaviorProviderDefinition", "GD_Allium_TorgueGranma.Character.AIDef_Torgue:AIBehaviorProviderDefinition_0")
        granma_ai.BehaviorSequences[1].EventData2[0].OutputLinks.ArrayIndexAndLength = 655361
        granma_ai.BehaviorSequences[1].EventData2[3].OutputLinks.ArrayIndexAndLength = 655361


"""
TODO
delete non-UVHM xp when enabling mod
make ulysses splat give bonus reward instance
co-op crashes in Village_P (from Roll Insight?)
"""
