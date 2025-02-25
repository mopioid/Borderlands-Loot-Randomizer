from unrealsdk import Log, FindAll, FindObject, GetEngine, KeepAlive
from unrealsdk import UObject, UFunction, FStruct

from ..defines import *

from .. import locations

from ..locations import Behavior, Dropper, MapDropper
from ..enemies import Enemy, Pawn
from ..missions import (
    PlaythroughDelegate,
    Mission,
    MissionDefinition,
    MissionTurnIn,
    MissionTurnInAlt,
    MissionDropper,
    MissionStatusDelegate,
    MissionPickup,
    MissionGiver,
    MissionObject,
)
from ..other import Other, Attachment, PositionalChest

from typing import Any, Dict, List, Optional, Sequence, Union


class LoyaltyRewards(Dropper):
    def enable(self) -> None:
        self.hook(
            "WillowGame.WillowPlayerController.AwardItemRewardEarned",
            lambda c, f, p: False,
        )


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


class PopulationDefinition:
    uobject: UObject
    original_weights: Sequence[float]

    def __init__(self, path: str) -> None:
        uobject = FindObject("PopulationDefinition", path)
        if not uobject:
            raise RuntimeError(f"Could not locate PopulationDefinition {path}")

        self.uobject = uobject

        self.original_weights = tuple(
            archetype.Probability.BaseValueConstant
            for archetype in uobject.ActorArchetypeList
        )

    def reset_archetypes(self) -> None:
        for original_weight, archetype in zip(
            self.original_weights, self.uobject.ActorArchetypeList
        ):
            archetype.Probability.BaseValueConstant = original_weight


class HolidayEvents(MapDropper):
    paths = ("*",)

    holidays: Sequence[str] = (
        "Bloody Harvest",
        "Celebration",
        "Mercenary Day",
    )
    holiday: Optional[str] = None

    populations: Sequence[PopulationDefinition] = ()

    def enable_holiday(self) -> None:
        self.populations = ()
        if self.holiday == "Bloody Harvest":
            self.bloody_harvest()
        elif self.holiday == "Celebration":
            self.celebration()
        elif self.holiday == "Mercenary Day":
            self.mercenary_day()

    def disable_holiday(self) -> None:
        for population in self.populations:
            population.reset_archetypes()
        self.populations = ()

    def enable(self) -> None:
        super().enable()

        from datetime import date

        today = date.today()
        year = today.year

        if date(year, 10, 31) <= today <= date(year, 11, 2):
            self.holiday = "Bloody Harvest"

        elif date(year, 11, 11) <= today <= date(year, 11, 19):
            self.holiday = "Celebration"

        elif today >= date(year, 12, 23) or today <= date(year, 1, 5):
            self.holiday = "Mercenary Day"

        self.hook(
            "WillowGame.FastTravelStationGFxObject.SendLocationData",
            self.send_location_data,
        )
        self.hook(
            "WillowGame.FastTravelStationGFxMovie.extActivate",
            self.fast_travel_activate,
        )

    def append_holiday_travels(self, travels: Sequence[str]) -> Sequence[str]:
        appended = list(travels)
        appended.append("-")
        for holiday in self.holidays:
            action = "Disable " if holiday == self.holiday else "Enable "
            appended.append(action + holiday)
        return appended

    def send_location_data(
        self, caller: UObject, _f: UFunction, params: FStruct
    ) -> bool:
        caller.SendLocationData(
            self.append_holiday_travels(params.LocationDisplayNames),
            params.LocationStationNames,
            params.InitialSelectionIndex,
            params.CurrentWaypointIndex,
        )
        return False

    def fast_travel_activate(
        self, caller: UObject, _f: UFunction, params: FStruct
    ) -> bool:
        original_length = len(tuple(caller.LocationDisplayNames))
        holiday_index: int = params.LocationIndex - original_length - 1
        if holiday_index < 0:
            return True

        self.disable_holiday()

        selected_holiday = self.holidays[holiday_index]
        if self.holiday == selected_holiday:
            self.holiday = None
        else:
            self.holiday = selected_holiday
            self.enable_holiday()

        if caller.CurrentWaypointStationDef:
            stations = tuple(caller.LocationStationDefinitions)
            waypoint_station = caller.CurrentWaypointStationDef
            waypoint_index = stations.index(waypoint_station)
        else:
            waypoint_index = -1

        travels = self.append_holiday_travels(caller.LocationDisplayNames)

        caller.FastTravelClip.SendLocationData(
            travels,
            list(caller.LocationStationStrings),
            caller.InitialSelectionIndex,
            waypoint_index,
        )

        for _ in travels:
            caller.FastTravelClip.ScrollLocationListDown()

        for _ in range(len(travels) - params.LocationIndex - 1):
            caller.FastTravelClip.ScrollLocationListUp()

        return False

    def entered_map(self) -> None:
        self.enable_holiday()

    def exited_map(self) -> None:
        pass

    def bloody_harvest(self) -> None:
        if locations.map_name != "Deadsurface_P".casefold():
            return

        barrels = PopulationDefinition(
            "GD_Explosives.Populations.Pop_BarrelMixture",
        )
        scavs = PopulationDefinition(
            "GD_Population_Scavengers.MapMixes.PopDef_ScavMix_SerentitysWaste",
        )
        pumpkins = PopulationDefinition(
            "GD_Population_Scavengers.HolidayMixes.Pumpkin.PopDef_ScavMix_Pumpkin",
        )
        deadlift = PopulationDefinition(
            "GD_SpacemanDeadlift.Population.PopDef_SpacemanDeadlift",
        )

        self.populations = (barrels, scavs, pumpkins, deadlift)

        for archetype in barrels.uobject.ActorArchetypeList:
            balance = archetype.SpawnFactory.ObjectBalanceDefinition
            if balance and balance.Name == "BD_Barrel_Shift_Harvest":
                archetype.Probability.BaseValueConstant = 1
            else:
                archetype.Probability.BaseValueConstant = 0

        for archetype in scavs.uobject.ActorArchetypeList:
            balance = archetype.SpawnFactory.PopulationDef
            if balance and balance.Name == "PopDef_ScavMix_Pumpkin":
                archetype.Probability.BaseValueConstant = 1
            else:
                archetype.Probability.BaseValueConstant = 0

        for archetype in pumpkins.uobject.ActorArchetypeList:
            balance = archetype.SpawnFactory.PawnBalanceDefinition
            if not balance:
                continue
            if balance.Name == "PawnBalance_ScavengerBandit_Pumpkin":
                archetype.Probability.BaseValueConstant = 2
            if balance.Name == "PawnBalance_ScavengerPsycho_Pumpkin":
                archetype.Probability.BaseValueConstant = 1
            if balance.Name == "PawnBalance_ScavMidget_Pumpkin":
                archetype.Probability.BaseValueConstant = 0.66
            if balance.Name == "PawnBalance_ScavengerBandit_Jetpack_Pumpkin":
                archetype.Probability.BaseValueConstant = 1

        for actor in deadlift.uobject.ActorArchetypeList:
            balance = actor.SpawnFactory.PawnBalanceDefinition
            if (
                balance
                and balance.Name == "PawnBalance_SpacemanDeadlift_Pumpkin"
            ):
                actor.Probability.BaseValueConstant = 1
            else:
                actor.Probability.BaseValueConstant = 0

    def celebration(self) -> None:
        try:
            barrels = PopulationDefinition(
                "GD_Explosives.Populations.Pop_BarrelMixture",
            )
            self.populations = (barrels,)
            for archetype in barrels.uobject.ActorArchetypeList:
                balance = archetype.SpawnFactory.ObjectBalanceDefinition
                if balance and balance.Name == "BD_Barrel_Shift_Celebrate":
                    archetype.Probability.BaseValueConstant = 1
        except RuntimeError:
            pass

    def mercenary_day(self) -> None:
        try:
            barrels = PopulationDefinition(
                "GD_Explosives.Populations.Pop_BarrelMixture",
            )
            self.populations = (barrels,)
            for archetype in barrels.uobject.ActorArchetypeList:
                balance = archetype.SpawnFactory.ObjectBalanceDefinition
                if balance and balance.Name == "BD_Barrel_Shift_Mercenary":
                    archetype.Probability.BaseValueConstant = 1
        except RuntimeError:
            pass

        if locations.map_name == "Moonsurface_P".casefold():
            zilla = PopulationDefinition(
                "GD_Cork_Population_EleBeast.Mix.PopDef_GiantBeasts_Mix",
            )
            self.populations = (*self.populations, zilla)

            for archetype in zilla.uobject.ActorArchetypeList:
                population = archetype.SpawnFactory.PopulationDef
                if population and population.Name == "PopDef_Frostzilla":
                    archetype.Probability.BaseValueConstant = 1
                else:
                    archetype.Probability.BaseValueConstant = 0

        if locations.map_name == "RandDFacility_P".casefold():
            dahl = PopulationDefinition(
                "GD_Population_Dahl.MapMixes.PopDef_DahlMix_RnD",
            )
            merry_dahl = PopulationDefinition(
                "GD_Population_Dahl.MapMixes.PopDef_DahlMix_RnD_MercDay",
            )
            self.populations = (*self.populations, dahl, merry_dahl)

            for archetype in dahl.uobject.ActorArchetypeList:
                balance = archetype.SpawnFactory.PopulationDef
                if balance and balance.Name == "PopDef_DahlMix_RnD_MercDay":
                    archetype.Probability.BaseValueConstant = 1
                else:
                    archetype.Probability.BaseValueConstant = 0

            for archetype in merry_dahl.uobject.ActorArchetypeList:
                population = archetype.SpawnFactory.PopulationDef
                if (
                    population
                    and population.Name
                    == "PopMix_Dahl_Elemental_Marines_MercDay"
                ):
                    archetype.Probability.BaseValueConstant = 0

        if locations.map_name == "Wreck_P".casefold():
            scavs = PopulationDefinition(
                "GD_Population_Scavengers.MapMixes.PopDef_ScavMix_PitysFall",
            )
            merry_scavs = PopulationDefinition(
                "GD_Population_Scavengers.HolidayMixes.MercDay.PopDef_ScavMix_MercDay",
            )
            self.populations = (*self.populations, scavs, merry_scavs)

            for archetype in scavs.uobject.ActorArchetypeList:
                balance = archetype.SpawnFactory.PawnBalanceDefinition
                if balance:
                    if balance.Name == "PawnBalance_ScavengerBandit_Jetpack":
                        archetype.Probability.BaseValueConstant = 0
                else:
                    population = archetype.SpawnFactory.PopulationDef
                    if population:
                        if population.Name == "PopDef_ScavMix_MercDay":
                            archetype.Probability.BaseValueConstant = 1

            for archetype in merry_scavs.uobject.ActorArchetypeList:
                balance = archetype.SpawnFactory.PawnBalanceDefinition
                if (
                    balance
                    and balance.Name
                    == "PawnBalance_ScavengerBandit_Jetpack_MercDay"
                ):
                    archetype.Probability.BaseValueConstant = 1


class PumpkinBarrel(MapDropper):
    paths = ("Deadsurface_P",)

    def killed(self, caller: UObject, _f: UFunction, _p: FStruct) -> bool:
        if (
            caller.InteractiveObjectDefinition.Name
            == "ExplodingBarrel_Shift_Harvest"
        ):
            spawn_loot(self.location.prepare_pools(), caller)
        return True

    def entered_map(self) -> None:
        self.hook("WillowGame.WillowInteractiveObject.KilledBy", self.killed)


class LastRequests(MissionDropper, MapDropper):
    # TODO: reward door not opening on repeat
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


