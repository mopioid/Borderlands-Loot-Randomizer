from __future__ import annotations

import enum
from typing import Callable, List, Optional, Sequence, TYPE_CHECKING

from unrealsdk import (
    FindAll,
    FindObject,
    FStruct,
    GetEngine,
    KeepAlive,
    Log,
    RemoveHook,
    RunHook,
    UFunction,
    UObject,
)

from . import items, options, seed
from .defines import *
from .locations import Dropper, Location, MapDropper, RegistrantDropper


class PlaythroughDelegate(MapDropper):
    paths = ("*",)

    playthrough: int

    def entered_map(self) -> None:
        pc = get_pc()
        if not pc:
            return

        new_playthrough = pc.GetCurrentPlaythrough()
        if new_playthrough == self.playthrough:
            return

        if seed.AppliedSeed:
            for location in seed.AppliedSeed.locations:
                if isinstance(location, Mission):
                    if new_playthrough == 2:
                        location.mission_definition.restore_xp()
                    else:
                        location.mission_definition.remove_xp()

        self.playthrough = new_playthrough

    def enable(self) -> None:
        super().enable()
        self.playthrough = 2


def Enable() -> None:
    RunHook(
        "WillowGame.WillowPlayerController.AcceptMission",
        "LootRandomizer",
        _AcceptMission,
    )
    RunHook(
        "WillowGame.WillowPlayerController.ServerCompleteMission",
        "LootRandomizer",
        _CompleteMission,
    )

    RunHook(
        "WillowGame.WillowMissionItem.MissionDenyPickup",
        "LootRandomizer",
        _MissionDenyPickup,
    )
    RunHook(
        "Engine.WillowInventory.PickupAssociated",
        "LootRandomizer",
        _PickupAssociated,
    )

    RunHook(
        "WillowGame.WillowPlayerController.TryPromptForFastForward",
        "LootRandomizer",
        lambda c, f, p: False,
    )
    RunHook(
        "WillowGame.WillowPlayerController.CheckAllSideMissionsCompleteAchievement",
        "LootRandomizer",
        lambda c, f, p: False,
    )


def Disable() -> None:
    RemoveHook(
        "WillowGame.WillowPlayerController.AcceptMission",
        "LootRandomizer",
    )
    RemoveHook(
        "WillowGame.WillowPlayerController.ServerCompleteMission",
        "LootRandomizer",
    )

    RemoveHook(
        "Engine.WillowInventory.PickupAssociated",
        "LootRandomizer",
    )
    RemoveHook(
        "WillowGame.WillowMissionItem.MissionDenyPickup",
        "LootRandomizer",
    )

    RemoveHook(
        "WillowGame.WillowPlayerController.TryPromptForFastForward",
        "LootRandomizer",
    )
    RemoveHook(
        "WillowGame.WillowPlayerController.CheckAllSideMissionsCompleteAchievement",
        "LootRandomizer",
    )


def _AcceptMission(caller: UObject, _f: UFunction, params: FStruct) -> bool:
    missiondef = params.Mission
    registry = MissionDefinition.Registrants(missiondef)
    if not registry:
        return True

    delegates: List[Callable[[], None]] = []
    for mission_dropper in registry:
        for dropper in mission_dropper.location.droppers:
            if isinstance(dropper, MissionStatusDelegate):
                delegates.append(dropper.accepted)

    if (
        get_missiontracker().GetMissionStatus(missiondef)
        == Mission.Status.NotStarted
    ):
        do_next_tick(*delegates)
        return True

    def play_kickoff(missiondef: UObject = missiondef):
        tracker = get_missiontracker()
        tracker.PlayKickoff(missiondef)
        tracker.SetKickoffHeard(missiondef)

    do_next_tick(play_kickoff, *delegates)
    return True


def _CompleteMission(caller: UObject, _f: UFunction, params: FStruct) -> bool:
    missiondef = params.Mission
    registry = MissionDefinition.Registrants(missiondef)
    if not registry:
        return True

    pc = get_pc()
    playthrough = pc.GetCurrentPlaythrough()
    mission_index = pc.NativeGetMissionIndex(missiondef)
    mission_list = pc.MissionPlaythroughs[playthrough].MissionList
    mission_data = mission_list[mission_index]

    delegates: List[Callable[[], None]] = []

    for mission_dropper in registry:
        for dropper in mission_dropper.location.droppers:
            if isinstance(dropper, MissionStatusDelegate):
                delegates.append(dropper.completed)

        if mission_dropper.should_inject(mission_data):
            mission_dropper.inject(mission_data)
            delegates.append(mission_dropper.revert)

    do_next_tick(*delegates)

    return True


