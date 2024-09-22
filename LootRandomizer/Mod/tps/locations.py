from unrealsdk import Log, FindAll, FindObject, KeepAlive
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct

from ..defines import *

from .. import locations

from ..locations import Behavior, MapDropper
from ..enemies import Enemy, Pawn
from ..missions import Mission, MissionDefinition, MissionDefinitionAlt
from ..missions import MissionDropper, MissionStatusDelegate, MissionPickup
from ..missions import MissionGiver, MissionObject, ObjectiveKillInfo
from ..other import Other, Attachment, PositionalChest

from typing import Any, Dict, List, Optional, Sequence, Union


class WorldUniques(MapDropper):
    paths = ("*",)
    blacklists: Dict[UObject, Sequence[UObject]]

    def enable(self) -> None:
        super().enable()

        self.blacklists = dict()

        blacklist_list: Dict[str, Sequence[str]] = {
            "GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_04_Rare": (
                "gd_cork_weap_assaultrifle.A_Weapons_Unique.AR_Vladof_3_OldPainful",
            ),
            "GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_04_Rare": (
                "GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Torgue_3_JackOCannon",
                "GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_Boomacorn",
            ),
            "GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_04_Rare": (
                "GD_Cork_Weap_SniperRifles.A_Weapons_Unique.Sniper_Vladof_3_TheMachine",
            ),
        }
        for pool_path, blacklist_paths in blacklist_list.items():
            pool = FindObject("ItemPoolDefinition", pool_path)
            if not pool:
                raise Exception(
                    f"Could not find blacklisted world item pool {pool_path}"
                )

            blacklist: List[UObject] = []
            for blacklist_path in blacklist_paths:
                blacklist_item = FindObject(
                    "WeaponBalanceDefinition", blacklist_path
                )
                if not blacklist_item:
                    raise Exception(
                        f"Could not find blacklisted world item {blacklist_path}"
                    )
                KeepAlive(blacklist_item)
                blacklist.append(blacklist_item)

            self.blacklists[pool] = tuple(blacklist)

    def entered_map(self) -> None:
        for pool, blacklist in self.blacklists.items():
            pool.BalancedItems = tuple(
                convert_struct(balanced_item)
                for balanced_item in pool.BalancedItems
                if balanced_item.InvBalanceDefinition not in blacklist
            )


class LastRequests(MissionDropper, MapDropper):
    paths = ("Deadsurface_P",)

    def entered_map(self) -> None:
        tom = FindObject(
            "WillowInteractiveObject",
            "Deadsurface_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_5",
        )
        if not tom:
            raise Exception("Could not locate Tom for Last Requests")

        kernel = get_behaviorkernel()
        handle = (tom.ConsumerHandle.PID,)
        bpd = tom.InteractiveObjectDefinition.BehaviorProviderDefinition

        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "Disable", 2
        )
        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "Default", 1
        )


class FriskedCorpse(MissionDropper, MapDropper):
    corpse: Optional[str]

    def __init__(self, map_name: str, corpse: str) -> None:
        super().__init__(map_name)
        self.corpse = corpse

    def entered_map(self) -> None:
        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            if UObject.PathName(caller) != self.corpse:
                return True

            mission = self.location.mission
            if not mission:
                raise Exception(
                    f"No mission for corpse for {self.location.name}"
                )

            if mission.current_status is not Mission.Status.Active:
                return True

            spawn_loot(
                self.location.prepare_pools(),
                mission.mission_definition.uobject,
                convert_struct(caller.Location),
            )
            return True

        RunHook(
            "WillowGame.WillowInteractiveObject.UsedBy",
            f"LootRandomizer.{id(self)}",
            hook,
        )

    def exited_map(self) -> None:
        RemoveHook(
            "WillowGame.WillowInteractiveObject.UsedBy",
            f"LootRandomizer.{id(self)}",
        )


class Dick(MapDropper):
    paths = ("Deadsurface_P",)

    def entered_map(self) -> None:
        bpd = FindObject(
            "BehaviorProviderDefinition",
            "GD_Co_LastRequests.M_LastRequests:BehaviorProviderDefinition_0",
        )
        if not bpd:
            raise Exception("Could not locate BPD for calling Nel a dick")

        output_links = bpd.BehaviorSequences[0].ConsolidatedOutputLinkData
        output_links[0].ActivateDelay = 11.25
        output_links[1].ActivateDelay = 11.25

        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            if (
                UObject.PathName(caller)
                != "GD_Co_LastRequests.M_LastRequests:Behavior_AddMissionDirectives_2"
            ):
                return True

            for pawn in get_pawns():
                if pawn.AIClass.Name == "CharClass_Nel":
                    break
            else:
                raise Exception("Could not find Nel for calling Nel a dick")

            location = (
                pawn.Location.X - 20,
                pawn.Location.Y + 20,
                pawn.Location.Z - 50,
            )
            spawn_loot(
                self.location.prepare_pools(), pawn, location, (-370, 354, -10)
            )

            RemoveHook(
                "WillowGame.Behavior_AddMissionDirectives.ApplyBehaviorToContext",
                f"LootRandomizer.{id(self)}",
            )
            return True

        RunHook(
            "WillowGame.Behavior_AddMissionDirectives.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}",
            hook,
        )

    def exited_map(self) -> None:
        RemoveHook(
            "WillowGame.Behavior_AddMissionDirectives.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}",
        )


class TorgueO(MapDropper):
    paths = ("Moonsurface_P",)

    def entered_map(self) -> None:
        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            if not (
                caller.AIClass
                and caller.AIClass.Name == "CharClass_UniqueCharger"
                and params.InstigatedBy
                and params.InstigatedBy.Class.Name == "WillowPlayerController"
            ):
                return True

            behavior = FindObject(
                "Behavior_RemoteCustomEvent",
                "GD_Cork_Weap_Pistol.FiringModes.Bullet_Pistol_Maliwan_MoxxisProbe:Behavior_RemoteCustomEvent_3",
            )
            if not behavior:
                raise Exception("Could not find Probe behavior")

            behavior.ApplyBehaviorToContext(
                caller, (), None, params.InstigatedBy, None, ()
            )
            return True

        RunHook(
            "WillowGame.WillowAIPawn.TakeDamage",
            f"LootRandomizer.{id(self)}",
            hook,
        )

    def exited_map(self) -> None:
        RemoveHook(
            "WillowGame.WillowAIPawn.TakeDamage", f"LootRandomizer.{id(self)}"
        )


class SwordInStone(MapDropper):
    paths = ("StantonsLiver_P",)

    def entered_map(self) -> None:
        bpd = FindObject(
            "BehaviorProviderDefinition",
            "GD_Co_EasterEggs.Excalibastard.InteractiveObject_Excalibastard:BehaviorProviderDefinition_0",
        )
        if not bpd:
            raise Exception("Could not find BPD for Sword In The Stone")

        event_data = bpd.BehaviorSequences[0].EventData2[0]
        event_data.OutputLinks.ArrayIndexAndLength = 327681


class Swagman(Pawn):
    map_name: str

    def __init__(self, map_name: str) -> None:
        self.map_name = map_name.casefold()
        super().__init__("PawnBalance_ScavWastelandWalker")

    def should_inject(self, pawn: UObject) -> bool:
        return locations.map_name == self.map_name


class ToArms(MapDropper):
    paths = ("Moon_P",)

    objective: UObject
    count_advancements: Dict[int, UObject]

    def enable(self) -> None:
        super().enable()
        objective = FindObject(
            "MissionObjectiveDefinition",
            "GD_Co_ToArms.M_Co_ToArms:DonateWeapons10",
        )
        adv1 = FindObject(
            "Behavior_AdvanceObjectiveSet",
            "GD_Co_ToArms.M_Co_ToArms:Behavior_AdvanceObjectiveSet_243",
        )
        adv2 = FindObject(
            "Behavior_AdvanceObjectiveSet",
            "GD_Co_ToArms.M_Co_ToArms:Behavior_AdvanceObjectiveSet_250",
        )
        adv3 = FindObject(
            "Behavior_AdvanceObjectiveSet",
            "GD_Co_ToArms.M_Co_ToArms:Behavior_AdvanceObjectiveSet_255",
        )
        adv4 = FindObject(
            "Behavior_AdvanceObjectiveSet",
            "GD_Co_ToArms.M_Co_ToArms:Behavior_AdvanceObjectiveSet_254",
        )
        adv5 = FindObject(
            "Behavior_AdvanceObjectiveSet",
            "GD_Co_ToArms.M_Co_ToArms:Behavior_AdvanceObjectiveSet_252",
        )

        if not (objective and adv1 and adv2 and adv3 and adv4 and adv5):
            raise Exception("Could not locate mission objective for To Arms")

        self.objective = objective
        self.objective.ObjectiveCount = 5

        self.count_advancements = {1: adv1, 2: adv2, 3: adv3, 4: adv4, 5: adv5}

    def entered_map(self) -> None:
        def open_hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            caller.MailBoxStorage.ChestSlots = 1
            return True

        RunHook(
            "WillowGame.MailBoxGFxMovie.extInitMainPanel",
            f"LootRandomizer.{id(self)}",
            open_hook,
        )

        def deposit_hook(
            caller: UObject, _f: UFunction, params: FStruct
        ) -> bool:
            if (
                UObject.PathName(caller)
                != "GD_Co_ToArms.M_Co_ToArms:Behavior_MissionRemoteEvent_392"
            ):
                return True

            count = get_missiontracker().GetObjectiveCount(self.objective)
            advancement = self.count_advancements.get(count)
            if not advancement:
                raise Exception("Unexpected donation count for To Arms")

            advancement.ApplyBehaviorToContext(
                params.ContextObject,
                (),
                params.SelfObject,
                params.MyInstigatorObject,
                params.OtherEventParticipantObject,
                (),
            )

            return True

        RunHook(
            "WillowGame.Behavior_MissionRemoteEvent.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}",
            deposit_hook,
        )

    def exited_map(self) -> None:
        RemoveHook(
            "WillowGame.MailBoxGFxMovie.extInitMainPanel",
            f"LootRandomizer.{id(self)}",
        )
        RemoveHook(
            "WillowGame.Behavior_MissionRemoteEvent.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}",
        )

    def disable(self) -> None:
        self.objective.ObjectiveCount = 50


class PopRacing(MapDropper):
    paths = ("Moon_P",)

    def entered_map(self) -> None:
        loaded1 = FindObject(
            "SeqEvent_LevelLoaded",
            "Moon_SideMissions.TheWorld:PersistentLevel.Main_Sequence.PopRacing.SeqEvent_LevelLoaded_1",
        )
        loaded6 = FindObject(
            "SeqEvent_LevelLoaded",
            "Moon_SideMissions.TheWorld:PersistentLevel.Main_Sequence.PopRacing.SeqEvent_LevelLoaded_6",
        )
        if not (loaded1 and loaded6):
            raise Exception(
                "Could not locate loading sequences for Pop Racing"
            )

        loaded1.OutputLinks[0].Links = ()
        loaded6.OutputLinks[0].Links = ()


class Zapped1(MissionDropper, MapDropper):
    paths = ("Moon_P",)

    def entered_map(self) -> None:
        if self.location.current_status not in (
            Mission.Status.NotStarted,
            Mission.Status.Complete,
        ):
            return

        box = FindObject(
            "WillowInteractiveObject",
            "Moon_SideMissions.TheWorld:PersistentLevel.WillowInteractiveObject_114",
        )
        if not box:
            raise Exception("Could not locate box for Zapped 1.0")

        kernel = get_behaviorkernel()
        handle = (box.ConsumerHandle.PID,)
        bpd = box.InteractiveObjectDefinition.BehaviorProviderDefinition

        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "AcceptedMission", 2
        )
        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "MissionAvailable", 1
        )