class ObjectiveKillInfo(MissionDropper):
    damage_type: Optional[int]
    damage_causer: Optional[int]

    original_mission_weapon: bool
    original_damage_type: int
    original_damage_causer: int

    def __init__(
        self,
        path: str,
        damage_type: Optional[int] = None,
        damage_causer: Optional[int] = None,
    ) -> None:
        self.path = path
        self.damage_type = damage_type
        self.damage_causer = damage_causer
        super().__init__()

    def enable(self) -> None:
        super().enable()

        killinfo = FindObject("MissionObjectiveKillInfo", self.path)
        if not killinfo:
            raise Exception("Could not locate objective kill info")

        if self.damage_type:
            self.original_damage_type = killinfo.DamageType
            killinfo.DamageType = self.damage_type

        if self.damage_causer:
            self.original_damage_causer = killinfo.DamageCauserType
            killinfo.DamageCauserType = self.damage_causer

        self.original_mission_weapon = killinfo.bMissionWeapon
        killinfo.bMissionWeapon = False

    def disable(self) -> None:
        super().disable()

        killinfo = FindObject("MissionObjectiveKillInfo", self.path)
        if not killinfo:
            raise Exception("Could not locate objective kill info")

        if self.damage_type:
            killinfo.DamageType = self.original_damage_type

        if self.damage_causer:
            killinfo.DamageCauserType = self.original_damage_causer

        killinfo.bMissionWeapon = self.original_mission_weapon


class FriskedCorpse(MissionDropper, MapDropper):
    corpse: Optional[str]

    def __init__(self, map_name: str, corpse: str) -> None:
        self.corpse = corpse
        super().__init__(map_name)

    def used(self, caller: UObject, _f: UFunction, params: FStruct) -> bool:
        if UObject.PathName(caller) != self.corpse:
            return True

        mission = self.location.mission
        if not mission:
            raise Exception(f"No mission for corpse for {self.location.name}")

        if mission.current_status is not Mission.Status.Active:
            return True

        spawn_loot(
            self.location.prepare_pools(),
            mission.mission_definition.uobject,
            convert_struct(caller.Location),
        )
        return True

    def entered_map(self) -> None:
        self.hook("WillowGame.WillowInteractiveObject.UsedBy", self.used)


class Dick(MapDropper):
    paths = ("Deadsurface_P",)

    def directives(self, caller: UObject, _f: UFunction, _p: FStruct) -> bool:
        if (
            UObject.PathName(caller)
            != "GD_Co_LastRequests.M_LastRequests:Behavior_AddMissionDirectives_2"
        ):
            return True

        pawn = get_pawn("CharClass_Nel")
        if not pawn:
            return True

        location = (
            pawn.Location.X - 20,
            pawn.Location.Y + 20,
            pawn.Location.Z - 50,
        )
        spawn_loot(
            self.location.prepare_pools(), pawn, location, (-370, 354, -10)
        )

        self.unhook(
            "WillowGame.Behavior_AddMissionDirectives.ApplyBehaviorToContext"
        )
        return True

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

        self.hook(
            "WillowGame.Behavior_AddMissionDirectives.ApplyBehaviorToContext",
            self.directives,
        )


class TorgueO(MissionStatusDelegate, MapDropper):
    paths = ("Moonsurface_P",)

    kraggon_objective: UObject
    probe_behavior: UObject

    def enable(self) -> None:
        super().enable()

        kraggon_objective = FindObject(
            "MissionObjectiveDefinition",
            "GD_Co_ToroToro.M_ToroToro:FindKraggonDen",
        )
        probe_behavior = FindObject(
            "Behavior_RemoteCustomEvent",
            "GD_Cork_Weap_Pistol.FiringModes.Bullet_Pistol_Maliwan_MoxxisProbe:Behavior_RemoteCustomEvent_3",
        )
        if not (kraggon_objective and probe_behavior):
            raise Exception("Could not locate objects for Torgue-O")

        self.kraggon_objective = kraggon_objective
        self.probe_behavior = probe_behavior

    def damaged(self, caller: UObject, _f: UFunction, params: FStruct) -> bool:
        if not (
            caller.AIClass
            and caller.AIClass.Name == "CharClass_UniqueCharger"
            and params.InstigatedBy
            and params.InstigatedBy.Class.Name == "WillowPlayerController"
        ):
            return True

        self.probe_behavior.ApplyBehaviorToContext(
            caller, (), None, params.InstigatedBy, None, ()
        )
        return True

    def objective(self, _c: UObject, _f: UFunction, params: FStruct) -> bool:
        if params.MissionObjective is self.kraggon_objective:
            self.hook("WillowGame.WillowAIPawn.TakeDamage", self.damaged)
            self.unhook(
                "WillowGame.WillowPlayerController.UpdateMissionObjective"
            )
        return True

    def entered_map(self) -> None:
        if get_missiontracker().IsMissionObjectiveComplete(
            self.kraggon_objective
        ):
            self.hook("WillowGame.WillowAIPawn.TakeDamage", self.damaged)
        else:
            self.hook(
                "WillowGame.WillowPlayerController.UpdateMissionObjective",
                self.objective,
            )

    def completed(self) -> None:
        self.unhook("WillowGame.WillowAIPawn.TakeDamage")


class SwordInStone(MapDropper):
    paths = ("StantonsLiver_P",)

    def entered_map(self) -> None:
        bpd = FindObject(
            "BehaviorProviderDefinition",
            "GD_Co_EasterEggs.Excalibastard.InteractiveObject_Excalibastard:BehaviorProviderDefinition_0",
        )
        condition = FindObject(
            "AttributeExpressionEvaluator",
            "GD_Co_EasterEggs.Excalibastard.InteractiveObject_Excalibastard:BehaviorProviderDefinition_0.Behavior_Conditional_22.AttributeExpressionEvaluator_0",
        )

        if not (bpd and condition):
            raise Exception(
                "Could not find objects for ART THOU BADASS ENOUGH"
            )

        previously_taken = bpd.BehaviorSequences[0].EventData2[0]
        previously_taken.OutputLinks.ArrayIndexAndLength = 327681

        condition.Expression.ConstantOperand2 = 0


class Swagman(Pawn):
    map_name: str

    def __init__(self, map_name: str) -> None:
        self.map_name = map_name.casefold()
        super().__init__("PawnBalance_ScavWastelandWalker")

    def should_inject(self, pawn: UObject) -> bool:
        return locations.map_name == self.map_name


class GrinderBuggy(MapDropper):
    paths = ("Moon_P",)

    def died(self, caller: UObject, _f: UFunction, params: FStruct) -> bool:
        if (
            caller.VehicleDef
            and caller.VehicleDef.Name == "Class_MoonBuggy_Grinder_AIOnly"
        ):
            spawn_loot(self.location.prepare_pools(), caller.Driver)
        return True

    def entered_map(self) -> None:
        self.hook("WillowGame.WillowVehicle.Died", self.died)


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
            raise Exception("Could not locate mission objectives for To Arms")

        self.objective = objective
        self.objective.ObjectiveCount = 5

        self.count_advancements = {1: adv1, 2: adv2, 3: adv3, 4: adv4, 5: adv5}

    def open(self, caller: UObject, _f: UFunction, params: FStruct) -> bool:
        caller.MailBoxStorage.ChestSlots = 1
        return True

    def deposit(self, caller: UObject, _f: UFunction, params: FStruct) -> bool:
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

    def entered_map(self) -> None:
        self.hook("WillowGame.MailBoxGFxMovie.extInitMainPanel", self.open)
        self.hook(
            "WillowGame.Behavior_MissionRemoteEvent.ApplyBehaviorToContext",
            self.deposit,
        )

    def disable(self) -> None:
        super().disable()
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

    def event(self, caller: UObject, _f: UFunction, _p: FStruct) -> bool:
        if (
            UObject.PathName(caller)
            != "Outlands_SideMissions2.TheWorld:PersistentLevel.Main_Sequence.Boomshakalaka.SeqAct_ApplyBehavior_4.Behavior_RemoteCustomEvent_0"
        ):
            return True

        mission = self.location.mission
        if not mission:
            raise Exception("No mission for Dunks Watson")

        pawn = get_pawn("CharClass_Superballa")
        if not pawn:
            raise Exception("Could not locate Dunks Watson")

        spawn_loot(
            self.location.prepare_pools(),
            mission.mission_definition.uobject,
            (-14540.578125, 106299.593750, 8647.15625),
            (0, 0, -4800),
        )
        return True

    def entered_map(self) -> None:
        self.hook(
            "WillowGame.Behavior_RemoteCustomEvent.ApplyBehaviorToContext",
            self.event,
        )


class SpaceSlam(MissionStatusDelegate, MapDropper):
    paths = ("Outlands_P2",)

    def apply(self) -> None:
        pawn = get_pawn("CharClass_Tog")
        if not pawn:
            raise Exception("Could not locate Tog for Space Slam")

        pawn.SetUsable(True, None, 0)

    def entered_map(self) -> None:
        self.apply()

    def completed(self) -> None:
        self.apply()


class BasketballHoop(MapDropper):
    paths = ("Outlands_P2",)

    def objective(self, _c: UObject, _f: UFunction, params: FStruct) -> bool:
        if (
            UObject.PathName(params.MissionObjective)
            != "GD_Co_SpaceSlam.M_SpaceSlam:SlamHoop"
        ):
            return True

        mission = self.location.mission
        if not mission:
            raise Exception("Could not location mission for Basketball Hoop")

        spawn_loot(
            self.location.prepare_pools(),
            mission.mission_definition.uobject,
            (-14541, 106290, -3204),
            radius=256,
        )
        return True

    def entered_map(self) -> None:
        self.hook(
            "WillowGame.WillowPlayerController.UpdateMissionObjective",
            self.objective,
        )


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
        mission = FindObject(
            "MissionDefinition", "GD_Co_Chapter05.M_Cork_WreckMain"
        )
        poop = FindObject(
            "PopulationOpportunityDen",
            "Wreck_Combat2.TheWorld:PersistentLevel.PopulationOpportunityDen_9",
        )
        seq = FindObject(
            "SeqEvent_PopulatedActor",
            "Wreck_Combat2.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_PopulatedActor_0",
        )
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
            invisible = FindObject(
                "SeqAct_ApplyBehavior",
                "Moon_SideMissions.TheWorld:PersistentLevel.Main_Sequence.NoSuchTHingAsAFreeLaunch.SeqAct_ApplyBehavior_0",
            )
            if not invisible:
                raise Exception(
                    "Could not locate Cosmo invisibility for Free Launch"
                )
            invisible.Behaviors = ()


class Cosmo(MapDropper):
    paths = ("Moon_p",)

    def fanfare(self, caller: UObject, _f: UFunction, params: FStruct) -> bool:
        mission = self.location.mission
        if not mission:
            raise Exception("No mission for Cosmo")

        if not (
            params.MissionDef is mission.mission_definition.uobject
            and params.FanFareType == 6  # EMFT_MissionReadyToTurnIn
        ):
            return True

        pawn = get_pawn("CharClass_Cosmo")
        if not pawn:
            raise Exception("Could not locate Cosmo for Cosmo")

        spawn_loot(
            self.location.prepare_pools(),
            mission.mission_definition.uobject,
            convert_struct(pawn.Location),
        )
        return True

    def entered_map(self) -> None:
        self.hook(
            "WillowGame.WillowPlayerController.ClientDoMissionStatusFanfare",
            self.fanfare,
        )


class NeilParsec(MapDropper):
    paths = ("Moon_P",)

    def entered_map(self) -> None:
        freelaunch = FindObject(
            "MissionDefinition",
            "GD_Cork_Rocketeering.M_Rocketeering",
        )
        if not (freelaunch):
            raise Exception("Could not locate mission for Neil Parsec")

        mission_status = get_missiontracker().GetMissionStatus(freelaunch)
        if mission_status == Mission.Status.Complete:
            den = FindObject(
                "PopulationOpportunityDen",
                "Moon_Combat.TheWorld:PersistentLevel.PopulationOpportunityDen_13",
            )
            neil = FindObject(
                "WillowAIPawn",
                "GD_Co_LuzzFightbeer.Character.Pawn_LuzzFightbeer",
            )
            if not (den and neil):
                raise Exception("Could not locate objects for Neil Parsec")

            neil.ActorSpawnCost = 0
            den.IsEnabled = True
            den.GameStageRegion = freelaunch.GameStageRegion