def _itemdef_make_repeatable(itemdef: UObject) -> bool:
    if not (itemdef and itemdef.MissionDirective):
        return False

    registry = MissionDefinition.Registrants(itemdef.MissionDirective)
    if not registry:
        return False

    for mission_dropper in registry:
        if mission_dropper.location.item:
            break
    else:
        return False

    return mission_dropper.location.current_status in (
        Mission.Status.NotStarted,
        Mission.Status.Complete,
    )


def _MissionDenyPickup(
    caller: UObject, _f: UFunction, params: FStruct
) -> bool:
    itemdef = caller.GetInventoryDefinition()
    if not _itemdef_make_repeatable(itemdef):
        return True

    # Don't judge me; this is literally how the game does it.
    for pickup in FindAll("WillowPickup"):
        if (
            pickup.Inventory
            and pickup.Inventory.GetInventoryDefinition() == itemdef
        ):
            return True

    return False


def _PickupAssociated(caller: UObject, _f: UFunction, params: FStruct) -> bool:
    itemdef = caller.GetInventoryDefinition()
    if not _itemdef_make_repeatable(itemdef):
        return True

    def enable_pickup(pickup: UObject = params.Pickup):
        pickup.SetPickupability(True)
        if not is_client():
            get_missiontracker().RegisterMissionDirector(pickup)

    do_next_tick(enable_pickup)
    return True


class MissionDropper(Dropper):
    location: Mission


