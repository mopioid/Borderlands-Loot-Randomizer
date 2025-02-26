from typing import Optional, Sequence, Set, Union

from unrealsdk import (
    FindAll,
    FindObject,
    FStruct,
    GetEngine,
    Log,
    RemoveHook,
    RunHook,
    UFunction,
    UObject,
)

from .. import locations
from ..defines import *
from ..enemies import Enemy, Pawn
from ..items import ItemPool
from ..locations import Behavior, Dropper, MapDropper, PreventDestroy
from ..missions import (
    PlaythroughDelegate,
    Mission,
    MissionDropper,
    MissionDefinition,
    MissionTurnIn,
    MissionTurnInAlt,
    MissionGiver,
    MissionObject,
    MissionPickup,
    MissionStatusDelegate,
)
from ..other import Attachment, Other, VendingMachine


class MarketingBonuses(Dropper):
    def enable(self) -> None:
        super().enable()

        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            premier = FindObject(
                "MarketingUnlockInventoryDefinition",
                "GD_Globals.Unlocks.MarketingUnlock_PremierClub",
            )
            if premier:
                premier_items = tuple(premier.UnlockItems[0].UnlockItems)
                premier.UnlockItems[0].UnlockItems = ()

                def revert_premier():
                    premier.UnlockItems[0].UnlockItems = premier_items

                do_next_tick(revert_premier)

            collectors = FindObject(
                "MarketingUnlockInventoryDefinition",
                "GD_Globals.Unlocks.MarketingUnlock_Collectors",
            )
            if collectors:
                collectors_items = tuple(collectors.UnlockItems[0].UnlockItems)
                collectors.UnlockItems[0].UnlockItems = ()

                def revert_collectors():
                    collectors.UnlockItems[0].UnlockItems = collectors_items

                do_next_tick(revert_collectors)

            return True

        RunHook(
            "WillowGame.WillowPlayerController.GrantNewMarketingCodeBonuses",
            "LootRandomizer",
            hook,
        )

    def disable(self) -> None:
        super().disable()
        RemoveHook(
            "WillowGame.WillowPlayerController.GrantNewMarketingCodeBonuses",
            "LootRandomizer",
        )


class XCom(MissionStatusDelegate, MapDropper):
    paths = ("*",)

    objective: UObject

    def enable(self) -> None:
        super().enable()

        objective = FindObject(
            "MissionObjectiveDefinition",
            "GD_Z3_MedicalMystery2.M_MedicalMystery2:KillBandits",
        )
        if not objective:
            raise Exception("Could not locate objective for X-Communicate")
        self.objective = objective

        self.objective.KillRestrictions.bMissionWeapon = False
        self.objective.KillRestrictions.bCriticalHit = True
        self.objective.KillRestrictions.bNotCriticalHit = True

    def disable(self) -> None:
        super().disable()

        if self.objective:
            self.objective.KillRestrictions.bMissionWeapon = True
            self.objective.KillRestrictions.bCriticalHit = False
            self.objective.KillRestrictions.bNotCriticalHit = False

    def accepted(self) -> None:
        self.apply()

    def completed(self) -> None:
        self.unapply()

    def entered_map(self) -> None:
        if self.location.current_status == Mission.Status.Active:
            self.apply()

    def exited_map(self) -> None:
        self.unapply()

    def apply(self) -> None:
        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            allegiance = caller.Allegiance
            if not (
                allegiance
                and allegiance.AllegianceKilledStat
                == "STAT_PLAYER_KILLS_GROUP_BANDIT"
            ):
                return True

            killer = params.Killer
            if not (killer and killer.Class.Name == "WillowPlayerController"):
                return True

            weapon = killer.Pawn.Weapon
            if not weapon:
                return True

            mesh = str(
                weapon.DefinitionData.BarrelPartDefinition.GestaltModeSkeletalMeshName
            )
            if mesh.endswith("_Alien"):
                get_missiontracker().UpdateObjective(self.objective)
            return True

        RunHook(
            "WillowGame.WillowAIPawn.Died", f"LootRandomizer.{id(self)}", hook
        )

    def unapply(self) -> None:
        RemoveHook(
            "WillowGame.WillowAIPawn.Died",
            f"LootRandomizer.{id(self)}",
        )


class Radio1340(MapDropper):
    def __init__(self) -> None:
        super().__init__("Sanctuary_P", "SanctuaryAir_P")

    def entered_map(self) -> None:
        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            if not (
                caller.InteractiveObjectDefinition
                and caller.InteractiveObjectDefinition.Name == "IO_MoxieRadio"
            ):
                return True

            tracker = get_missiontracker()
            objective = FindObject(
                "MissionObjectiveDefinition",
                "GD_Z3_OutOfBody.M_OutOfBody:DestroyRadio",
            )
            if not tracker.IsMissionObjectiveActive(objective):
                return True

            gamestage_region = FindObject(
                "WillowRegionDefinition", "GD_GameStages.Zone1.Dam"
            )
            if not gamestage_region:
                raise Exception("Could not find GD_GameStages.Zone1.Dam")
            _, level, _ = gamestage_region.GetRegionGameStage()

            caller.ManuallyBalanceToRegionDef = gamestage_region
            caller.ExpLevel = caller.GameStage = level

            spawn_loot(
                self.location.prepare_pools(),
                caller,
                (3539, 5261, 3703),
            )

            RemoveHook(
                "WillowGame.WillowInteractiveObject.TakeDamage",
                f"LootRandomizer.{id(self)}",
            )
            return True

        RunHook(
            "WillowGame.WillowInteractiveObject.TakeDamage",
            f"LootRandomizer.{id(self)}",
            hook,
        )

    def exited_map(self) -> None:
        RemoveHook(
            "WillowGame.WillowInteractiveObject.TakeDamage",
            f"LootRandomizer.{id(self)}",
        )


class Leviathan(MapDropper):
    paths = ("Orchid_WormBelly_P",)

    def entered_map(self) -> None:
        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            if (
                UObject.PathName(caller.MissionObjective)
                != "GD_Orchid_Plot_Mission09.M_Orchid_PlotMission09:KillBossWorm"
            ):
                return True

            pawn = GetEngine().GetCurrentWorldInfo().PawnList
            while pawn:
                if (
                    pawn.AIClass
                    and pawn.AIClass.Name == "CharacterClass_Orchid_BossWorm"
                ):
                    break
                pawn = pawn.NextPawn

            spawn_loot(
                self.location.prepare_pools(),
                pawn,
                (1200, -66000, 3000),
                (-400, -1800, -400),
                200,
            )
            return True

        RunHook(
            "WillowGame.Behavior_UpdateMissionObjective.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}",
            hook,
        )

    def exited_map(self) -> None:
        RemoveHook(
            "WillowGame.Behavior_UpdateMissionObjective.ApplyBehaviorToContext",
            f"LootRandomizer.{id(self)}",
        )


class MonsterTruckDriver(Pawn):
    def should_inject(self, pawn: UObject) -> bool:
        return (
            pawn.MySpawnPoint
            and UObject.PathName(pawn.MySpawnPoint)
            == "Iris_Hub2_Combat.TheWorld:PersistentLevel.WillowPopulationPoint_52"
        )


class PetesBurner(Pawn):
    def should_inject(self, pawn: UObject) -> bool:
        return (
            pawn.Allegiance.Name == "Iris_Allegiance_DragonGang"
            and locations.map_name != "Iris_DL2_Interior_P".casefold()
        )


_doctorsorders_midgets: Set[str] = set()


def _spawn_midget(caller: UObject, _f: UFunction, params: FStruct) -> bool:
    if (
        params.SpawnedActor
        and UObject.PathName(caller)
        == "GD_Balance_Treasure.InteractiveObjectsTrap.MidgetHyperion.InteractiveObj_CardboardBox_MidgetHyperion:BehaviorProviderDefinition_1.Behavior_SpawnFromPopulationSystem_5"
    ):
        _doctorsorders_midgets.add(UObject.PathName(params.SpawnedActor))
    return True


class Midget(Pawn):
    def should_inject(self, pawn: UObject) -> bool:
        return UObject.PathName(pawn) not in _doctorsorders_midgets and not (
            pawn.MySpawnPoint
            and UObject.PathName(pawn.MySpawnPoint)
            == "OldDust_Mission_Side.TheWorld:PersistentLevel.WillowPopulationPoint_26"
        )


class DoctorsOrdersMidget(Pawn):
    def should_inject(self, pawn: UObject) -> bool:
        return UObject.PathName(pawn) in _doctorsorders_midgets


class SpaceCowboyMidget(Pawn):
    def should_inject(self, pawn: UObject) -> bool:
        return (
            pawn.MySpawnPoint
            and UObject.PathName(pawn.MySpawnPoint)
            == "OldDust_Mission_Side.TheWorld:PersistentLevel.WillowPopulationPoint_26"
        )


class DoctorsOrdersMidgetRegistry(MapDropper):
    paths = ("PandoraPark_P",)

    def entered_map(self) -> None:
        _doctorsorders_midgets.clear()
        RunHook(
            "WillowGame.Behavior_SpawnFromPopulationSystem.PublishBehaviorOutput",
            f"LootRandomizer.{id(self)}",
            _spawn_midget,
        )

    def exited_map(self) -> None:
        _doctorsorders_midgets.clear()
        RemoveHook(
            "WillowGame.Behavior_SpawnFromPopulationSystem.PublishBehaviorOutput",
            f"LootRandomizer.{id(self)}",
        )


class Haderax(MapDropper):
    paths = ("SandwormLair_P",)

    def entered_map(self) -> None:
        digicrate = FindObject(
            "InteractiveObjectBalanceDefinition",
            "GD_Anemone_Lobelia_DahDigi.LootableGradesUnique.ObjectGrade_DalhEpicCrate_Digi",
        )
        if digicrate:
            digicrate.DefaultInteractiveObject = None

        digicrate_shield = FindObject(
            "InteractiveObjectBalanceDefinition",
            "GD_Anemone_Lobelia_DahDigi.LootableGradesUnique.ObjectGrade_DalhEpicCrate_Digi_Shield",
        )
        if digicrate_shield:
            digicrate_shield.DefaultInteractiveObject = None

        digicrate_artifact = FindObject(
            "InteractiveObjectBalanceDefinition",
            "GD_Anemone_Lobelia_DahDigi.LootableGradesUnique.ObjectGrade_DalhEpicCrate_Digi_Articfact",
        )
        if digicrate_artifact:
            digicrate_artifact.DefaultInteractiveObject = None


class DigiEnemy(Enemy):
    fallback: str
    fallback_enemy: Enemy

    _item: Optional[ItemPool] = None

    def __init__(
        self,
        name: str,
        *droppers: Dropper,
        fallback: str,
        tags: Tag = Tag(0),
        rarities: Optional[Sequence[int]] = None,
    ) -> None:
        self.fallback = fallback
        super().__init__(name, *droppers, tags=tags, rarities=rarities)

    def enable(self) -> None:
        super().enable()

        for location in Locations:
            if isinstance(location, Enemy) and location.name == self.fallback:
                self.fallback_enemy = location

        if not self.fallback_enemy:
            raise Exception(f"Failed to find fallback enemy for {self}")

    @property
    def item(self) -> Optional[ItemPool]:
        return self._item if self._item else self.fallback_enemy.item

    @item.setter
    def item(self, item: Optional[ItemPool]) -> None:
        self._item = item

    @property
    def hint_pool(self) -> UObject:  # ItemPoolDefinition
        return (
            super().hint_pool if self._item else self.fallback_enemy.hint_pool
        )

    @property
    def tracker_name(self) -> str:
        return (
            super().tracker_name
            if self._item
            else self.fallback_enemy.tracker_name
        )


class Loader1340(MissionDropper, MapDropper):
    paths = ("dam_p",)

    def entered_map(self) -> None:
        missiondef = self.location.mission_definition.uobject
        if get_missiontracker().GetMissionStatus(missiondef) != 4:
            return

        toggle = FindObject(
            "SeqAct_Toggle",
            "Dam_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Loader1340.SeqAct_Toggle_1",
        )

        loaded0 = FindObject(
            "SeqEvent_LevelLoaded",
            "Dam_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Loader1340.SeqEvent_LevelLoaded_0",
        )
        loaded1 = FindObject(
            "SeqEvent_LevelLoaded",
            "Dam_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Loader1340.SeqEvent_LevelLoaded_1",
        )
        if not (loaded0 and loaded1):
            raise Exception(
                "Could not locate dam loading sequence for Loader 1340"
            )

        loaded0.OutputLinks[0].Links[0].LinkedOp = toggle
        loaded1.OutputLinks[0].Links[0].LinkedOp = toggle


class WillTheBandit(MapDropper):
    paths = ("tundraexpress_p",)

    def entered_map(self) -> None:
        toggle = FindObject(
            "SeqAct_Toggle",
            "TundraExpress_Combat.TheWorld:PersistentLevel.Main_Sequence.NoHardFeelings.SeqAct_Toggle_0",
        )

        loaded0 = FindObject(
            "SeqEvent_LevelLoaded",
            "TundraExpress_Combat.TheWorld:PersistentLevel.Main_Sequence.NoHardFeelings.SeqEvent_LevelLoaded_0",
        )
        loaded1 = FindObject(
            "SeqEvent_LevelLoaded",
            "TundraExpress_Combat.TheWorld:PersistentLevel.Main_Sequence.NoHardFeelings.SeqEvent_LevelLoaded_1",
        )
        if not (loaded0 and loaded1):
            raise Exception("Could not locate Tundra sequence for Loader 1340")

        loaded0.OutputLinks[0].Links[0].LinkedOp = toggle
        loaded0.OutputLinks[0].Links[0].InputLinkIdx = 0

        loaded1.OutputLinks[0].Links[0].LinkedOp = toggle
        loaded1.OutputLinks[0].Links[0].InputLinkIdx = 0


class McShooty(MissionStatusDelegate, MapDropper):
    paths = ("Grass_Cliffs_P",)

    def accepted(self) -> None:
        for pawn in get_pawns():
            if (
                pawn.bIsDead
                and pawn.AIClass
                and pawn.AIClass.Name == "CharClass_Shootyface"
            ):
                pawn.SetHidden(True)
                pawn.SetCollisionType(1)

    def entered_map(self) -> None:
        destroyreal = FindObject(
            "WillowSeqEvent_MissionRemoteEvent",
            "Grass_Cliffs_Dynamic.TheWorld:PersistentLevel.Main_Sequence.ShootMeInTheFace.WillowSeqEvent_MissionRemoteEvent_2",
        )
        shooty_bpd = FindObject(
            "BehaviorProviderDefinition",
            "GD_Shootyface.Character.CharClass_Shootyface:BehaviorProviderDefinition_0",
        )
        if not (destroyreal and shooty_bpd):
            raise Exception("Could not locate objects for McShooty")

        destroyreal.OutputLinks[0].Links = ()

        ready_event_data = shooty_bpd.BehaviorSequences[1].EventData2[0]
        ready_event_data.OutputLinks.ArrayIndexAndLength = 327681

        dead_event_data = shooty_bpd.BehaviorSequences[2].EventData2[0]
        dead_event_data.OutputLinks.ArrayIndexAndLength = 0


class BFFs(MapDropper):
    paths = ("SanctuaryAir_P",)

    def entered_map(self) -> None:
        toggle0 = FindObject(
            "SeqAct_Toggle",
            "SanctuaryAir_Side.TheWorld:PersistentLevel.Main_Sequence.BFFs.SeqAct_Toggle_0",
        )
        toggle1 = FindObject(
            "SeqAct_Toggle",
            "SanctuaryAir_Side.TheWorld:PersistentLevel.Main_Sequence.BFFs.SeqAct_Toggle_1",
        )
        loaded1 = FindObject(
            "SeqEvent_LevelLoaded",
            "SanctuaryAir_Side.TheWorld:PersistentLevel.Main_Sequence.BFFs.SeqEvent_LevelLoaded_1",
        )
        loaded2 = FindObject(
            "SeqEvent_LevelLoaded",
            "SanctuaryAir_Side.TheWorld:PersistentLevel.Main_Sequence.BFFs.SeqEvent_LevelLoaded_2",
        )
        loaded3 = FindObject(
            "SeqEvent_LevelLoaded",
            "SanctuaryAir_Side.TheWorld:PersistentLevel.Main_Sequence.BFFs.SeqEvent_LevelLoaded_3",
        )
        aiscripted = FindObject(
            "WillowSeqAct_AIScripted",
            "SanctuaryAir_Side.TheWorld:PersistentLevel.Main_Sequence.BFFs.WillowSeqAct_AIScripted_0",
        )
        gamestage_region = FindObject(
            "WillowRegionDefinition", "GD_GameStages.Zone3.Sanctuary_C"
        )

        if not (
            toggle0
            and toggle1
            and loaded1
            and loaded2
            and loaded3
            and aiscripted
            and gamestage_region
        ):
            raise Exception("Could not locate objects for BFFs")

        loaded1.OutputLinks[0].Links[0].LinkedOp = toggle1
        loaded1.OutputLinks[0].Links[1].LinkedOp = toggle0
        loaded2.OutputLinks[0].Links[0].LinkedOp = toggle1
        loaded3.OutputLinks[0].Links[0].LinkedOp = toggle0

        aiscripted.InputLinks[0].bDisabled = True

        for path in (
            "SanctuaryAir_Side.TheWorld:PersistentLevel.WillowPopulationOpportunityPoint_1",
            "SanctuaryAir_Side.TheWorld:PersistentLevel.WillowPopulationOpportunityPoint_6",
            "SanctuaryAir_Side.TheWorld:PersistentLevel.WillowPopulationOpportunityPoint_7",
            "SanctuaryAir_Side.TheWorld:PersistentLevel.WillowPopulationOpportunityPoint_8",
        ):
            population = FindObject("WillowPopulationOpportunityPoint", path)
            if not population:
                raise Exception("Could not locate populations for BFFs")
            population.GameStageRegion = gamestage_region