class Garbage(MapDropper):
    paths = ("Outlands_P2",)

    def event(self, caller: UObject, _f: UFunction, params: FStruct) -> bool:
        obj = params.ContextObject
        if not (
            "GarbageShoveled" in caller.EventName
            and obj.InteractiveObjectDefinition
            and obj.InteractiveObjectDefinition.Name == "IO_DirtPile"
        ):
            return True

        collision = 1  # COLLIDE_NoCollision
        obj.Behavior_ChangeCollision(collision)
        for comp in obj.AllComponents:
            if comp.Class.Name == "StaticMeshComponent":
                comp.Behavior_ChangeCollision(collision)

        mission = self.location.mission
        if not mission:
            raise Exception("No mission for Garbage")

        spawn_loot(
            self.location.prepare_pools(),
            mission.mission_definition.uobject,
            (obj.Location.X, obj.Location.Y, obj.Location.Z + 50),
        )
        return True

    def entered_map(self) -> None:
        self.hook(
            "Engine.Behavior_RemoteEvent.ApplyBehaviorToContext",
            self.event,
        )


class Abbot(MapDropper):
    paths = ("Moon_P",)

    def objective(
        self, caller: UObject, _f: UFunction, params: FStruct
    ) -> bool:
        if (
            UObject.PathName(params.MissionObjective)
            != "GD_Cork_AnotherPickle.M_Cork_AnotherPickle:SlapAbbotAgain"
        ):
            return True

        pawn = get_pawn("CharClass_Burner")
        if not pawn:
            raise Exception("Could not locate Abbot for Abbot")

        mission = self.location.mission
        if not mission:
            raise Exception("Could not location mission for Abbot")

        spawn_loot(
            self.location.prepare_pools(),
            mission.mission_definition.uobject,
            convert_struct(pawn.Location),
        )
        return True

    def entered_map(self) -> None:
        self.hook(
            "WillowGame.WillowPlayerController.UpdateMissionObjective",
            self.objective,
        )


class MoxxiBox(MapDropper):
    paths = ("Spaceport_P",)

    def entered_map(self) -> None:
        mission = FindObject(
            "MissionDefinition",
            "GD_Cork_HeliosFoothold_Plot.M_Cork_HeliosFoothold",
        )
        if not mission:
            raise Exception("Could not location mission for Moxxi's Toy Box")

        mission_status = get_missiontracker().GetMissionStatus(mission)
        if mission_status == Mission.Status.NotStarted:
            return

        loaded11 = FindObject(
            "SeqEvent_LevelLoaded",
            "Spaceport_M_Chp4.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_LevelLoaded_11",
        )
        loaded12 = FindObject(
            "SeqEvent_LevelLoaded",
            "Spaceport_M_Chp4.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_LevelLoaded_12",
        )
        spawn = FindObject(
            "WillowPopulationOpportunityPoint",
            "Spaceport_M_Chp4.TheWorld:PersistentLevel.WillowPopulationOpportunityPoint_0",
        )
        if not (loaded11 and loaded12 and spawn):
            raise Exception("Could not locate objects for Moxxi's Toy Box")

        loaded11.OutputLinks[0].Links[0].LinkedOp = None
        loaded12.OutputLinks[0].Links[0].LinkedOp = None
        spawn.IsEnabled = True


class SubLevel13(MapDropper):
    paths = ("Sublevel13_P",)

    def entered_map(self) -> None:
        keypad = FindObject(
            "WillowInteractiveObject",
            "Sublevel13_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_0",
        )
        if not keypad:
            raise Exception("Could not locate keypad for Sub-Level 13")

        handle = (keypad.ConsumerHandle.PID,)
        bpd = keypad.InteractiveObjectDefinition.BehaviorProviderDefinition
        kernel = get_behaviorkernel()

        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Usable", 1)
        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "Usable2", 1
        )


class ChefVoyage(MissionDropper, MapDropper):
    paths = ("Moon_P",)

    def entered_map(self) -> None:
        if self.location.current_status != Mission.Status.Complete:
            return

        loaded16 = FindObject(
            "SeqEvent_LevelLoaded",
            "Moon_SideMissions.TheWorld:PersistentLevel.Main_Sequence.VoyageOfCaptainChef.SeqEvent_LevelLoaded_16",
        )
        if not loaded16:
            raise Exception(
                "Could not locate loading for Voyage Of Captain Chef"
            )

        pawn = get_pawn("CharClass_CaptainChef")
        if not pawn:
            raise Exception("Could not locate Chef for Voyage Of Captain Chef")

        loaded16.OutputLinks[0].Links = ()

        handle = (pawn.ConsumerHandle.PID,)
        bpd = pawn.AIClass.AIDef.BehaviorProviderDefinition
        kernel = get_behaviorkernel()

        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "Invisible", 2
        )
        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "DisableUse", 2
        )

        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "AI", 1)
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Brain", 1)


class FreshAir(MapDropper):
    paths = ("RandDFacility_P",)

    def entered_map(self) -> None:
        den = FindObject(
            "PopulationOpportunityDen",
            "RandDFacility_Mission.TheWorld:PersistentLevel.PopulationOpportunityDen_5",
        )
        if not den:
            raise Exception("Could not locate den for Fresh Air")
        den.IsEnabled = True


class DrMinte(MapDropper):
    paths = ("RandDFacility_P",)

    def destroy(self, caller: UObject, _f: UFunction, _p: FStruct) -> bool:
        if not (
            caller.Class.Name == "WillowAIPawn"
            and caller.AIClass
            and caller.AIClass.Name == "CharClass_DrMinteNPC"
        ):
            return True

        mission = self.location.mission
        if not mission:
            raise Exception("Could not locate mission for Dr. Minte")

        window = FindObject(
            "WillowInteractiveObject",
            "RandDFacility_Mission.TheWorld:PersistentLevel.WillowInteractiveObject_29",
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

    def entered_map(self) -> None:
        self.hook("Engine.Actor.OnDestroy", self.destroy)


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
                (-19404, 39254, -2074),
            )


class SpaceHurps(MissionGiver):
    def apply(self) -> Union[UObject, None]:
        giver = super().apply()
        enable = FindObject(
            "BehaviorSequenceEnableByMission",
            "GD_Cork_TroubleWithSpaceH_Data.InteractiveObjects.IO_SpaceHurpTurnIn:BehaviorProviderDefinition_2.BehaviorSequenceEnableByMission_4",
        )
        if not (giver and giver.Outer and enable):
            raise Exception("Could not locate objects for Space Hurps")

        kernel = get_behaviorkernel()
        bpd = (
            giver.Outer.InteractiveObjectDefinition.BehaviorProviderDefinition
        )
        handle = (giver.Outer.ConsumerHandle.PID,)

        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "TroubleTurnIn", 1
        )
        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "TroubleECHO", 1
        )

        enable.MissionStatesToLinkTo.bReadyToTurnIn = True
        enable.MissionStatesToLinkTo.bComplete = True


class DontGetCocky(MissionObject):
    def apply(self) -> Union[UObject, None]:
        console = super().apply()
        enable = FindObject(
            "BehaviorSequenceEnableByMission",
            "GD_GenericSwitches.InteractiveObjects.IO_ComputerConsole_C:BehaviorProviderDefinition_1.BehaviorSequenceEnableByMission_8",
        )
        applybehavior7 = FindObject(
            "SeqAct_ApplyBehavior",
            "InnerHull_Mission.TheWorld:PersistentLevel.Main_Sequence.DontGetCocky.SeqAct_ApplyBehavior_7",
        )
        activatesequence8 = FindObject(
            "WillowSeqAct_ActivateInstancedBehaviorSequences",
            "InnerHull_Mission.TheWorld:PersistentLevel.Main_Sequence.DontGetCocky.WillowSeqAct_ActivateInstancedBehaviorSequences_8",
        )
        if not (console and enable and applybehavior7 and activatesequence8):
            raise Exception("Could not locate console for Dont Get Cocky")

        applybehavior7.VariableLinks[0].LinkedVariables = ()
        activatesequence8.VariableLinks[0].LinkedVariables = ()

        kernel = get_behaviorkernel()
        bpd = console.InteractiveObjectDefinition.BehaviorProviderDefinition
        handle = (console.ConsumerHandle.PID,)

        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "Offline", 2
        )
        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "Enabled", 1
        )
        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "DontGetCocky_Director_Failed", 1
        )

        enable.MissionStatesToLinkTo.bReadyToTurnIn = True
        enable.MissionStatesToLinkTo.bComplete = True


class TheseAreTheBots(MissionDropper, MapDropper):
    paths = ("Digsite_P",)

    def entered_map(self) -> None:
        loaded17 = FindObject(
            "SeqEvent_LevelLoaded",
            "Digsite_SideMissions.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_LevelLoaded_17",
        )
        loaded21 = FindObject(
            "SeqEvent_LevelLoaded",
            "Digsite_SideMissions.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_LevelLoaded_21",
        )
        if not (loaded17 and loaded21):
            raise Exception("Could not locate loading for These Are The Bots")

        loaded17.OutputLinks[0].Links = ()
        loaded21.OutputLinks[0].Links = ()

        pawn = get_pawn("CharClass_L3PO")
        if not pawn:
            raise Exception("Could not locate ICU-P for These Are The Bots")

        pawn.SetUsable(True, None, 0)


class ChefReturn(MissionDropper, MapDropper):
    paths = ("Digsite_P",)

    def entered_map(self) -> None:
        if self.location.current_status != Mission.Status.Complete:
            return

        loaded24 = FindObject(
            "SeqEvent_LevelLoaded",
            "Digsite_SideMissions.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_LevelLoaded_30",
        )
        if not loaded24:
            raise Exception(
                "Could not locate loading for Return Of Captain Chef"
            )

        pawn = get_pawn("CharClass_CaptainChefZone4")
        if not pawn:
            raise Exception("Could not locate Chef for Return Of Captain Chef")

        loaded24.OutputLinks[0].Links = ()

        handle = (pawn.ConsumerHandle.PID,)
        bpd = pawn.AIClass.AIDef.BehaviorProviderDefinition
        kernel = get_behaviorkernel()

        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "Invisible", 2
        )
        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "DisableUse", 2
        )
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "AI", 1)
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Brain", 1)


class InjuredSoldier(MapDropper):
    paths = ("Digsite_Rk5arena_P",)

    def died(self, caller: UObject, _f: UFunction, _p: FStruct) -> bool:
        if not (
            caller.AIClass
            and caller.AIClass.Name == "CharClass_NPCInjuredSoldier"
        ):
            return True

        mission = FindObject(
            "MissionDefinition", "GD_Co_Chapter11.M_DahlDigsite"
        )
        if not mission:
            raise Exception("Could not locate mission for Injured Soldier")

        spawn_loot(
            self.location.prepare_pools(),
            mission,
            (caller.Location.X, caller.Location.Y, caller.Location.Z),
        )
        return True

    def entered_map(self) -> None:
        den = FindObject(
            "PopulationOpportunityDen",
            "Digsite_Rk5arena_Audio.TheWorld:PersistentLevel.PopulationOpportunityDen_1",
        )
        if not den:
            raise Exception("Could not locate den for Injured Soldier")

        den.IsEnabled = True

        self.hook("WillowGame.WillowAIPawn.Died", self.died)


class Hanna(MapDropper):
    paths = ("Moon_P",)

    def died(self, caller: UObject, _f: UFunction, _p: FStruct) -> bool:
        if not (caller.AIClass and caller.AIClass.Name == "CharClass_Hanna"):
            return True

        mission = self.location.mission
        if not mission:
            raise Exception("Could not locate mission for Injured Soldier")

        spawn_loot(
            self.location.prepare_pools(),
            mission.mission_definition.uobject,
            (caller.Location.X, caller.Location.Y, caller.Location.Z),
        )
        return True

    def entered_map(self) -> None:
        self.hook("WillowGame.WillowAIPawn.Died", self.died)