class MissionDefinition(MissionDropper, RegistrantDropper):
    Registries = dict()

    uobject: UObject

    block_weapon: bool
    unlink_next: bool

    reward_items: Sequence[UObject]
    reward_pools: Sequence[UObject]
    reward_xp_scale: int

    mission_weapon: Optional[UObject] = None
    give_weapon_set: Optional[UObject] = None
    take_weapon_set: Optional[UObject] = None

    repeatable: bool
    next_link: Optional[UObject]

    def __init__(
        self,
        path: str,
        *,
        block_weapon: bool = True,
        unlink_next: bool = False,
    ) -> None:
        self.block_weapon = block_weapon
        self.unlink_next = unlink_next
        super().__init__(path)

    @property
    def reward(self) -> FStruct:
        return self.uobject.Reward

    def enable(self) -> None:
        super().enable()

        uobject = FindObject("MissionDefinition", self.paths[0])
        if not uobject:
            raise Exception(f"Failed to find mission {self.paths[0]}")
        self.uobject = uobject

        for reward_items in self.reward.RewardItems:
            KeepAlive(reward_items)
        self.reward_items = tuple(self.reward.RewardItems)
        self.reward.RewardItems = ()

        for reward_pool in self.reward.RewardItemPools:
            KeepAlive(reward_pool)
        self.reward_pools = tuple(self.reward.RewardItemPools)
        self.reward.RewardItemPools = ()

        self.reward_xp_scale = (
            self.reward.ExperienceRewardPercentage.BaseValueScaleConstant
        )

        self.repeatable = self.uobject.bRepeatable

        self.prepare_attributes()

    def disable(self) -> None:
        super().disable()

        self.reward.RewardItems = self.reward_items
        self.reward.RewardItemPools = self.reward_pools
        self.restore_xp()

        self.revert_attributes()

    def prepare_attributes(self) -> None:
        self.mission_weapon = self.uobject.MissionWeapon
        if self.mission_weapon and self.block_weapon:
            KeepAlive(self.mission_weapon)
            self.uobject.MissionWeapon = None

            self.give_weapon_set = self.uobject.GiveWeaponSet
            if self.give_weapon_set:
                KeepAlive(self.give_weapon_set)
                self.uobject.GiveWeaponSet = None

            self.take_weapon_set = self.uobject.TakeWeaponSet
            if self.take_weapon_set:
                KeepAlive(self.take_weapon_set)
                self.uobject.TakeWeaponSet = None

        if self.unlink_next:
            self.next_link = self.uobject.NextMissionInChain
            if self.next_link:
                KeepAlive(self.next_link)
                self.uobject.NextMissionInChain = None

    def revert_attributes(self) -> None:
        self.uobject.bRepeatable = self.repeatable

        if self.mission_weapon and self.block_weapon:
            self.uobject.MissionWeapon = self.mission_weapon
            if self.give_weapon_set:
                self.uobject.GiveWeaponSet = self.give_weapon_set
            if self.take_weapon_set:
                self.uobject.TakeWeaponSet = self.take_weapon_set

        if self.unlink_next:
            self.uobject.NextMissionInChain = self.next_link

    def remove_xp(self) -> None:
        self.reward.ExperienceRewardPercentage.BaseValueScaleConstant = 0

    def restore_xp(self) -> None:
        self.reward.ExperienceRewardPercentage.BaseValueScaleConstant = (
            self.reward_xp_scale
        )

    def make_repeatable(self) -> None:
        self.uobject.bRepeatable = True

    def revert_repeatable(self) -> None:
        self.uobject.bRepeatable = self.repeatable

    def should_inject(self, mission_data: FStruct) -> bool:
        if not self.location.item:
            return False

        progress = tuple(mission_data.ObjectivesProgress)
        alt_reward, _ = self.uobject.ShouldGrantAlternateReward(progress)
        return not alt_reward

    def inject(self, mission_data: FStruct) -> None:
        if not self.location.item:
            return

        pool = self.location.prepare_pools(1)[0]
        self.reward.RewardItemPools = (pool,)

        if self.location.item == items.DudItem:
            return

        for pri in GetEngine().GetCurrentWorldInfo().GRI.PRIArray:
            pc = pri.Owner

            bonuses = len(self.location.rarities)
            if pc is get_pc():
                bonuses -= 1
            if not bonuses:
                continue

            if pc is get_pc() and not options.RewardsTrainingSeen.CurrentValue:

                def training() -> None:
                    show_dialog(
                        "Multiple Rewards",
                        (
                            "The mission you just completed takes longer than "
                            "average to complete. As a reward, a bonus "
                            "instance of its reward has been added to your "
                            "backpack."
                        ),
                        5,
                    )
                    options.RewardsTrainingSeen.CurrentValue = True
                    options.SaveSettings()

                do_next_tick(training)

            def loot_callback(item: UObject, pc: UObject = pc) -> None:
                definition_data = item.DefinitionData
                definition_data.ManufacturerGradeIndex = mission_data.GameStage
                definition_data.GameStage = mission_data.GameStage
                definition_data = convert_struct(definition_data)

                if definition_data[0].Class.Name == "WeaponTypeDefinition":
                    pc.GetPawnInventoryManager().ClientAddWeaponToBackpack(
                        definition_data, 1
                    )
                else:
                    pc.GetPawnInventoryManager().ClientAddItemToBackpack(
                        definition_data, 1, 1
                    )

            for _ in range(bonuses):
                spawn_item(self.location.item.pool, pc, loot_callback)

    def revert(self) -> None:
        self.reward.RewardItemPools = ()

    def __eq__(self, value: object) -> bool:
        if isinstance(value, self.__class__):
            return (
                self.__class__ == value.__class__ and self.paths == value.paths
            )
        return False

    def __hash__(self) -> int:
        return id(self)


class MissionTurnIn(MissionDefinition):
    alt: bool

    def __init__(self, path: str) -> None:
        super(MissionDefinition, self).__init__(path)

    def prepare_attributes(self) -> None:
        pass

    def revert_attributes(self) -> None:
        pass

    def make_repeatable(self) -> None:
        pass

    def revert_repeatable(self) -> None:
        pass


class MissionTurnInAlt(MissionTurnIn):
    @property
    def reward(self) -> FStruct:
        return self.uobject.AlternativeReward

    def should_inject(self, mission_data: FStruct) -> bool:
        if not self.location.item:
            return False

        return not super().should_inject(mission_data)


class MissionStatusDelegate(MissionDropper):
    def accepted(self) -> None:
        pass

    def completed(self) -> None:
        pass