class PoeticLicense(MapDropper):
    paths = ("SanctuaryAir_P",)

    def entered_map(self) -> None:
        daisy_den = FindObject(
            "PopulationOpportunityDen",
            "SanctuaryAir_Dynamic.TheWorld:PersistentLevel.PopulationOpportunityDen_2",
        )
        daisy_ai = FindObject(
            "AIBehaviorProviderDefinition",
            "GD_Daisy.Character.AIDef_Daisy:AIBehaviorProviderDefinition_1",
        )
        seq_objective = FindObject(
            "SeqAct_ApplyBehavior",
            "SanctuaryAir_Dynamic.TheWorld:PersistentLevel.Main_Sequence.PoeticLicense.SeqAct_ApplyBehavior_1",
        )
        timetodie = FindObject(
            "SeqEvent_RemoteEvent",
            "SanctuaryAir_Dynamic.TheWorld:PersistentLevel.Main_Sequence.PoeticLicense.SeqEvent_RemoteEvent_2",
        )
        gamestageregion = FindObject(
            "WillowRegionDefinition", "GD_GameStages.Zone2.Cliffs_A"
        )
        if not (
            daisy_den
            and daisy_ai
            and seq_objective
            and timetodie
            and gamestageregion
        ):
            raise Exception("Could not locate objects for Daisy")

        daisy_den.GameStageRegion = gamestageregion

        daisy_ai.BehaviorSequences[2].BehaviorData2[
            11
        ].Behavior = construct_object("Behavior_Kill", daisy_ai)

        dialog_behavior_data = daisy_ai.BehaviorSequences[2].BehaviorData2[15]
        dialog_behavior_data.Behavior.EventTag = None

        die_behavior_data = daisy_ai.BehaviorSequences[5].BehaviorData2[2]
        die_behavior_data.OutputLinks.ArrayIndexAndLength = 1

        timetodie.OutputLinks[0].Links = ((seq_objective, 0),)


class WrittenByTheVictor(MapDropper):
    paths = ("HyperionCity_P",)

    def entered_map(self) -> None:
        buttonlocked = FindObject(
            "Behavior_ChangeRemoteBehaviorSequenceState",
            "HyperionCity_Dynamic.TheWorld:PersistentLevel.Main_Sequence.WrittenByVictor.SeqAct_ApplyBehavior_2.Behavior_ChangeRemoteBehaviorSequenceState_190",
        )
        if not buttonlocked:
            raise Exception(
                "Could not locate button for Written By The Victor"
            )
        buttonlocked.Action = 2


class ARealBoy(MapDropper):
    # TODO: fix mal not spawning during/after talon of god + real boy
    paths = ("Ash_P",)

    def entered_map(self) -> None:
        mal_ai = FindObject(
            "BehaviorProviderDefinition",
            "GD_PinocchioBot.Character.CharClass_PinocchioBot:BehaviorProviderDefinition_84",
        )
        if not mal_ai:
            raise Exception("Could not locate Mal for A Real Boy")

        finished_event_data = mal_ai.BehaviorSequences[12].EventData2[0]
        finished_event_data.OutputLinks.ArrayIndexAndLength = 0


class GreatEscape(MissionStatusDelegate, MapDropper):
    paths = ("CraterLake_P",)

    def completed(self) -> None:
        missiondef = self.location.mission_definition.uobject
        missiondef.bRepeatable = False

    def entered_map(self) -> None:
        missiondef = self.location.mission_definition.uobject
        missiondef.bRepeatable = True

        ulysses: Optional[UObject] = None
        for pawn in get_pawns():
            if pawn.AIClass and pawn.AIClass.Name == "CharClass_Ulysses":
                ulysses = pawn
                break

        ulysses_loaded = FindObject(
            "SeqEvent_LevelLoaded",
            "CraterLake_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Ulysess.SeqEvent_LevelLoaded_0",
        )
        ulysses_savestate = FindObject(
            "SeqEvent_RemoteEvent",
            "CraterLake_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Ulysess.SeqEvent_RemoteEvent_1",
        )

        if not (ulysses and ulysses_loaded and ulysses_savestate):
            raise Exception("Could not locate Ulysses for Great Escape")

        if not is_client():
            get_missiontracker().RegisterMissionDirector(ulysses)

        ulysses_loaded.OutputLinks[0].Links = ()
        ulysses_savestate.OutputLinks[0].Links = ()

        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            if caller.AIClass.Name != "CharClass_Ulysses":
                return True

            spawn_loot(
                self.location.prepare_pools(),
                self.location.mission_definition.uobject,
                location=(26075, 25255, 10026),
                velocity=(-855, 565, 0),
            )

            return True

        RunHook(
            "WillowGame.WillowAIPawn.Died", f"LootRandomizer.{id(self)}", hook
        )

    def exited_map(self) -> None:
        RemoveHook(
            "WillowGame.WillowAIPawn.Died", f"LootRandomizer.{id(self)}"
        )


class MessageInABottle(MissionStatusDelegate, MapDropper):
    path: Optional[str]

    def __init__(self, path: Optional[str], map_name: str) -> None:
        self.path = path
        super().__init__(map_name)

    def accepted(self) -> None:
        for chest in FindAll("WillowInteractiveObject"):
            if (
                chest.InteractiveObjectDefinition
                and UObject.PathName(chest.InteractiveObjectDefinition)
                == "GD_Orchid_SM_Message_Data.MO_Orchid_XMarksTheSpot"
            ):
                missiondef = self.location.mission_definition.uobject
                directive = (missiondef, False, True)
                chest.AddMissionDirective(directive, True)

    def entered_map(self) -> None:
        bottle_bpd = FindObject(
            "BehaviorProviderDefinition",
            "GD_Orchid_SM_Message_Data.MessageBottle.MO_Orchid_MessageBottle:BehaviorProviderDefinition_3",
        )
        bottle_active = FindObject(
            "Behavior_ChangeRemoteBehaviorSequenceState",
            "GD_Orchid_Plot.M_Orchid_PlotMission01:Behavior_ChangeRemoteBehaviorSequenceState_6",
        )
        if not (bottle_bpd and bottle_active):
            raise Exception("Could not locate bottle for Message In A Bottle")

        bottle_bpd.BehaviorSequences[1].BehaviorData2[
            0
        ].Behavior = bottle_active
        bottle_bpd.BehaviorSequences[1].BehaviorData2[
            0
        ].OutputLinks.ArrayIndexAndLength = 0

        if self.path:
            chest_state = FindObject(
                "BehaviorSequenceEnableByMission", self.path
            )
            if chest_state:
                chest_state.MissionStatesToLinkTo.bComplete = False


class CommercialAppeal(MissionStatusDelegate, MapDropper):
    paths = ("Iris_DL3_P",)

    objective: UObject

    def enable(self) -> None:
        super().enable()

        objective = FindObject(
            "MissionObjectiveDefinition",
            "GD_IrisDL3_CommAppeal.M_IrisDL3_CommAppeal:KillGuys",
        )
        if not objective:
            raise Exception("Could not locate objective for X-Communicate")
        self.objective = objective

        self.objective.KillRestrictions.bMissionWeapon = False
        self.objective.KillRestrictions.bCriticalHit = True
        self.objective.KillRestrictions.bNotCriticalHit = True

    def disable(self) -> None:
        super().disable()

        if self.objective:
            self.objective.KillRestrictions.bMissionWeapon = True
            self.objective.KillRestrictions.bCriticalHit = False
            self.objective.KillRestrictions.bNotCriticalHit = False

    def accepted(self) -> None:
        self.apply()

    def completed(self) -> None:
        self.unapply()

    def entered_map(self) -> None:
        if self.location.current_status == Mission.Status.Active:
            self.apply()

    def exited_map(self) -> None:
        self.unapply()

    def apply(self) -> None:
        def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
            objective = caller.MissionObjectiveToUpdateOnDeath
            if not (
                objective
                and UObject.PathName(objective)
                == "GD_IrisDL3_CommAppeal.M_IrisDL3_CommAppeal:KillGuys"
            ):
                return True

            killer = params.Killer
            if not (killer and killer.Class.Name == "WillowPlayerController"):
                return True

            weapon = killer.Pawn.Weapon
            if not weapon:
                return True

            make = weapon.DefinitionData.ManufacturerDefinition.Name
            if make == "Torgue":
                get_missiontracker().UpdateObjective(self.objective)
            return True

        RunHook(
            "WillowGame.WillowAIPawn.Died", f"LootRandomizer.{id(self)}", hook
        )

    def unapply(self) -> None:
        RemoveHook(
            "WillowGame.WillowAIPawn.Died",
            f"LootRandomizer.{id(self)}",
        )


class RollInsight(MissionGiver):
    def apply(self) -> Optional[UObject]:
        directives = super().apply()

        die = FindObject(
            "WillowInteractiveObject",
            "Village_Mission.TheWorld:PersistentLevel.WillowInteractiveObject_297",
        )
        if not die:
            raise Exception("Could not locate die for Roll Insight")
        handle = (die.ConsumerHandle.PID,)
        bpd = die.InteractiveObjectDefinition.BehaviorProviderDefinition

        kernel = get_behaviorkernel()
        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "Complete", 2
        )
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "TurnIn", 1)

        die.SetMissionDirectivesUsability(1)
        if not is_client():
            get_missiontracker().RegisterMissionDirector(die)

        return directives


class TreeHugger(MapDropper):
    paths = ("Dark_Forest_P",)

    def entered_map(self) -> None:
        for pawn in get_pawns():
            if (
                pawn.AIClass
                and pawn.AIClass.Name == "CharClass_Aster_Treant_TreeHuggerNPC"
            ):
                handle = (pawn.ConsumerHandle.PID,)
                bpd = pawn.AIClass.BehaviorProviderDefinition
                kernel = get_behaviorkernel()

                enable = bpd.BehaviorSequences[1].CustomEnableCondition
                enable.EnableConditions = (enable.EnableConditions[0],)
                kernel.ChangeBehaviorSequenceActivationStatus(
                    handle, bpd, "DuringMission", 2
                )
                break


class LostSouls(MissionGiver):
    def apply(self) -> Optional[UObject]:
        directives = super().apply()
        for pawn in get_pawns():
            if pawn.MissionDirectives == directives:
                handle = (pawn.ConsumerHandle.PID,)
                bpd = pawn.AIClass.AIDef.BehaviorProviderDefinition
                kernel = get_behaviorkernel()
                kernel.ChangeBehaviorSequenceActivationStatus(
                    handle, bpd, "Mission", 1
                )
                pawn.SetUsable(True, None, 0)
                if not is_client():
                    get_missiontracker().RegisterMissionDirector(pawn)

    def entered_map(self) -> None:
        missiondef = self.location.mission_definition.uobject
        if get_missiontracker().GetMissionStatus(missiondef) == 4:
            skel_den = FindObject(
                "PopulationOpportunityDen",
                "Dead_Forest_Mission.TheWorld:PersistentLevel.PopulationOpportunityDen_19",
            )
            knight_den = FindObject(
                "PopulationOpportunityDen",
                "Dead_Forest_Mission.TheWorld:PersistentLevel.PopulationOpportunityDen_13",
            )
            if not (skel_den and knight_den):
                raise Exception("Could not locate dens for Lost Souls")

            skel_den.IsEnabled = True
            knight_den.IsEnabled = False


class MyDeadBrother(MissionDropper, MapDropper):
    paths = ("Dungeon_P",)

    def entered_map(self) -> None:
        missiondef = self.location.mission_definition.uobject
        if get_missiontracker().GetMissionStatus(missiondef) != 4:
            return

        simon_enabled = FindObject(
            "BehaviorSequenceEnableByMission",
            "GD_Wizard_DeadBrotherSimon_Proto2.Character.CharClass_Wizard_DeadBrotherSimon_Proto2:BehaviorProviderDefinition_5.BehaviorSequenceEnableByMission_9",
        )
        simon_talking = FindObject(
            "BehaviorSequenceEnableByMission",
            "GD_Wizard_DeadBrotherSimon_Proto2.Character.CharClass_Wizard_DeadBrotherSimon_Proto2:BehaviorProviderDefinition_5.BehaviorSequenceEnableByMission_7",
        )
        simon_bpd = FindObject(
            "BehaviorProviderDefinition",
            "GD_Wizard_DeadBrotherSimon_Proto2.Character.CharClass_Wizard_DeadBrotherSimon_Proto2:BehaviorProviderDefinition_5",
        )
        simon_den = FindObject(
            "PopulationOpportunityDen",
            "Dungeon_Mission.TheWorld:PersistentLevel.PopulationOpportunityDen_68",
        )

        if not (simon_enabled and simon_talking and simon_bpd and simon_den):
            raise Exception("Could not locate Simon for My Dead Brother")

        simon_enabled.MissionStatesToLinkTo.bComplete = True
        simon_talking.MissionStatesToLinkTo.bComplete = False

        simon_bpd.BehaviorSequences[4].BehaviorData2[
            1
        ].Behavior = construct_behaviorsequence_behavior(
            "GD_Wizard_DeadBrotherSimon_Proto2",
            "Character",
            "CharClass_Wizard_DeadBrotherSimon_Proto2",
            "BehaviorProviderDefinition_5",
            sequence="TurnInSimon",
            outer=simon_bpd,
        )

        simon_den.IsEnabled = True


class OddestCouple(MissionObject):
    def apply(self) -> Optional[UObject]:
        door = super().apply()
        if door:
            handle = (door.ConsumerHandle.PID,)
            bpd = door.InteractiveObjectDefinition.BehaviorProviderDefinition

            kernel = get_behaviorkernel()
            kernel.ChangeBehaviorSequenceActivationStatus(
                handle, bpd, "S020_Brain", 1
            )
            kernel.ChangeBehaviorSequenceActivationStatus(
                handle, bpd, "S020_TurnIn", 1
            )

        return door


class Sirentology(MapDropper):
    paths = ("BackBurner_P",)

    def entered_map(self) -> None:
        for pawn in get_pawns():
            if (
                pawn.AIClass
                and pawn.AIClass.Name == "CharClass_mone_GD_Lilith"
            ):
                handle = (pawn.ConsumerHandle.PID,)
                ai_bpd = pawn.AIClass.AIDef.BehaviorProviderDefinition
                kernel = get_behaviorkernel()

                kernel.ChangeBehaviorSequenceActivationStatus(
                    handle, ai_bpd, "S050_GiveMission", 1
                )
                break


class EchoesOfThePast(MissionObject):
    def apply(self) -> Optional[UObject]:
        echo = super().apply()
        if echo:
            handle = (echo.ConsumerHandle.PID,)
            bpd = echo.InteractiveObjectDefinition.BehaviorProviderDefinition

            kernel = get_behaviorkernel()
            kernel.ChangeBehaviorSequenceActivationStatus(
                handle, bpd, "S080_MissionGiver", 1
            )

        return echo


class GrandmaStoryRaid(MapDropper):
    paths = ("Hunger_P",)

    def entered_map(self) -> None:
        granma_ai = FindObject(
            "AIBehaviorProviderDefinition",
            "GD_Allium_TorgueGranma.Character.AIDef_Torgue:AIBehaviorProviderDefinition_0",
        )
        if not granma_ai:
            raise Exception("Could not locate Granma for Grandma Story Raid")

        event_data = granma_ai.BehaviorSequences[1].EventData2
        event_data[0].OutputLinks.ArrayIndexAndLength = 655361
        event_data[3].OutputLinks.ArrayIndexAndLength = 655361


class MichaelMamaril(MapDropper):
    paths = ("Sanctuary_P", "SanctuaryAir_P")

    def entered_map(self) -> None:
        switch = locations.map_name.replace(
            "_P".casefold(),
            "_Dynamic.TheWorld:PersistentLevel.Main_Sequence.SeqAct_RandomSwitch_0",
        )
        set_command(switch, "LinkCount", "2")


class DahlAbandonGrave(MapDropper):
    paths = ("OldDust_P",)

    def entered_map(self) -> None:
        grave_bpd = FindObject(
            "BehaviorProviderDefinition",
            "GD_Anemone_Balance_Treasure.InteractiveObjects.InteractiveObj_Brothers_Pile:BehaviorProviderDefinition_13",
        )
        if not grave_bpd:
            raise Exception("Could not locate BPD for Dahl Abandon Grave")
        behavior_data = grave_bpd.BehaviorSequences[2].BehaviorData2
        behavior_data[3].Behavior = behavior_data[5].Behavior


class ButtstallionWithAmulet(MapDropper):
    paths = ("BackBurner_P",)

    def entered_map(self) -> None:
        butt_ai = FindObject(
            "AIBehaviorProviderDefinition",
            "GD_Anem_ButtStallion.Character.AIDef_Anem_ButtStallion:AIBehaviorProviderDefinition_1",
        )
        if not butt_ai:
            raise Exception("Could not locate AI for Buttstallion With Amulet")

        behavior_data = butt_ai.BehaviorSequences[5].BehaviorData2
        output_links = behavior_data[26].OutputLinks.ArrayIndexAndLength

        behavior_data[20].Behavior = behavior_data[26].Behavior
        behavior_data[20].LinkedVariables.ArrayIndexAndLength = 0
        behavior_data[20].OutputLinks.ArrayIndexAndLength = output_links


# fmt: off