class SentinelRaid(MapDropper):
    paths = ("InnerCore_P",)

    loot_behaviors = (
        "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_82",
        "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_83",
        "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_88",
        "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_89",
    )

    block_loot: bool = False

    def spawn_loot(self, caller: UObject, _f: UFunction, _p: FStruct) -> bool:
        if UObject.PathName(caller) in self.loot_behaviors:
            if self.block_loot:
                return False
            self.block_loot = True
        return True

    def detect_kill(self, caller: UObject, _f: UFunction, _p: FStruct) -> bool:
        if (
            UObject.PathName(caller)
            == "GD_FinalBossCorkBig.Character.AIDef_FBCBig:AIBehaviorProviderDefinition_0.Behavior_RemoteEvent_19"
        ):
            self.block_loot = False
        return True

    def entered_map(self) -> None:
        self.hook(
            "WillowGame.Behavior_SpawnItems.ApplyBehaviorToContext",
            self.spawn_loot,
        )
        self.hook(
            "Engine.Behavior_RemoteEvent.ApplyBehaviorToContext",
            self.detect_kill,
        )


class MasterPoacher(MapDropper):
    paths = ("Digsite_P",)

    def died(self, caller: UObject, _f: UFunction, _p: FStruct) -> bool:
        if (
            UObject.PathName(caller.AIClass)
            != "GD_Co_NPCs_GuardianHunter.Character.CharClass_ScavBandit"
        ):
            return True

        mission = self.location.mission
        if not mission:
            raise Exception("Could not locate mission for Master Poacher")

        spawn_loot(
            self.location.prepare_pools(),
            mission.mission_definition.uobject,
            (caller.Location.X, caller.Location.Y, caller.Location.Z),
        )
        return True

    def entered_map(self) -> None:
        self.hook("WillowGame.WillowAIPawn.Died", self.died)


class PopupAd(MapDropper):
    paths = ("Ma_Nexus_P", "Ma_Motherboard_P")

    def spawn_loot(self, caller: UObject, _f: UFunction, _p: FStruct) -> bool:
        if (
            UObject.PathName(caller)
            == "GD_Ma_AdPopup.BE_Shared_AdPopup:Behavior_SpawnLootAtPoints_3"
        ):
            caller.ItemPools = self.location.prepare_pools()
            caller.SpawnVelocity = (64, 64, 850)
        return True

    def entered_map(self) -> None:
        self.hook(
            "WillowGame.Behavior_SpawnLoot.ApplyBehaviorToContext",
            self.spawn_loot,
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
        chest_bpd = FindObject(
            "BehaviorProviderDefinition",
            "GD_Ma_Side_SpywareData.InteractiveObjects.InteractiveObj_SpywareChest:BehaviorProviderDefinition_0",
        )
        if not chest_bpd:
            raise Exception(
                "Could not locate chest for Spyware Who Came in from the Cold"
            )

        behavior_data = chest_bpd.BehaviorSequences[1].BehaviorData2
        set_flag = behavior_data[1].Behavior

        behavior_data[1].Behavior = behavior_data[4].Behavior
        behavior_data[1].LinkedVariables.ArrayIndexAndLength = 0

        behavior_data[4].Behavior = set_flag
        behavior_data[4].LinkedVariables.ArrayIndexAndLength = 1

        if self.location.current_status != Mission.Status.Complete:
            return

        pawn = get_pawn("CharacterClass_Ma_HoneyPot")
        if not pawn:
            raise Exception(
                "Could not locate bug for Spyware Who Came in from the Cold"
            )

        handle = (pawn.ConsumerHandle.PID,)
        bpd = pawn.AIClass.AIDef.BehaviorProviderDefinition
        kernel = get_behaviorkernel()

        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Brain", 1)


class RoseTinting(MissionDropper, MapDropper):
    paths = ("Ma_LeftCluster_P",)

    def entered_map(self) -> None:
        completed_event = FindObject(
            "WillowSeqEvent_MissionRemoteEvent",
            "Ma_LeftCluster_SideMissions.TheWorld:PersistentLevel.Main_Sequence.WillowSeqEvent_MissionRemoteEvent_33",
        )
        sequence_conditions = FindObject(
            "BehaviorSequenceEnableByMultipleConditions",
            "GD_Ma_Side_MINACData.InteractiveObjects.IO_MinacMissionObject:BehaviorProviderDefinition_1.BehaviorSequenceEnableByMultipleConditions_0",
        )
        minac_eye = FindObject(
            "WillowInteractiveObject",
            "Ma_LeftCluster_SideMissions.TheWorld:PersistentLevel.WillowInteractiveObject_0",
        )
        if not (completed_event and sequence_conditions and minac_eye):
            raise Exception("Could not locate objects for Rose Tinting")

        completed_event.OutputLinks[0].Links = ()

        sequence_conditions.EnableConditions = ()

        kernel = get_behaviorkernel()
        handle = (minac_eye.ConsumerHandle.PID,)
        bpd = minac_eye.InteractiveObjectDefinition.BehaviorProviderDefinition

        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "MissionComplete", 2
        )
        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "MissionAvailable", 1
        )


class DataMining(MissionStatusDelegate, MapDropper):
    paths = ("Ma_LeftCluster_P",)

    def entered_map(self) -> None:
        completed_event = FindObject(
            "WillowSeqEvent_MissionRemoteEvent",
            "Ma_LeftCluster_SideMissions.TheWorld:PersistentLevel.Main_Sequence.WillowSeqEvent_MissionRemoteEvent_37",
        )
        kill_event = FindObject(
            "WillowSeqEvent_MissionRemoteEvent",
            "Ma_LeftCluster_SideMissions.TheWorld:PersistentLevel.Main_Sequence.WillowSeqEvent_MissionRemoteEvent_31",
        )
        if not (completed_event and kill_event):
            raise Exception("Could not locate objects for Data Mining")

        completed_event.OutputLinks[0].Links = ()
        kill_event.OutputLinks[0].Links = ()

    def completed(self) -> None:
        shame = get_pawn("CharClass_Ma_MiniTrojan_Shame")
        if not shame:
            return

        bpd = shame.AIClass.AIDef.BehaviorProviderDefinition
        handle = (shame.ConsumerHandle.PID,)
        kernel = get_behaviorkernel()

        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "MissionComplete", 2
        )
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "TurnIn", 1)


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

    def spawn_dignity(self) -> None:
        den = FindObject(
            "PopulationOpportunityDen",
            "Ma_Motherboard_Side.TheWorld:PersistentLevel.PopulationOpportunityDen_0",
        )
        loaded2 = FindObject(
            "SeqEvent_LevelLoaded",
            "Ma_Motherboard_Side.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_LevelLoaded_2",
        )
        pop_eval = FindObject(
            "OzMissionExpressionEvaluator",
            "GD_Ma_DignityTrap.Population.BD_Dignity:OzMissionExpressionEvaluator_0",
        )
        if not (den and loaded2 and pop_eval):
            raise Exception("Could not locate den for Dignity")

        loaded2.OutputLinks[0].Links = ()
        pop_eval.ObjectiveStatesToLinkTo.bComplete = True
        den.Aspect = None
        den.IsEnabled = True
        den.RespawnKilledActors(1)

    def hide_monocle(self) -> None:
        for obj in FindAll("WillowInteractiveObject"):
            obj_def = obj.InteractiveObjectDefinition
            if obj_def and obj_def.Name == "IO_Ma_ShredOfDignity":
                break
        else:
            raise Exception("Could not locate monocle for Dignity")

        get_behaviorkernel().ChangeBehaviorSequenceActivationStatus(
            (obj.ConsumerHandle.PID,),
            obj.InteractiveObjectDefinition.BehaviorProviderDefinition,
            "Invisible",
            1,
        )
        obj.ChangeInstanceDataSwitch("PooPile", 0)

    def completed(self) -> None:
        self.spawn_dignity()
        self.hide_monocle()

    def entered_map(self) -> None:
        if self.location.current_status == Mission.Status.Complete:
            self.hide_monocle()
            self.spawn_dignity()

    def exited_map(self) -> None:
        self.den = None
        self.monocle = None


class EgoTrap(MissionStatusDelegate, MapDropper):
    paths = ("Ma_Nexus_P",)

    def apply(self) -> None:
        pawn = get_pawn("CharacterClass_Ma_EgoTrap")
        if not pawn:
            raise Exception("Could not locate 3G0-TP")

        get_behaviorkernel().ChangeBehaviorSequenceActivationStatus(
            (pawn.ConsumerHandle.PID,),
            pawn.AIClass.AIDef.BehaviorProviderDefinition,
            "Brain",
            1,
        )

    def entered_map(self) -> None:
        if self.location.current_status == Mission.Status.Complete:
            self.apply()

    def completed(self) -> None:
        self.apply()


class StopTheMusic(MissionDropper, MapDropper):
    paths = ("Ma_Nexus_P",)

    def entered_map(self) -> None:
        loaded2 = FindObject(
            "SeqEvent_LevelLoaded",
            "Ma_Nexus_Side.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_LevelLoaded_2",
        )
        if not loaded2:
            raise Exception("Could not locate loading for Stop The Music")
        loaded2.OutputLinks[0].Links = ()


class ByteClub(MissionDropper, MapDropper):
    paths = ("Ma_RightCluster_P",)

    def entered_map(self) -> None:
        den = FindObject(
            "PopulationOpportunityDen",
            "Ma_RightCluster_SideMission.TheWorld:PersistentLevel.PopulationOpportunityDen_7",
        )
        if not den:
            raise Exception("Could not locate den for Byte Club")

        turnedin_enable = FindObject(
            "BehaviorSequenceEnableByMission",
            "GD_Ma_BotPit.Character.AIDef_Ma_BotPit:AIBehaviorProviderDefinition_0.BehaviorSequenceEnableByMission_2",
        )
        brain_enable = FindObject(
            "BehaviorSequenceEnableByMission",
            "GD_Ma_BotPit.Character.AIDef_Ma_BotPit:AIBehaviorProviderDefinition_0.BehaviorSequenceEnableByMission_0",
        )
        if not (turnedin_enable and brain_enable):
            raise Exception("Could not locate objects for Byte Club")

        den.IsEnabled = True

        turnedin_enable.MissionStatesToLinkTo.bComplete = False
        brain_enable.MissionStatesToLinkTo.bComplete = True


class SupaEgoTrap(MissionDropper, MapDropper):
    paths = ("Ma_Nexus_P",)

    def entered_map(self) -> None:
        den = FindObject(
            "PopulationOpportunityDen",
            "Ma_Nexus_Side.TheWorld:PersistentLevel.PopulationOpportunityDen_1",
        )
        mission_enable = FindObject(
            "BehaviorSequenceEnableByMission",
            "GD_Ma_SuperEgoTrap.Character.AIDef_Ma_SuperEgoTrap:AIBehaviorProviderDefinition_0.BehaviorSequenceEnableByMission_0",
        )
        if not (den and mission_enable):
            raise Exception("Could not locate objects for 5UP4-3G0-TP")

        den.IsEnabled = True
        mission_enable.MissionStatesToLinkTo.bComplete = True


class JackBobble(MapDropper):
    paths = ("Ma_Subconscious_P",)

    def emitter(self, caller: UObject, _f: UFunction, params: FStruct) -> bool:
        if (
            UObject.PathName(caller)
            != "Ma_Subconscious_Game.TheWorld:PersistentLevel.Emitter_2"
        ):
            return True

        missiondef = FindObject(
            "MissionDefinition", "GD_Ma_Chapter05.M_Ma_Chapter05"
        )
        if not missiondef:
            raise Exception(f"No mission for {self.location.name}")

        spawn_loot(
            self.location.prepare_pools(),
            missiondef,
            (-54300, -6464, 5028),
            (-212, 1037, 0),
        )
        return True

    def entered_map(self) -> None:
        self.hook("Engine.Actor.OnToggleHidden", self.emitter)