class Boomshakalaka(MissionStatusDelegate, MapDropper):
    paths = ("Outlands_P2",)

    def entered_map(self) -> None:
        if self.location.current_status is Mission.Status.Active:
            self.accepted()

    def set_hoop_collision(self, collision: int) -> None:
        hoop = FindObject(
            "WillowInteractiveObject",
            "Outlands_SideMissions2.TheWorld:PersistentLevel.WillowInteractiveObject_0",
        )
        if not hoop:
            raise Exception("Could not locate hoop for Boomshakalaka")

        hoop.Behavior_ChangeCollision(collision)
        for comp in hoop.AllComponents:
            if comp.Class.Name == "StaticMeshComponent":
                comp.Behavior_ChangeCollision(collision)

    def accepted(self) -> None:
        self.set_hoop_collision(1)  # COLLIDE_NoCollision

    def completed(self) -> None:
        self.set_hoop_collision(2)  # COLLIDE_BlockAll


class DunksWatson(MapDropper):
    paths = ("Outlands_P2",)

    def entered_map(self) -> None:
        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            if (
                UObject.PathName(caller)
                != "Outlands_SideMissions2.TheWorld:PersistentLevel.Main_Sequence.Boomshakalaka.SeqAct_ApplyBehavior_4.Behavior_RemoteCustomEvent_0"
            ):
                return True

            mission = self.location.mission
            if not mission:
                raise Exception("No mission for Dunks Watson")

            for pawn in get_pawns():
                if pawn.AIClass.Name == "CharClass_Superballa":
                    break
            else:
                raise Exception("Could not locate Dunks Watson")

            spawn_loot(
                self.location.prepare_pools(),
                mission.mission_definition.uobject,
                (-14540.578125, 106299.593750, 8647.15625),
                (0, 0, -4800),
            )
            return True

        RunHook(
            "WillowGame.Behavior_RemoteCustomEvent.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}",
            hook,
        )

    def exited_map(self) -> None:
        RemoveHook(
            "WillowGame.Behavior_RemoteCustomEvent.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}",
        )


class SpaceSlam(MissionStatusDelegate, MapDropper):
    paths = ("Outlands_P2",)

    def apply(self) -> None:
        for pawn in get_pawns():
            if pawn.AIClass and pawn.AIClass.Name == "CharClass_Tog":
                pawn.SetUsable(True, None, 0)
                break
        else:
            raise Exception("Could not locate Tog for Space Slam")

    def entered_map(self) -> None:
        self.apply()

    def completed(self) -> None:
        self.apply()


class DAHLTraining(MapDropper):
    paths = ("MoonSlaughter_P",)

    def entered_map(self) -> None:
        loaded = FindObject(
            "SeqEvent_LevelLoaded",
            "MoonSlaughter_Combat.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_LevelLoaded_2",
        )
        tr4nu = FindObject(
            "WillowInteractiveObject",
            "MoonSlaughter_Combat.TheWorld:PersistentLevel.WillowInteractiveObject_1",
        )

        if not (loaded and tr4nu):
            raise Exception(
                "Could not locate objects for DAHL Combat Training"
            )

        loaded.OutputLinks[0].Links = ()

        kernel = get_behaviorkernel()
        handle = (tr4nu.ConsumerHandle.PID,)
        bpd = tr4nu.InteractiveObjectDefinition.BehaviorProviderDefinition

        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "Disabled", 2
        )
        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "Enabled", 1
        )


class PoopDeck(MapDropper):
    paths = ("Wreck_P",)

    def entered_map(self) -> None:
        mission = FindObject("MissionDefinition", "GD_Co_Chapter05.M_Cork_WreckMain")
        poop = FindObject("PopulationOpportunityDen", "Wreck_Combat2.TheWorld:PersistentLevel.PopulationOpportunityDen_9")
        seq = FindObject("SeqEvent_PopulatedActor", "Wreck_Combat2.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_PopulatedActor_0")
        if not (mission and poop and seq):
            raise Exception("Could not locate objects for Poop Deck")

        mission_status = get_missiontracker().GetMissionStatus(mission)
        if mission_status == Mission.Status.Complete:
            seq.OutputLinks = ()
            poop.SetEnabledStatus(True)


class FreeLaunch(MissionDropper, MapDropper):
    paths = ("Moon_P",)

    def entered_map(self) -> None:
        if self.location.current_status != Mission.Status.Active:
            invisible = FindObject("SeqAct_ApplyBehavior", "Moon_SideMissions.TheWorld:PersistentLevel.Main_Sequence.NoSuchTHingAsAFreeLaunch.SeqAct_ApplyBehavior_0")
            if not invisible:
                raise Exception("Could not locate Cosmo invisibility for Free Launch")
            invisible.Behaviors = ()


class Cosmo(MapDropper):
    paths = ("Moon_p",)

    def entered_map(self) -> None:
        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            mission = self.location.mission
            if not mission:
                raise Exception("No mission for Cosmo")
            
            if not (
                params.MissionDef is mission.mission_definition.uobject
                and params.FanFareType == 6  # EMFT_MissionReadyToTurnIn
            ):
                return True

            for pawn in get_pawns():
                if pawn.AIClass and pawn.AIClass.Name == "CharClass_Cosmo":
                    break
            else:
                raise Exception("Could not locate Cosmo for Cosmo")
            
            spawn_loot(
                self.location.prepare_pools(),
                mission.mission_definition.uobject,
                convert_struct(pawn.Location)
            )
            return True
        RunHook(
            "WillowGame.WillowPlayerController.ClientDoMissionStatusFanfare",
            f"LootRandomizer.{id(self)}",
            hook,
        )

    def exited_map(self) -> None:
        RemoveHook(
            "WillowGame.WillowPlayerController.ClientDoMissionStatusFanfare",
            f"LootRandomizer.{id(self)}",
        )


class NeilParsec(MapDropper):
    paths = ("Moon_P",)

    def entered_map(self) -> None:
        freelaunch = FindObject("MissionDefinition", "GD_Cork_Rocketeering.M_Rocketeering")
        if not (freelaunch):
            raise Exception("Could not locate mission for Neil Parsec")

        mission_status = get_missiontracker().GetMissionStatus(freelaunch)
        if mission_status == Mission.Status.Complete:
            den = FindObject("PopulationOpportunityDen", "Moon_Combat.TheWorld:PersistentLevel.PopulationOpportunityDen_13")
            neil = FindObject("WillowAIPawn", "GD_Co_LuzzFightbeer.Character.Pawn_LuzzFightbeer")
            if not (den and neil):
                raise Exception("Could not locate objects for Neil Parsec")

            neil.ActorSpawnCost = 0
            den.IsEnabled = True
            den.GameStageRegion = freelaunch.GameStageRegion


class Abbot(MapDropper):
    paths = ("Moon_P",)

    def entered_map(self) -> None:
        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            if (
                UObject.PathName(params.MissionObjective) !=
                "GD_Cork_AnotherPickle.M_Cork_AnotherPickle:SlapAbbotAgain"
            ):
                return True

            for pawn in get_pawns():
                if pawn.AIClass and pawn.AIClass.Name == "CharClass_Burner":
                    break
            else:
                raise Exception("Could not locate Abbot for Abbot")

            mission = self.location.mission
            if not mission:
                raise Exception("Could not location mission for Abbot")

            spawn_loot(
                self.location.prepare_pools(),
                mission.mission_definition.uobject,
                convert_struct(pawn.Location)
            )
            return True
        RunHook(
            "WillowGame.WillowPlayerController.UpdateMissionObjective",
            f"LootRandomizer.{id(self)}",
            hook,
        )

    def exited_map(self) -> None:
        RemoveHook(
            "WillowGame.WillowPlayerController.UpdateMissionObjective",
            f"LootRandomizer.{id(self)}",
        )


class MoxxiBox(MapDropper):
    paths = ("Spaceport_P",)

    def entered_map(self) -> None:
        mission = FindObject("MissionDefinition", "GD_Cork_HeliosFoothold_Plot.M_Cork_HeliosFoothold")
        if not mission:
            raise Exception("Could not location mission for Moxxi's Toy Box")
        
        mission_status = get_missiontracker().GetMissionStatus(mission)
        if mission_status == Mission.Status.NotStarted:
            return

        loaded11 = FindObject("SeqEvent_LevelLoaded", "Spaceport_M_Chp4.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_LevelLoaded_11")
        loaded12 = FindObject("SeqEvent_LevelLoaded", "Spaceport_M_Chp4.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_LevelLoaded_12")
        box = FindObject("WillowPopulationOpportunityPoint", "Spaceport_M_Chp4.TheWorld:PersistentLevel.WillowPopulationOpportunityPoint_0")
        if not (loaded11 and loaded12 and box):
            raise Exception("Could not locate objects for Moxxi's Toy Box")

        loaded11.OutputLinks[0].Links[0].LinkedOp = None
        loaded12.OutputLinks[0].Links[0].LinkedOp = None
        box.IsEnabled = True


class SubLevel13(MapDropper):
    paths = ("Sublevel13_P",)

    def entered_map(self) -> None:
        keypad = FindObject("WillowInteractiveObject", "Sublevel13_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_0")
        if not keypad:
            raise Exception("Could not locate keypad for Sub-Level 13")

        handle = (keypad.ConsumerHandle.PID,)
        bpd = keypad.InteractiveObjectDefinition.BehaviorProviderDefinition
        kernel = get_behaviorkernel()

        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Usable", 1)


class ChefVoyage(MissionDropper, MapDropper):
    paths = ("Moon_P",)

    def entered_map(self) -> None:
        if self.location.current_status != Mission.Status.Complete:
            return

        loaded16 = FindObject("SeqEvent_LevelLoaded", "Moon_SideMissions.TheWorld:PersistentLevel.Main_Sequence.VoyageOfCaptainChef.SeqEvent_LevelLoaded_16")
        if not loaded16:
            raise Exception("Could not locate loading for Voyage Of Captain Chef")

        for pawn in get_pawns():
            if pawn.AIClass and pawn.AIClass.Name == "CharClass_CaptainChef":
                break
        else:
            raise Exception("Could not locate Chef for Voyage Of Captain Chef")

        loaded16.OutputLinks[0].Links = ()
        
        handle = (pawn.ConsumerHandle.PID,)
        bpd = pawn.AIClass.AIDef.BehaviorProviderDefinition
        kernel = get_behaviorkernel()

        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Invisible", 2)
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "DisableUse", 2)

        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "AI", 1)
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Brain", 1)


class Bob(MapDropper):
    paths = ("centralterminal_p",)
        # TODO: BUFF BAHB

    def entered_map(self) -> None:
        pass
        # bob = FindObject("WillowAIPawn", "GD_DahlMarine_CentralTerm.Character.Pawn_DahlMarine_CentralTerm")
        # event47 = FindObject("SeqEvent_RemoteEvent", "CentralTerminal_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Map_Combat.SeqEvent_RemoteEvent_47")
        # event79 = FindObject("SeqEvent_RemoteEvent", "CentralTerminal_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Map_Combat.SeqEvent_RemoteEvent_79")
        # encounter = FindObject("WillowPopulationEncounter", "CentralTerminal_Dynamic.TheWorld:PersistentLevel.WillowPopulationEncounter_1")

        # bobmix = FindObject("PopulationOpportunityDen", "CentralTerminal_Dynamic.TheWorld:PersistentLevel.PopulationOpportunityDen_10")
        # dahlmix = FindObject("PopulationOpportunityDen", "CentralTerminal_Dynamic.TheWorld:PersistentLevel.PopulationOpportunityDen_14")
        # othermix = FindObject("PopulationOpportunityDen", "CentralTerminal_Dynamic.TheWorld:PersistentLevel.PopulationOpportunityDen_18")
        # dahlmix.PopulationDef = bobmix.PopulationDef
        # othermix.PopulationDef = bobmix.PopulationDef

        # bob.ActorSpawnCost = 0
        # event47.OutputLinks[0].Links = ()
        # event79.OutputLinks[0].Links = ()
        # encounter.IsEnabled = True


class FreshAir(MapDropper):
    paths = ("RandDFacility_P",)

    def entered_map(self) -> None:
        den = FindObject("PopulationOpportunityDen", "RandDFacility_Mission.TheWorld:PersistentLevel.PopulationOpportunityDen_5")
        if not den:
            raise Exception("Could not locate den for Fresh Air")
        den.IsEnabled = True