Locations: Sequence[locations.Location] = (
    Other("Playthrough Delegate", PlaythroughDelegate(), tags=Tag.Excluded),
    Other("Marketing Bonuses", MarketingBonuses(), tags=Tag.Excluded),

    Enemy("Knuckle Dragger", Pawn("PawnBalance_PrimalBeast_KnuckleDragger")),
    Mission("This Town Ain't Big Enough", MissionDefinition("GD_Z1_ThisTown.M_ThisTown")),
    Mission("Shielded Favors", MissionDefinition("GD_Episode02.M_Ep2b_Henchman")),
    Mission("Bad Hair Day (Turn in Hammerlock)", MissionDefinition("GD_Z1_BadHairDay.M_BadHairDay")),
    Mission("Bad Hair Day (Turn in Claptrap)", MissionTurnInAlt("GD_Z1_BadHairDay.M_BadHairDay")),
    Mission("Symbiosis", MissionDefinition("GD_Z1_Symbiosis.M_Symbiosis"), tags=Tag.LongMission),
    Enemy("Midgemong", Pawn("PawnBalance_PrimalBeast_Warmong"), tags=Tag.SlowEnemy),
    Mission("Handsome Jack Here!", MissionDefinition("GD_Z1_HandsomeJackHere.M_HandsomeJackHere")),
        # bandit camp enemies dont drop echo again
    Enemy("Boom", Pawn("PawnBalance_BoomBoom")),
    Enemy("Bewm", Pawn("PawnBalance_Boom")),
    Enemy("Captain Flynt", Pawn("PawnBalance_Flynt"), tags=Tag.SlowEnemy, rarities=(33,33,33)),
    Enemy("Savage Lee", Pawn("PawnBalance_SavageLee")),
    Other("Michael Mamaril", Behavior("GD_JohnMamaril.Character.AIDef_JohnMamaril:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_92"),
        MichaelMamaril(),
    tags=Tag.Freebie),
    Other("Tip Moxxi", Behavior(
        "GD_Moxxi.Character.CharClass_Moxxi:BehaviorProviderDefinition_3.Behavior_SpawnItems_17",
        "GD_Moxxi.Character.CharClass_Moxxi:BehaviorProviderDefinition_3.Behavior_SpawnItems_23",
    ), tags=Tag.Freebie),
    Mission("Claptrap's Secret Stash", MissionDefinition("GD_Z1_ClapTrapStash.M_ClapTrapStash"), tags=Tag.Freebie),
    Mission("Do No Harm", MissionDefinition("GD_Z1_Surgery.M_PerformSurgery"), tags=Tag.Freebie),
    Mission("Rock, Paper, Genocide: Fire Weapons!", MissionDefinition("GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Fire"), tags=Tag.Freebie),
    Mission("Rock, Paper, Genocide: Shock Weapons!", MissionDefinition("GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Shock"), tags=Tag.Freebie),
    Mission("Rock, Paper, Genocide: Corrosive Weapons!", MissionDefinition("GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Corrosive"), tags=Tag.Freebie),
    Mission("Rock, Paper, Genocide: Slag Weapons!", MissionDefinition("GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Amp"), tags=Tag.Freebie),
    Mission("The Name Game", MissionDefinition("GD_Z1_NameGame.M_NameGame"), tags=Tag.LongMission),
    Mission("Assassinate the Assassins", MissionDefinition("GD_Z1_Assasinate.M_AssasinateTheAssassins"), tags=Tag.LongMission),
    Enemy("Assassin Wot", Pawn("PawnBalance_Assassin1")),
    Enemy("Assassin Oney", Pawn("PawnBalance_Assassin2")),
    Enemy("Assassin Reeth", Pawn("PawnBalance_Assassin3"), tags=Tag.SlowEnemy),
    Enemy("Assassin Rouf", Pawn("PawnBalance_Assassin4"), tags=Tag.SlowEnemy),
    Mission("Medical Mystery", MissionDefinition("GD_Z3_MedicalMystery.M_MedicalMystery")),
    Enemy("Doc Mercy", Pawn("PawnBalance_MrMercy")),
    Mission("Medical Mystery: X-Com-municate", MissionDefinition("GD_Z3_MedicalMystery2.M_MedicalMystery2"),
        MissionGiver("GD_Zed.Character.Pawn_Zed:MissionDirectivesDefinition_1", True, True, "Sanctuary_P", "SanctuaryAir_P"),
        MissionGiver("Frost_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_413.MissionDirectivesDefinition_0", False, False, "Frost_P"),
        XCom(),
    tags=Tag.LongMission),
    # TODO: Fix residual "!" above Mercy corpse
    Mission("No Vacancy", MissionDefinition("GD_Z1_NoVacancy.BalanceDefs.M_NoVacancy"),
        MissionGiver("Frost_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_32.MissionDirectivesDefinition_0", True, True, "Frost_P")
    ),
    Mission("Neither Rain nor Sleet nor Skags", MissionDefinition("gd_z3_neitherrainsleet.M_NeitherRainSleetSkags")),
    Enemy("Loot Midget",
        Midget(
            "PawnBalance_Jimmy",
            "PawnBalance_LootMidget_CombatEngineer",
            "PawnBalance_LootMidget_Engineer",
            "PawnBalance_LootMidget_LoaderGUN",
            "PawnBalance_LootMidget_LoaderJET",
            "PawnBalance_LootMidget_LoaderWAR",
            "PawnBalance_LootMidget_Marauder",
            "PawnBalance_LootMidget_Goliath",
            "PawnBalance_LootMidget_Nomad",
            "PawnBalance_LootMidget_Psycho",
            "PawnBalance_LootMidget_Rat"
        ),
        DoctorsOrdersMidgetRegistry(),
    tags=Tag.VeryRareEnemy),
    Enemy("Chubby/Tubby",
        Pawn(
            "PawnBalance_BugMorphChubby",
            "PawnBalance_MidgetChubby",
            "PawnBalance_RakkChubby",
            "PawnBalance_SkagChubby",
            "PawnBalance_SpiderantChubby",
            "PawnBalance_StalkerChubby",
            "PawnBalance_SkagChubby_Orchid",
            "PawnBalance_SpiderantChubby_Orchid",
            "PawnBalance_Orchid_StalkerChubby",
            "PawnBalance_SkeletonChubby"
        ),
    tags=Tag.VeryRareEnemy),
    Enemy("GOD-liath",
        Pawn(
            "PawnBalance_Goliath",
            "PawnBalance_GoliathBadass",
            "PawnBalance_GoliathCorrosive",
            "PawnBalance_DiggerGoliath",
            "PawnBalance_GoliathBlaster",
            "PawnBalance_GoliathLootGoon",
            "PawnBalance_LootMidget_Goliath",
            "PawnBalance_MidgetGoliath",
            "Iris_PawnBalance_ArenaGoliath",
            "PawnBalance_InfectedGoliath",
            "PawnBalance_Infected_Badass_Goliath",
            "PawnBalance_Infected_Gargantuan_Goliath",
            "PawnBalance_GoliathSnow",
            "PawnBalance_GoliathBride",
            "PawnBalance_GoliathBrideRaid",
            "PawnBalance_GoliathGroom",
            "PawnBalance_GoliathGroomRaid",
        transform=5),
    tags=Tag.EvolvedEnemy),
    Other("Frostburn Canyon Cave Pool", Behavior("Env_IceCanyon.InteractiveObjects.LootSpawner:BehaviorProviderDefinition_0.Behavior_SpawnItems_22")),
    Mission("Cult Following: Eternal Flame", MissionDefinition("GD_Z1_ChildrenOfPhoenix.M_EternalFlame")),
    Mission("Cult Following: False Idols", MissionDefinition("GD_Z1_ChildrenOfPhoenix.M_FalseIdols")),
    Enemy("Scorch", Pawn("PawnBalance_SpiderantScorch")),
    Mission("Cult Following: Lighting the Match", MissionDefinition("GD_Z1_ChildrenOfPhoenix.M_LightingTheMatch"), tags=Tag.LongMission),
    Mission("Cult Following: The Enkindling", MissionDefinition("GD_Z1_ChildrenOfPhoenix.M_TheEnkindling"),
        PreventDestroy("GD_IncineratorVanya.Character.AIDef_IncineratorVanya:AIBehaviorProviderDefinition_1.Behavior_Destroy_0"),
    tags=Tag.LongMission),
    Enemy("Incinerator Clayton", Pawn("PawnBalance_IncineratorVanya_Combat"), tags=Tag.SlowEnemy),
    Mission("In Memoriam", MissionDefinition("GD_Z1_InMemoriam.M_InMemoriam")),
    Enemy("Boll", Pawn("PawnBalance_Boll")),
    Other("What's In The Box?", Attachment("ObjectGrade_WhatsInTheBox"), tags=Tag.Freebie),
    Enemy("The Black Queen", Pawn("PawnBalance_SpiderantBlackQueen"), tags=Tag.SlowEnemy|Tag.RareEnemy),
    Mission("Too Close For Missiles", MissionDefinition("gd_z3_toocloseformissiles.M_TooCloseForMissiles")),
    Enemy("Shirtless Man", Pawn("PawnBalance_ShirtlessMan"), mission="Too Close For Missiles"),
    Mission("Positive Self Image", MissionDefinition("GD_Z3_PositiveSelfImage.M_PositiveSelfImage"), tags=Tag.VehicleMission),
    Enemy("Bad Maw", Pawn("PawnBalance_BadMaw")),
    Enemy("Mad Mike", Pawn("PawnBalance_MadMike"), tags=Tag.SlowEnemy),
    Mission("Out of Body Experience (Turn in Marcus)", MissionDefinition("GD_Z3_OutOfBody.M_OutOfBody"), Loader1340(), tags=Tag.LongMission), 
    Mission("Out of Body Experience (Turn in Dr. Zed)", MissionTurnInAlt("GD_Z3_OutOfBody.M_OutOfBody"), tags=Tag.LongMission), 
        # Construct/War Loader 1340 dont respawn without savequit
    Enemy("Loader #1340",
        Pawn("PawnBalance_Constructor_1340", "PawnBalance_LoaderWAR_1340"),
        Radio1340(),
    mission="Out of Body Experience (Turn in Marcus)"),
    Mission("Splinter Group", MissionDefinition("GD_Z2_SplinterGroup.M_SplinterGroup")),
    Enemy("Lee", Pawn("PawnBalance_Lee")),
    Enemy("Dan", Pawn("PawnBalance_Dan")),
    Enemy("Ralph", Pawn("PawnBalance_Ralph")),
    Enemy("Mick", Pawn("PawnBalance_Mick")),
    Enemy("Flinter", Pawn("PawnBalance_RatEasterEgg")),
    Other("Tundra Express Snowman Head",
        Attachment("BD_Ep7_SnowManHead_Ammo"),
        Attachment("BD_Ep7_SnowManHead_FlareGun"),
    tags=Tag.Freebie),
    Enemy("Ultimate Badass Varkid", Pawn("PawnBalance_BugMorphUltimateBadass"), tags=Tag.EvolvedEnemy|Tag.VeryRareEnemy),
    Enemy("Vermivorous the Invincible", Pawn("PawnBalance_BugMorphRaid"), tags=Tag.EvolvedEnemy|Tag.VeryRareEnemy|Tag.Raid),
    Mission("Mighty Morphin'", MissionDefinition("GD_Z1_MightyMorphin.M_MightyMorphin")),
    Enemy("Mutated Badass Varkid", Pawn("PawnBalance_BugMorphBadass_Mutated"), mission="Mighty Morphin'"),
    Mission("No Hard Feelings", MissionDefinition("gd_z1_nohardfeelings.M_NoHardFeelings"), WillTheBandit()), 
        # Will doesnt respawn
    Mission("You Are Cordially Invited: Party Prep", MissionDefinition("GD_Z1_CordiallyInvited.M_CordiallyInvited")),
    Enemy("Madame Von Bartlesby", Pawn("PawnBalance_SirReginald")),
    Mission("You Are Cordially Invited: RSVP", MissionDefinition("GD_Z1_CordiallyInvited.M_CordiallyInvited02"), tags=Tag.LongMission),
        # Respawn Fleshstick withour map reload (remove LongMission tag)
    Enemy("Flesh-Stick", Pawn("PawnBalance_FleshStick"), mission="You Are Cordially Invited: RSVP"),
    Mission("You Are Cordially Invited: Tea Party", MissionDefinition("GD_Z1_CordiallyInvited.M_CordiallyInvited03")),
    Mission("Mine, All Mine", MissionDefinition("GD_Z1_MineAllMine.M_MineAllMine"), tags=Tag.LongMission),
    Enemy("Prospector Zeke", Pawn("PawnBalance_Prospector"), tags=Tag.SlowEnemy),
    Mission("The Pretty Good Train Robbery", MissionDefinition("GD_Z1_TrainRobbery.M_TrainRobbery")),
        # Train chests do not reset without relog
    Enemy("Wilhelm", Pawn("PawnBalance_Willhelm")),
    Mission("The Good, the Bad, and the Mordecai", MissionDefinition("GD_Z3_GoodBadMordecai.M_GoodBadMordecai"), tags=Tag.LongMission),
    Enemy("Mobley", Pawn("PawnBalance_Mobley"), tags=Tag.SlowEnemy),
    Enemy("Gettle", Pawn("PawnBalance_Gettle"), tags=Tag.SlowEnemy),
    Enemy("Badass Creeper", Pawn("PawnBalance_CreeperBadass"), tags=Tag.SlowEnemy, rarities=(50,)),
    Mission("The Ice Man Cometh", MissionDefinition("GD_Z1_IceManCometh.M_IceManCometh")),
        # Dynamite interactable but invisible on repeat
    Mission("Bandit Slaughter: Round 1", MissionDefinition("GD_Z1_BanditSlaughter.M_BanditSlaughter1"), tags=Tag.Slaughter),
    Mission("Bandit Slaughter: Round 2", MissionDefinition("GD_Z1_BanditSlaughter.M_BanditSlaughter2"), tags=Tag.Slaughter),
    Mission("Bandit Slaughter: Round 3", MissionDefinition("GD_Z1_BanditSlaughter.M_BanditSlaughter3"), tags=Tag.Slaughter|Tag.LongMission),
    Mission("Bandit Slaughter: Round 4", MissionDefinition("GD_Z1_BanditSlaughter.M_BanditSlaughter4"), tags=Tag.Slaughter|Tag.LongMission),
    Mission("Bandit Slaughter: Round 5", MissionDefinition("GD_Z1_BanditSlaughter.M_BanditSlaughter5"), tags=Tag.Slaughter|Tag.VeryLongMission),
        # double-check repeating mission with no save-quit
    Mission("Won't Get Fooled Again", MissionDefinition("GD_Z1_WontGetFooled.M_WontGetFooled"), tags=Tag.Freebie),
    Enemy("Barlo Gutter", Pawn("BD_BarloGutter"), mission="Won't Get Fooled Again"),
    Mission("Claptrap's Birthday Bash!", MissionDefinition("GD_Z2_ClaptrapBirthdayBash.M_ClaptrapBirthdayBash"), tags=Tag.Freebie),
        # No pizza or noisemaker prompts on repeat
    Mission("Slap-Happy", MissionDefinition("GD_Z2_SlapHappy.M_SlapHappy")),
    Enemy("Old Slappy", Pawn("PawnBalance_Slappy")),
    Mission("Hidden Journals", MissionDefinition("GD_Z3_HiddenJournals.M_HiddenJournals")),
    Mission("Torture Chairs", MissionDefinition("GD_Z1_HiddenJournalsFurniture.M_HiddenJournalsFurniture"), tags=Tag.Freebie),
    Mission("Arms Dealing", MissionDefinition("GD_Z2_ArmsDealer.M_ArmsDealer"), tags=Tag.VehicleMission),
    Mission("Stalker of Stalkers", MissionDefinition("GD_Z2_TaggartBiography.M_TaggartBiography")),
    Mission("Best Mother's Day Ever", MissionDefinition("GD_Z2_MothersDayGift.BalanceDefs.M_MothersDayGift")),
    Enemy("Henry", Pawn("PawnBalance_Henry")),
    Mission("The Overlooked: Medicine Man", MissionDefinition("GD_Z2_Overlooked.M_Overlooked"), tags=Tag.LongMission),
    Enemy("Requisition Officer", Pawn("PawnBalance_RequisitionOfficer"), mission="The Overlooked: Medicine Man"),
    Mission("The Overlooked: Shields Up", MissionDefinition("GD_Z2_Overlooked2.M_Overlooked2")),
    Mission("The Overlooked: This Is Only a Test", MissionDefinition("GD_Z2_Overlooked3.M_Overlooked3"),
        MissionObject("Grass_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_48", "Grass_P"),
    ),
    Mission("Clan War: Starting the War", MissionDefinition("GD_Z2_MeetWithEllie.M_MeetWithEllie")),
    Mission("Clan War: First Place", MissionDefinition("GD_Z2_RiggedRace.M_RiggedRace")),
    Mission("Clan War: Reach the Dead Drop", MissionDefinition("GD_Z2_LuckysDirtyMoney.M_FamFeudDeadDrop"), tags=Tag.Freebie),
    Mission("Clan War: End of the Rainbow", MissionDefinition("GD_Z2_LuckysDirtyMoney.M_LuckysDirtyMoney"),
        MissionObject("Luckys_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_2788", "Luckys_P"),
    ),
    Enemy("Bagman", Pawn("PawnBalance_Leprechaun"), mission="Clan War: End of the Rainbow"),
    Mission("Clan War: Trailer Trashing", MissionDefinition("GD_Z2_TrailerTrashin.M_TrailerTrashin")),
        # Gas tanks do not reset without relog
    Mission("Clan War: Wakey Wakey", MissionDefinition("GD_Z2_WakeyWakey.M_WakeyWakey"), tags=Tag.Freebie),
    Mission("Clan War: Zafords vs. Hodunks (Kill Hodunks)", MissionDefinition("GD_Z2_DuelingBanjos.M_DuelingBanjos")),
    Enemy("Tector Hodunk", Pawn("PawnBalance_TectorHodunk_Combat")),
    Mission("Clan War: Zafords vs. Hodunks (Kill Zafords)", MissionTurnInAlt("GD_Z2_DuelingBanjos.M_DuelingBanjos")),
    Enemy("Mick Zaford", Pawn("PawnBalance_MickZaford_Combat")),
    Mission("Safe and Sound (Turn in Marcus)", MissionDefinition("GD_Z2_SafeAndSound.M_SafeAndSound")),
    Mission("Safe and Sound (Turn in Moxxi)", MissionTurnInAlt("GD_Z2_SafeAndSound.M_SafeAndSound")),
    Enemy("Blue", Pawn("PawnBalance_Blue")),
    Mission("Minecart Mischief", MissionDefinition("gd_z1_minecartmischief.M_MinecartMischief"),
        MissionPickup("Caverns_Dynamic.TheWorld:PersistentLevel.WillowMissionPickupSpawner_0", "Caverns_P"),
    tags=Tag.LongMission),
    Mission("Perfectly Peaceful", MissionDefinition("GD_Z1_PerfectlyPeaceful.M_PerfectlyPeaceful"), tags=Tag.LongMission),
    Mission("The Cold Shoulder", MissionDefinition("GD_Z3_ColdShoulder.M_ColdShoulder")),
    Enemy("Laney White", Pawn("PawnBalance_Laney")),
    Mission("Swallowed Whole", MissionDefinition("GD_Z3_SwallowedWhole.M_SwallowedWhole")),
    Enemy("Sinkhole", Pawn("PawnBalance_Stalker_SwallowedWhole"), tags=Tag.SlowEnemy),
    Enemy("Shorty", Pawn("PawnBalance_Midge"), tags=Tag.SlowEnemy),
    Mission("Note for Self-Person", MissionDefinition("gd_z2_notetoself.M_NoteToSelf")),
    Enemy("Smash-Head", Pawn("PawnBalance_SmashHead"), tags=Tag.SlowEnemy),
    Enemy("Rakkman", Pawn("PawnBalance_RakkMan"), tags=Tag.SlowEnemy),
    Mission("Doctor's Orders", MissionDefinition("GD_Z2_DoctorsOrders.M_DoctorsOrders"), tags=Tag.LongMission),
        # Stalker crates with final ECHO arent accessible on repeat
    Enemy("Loot Midget (Doctor's Orders)",
        DoctorsOrdersMidget(
            "PawnBalance_Jimmy",
            "PawnBalance_LootMidget_CombatEngineer",
            "PawnBalance_LootMidget_Engineer",
            "PawnBalance_LootMidget_LoaderGUN",
            "PawnBalance_LootMidget_LoaderJET",
            "PawnBalance_LootMidget_LoaderWAR"
        ),
        DoctorsOrdersMidgetRegistry(),
    mission="Doctor's Orders", rarities=(15,)),
    Enemy("Tumbaa", Pawn("PawnBalance_Tumbaa"), tags=Tag.RareEnemy),
    Enemy("Pimon", Pawn("PawnBalance_Stalker_Simon"), tags=Tag.RareEnemy),
    Mission("Creature Slaughter: Round 1", MissionDefinition("GD_Z2_CreatureSlaughter.M_CreatureSlaughter_1"), tags=Tag.Slaughter),
        # Victory dialog plays upon completing last wave, but no objective update
    Mission("Creature Slaughter: Round 2", MissionDefinition("GD_Z2_CreatureSlaughter.M_CreatureSlaughter_2"), tags=Tag.Slaughter),
        # UBA Varkid doesnt respawn in last wave
    Mission("Creature Slaughter: Round 3", MissionDefinition("GD_Z2_CreatureSlaughter.M_CreatureSlaughter_3"), tags=Tag.Slaughter|Tag.LongMission),
        # Victory dialog plays upon completing last wave, but no objective update
    Mission("Creature Slaughter: Round 4", MissionDefinition("GD_Z2_CreatureSlaughter.M_CreatureSlaughter_4"), tags=Tag.Slaughter|Tag.LongMission),
        # Victory dialog plays and objective updates upon completing last wave, but no turn-in
    Mission("Creature Slaughter: Round 5", MissionDefinition("GD_Z2_CreatureSlaughter.M_CreatureSlaughter_5"), tags=Tag.Slaughter|Tag.VeryLongMission),
        # Fire Thresher doesnt respawn in last wave
    Enemy("Son of Mothrakk", Pawn("PawnBalance_SonMothrakk"), tags=Tag.SlowEnemy, rarities=(100,)),
    Mission("Animal Rights", MissionDefinition("GD_Z2_FreeWilly.M_FreeWilly"), tags=Tag.LongMission),
        # Neither animals nor guards respawn on repeat
    Mission("Rakkaholics Anonymous (Turn in Mordecai)", MissionDefinition("GD_Z2_Rakkaholics.M_Rakkaholics")),
    Mission("Rakkaholics Anonymous (Turn in Moxxi)", MissionTurnInAlt("GD_Z2_Rakkaholics.M_Rakkaholics")),

    Mission("Poetic License", MissionDefinition("GD_Z2_PoeticLicense.M_PoeticLicense"), PoeticLicense(), tags=Tag.Freebie),
        # On repeat, traveling to thousand cuts gives 2/3 photos
        # LOOT DAISY: Daisy should stay outside, no dialog, not gun sound, just die
    Enemy("Daisy", Pawn("BD_Daisy"), mission="Poetic License"),
    Enemy("Muscles", Pawn("PawnBalance_Bruiser_Muscles"), tags=Tag.VeryRareEnemy),
    Mission("Shoot This Guy in the Face", MissionDefinition("GD_Z1_ShootMeInTheFace.M_ShootMeInTheFace"),
        McShooty(),
        MissionGiver("GD_Shootyface.Character.Pawn_Shootyface:MissionDirectivesDefinition_1", True, True, "Grass_Cliffs_P"),
        MissionGiver("Grass_Cliffs_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_725.MissionDirectivesDefinition_0", False, False, "Grass_Cliffs_P"),
    tags=Tag.Freebie),
    Mission("Rocko's Modern Strife", MissionDefinition("GD_Z2_RockosModernStrife.M_RockosModernStrife"), tags=Tag.Freebie),
    Mission("Defend Slab Tower", MissionDefinition("GD_Z2_DefendSlabTower.M_DefendSlabTower")),
        # On repeat, loader waves spawn before other objectives, softlock if killed first

    Mission("Hyperion Contract #873", MissionDefinition("GD_Z3_HyperionContract873.M_HyperionContract873"), tags=Tag.LongMission),
    Mission("The Bane", MissionDefinition("GD_Z3_Bane.M_Bane"),
        MissionPickup("SanctuaryAir_Dynamic.TheWorld:PersistentLevel.WillowMissionPickupSpawner_3", "SanctuaryAir_P"),
    tags=Tag.LongMission),
    Enemy("McNally", Pawn("PawnBalance_McNally")),
    Mission("3:10 to Kaboom", MissionDefinition("GD_Z2_BlowTheBridge.M_BlowTheBridge")),
        # Must fail mission once before repeating to be able to place bomb cart
    Enemy("Mad Dog", Pawn("PawnBalance_MadDog"), tags=Tag.SlowEnemy),
    Mission("Breaking the Bank", MissionDefinition("GD_Z2_TheBankJob.M_TheBankJob"), tags=Tag.LongMission),
        # On repeat, skag pile already broken
    Mission("Showdown", MissionDefinition("GD_Z2_KillTheSheriff.M_KillTheSheriff")),
    Enemy("The Sheriff of Lynchwood", Pawn("PawnBalance_Sheriff")),
    Enemy("Deputy Winger", Pawn("PawnBalance_Deputy")),
    Mission("Animal Rescue: Medicine", MissionDefinition("GD_Z2_Skagzilla2.M_Skagzilla2_Pup"),
        MissionGiver("GD_SkagzillaAdult.Character.Pawn_SkagzillaAdult:MissionDirectivesDefinition_0", True, True, "Grass_Lynchwood_P"),
    ),
    Mission("Animal Rescue: Food", MissionDefinition("GD_Z2_Skagzilla2.M_Skagzilla2_Adult")),
        # On repeat, cannot place food
    Mission("Animal Rescue: Shelter", MissionDefinition("GD_Z2_Skagzilla2.M_Skagzilla2_Den")),
    # TODO: After completion, make grownup Dukino spawn outside doghouse + interactible + visible
        # On repeat, Dukino sotflocks already in shelter until savequit
    Mission("Hell Hath No Fury", MissionDefinition("GD_Z2_HellHathNo.M_FloodingHyperionCity")),
        # On repeat, foreman doesnt respawn
    Enemy("Foreman Jasper/Rusty", Pawn("PawnBalance_Foreman")),
    Mission("Statuesque", MissionDefinition("GD_Z2_HyperionStatue.M_MonumentsVandalism"), tags=Tag.LongMission),
        # On repeat, third statue softlocks, not progressing to "here's your prize" enemy wave
    Enemy("Hacked Overseer", Pawn("PawnBalance_ConstructorLaserStatue"), mission="Statuesque"),
    Mission("Home Movies", MissionDefinition("GD_Z2_HomeMovies.M_HomeMovies")),
    Mission("Written by the Victor",
        MissionDefinition("GD_Z2_WrittenByVictor.M_WrittenByVictor"),
        WrittenByTheVictor()
    ),
        # On repeat, history buttons are disabled
        # After all dialog plays after first turn-in, button becomes disabled
    Enemy("BNK-3R",
        Behavior("GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_4"),
        Behavior(
            "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_0",
            "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_1",
            "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_2",
            "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_3",
            "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_5",
            "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_6",
            "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_7",
            "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_8",
            "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_9",
            "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_10",
            "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_11",
            "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_12",
            "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_13",
            "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_14",
            "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_15",
            "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_16",
            "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_17",
        inject=False),
    tags=Tag.SlowEnemy),
    Mission("Bearer of Bad News", MissionDefinition("GD_Z1_BearerBadNews.M_BearerBadNews"), tags=Tag.Freebie),
    Mission("BFFs", MissionDefinition("GD_Z1_BFFs.M_BFFs"), BFFs(), tags=Tag.Freebie), 
        # After completion, cannot interact with Sam to reaccpet mission
        # After save quit, Sam not spawned to give mission
    Enemy("Jim Kepler", Pawn("BD_BFF_Jim"), mission="BFFs"),
    Mission("Demon Hunter", MissionDefinition("GD_Z2_DemonHunter.M_DemonHunter")),
        # On repeat, mom no spawn without savequit
    Enemy("Dukino's Mom", Pawn("PawnBalance_Skagzilla"), tags=Tag.SlowEnemy),
    Mission("Monster Mash (Part 1)", MissionDefinition("GD_Z3_MonsterMash1.M_MonsterMash1")),
    Mission("Monster Mash (Part 2)", MissionDefinition("GD_Z3_MonsterMash2.M_MonsterMash2")),

    Other("Geary's Unbreakable Gear",
        Attachment("ObjectGrade_Eagle", 0, 1, 2, 3, configuration=1),
    tags=Tag.VeryLongMission),
    Enemy("Geary", Pawn("PawnBalance_Smagal"), tags=Tag.SlowEnemy),
    Enemy("Donkey Mong", Pawn("PawnBalance_PrimalBeast_DonkeyMong"), tags=Tag.RareEnemy),
    Enemy("King Mong", Pawn("PawnBalance_PrimalBeast_KingMong"), tags=Tag.RareEnemy),
    Mission("Kill Yourself (Do it)", MissionDefinition("GD_Z3_KillYourself.M_KillYourself"), tags=Tag.Freebie),
        # Killing self doesnt trigger on repeat
    Mission("Kill Yourself (Don't do it)", MissionTurnInAlt("GD_Z3_KillYourself.M_KillYourself"), tags=Tag.Freebie),
    Mission("Customer Service", MissionDefinition("GD_Z3_CustomerService.M_CustomerService"), tags=Tag.VehicleMission),
        # Mailboxes unopenable on repeat
    Mission("To Grandmother's House We Go", MissionDefinition("GD_Z3_GrandmotherHouse.M_GrandmotherHouse")),
    Mission("A Real Boy: Clothes Make the Man", MissionDefinition("GD_Z2_ARealBoy.M_ARealBoy_Clothes")),
        # On repeat, Mal unable to accept so many clothes
    Mission("A Real Boy: Face Time", MissionDefinition("GD_Z2_ARealBoy.M_ARealBoy_ArmLeg")),
        # On repeat, topmost two limbs (legs) do not respawn
    Mission("A Real Boy: Human",
        MissionDefinition("GD_Z2_ARealBoy.M_ARealBoy_Human"),
        ARealBoy()
    ),
        # On repeat, mal unprepared for combat
    Mission("Hyperion Slaughter: Round 1", MissionDefinition("GD_Z3_RobotSlaughter.M_RobotSlaughter_1"), tags=Tag.Slaughter),
    Mission("Hyperion Slaughter: Round 2", MissionDefinition("GD_Z3_RobotSlaughter.M_RobotSlaughter_2"), tags=Tag.Slaughter),
    Mission("Hyperion Slaughter: Round 3", MissionDefinition("GD_Z3_RobotSlaughter.M_RobotSlaughter_3"), tags=Tag.Slaughter|Tag.LongMission),
    Mission("Hyperion Slaughter: Round 4", MissionDefinition("GD_Z3_RobotSlaughter.M_RobotSlaughter_4"), tags=Tag.Slaughter|Tag.LongMission),
    Mission("Hyperion Slaughter: Round 5", MissionDefinition("GD_Z3_RobotSlaughter.M_RobotSlaughter_5"), tags=Tag.Slaughter|Tag.VeryLongMission),
    Mission("The Lost Treasure", MissionDefinition("GD_Z3_LostTreasure.M_LostTreasure"),
        MissionObject("CraterLake_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_38", "CraterLake_P"),
    tags=Tag.VeryLongMission), 
    Mission("The Great Escape",
        MissionDefinition("GD_Z3_GreatEscape.M_GreatEscape"),
        GreatEscape()
    ),
        # Beacon doesnt spawn on repeat
        # Ulysses stays dead after save quit
    Mission("The Chosen One", MissionDefinition("GD_Z3_ChosenOne.M_ChosenOne")),
    Mission("Capture the Flags", MissionDefinition("GD_Z3_CaptureTheFlags.M_CaptureTheFlags"), tags=Tag.VeryLongMission),
    Enemy("Mortar", Pawn("PawnBalance_Mortar")),
    Mission("Monster Mash (Part 3)", MissionDefinition("GD_Z3_MonsterMash3.M_MonsterMash3"), tags=Tag.LongMission),
        # Only 29 skrakk and 1 spycho total spawn
    Enemy("Spycho", Pawn("PawnBalance_MonsterMash1"), tags=Tag.SlowEnemy),
    Mission("This Just In", MissionDefinition("GD_Z3_ThisJustIn.M_ThisJustIn")),
    Enemy("Hunter Hellquist", Pawn("PawnBalance_DJHyperion")),
    Mission("Uncle Teddy (Turn in Una)", MissionDefinition("GD_Z3_UncleTeddy.M_UncleTeddy")),
    Mission("Uncle Teddy (Turn in Hyperion)", MissionTurnInAlt("GD_Z3_UncleTeddy.M_UncleTeddy")),
        # ECHO boxes dont reclose on repeat
    Mission("Get to Know Jack", MissionDefinition("GD_Z3_YouDontKnowJack.M_YouDontKnowJack")),
        # ECHO rakk doesnt respawn on repeat
    Mission("Hungry Like the Skag", MissionDefinition("GD_Z3_HungryLikeSkag.M_HungryLikeSkag")), 
    Enemy("Bone Head 2.0", Pawn("PawnBalance_BoneHead2")),
    Enemy("Saturn", Pawn("PawnBalance_LoaderGiant"), tags=Tag.SlowEnemy),
    Enemy("The Warrior",
        Behavior(
            "Boss_Volcano_Combat_Monster.TheWorld:PersistentLevel.Main_Sequence.SeqAct_ApplyBehavior_16.Behavior_SpawnItems_6",
            "Boss_Volcano_Combat_Monster.TheWorld:PersistentLevel.Main_Sequence.SeqAct_ApplyBehavior_31.Behavior_SpawnItems_6",
            "Boss_Volcano_Combat_Monster.TheWorld:PersistentLevel.Main_Sequence.SeqAct_ApplyBehavior_59.Behavior_SpawnItems_6"
        ),
        Behavior(
            "Boss_Volcano_Combat_Monster.TheWorld:PersistentLevel.Main_Sequence.SeqAct_ApplyBehavior_12.Behavior_SpawnItems_6",
            "Boss_Volcano_Combat_Monster.TheWorld:PersistentLevel.Main_Sequence.SeqAct_ApplyBehavior_14.Behavior_SpawnItems_6",
            "Boss_Volcano_Combat_Monster.TheWorld:PersistentLevel.Main_Sequence.SeqAct_ApplyBehavior_15.Behavior_SpawnItems_6",
            "Boss_Volcano_Combat_Monster.TheWorld:PersistentLevel.Main_Sequence.SeqAct_ApplyBehavior_56.Behavior_SpawnItems_6",
            "Boss_Volcano_Combat_Monster.TheWorld:PersistentLevel.Main_Sequence.SeqAct_ApplyBehavior_57.Behavior_SpawnItems_6",
            "Boss_Volcano_Combat_Monster.TheWorld:PersistentLevel.Main_Sequence.SeqAct_ApplyBehavior_58.Behavior_SpawnItems_6",
            "GD_FinalBoss.Character.AIDef_FinalBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_12",
            "GD_FinalBoss.Character.AIDef_FinalBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_13",
            "GD_FinalBoss.Character.AIDef_FinalBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_14",
            "GD_FinalBoss.Character.AIDef_FinalBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_15",
            "GD_FinalBoss.Character.AIDef_FinalBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_16",
            "GD_FinalBoss.Character.AIDef_FinalBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_17",
        inject=False),
    tags=Tag.SlowEnemy),
    Mission("You. Will. Die. (Seriously.)", MissionDefinition("GD_Z2_ThresherRaid.M_ThresherRaid"), tags=Tag.Raid),
        # Terra no respawn after first completion
    Enemy("Terramorphous the Invincible",
        Pawn("PawnBalance_ThresherRaid"),
        Behavior(
            "GD_ThresherShared.Anims.Anim_Raid_Death1:BehaviorProviderDefinition_29.Behavior_SpawnItems_46",
            "GD_ThresherShared.Anims.Anim_Raid_Death1:BehaviorProviderDefinition_29.Behavior_SpawnItems_47",
        inject=False),
    tags=Tag.Raid),


    Enemy("No-Beard", Pawn("PawnBalance_Orchid_NoBeard"), tags=Tag.PiratesBooty|Tag.Excluded),
    Other("Oasis Seraph Vendor",
        VendingMachine("GD_Orchid_SeraphCrystalVendor.Balance.Balance_SeraphCrystalVendor", "GD_Orchid_SeraphCrystalVendor.VendingMachine.VendingMachine_SeraphCrystal:BehaviorProviderDefinition_0.Behavior_Conditional_1.AttributeExpressionEvaluator_20"),
    tags=Tag.PiratesBooty|Tag.Vendor),
    Mission("Message in a Bottle (Oasis)",
        MissionDefinition("GD_Orchid_SM_Message.M_Orchid_MessageInABottle1"),
        MessageInABottle(None, "Orchid_OasisTown_P"),
    tags=Tag.PiratesBooty|Tag.Freebie), 
        # On repeat, bottle uninteractable without savequit
    Mission("Man's Best Friend", MissionDefinition("GD_Orchid_SM_MansBestFriend.M_Orchid_MansBestFriend"), tags=Tag.PiratesBooty),
    Enemy("Tinkles", Pawn("PawnBalance_Orchid_StalkerPet"), tags=Tag.PiratesBooty),
    Mission("Burying the Past", MissionDefinition("GD_Orchid_SM_BuryPast.M_Orchid_BuryingThePast"), tags=Tag.PiratesBooty),
    Mission("Fire Water", MissionDefinition("GD_Orchid_SM_FireWater.M_Orchid_FireWater"), tags=Tag.PiratesBooty),
    Mission("Giving Jocko A Leg Up", MissionDefinition("GD_Orchid_SM_JockoLegUp.M_Orchid_JockoLegUp"), tags=Tag.PiratesBooty),
    Mission("Wingman", MissionDefinition("GD_Orchid_SM_Wingman.M_Orchid_Wingman"), tags=Tag.PiratesBooty),
    Mission("Smells Like Victory", MissionDefinition("GD_Orchid_SM_Smells.M_Orchid_SmellsLikeVictory"), tags=Tag.PiratesBooty),
        # Shiv-spike doesnt respawn without savequit
    Mission("Declaration Against Independents", MissionDefinition("GD_Orchid_SM_Declaration.M_Orchid_DeclarationAgainstIndependents"), tags=Tag.PiratesBooty|Tag.VehicleMission),
        # Not enough union vehicles spawn unless savequit
    Mission("Ye Scurvy Dogs", MissionDefinition("GD_Orchid_SM_Scurvy.M_Orchid_ScurvyDogs"), tags=Tag.PiratesBooty),
        # Fruits unshootable unless savequit
    Mission("Message in a Bottle (Wurmwater)",
        MissionDefinition("GD_Orchid_SM_Message.M_Orchid_MessageInABottle2"),
        MessageInABottle("GD_Orchid_SM_Message_Data.MO_Orchid_XMarksTheSpot:BehaviorProviderDefinition_2.BehaviorSequenceEnableByMission_13", "Orchid_SaltFlats_P"),
    tags=Tag.PiratesBooty), 
    Mission("Grendel", MissionDefinition("GD_Orchid_SM_Grendel.M_Orchid_Grendel"), tags=Tag.PiratesBooty),
        # Grendel doesnt respawn without savequit
    Enemy("Grendel", Pawn("PawnBalance_Orchid_Grendel"), tags=Tag.PiratesBooty),
    Mission("Message in a Bottle (Hayter's Folly)",
        MissionDefinition("GD_Orchid_SM_Message.M_Orchid_MessageInABottle3"),
        MessageInABottle("GD_Orchid_SM_Message_Data.MO_Orchid_XMarksTheSpot:BehaviorProviderDefinition_2.BehaviorSequenceEnableByMission_23", "Orchid_Caves_P"),
    tags=Tag.PiratesBooty), 
    Enemy("The Big Sleep", Pawn("PawnBalance_Orchid_BigSleep"), tags=Tag.PiratesBooty|Tag.SlowEnemy),
    Enemy("Sandman", Pawn("PawnBalance_Orchid_Sandman_Solo"), tags=Tag.PiratesBooty|Tag.SlowEnemy),
    Mission("Just Desserts for Desert Deserters", MissionDefinition("GD_Orchid_SM_Deserters.M_Orchid_Deserters"), tags=Tag.PiratesBooty|Tag.LongMission),
        # Deserters dont respawn without savequit
    Enemy("Benny the Booster", Pawn("PawnBalance_Orchid_Deserter1"), tags=Tag.PiratesBooty),
    Enemy("Deckhand", Pawn("PawnBalance_Orchid_Deserter2"), tags=Tag.PiratesBooty|Tag.SlowEnemy),
    Enemy("Toothless Terry", Pawn("PawnBalance_Orchid_Deserter3"), mission="Just Desserts for Desert Deserters"),
    Mission("Message in a Bottle (The Rustyards)",
        MissionDefinition("GD_Orchid_SM_Message.M_Orchid_MessageInABottle4"),
        MessageInABottle("GD_Orchid_SM_Message_Data.MO_Orchid_XMarksTheSpot:BehaviorProviderDefinition_2.BehaviorSequenceEnableByMission_16", "Orchid_ShipGraveyard_P"),
    tags=Tag.PiratesBooty), 
    Mission("I Know It When I See It", MissionDefinition("GD_Orchid_SM_KnowIt.M_Orchid_KnowItWhenSeeIt"), tags=Tag.PiratesBooty),
    Enemy("P3RV-E", Pawn("PawnBalance_Orchid_Pervbot"), tags=Tag.PiratesBooty|Tag.SlowEnemy),
    Mission("Don't Copy That Floppy", MissionDefinition("GD_Orchid_SM_FloppyCopy.M_Orchid_DontCopyThatFloppy"), tags=Tag.PiratesBooty),
    Enemy("H3RL-E", Pawn("PawnBalance_Orchid_LoaderBoss"), tags=Tag.PiratesBooty|Tag.SlowEnemy),
    Mission("Whoops", MissionTurnIn("GD_Orchid_Plot_Mission07.M_Orchid_PlotMission07"), tags=Tag.PiratesBooty|Tag.Excluded),
        # Not enough floppy pirates spawn without savequit
    Mission("Faster Than the Speed of Love", MissionDefinition("GD_Orchid_SM_Race.M_Orchid_Race"), tags=Tag.PiratesBooty|Tag.VehicleMission|Tag.Freebie),
    Mission("Catch-A-Ride, and Also Tetanus", MissionDefinition("GD_Orchid_SM_Tetanus.M_Orchid_CatchRideTetanus"), tags=Tag.PiratesBooty),
    Mission("Freedom of Speech", MissionDefinition("GD_Orchid_SM_Freedom.M_Orchid_FreedomOfSpeech"), tags=Tag.PiratesBooty),
        # DJ Tanner doesnt respawn until savequit
    Enemy("DJ Tanner", Pawn("PawnBalance_Orchid_PirateRadioGuy"), tags=Tag.PiratesBooty|Tag.SlowEnemy),
    Enemy("Mr. Bubbles", Pawn("PawnBalance_Orchid_Bubbles"), tags=Tag.PiratesBooty|Tag.VeryRareEnemy),
    Enemy("Lil' Sis", Behavior("GD_Orchid_LittleSis.Character.AIDef_Orchid_LittleSis:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_85"), tags=Tag.PiratesBooty|Tag.VeryRareEnemy),
    Mission("Message In A Bottle (Magnys Lighthouse)",
        MissionDefinition("GD_Orchid_SM_Message.M_Orchid_MessageInABottle6"),
        MessageInABottle("GD_Orchid_SM_Message_Data.MO_Orchid_XMarksTheSpot:BehaviorProviderDefinition_2.BehaviorSequenceEnableByMission_7", "Orchid_Spire_P"),
    tags=Tag.PiratesBooty),
    Mission("Treasure of the Sands",
        MissionDefinition("GD_Orchid_SM_EndGameClone.M_Orchid_EndGame"),
        MissionDefinition("GD_Orchid_Plot_Mission09.M_Orchid_PlotMission09"),
    tags=Tag.PiratesBooty|Tag.VeryLongMission),
        # Roscoe/Scarlett dont respawn until savequit
    Enemy("Lieutenant White", Pawn("PawnBalance_Orchid_PirateHenchman"), mission="Treasure of the Sands"),
    Enemy("Lieutenant Hoffman", Pawn("PawnBalance_Orchid_PirateHenchman2"), mission="Treasure of the Sands"),
    Enemy("Captain Scarlett", Behavior("GD_Orchid_PirateQueen_Combat.Animation.Anim_Farewell:BehaviorProviderDefinition_0.Behavior_SpawnItems_10"), mission="Treasure of the Sands"),
    Enemy("Leviathan",
        Leviathan(),
    mission="Treasure of the Sands"),
    Mission("Hyperius the Invincible", MissionDefinition("GD_Orchid_Raid.M_Orchid_Raid1"), tags=Tag.PiratesBooty|Tag.Raid),
    Enemy("Hyperius the Invincible",
        Pawn("PawnBalance_Orchid_RaidEngineer"),
        Behavior(
            "GD_Orchid_RaidEngineer.Death.BodyDeath_Orchid_RaidEngineer:BehaviorProviderDefinition_6.Behavior_SpawnItems_203",
            "GD_Orchid_RaidEngineer.Death.BodyDeath_Orchid_RaidEngineer:BehaviorProviderDefinition_6.Behavior_SpawnItems_204",
        inject=False),
    tags=Tag.PiratesBooty|Tag.Raid),
    Mission("Master Gee the Invincible", MissionDefinition("GD_Orchid_Raid.M_Orchid_Raid3"), tags=Tag.PiratesBooty|Tag.Raid),
    Enemy("Master Gee the Invincible",
        Pawn("PawnBalance_Orchid_RaidShaman"),
        Behavior(
            "GD_Orchid_RaidShaman.Character.AIDef_Orchid_RaidShaman:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_102",
            "GD_Orchid_RaidShaman.Character.AIDef_Orchid_RaidShaman:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_103",
            "GD_Orchid_RaidShaman.Character.AIDef_Orchid_RaidShaman:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_257",
            "Transient.Behavior_SpawnItems_Orchid_MasterGeeDeath",
        inject=False),
    tags=Tag.PiratesBooty|Tag.Raid),



    Other("Badass Crater Seraph Vendor",
        VendingMachine("GD_Iris_SeraphCrystalVendor.Balance.Balance_SeraphCrystalVendor", "GD_Iris_SeraphCrystalVendor.VendingMachine.VendingMachine_SeraphCrystal:BehaviorProviderDefinition_0.Behavior_Conditional_3.AttributeExpressionEvaluator_20"),
    tags=Tag.CampaignOfCarnage|Tag.Vendor),
    Other("Torgue Vendor",
        VendingMachine("GD_Iris_TorgueTokenVendor.Balance.Balance_TorgueTokenVendor"),
    tags=Tag.CampaignOfCarnage|Tag.Vendor),
    Other("Torgue Arena Provided Loot",
        Attachment("ObjectGrade_Iris_HyperionChest", 0),
    tags=Tag.CampaignOfCarnage|Tag.Freebie),
    Enemy("Gladiator Goliath", Pawn("Iris_PawnBalance_ArenaGoliath", evolved=5), mission="Tier 2 Battle: Appetite for Destruction"),
    Mission("Tier 2 Battle: Appetite for Destruction", MissionDefinition("GD_IrisEpisode02_Battle.M_IrisEp2Battle_CoP2"), tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Tier 3 Battle: Appetite for Destruction",
        MissionDefinition("GD_IrisEpisode02_Battle.M_IrisEp2Battle_CoPR3"),
        MissionDefinition("GD_IrisEpisode02_Battle.M_IrisEp2Battle_CoP3"),
    tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Tier 3 Rematch: Appetite for Destruction",
        MissionDefinition("GD_IrisEpisode02_Battle.M_IrisEp2Battle_CoPR3"),
    tags=Tag.CampaignOfCarnage|Tag.Slaughter|Tag.Excluded),
        # When tiers repeated concurrently, killing all enemies doesnt complete wave 4
    Enemy("Pete's Burner",
        PetesBurner(
            "Iris_PawnBalance_BikerMidget",
            "Iris_PawnBalance_BikerBruiser",
            "Iris_PawnBalance_Biker",
            "Iris_PawnBalance_BikerBadass",
            "Iris_PawnBalance_BigBiker",
            "Iris_PawnBalance_BigBikerBadass"
        ),
    tags=Tag.CampaignOfCarnage|Tag.MobFarm),
    Mission("Tier 2 Battle: Bar Room Blitz", MissionDefinition("GD_IrisEpisode03_Battle.M_IrisEp3Battle_BarFight2"), tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Tier 3 Battle: Bar Room Blitz",
        MissionDefinition("GD_IrisEpisode03_Battle.M_IrisEp3Battle_BarFightR3"),
        MissionDefinition("GD_IrisEpisode03_Battle.M_IrisEp3Battle_BarFight3"),
    tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Tier 3 Rematch: Bar Room Blitz",
        MissionDefinition("GD_IrisEpisode03_Battle.M_IrisEp3Battle_BarFightR3"),
    tags=Tag.CampaignOfCarnage|Tag.Slaughter|Tag.Excluded),
    Mission("Totally Recall", MissionDefinition("GD_IrisDL2_ProductRecall.M_IrisDL2_ProductRecall"), tags=Tag.CampaignOfCarnage),
    Mission("Mother-Lover (Turn in Scooter)", MissionDefinition("GD_IrisDL2_DontTalkAbtMama.M_IrisDL2_DontTalkAbtMama"), tags=Tag.CampaignOfCarnage),
    Mission("Mother-Lover (Turn in Moxxi)", MissionTurnInAlt("GD_IrisDL2_DontTalkAbtMama.M_IrisDL2_DontTalkAbtMama"), tags=Tag.CampaignOfCarnage),
    Enemy("Hamhock the Ham", Pawn("Iris_PawnBalance_BB_Hamlock"), mission="Mother-Lover (Turn in Scooter)"),
    Mission("Tier 2 Battle: The Death Race", MissionDefinition("GD_IrisEpisode04_Battle.M_IrisEp4Battle_Race2"), tags=Tag.CampaignOfCarnage|Tag.VehicleMission|Tag.Freebie),
    Mission("Tier 3 Battle: The Death Race",
        MissionDefinition("GD_IrisEpisode04_Battle.M_IrisEp4Battle_RaceR4"),
        MissionDefinition("GD_IrisEpisode04_Battle.M_IrisEp4Battle_Race4"),
    tags=Tag.CampaignOfCarnage|Tag.VehicleMission|Tag.Freebie),
    Mission("Tier 3 Rematch: The Death Race",
        MissionDefinition("GD_IrisEpisode04_Battle.M_IrisEp4Battle_RaceR4"),
    tags=Tag.CampaignOfCarnage|Tag.VehicleMission|Tag.Excluded),
    Mission("Number One Fan", MissionDefinition("GD_IrisDL2_PumpkinHead.M_IrisDL2_PumpkinHead"), tags=Tag.CampaignOfCarnage),
        # Sully doesnt respawn without savequit
    Enemy("Sully the Stabber", Pawn("Iris_PawnBalance_SullyTheStabber"), mission="Number One Fan"),
    Mission("Walking the Dog", MissionDefinition("GD_IrisHUB_WalkTheDog.M_IrisHUB_WalkTheDog"), tags=Tag.CampaignOfCarnage|Tag.LongMission),
    Enemy("Enrique", Pawn("Iris_PawnBalance_TinasSkag"), mission="Walking the Dog"),
    Mission("Monster Hunter", MissionDefinition("GD_IrisHUB_MonsterHunter.M_IrisHUB_MonsterHunter"), tags=Tag.CampaignOfCarnage),
    Enemy("The Monster Truck", MonsterTruckDriver("PawnBalance_MarauderGrunt"), mission="Monster Hunter"),
    Mission("Gas Guzzlers (Turn in Hammerlock)", MissionDefinition("GD_IrisHUB_GasGuzzlers.M_IrisHUB_GasGuzzlers"), tags=Tag.CampaignOfCarnage|Tag.LongMission),
    Mission("Gas Guzzlers (Turn in Scooter)", MissionTurnInAlt("GD_IrisHUB_GasGuzzlers.M_IrisHUB_GasGuzzlers"), tags=Tag.CampaignOfCarnage|Tag.LongMission),
    Enemy("Chubby Rakk (Gas Guzzlers)", Pawn("Iris_PawnBalance_RakkChubby"), mission="Gas Guzzlers (Turn in Hammerlock)"),
    Mission("Matter Of Taste", MissionDefinition("GD_IrisHUB_MatterOfTaste.M_IrisHUB_MatterOfTaste"), tags=Tag.CampaignOfCarnage|Tag.LongMission),
        # Staff enemies do not respawn without savequit
    Enemy("BuffGamer G", Pawn("Iris_PawnBalance_BB_JohnnyAbs"), mission="Matter Of Taste"),
    Enemy("Game Critic Extraordinaire", Pawn("Iris_PawnBalance_BB_TonyGlutes"), mission="Matter Of Taste"),
    Mission("Everybody Wants to be Wanted", MissionDefinition("GD_IrisHUB_Wanted.M_IrisHUB_Wanted"), tags=Tag.CampaignOfCarnage),
    Mission("Interview with a Vault Hunter", MissionDefinition("GD_IrisHUB_SmackTalk.M_IrisHUB_SmackTalk"), tags=Tag.CampaignOfCarnage),
    Enemy("Motor Momma", Pawn("Iris_PawnBalance_MotorMama"), tags=Tag.CampaignOfCarnage|Tag.SlowEnemy),
    Mission("Tier 2 Battle: Twelve O' Clock High", MissionDefinition("GD_IrisEpisode05_Battle.M_IrisEp5Battle_FlyboyGyro2"), tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Tier 3 Battle: Twelve O' Clock High",
        MissionDefinition("GD_IrisEpisode05_Battle.M_IrisEp5Battle_FlyboyGyroR3"),
        MissionDefinition("GD_IrisEpisode05_Battle.M_IrisEp5Battle_FlyboyGyro3"),
    tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Tier 3 Rematch: Twelve O' Clock High",
        MissionDefinition("GD_IrisEpisode05_Battle.M_IrisEp5Battle_FlyboyGyroR3"),
    tags=Tag.CampaignOfCarnage|Tag.Slaughter|Tag.Excluded),
        # Timer doesnt trigger for all tiers when repeated concurrently
        # Not enough buzzards spawn when repeated concurrently
    Mission("My Husband the Skag (Kill Uriah)", MissionDefinition("GD_IrisDL3_MySkag.M_IrisDL3_MySkag"), tags=Tag.CampaignOfCarnage),
    Mission("My Husband the Skag (Spare Uriah)", MissionTurnInAlt("GD_IrisDL3_MySkag.M_IrisDL3_MySkag"), tags=Tag.CampaignOfCarnage),
        # Skags dont respawn without savequit
    Mission("Say That To My Face", MissionDefinition("GD_IrisDL3_PSYouSuck.M_IrisDL3_PSYouSuck"), tags=Tag.CampaignOfCarnage),
    Enemy("Anonymous Troll Face", Pawn("Iris_PawnBalance_SayFaceTroll"), mission="Say That To My Face"),
    Mission("Commercial Appeal",
        MissionDefinition("GD_IrisDL3_CommAppeal.M_IrisDL3_CommAppeal"),
        CommercialAppeal(),
    tags=Tag.CampaignOfCarnage|Tag.LongMission),        
    Enemy("Piston/Badassasarus Rex",
        Pawn(
            "Iris_PawnBalance_Truckasaurus",
            "Iris_PawnBalance_PistonBoss",
            "Iris_PawnBalance_Truckasaurus_Runable"
        ),
    tags=Tag.CampaignOfCarnage|Tag.SlowEnemy),
    Mission("Pete the Invincible", MissionDefinition("GD_IrisRaidBoss.M_Iris_RaidPete"), tags=Tag.CampaignOfCarnage|Tag.Raid),
        # Pete doesnt respawn without savequit
    Enemy("Pyro Pete the Invincible",
        Pawn("Iris_PawnBalance_RaidPete"),
        Behavior(
            "GD_Iris_Raid_PyroPete.Death.BodyDeath_Iris_Raid_PyroPete:BehaviorProviderDefinition_6.Behavior_SpawnItems_5",
            "GD_Iris_Raid_PyroPete.Death.BodyDeath_Iris_Raid_PyroPete:BehaviorProviderDefinition_6.Behavior_SpawnItems_6",
            "GD_Iris_Raid_PyroPete.Death.BodyDeath_Iris_Raid_PyroPete:BehaviorProviderDefinition_6.Behavior_SpawnItems_7",
            "GD_Iris_Raid_PyroPete.Death.BodyDeath_Iris_Raid_PyroPete:BehaviorProviderDefinition_6.Behavior_SpawnItems_8",
            "GD_Iris_Raid_PyroPete.Death.BodyDeath_Iris_Raid_PyroPete:BehaviorProviderDefinition_6.Behavior_SpawnItems_9",
        inject=False),
    tags=Tag.CampaignOfCarnage|Tag.Raid),



    Other("Hunter's Grotto Seraph Vendor",
        VendingMachine("GD_Sage_SeraphCrystalVendor.Balance.Balance_SeraphCrystalVendor", "GD_Sage_SeraphCrystalVendor.VendingMachine.VendingMachine_SeraphCrystal:BehaviorProviderDefinition_0.Behavior_Conditional_0.AttributeExpressionEvaluator_20"),
    tags=Tag.HammerlocksHunt|Tag.Vendor),
    Enemy("Omnd-Omnd-Ohk",
        Pawn("PawnBalance_Native_Badass", "PawnBalance_Nast_Native_Badass", transform=3),
    tags=Tag.HammerlocksHunt|Tag.EvolvedEnemy|Tag.VeryRareEnemy),
    Enemy("Dexiduous the Invincible",
        Pawn("PawnBalance_DrifterRaid"),
        Behavior("GD_DrifterRaid.Anims.Anim_Raid_Death:BehaviorProviderDefinition_29.Behavior_SpawnItems_38", inject=False),
    tags=Tag.HammerlocksHunt|Tag.Raid),
    Mission("I Like My Monsters Rare", MissionDefinition("GD_Sage_SM_RareSpawns.M_Sage_RareSpawns"), tags=Tag.HammerlocksHunt|Tag.VeryLongMission, rarities=(100, 100, 100, 100, 100, 100)),
    Mission("Still Just a Borok in a Cage", MissionDefinition("GD_Sage_SM_BorokCage.M_Sage_BorokCage"), tags=Tag.HammerlocksHunt),
    Enemy("Der Monstrositat", Pawn("PawnBalance_Sage_BorokCage_Creature"), mission="Still Just a Borok in a Cage"),
    Mission("Egg on Your Face", MissionDefinition("GD_Sage_SM_EggOnFace.M_Sage_EggOnFace"), tags=Tag.HammerlocksHunt|Tag.LongMission|Tag.VehicleMission),
        # Cage still closed without savequit
    Mission("An Acquired Taste", MissionDefinition("GD_Sage_SM_AcquiredTaste.M_Sage_AcquiredTaste"), tags=Tag.HammerlocksHunt),
    Enemy("Bulstoss", Pawn("PawnBalance_Sage_AcquiredTaste_Creature"), tags=Tag.HammerlocksHunt|Tag.SlowEnemy),
    Enemy("Arizona", Pawn("PawnBalance_DrifterNamed"), tags=Tag.HammerlocksHunt|Tag.SlowEnemy, rarities=(50, 50)),
    Mission("Palling Around", MissionDefinition("GD_Sage_SM_PallingAround.M_Sage_PallingAround"), tags=Tag.HammerlocksHunt),
        # Bulwark doesnt respawn without savequit
    Enemy("The Bulwark", Pawn("Balance_Sage_SM_PallingAround_Creature"), tags=Tag.HammerlocksHunt|Tag.SlowEnemy),
    Mission("Ol' Pukey", MissionDefinition("GD_Sage_SM_OldPukey.M_Sage_OldPukey"), tags=Tag.HammerlocksHunt|Tag.LongMission),
        # Pukey no AI without savequit
    Mission("Nakayama-rama", MissionDefinition("GD_Sage_SM_Nakarama.M_Sage_Nakayamarama"), tags=Tag.HammerlocksHunt|Tag.LongMission),
        # Only 2 echos respawn without savequit
    Mission("The Rakk Dahlia Murder", MissionDefinition("GD_Sage_SM_DahliaMurder.M_Sage_DahliaMurder"), tags=Tag.HammerlocksHunt),
        # Rakkanoth doesnt respawn without savequit
    Enemy("Rakkanoth", Pawn("PawnBalance_Sage_DahliaMurder_Creature"), mission="The Rakk Dahlia Murder", rarities=(100,)),
    Mission("Urine, You're Out", MissionDefinition("GD_Sage_SM_Urine.M_Sage_Urine"), tags=Tag.HammerlocksHunt|Tag.VeryLongMission, rarities=(100, 100, 100, 100, 100)),
        # Urine not reinteractable without savequit
    Mission("Follow The Glow", MissionDefinition("GD_Sage_SM_FollowGlow.M_Sage_FollowGlow"), tags=Tag.HammerlocksHunt),
        # Dribbles wave fight doesnt reset without savequit
    Enemy("Dribbles", Pawn("PawnBalance_Sage_FollowGlow_Creature"), tags=Tag.HammerlocksHunt),
    Enemy("Woundspike", Pawn("PawnBalance_Sage_Ep4_Creature"), tags=Tag.HammerlocksHunt|Tag.SlowEnemy),
    Mission("Big Feet", MissionDefinition("GD_Sage_SM_BigFeet.M_Sage_BigFeet"), tags=Tag.HammerlocksHunt),
    Enemy("Rouge",
        Pawn("PawnBalance_Sage_BigFeet_Creature"),
        Behavior(
            "GD_Sage_SM_BigFeetData.Creature.Character.BodyDeath_BigFeetCrystalisk:BehaviorProviderDefinition_6.Behavior_SpawnItems_115",
            "GD_Sage_SM_BigFeetData.Creature.Character.BodyDeath_BigFeetCrystalisk:BehaviorProviderDefinition_6.Behavior_SpawnItems_114",
            "GD_Sage_SM_BigFeetData.Creature.Character.BodyDeath_BigFeetCrystalisk:BehaviorProviderDefinition_6.Behavior_SpawnItems_116",
            "GD_Sage_SM_BigFeetData.Creature.Character.BodyDeath_BigFeetCrystalisk:BehaviorProviderDefinition_6.Behavior_SpawnItems_117",
            "GD_Sage_SM_BigFeetData.Creature.Character.BodyDeath_BigFeetCrystalisk:BehaviorProviderDefinition_6.Behavior_SpawnItems_118",
            "GD_Sage_SM_BigFeetData.Creature.Character.BodyDeath_BigFeetCrystalisk:BehaviorProviderDefinition_6.Behavior_SpawnItems_119",
        inject=False),
    tags=Tag.HammerlocksHunt|Tag.SlowEnemy),
    Mission("Now You See It", MissionDefinition("GD_Sage_SM_NowYouSeeIt.M_Sage_NowYouSeeIt"), tags=Tag.HammerlocksHunt|Tag.LongMission),
    Enemy("Bloodtail", Pawn("PawnBalance_Sage_NowYouSeeIt_Creature"), tags=Tag.HammerlocksHunt|Tag.SlowEnemy),
    Enemy("Jackenstein", Pawn("PawnBalance_Sage_FinalBoss"), tags=Tag.HammerlocksHunt|Tag.SlowEnemy),
    Mission("Voracidous the Invincible", MissionDefinition("GD_Sage_Raid.M_Sage_Raid"), tags=Tag.HammerlocksHunt|Tag.Raid),
    Enemy("Voracidous the Invincible",
        Pawn("Balance_Sage_Raid_Beast"),
        Behavior(
            "GD_Sage_Raid_Beast.Character.DeathDef_Sage_Raid_Beast:BehaviorProviderDefinition_0.Behavior_SpawnItems_0",
            "GD_Sage_Raid_Beast.Character.DeathDef_Sage_Raid_Beast:BehaviorProviderDefinition_0.Behavior_SpawnItems_1",
            "GD_Sage_Raid_Beast.Character.DeathDef_Sage_Raid_Beast:BehaviorProviderDefinition_0.Behavior_SpawnItems_2",
        inject=False),
    tags=Tag.HammerlocksHunt|Tag.Raid),



    Enemy("Mister Boney Pants Guy", Pawn("PawnBalance_BoneyPants"), tags=Tag.DragonKeep),
    Other("Mimic Chest",
        Pawn("PawnBalance_Mimic"),
        Attachment("ObjectGrade_MimicChest", 0, 1, 2, 3, configuration=6),
        Attachment("ObjectGrade_MimicChest_NoMimic", 0, 1, 2, 3, configuration=6),
    tags=Tag.DragonKeep|Tag.Freebie, rarities=(33,)),
    Other("Flamerock Refuge Seraph Vendor",
        VendingMachine("GD_Aster_SeraphCrystalVendor.Balance.Balance_SeraphCrystalVendor", "GD_Aster_SeraphCrystalVendor.VendingMachine.VendingMachine_SeraphCrystal:BehaviorProviderDefinition_0.Behavior_Conditional_12.AttributeExpressionEvaluator_20"),
    tags=Tag.DragonKeep|Tag.Vendor),
    Mission("Roll Insight", MissionDefinition("GD_Aster_RollInsight.M_RollInsight"),
        RollInsight("Village_Mission.TheWorld:PersistentLevel.WillowInteractiveObject_297.MissionDirectivesDefinition_1", True, True, "Village_P"),
    tags=Tag.DragonKeep|Tag.Freebie),
    Mission("Fake Geek Guy", MissionDefinition("GD_Aster_FakeGeekGuy.M_FakeGeekGuy"), tags=Tag.DragonKeep),
        # Questions dont respawn until savequit
    Mission("Post-Crumpocalyptic", MissionDefinition("GD_Aster_Post-Crumpocalyptic.M_Post-Crumpocalyptic"), tags=Tag.DragonKeep|Tag.VeryLongMission),
    Enemy("Treant",
        Pawn(
            "PawnBalance_Treant",
            "PawnBalance_Treant_StandStill",
            "PawnBalance_Treant_StandStill_OL",
            "PawnBalance_Treant_Overleveled"
        ),
    tags=Tag.DragonKeep),
    Mission("Ell in Shining Armor (Skimpy Armor)", MissionDefinition("GD_Aster_EllieDress.M_EllieDress"), tags=Tag.DragonKeep),
    Mission("Ell in Shining Armor (Bulky Armor)", MissionTurnInAlt("GD_Aster_EllieDress.M_EllieDress"), tags=Tag.DragonKeep),
    Enemy("Warlord Grug", Pawn("PawnBalance_Orc_WarlordGrug", evolved=4), tags=Tag.DragonKeep),
    Enemy("Duke of Ork",
        Pawn("PawnBalance_Orc_WarlordGrug", "PawnBalance_Orc_WarlordTurge", transform=4),
    tags=Tag.DragonKeep|Tag.EvolvedEnemy),
    Mission("Tree Hugger",
        MissionDefinition("GD_Aster_TreeHugger.M_TreeHugger"),
        TreeHugger(),
    tags=Tag.DragonKeep|Tag.LongMission),
    Mission("Critical Fail", MissionDefinition("GD_Aster_CriticalFail.M_CriticalFail"), tags=Tag.DragonKeep),
        # Huts dont respawn without savequit
    Enemy("Arguk the Butcher", Pawn("PawnBalance_Orc_Butcher"), mission="Critical Fail"),
    Mission("Lost Souls",
        MissionDefinition("GD_Aster_DemonicSouls.M_DemonicSouls"),
        LostSouls("GD_Knight_LostSoulsNPC_Proto2.Character.Pawn_Knight_LostSoulsNPC_Proto2:MissionDirectivesDefinition_1", True, True, "Dead_Forest_P"),
    tags=Tag.DragonKeep), 
        # Dark Souls guy stays revived  after completion, and also until savequit with purge
    Enemy("-=nOObkiLLer=-", Pawn("PawnBalance_Knight_LostSouls_Invader"), mission="Lost Souls"),
    Mission("MMORPGFPS", MissionDefinition("GD_Aster_MMORPGFPS.M_MMORPGFPS"), tags=Tag.DragonKeep|Tag.LongMission),
        # Knights dont respawn unless savequit
    Enemy("xxDatVaultHuntrxx", Pawn("PawnBalance_Knight_MMORPG1"), mission="MMORPGFPS", rarities=(10,)),
    Enemy("420_E-Sports_Masta", Pawn("PawnBalance_Knight_MMORPG2"), mission="MMORPGFPS", rarities=(10,)),
    Enemy("[720NoScope]Headshotz", Pawn("PawnBalance_Knight_MMORPG3"), mission="MMORPGFPS", rarities=(10,)),
    Enemy("King Aliah", Pawn("PawnBalance_SkeletonKing_Aliah"), tags=Tag.DragonKeep|Tag.SlowEnemy),
    Enemy("King Crono", Pawn("PawnBalance_SkeletonKing_Crono"), tags=Tag.DragonKeep|Tag.SlowEnemy),
    Enemy("King Seth", Pawn("PawnBalance_SkeletonKing_Seth"), tags=Tag.DragonKeep|Tag.SlowEnemy),
    Enemy("King Nazar", Pawn("PawnBalance_SkeletonKing_Nazar"), tags=Tag.DragonKeep|Tag.SlowEnemy),
    Mission("The Sword in The Stoner", MissionDefinition("GD_Aster_SwordInStone.M_SwordInStoner"), tags=Tag.DragonKeep|Tag.LongMission),
        # Stoner doesnt respawn without savequit
    Enemy("Unmotivated Golem", Pawn("PawnBalance_Golem_SwordInStone"), mission="The Sword in The Stoner"),
    Enemy("Warlord Turge", Pawn("PawnBalance_Orc_WarlordTurge", evolved=4), tags=Tag.DragonKeep),
    Enemy("Spiderpants", Pawn("PawnBalance_Spiderpants"), tags=Tag.DragonKeep|Tag.VeryRareEnemy|Tag.SlowEnemy, rarities=(100, 100, 50, 50)),
    # TODO: buff spawn rate
    Enemy("Iron GOD", Pawn("PawnBalance_Golem_Badass", transform=5), tags=Tag.DragonKeep|Tag.SlowEnemy|Tag.EvolvedEnemy|Tag.Raid),
    Mission("The Beard Makes The Man", MissionDefinition("GD_Aster_ClapTrapBeard.M_ClapTrapBeard"), tags=Tag.DragonKeep|Tag.LongMission),
        # Forge doesnt reset without savequit
    Mission("My Kingdom for a Wand", MissionDefinition("GD_Aster_ClaptrapWand.M_WandMakesTheMan"), tags=Tag.DragonKeep),
    Enemy("Maxibillion", Pawn("PawnBalance_GolemFlying_Maxibillion"), mission="My Kingdom for a Wand", rarities=(5,)),
    Enemy("Magical Spider", Pawn("PawnBalance_Spider_ClaptrapWand"), mission="My Kingdom for a Wand", rarities=(5,)),
    Enemy("Magical Orc", Pawn("PawnBalance_Orc_ClaptrapWand"), mission="My Kingdom for a Wand", rarities=(5,)),
    Mission("The Claptrap's Apprentice", MissionDefinition("GD_Aster_ClaptrapApprentice.M_ClaptrapApprentice"), tags=Tag.DragonKeep),
        # After turn in, claptrap animates disappearing and then only returns after savequit
    Enemy("Gold Golem", Pawn("PawnBalance_GolemGold"), tags=Tag.DragonKeep|Tag.SlowEnemy, rarities=(33,33,33)),
    Enemy("The Darkness", Pawn("PawnBalance_Darkness"), tags=Tag.DragonKeep),
    Mission("Loot Ninja", MissionDefinition("GD_Aster_LootNinja.M_LootNinja"),
        MissionGiver("GD_Aster_Torgue.Character.Pawn_Torgue:MissionDirectivesDefinition_1", True, True, "Village_P"),
    tags=Tag.DragonKeep), 
        # After turn in, Sir Gallow does not spawn to give mission
    Enemy("Sir Boil", Pawn("PawnBalance_SirBoil"), mission="Loot Ninja"),
    Enemy("Sir Mash", Pawn("PawnBalance_SirMash"), mission="Loot Ninja"),
    Enemy("Sir Stew", Pawn("PawnBalance_SirStew"), mission="Loot Ninja"),
    Enemy("Handsome Dragon",
        Behavior("GD_DragonBridgeBoss.InteractiveObjects.IO_DragonBridgeBoss_LootExplosion:BehaviorProviderDefinition_0.Behavior_SpawnItems_26"),
        Behavior(
            "GD_DragonBridgeBoss.InteractiveObjects.IO_DragonBridgeBoss_LootExplosion:BehaviorProviderDefinition_0.Behavior_SpawnItems_17",
            "GD_DragonBridgeBoss.InteractiveObjects.IO_DragonBridgeBoss_LootExplosion:BehaviorProviderDefinition_0.Behavior_SpawnItems_18",
            "GD_DragonBridgeBoss.InteractiveObjects.IO_DragonBridgeBoss_LootExplosion:BehaviorProviderDefinition_0.Behavior_SpawnItems_19",
            "GD_DragonBridgeBoss.InteractiveObjects.IO_DragonBridgeBoss_LootExplosion:BehaviorProviderDefinition_0.Behavior_SpawnItems_20",
            "GD_DragonBridgeBoss.InteractiveObjects.IO_DragonBridgeBoss_LootExplosion:BehaviorProviderDefinition_0.Behavior_SpawnItems_21",
            "GD_DragonBridgeBoss.InteractiveObjects.IO_DragonBridgeBoss_LootExplosion:BehaviorProviderDefinition_0.Behavior_SpawnItems_27",
            "GD_DragonBridgeBoss.InteractiveObjects.IO_DragonBridgeBoss_LootExplosion:BehaviorProviderDefinition_0.Behavior_SpawnItems_28",
            "GD_DragonBridgeBoss.InteractiveObjects.IO_DragonBridgeBoss_LootExplosion:BehaviorProviderDefinition_0.Behavior_SpawnItems_29",
            "GD_DragonBridgeBoss.InteractiveObjects.IO_DragonBridgeBoss_LootExplosion:BehaviorProviderDefinition_0.Behavior_SpawnItems_31",
        inject=False),
    tags=Tag.DragonKeep, rarities=(33,33,33)),
    Mission("Winter is a Bloody Business", MissionDefinition("GD_Aster_WinterIsComing.M_WinterIsComing"), tags=Tag.DragonKeep|Tag.LongMission),
    Enemy("Canine", Pawn("PawnBalance_Knight_Winter_Canine"), mission="Winter is a Bloody Business"),
    Enemy("Molehill", Pawn("PawnBalance_Knight_Winter_Molehill"), mission="Winter is a Bloody Business"),
    Mission("My Dead Brother (Kill Edgar)",
        MissionDefinition("GD_Aster_DeadBrother.M_MyDeadBrother"),
        MyDeadBrother(),
    tags=Tag.DragonKeep|Tag.LongMission), 
    Enemy("Edgar", Pawn("PawnBalance_Wizard_DeadBrotherEdgar"), mission="My Dead Brother (Kill Edgar)"),
    Mission("My Dead Brother (Kill Simon)", MissionTurnInAlt("GD_Aster_DeadBrother.M_MyDeadBrother"), tags=Tag.DragonKeep|Tag.LongMission), 
    Enemy("Simon", Pawn("PawnBalance_Wizard_DeadBrotherSimon"), mission="My Dead Brother (Kill Edgar)"),
    Enemy("Sorcerer", Pawn("PawnBalance_Sorcerer"), tags=Tag.DragonKeep),
    Enemy("Badass Sorcerer", Pawn("PawnBalance_Sorcerer_Badass"), tags=Tag.DragonKeep),
    Enemy("Fire Mage", Pawn("PawnBalance_FireMage"), tags=Tag.DragonKeep),
    Enemy("Badass Fire Mage", Pawn("PawnBalance_FireMage_Badass"), tags=Tag.DragonKeep),
    Mission("The Amulet (Buy Miz's Amulet)", MissionDefinition("GD_Aster_AmuletDoNothing.M_AmuletDoNothing"), tags=Tag.DragonKeep|Tag.LongMission),
    Mission("The Amulet (Punch Miz In The Face)", MissionTurnInAlt("GD_Aster_AmuletDoNothing.M_AmuletDoNothing"), tags=Tag.DragonKeep|Tag.LongMission),
        # Upon reaccepting mission, Miz has no behavior
    Enemy("Necromancer", Pawn("PawnBalance_Necromancer"), tags=Tag.DragonKeep),
    Enemy("Badass Necromancer", Pawn("PawnBalance_Necro_Badass"), tags=Tag.DragonKeep),
    Enemy("Sorcerer's Daughter", Pawn("PawnBalance_AngelBoss"), tags=Tag.DragonKeep|Tag.SlowEnemy, rarities=(33,33)),
    Enemy("Handsome Sorcerer",
        Behavior("GD_ButtStallion_Proto.Character.AIDef_ButtStallion_Proto:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_46"),
        Behavior("GD_DragonBridgeBoss.InteractiveObjects.IO_DragonBridgeBoss_LootExplosion:BehaviorProviderDefinition_0.Behavior_SpawnItems_32"),
        Behavior(
            "GD_ButtStallion_Proto.Character.AIDef_ButtStallion_Proto:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_43",
            "GD_ButtStallion_Proto.Character.AIDef_ButtStallion_Proto:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_44",
            "GD_ButtStallion_Proto.Character.AIDef_ButtStallion_Proto:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_45",
            "GD_DragonBridgeBoss.InteractiveObjects.IO_DragonBridgeBoss_LootExplosion:BehaviorProviderDefinition_0.Behavior_SpawnItems_53",
            "GD_DragonBridgeBoss.InteractiveObjects.IO_DragonBridgeBoss_LootExplosion:BehaviorProviderDefinition_0.Behavior_SpawnItems_30",
        inject=False),
    tags=Tag.DragonKeep|Tag.SlowEnemy, rarities=(33,33,33)),
    Mission("Pet Butt Stallion", MissionDefinition("GD_Aster_PetButtStallion.M_PettButtStallion"), tags=Tag.DragonKeep|Tag.Freebie),
    Mission("Feed Butt Stallion", MissionDefinition("GD_Aster_FeedButtStallion.M_FeedButtStallion"), tags=Tag.DragonKeep|Tag.Freebie),
    Other("Butt Stallion Fart",
        Behavior("GD_ButtStallion_Proto.Character.AIDef_ButtStallion_Proto:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_66"),
    tags=Tag.DragonKeep|Tag.Freebie),
    Mission("Find Murderlin's Temple", MissionDefinition("GD_Aster_TempleSlaughter.M_TempleSlaughterIntro"), tags=Tag.DragonKeep|Tag.Freebie),
    Mission("Magic Slaughter: Round 1", MissionDefinition("GD_Aster_TempleSlaughter.M_TempleSlaughter1"), tags=Tag.DragonKeep|Tag.Slaughter),
    Mission("Magic Slaughter: Round 2", MissionDefinition("GD_Aster_TempleSlaughter.M_TempleSlaughter2"), tags=Tag.DragonKeep|Tag.Slaughter),
    Mission("Magic Slaughter: Round 3", MissionDefinition("GD_Aster_TempleSlaughter.M_TempleSlaughter3"), tags=Tag.DragonKeep|Tag.Slaughter|Tag.LongMission),
    Enemy("Wizard", Pawn("PawnBalance_Wizard"), mission="Magic Slaughter: Round 3", tags=Tag.RareEnemy),
    Mission("Magic Slaughter: Round 4", MissionDefinition("GD_Aster_TempleSlaughter.M_TempleSlaughter4"), tags=Tag.DragonKeep|Tag.Slaughter|Tag.LongMission),
    Mission("Magic Slaughter: Round 5", MissionDefinition("GD_Aster_TempleSlaughter.M_TempleSlaughter5"), tags=Tag.DragonKeep|Tag.Slaughter|Tag.VeryLongMission),
    Mission("Magic Slaughter: Badass Round", MissionDefinition("GD_Aster_TempleSlaughter.M_TempleSlaughter6Badass"), tags=Tag.DragonKeep|Tag.Slaughter|Tag.VeryLongMission),
    Enemy("Badass Wizard", Pawn("PawnBalance_Wizard_Badass"), mission="Magic Slaughter: Badass Round", tags=Tag.RareEnemy),
    Enemy("Warlord Slog", Pawn("PawnBalance_Orc_WarlordSlog", evolved=4), mission="Magic Slaughter: Badass Round"),
    Enemy("King of Orks", Pawn("PawnBalance_Orc_WarlordSlog", transform=4), mission="Magic Slaughter: Badass Round", tags=Tag.EvolvedEnemy),
    Mission("The Magic of Childhood", MissionDefinition("GD_Aster_TempleTower.M_TempleTower"), tags=Tag.DragonKeep|Tag.Slaughter|Tag.LongMission|Tag.Slaughter),
    Mission("Raiders of the Last Boss", MissionDefinition("GD_Aster_RaidBoss.M_Aster_RaidBoss"), tags=Tag.DragonKeep|Tag.Raid),
    Enemy("The Ancient Dragons of Destruction",
        Behavior("GD_Aster_RaidBossData.IOs.IO_LootSpewer:BehaviorProviderDefinition_0.Behavior_SpawnItems_706"),
        Behavior(
            "GD_Aster_RaidBossData.IOs.IO_LootSpewer:BehaviorProviderDefinition_0.Behavior_SpawnItems_702",
            "GD_Aster_RaidBossData.IOs.IO_LootSpewer:BehaviorProviderDefinition_0.Behavior_SpawnItems_703",
            "GD_Aster_RaidBossData.IOs.IO_LootSpewer:BehaviorProviderDefinition_0.Behavior_SpawnItems_704",
            "GD_Aster_RaidBossData.IOs.IO_LootSpewer:BehaviorProviderDefinition_0.Behavior_SpawnItems_705",
            "GD_Aster_RaidBossData.IOs.IO_LootSpewer:BehaviorProviderDefinition_0.Behavior_SpawnItems_707",
            "GD_Aster_RaidBossData.IOs.IO_LootSpewer:BehaviorProviderDefinition_0.Behavior_SpawnItems_708",
            "GD_Aster_RaidBossData.IOs.IO_LootSpewer:BehaviorProviderDefinition_0.Behavior_SpawnItems_709",
            "GD_Aster_RaidBossData.IOs.IO_LootSpewer:BehaviorProviderDefinition_0.Behavior_SpawnItems_710",
            "GD_Aster_RaidBossData.IOs.IO_LootSpewer:BehaviorProviderDefinition_0.Behavior_SpawnItems_711",
        inject=False),
    tags=Tag.DragonKeep|Tag.Raid),


    Enemy("Infected Badass Sprout", Pawn("PawnBalance_Infected_Badass_Midget"), tags=Tag.FightForSanctuary|Tag.MobFarm, rarities=(7,)),
    Other("Dahl Abandon Grave",
        Behavior("GD_Anemone_Balance_Treasure.InteractiveObjects.InteractiveObj_Brothers_Pile:BehaviorProviderDefinition_13.Behavior_SpawnItems_21"),
        DahlAbandonGrave(),
    tags=Tag.FightForSanctuary|Tag.Freebie),
    Enemy("Loot Nest", Pawn("PawnBalance_Infected_Mimic"), tags=Tag.FightForSanctuary),
    Enemy("New Pandora Soldier",
        Pawn(
            "PawnBalance_Flamer",
            "PawnBalance_NP_Enforcer",
            "PawnBalance_NP_BadassSniper",
            "PawnBalance_NP_Commander",
            "PawnBalance_NP_Enforcer",
            "PawnBalance_NP_Infecto",
            "PawnBalance_NP_Medic"
        ),
    tags=Tag.FightForSanctuary|Tag.MobFarm),
    Mission("The Oddest Couple",
        MissionDefinition("GD_Anemone_Side_OddestCouple.M_Anemone_OddestCouple"),
        OddestCouple("OldDust_Mission_Side.TheWorld:PersistentLevel.WillowInteractiveObject_2", "OldDust_P"),
    tags=Tag.FightForSanctuary),
    Enemy("Pizza-Addicted Skag", Pawn("PawnBalance_Infected_Moxxi_Skag"), mission="The Oddest Couple"),
    Mission("Space Cowboy", MissionDefinition("GD_Anemone_Side_SpaceCowboy.M_Anemone_SpaceCowboy"), tags=Tag.FightForSanctuary|Tag.LongMission),
        # Midget toilet porn doesnt respawn without savequit
    Enemy("Loot Midget (Space Cowboy)", SpaceCowboyMidget("PawnBalance_LootMidget_Marauder"), mission="Space Cowboy", rarities=(50,)),
    Enemy("Sand Worm",
          Pawn("PawnBalance_SandWorm_Queen", "PawnBalance_InfectedSandWorm"),
    tags=Tag.FightForSanctuary|Tag.MobFarm),
    Enemy("Ghost", Pawn("PawnBalance_Ghost"), tags=Tag.FightForSanctuary),
    Enemy("Bandit Leader (Nomad)", Pawn("PawnBalance_NomadBadass_Leader"), mission="The Vaughnguard"),
    Enemy("Bandit Leader (Marauder)", Pawn("PawnBalance_MarauderBadass_Leader"), mission="The Vaughnguard"),
    Enemy("Jerry", Pawn("PawnBalance_Ini_Scavenger"), mission="The Vaughnguard"),
    Mission("The Hunt is Vaughn", MissionDefinition("GD_Anemone_Side_VaughnPart2.M_Anemone_VaughnPart2"), tags=Tag.FightForSanctuary),
    Mission("Hypocritical Oath", MissionDefinition("GD_Anemone_Side_HypoOathPart1.M_HypocriticalOathPart1"), tags=Tag.FightForSanctuary),
        # Experiment doesnt respawn without savequit
    Enemy("Dr. Zed's Experiment",
        Pawn("PawnBalance_Anemone_Slagsteins1", "PawnBalance_Anemone_Slagsteins2"),
    mission="Hypocritical Oath"),
    Mission("Cadeuceus", MissionDefinition("GD_Anemone_Side_HypoOathPart2.M_HypocriticalOathPart2"), tags=Tag.FightForSanctuary),
        # Experiment doesnt respawn without savequit
    Mission("The Vaughnguard", MissionDefinition("GD_Anemone_Side_VaughnPart1.M_Anemone_VaughnPart1"), tags=Tag.FightForSanctuary|Tag.LongMission),
        # Recruits dont respawn without savequit
    Enemy("Uranus", Pawn("PawnBalance_Uranus"), tags=Tag.FightForSanctuary|Tag.SlowEnemy),
    Mission("Claptocurrency", MissionDefinition("GD_Anemone_Side_Claptocurrency.M_Claptocurrency"), tags=Tag.FightForSanctuary),
        # On repeat, cannot place blocks without savequit
    Enemy("The Dark Web", Pawn("PawnBalance_Anemone_TheDarkWeb"), mission="Claptocurrency"),
    Enemy("Cassius", Pawn("PawnBalance_Anemone_Cassius"), tags=Tag.FightForSanctuary|Tag.SlowEnemy),
    Mission("Echoes of the Past", MissionDefinition("GD_Anemone_Side_Echoes.M_Anemone_EchoesOfThePast"),
        EchoesOfThePast("ResearchCenter_MissionSide.TheWorld:PersistentLevel.WillowInteractiveObject_1", "ResearchCenter_P"),
    tags=Tag.FightForSanctuary),
        # ECHO mission giver not interactable after completion
    Mission("Paradise Found", MissionTurnIn("GD_Anemone_Plot_Mission060.M_Anemone_PlotMission060"), tags=Tag.FightForSanctuary|Tag.Excluded),
    Mission("Sirentology",
        MissionDefinition("GD_Anemone_Side_Sirentology.M_Anemone_Sirentology"),
        Sirentology(),
    tags=Tag.FightForSanctuary|Tag.LongMission),
    Mission("My Brittle Pony", MissionDefinition("GD_Anemone_Side_MyBrittlePony.M_Anemone_MyBrittlePony"), tags=Tag.FightForSanctuary|Tag.LongMission),
        # Brick and enemy waves dont respawn without savequit
    Other("Butt Stallion with Mysterious Amulet",
        Behavior("GD_Anem_ButtStallion.Character.AIDef_Anem_ButtStallion:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_18"),
        ButtstallionWithAmulet(),
    tags=Tag.DragonKeep|Tag.FightForSanctuary|Tag.Freebie, content=Tag.FightForSanctuary),
    Mission("BFFFs", MissionDefinition("GD_Anemone_Side_EyeSnipers.M_Anemone_EyeOfTheSnipers"), tags=Tag.FightForSanctuary),
        # Lieutenants dont respawn without savequit
    Enemy("Lt. Bolson", Pawn("PawnBalance_Lt_Bolson"), tags=Tag.FightForSanctuary|Tag.SlowEnemy),
    Enemy("Lt. Angvar", Pawn("PawnBalance_NP_Lt_Angvar"), tags=Tag.FightForSanctuary|Tag.SlowEnemy),
    Enemy("Lt. Tetra", Pawn("PawnBalance_NP_Lt_Tetra"), tags=Tag.FightForSanctuary|Tag.SlowEnemy),
    Enemy("Lt. Hoffman", Pawn("PawnBalance_NP_Lt_Hoffman"), tags=Tag.FightForSanctuary|Tag.SlowEnemy),
    Mission("Chief Executive Overlord", MissionDefinition("GD_Anemone_Side_VaughnPart3.M_Anemone_VaughnPart3"), tags=Tag.FightForSanctuary|Tag.Freebie),
    Mission("A Most Cacophonous Lure", MissionDefinition("GD_Anemone_Side_RaidBoss.M_Anemone_CacophonousLure"), tags=Tag.FightForSanctuary|Tag.Raid),
        # Haderax doesnt respawn without savequit
    Enemy("Haderax The Invincible",
        Attachment("ObjectGrade_DalhEpicCrate_Digi_PeakOpener", *range(12), configuration=0),
        Behavior("GD_Anemone_SandWormBoss_1.Character.BodyDeath_Anemone_SandWormBoss_1:BehaviorProviderDefinition_2.Behavior_SpawnItems_5", inject=False),
        Haderax(),
    tags=Tag.FightForSanctuary|Tag.Raid),
    Other("Writhing Deep Dune Raider Chest",
        Attachment("ObjectGrade_DalhEpicCrate_Digi_RocketLauncher", *range(10)),
    tags=Tag.FightForSanctuary|Tag.Excluded),



    Mission("The Hunger Pangs",
        MissionDefinition("GD_Allium_TG_Plot_Mission01.M_Allium_ThanksgivingMission01"),
        MissionGiver("GD_Allium_Torgue.Character.Pawn_Allium_Torgue:MissionDirectivesDefinition_1", True, True, "Hunger_P"),
    tags=Tag.WattleGobbler|Tag.VeryLongMission),
        # On reaccept, no sequence until after savequit
    Enemy("The Rat in the Hat", Pawn("PawnBalance_RatChef"), mission="The Hunger Pangs"),
    Enemy("Chef Gouda Remsay", Pawn("PawnBalance_ButcherBoss"), mission="The Hunger Pangs"),
    Enemy("Chef Brulee", Pawn("PawnBalance_ButcherBoss2"), mission="The Hunger Pangs"),
    Enemy("Chef Bork Bork", Pawn("PawnBalance_ButcherBoss3"), mission="The Hunger Pangs"),
    Enemy("Glasspool, Tribute of Wurmwater", Pawn("PawnBalance_SandMale"), mission="The Hunger Pangs"),
    Enemy("William, Tribute of Wurmwater", Pawn("PawnBalance_SandFemale"), mission="The Hunger Pangs"),
    Enemy("Axel, Tribute of Opportunity", Pawn("PawnBalance_EngineerMale"), mission="The Hunger Pangs"),
    Enemy("Rose, Tribute of Opportunity", Pawn("PawnBalance_EngineerFemale"), mission="The Hunger Pangs"),
    Enemy("Fiona, Tribute of Sanctuary", Pawn("PawnBalance_RaiderFemale"), tags=Tag.WattleGobbler|Tag.RareEnemy, rarities=(67,)),
    Enemy("Max, Tribute of Sanctuary", Pawn("PawnBalance_RaiderMale"), tags=Tag.WattleGobbler|Tag.RareEnemy, rarities=(67,)),
    Enemy("Strip, Tribute of Southern Shelf", Pawn("PawnBalance_FleshripperFemale"), tags=Tag.WattleGobbler|Tag.RareEnemy, rarities=(67,)),
    Enemy("Flay, Tribute of Southern Shelf", Pawn("PawnBalance_FleshripperMale"), tags=Tag.WattleGobbler|Tag.RareEnemy, rarities=(67,)),
    Enemy("Fuse, Tribute of Frostburn", Pawn("PawnBalance_IncineratorMale"), tags=Tag.WattleGobbler|Tag.RareEnemy, rarities=(67,)),
    Enemy("Cynder, Tribute of Frostburn", Pawn("PawnBalance_IncineratorFemale"), tags=Tag.WattleGobbler|Tag.RareEnemy, rarities=(67,)),
    Enemy("Annie, Tribute of Lynchwood", Pawn("PawnBalance_Lynchwood_Female"), tags=Tag.WattleGobbler|Tag.RareEnemy, rarities=(67,)),
    Enemy("Garret, Tribute of Lynchwood", Pawn("PawnBalance_Lynchwood_Male"), tags=Tag.WattleGobbler|Tag.RareEnemy, rarities=(67,)),
    Enemy("Moretus, Tribute of Sawtooth Cauldron", Pawn("PawnBalance_CraterMale"), tags=Tag.WattleGobbler|Tag.RareEnemy, rarities=(67,)),
    Enemy("Bailly, Tribute of Sawtooth Cauldron", Pawn("PawnBalance_CraterFemale"), tags=Tag.WattleGobbler|Tag.RareEnemy, rarities=(67,)),
    Enemy("Ravenous Wattle Gobbler",
        Pawn("PawnBalance_BigBird", "PawnBalance_BigBird_HARD"),
        Behavior("GD_Allium_Lootables.IO.IO_Hunger_BossLoot:BehaviorProviderDefinition_1.Behavior_SpawnItems_3", inject=False),
    tags=Tag.WattleGobbler|Tag.SlowEnemy),
    Mission("Grandma Flexington's Story",
        MissionDefinition("GD_Allium_GrandmaFlexington.M_ListenToGrandma"),
        Behavior("GD_Allium_TorgueGranma.Character.AIDef_Torgue:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_6"),
    tags=Tag.WattleGobbler|Tag.LongMission|Tag.Freebie),
    Mission("Grandma Flexington's Story: Raid Difficulty", MissionDefinition("GD_Allium_Side_GrandmaRaid.M_ListenToGrandmaRaid"),
        Behavior("GD_Allium_TorgueGranma.Character.AIDef_Torgue:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_3"),
        GrandmaStoryRaid(),
    tags=Tag.WattleGobbler|Tag.Raid|Tag.VeryLongMission),
        # Grandma not interactable without savequit after completion

    Mission("Get Frosty",
        MissionDefinition("GD_Allium_KillSnowman.M_KillSnowman"),
        MissionGiver("Xmas_Mission.TheWorld:PersistentLevel.WillowAIPawn_28.MissionDirectivesDefinition_0", True, True, "Xmas_P"),
    tags=Tag.MercenaryDay|Tag.VeryLongMission),
        # On reaccept, no marcus AI until after savequit
    Enemy("The Abominable Mister Tinder Snowflake",
        Pawn("PawnBalance_SnowMan", "PawnBalance_SnowMan_HARD"),
        Behavior(
            "GD_Snowman.Death.BodyDeath_SnowMan:BehaviorProviderDefinition_6.Behavior_SpawnItems_9",
            "GD_Snowman.Death.BodyDeath_SnowMan:BehaviorProviderDefinition_6.Behavior_SpawnItems_10",
            "GD_Snowman.Death.BodyDeath_SnowMan:BehaviorProviderDefinition_6.Behavior_SpawnItems_11",
        inject=False),
    tags=Tag.MercenaryDay|Tag.SlowEnemy),
    Mission("Special Delivery", MissionDefinition("GD_Allium_Delivery.M_Delivery"), tags=Tag.MercenaryDay),
        # Toys dont respawn until savequit; resetting dens works
    
    Mission("The Bloody Harvest",
        MissionDefinition("GD_FlaxMissions.M_BloodHarvest"),
        MissionGiver("Pumpkin_Patch_Dynamic.TheWorld:PersistentLevel.WillowAIPawn_5.MissionDirectivesDefinition_0", True, True, "Pumpkin_Patch_P"),
    tags=Tag.BloodyHarvest|Tag.VeryLongMission),
    Enemy("Enchanted Skeleton", Pawn("PawnBalance_HallowSkeletonEnchanted"), tags=Tag.BloodyHarvest|Tag.VeryRareEnemy),
    Enemy("Sully the Blacksmith", Pawn("PawnBalance_Spycho"), mission="The Bloody Harvest"),
    Enemy("Pumpkin Kingpin/Jacques O'Lantern",
        Behavior("GD_PumpkinheadFlying.Character.DeathDef_Pumpkinheadflying:BehaviorProviderDefinition_0.Behavior_SpawnItems_209"),
        Behavior("GD_Flax_Lootables.IOs.IO_Pumpkin_BossLoot:BehaviorProviderDefinition_1.Behavior_SpawnItems_210", inject=False),
    tags=Tag.BloodyHarvest|Tag.SlowEnemy, rarities=(33,33,33)),
    Mission("Trick or Treat", MissionDefinition("GD_FlaxMissions.M_TrickOrTreat"), tags=Tag.BloodyHarvest),
        # Not all candies collectable again until savequit
    Enemy("Clark the Combusted Cryptkeeper", Pawn("PawnBalance_UndeadFirePsycho_Giant"), tags=Tag.BloodyHarvest|Tag.SlowEnemy|Tag.MissionLocation|Tag.VeryLongMission),

    Mission("Fun, Sun, and Guns",
        MissionDefinition("GD_Nast_Easter_Plot_M01.M_Nast_Easter"),
        MissionGiver("GD_Nasturtium_Hammerlock.Character.Pawn_Hammerlock:MissionDirectivesDefinition_1", True, True, "Easter_P"),
    tags=Tag.SonOfCrawmerax|Tag.VeryLongMission),
    Enemy("Son of Crawmerax the Invincible", Pawn("PawnBalance_Crawmerax_Son"), mission="Fun, Sun, and Guns", rarities=(33,33,33)),
    Enemy("The Invincible Son of Crawmerax the Invincible",
        Pawn("PawnBalance_Crawmerax_Son_Raid"),
        Behavior(
            "GD_Nasturtium_Lootables.IOs.IO_BossLootSpout:BehaviorProviderDefinition_0.Behavior_SpawnItems_502",
            "GD_Nasturtium_Lootables.IOs.IO_BossLootSpout:BehaviorProviderDefinition_0.Behavior_SpawnItems_6",
            "GD_Nasturtium_Lootables.IOs.IO_BossLootSpout:BehaviorProviderDefinition_0.Behavior_SpawnItems_7",
            "GD_Nasturtium_Lootables.IOs.IO_BossLootSpout:BehaviorProviderDefinition_0.Behavior_SpawnItems_8",
        inject=False),
    tags=Tag.SonOfCrawmerax|Tag.Raid),
    Mission("Victims of Vault Hunters", MissionDefinition("GD_Nast_Easter_Mission_Side01.M_Nast_Easter_Side01"), tags=Tag.SonOfCrawmerax|Tag.LongMission),
        # Evidence locations dont reset without savequit
    Enemy("Sparky, Son of Flynt", Pawn("PawnBalance_FlyntSon", "PawnBalance_FlyntSon_Run"), tags=Tag.SonOfCrawmerax|Tag.SlowEnemy),



    Mission("A Match Made on Pandora",
        MissionDefinition("GD_Nast_Vday_Mission_Plot.M_Nast_Vday"),
        MissionGiver("GD_Nasturtium_Moxxi.Character.Pawn_Moxxi:MissionDirectivesDefinition_1", True, True, "Distillery_P"),
    tags=Tag.WeddingDayMassacre|Tag.VeryLongMission),
    Other("Loot Leprechaun",
        Behavior("GD_Nast_Leprechaun.Character.CharClass_Nast_Leprechaun:BehaviorProviderDefinition_5.Behavior_SpawnItems_26"),
        Behavior("GD_Nast_Leprechaun.Character.CharClass_Nast_Leprechaun:BehaviorProviderDefinition_5.Behavior_SpawnItems_27"),
    tags=Tag.WeddingDayMassacre, rarities=(7,)),
    Enemy("BLNG Loader", Pawn("PawnBalance_BlingLoader"), mission="A Match Made on Pandora"),
    Enemy("Colin Zaford",
        Pawn("PawnBalance_GoliathGroom", "PawnBalance_GoliathGroomRaid", evolved=5),
        Behavior("GD_GoliathGroom.Death.BodyDeath_GoliathGroom:BehaviorProviderDefinition_6.Behavior_SpawnItems_8", inject=False),
    tags=Tag.WeddingDayMassacre|Tag.SlowEnemy),
    Enemy("Bridget Hodunk",
        Pawn("PawnBalance_GoliathBride", "PawnBalance_GoliathBrideRaid", evolved=5),
        Behavior("GD_GoliathBride.Death.BodyDeath_GoliathBride:BehaviorProviderDefinition_6.Behavior_SpawnItems_12", inject=False),
    tags=Tag.WeddingDayMassacre|Tag.SlowEnemy),
    Enemy("Sigmand", Pawn("PawnBalance_Nast_ThresherWhite"), tags=Tag.WeddingDayMassacre),
    Enemy("Ikaroa", Pawn("PawnBalance_Nast_ThresherGreen"), tags=Tag.WeddingDayMassacre),
    Enemy("Moby", Pawn("PawnBalance_Nast_ThresherBlue"), tags=Tag.WeddingDayMassacre|Tag.SlowEnemy),
    Enemy("Fire Crak'n", Pawn("PawnBalance_Nast_ThresherPurple"), tags=Tag.WeddingDayMassacre|Tag.SlowEnemy),
    Enemy("Rue, The Love Thresher", Pawn("PawnBalance_Nast_ThresherOrange"), tags=Tag.WeddingDayMassacre|Tag.SlowEnemy, rarities=(50, 50)),
    Mission("Learning to Love", MissionDefinition("GD_Nast_Vday_Mission_Side01.M_Nast_Vday_Side01"),
        MissionGiver("GD_Nasturtium_Moxxi.Character.Pawn_Moxxi:MissionDirectivesDefinition_1", True, True, "Distillery_P"),
    tags=Tag.WeddingDayMassacre|Tag.LongMission),
    Enemy("Ed", Pawn("PawnBalance_BadassJunkLoader"), mission="Learning to Love"),
    Enemy("Stella", Pawn("PawnBalance_LoaderGirl"), mission="Learning to Love"),
    Enemy("Innuendobot 5000", Pawn("PawnBalance_Innuendobot_NPC"), mission="Learning to Love"),



    Mission("Dr. T and the Vault Hunters", MissionDefinition("GD_Lobelia_UnlockDoor.M_Lobelia_UnlockDoor"), tags=Tag.DigistructPeak|Tag.Freebie),
    Mission("A History of Simulated Violence", MissionDefinition("GD_Lobelia_TestingZone.M_TestingZone"), tags=Tag.DigistructPeak|Tag.VeryLongMission),
    DigiEnemy("Digistruct Assassin Wot", Pawn("PawnBalance_Assassin1_Digi"), fallback="Assassin Wot", tags=Tag.DigistructPeak|Tag.DigistructEnemy, rarities=(100, 100, 50)),
    DigiEnemy("Digistruct Assassin Oney", Pawn("PawnBalance_Assassin2_Digi"), fallback="Assassin Oney", tags=Tag.DigistructPeak|Tag.DigistructEnemy, rarities=(100, 100, 50)),
    DigiEnemy("Digistruct Assassin Reeth", Pawn("PawnBalance_Assassin3_Digi"), fallback="Assassin Reeth", tags=Tag.DigistructPeak|Tag.DigistructEnemy, rarities=(100, 100, 50)),
    DigiEnemy("Digistruct Assassin Rouf", Pawn("PawnBalance_Assassin4_Digi"), fallback="Assassin Rouf", tags=Tag.DigistructPeak|Tag.DigistructEnemy, rarities=(100, 100, 50)),
    Mission("More History of Simulated Violence", MissionDefinition("GD_Lobelia_TestingZone.M_TestingZoneRepeatable"), tags=Tag.DigistructPeak|Tag.VeryLongMission),
    DigiEnemy("Digistruct Scorch", Pawn("PawnBalance_SpiderantScorch_Digi"), fallback="Scorch", tags=Tag.DigistructPeak|Tag.DigistructEnemy, rarities=(50, 50)),
    DigiEnemy("Digistruct Black Queen", Pawn("PawnBalance_SpiderantBlackQueen_Digi"), fallback="The Black Queen", tags=Tag.DigistructPeak|Tag.DigistructEnemy, rarities=(100, 33)),
    DigiEnemy("Bone Head v3.0", Pawn("PawnBalance_BoneHead_V3"), fallback="Bone Head 2.0", tags=Tag.DigistructPeak|Tag.DigistructEnemy, rarities=(50, 50)),
    DigiEnemy("Digistruct Doc Mercy", Pawn("PawnBalance_MrMercy_Digi"), fallback="Doc Mercy", tags=Tag.DigistructPeak|Tag.DigistructEnemy, rarities=(100, 50)),
    DigiEnemy("Digistruct Dukino's Mom", Pawn("PawnBalance_Skagzilla_Digi"), fallback="Dukino's Mom", tags=Tag.DigistructPeak|Tag.DigistructEnemy, rarities=(100, 33, 33)),
    Enemy("010011110100110101000111-010101110101010001001000",
        Pawn("PawnBalance_SpiderTank_Boss"),
        Behavior(
            "GD_SpiderTank_Boss.Death.DeathDef_SpiderTank_Boss:BehaviorProviderDefinition_0.Behavior_SpawnItems_42",
            "GD_SpiderTank_Boss.Death.DeathDef_SpiderTank_Boss:BehaviorProviderDefinition_0.Behavior_SpawnItems_43",
            "GD_SpiderTank_Boss.Death.DeathDef_SpiderTank_Boss:BehaviorProviderDefinition_0.Behavior_SpawnItems_44",
            "GD_SpiderTank_Boss.Death.DeathDef_SpiderTank_Boss:BehaviorProviderDefinition_0.Behavior_SpawnItems_45",
            "GD_SpiderTank_Boss.Death.DeathDef_SpiderTank_Boss:BehaviorProviderDefinition_0.Behavior_SpawnItems_46",
            "GD_SpiderTank_Boss.Death.DeathDef_SpiderTank_Boss:BehaviorProviderDefinition_0.Behavior_SpawnItems_47",
        inject=False),
    tags=Tag.DigistructPeak|Tag.DigistructEnemy, rarities=(100, 100, 100, 50, 50, 50, 33, 33, 33)),
    DigiEnemy("Saturn v2.0", Pawn("PawnBalance_LoaderUltimateBadass_Digi"), fallback="Saturn", tags=Tag.DigistructPeak|Tag.DigistructEnemy, rarities=(100, 100, 50, 50)),
)