class MissionObject(MissionStatusDelegate, MapDropper):
    path: str

    def __init__(self, path: str, *map_names: str) -> None:
        self.path = path
        super().__init__(*map_names)

    def apply(self) -> Optional[UObject]:
        obj = FindObject("WillowInteractiveObject", self.path)
        if obj:
            obj.SetUsability(True, 0)

            if BL2:
                obj.SetMissionDirectivesUsability(1)
            else:
                obj.SetMissionDirectivesUsability(1, 0)

            if not is_client():
                get_missiontracker().RegisterMissionDirector(obj)
        return obj

    def entered_map(self) -> None:
        if self.location.current_status != Mission.Status.NotStarted:
            self.apply()

    def completed(self) -> None:
        self.apply()


class MissionPickup(MissionObject):
    location: Mission

    def apply(self) -> Optional[UObject]:
        spawner = FindObject("WillowMissionPickupSpawner", self.path)
        if spawner:
            spawner.SetPickupStatus(True)
            if spawner.MissionPickup:
                spawner.MissionPickup.SetPickupability(True)
                if not is_client():
                    get_missiontracker().RegisterMissionDirector(
                        spawner.MissionPickup
                    )
        return spawner


class MissionGiver(MissionObject):
    path: str
    begins: bool
    ends: bool
    mission: Optional[str]

    def __init__(
        self, path: str, begins: bool, ends: bool, *map_names: str
    ) -> None:
        self.begins = begins
        self.ends = ends
        super().__init__(path, *map_names)

    def apply(self) -> Optional[UObject]:
        giver = FindObject("MissionDirectivesDefinition", self.path)
        if not giver:
            return None

        missiondef = self.location.mission_definition.uobject

        if self.begins or self.ends:
            for directive in giver.MissionDirectives:
                if directive.MissionDefinition == missiondef:
                    directive.bBeginsMission = self.begins
                    directive.bEndsMission = self.ends
                    break
            else:
                directives = convert_struct(giver.MissionDirectives)
                directives.append((missiondef, self.begins, self.ends, 0))
                giver.MissionDirectives = directives
        else:
            directives = tuple(
                convert_struct(directive)
                for directive in giver.MissionDirectives
                if directive.MissionDefinition != missiondef
            )
            giver.MissionDirectives = directives

        return giver


class Mission(Location):
    mission_definition: MissionDefinition

    class Status(enum.IntEnum):
        NotStarted = 0
        Active = 1
        RequiredObjectivesComplete = 2
        ReadyToTurnIn = 3
        Complete = 4
        Failed = 5
        Unknown = 6

    def enable(self) -> None:
        super().enable()

        self.select_mission_definition()
        if self.item:
            if not hasattr(self, "mission_definition"):
                raise Exception(f"No MissionDefinition for {self.name}")
            self.mission_definition.make_repeatable()

        if not (self.tags & MissionTags):
            self.tags |= Tag.ShortMission
        if not (self.tags & ContentTags):
            self.tags |= Tag.BaseGame

        self.rarities = [100]
        if self.tags & Tag.LongMission:
            self.rarities += (100,)
        if self.tags & Tag.VeryLongMission:
            self.rarities += (100, 100, 100)
        if self.tags & Tag.Raid:
            self.rarities += (100, 100, 100)

    def disable(self) -> None:
        super().disable()
        if hasattr(self, "mission_definition"):
            self.mission_definition.revert_repeatable()
            del self.mission_definition

    def handles_mission_definition(self, other: MissionDefinition) -> bool:
        for dropper in self.droppers:
            if isinstance(dropper, MissionDefinition):
                if dropper == other:
                    return True
        return False

    def select_mission_definition(self) -> None:
        if not seed.AppliedSeed:
            raise Exception("Enabling mission with no seed applied.")

        for dropper in self.droppers:
            if not isinstance(dropper, MissionDefinition):
                continue

            for other_location in reversed(seed.AppliedSeed.locations):
                if other_location is self:
                    self.mission_definition = dropper
                    return

                if isinstance(other_location, Mission):
                    if other_location.handles_mission_definition(dropper):
                        dropper.disable()
                        break
            else:
                self.mission_definition = dropper
                return

    @property
    def current_status(self) -> Status:
        uobject = self.mission_definition.uobject
        status = get_missiontracker().GetMissionStatus(uobject)
        return Mission.Status(status)

    def __str__(self) -> str:
        return f"Mission: {self.name}"