class DrMinte(MapDropper):
    paths = ("RandDFacility_P",)

    def entered_map(self) -> None:
        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            if not (
                caller.Class.Name == "WillowAIPawn" and
                caller.AIClass and
                caller.AIClass.Name == "CharClass_DrMinteNPC"
            ):
                return True

            mission = self.location.mission
            if not mission:
                raise Exception("Could not locate mission for Dr. Minte")

            window = FindObject(
                "WillowInteractiveObject",
                "RandDFacility_Mission.TheWorld:PersistentLevel.WillowInteractiveObject_29"
            )
            if not window:
                raise Exception("Could not locate window for Dr. Minte")

            window.Behavior_ChangeCollision(1)  # COLLIDE_NoCollision
            for comp in window.AllComponents:
                if comp.Class.Name == "StaticMeshComponent":
                    comp.Behavior_ChangeCollision(1)  # COLLIDE_NoCollision

            spawn_loot(
                self.location.prepare_pools(),
                mission.mission_definition.uobject,
                (3271, 13342, 2416),
                (-4670, -1582, -1200),
            )
            return True

        RunHook(
            "Engine.Actor.OnDestroy",
            f"LootRandomizer.{id(self)}",
            hook,
        )

    def exited_map(self) -> None:
        RemoveHook(
            "Engine.Actor.OnDestroy",
            f"LootRandomizer.{id(self)}",
        )


class Defector(MapDropper):
    paths = ("Moon_P",)

    def entered_map(self) -> None:
        mission = self.location.mission
        if not mission:
            raise Exception("Could not locate mission for Defector")
        
        if mission.current_status == Mission.Status.Active:
            spawn_loot(
                self.location.prepare_pools(),
                mission.mission_definition.uobject,
                (-19404, 39254, -2074)
            )


class SpaceHurps(MissionGiver):
    def apply(self) -> Union[UObject, None]:
        giver = super().apply()
        enable = FindObject("BehaviorSequenceEnableByMission", "GD_Cork_TroubleWithSpaceH_Data.InteractiveObjects.IO_SpaceHurpTurnIn:BehaviorProviderDefinition_2.BehaviorSequenceEnableByMission_4")
        if not (giver and giver.Outer and enable):
            raise Exception("Could not locate objects for Space Hurps")

        kernel = get_behaviorkernel()
        bpd = giver.Outer.InteractiveObjectDefinition.BehaviorProviderDefinition
        handle = (giver.Outer.ConsumerHandle.PID,)

        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "TroubleTurnIn", 1)
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "TroubleECHO", 1)

        enable.MissionStatesToLinkTo.bReadyToTurnIn = True
        enable.MissionStatesToLinkTo.bComplete = True


class DontGetCocky(MissionObject):
    def apply(self) -> Union[UObject, None]:
        console = super().apply()
        enable = FindObject("BehaviorSequenceEnableByMission", "GD_GenericSwitches.InteractiveObjects.IO_ComputerConsole_C:BehaviorProviderDefinition_1.BehaviorSequenceEnableByMission_8")
        applybehavior7 = FindObject("SeqAct_ApplyBehavior", "InnerHull_Mission.TheWorld:PersistentLevel.Main_Sequence.DontGetCocky.SeqAct_ApplyBehavior_7")
        activatesequence8 = FindObject("WillowSeqAct_ActivateInstancedBehaviorSequences", "InnerHull_Mission.TheWorld:PersistentLevel.Main_Sequence.DontGetCocky.WillowSeqAct_ActivateInstancedBehaviorSequences_8")
        if not (console and enable and applybehavior7 and activatesequence8):
            raise Exception("Could not locate console for Dont Get Cocky")

        applybehavior7.VariableLinks[0].LinkedVariables = ()
        activatesequence8.VariableLinks[0].LinkedVariables = ()

        kernel = get_behaviorkernel()
        bpd = console.InteractiveObjectDefinition.BehaviorProviderDefinition
        handle = (console.ConsumerHandle.PID,)
        
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Offline", 2)
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Enabled", 1)
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "DontGetCocky_Director_Failed", 1)

        enable.MissionStatesToLinkTo.bReadyToTurnIn = True
        enable.MissionStatesToLinkTo.bComplete = True


class TheseAreTheBots(MissionDropper, MapDropper):
    paths = ("Digsite_P",)

    def entered_map(self) -> None:
        loaded17 = FindObject("SeqEvent_LevelLoaded", "Digsite_SideMissions.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_LevelLoaded_17")
        loaded21 = FindObject("SeqEvent_LevelLoaded", "Digsite_SideMissions.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_LevelLoaded_21")
        if not (loaded17 and loaded21):
            raise Exception("Could not locate loading for These Are The Bots")

        loaded17.OutputLinks[0].Links = ()
        loaded21.OutputLinks[0].Links = ()

        for pawn in get_pawns():
            if pawn.AIClass and pawn.AIClass.Name == "CharClass_L3PO":
                break
        else:
            raise Exception("Could not locate ICU-P for These Are The Bots")

        pawn.SetUsable(True, None, 0)


class ChefReturn(MissionDropper, MapDropper):
    paths = ("Digsite_P",)

    def entered_map(self) -> None:
        if self.location.current_status != Mission.Status.Complete:
            return

        loaded24 = FindObject("SeqEvent_LevelLoaded", "Digsite_SideMissions.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_LevelLoaded_30")
        if not loaded24:
            raise Exception("Could not locate loading for Return Of Captain Chef")

        for pawn in get_pawns():
            if pawn.AIClass and pawn.AIClass.Name == "CharClass_CaptainChefZone4":
                break
        else:
            raise Exception("Could not locate Chef for Return Of Captain Chef")

        loaded24.OutputLinks[0].Links = ()
        
        handle = (pawn.ConsumerHandle.PID,)
        bpd = pawn.AIClass.AIDef.BehaviorProviderDefinition
        kernel = get_behaviorkernel()

        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Invisible", 2)
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "DisableUse", 2)

        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "AI", 1)
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Brain", 1)


class InjuredSoldier(MapDropper):
    paths = ("Digsite_Rk5arena_P",)

    def entered_map(self) -> None:
        den = FindObject("PopulationOpportunityDen", "Digsite_Rk5arena_Audio.TheWorld:PersistentLevel.PopulationOpportunityDen_1")
        if not den:
            raise Exception("Could not locate den for Injured Soldier")
        
        den.IsEnabled = True

        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            if not (caller.AIClass and caller.AIClass.Name == "CharClass_NPCInjuredSoldier"):
                return True

            mission = FindObject("MissionDefinition", "GD_Co_Chapter11.M_DahlDigsite")
            if not mission:
                raise Exception("Could not locate mission for Injured Soldier")

            spawn_loot(
                self.location.prepare_pools(),
                mission,
                (caller.Location.X, caller.Location.Y, caller.Location.Z)
            )
            return True

        RunHook(
            "WillowGame.WillowAIPawn.Died",
            f"LootRandomizer.{id(self)}",
            hook,
        )

    def exited_map(self) -> None:
        RemoveHook(
            "WillowGame.WillowAIPawn.Died",
            f"LootRandomizer.{id(self)}",
        )


class Hanna(MapDropper):
    paths = ("Moon_P",)

    def entered_map(self) -> None:
        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            if not (caller.AIClass and caller.AIClass.Name == "CharClass_Hanna"):
                return True

            mission = self.location.mission
            if not mission:
                raise Exception("Could not locate mission for Injured Soldier")

            spawn_loot(
                self.location.prepare_pools(),
                mission.mission_definition.uobject,
                (caller.Location.X, caller.Location.Y, caller.Location.Z)
            )
            return True

        RunHook(
            "WillowGame.WillowAIPawn.Died",
            f"LootRandomizer.{id(self)}",
            hook,
        )

    def exited_map(self) -> None:
        RemoveHook(
            "WillowGame.WillowAIPawn.Died",
            f"LootRandomizer.{id(self)}",
        )


class SentinelRaid(MapDropper):
    paths = ("InnerCore_P",)

    def block_loot(self) -> None:
        def hook_loot(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            path = UObject.PathName(caller)
            return path != "Vault_Boss.TheWorld:PersistentLevel.Main_Sequence.SeqAct_ApplyBehavior_3.Behavior_RemoteCustomEvent_0"

        RunHook(
            "WillowGame.Behavior_RemoteCustomEvent.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}.block_loot",
            hook_loot,
        )

    def unblock_loot(self) -> None:
        RemoveHook(
            "WillowGame.Behavior_RemoteCustomEvent.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}.block_loot",
        )

    def detect_loot(self) -> None:
        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            path = UObject.PathName(caller)
            if path in (
                "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_82",
                "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_83",
                "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_88",
                "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_89",
            ):
                self.undetect_loot()
                self.block_loot()
            return True
        RunHook(
            "WillowGame.Behavior_SpawnItems.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}.detect_loot",
            hook,
        )

    def undetect_loot(self) -> None:
        RemoveHook(
            "WillowGame.Behavior_RemoteCustomEvent.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}.detect_loot",
        )

    def detect_kill(self) -> None:
        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            if (
                UObject.PathName(caller) ==
                "GD_FinalBossCorkBig.Character.AIDef_FBCBig:AIBehaviorProviderDefinition_0.Behavior_RemoteEvent_19"
            ):
                self.detect_loot()
                self.unblock_loot()
            return True
        RunHook(
            "Engine.Behavior_RemoteEvent.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}.detect_kill",
            hook,
        )

    def undetect_kill(self) -> None:
        RemoveHook(
            "Engine.Behavior_RemoteEvent.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}.detect_kill",
        )

    def entered_map(self) -> None:
        self.detect_kill()

        for path in (
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_81",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_82",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_83",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_84",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_85",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_86",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_87",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_88",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_89",
        ):
            spawner = FindObject("Behavior_SpawnItems", path)
            if spawner:
                spawner.ItemDropOffset.Z = 256
        
    def exited_map(self) -> None:
        self.undetect_loot()
        self.undetect_kill()
        self.unblock_loot()


class MasterPoacher(MapDropper):
    paths = ("Digsite_P",)

    def entered_map(self) -> None:
        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            if UObject.PathName(caller.AIClass) != "GD_Co_NPCs_GuardianHunter.Character.CharClass_ScavBandit":
                return True

            mission = self.location.mission
            if not mission:
                raise Exception("Could not locate mission for Master Poacher")

            spawn_loot(
                self.location.prepare_pools(),
                mission.mission_definition.uobject,
                (caller.Location.X, caller.Location.Y, caller.Location.Z)
            )
            return True

        RunHook(
            "WillowGame.WillowAIPawn.Died",
            f"LootRandomizer.{id(self)}",
            hook,
        )

    def exited_map(self) -> None:
        RemoveHook(
            "WillowGame.WillowAIPawn.Died",
            f"LootRandomizer.{id(self)}",
        )


class PopupAd(MapDropper):
    paths = ("Ma_Nexus_P", "Ma_Motherboard_P")

    def entered_map(self) -> None:
        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            if UObject.PathName(caller) == "GD_Ma_AdPopup.BE_Shared_AdPopup:Behavior_SpawnLootAtPoints_3":
                caller.ItemPools = self.location.prepare_pools()
            return True

        RunHook(
            "WillowGame.Behavior_SpawnLoot.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}",
            hook,
        )

    def exited_map(self) -> None:
        RemoveHook(
            "WillowGame.Behavior_SpawnLoot.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}",
        )


class SpywareChest(Attachment):
    def inject(self, obj: UObject) -> None:
        rarities = self.location.rarities
        self.location.rarities = (100,) * 11
        super().inject(obj)
        self.location.rarities = rarities


class SpywareBug(MissionDropper, MapDropper):
    paths = ("Ma_Nexus_P",)

    def entered_map(self) -> None:
        chest_bpd = FindObject("BehaviorProviderDefinition", "GD_Ma_Side_SpywareData.InteractiveObjects.InteractiveObj_SpywareChest:BehaviorProviderDefinition_0")
        if not chest_bpd:
            raise Exception("Could not locate chest for Spyware Who Came in from the Cold")

        behavior_data = chest_bpd.BehaviorSequences[1].BehaviorData2
        set_flag = behavior_data[1].Behavior

        behavior_data[1].Behavior = behavior_data[4].Behavior
        behavior_data[1].LinkedVariables.ArrayIndexAndLength = 0

        behavior_data[4].Behavior = set_flag
        behavior_data[4].LinkedVariables.ArrayIndexAndLength = 1

        if self.location.current_status != Mission.Status.Complete:
            return

        for pawn in get_pawns():
            if pawn.AIClass and pawn.AIClass.Name == "CharacterClass_Ma_HoneyPot":
                break
        else:
            raise Exception("Could not locate bug for Spyware Who Came in from the Cold")

        handle = (pawn.ConsumerHandle.PID,)
        bpd = pawn.AIClass.AIDef.BehaviorProviderDefinition
        kernel = get_behaviorkernel()
        
        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "Brain", 1
        )