"""

TODO:
- Fix leviathan's loot fling with smol items
- BL2fix midget compatibility
- prevent mcshooty from despawning after completion?

LOGIC:
- buttstallion w/ amulet requires amulet
- pot o' gold requires pot o' gold
- peak enemies past OP 0 requires moxxi's endowment
- haderax launcher chest requires toothpick + retainer

CUT:
- pot of gold "boosters"
- loot goon chests
- loot loader chests
- slot machines
- tina slot machines
- roland's armory
- Gobbler slag pistol
- digi peak chests
- Wam Bam loot injectors
    GD_Nasturtium_Lootables.InteractiveObjects.ObjectGrade_NastChest_Epic
    ^ Same as all Wam Bam red chests
- chest being stolen by yeti
- Caravan
    GD_Orchid_PlotDataMission04.Mission04.Balance_Orchid_CaravanChest
- halloween gun sacrifice
- dragon keep altar
- marcus statue suicide
- Scarlet Caravan
- Wedding balloon
    GD_Nasturtium_Lootables.IOs.IO_BossBalloons:BehaviorProviderDefinition_1.Behavior_SpawnItems_0
    GD_Nasturtium_Lootables.IOs.IO_BossBalloons:BehaviorProviderDefinition_1.Behavior_SpawnItems_2
    GD_Nasturtium_Lootables.IOs.IO_BossBalloons:BehaviorProviderDefinition_1.Behavior_SpawnItems_1
- Rotgut Fishing Chest
- Enemy("Mr. Miz",
    # GD_Aster_AmuletDoNothingData.VendingMachineGrades.ObjectGrade_VendingMachine_Pendant
    # note that logic requires amulet for buttstallion
tags=Tag.DragonKeep|Tag.LongMission),
- Butt Stallion Legendary Fart
    Behavior("GD_ButtStallion_Proto.Character.AIDef_ButtStallion_Proto:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_66"),

"""