class DeadlierGame(MissionStatusDelegate, MapDropper):
    paths = ("Ma_Subconscious_P",)

    def apply(self) -> None:
        pawn = FindObject(
            "WillowAIPawn",
            "Ma_Subconscious_SideMissions.TheWorld:PersistentLevel.WillowAIPawn_0",
        )
        icon = FindObject(
            "InteractionIconDefinition",
            "GD_InteractionIcons.Default.Icon_DefaultTalk",
        )
        if not (pawn and icon):
            raise Exception("Could not locate objects for Deadlier Game")

        pawn.SetInteractionIcon(icon, 0)
        pawn.SetUsable(True, None, 0)

        bpd = pawn.AIClass.AIDef.BehaviorProviderDefinition
        kernel = get_behaviorkernel()
        handle = (pawn.ConsumerHandle.PID,)

        kernel.ChangeBehaviorSequenceActivationStatus(
            handle, bpd, "MissionComplete", 2
        )
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Brain", 1)

    def entered_map(self) -> None:
        if self.location.current_status == Mission.Status.Complete:
            self.apply()

    def completed(self) -> None:
        self.apply()


class SumFears(MapDropper):
    paths = ("Ma_Subconscious_P",)

    def entered_map(self) -> None:
        turnin_enable = FindObject(
            "BehaviorSequenceEnableByMission",
            "GD_Ma_MetaTrap_SomeFears.Character.AIDef_Ma_MetaTrap_SomeFears:AIBehaviorProviderDefinition_0.BehaviorSequenceEnableByMission_0",
        )
        if not turnin_enable:
            raise Exception("Could not locate objects for Sum Of Some Fears")
        turnin_enable.MissionStatesToLinkTo.bComplete = True