class RoseTinting(MissionDropper, MapDropper):
    paths = ("Ma_LeftCluster_P",)

    def entered_map(self) -> None:
        completed_event = FindObject("WillowSeqEvent_MissionRemoteEvent", "Ma_LeftCluster_SideMissions.TheWorld:PersistentLevel.Main_Sequence.WillowSeqEvent_MissionRemoteEvent_33")
        sequence_conditions = FindObject("BehaviorSequenceEnableByMultipleConditions", "GD_Ma_Side_MINACData.InteractiveObjects.IO_MinacMissionObject:BehaviorProviderDefinition_1.BehaviorSequenceEnableByMultipleConditions_0")
        minac_eye = FindObject("WillowInteractiveObject", "Ma_LeftCluster_SideMissions.TheWorld:PersistentLevel.WillowInteractiveObject_0")
        if not (completed_event and sequence_conditions and minac_eye):
            raise Exception("Could not locate objects for Rose Tinting")

        completed_event.OutputLinks[0].Links = ()

        sequence_conditions.EnableConditions = ()

        kernel = get_behaviorkernel()
        handle = (minac_eye.ConsumerHandle.PID,)
        bpd = minac_eye.InteractiveObjectDefinition.BehaviorProviderDefinition

        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "MissionComplete", 2)
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "MissionAvailable", 1)


class DataMining(MissionDropper, MapDropper):
    paths = ("Ma_LeftCluster_P",)

    def entered_map(self) -> None:
        completed_event = FindObject("WillowSeqEvent_MissionRemoteEvent", "Ma_LeftCluster_SideMissions.TheWorld:PersistentLevel.Main_Sequence.WillowSeqEvent_MissionRemoteEvent_37")
        kill_event = FindObject("WillowSeqEvent_MissionRemoteEvent", "Ma_LeftCluster_SideMissions.TheWorld:PersistentLevel.Main_Sequence.WillowSeqEvent_MissionRemoteEvent_31")
        if not (completed_event and kill_event):
            raise Exception("Could not locate objects for Data Mining")

        completed_event.OutputLinks[0].Links = ()
        kill_event.OutputLinks[0].Links = ()


class ClaptasticStash(MapDropper):
    bpd_path: str

    def __init__(self, bpd_path: str, map_name: str) -> None:
        self.bpd_path = bpd_path
        super().__init__(map_name)

    def entered_map(self) -> None:
        bpd = FindObject("BehaviorProviderDefinition", self.bpd_path)
        if not bpd:
            raise Exception("Could not locate BPD for hidden stash")

        closed_events = bpd.BehaviorSequences[0].EventData2        
        for event in closed_events:
            if event.UserData.EventName == "OnBehaviorSequenceEnabled":
                event.OutputLinks.ArrayIndexAndLength = 0

        pt02_events = bpd.BehaviorSequences[4].EventData2
        for event in pt02_events:
            if event.UserData.EventName == "OnBehaviorSequenceEnabled":
                event.OutputLinks.ArrayIndexAndLength = 0



class Dignity(MissionStatusDelegate, MapDropper):
    paths = ("Ma_Motherboard_P",)

    den: Optional[UObject] = None
    monocle: Optional[UObject] = None

    def spawn_dignity(self) -> None:
        if self.den:
            self.den.Aspect = None
            self.den.IsEnabled = True
            self.den.RespawnKilledActors(1)

    def hide_monocle(self) -> None:
        if self.monocle:
            get_behaviorkernel().ChangeBehaviorSequenceActivationStatus(
                (self.monocle.ConsumerHandle.PID,),
                self.monocle.InteractiveObjectDefinition.BehaviorProviderDefinition,
                "Invisible",
                1
            )
            self.monocle.ChangeInstanceDataSwitch("PooPile", 0)

    def completed(self) -> None:
        self.spawn_dignity()
        self.hide_monocle()

    def entered_map(self) -> None:
        self.den = FindObject("PopulationOpportunityDen", "Ma_Motherboard_Side.TheWorld:PersistentLevel.PopulationOpportunityDen_0")
        loaded2 = FindObject("SeqEvent_LevelLoaded", "Ma_Motherboard_Side.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_LevelLoaded_2")
        pop_eval = FindObject("OzMissionExpressionEvaluator", "GD_Ma_DignityTrap.Population.BD_Dignity:OzMissionExpressionEvaluator_0")
        if not (self.den and loaded2 and pop_eval):
            raise Exception("Could not locate den for Dignity")

        for obj in FindAll("WillowInteractiveObject"):
            obj_def = obj.InteractiveObjectDefinition
            if (obj_def and obj_def.Name == "IO_Ma_ShredOfDignity"):
                break
        else:
            raise Exception("Could not locate monocle for Dignity")
        self.monocle = obj

        loaded2.OutputLinks[0].Links = ()
        pop_eval.ObjectiveStatesToLinkTo.bComplete = True

        if self.location.current_status == Mission.Status.Complete:
            self.hide_monocle()
            self.spawn_dignity()

    def exited_map(self) -> None:
        self.den = None
        self.monocle = None


class EgoTrap(MissionStatusDelegate, MapDropper):
    paths = ("Ma_Nexus_P",)

    def apply(self) -> None:
        for pawn in get_pawns():
            if pawn.AIClass and pawn.AIClass.Name == "CharacterClass_Ma_EgoTrap":
                break
        else:
            raise Exception("Could not locate 3G0-TP")

        get_behaviorkernel().ChangeBehaviorSequenceActivationStatus(
            (pawn.ConsumerHandle.PID,),
            pawn.AIClass.AIDef.BehaviorProviderDefinition,
            "Brain",
            1
        )

    def entered_map(self) -> None:
        if self.location.current_status == Mission.Status.Complete:
            self.apply()

    def completed(self) -> None:
        Log("EgoTrap completed")
        self.apply()


class StopTheMusic(MissionDropper, MapDropper):
    paths = ("Ma_Nexus_P",)

    def entered_map(self) -> None:
        loaded2 = FindObject("SeqEvent_LevelLoaded", "Ma_Nexus_Side.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_LevelLoaded_2")
        if not loaded2:
            raise Exception("Could not locate loading for Stop The Music")
        loaded2.OutputLinks[0].Links = ()


class ByteClub(MissionDropper, MapDropper):
    paths = ("Ma_RightCluster_P",)

    def entered_map(self) -> None:
        den = FindObject("PopulationOpportunityDen", "Ma_RightCluster_SideMission.TheWorld:PersistentLevel.PopulationOpportunityDen_7")
        if not den:
            raise Exception("Could not locate den for Byte Club")

        turnedin_enable = FindObject("BehaviorSequenceEnableByMission", "GD_Ma_BotPit.Character.AIDef_Ma_BotPit:AIBehaviorProviderDefinition_0.BehaviorSequenceEnableByMission_2")
        brain_enable = FindObject("BehaviorSequenceEnableByMission", "GD_Ma_BotPit.Character.AIDef_Ma_BotPit:AIBehaviorProviderDefinition_0.BehaviorSequenceEnableByMission_0")
        if not (turnedin_enable and brain_enable):
            raise Exception("Could not locate objects for Byte Club")

        den.IsEnabled = True

        turnedin_enable.MissionStatesToLinkTo.bComplete = False
        brain_enable.MissionStatesToLinkTo.bComplete = True


class SupaEgoTrap(MissionDropper, MapDropper):
    paths = ("Ma_Nexus_P",)

    def entered_map(self) -> None:
        den = FindObject("PopulationOpportunityDen", "Ma_Nexus_Side.TheWorld:PersistentLevel.PopulationOpportunityDen_1")
        mission_enable = FindObject("BehaviorSequenceEnableByMission", "GD_Ma_SuperEgoTrap.Character.AIDef_Ma_SuperEgoTrap:AIBehaviorProviderDefinition_0.BehaviorSequenceEnableByMission_0")
        if not (den and mission_enable):
            raise Exception("Could not locate objects for 5UP4-3G0-TP")
        
        den.IsEnabled = True
        mission_enable.MissionStatesToLinkTo.bComplete = True


class JackBobble(MapDropper):
    paths = ("Ma_Subconscious_P",)

    def entered_map(self) -> None:
        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            if UObject.PathName(caller) != "Ma_Subconscious_Game.TheWorld:PersistentLevel.Emitter_2":
                return True

            missiondef = FindObject("MissionDefinition", "GD_Ma_Chapter05.M_Ma_Chapter05")
            if not missiondef:
                raise Exception(
                    f"No mission for {self.location.name}"
                )

            spawn_loot(
                self.location.prepare_pools(),
                missiondef,
                (-54300, -6464, 5028),
                (-212, 1037, 0)
            )
            return True

        RunHook(
            "Engine.Actor.OnToggleHidden",
            f"LootRandomizer.{id(self)}",
            hook,
        )

    def exited_map(self) -> None:
        RemoveHook(
            "Engine.Actor.OnToggleHidden",
            f"LootRandomizer.{id(self)}",
        )
        

class DeadlierGame(MissionStatusDelegate, MapDropper):
    paths = ("Ma_Subconscious_P",)

    def apply(self) -> None:
        pawn = FindObject("WillowAIPawn", "Ma_Subconscious_SideMissions.TheWorld:PersistentLevel.WillowAIPawn_0")
        icon = FindObject("InteractionIconDefinition", "GD_InteractionIcons.Default.Icon_DefaultTalk")
        if not (pawn and icon):
            raise Exception("Could not locate objects for Deadlier Game")

        pawn.SetInteractionIcon(icon, 0)
        pawn.SetUsable(True, None, 0)

        bpd = pawn.AIClass.AIDef.BehaviorProviderDefinition
        kernel = get_behaviorkernel()
        handle = (pawn.ConsumerHandle.PID,)

        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "MissionComplete", 2)
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Brain", 1)


    def entered_map(self) -> None:
        if self.location.current_status == Mission.Status.Complete:
            self.apply()

    def completed(self) -> None:
        self.apply()


class SumFears(MapDropper):
    paths = ("Ma_Subconscious_P",)

    def entered_map(self) -> None:
        turnin_enable = FindObject("BehaviorSequenceEnableByMission", "GD_Ma_MetaTrap_SomeFears.Character.AIDef_Ma_MetaTrap_SomeFears:AIBehaviorProviderDefinition_0.BehaviorSequenceEnableByMission_0")
        if not turnin_enable:
            raise Exception("Could not locate objects for Sum Of Some Fears")
        turnin_enable.MissionStatesToLinkTo.bComplete = True


def get_mutator_multiplier() -> int:
    machine_attr = FindObject(
        "DesignerAttributeDefinition",
        "GD_Ma_Mutator.Attributes.Att_MutatorMachineType"
    )
    if not machine_attr:
        raise Exception("Could not locate objects for Mutator Chest")

    for machine in FindAll("WillowInteractiveObject"):
        obj_def = machine.InteractiveObjectDefinition
        if not (obj_def and obj_def.Name == "IO_MutatorMachine"):
            continue

        machine_type, *_ = machine_attr.GetValue(machine)
        if int(machine_type) == 2:
            break
    else:
        raise Exception("Could not locate level machine for Mutator Chest")
        
    for datum in machine.InstanceState.Data:
        if datum.Name == "NumberSwitch":
            level = datum.Int
            break
    else:
        raise Exception("Could not determine level for Mutator Chest")

    if   level in (1, 2):    return 1
    elif level in (3, 4):    return 2
    elif level in (5, 6):    return 3
    elif level in (7, 8, 9): return 4
    else: raise Exception(f"Found unexpected level {level} for Mutator Chest")


class MutatorChest(Attachment):
    def inject(self, obj: UObject) -> None:
        original_rarities = self.location.rarities
        self.location.rarities = (100,) * get_mutator_multiplier()
        super().inject(obj)
        self.location.rarities = original_rarities


class MutatorPawn(Pawn):
    def inject(self, pools: List[Any]) -> None:
        original_rarities = tuple(self.location.rarities)
        self.location.rarities = original_rarities * get_mutator_multiplier()
        Log(f"--- MutatorPawn rarities: {self.location.rarities} ---")
        super().inject(pools)
        self.location.rarities = original_rarities


class HolodomeMission(MissionDropper, MapDropper):
    paths = ("Eridian_slaughter_P",)

    compare_path: str
    objective_path: str
    didntdo_behavior_path: str
    did_behavior_path: str

    def __init__(
        self,
        *,
        objective_path: str,
        compare_path: str,
        didntdo_behavior_path: str,
        did_behavior_path: str,
    ) -> None:
        self.objective_path = objective_path
        self.compare_path = compare_path
        self.didntdo_behavior_path = didntdo_behavior_path
        self.did_behavior_path = did_behavior_path
        super().__init__()

    def entered_map(self) -> None:
        objective = FindObject("MissionObjectiveDefinition", self.objective_path)
        didntdo_bevavior = FindObject("Behavior_UpdateMissionObjective", self.didntdo_behavior_path)
        did_behavior = FindObject("Behavior_UpdateMissionObjective", self.did_behavior_path)
        if not (objective and did_behavior and didntdo_bevavior):
            raise Exception("Could not locate objectives for Holodome")

        didntdo_objective = didntdo_bevavior.MissionObjective
        did_objective = did_behavior.MissionObjective

        Log(f"didntdo_objective: {UObject.PathName(didntdo_objective)}")
        Log(f"did_objective: {UObject.PathName(did_objective)}")

        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            if UObject.PathName(caller) != self.compare_path:
                return True
            
            objective_complete = get_missiontracker().IsMissionObjectiveComplete(objective)
            Log(f"objective_complete: {objective_complete}")

            if objective_complete:
                didntdo_bevavior.MissionObjective = did_objective
                did_behavior.MissionObjective = did_objective
            else:
                didntdo_bevavior.MissionObjective = didntdo_objective
                did_behavior.MissionObjective = didntdo_objective

            return True

        RunHook(
            "GearboxFramework.Behavior_CompareBool.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}",
            hook,
        )

    def exited_map(self) -> None:
        RemoveHook(
            "GearboxFramework.Behavior_CompareBool.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}",
        )


class HolodomeScientists(MapDropper):
    paths = ("Eridian_slaughter_P",)

    def entered_map(self) -> None:
        button_bpd = FindObject("BehaviorProviderDefinition", "GD_EridianSlaughterData.InteractiveObjects.GenericButtonDigi:BehaviorProviderDefinition_0")
        if not button_bpd:
            raise Exception("Could not locate button for Scientists")
        
        off_sequence = button_bpd.BehaviorSequences[5]
        off_sequence.ConsolidatedOutputLinkData[6].ActivateDelay = 1

        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            if UObject.PathName(caller) != "GD_EridianSlaughterData.InteractiveObjects.GenericButtonDigi:BehaviorProviderDefinition_0.Behavior_InterpolateFloatOverTime_10":
                return True
            
            mission = self.location.mission
            if not mission:
                raise Exception("Could not locate mission for Scientists")

            spawn_loot(
                tuple(self.location.prepare_pools()) * 4,
                mission.mission_definition.uobject,
                (14958, -3456, 674),
                (-468, -544, 0),
                64
            )
            return True

        RunHook(
            "GearboxFramework.Behavior_InterpolateFloatOverTime.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}",
            hook,
        )

    def exited_map(self) -> None:
        RemoveHook(
            "GearboxFramework.Behavior_InterpolateFloatOverTime.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}",
        )


# fmt: off