def _mutate_rarities(original_rarities: Sequence[int]) -> List[int]:
    machine_attr = FindObject(
        "DesignerAttributeDefinition",
        "GD_Ma_Mutator.Attributes.Att_MutatorMachineType",
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

    multiplier = {
        2: 1.33,
        3: 1.67,
        4: 2.0,
        5: 2.33,
        6: 2.67,
        7: 3.0,
        8: 3.5,
        9: 4.0,
    }.get(level, 1.0)

    total_rarity = multiplier * sum(original_rarities)

    rarities = [100] * int(total_rarity // 100)
    if total_rarity % 100:
        rarities.append(int(total_rarity % 100))
    return rarities


class MutatorMissionDefinition(MissionDefinition):
    def inject(self, mission_data: FStruct) -> None:
        original_rarities = self.location.rarities
        Log(original_rarities)
        rarities = _mutate_rarities(original_rarities)
        if rarities[-1] < 50:
            rarities.pop()
        else:
            rarities[-1] = 100

        self.location.rarities = rarities
        super().inject(mission_data)
        self.location.rarities = original_rarities


class MutatorChest(Attachment):
    def inject(self, obj: UObject) -> None:
        Log("Injecting MutatorChest")
        original_rarities = self.location.rarities
        rarities = _mutate_rarities(original_rarities)

        self.location.rarities = rarities
        super().inject(obj)
        self.location.rarities = original_rarities


class MutatorPawn(Pawn):
    def inject(self, pools: List[Any]) -> None:
        original_rarities = self.location.rarities
        rarities = _mutate_rarities(original_rarities)

        self.location.rarities = rarities
        super().inject(pools)
        self.location.rarities = original_rarities


class HolodomeMission(MissionDropper, MapDropper):
    paths = ("Eridian_slaughter_P",)

    compare_path: str
    objective_path: str
    didntdo_behavior_path: str
    did_behavior_path: str

    objective: UObject

    didntdo_bevavior: UObject
    did_behavior: UObject

    didntdo_objective: UObject
    did_objective: UObject

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

    def enable(self) -> None:
        super().enable()
        objective = FindObject(
            "MissionObjectiveDefinition", self.objective_path
        )
        didntdo_bevavior = FindObject(
            "Behavior_UpdateMissionObjective", self.didntdo_behavior_path
        )
        did_behavior = FindObject(
            "Behavior_UpdateMissionObjective", self.did_behavior_path
        )
        if not (objective and didntdo_bevavior and did_behavior):
            raise Exception("Could not locate objectives for Holodome")

        self.objective = objective

        self.didntdo_bevavior = didntdo_bevavior
        self.did_behavior = did_behavior

        self.didntdo_objective = didntdo_bevavior.MissionObjective
        self.did_objective = did_behavior.MissionObjective

    def disable(self) -> None:
        super().disable()

        self.didntdo_bevavior.MissionObjective = self.didntdo_objective
        self.did_behavior.MissionObjective = self.did_objective

    def compare(self, caller: UObject, _f: UFunction, _p: FStruct) -> bool:
        if UObject.PathName(caller) != self.compare_path:
            return True

        objective_complete = get_missiontracker().IsMissionObjectiveComplete(
            self.objective
        )

        if objective_complete:
            self.didntdo_bevavior.MissionObjective = self.did_objective
            self.did_behavior.MissionObjective = self.did_objective
        else:
            self.didntdo_bevavior.MissionObjective = self.didntdo_objective
            self.did_behavior.MissionObjective = self.didntdo_objective

        return True

    def entered_map(self) -> None:
        self.hook(
            "GearboxFramework.Behavior_CompareBool.ApplyBehaviorToContext",
            self.compare,
        )


class HolodomeScientists(MapDropper):
    paths = ("Eridian_slaughter_P",)

    def button(self, caller: UObject, _f: UFunction, params: FStruct) -> bool:
        if (
            UObject.PathName(caller)
            != "GD_EridianSlaughterData.InteractiveObjects.GenericButtonDigi:BehaviorProviderDefinition_0.Behavior_ChangeInstanceDataSwitch_69"
        ):
            return True

        objective = FindObject(
            "MissionObjectiveDefinition",
            "GD_EridianSlaughter.MissionDef.M_EridianSlaughter03:OBJ_35_FreeSci",
        )
        if not (objective and objective.Outer):
            raise Exception("Could not locate objective for Scientists")

        if get_missiontracker().IsMissionObjectiveComplete(objective):
            original_rarities = self.location.rarities
            self.location.rarities = tuple(original_rarities) * 4
            spawn_loot(
                tuple(self.location.prepare_pools()),
                objective.Outer,
                (14958, -3456, 674),
                (-468, -544, 0),
                64,
            )
            self.location.rarities = original_rarities
        return True

    def entered_map(self) -> None:
        button_bpd = FindObject(
            "BehaviorProviderDefinition",
            "GD_EridianSlaughterData.InteractiveObjects.GenericButtonDigi:BehaviorProviderDefinition_0",
        )
        if not button_bpd:
            raise Exception("Could not locate button for Scientists")

        off_sequence = button_bpd.BehaviorSequences[5]
        off_sequence.ConsolidatedOutputLinkData[1].ActivateDelay = 1

        self.hook(
            "WillowGame.Behavior_ChangeInstanceDataSwitch.ApplyBehaviorToContext",
            self.button,
        )


# fmt: off

Locations: Sequence[locations.Location] = (
    Other("Playthrough Delegate", PlaythroughDelegate(), tags=Tag.Excluded),
    Other("Loyalty Rewards", LoyaltyRewards(), tags=Tag.Excluded),
    Other("Holiday Events", HolidayEvents(), tags=Tag.Excluded),
    Other("World Uniques", WorldUniques(), tags=Tag.Excluded),

    Mission("Lost Legion Invasion", MissionTurnIn("GD_Co_Chapter01.M_CH01b_MoonShot"), tags=Tag.Excluded),
    Mission("Tales from Elpis", MissionDefinition("GD_Co_TalesFromElpis.M_TalesFromElpis")),
    Enemy("Son of Flamey", Pawn("PawnBalance_SonFlamey")),
    Enemy("Grandson of Flamey", Pawn("PawnBalance_GrandsonFlamey")),
    Enemy("Badass Kraggon", Pawn("PawnBalance_ElementalSpitterBadass"), tags=Tag.VeryRareEnemy),
    Enemy("Phonic Kraggon", Pawn("PawnBalance_ElementalPhonic"), tags=Tag.RareEnemy),
    Mission("Land Among the Stars", MissionDefinition("GD_Co_Motivation.M_Motivation"), tags=Tag.Freebie),
    Mission("Follow Your Heart", MissionDefinition("GD_Co_FollowYourHeart.M_FollowYourHeart"), tags=Tag.LongMission),
    Enemy("Delivery Confirmationist", Pawn("PawnBalance_ScavAccepterDude"), mission="Follow Your Heart"),
    Enemy("Pumpkin Scav", Pawn(
        "PawnBalance_ScavengerBandit_Jetpack_Pumpkin",
        "PawnBalance_ScavengerBandit_Pumpkin",
        "PawnBalance_ScavengerPsycho_Pumpkin",
        "PawnBalance_ScavMidget_Pumpkin",
    ), tags=Tag.Holiday|Tag.MobFarm),
    Other("Bloody Harvest Barrel", PumpkinBarrel(), tags=Tag.Holiday, rarities=(3,)),
    Other("Celebration Barrel", Behavior("GD_Explosives.Barrels.ExplodingBarrel_Shift_Celebrate:BehaviorProviderDefinition_0.Behavior_SpawnItems_81"), tags=Tag.Holiday, rarities=(33,)),
    Other("Mercenary Day Barrel", Behavior("GD_Explosives.Barrels.ExplodingBarrel_Shift_Mercenary:BehaviorProviderDefinition_0.Behavior_SpawnItems_98"), tags=Tag.Holiday, rarities=(33,)),
    Enemy("Deadlift", Pawn("PawnBalance_SpacemanDeadlift"), tags=Tag.SlowEnemy),
    Enemy("Undeadlift", Pawn("PawnBalance_SpacemanDeadlift_Pumpkin"), tags=Tag.SlowEnemy|Tag.Holiday),
    Mission("Last Requests", MissionDefinition("GD_Co_LastRequests.M_LastRequests"),
        LastRequests(),
    tags=Tag.LongMission),
    Enemy("Tom Thorson", FriskedCorpse("Deadsurface_P", "Deadsurface_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_5"), mission="Last Requests"),
    Enemy("Squat", Pawn("PawnBalance_Squat"), mission="Last Requests"),
    Enemy("Nel (Called a Dick)", Dick(), mission="Last Requests"),
    Enemy("Nel", Pawn("PawnBalance_Nel"), tags=Tag.SlowEnemy),
    Mission("Nova? No Problem!", MissionDefinition("GD_Co_NovaNoProblem.M_NovaNoProblem")),
    Other("Janey's Chest", Attachment("BD_DahlShockChest", 0), mission="Nova? No Problem!"),
    Other("Janey's Safe", Attachment("BD_ElectronicObjectThree", 0), mission="Nova? No Problem!"),
    Mission("Torgue-o! Torgue-o! (Turn in Janey)", MissionDefinition("GD_Co_ToroToro.M_ToroToro"),
        TorgueO()
    ),
    Mission("Torgue-o! Torgue-o! (Turn in Lava)", MissionTurnInAlt("GD_Co_ToroToro.M_ToroToro")),
    Enemy("Antagonized Kraggon", Pawn("PawnBalance_UniqueCharger"), mission="Torgue-o! Torgue-o! (Turn in Janey)", rarities=(5,)),
    Other("Isaiah's Loot", Attachment("ObjectGrade_StrongBox_Isaiah"), tags=Tag.Freebie),
    Enemy("Oscar", Pawn("PawnBalance_ScavSuicidePsycho_Oscar")),
    Mission("Wherefore Art Thou?", MissionDefinition("GD_Co_WhereforeArtThou.M_Co_WhereforeArtThou"), tags=Tag.LongMission|Tag.VehicleMission),
    Enemy("Maureen", Pawn("PawnBalance_MaureenRider"), mission="Wherefore Art Thou?"),
    Mission("All the Little Creatures", MissionDefinition("gd_cork_allthelittlecreatures.M_AllTheLittleCreatures")),
    Enemy("Not-So-Cute Tork", Pawn("PawnBalance_NotCuteTork"), mission="All the Little Creatures", rarities=(33,)),
    Enemy("Even-More-Disgusting Tork", Pawn("PawnBalance_NotCuteBadassTork")),
    Other("ART THOU BADASS ENOUGH?", Behavior("GD_Co_EasterEggs.Excalibastard.InteractiveObject_Excalibastard:BehaviorProviderDefinition_0.Behavior_SpawnItems_44"),
        SwordInStone(),
    tags=Tag.Miscellaneous),
    Enemy("Swagman (Stanton's Liver)",
        Swagman("StantonsLiver_P")
    ),
    Other("Obelisk Chest", PositionalChest("ObjectGrade_TreasureChest", "StantonsLiver_P", 15677, 24953, -14827)),
    Mission("Recruitment Drive", MissionDefinition("GD_Cork_Resistors.M_Resistors"), tags=Tag.VehicleMission),
    Enemy("Magma Rivers", Pawn("PawnBalance_LittleDarksiderBadassBandit")),
    Enemy("Wally Wrong", Pawn("PawnBalance_DarksiderBadassBandit")),
    Enemy("Fair Dinkum", Pawn("PawnBalance_DarksiderBadassPsycho")),
    Other("Triton Flats Hidden Treasure", PositionalChest("ObjectGrade_DahlEpic", "Moon_P", -36437, -2434, -1413)),
    Mission("The Empty Billabong", MissionDefinition("GD_Co_EmptyBillabong.M_EmptyBillaBong")),
    Enemy("Jolly Swagman", FriskedCorpse("ComFacility_P", "ComFacility_SideMissions.TheWorld:PersistentLevel.WillowInteractiveObject_4"), mission="The Empty Billabong"),
    Enemy("Red", Pawn("PawnBalance_Ned"), tags=Tag.SlowEnemy),
    Enemy("Belly", Pawn("PawnBalance_Kelly"), tags=Tag.SlowEnemy),
    Mission("Grinders", MissionDefinition("GD_Cork_Grinding.M_Cork_Grinding"), tags=Tag.VeryLongMission),
    Enemy("Grinder Buggy", GrinderBuggy(), mission="Grinders"),
    Enemy("Rooster Booster", Pawn("PawnBalance_RoosterBooster"), tags=Tag.SlowEnemy),
    Mission("To Arms!", ToArms(), MissionDefinition("GD_Co_ToArms.M_Co_ToArms"), tags=Tag.VeryLongMission),
    Enemy("PLA Member Tim Pot", Pawn("PawnBalance_TimPot"), mission="To Arms!"),
    Enemy("PLA Member Tom Pot", Pawn("PawnBalance_TomPot"), mission="To Arms!"),
    Enemy("PLA Member Tum Pot", Pawn("PawnBalance_TumPot"), mission="To Arms!"),
    Mission("Bunch of Ice Holes (Turn in Nurse Nina)", MissionDefinition("GD_Co_IceHoles.M_Co_IceHoles")),
    Mission("Bunch of Ice Holes (Turn in B4R-BOT)", MissionTurnInAlt("GD_Co_IceHoles.M_Co_IceHoles")),
    Enemy("Giant Shuggurath of Ice", Pawn("PawnBalance_GiantCryoHive")),
    Mission("Pop Racing", MissionDefinition("GD_Co_PopRacing.M_Co_PopRacing"),
        PopRacing(),
    tags=Tag.VehicleMission),
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
    Mission("Zapped 3.0", MissionDefinition("GD_Co_Zapped.M_Co_Zapped3"), tags=Tag.Freebie),
    Enemy("Malfunctioning CL4P-TP", Pawn("BD_MalfunctioningClaptrap"), mission="Zapped 3.0", rarities=(15,)),
    Enemy("Swagman (Outlands Canyon)",
        Swagman("Outlands_P2")
    ),
    Other("Perfect Timing Chest", PositionalChest("ObjectGrade_TreasureChest", "Outlands_P2", -28896, 56862, -828)),
    Mission("Boomshakalaka", MissionDefinition("GD_Co_Boomshakalaka.M_Boomshakalaka"),
        Boomshakalaka(),
    ),
    Enemy("Dunks Watson",
        DunksWatson(),
    mission="Boomshakalaka"),
    Mission("Space Slam", MissionDefinition("GD_Co_SpaceSlam.M_SpaceSlam"),
        SpaceSlam(),
    tags=Tag.Freebie),
    Other("Basketball Hoop",
        BasketballHoop(),
    mission="Space Slam", rarities=(7,) * 15),
    Enemy("Tork Dredger", Pawn("PawnBalance_TorkDredger"), tags=Tag.MobFarm, rarities=(33,)),
    Other("King of the Hill", PositionalChest("ObjectGrade_TreasureChest", "Outlands_P2", -12476, 91186, 2471)),
    Enemy("Merry Scav", Pawn("PawnBalance_ScavengerBandit_Jetpack_MercDay"), tags=Tag.Holiday|Tag.RareEnemy),
    Enemy("Poop Deck", Pawn("PawnBalance_PoopDeck"),
        PoopDeck(),
    tags=Tag.SlowEnemy),
    Enemy("Bosun", Pawn("PawnBalance_Bosun")),
    Mission("The Secret Chamber", MissionDefinition("GD_Co_SecretChamber.M_SecretChamber"),
        MissionPickup("Wreck_SideMissions.TheWorld:PersistentLevel.WillowMissionPickupSpawner_0", "Wreck_P"),
    tags=Tag.LongMission),
    Other("Zarpedon's Stash", Attachment("Balance_Chest_ZarpedonsStash"), mission="The Secret Chamber"),
    Mission("Wiping the Slate", MissionDefinition("GD_Co_WipingSlate.M_WipingSlate"), tags=Tag.Freebie),
    Mission("No Such Thing as a Free Launch", MissionDefinition("GD_Cork_Rocketeering.M_Rocketeering"),
        FreeLaunch(),
    tags=Tag.LongMission),
    Enemy("Tony Slows", Pawn("PawnBalance_TonySlows"), mission="No Such Thing as a Free Launch"),
    Enemy("Cosmo Wishbone",
        Cosmo(),
    mission="No Such Thing as a Free Launch"),
    Enemy("Neil Parsec", Pawn("Balance_Co_LuzzFightbeer"),
        NeilParsec(),
    ),
    Mission("Nothing is Never an Option", MissionDefinition("GD_Co_YouAskHowHigh.M_Co_YouAskHowHigh"), tags=Tag.LongMission),
    Enemy("Boomer", Pawn("PawnBalance_BoomerJetFighter"), tags=Tag.SlowEnemy, rarities=(100,)),
    Mission("Treasures of ECHO Madre", MissionDefinition("GD_Co_TreasuresofECHO.M_Co_TreasuresofECHO"), tags=Tag.LongMission),
    Other("Research Facility Garbage", Garbage(), mission="Treasures of ECHO Madre", rarities=(50,)),
    Enemy("Rabid Adams", Pawn("PawnBalance_RabidAdams")),
    Mission("Another Pickle", MissionDefinition("GD_Cork_AnotherPickle.M_Cork_AnotherPickle"), tags=Tag.LongMission),
    Enemy("Orphan Rathyd", Pawn("PawnBalance_OrphanRodunk"), mission="Another Pickle", rarities=(20,)),
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
    Other("Moxxi's Toy Box", Attachment("ObjectGrade_MoxxiDahlEpic"),
        MoxxiBox(),
    tags=Tag.Freebie),
    Mission("Sub-Level 13", MissionDefinition("GD_Co_SubLevel13.M_Co_SubLevel13Part1")),
    Enemy("Ghostly Apparition", Pawn("PawnBalance_SubLevel13Ghost"), mission="Sub-Level 13"),
    Mission("Sub-Level 13: Part 2 (Turn in Pickle)", MissionDefinition("GD_Co_SubLevel13.M_Co_SubLevel13Part2"),
        SubLevel13(),
    ),
    Mission("Sub-Level 13: Part 2 (Turn in Schmidt)", MissionTurnInAlt("GD_Co_SubLevel13.M_Co_SubLevel13Part2")),
    Mission("The Voyage of Captain Chef", MissionDefinition("GD_Co_VoyageOfCaptainChef.M_VoyageOfCaptainChef"),
        ChefVoyage(),
    ),
    Other("Playing Chicken Chest", PositionalChest("ObjectGrade_HyperionChest", "centralterminal_p", 16985, 2962, 2009)),
    Enemy("Merry Lost Legion", Pawn(
        "PawnBalance_DahlScout_MercDay",
        "PawnBalance_DahlFlameMarine_MercDay",
        "PawnBalance_DahlMarine_MercDay",
        "PawnBalance_DahlMedic_MercDay",
        "PawnBalance_DahlSergeant_MercDay",
        "PawnBalance_BadassDahlMarine_MercDay",
    ), tags=Tag.Holiday|Tag.MobFarm),
    Enemy("X-STLK-23-3", Pawn("PawnBalance_Stalker_RnD")),
    Enemy("Corporal Bob", Pawn("PawnBalance_DahlMarine_CentralTerm"), tags=Tag.VeryRareEnemy),
    # TODO buff bahb
    Mission("Boarding Party", MissionDefinition("GD_Co_Boarding_Party.M_BoardingParty")),
    Mission("Voice Over", MissionDefinition("GD_Co_VoiceOver.M_VoiceOver")),
    Mission("Hot Head", MissionDefinition("GD_Co_Hot_Head.M_Hot_Head")),
    Enemy("Dean", Pawn("PawnBalance_Dean"), mission="Hot Head"),
    Mission("Cleanliness Uprising", MissionDefinition("GD_Co_Cleanliness_Uprising.M_Cleanliness_Uprising")),
    Mission("An Urgent Message", MissionDefinition("GD_Co_Detention.M_Detention")),
    Mission("Handsome AI", MissionDefinition("GD_Co_PushButtonMission.M_PushButtonMission")),
    Mission("Paint Job", MissionDefinition("GD_Co_Paint_Job.M_Paint_Job")),
    Mission("Kill Meg", MissionDefinition("GD_Co_Kill_Meg.M_Kill_Meg")),
    Enemy("Meg", Pawn("PawnBalance_Meg")),
    Other("Hyperion Gun Shop",
        PositionalChest("ObjectGrade_HypWeaponChest", "centralterminal_p", 22160, 3261, 611),
        PositionalChest("ObjectGrade_HypWeaponChest", "centralterminal_p", 22276, 4533, 613),
    rarities=(7,7)),
    Mission("Infinite Loop (Restrain CLAP-9000)", MissionDefinition("GD_Co_Side_Loop.M_InfiniteLoop")),
    Mission("Infinite Loop (Restrain DAN-TRP)", MissionTurnInAlt("GD_Co_Side_Loop.M_InfiniteLoop")),
    Mission("It Ain't Rocket Surgery", MissionDefinition("GD_Co_Side_RocketSurgery.M_RocketSurgery"), tags=Tag.LongMission),
    Other("Dr. Spara's Stash", Attachment("ObjectGrade_HypWeaponChest_Ice", 0, 1), mission="It Ain't Rocket Surgery"),
    Mission("Fresh Air", MissionDefinition("GD_Co_Side_FreshAir.M_FreshAir"),
        FreshAir(),
    ),
    Enemy("Dr. Minte",
        DrMinte(),
    mission="Fresh Air"),
    Mission("Lab 19", MissionDefinition("GD_Co_Side_Lab19.M_Lab19"),
        MissionPickup("RandDFacility_P.TheWorld:PersistentLevel.WillowMissionPickupSpawner_1", "RandDFacility_P"),
    ),
    Enemy("Tiny Destroyer", Pawn("PawnBalance_MiniDestroyer")),
    Enemy("Benjamin Blue", Attachment("BD_Ben"), rarities=(100,)),
    Mission("Quarantine: Back On Schedule", MissionDefinition("GD_Cork_BackOnSchedule.M_BackOnSchedule")),
    Mission("Quarantine: Infestation", MissionDefinition("GD_Cork_Quarantine.M_Quarantine")),
    Mission("In Perfect Hibernation", MissionDefinition("GD_Cork_PerfectHibernation.M_PerfectHibernation")),
    Mission("Trouble with Space Hurps", MissionDefinition("GD_Cork_TroubleWithSpaceHurps.M_TroubleWithSpaceHurps"),
        SpaceHurps("InnerHull_Mission.TheWorld:PersistentLevel.WillowInteractiveObject_42.MissionDirectivesDefinition_0", True, True, "InnerHull_P"),
    ),
    Enemy("One of Us", Pawn(
        "PawnBalance_BoilBadass",
        "PawnBalance_BoilGuard",
        "PawnBalance_BoilWorker",
    transform=1), mission="Trouble with Space Hurps"),
    Enemy("Better With Butter", Pawn(
        "PawnBalance_BoilBadass",
        "PawnBalance_BoilGuard",
        "PawnBalance_BoilWorker",
    transform=2), mission="Trouble with Space Hurps"),
    Enemy("Slimy Yet Satisfying", Pawn(
        "PawnBalance_BoilBadass",
        "PawnBalance_BoilGuard",
        "PawnBalance_BoilWorker",
    transform=3), mission="Trouble with Space Hurps"),
    Enemy("Meat Is Murder", Pawn(
        "PawnBalance_BoilBadass",
        "PawnBalance_BoilGuard",
        "PawnBalance_BoilWorker",
    transform=5), mission="Trouble with Space Hurps"),
    Enemy("Vegans Are Weird", Pawn(
        "PawnBalance_BoilBadass",
        "PawnBalance_BoilGuard",
        "PawnBalance_BoilWorker",
    transform=6), mission="Trouble with Space Hurps"),
    Enemy("Choice Cut", Pawn(
        "PawnBalance_HypRatGuard",
        "PawnBalance_HypRatWorker",
    transform=1), mission="Trouble with Space Hurps"),
    Enemy("Yummy Down On This", Pawn(
        "PawnBalance_HypRatGuard",
        "PawnBalance_HypRatWorker",
    transform=2), mission="Trouble with Space Hurps"),
    Enemy("Marinated Morsel", Pawn(
        "PawnBalance_HypRatGuard",
        "PawnBalance_HypRatWorker",
    transform=3), mission="Trouble with Space Hurps"),
    Enemy("Free-Range, Farm-Fresh", Pawn(
        "PawnBalance_HypRatGuard",
        "PawnBalance_HypRatWorker",
    transform=5), mission="Trouble with Space Hurps"),
    Enemy("Eat At Boil's", Pawn(
        "PawnBalance_HypRatGuard",
        "PawnBalance_HypRatWorker",
    transform=6), mission="Trouble with Space Hurps"),
    Enemy("Lazlo", Pawn("PawnBalance_Lazlo")),
    Mission("Eradicate! (Destroy CL4P-L3K)", MissionDefinition("GD_Cork_Eradicate.M_Eradicate"), tags=Tag.LongMission),
    Mission("Eradicate! (Secure CL4P-L3K)", MissionTurnInAlt("GD_Cork_Eradicate.M_Eradicate"), tags=Tag.LongMission),
    Enemy("Eghood", Pawn("PawnBalance_Eghood")),
    Enemy("CL4P-L3K", Pawn("PawnBalance_Clap_L3K")),
    Mission("Don't Get Cocky", MissionDefinition("GD_Cork_DontGetCocky.M_DontGetCocky"),
        DontGetCocky("InnerHull_Mission.TheWorld:PersistentLevel.WillowInteractiveObject_254", "InnerHull_P"),
    tags=Tag.VehicleMission),
    Other("Protected Incoming Shipment Chest",
        PositionalChest("ObjectGrade_HyperionChest", "InnerHull_P", 16216, -6842, 2279),
        PositionalChest("ObjectGrade_HyperionChest", "InnerHull_P", 16104, -6570, 2279),
        PositionalChest("ObjectGrade_HyperionChest", "InnerHull_P", 16400, -6563, 2279),
    mission="Don't Get Cocky"),
    Enemy("Dan Zando", Pawn("PawnBalance_DanZando"), mission="Don't Get Cocky"),
    Mission("Red, Then Dead", MissionDefinition("GD_Co_Side_Reshirt.M_RedShirt")),
    Mission("Things That Go Boom", MissionDefinition("GD_Co_Side_Exploders.M_Exploders")),
    Enemy("Lost Legion Courier", Pawn("PawnBalance_DahlRedShirt"), mission="Red, Then Dead"),
    Enemy("Lost Legion Powersuit Noob", Pawn("PawnBalance_DahlRedShirtPowersuit")),
    Mission("To the Moon", MissionDefinition("GD_Co_Side_EngineerMoonShot.M_EngineerMoonShot"), tags=Tag.LongMission),
    Enemy("Lost Legion Defector",
        Defector(),
    mission="To the Moon"),
    Mission("Lock and Load", MissionDefinition("GD_Co_Side_LockAndLoad.M_LockAndLoad")),
    Enemy("Tungsteena Zarpedon",
        Pawn("PawnBalance_ColZ"),
        Behavior("GD_ColZMech.Character.AIDef_ColZMech:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_60"),
        Behavior("GD_ColZMech.Character.AIDef_ColZMech:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_61"),
        Behavior("GD_ColZMech.Character.AIDef_ColZMech:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_62"),
    tags=Tag.Excluded),
    Mission("Eye to Eye", MissionTurnIn("GD_Co_LaserRebootMission.M_LaserRebootMission"), tags=Tag.Excluded),
    Mission("Picking Up the Pieces", MissionDefinition("GD_Co_Side_PickingUp.M_PickingUpThePieces"),
        MissionPickup("Laser_P.TheWorld:PersistentLevel.WillowMissionPickupSpawner_3", "Laser_P"),
    ),
    Other("Scientist Laser Stash", Attachment("ObjectGrade_HypWeaponChest_Laser"), mission="Picking Up the Pieces"),
    Mission("These are the Bots", MissionDefinition("GD_Co_Side_TheseAreTheBots.M_TheseAreTheBots"),
        TheseAreTheBots(),
    tags=Tag.LongMission),
    Mission("The Don", MissionDefinition("GD_Co_Side_TheDon.M_TheDon")),
    Mission("Return of Captain Chef", MissionDefinition("GD_Co_ReturnOfCapnChef.M_ReturnOfCaptainChef"),
        ChefReturn(),
    tags=Tag.LongMission),
    Enemy("Injured Lost Legion Soldier",
        InjuredSoldier(),
    tags=Tag.Freebie),
    Enemy("Raum-Kampfjet Mark V", Behavior("GD_ZarpedonJetP1Boss.Character.AIDef_ZarpedonJetP1Boss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_104"),
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
    Mission("Don't Shoot the Messenger", MissionDefinition("GD_Co_DontShootMessenger.MissionDef.M_DontShootMsgr"),
        MissionPickup("11B_Access_GAME.TheWorld:PersistentLevel.WillowMissionPickupSpawner_0", "Access_P"),
    tags=Tag.LongMission),
    Enemy("Hanna",
        Hanna(),
    mission="Don't Shoot the Messenger"),
    Enemy("Opha Superior", Pawn("PawnBalance_OphaBoss")),
    Enemy("The Sentinel (First Phase)", Pawn("PawnBalance_FinalBossCork"), tags=Tag.Excluded),
    Enemy("The Sentinel", Behavior("GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_86", offset=(0, 0, 256)),
        Behavior(
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_81",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_84",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_85",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_87",
        inject=False, offset=(0, 0, 256)),
    tags=Tag.SlowEnemy, rarities=(50, 50)),
    Mission("The Beginning of the End", MissionTurnIn("GD_Co_Chapter11.M_DahlDigsite"), tags=Tag.Excluded),
    Mission("Guardian Hunter (Turn in Sterwin)", MissionDefinition("GD_Co_GuardianHunter.MissionDef.M_GuardianHunter", block_weapon=False), tags=Tag.LongMission),
    Mission("Guardian Hunter (Turn in Master Poacher)", MissionTurnInAlt("GD_Co_GuardianHunter.MissionDef.M_GuardianHunter"), tags=Tag.LongMission),
    Enemy("Master Poacher", MasterPoacher(), mission="Guardian Hunter (Turn in Sterwin)"),
    Mission("Sterwin Forever", MissionDefinition("GD_Co_GuardianHunter.MissionDef.M_SterwinForever", block_weapon=False)),
    Enemy("Iwajira",
        Pawn("PawnBalance_Rockzilla"),
        Behavior(
            "GD_Rockzilla.Death.DeathDef_Rockzilla:BehaviorProviderDefinition_0.Behavior_SpawnItems_147",
            "GD_Rockzilla.Death.DeathDef_Rockzilla:BehaviorProviderDefinition_0.Behavior_SpawnItems_146",
        inject=False, scatter=(512, 512, 512)),
    tags=Tag.SlowEnemy),
    Enemy("Odjurymir",
        Pawn("PawnBalance_Frostzilla"),
        Behavior(
            "GD_Frostzilla.Character.AIDef_Frostzilla:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_74",
            "GD_Frostzilla.Character.AIDef_Frostzilla:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_75",
            "GD_Frostzilla.Character.AIDef_Frostzilla:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_76",
            "GD_Frostzilla.Character.AIDef_Frostzilla:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_77",
        inject=False, scatter=(512, 512, 512)),
    tags=Tag.Holiday|Tag.SlowEnemy),
    Mission("The Bestest Story Ever Told", MissionDefinition("GD_Co_CorkRaid.M_CorkRaid"), tags=Tag.Raid),
    Enemy("The Invincible Sentinel (First Phase)", Pawn("PawnBalance_RaidBossCork"), tags=Tag.Excluded),
    Enemy("The Invincible Sentinel",
        SentinelRaid(),
        Behavior(
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_82",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_83",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_88",
            "GD_FinalBossCorkBig.IOs.IO_LootSpew:BehaviorProviderDefinition_0.Behavior_SpawnItems_89",
        offset=(0, 0, 256)),
    tags=Tag.Raid),

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
    Other("Popup Ad",
        PopupAd(),
    tags=Tag.ClaptasticVoyage|Tag.Freebie, rarities=(33,)),
    Enemy("Loot Bug", Pawn("PawnBalance_LootBug"), tags=Tag.ClaptasticVoyage|Tag.RareEnemy),
    Other("File Search Glitch Chest", Attachment("ObjectGrade_HypWeaponChest_FileSearch_Glitched"), tags=Tag.Excluded),
    Mission("Spyware Who Came in from the Cold", MissionDefinition("GD_Ma_Side_SpywareInFromCold.M_Ma_Side_SpywareInFromCold"),
        SpywareChest("Balance_SpywareChest"),
        SpywareBug(),
    tags=Tag.ClaptasticVoyage|Tag.VeryLongMission),
    Other("Advanced Search Chest", PositionalChest("ObjectGrade_HyperionChest_Glitched", "Ma_Motherboard_P", -133482, 55869, 2782), tags=Tag.ClaptasticVoyage),
    Mission("Rose Tinting", MissionDefinition("GD_Ma_Side_MINAC.M_Ma_Side_MINAC"),
        RoseTinting(),
    tags=Tag.ClaptasticVoyage),
    Mission("Chip's Data Mining Adventure (Kill Shame)", MissionDefinition("GD_Ma_Side_CookieDataMining.M_Ma_Side_CookieDataMining"),
        DataMining(),
    tags=Tag.ClaptasticVoyage),
    Enemy("Shame", Pawn("PawnBalance_Trojan_Shame"), mission="Chip's Data Mining Adventure (Kill Shame)"),
    Mission("Chip's Data Mining Adventure (Kill Cookies)", MissionTurnInAlt("GD_Ma_Side_CookieDataMining.M_Ma_Side_CookieDataMining"),
        MissionGiver("GD_Ma_MiniTrojan_Shame.Character.Pawn_Ma_MiniTrojan_Shame:MissionDirectivesDefinition_1", True, True, "Ma_LeftCluster_P"),
    tags=Tag.ClaptasticVoyage),
    Enemy("Chip", Pawn("PawnBalance_Ma_Chip"), mission="Chip's Data Mining Adventure (Kill Cookies)"),
    Enemy("Cookie", Pawn("PawnBalance_Ma_Cookie"), mission="Chip's Data Mining Adventure (Kill Cookies)", rarities=(15,)),
    Mission("1D-TP", MissionDefinition("GD_Ma_Side_IdTrap.M_Ma_Side_IdTrap"), tags=Tag.ClaptasticVoyage),
    Mission("3G0-TP", EgoTrap(), MissionDefinition("GD_Ma_Side_EgoTrap.M_Ma_Side_EgoTrap"), tags=Tag.ClaptasticVoyage|Tag.LongMission),
    Mission("Corrosion of Dignity", MissionDefinition("GD_Ma_Side_ShredOfDignity.M_Ma_Side_ShredOfDignity"),
        Dignity(),
    tags=Tag.ClaptasticVoyage|Tag.Freebie),
    Other("Motherlessboard Hidden Stash", Attachment("Balance_HiddenStash_03"),
        ClaptasticStash("GD_Ma_Population_Treasure.InteractiveObjects.InteractiveObj_HiddenStash_03:BehaviorProviderDefinition_0", "Ma_Motherboard_P"),
    tags=Tag.ClaptasticVoyage|Tag.Freebie),
    Other("Cluster 99002 0V3RL00K Hidden Stash", Attachment("Balance_HiddenStash_02"),
        ClaptasticStash("GD_Ma_Population_Treasure.InteractiveObjects.InteractiveObj_HiddenStash_02:BehaviorProviderDefinition_0", "Ma_RightCluster_P"),
    tags=Tag.ClaptasticVoyage),
    Other("Faptrap", PositionalChest("ObjectGrade_DahlWeaponChest_Marigold", "Ma_RightCluster_P", 63919, 1298, 128), tags=Tag.ClaptasticVoyage),
    Enemy("Denial Subroutine", Pawn("PawnBalance_CodeWorm"), tags=Tag.ClaptasticVoyage|Tag.SlowEnemy),
    Mission("You Can Stop the Music", MissionDefinition("GD_Ma_Side_StopTheMusic.M_Ma_Side_StopTheMusic"),
        StopTheMusic(),
    tags=Tag.ClaptasticVoyage),
    Enemy("Teh Earworm", Pawn("PawnBalance_EarWorm"), tags=Tag.ClaptasticVoyage|Tag.SlowEnemy),
    Enemy("Catchy Hook!", Pawn("PawnBalance_EarWormTentacle", transform=0), tags=Tag.ClaptasticVoyage),
    Enemy("Most Requested!", Pawn("PawnBalance_EarWormTentacle", transform=1), tags=Tag.ClaptasticVoyage),
    Enemy("Key Change!", Pawn("PawnBalance_EarWormTentacle", transform=2), tags=Tag.ClaptasticVoyage),
    Enemy("Tween Favorite!", Pawn("PawnBalance_EarWormTentacle", transform=3), tags=Tag.ClaptasticVoyage),
    Enemy("Verse Chorus Verse Chorus Bridge Chorus (x2)!", Pawn("PawnBalance_EarWormTentacle", transform=5), tags=Tag.ClaptasticVoyage),
    Enemy("Sparkly Formula!", Pawn("PawnBalance_EarWormTentacle", transform=6), tags=Tag.ClaptasticVoyage),
    Enemy("Floor Filler!", Pawn("PawnBalance_EarWormTentacle", transform=4), tags=Tag.ClaptasticVoyage),
    Mission("Byte Club", MissionDefinition("GD_Ma_Side_ByteClub.M_Ma_Side_ByteClub"),
        ByteClub(),
    tags=Tag.ClaptasticVoyage),
    Mission("5UP4-3G0-TP", MissionDefinition("GD_Ma_Side_SuperEgoTrap.M_Ma_Side_SuperEgoTrap"),
        SupaEgoTrap(),
    tags=Tag.ClaptasticVoyage),
    Enemy("Rex Loader", Pawn("Balance_Ma_RexLoader"), mission="5UP4-3G0-TP"),
    Enemy("5UP4-3G0-TP", Pawn("BD_Ma_SuperEgoTrap"), mission="5UP4-3G0-TP"),
    Mission("The Temple of Boom (Turn in Tannis)", MissionDefinition("GD_Ma_Side_TempleOfBoom.M_Ma_Side_TempleofBoom"), tags=Tag.ClaptasticVoyage),
    Mission("The Temple of Boom (Turn in Gladstone)", MissionTurnInAlt("GD_Ma_Side_TempleOfBoom.M_Ma_Side_TempleofBoom"), tags=Tag.ClaptasticVoyage),
    Enemy("The Sponx", Pawn("Balance_Ma_Sponx"), tags=Tag.ClaptasticVoyage|Tag.SlowEnemy),
    Enemy("Despair", Pawn("PawnBalance_Despair"), tags=Tag.ClaptasticVoyage|Tag.SlowEnemy),
    Enemy("Self-Loathing", Pawn("PawnBalance_SelfLoathing"), tags=Tag.ClaptasticVoyage|Tag.SlowEnemy),
    Other("Jack's Bobble Head",
        JackBobble(),
    tags=Tag.ClaptasticVoyage),
    Mission("A Deadlier Game", DeadlierGame(), MissionDefinition("GD_Ma_Side_BadTrap.M_Ma_Side_BadTrap"), tags=Tag.ClaptasticVoyage),
    Mission("The Sum of Some Fears", MissionDefinition("GD_Ma_Side_SumOfSomeFears.M_Ma_Side_SumOfSomeFears"),
        MissionGiver("GD_Ma_MetaTrap_SomeFears.Character.Pawn_Ma_MetaTrap_SomeFears:MissionDirectivesDefinition_0", True, True, "Ma_Subconscious_P"),
        MissionGiver("Ma_Subconscious_SideMissions.TheWorld:PersistentLevel.WillowInteractiveObject_1.MissionDirectivesDefinition_0", False, False, "Ma_Subconscious_P"),
        SumFears(),
    tags=Tag.ClaptasticVoyage|Tag.LongMission),
    Other("T.K. Baha's Chest",
        Attachment("Balance_HiddenStash_01"),
        ClaptasticStash("GD_Ma_Population_Treasure.InteractiveObjects.InteractiveObj_HiddenStash_01:BehaviorProviderDefinition_0", "Ma_Subconscious_P"),
    tags=Tag.ClaptasticVoyage),
    Mission("END OF LINE", MissionDefinition("GD_Ma_Chapter05.M_Ma_Chapter05"), tags=Tag.Excluded),
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
    Mission("System Shutdown", MissionTurnIn("GD_Ma_Chapter06.M_Ma_Chapter06"), tags=Tag.Excluded),
    Mission("h4X0rz", MissionDefinition("GD_Ma_Side_H4X0rz.M_Ma_Side_H4X0rz"), tags=Tag.ClaptasticVoyage|Tag.LongMission),
    Mission("l33t h4X0rz", MutatorMissionDefinition("GD_Ma_Side_H4X0rz.M_Ma_Side_H4X0rz_Repeat"), tags=Tag.ClaptasticVoyage|Tag.Slaughter),
    Other("Black Mutator Chest", MutatorChest("ObjectGrade_CommonChest_Mut", configuration=1), mission="l33t h4X0rz"),
    Other("Red Mutator Chest", MutatorChest("ObjectGrade_RedChest_Mut", configuration=1), mission="l33t h4X0rz"),
    Other("Purple Mutator Chest", MutatorChest("ObjectGrade_GlitchChest_Mut", configuration=1), mission="l33t h4X0rz"),
    Enemy("5H4D0W-TP", MutatorPawn("PawnBalance_SH4D0W-TP-Part1"), mission="l33t h4X0rz", tags=Tag.VeryRareEnemy),
    Enemy("Hope", MutatorPawn("PawnBalance_Hope"), mission="l33t h4X0rz", tags=Tag.VeryRareEnemy),
    Enemy("Self Esteem", MutatorPawn("PawnBalance_SelfEsteem"), mission="l33t h4X0rz", tags=Tag.VeryRareEnemy),

    Mission("Digistructed Madness: Round 1", MissionDefinition("GD_EridianSlaughter.MissionDef.M_EridianSlaughter01"), tags=Tag.Holodome|Tag.Slaughter|Tag.LongMission),
    Mission("Digistructed Madness: Round 1 (Turn On Jump Pads)",
        MissionTurnInAlt("GD_EridianSlaughter.MissionDef.M_EridianSlaughter01"),
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
        MissionTurnInAlt("GD_EridianSlaughter.MissionDef.M_EridianSlaughter02"),
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
        MissionTurnInAlt("GD_EridianSlaughter.MissionDef.M_EridianSlaughter03"),
        HolodomeMission(
            objective_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter03:OBJ_30_SaveSci",
            compare_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter03:Behavior_CompareBool_13",
            didntdo_behavior_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter03:Behavior_UpdateMissionObjective_53",
            did_behavior_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter03:Behavior_UpdateMissionObjective_48",
        ),
    tags=Tag.Holodome|Tag.Slaughter|Tag.LongMission),
    Enemy("Scientist", HolodomeScientists(), tags=Tag.Holodome),

    Mission("Digistructed Madness: Round 4", MissionDefinition("GD_EridianSlaughter.MissionDef.M_EridianSlaughter04"), tags=Tag.Holodome|Tag.Slaughter|Tag.VeryLongMission),
    Mission("Digistructed Madness: Round 4 (Destroy Destroyers)",
        MissionTurnInAlt("GD_EridianSlaughter.MissionDef.M_EridianSlaughter04"),
        HolodomeMission(
            objective_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter04:OBJ_30_KillDestroyer",
            compare_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter04:Behavior_CompareBool_1",
            didntdo_behavior_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter04:Behavior_UpdateMissionObjective_5",
            did_behavior_path = "GD_EridianSlaughter.MissionDef.M_EridianSlaughter04:Behavior_UpdateMissionObjective_6",
        ),
    tags=Tag.Holodome|Tag.Slaughter|Tag.VeryLongMission),
    Enemy("Defense Destroyer", Pawn("PawnBalance_DestroyerMini"), tags=Tag.Holodome),
    Enemy("Guardian Pondor / Lost Legion Chosen Powersuit",
        Pawn("PawnBalance_GuardianPondor"),
        Pawn("PawnBalance_DahlEternalPowersuit"),
        Pawn("PawnBalance_DahlEternalPowersuitShield"),
    mission="Digistructed Madness: Round 4", tags=Tag.MobFarm, rarities=(7,)),

    Mission("Digistructed Madness: Round 5", MissionDefinition("GD_EridianSlaughter.MissionDef.M_EridianSlaughter05"), tags=Tag.Holodome|Tag.Slaughter|Tag.VeryLongMission),
    Mission("Digistructed Madness: Round 5 (Install Vault Key Pieces)",
        MissionTurnInAlt("GD_EridianSlaughter.MissionDef.M_EridianSlaughter05"),
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
    rarities=(33,), tags=Tag.Holodome),

    Mission("Digistructed Madness: The Badass Round", MissionDefinition("GD_EridianSlaughter.MissionDef.M_EridianSlaughter_Badass"), tags=Tag.Holodome|Tag.Slaughter|Tag.VeryLongMission|Tag.Raid),
)

"""
TODO:
add:
    fair cop

Make main story scientists drop Scientists loot

genericize balanceless pawn deaths
"""