Locations = (
    Other("World Uniques", WorldUniques(), tags=Tag.Excluded),
    Enemy("Flame Knuckle",
        Pawn("PawnBalance_DahlPowersuit_Knuckle"),
        Pawn("PawnBalance_DahlSergeantFlameKnuckle"),
    tags=Tag.Excluded),

    Mission("Tales from Elpis", MissionDefinition("GD_Co_TalesFromElpis.M_TalesFromElpis")),
    Enemy("Son of Flamey", Pawn("PawnBalance_SonFlamey")),
    Enemy("Grandson of Flamey", Pawn("PawnBalance_GrandsonFlamey")),
    Enemy("Badass Kraggon", Pawn("PawnBalance_ElementalSpitterBadass"), tags=Tag.VeryRareEnemy),
    Enemy("Phonic Kraggon", Pawn("PawnBalance_ElementalPhonic"), tags=Tag.RareEnemy),
    Mission("Land Among the Stars", MissionDefinition("GD_Co_Motivation.M_Motivation")),
    Mission("Follow Your Heart", MissionDefinition("GD_Co_FollowYourHeart.M_FollowYourHeart"), tags=Tag.LongMission),
    Enemy("Deadlift", Pawn("PawnBalance_SpacemanDeadlift"), tags=Tag.SlowEnemy),
    Mission("Last Requests",
        MissionDefinition("GD_Co_LastRequests.M_LastRequests"),
        LastRequests(),
    tags=Tag.LongMission),
    Enemy("Tom Thorson",
        FriskedCorpse("Deadsurface_P", "Deadsurface_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_5"),
    mission="Last Requests"),
    Enemy("Squat", Pawn("PawnBalance_Squat"), mission="Last Requests"),
    Enemy("Nel (Called a Dick)", Dick(), mission="Last Requests"),
    Enemy("Nel", Pawn("PawnBalance_Nel"), tags=Tag.SlowEnemy),
    Mission("Nova? No Problem!", MissionDefinition("GD_Co_NovaNoProblem.M_NovaNoProblem")),
    Other("Janey's Chest", Attachment("BD_DahlShockChest", 0), mission="Nova? No Problem!"),
    Other("Janey's Safe", Attachment("BD_ElectronicObjectThree", 0), mission="Nova? No Problem!"),
    Mission("Torgue-o! Torgue-o! (Turn in Janey)", MissionDefinition("GD_Co_ToroToro.M_ToroToro"), TorgueO()),
    Mission("Torgue-o! Torgue-o! (Turn in Lava)", MissionDefinitionAlt("GD_Co_ToroToro.M_ToroToro"), TorgueO()),
    Enemy("Antagonized Kraggon", Pawn("PawnBalance_UniqueCharger"), mission="Torgue-o! Torgue-o! (Turn in Janey)", rarities=(5,)),
    Enemy("Oscar", Pawn("PawnBalance_ScavSuicidePsycho_Oscar")),
    Mission("Wherefore Art Thou?", MissionDefinition("GD_Co_WhereforeArtThou.M_Co_WhereforeArtThou"), tags=Tag.LongMission|Tag.VehicleMission),
    Enemy("Maureen", Pawn("PawnBalance_MaureenRider"), mission="Wherefore Art Thou?"),
    Mission("All the Little Creatures", MissionDefinition("gd_cork_allthelittlecreatures.M_AllTheLittleCreatures")),
    Enemy("Even-More-Disgusting Tork", Pawn("PawnBalance_NotCuteBadassTork")),
    Other("Sword in the Stone",
        SwordInStone(),
        Behavior("GD_Co_EasterEggs.Excalibastard.InteractiveObject_Excalibastard:BehaviorProviderDefinition_0.Behavior_SpawnItems_44"),
    tags=Tag.Miscellaneous),
    Enemy("Swagman (Stanton's Liver)", Swagman("StantonsLiver_P")),
    Other("Obelisk Chest", PositionalChest("ObjectGrade_TreasureChest", "StantonsLiver_P", 15677, 24953, -14827)),
    Mission("Recruitment Drive", MissionDefinition("GD_Cork_Resistors.M_Resistors"), tags=Tag.VehicleMission),
    Enemy("Magma Rivers", Pawn("PawnBalance_LittleDarksiderBadassBandit")),
    Enemy("Wally Wrong", Pawn("PawnBalance_DarksiderBadassBandit")),
    Enemy("Fair Dinkum", Pawn("PawnBalance_DarksiderBadassPsycho")),
    Mission("The Empty Billabong", MissionDefinition("GD_Co_EmptyBillabong.M_EmptyBillaBong")),
    Enemy("Jolly Swagman",
        FriskedCorpse("ComFacility_P", "ComFacility_SideMissions.TheWorld:PersistentLevel.WillowInteractiveObject_4"),
    mission="The Empty Billabong"),
    Enemy("Red", Pawn("PawnBalance_Ned")),
    Enemy("Belly", Pawn("PawnBalance_Kelly")),
    Mission("Grinders", MissionDefinition("GD_Cork_Grinding.M_Cork_Grinding"), tags=Tag.VeryLongMission),
    Enemy("Rooster Booster", Pawn("PawnBalance_RoosterBooster")),
    Mission("To Arms!", ToArms(), MissionDefinition("GD_Co_ToArms.M_Co_ToArms"), tags=Tag.VeryLongMission),
    Enemy("PLA Member Tim Pot", Pawn("PawnBalance_TimPot"), mission="To Arms!"),
    Enemy("PLA Member Tom Pot", Pawn("PawnBalance_TomPot"), mission="To Arms!"),
    Enemy("PLA Member Tum Pot", Pawn("PawnBalance_TumPot"), mission="To Arms!"),
    Mission("Bunch of Ice Holes (Turn in Nurse Nina)", MissionDefinition("GD_Co_IceHoles.M_Co_IceHoles")),
    Mission("Bunch of Ice Holes (Turn in B4R-BOT)", MissionDefinitionAlt("GD_Co_IceHoles.M_Co_IceHoles")),
    Enemy("Giant Shuggurath of Ice", Pawn("PawnBalance_GiantCryoHive")),
    Mission("Pop Racing", MissionDefinition("GD_Co_PopRacing.M_Co_PopRacing"), PopRacing(), tags=Tag.VehicleMission),
    Enemy("Lunestalker Snr", Pawn("PawnBalance_LunestalkerSnrRider")),
    Mission("Zapped 1.0",
        MissionDefinition("GD_Co_Zapped.M_Co_Zapped1"),
        Zapped1(),
        ObjectiveKillInfo("GD_Co_Zapped.M_Co_Zapped1:KillScavengers.MissionObjectiveKillInfo_12", damage_type=1), # DAMAGE_TYPE_Incindiary
    ),
    Mission("Zapped 2.0",
        MissionDefinition("GD_Co_Zapped.M_Co_Zapped2"),
        ObjectiveKillInfo("GD_Co_Zapped.M_Co_Zapped2:Killtorks.MissionObjectiveKillInfo_13", damage_type=8), # DAMAGE_TYPE_Ice
    ),
    Mission("Zapped 3.0", MissionDefinition("GD_Co_Zapped.M_Co_Zapped3")),
    Enemy("Malfunctioning CL4P-TP", Pawn("BD_MalfunctioningClaptrap"), mission="Zapped 3.0", rarities=(10,)),
    Enemy("Swagman (Outlands Canyon)", Swagman("Outlands_P2")),
    Other("Perfect Timing Chest", PositionalChest("ObjectGrade_TreasureChest", "Outlands_P2", -28896, 56862, -828)),
    Mission("Boomshakalaka", MissionDefinition("GD_Co_Boomshakalaka.M_Boomshakalaka"), Boomshakalaka()),
    Enemy("Dunks Watson", DunksWatson(), mission="Boomshakalaka"),
    Mission("Space Slam", MissionDefinition("GD_Co_SpaceSlam.M_SpaceSlam"), SpaceSlam()),
    Enemy("Tork Dredger", Pawn("PawnBalance_TorkDredger"), tags=Tag.MobFarm, rarities=(33,)),
    Enemy("Poop Deck", PoopDeck(), Pawn("PawnBalance_PoopDeck"), tags=Tag.SlowEnemy),
    Enemy("Bosun", Pawn("PawnBalance_Bosun")),
    Mission("The Secret Chamber",
        MissionDefinition("GD_Co_SecretChamber.M_SecretChamber"),
        MissionPickup("Wreck_SideMissions.TheWorld:PersistentLevel.WillowMissionPickupSpawner_0", "Wreck_P"),
    tags=Tag.LongMission),
    Other("Zarpedon's Stash", Attachment("Balance_Chest_ZarpedonsStash"), mission="The Secret Chamber"),
    Mission("Wiping the Slate", MissionDefinition("GD_Co_WipingSlate.M_WipingSlate")),
    Mission("No Such Thing as a Free Launch", FreeLaunch(), MissionDefinition("GD_Cork_Rocketeering.M_Rocketeering"), tags=Tag.LongMission),
    Enemy("Tony Slows", Pawn("PawnBalance_TonySlows"), mission="No Such Thing as a Free Launch"),
    Enemy("Cosmo", Cosmo(), mission="No Such Thing as a Free Launch"),
    Enemy("Neil Parsec", NeilParsec(), Pawn("Balance_Co_LuzzFightbeer")),
    Mission("Nothing is Never an Option", MissionDefinition("GD_Co_YouAskHowHigh.M_Co_YouAskHowHigh"), tags=Tag.LongMission),
    Enemy("Boomer", Pawn("PawnBalance_BoomerJetFighter"), tags=Tag.SlowEnemy, rarities=(100,)),
    Mission("Treasures of ECHO Madre", MissionDefinition("GD_Co_TreasuresofECHO.M_Co_TreasuresofECHO"), tags=Tag.LongMission),
    Enemy("Rabid Adams", Pawn("PawnBalance_RabidAdams")),
    Mission("Another Pickle", MissionDefinition("GD_Cork_AnotherPickle.M_Cork_AnotherPickle")),
    Enemy("Abbot", Abbot(), mission="Another Pickle"),
    Enemy("Bruce", Pawn("Bal_Bruce"), tags=Tag.SlowEnemy),
    Mission("Rough Love", MissionDefinition("GD_Co_RoughLove.M_Co_RoughLove")),
    Enemy("Meat Head", Pawn("PawnBalance_MeatHead")),
    Enemy("Drongo Bones", Pawn("PawnBalance_DrongoBones")),
    Mission("Home Delivery", MissionDefinition("GD_Co_HomeDelivery.M_HomeDelivery")),
    Other("What's In The Box?", Attachment("ObjectGrade_WhatsInTheBox")),
    Enemy("Felicity Rampant",
        Behavior(
            "GD_ProtoWarBot_CoreBody.Character.AIDef_ProtoWarBot_CoreBody:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_11",
            "GD_ProtoWarBot_CoreBody.Character.AIDef_ProtoWarBot_CoreBody:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_21",
        ),
        Behavior(
            "GD_ProtoWarBot_CoreBody.Character.AIDef_ProtoWarBot_CoreBody:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_10",
            "GD_ProtoWarBot_CoreBody.Character.AIDef_ProtoWarBot_CoreBody:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_20",
        inject=False),
    tags=Tag.SlowEnemy),
    Other("Moxxi's Toy Box", MoxxiBox(), Attachment("ObjectGrade_MoxxiDahlEpic")),
    Mission("Sub-Level 13", MissionDefinition("GD_Co_SubLevel13.M_Co_SubLevel13Part1")),
    Enemy("Ghostly Apparition", Pawn("PawnBalance_SubLevel13Ghost"), mission="Sub-Level 13"),
    Mission("Sub-Level 13: Part 2 (Turn in Pickle)", SubLevel13(), MissionDefinition("GD_Co_SubLevel13.M_Co_SubLevel13Part2")),
    Mission("Sub-Level 13: Part 2 (Turn in Schmidt)", MissionDefinitionAlt("GD_Co_SubLevel13.M_Co_SubLevel13Part2")),
    Mission("The Voyage of Captain Chef", ChefVoyage(), MissionDefinition("GD_Co_VoyageOfCaptainChef.M_VoyageOfCaptainChef")),
    Enemy("Benjamin Blue", Attachment("BD_Ben")),
    Enemy("X-STLK-23-3", Pawn("PawnBalance_Stalker_RnD")),
    Enemy("Corporal Bob", Bob(), Pawn("PawnBalance_DahlMarine_CentralTerm"), tags=Tag.VeryRareEnemy),
    Mission("Boarding Party", MissionDefinition("GD_Co_Boarding_Party.M_BoardingParty")),
    Mission("Voice Over", MissionDefinition("GD_Co_VoiceOver.M_VoiceOver")),
    Mission("Hot Head", MissionDefinition("GD_Co_Hot_Head.M_Hot_Head")),
    Mission("Cleanliness Uprising", MissionDefinition("GD_Co_Cleanliness_Uprising.M_Cleanliness_Uprising")),
    Mission("An Urgent Message", MissionDefinition("GD_Co_Detention.M_Detention")),
    Mission("Handsome AI", MissionDefinition("GD_Co_PushButtonMission.M_PushButtonMission")),
    Mission("Paint Job", MissionDefinition("GD_Co_Paint_Job.M_Paint_Job")),
    Mission("Kill Meg", MissionDefinition("GD_Co_Kill_Meg.M_Kill_Meg")),
    Enemy("Meg", Pawn("PawnBalance_Meg")),
    Mission("Infinite Loop (Restrain CLAP-9000)", MissionDefinition("GD_Co_Side_Loop.M_InfiniteLoop")),
    Mission("Infinite Loop (Restrain DAN-TRP)", MissionDefinitionAlt("GD_Co_Side_Loop.M_InfiniteLoop")),
    Mission("It Ain't Rocket Surgery", MissionDefinition("GD_Co_Side_RocketSurgery.M_RocketSurgery"), tags=Tag.LongMission),
    Other("Dr. Spara's Stash", Attachment("ObjectGrade_HypWeaponChest_Ice", 0, 1), mission="It Ain't Rocket Surgery"),
    Mission("Fresh Air", FreshAir(), MissionDefinition("GD_Co_Side_FreshAir.M_FreshAir")),
    Enemy("Dr. Minte", DrMinte(), mission="Fresh Air"),
    Enemy("Tiny Destroyer", Pawn("PawnBalance_MiniDestroyer")),
    Mission("Lab 19",
        MissionPickup("RandDFacility_P.TheWorld:PersistentLevel.WillowMissionPickupSpawner_1", "RandDFacility_P"),
        MissionDefinition("GD_Co_Side_Lab19.M_Lab19")
    ),
    Mission("Red, Then Dead", MissionDefinition("GD_Co_Side_Reshirt.M_RedShirt")),
    Mission("Things That Go Boom", MissionDefinition("GD_Co_Side_Exploders.M_Exploders")),
    Enemy("Lost Legion Courier", Pawn("PawnBalance_DahlRedShirt"), mission="Red, Then Dead"),
    Enemy("Lost Legion Powersuit Noob", Pawn("PawnBalance_DahlRedShirtPowersuit")),
    Mission("To the Moon", MissionDefinition("GD_Co_Side_EngineerMoonShot.M_EngineerMoonShot")),
    Enemy("Lost Legion Defector", Defector(), mission="To the Moon"),
    Mission("Lock and Load", MissionDefinition("GD_Co_Side_LockAndLoad.M_LockAndLoad")),
    Mission("Quarantine: Back On Schedule", MissionDefinition("GD_Cork_BackOnSchedule.M_BackOnSchedule")),
    Mission("Quarantine: Infestation", MissionDefinition("GD_Cork_Quarantine.M_Quarantine")),
    Mission("In Perfect Hibernation", MissionDefinition("GD_Cork_PerfectHibernation.M_PerfectHibernation")),
    Enemy("Lazlo", Pawn("PawnBalance_Lazlo")),
    Mission("Trouble with Space Hurps",
        MissionDefinition("GD_Cork_TroubleWithSpaceHurps.M_TroubleWithSpaceHurps"),
        SpaceHurps("InnerHull_Mission.TheWorld:PersistentLevel.WillowInteractiveObject_42.MissionDirectivesDefinition_0", True, True, "InnerHull_P"),
    ),
    Mission("Eradicate!", MissionDefinition("GD_Cork_Eradicate.M_Eradicate"), tags=Tag.LongMission),
    Enemy("Eghood", Pawn("PawnBalance_Eghood")),
    Enemy("CL4P-L3K", Pawn("PawnBalance_Clap_L3K")),
    Mission("Don't Get Cocky",
        MissionDefinition("GD_Cork_DontGetCocky.M_DontGetCocky"),
        DontGetCocky("InnerHull_Mission.TheWorld:PersistentLevel.WillowInteractiveObject_254", "InnerHull_P"),
    tags=Tag.VehicleMission),
    Mission("Picking Up the Pieces",
        MissionDefinition("GD_Co_Side_PickingUp.M_PickingUpThePieces"),
        MissionPickup("Laser_P.TheWorld:PersistentLevel.WillowMissionPickupSpawner_3", "Laser_P"),
    ),
    Other("Scientist Laser Stash", Attachment("ObjectGrade_HypWeaponChest_Laser"), mission="Picking Up the Pieces"),
    Mission("These are the Bots",
        MissionDefinition("GD_Co_Side_TheseAreTheBots.M_TheseAreTheBots"),
        TheseAreTheBots(),
    tags=Tag.LongMission),
    Mission("The Don", MissionDefinition("GD_Co_Side_TheDon.M_TheDon")),
    Mission("Return of Captain Chef",
        MissionDefinition("GD_Co_ReturnOfCapnChef.M_ReturnOfCaptainChef"),
        ChefReturn(),
    tags=Tag.LongMission),
    Enemy("Injured Lost Legion Soldier", InjuredSoldier()),
    Enemy("Raum-Kampfjet Mark V",
        Behavior("GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_104"),
        Behavior(
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_84",
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_85",
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_86",
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_87",
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_88",
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_89",
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_90",
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_91",
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_92",
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_93",
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_94",
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_95",
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_96",
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_97",
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_98",
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_99",
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_100",
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_101",
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_102",
            "GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_103",
        inject=False),
    tags=Tag.SlowEnemy),
    Other("Compression Chamber Chest", PositionalChest("ObjectGrade_DahlEpic", "Access_P", -21260, 35075, 78528)),
    Other("8-bit Chest", Attachment("ObjectGrade_8bitTreasureChest")),
    Mission("Z8N-TP", MissionDefinition("GD_Co_Side_Z8MTRP.M_Z8nTRP")),
    Mission("Don't Shoot the Messenger",
        MissionDefinition("GD_Co_DontShootMessenger.MissionDef.M_DontShootMsgr"),
        MissionPickup("11B_Access_GAME.TheWorld:PersistentLevel.WillowMissionPickupSpawner_0", "Access_P"),
    tags=Tag.LongMission),
    Enemy("Hanna", Hanna(), mission="Don't Shoot the Messenger"),
    Enemy("Opha Superior", Pawn("PawnBalance_OphaBoss")),
    Enemy("The Sentinel (First Phase)", Pawn("PawnBalance_FinalBossCork"), tags=Tag.Excluded),
    Enemy("The Sentinel",
        Behavior("GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_86"),
        Behavior(
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_81",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_84",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_85",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_87",
        inject=False),
    tags=Tag.SlowEnemy, rarities=(50, 50)),
    Mission("The Beginning of the End", MissionDefinition("GD_Co_Chapter11.M_DahlDigsite"), tags=Tag.Excluded),
    Mission("The Bestest Story Ever Told", MissionDefinition("GD_Co_CorkRaid.M_CorkRaid"), tags=Tag.Raid),
    Enemy("The Invincible Sentinel (First Phase)", Pawn("PawnBalance_RaidBossCork"), tags=Tag.Excluded),
    Enemy("The Invincible Sentinel",
        SentinelRaid(),
        Behavior(
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_82",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_83",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_88",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_89",
        ),
    tags=Tag.Raid),
    Enemy("Iwajira",
        Pawn("PawnBalance_Rockzilla"),
        Behavior(
            "GD_Rockzilla.Death.DeathDef_Rockzilla:BehaviorProviderDefinition_0.Behavior_SpawnItems_147",
            "GD_Rockzilla.Death.DeathDef_Rockzilla:BehaviorProviderDefinition_0.Behavior_SpawnItems_146",
        inject=False),
    tags=Tag.SlowEnemy),
    Mission("Guardian Hunter (Turn in Sterwin)", MissionDefinition("GD_Co_GuardianHunter.MissionDef.M_GuardianHunter", block_weapon=False), tags=Tag.LongMission),
    Mission("Guardian Hunter (Turn in Master Poacher)", MissionDefinitionAlt("GD_Co_GuardianHunter.MissionDef.M_GuardianHunter"), tags=Tag.LongMission),
    Enemy("Master Poacher", MasterPoacher(), mission="Guardian Hunter (Turn in Sterwin)"),
    Mission("Sterwin Forever", MissionDefinition("GD_Co_GuardianHunter.MissionDef.M_SterwinForever", block_weapon=False)),

    Mission("DAHL Combat Training: Round 1", MissionDefinition("GD_Co_MoonSlaughter.M_Co_MoonSlaughter01", unlink_next=True), DAHLTraining(), tags=Tag.ShockDrop|Tag.Slaughter|Tag.LongMission),
    Mission("DAHL Combat Training: Round 2", MissionDefinition("GD_Co_MoonSlaughter.M_Co_MoonSlaughter02", unlink_next=True), tags=Tag.ShockDrop|Tag.Slaughter|Tag.LongMission),
    Mission("DAHL Combat Training: Round 3", MissionDefinition("GD_Co_MoonSlaughter.M_Co_MoonSlaughter03", unlink_next=True), tags=Tag.ShockDrop|Tag.Slaughter|Tag.LongMission),
    Mission("DAHL Combat Training: Round 4", MissionDefinition("GD_Co_MoonSlaughter.M_Co_MoonSlaughter04", unlink_next=True), tags=Tag.ShockDrop|Tag.Slaughter|Tag.LongMission),
    Mission("DAHL Combat Training: Round 5", MissionDefinition("GD_Co_MoonSlaughter.M_Co_MoonSlaughter05", unlink_next=True), tags=Tag.ShockDrop|Tag.Slaughter|Tag.LongMission),

    Enemy("Bug",
          Pawn("PawnBalance_AdBug"),
          Pawn("PawnBalance_BadassBug"),
          Pawn("PawnBalance_Bug"),
          Pawn("PawnBalance_SimpleBug"),
          Pawn("PawnBalance_SimpleBug_Eos"),
          Pawn("PawnBalance_SpyBug"),
          Pawn("PawnBalance_UnstableBug"),
    tags=Tag.ClaptasticVoyage|Tag.MobFarm),
    Enemy("Insecurity Bot",
        Pawn("PawnBalance_BadassClapDawg"),
        Pawn("PawnBalance_BotRider"),
        Pawn("PawnBalance_ClapDawg"),
        Pawn("PawnBalance_ClapDawgRider"),
        Pawn("PawnBalance_ClapPuppy"),
        Pawn("PawnBalance_ClapTurret"),
        Pawn("PawnBalance_ClapTurret_Missile"),
        Pawn("PawnBalance_CleanupRuntime"),
        Pawn("PawnBalance_FireWall"),
        Pawn("PawnBalance_FlyTrap"),
        Pawn("PawnBalance_InsecWheelie"),
        Pawn("PawnBalance_InsecurityBot"),
        Pawn("PawnBalance_InsecurityBot_LowDamage"),
        Pawn("PawnBalance_InsecuritySniper"),
        Pawn("PawnBalance_MinacMinion"),
        Pawn("PawnBalance_PermFlyTrap"),
        Pawn("PawnBalance_RexLoaderMinion"),
        Pawn("PawnBalance_VeryInsecureBadass"),
        Pawn("PawnBalance_VeryInsecureBadassClapDawg"),
        Pawn("PawnBalance_VeryInsecureBot"),
        Pawn("PawnBalance_VeryInsecureClapPuppy"),
        Pawn("PawnBalance_VeryInsecureFlight"),
        Pawn("PawnBalance_VeryInsecureSentry"),
        Pawn("PawnBalance_VeryInsecureSniper"),
        Pawn("PawnBalance_ShadowClone"),
    tags=Tag.ClaptasticVoyage|Tag.MobFarm),
    Enemy("Virus",
        Pawn("PawnBalance_BadassVirus"),
        Pawn("PawnBalance_MiniVirus"),
        Pawn("PawnBalance_ParasiticVirus"),
        Pawn("PawnBalance_Virus"),
        Pawn("PawnBalance_VirusLauncher"),
        Pawn("PawnBalance_Virus_Deletion"),
    tags=Tag.ClaptasticVoyage|Tag.MobFarm),
    Enemy("Fragmented Bandit",
        Pawn("PawnBalance_FragBadassBandit"),
        Pawn("PawnBalance_FragBadassPsycho"),
        Pawn("PawnBalance_FragBandit"),
        Pawn("PawnBalance_FragBanditMidget"),
        Pawn("PawnBalance_FragPsycho"),
        Pawn("PawnBalance_FragPsychoMidget"),
        Pawn("PawnBalance_FragSuicidePsycho"),
        Pawn("PawnBalance_FragSuicidePsychoMidget"),
    tags=Tag.ClaptasticVoyage|Tag.MobFarm),
    Other("Popup Ad", PopupAd(), tags=Tag.ClaptasticVoyage, rarities=(33,)),
    Enemy("Loot Bug", Pawn("PawnBalance_LootBug"), tags=Tag.ClaptasticVoyage|Tag.RareEnemy),
    Mission("Spyware Who Came in from the Cold", #TODO make repeatable
        MissionDefinition("GD_Ma_Side_SpywareInFromCold.M_Ma_Side_SpywareInFromCold"),
        SpywareChest("Balance_SpywareChest"),
        SpywareBug(),
    tags=Tag.ClaptasticVoyage|Tag.VeryLongMission),
    Mission("Rose Tinting",
        MissionDefinition("GD_Ma_Side_MINAC.M_Ma_Side_MINAC"),
        RoseTinting(),
    tags=Tag.ClaptasticVoyage),
    Mission("Chip's Data Mining Adventure (Kill Shame)",
        MissionDefinition("GD_Ma_Side_CookieDataMining.M_Ma_Side_CookieDataMining"),
        DataMining(),
    tags=Tag.ClaptasticVoyage),
    Enemy("Shame", Pawn("PawnBalance_Trojan_Shame"), mission="Chip's Data Mining Adventure (Kill Shame)"),
    Mission("Chip's Data Mining Adventure (Kill Cookies)", MissionDefinitionAlt("GD_Ma_Side_CookieDataMining.M_Ma_Side_CookieDataMining"), tags=Tag.ClaptasticVoyage),
    Enemy("Chip", Pawn("PawnBalance_Ma_Chip"), mission="Chip's Data Mining Adventure (Kill Cookies)"),
    Mission("1D-TP", MissionDefinition("GD_Ma_Side_IdTrap.M_Ma_Side_IdTrap"), tags=Tag.ClaptasticVoyage),
    Mission("3G0-TP", EgoTrap(), MissionDefinition("GD_Ma_Side_EgoTrap.M_Ma_Side_EgoTrap"), tags=Tag.ClaptasticVoyage|Tag.LongMission),
    Mission("Corrosion of Dignity",
        MissionDefinition("GD_Ma_Side_ShredOfDignity.M_Ma_Side_ShredOfDignity"),
        Dignity(),
    tags=Tag.ClaptasticVoyage),
    Other("Motherlessboard Hidden Stash",
        ClaptasticStash("GD_Ma_Population_Treasure.InteractiveObjects.InteractiveObj_HiddenStash_03:BehaviorProviderDefinition_0", "Ma_Motherboard_P"),
        Attachment("Balance_HiddenStash_03"),
    tags=Tag.ClaptasticVoyage),    
    Other("Cluster 99002 0V3RL00K Hidden Stash",
        ClaptasticStash("GD_Ma_Population_Treasure.InteractiveObjects.InteractiveObj_HiddenStash_02:BehaviorProviderDefinition_0", "Ma_RightCluster_P"),
        Attachment("Balance_HiddenStash_02"),
    tags=Tag.ClaptasticVoyage),
    Other("Faptrap", PositionalChest("ObjectGrade_DahlWeaponChest_Marigold", "Ma_RightCluster_P", 63919, 1298, 128), tags=Tag.ClaptasticVoyage),
    Mission("You Can Stop the Music",
        MissionDefinition("GD_Ma_Side_StopTheMusic.M_Ma_Side_StopTheMusic"),
        StopTheMusic(),
    tags=Tag.ClaptasticVoyage),
    Enemy("Denial Subroutine", Pawn("PawnBalance_CodeWorm"), tags=Tag.ClaptasticVoyage),
    Enemy("Teh Earworm", Pawn("PawnBalance_EarWorm"), tags=Tag.ClaptasticVoyage),
    Enemy("Catchy Hook!", Pawn("PawnBalance_EarWormTentacle", transform=0), tags=Tag.ClaptasticVoyage|Tag.RareEnemy),
    Enemy("Most Requested!", Pawn("PawnBalance_EarWormTentacle", transform=1), tags=Tag.ClaptasticVoyage|Tag.RareEnemy),
    Enemy("Key Change!", Pawn("PawnBalance_EarWormTentacle", transform=2), tags=Tag.ClaptasticVoyage|Tag.RareEnemy),
    Enemy("Tween Favorite!", Pawn("PawnBalance_EarWormTentacle", transform=3), tags=Tag.ClaptasticVoyage|Tag.RareEnemy),
    Enemy("Verse Chorus Verse Chorus Bridge Chorus (x2)!", Pawn("PawnBalance_EarWormTentacle", transform=5), tags=Tag.ClaptasticVoyage|Tag.RareEnemy),
    Enemy("Sparkly Formula!", Pawn("PawnBalance_EarWormTentacle", transform=6), tags=Tag.ClaptasticVoyage|Tag.RareEnemy),
    Enemy("Floor Filler!", Pawn("PawnBalance_EarWormTentacle", transform=4), tags=Tag.ClaptasticVoyage|Tag.RareEnemy),
    Mission("Byte Club", ByteClub(), MissionDefinition("GD_Ma_Side_ByteClub.M_Ma_Side_ByteClub"), tags=Tag.ClaptasticVoyage),
    Mission("5UP4-3G0-TP", SupaEgoTrap(), MissionDefinition("GD_Ma_Side_SuperEgoTrap.M_Ma_Side_SuperEgoTrap"), tags=Tag.ClaptasticVoyage),
    Enemy("5UP4-3G0-TP", Pawn("BD_Ma_SuperEgoTrap"), mission="5UP4-3G0-TP"),
    Mission("The Temple of Boom (Turn in Tannis)", MissionDefinition("GD_Ma_Side_TempleOfBoom.M_Ma_Side_TempleofBoom"), tags=Tag.ClaptasticVoyage),
    Mission("The Temple of Boom (Turn in Gladstone)", MissionDefinitionAlt("GD_Ma_Side_TempleOfBoom.M_Ma_Side_TempleofBoom"), tags=Tag.ClaptasticVoyage),
    Enemy("The Sponx", Pawn("Balance_Ma_Sponx"), tags=Tag.ClaptasticVoyage|Tag.SlowEnemy),
    Enemy("Despair", Pawn("PawnBalance_Despair"), tags=Tag.ClaptasticVoyage|Tag.SlowEnemy),
    Enemy("Self-Loathing", Pawn("PawnBalance_SelfLoathing"), tags=Tag.ClaptasticVoyage|Tag.SlowEnemy),
    Other("Jack's Bobble Head", JackBobble(), tags=Tag.ClaptasticVoyage),
    Mission("A Deadlier Game", DeadlierGame(), MissionDefinition("GD_Ma_Side_BadTrap.M_Ma_Side_BadTrap"), tags=Tag.ClaptasticVoyage),
    Mission("The Sum of Some Fears",
        MissionDefinition("GD_Ma_Side_SumOfSomeFears.M_Ma_Side_SumOfSomeFears"),
        MissionGiver("GD_Ma_MetaTrap_SomeFears.Character.Pawn_Ma_MetaTrap_SomeFears:MissionDirectivesDefinition_0", True, True, "Ma_Subconscious_P"),
        MissionGiver("Ma_Subconscious_SideMissions.TheWorld:PersistentLevel.WillowInteractiveObject_1.MissionDirectivesDefinition_0", False, False, "Ma_Subconscious_P"),
        SumFears(),
    tags=Tag.ClaptasticVoyage|Tag.LongMission),
    Other("T.K. Baha's Chest",
        Attachment("Balance_HiddenStash_01"),
        ClaptasticStash("GD_Ma_Population_Treasure.InteractiveObjects.InteractiveObj_HiddenStash_01:BehaviorProviderDefinition_0", "Ma_Subconscious_P"),
    tags=Tag.ClaptasticVoyage),
    Enemy("ECLIPSE", Pawn("PawnBalance_VoltronTrap"), tags=Tag.ClaptasticVoyage|Tag.Raid, rarities=(100, 50, 50)),
    Enemy("EOS",
        Behavior(
            "GD_Ma_Chapter05_Data.IO_Ma_LootShower:BehaviorProviderDefinition_1.Behavior_SpawnItems_146",
            "GD_Ma_Chapter05_Data.IO_Ma_LootShower:BehaviorProviderDefinition_1.Behavior_SpawnItems_152",
            "GD_Ma_Chapter05_Data.IO_Ma_LootShower:BehaviorProviderDefinition_1.Behavior_SpawnItems_153",
        ),
        Behavior(
            "GD_Ma_Chapter05_Data.IO_Ma_LootShower:BehaviorProviderDefinition_1.Behavior_SpawnItems_144",
            "GD_Ma_Chapter05_Data.IO_Ma_LootShower:BehaviorProviderDefinition_1.Behavior_SpawnItems_145",
            "GD_Ma_Chapter05_Data.IO_Ma_LootShower:BehaviorProviderDefinition_1.Behavior_SpawnItems_147",
            "GD_Ma_Chapter05_Data.IO_Ma_LootShower:BehaviorProviderDefinition_1.Behavior_SpawnItems_148",
            "GD_Ma_Chapter05_Data.IO_Ma_LootShower:BehaviorProviderDefinition_1.Behavior_SpawnItems_149",
            "GD_Ma_Chapter05_Data.IO_Ma_LootShower:BehaviorProviderDefinition_1.Behavior_SpawnItems_150",
            "GD_Ma_Chapter05_Data.IO_Ma_LootShower:BehaviorProviderDefinition_1.Behavior_SpawnItems_151",
            "GD_Ma_Chapter05_Data.IO_Ma_LootShower:BehaviorProviderDefinition_1.Behavior_SpawnItems_154",
            "GD_Ma_Chapter05_Data.IO_Ma_LootShower:BehaviorProviderDefinition_1.Behavior_SpawnItems_155",
            "GD_Ma_Chapter05_Data.IO_Ma_LootShower:BehaviorProviderDefinition_1.Behavior_SpawnItems_156",
            "GD_Ma_Chapter05_Data.IO_Ma_LootShower:BehaviorProviderDefinition_1.Behavior_SpawnItems_157",
            "GD_Ma_Chapter05_Data.IO_Ma_LootShower:BehaviorProviderDefinition_1.Behavior_SpawnItems_158",
            "GD_Ma_Chapter05_Data.IO_Ma_LootShower:BehaviorProviderDefinition_1.Behavior_SpawnItems_159",
            "GD_Ma_Chapter05_Data.IO_Ma_LootShower:BehaviorProviderDefinition_1.Behavior_SpawnItems_160",
            "GD_Ma_Chapter05_Data.IO_Ma_LootShower:BehaviorProviderDefinition_1.Behavior_SpawnItems_161",
        inject=False),
    tags=Tag.ClaptasticVoyage|Tag.Raid),
    Mission("System Shutdown", MissionDefinition("GD_Ma_Chapter06.M_Ma_Chapter06"), tags=Tag.Excluded),
    Mission("h4X0rz", MissionDefinition("GD_Ma_Side_H4X0rz.M_Ma_Side_H4X0rz"), tags=Tag.ClaptasticVoyage|Tag.LongMission),
    Mission("l33t h4X0rz", MissionDefinition("GD_Ma_Side_H4X0rz.M_Ma_Side_H4X0rz_Repeat"), tags=Tag.ClaptasticVoyage|Tag.Slaughter),
    Other("Black Mutator Chest", MutatorChest("ObjectGrade_CommonChest_Mut", configuration=1), mission="l33t h4X0rz"),
    Other("Red Mutator Chest", MutatorChest("ObjectGrade_RedChest_Mut", configuration=1), mission="l33t h4X0rz"),
    Other("Purple Mutator Chest", MutatorChest("ObjectGrade_GlitchChest_Mut", configuration=1), mission="l33t h4X0rz"),
    Enemy("5H4D0W-TP", MutatorPawn("PawnBalance_SH4D0W-TP-Part1"), mission="l33t h4X0rz", tags=Tag.RareEnemy),
    Enemy("Hope", MutatorPawn("PawnBalance_Hope"), mission="l33t h4X0rz", tags=Tag.RareEnemy),
    Enemy("Self Esteem", MutatorPawn("PawnBalance_SelfEsteem"), mission="l33t h4X0rz", tags=Tag.RareEnemy),

    # OptionalObjectiveCheck

    Mission("Digistructed Madness: Round 1", MissionDefinition("GD_EridianSlaughter.MissionDef.M_EridianSlaughter01"), tags=Tag.Holodome|Tag.Slaughter|Tag.LongMission),
    Mission("Digistructed Madness: Round 1 (Turn On Jump Pads)",
        MissionDefinitionAlt("GD_EridianSlaughter.MissionDef.M_EridianSlaughter01"),
        HolodomeMission(
            objective_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter01:OBJ_30_TurnOnJumpPads",
            compare_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter01:Behavior_CompareBool_25",
            didntdo_behavior_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter01:Behavior_UpdateMissionObjective_91",
            did_behavior_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter01:Behavior_UpdateMissionObjective_88",
        ),
    tags=Tag.Holodome|Tag.Slaughter|Tag.LongMission),
    Enemy("Flameknuckle", Pawn("PawnBalance_DahlSergeantFlameKnuckle"), mission="Digistructed Madness: Round 1"),

    Mission("Digistructed Madness: Round 2", MissionDefinition("GD_EridianSlaughter.MissionDef.M_EridianSlaughter02"), tags=Tag.Holodome|Tag.Slaughter|Tag.LongMission),
    Mission("Digistructed Madness: Round 2 (Build Robot)",
        MissionDefinitionAlt("GD_EridianSlaughter.MissionDef.M_EridianSlaughter02"),
        HolodomeMission(
            objective_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter02:OBJ_30_BuildRobots",
            compare_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter02:Behavior_CompareBool_1",
            didntdo_behavior_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter02:Behavior_UpdateMissionObjective_5",
            did_behavior_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter02:Behavior_UpdateMissionObjective_6",
        ),
    tags=Tag.Holodome|Tag.Slaughter|Tag.LongMission),
    Enemy("Powersuit Felicity", Pawn("PawnBalance_DahlCombatSuit_Felicity"), mission="Digistructed Madness: Round 2 (Build Robot)"),

    Mission("Digistructed Madness: Round 3", MissionDefinition("GD_EridianSlaughter.MissionDef.M_EridianSlaughter03"), tags=Tag.Holodome|Tag.Slaughter|Tag.LongMission),
    Mission("Digistructed Madness: Round 3 (Help Scientists Escape)",
        MissionDefinitionAlt("GD_EridianSlaughter.MissionDef.M_EridianSlaughter03"),
        HolodomeMission(
            objective_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter03:OBJ_30_SaveSci",
            compare_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter03:Behavior_CompareBool_13",
            didntdo_behavior_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter03:Behavior_UpdateMissionObjective_53",
            did_behavior_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter03:Behavior_UpdateMissionObjective_48",
        ),
    tags=Tag.Holodome|Tag.Slaughter|Tag.LongMission),
    Enemy("Scientist", HolodomeScientists(), rarities=(33,)),

    Mission("Digistructed Madness: Round 4", MissionDefinition("GD_EridianSlaughter.MissionDef.M_EridianSlaughter04"), tags=Tag.Holodome|Tag.Slaughter|Tag.VeryLongMission),
    Mission("Digistructed Madness: Round 4 (Destroy Destroyers)",
        MissionDefinitionAlt("GD_EridianSlaughter.MissionDef.M_EridianSlaughter04"),
        HolodomeMission(
            objective_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter04:OBJ_30_KillDestroyer",
            compare_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter04:Behavior_CompareBool_1",
            didntdo_behavior_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter04:Behavior_UpdateMissionObjective_5",
            did_behavior_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter04:Behavior_UpdateMissionObjective_6",
        ),
    tags=Tag.Holodome|Tag.Slaughter|Tag.VeryLongMission),
    Enemy("Defense Destroyer", Pawn("PawnBalance_DestroyerMini")),
    Enemy("Guardian Pondor / Lost Legion Chosen Powersuit",
        Pawn("PawnBalance_GuardianPondor"),
        Pawn("PawnBalance_DahlEternalPowersuit"),
        Pawn("PawnBalance_DahlEternalPowersuitShield"),
    mission="Digistructed Madness: Round 4", tags=Tag.MobFarm, rarities=(7,)),

    Mission("Digistructed Madness: Round 5", MissionDefinition("GD_EridianSlaughter.MissionDef.M_EridianSlaughter05"), tags=Tag.Holodome|Tag.Slaughter|Tag.VeryLongMission),
    Mission("Digistructed Madness: Round 5 (Install Vault Key Pieces)",
        MissionDefinitionAlt("GD_EridianSlaughter.MissionDef.M_EridianSlaughter05"),
        HolodomeMission(
            objective_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter05:OBJ_35_OpenVault",
            compare_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter05:Behavior_CompareBool_5",
            didntdo_behavior_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter05:Behavior_UpdateMissionObjective_25",
            did_behavior_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter05:Behavior_UpdateMissionObjective_24",
        ),
    tags=Tag.Holodome|Tag.Slaughter|Tag.VeryLongMission),
    Other("Vault Chest",
        PositionalChest("ObjectGrade_DahlEpic", "Eridian_slaughter_P", 15817, 3788, 680),
        PositionalChest("ObjectGrade_DahlEpic", "Eridian_slaughter_P", 14885, 4514, 680),
        PositionalChest("ObjectGrade_DahlEpic", "Eridian_slaughter_P", 13968, 3802, 680),
    rarities=(33,)),

    Mission("Digistructed Madness: The Badass Round", MissionDefinition("GD_EridianSlaughter.MissionDef.M_EridianSlaughter_Badass"), tags=Tag.Holodome|Tag.Slaughter|Tag.VeryLongMission|Tag.Raid),
)

"""
TODO:
re-rarity VeryRareEnemy's

genericize balanceless pawn deaths
"""
