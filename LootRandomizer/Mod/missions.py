from __future__ import annotations

from unrealsdk import Log, FindObject, FindAll, GetEngine, KeepAlive
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct

from . import options, items
from .defines import *
from .locations import Dropper, Location, MapDropper, RegistrantDropper

import enum

from typing import Callable, Generator, List, Optional, Sequence


class PlaythroughDelegate(MapDropper):
    paths = ("*",)

    def entered_map(self) -> None:
        pc = get_pc()
        if not pc:
            return

        new_playthrough = pc.GetCurrentPlaythrough()
        if new_playthrough == self.playthrough:
            return

        if   BL2: from .bl2.locations import Locations
        elif TPS: from .tps.locations import Locations
        else: raise

        for location in Locations:
            if isinstance(location, Mission) and Tag.Excluded not in location.tags:
                if new_playthrough == 2:
                    location.mission_definition.restore_xp()
                else:
                    location.mission_definition.remove_xp()

        self.playthrough = new_playthrough

    def enable(self) -> None:
        super().enable()
        self.playthrough = 2

_playthrough_delegate = PlaythroughDelegate()


def Enable() -> None:
    _playthrough_delegate.enable()

    RunHook("WillowGame.WillowPlayerController.TryPromptForFastForward", "LootRandomizer", lambda c,f,p: False)

    RunHook("WillowGame.WillowPlayerController.AcceptMission", "LootRandomizer", _AcceptMission)
    RunHook("WillowGame.WillowPlayerController.ServerCompleteMission", "LootRandomizer", _CompleteMission)

    RunHook("WillowGame.WillowMissionItem.MissionDenyPickup", "LootRandomizer", _MissionDenyPickup)
    RunHook("Engine.WillowInventory.PickupAssociated", "LootRandomizer", _PickupAssociated)


def Disable() -> None:
    _playthrough_delegate.disable()

    RemoveHook("WillowGame.WillowPlayerController.TryPromptForFastForward", "LootRandomizer")

    RemoveHook("WillowGame.WillowPlayerController.AcceptMission", "LootRandomizer")
    RemoveHook("WillowGame.WillowPlayerController.ServerCompleteMission", "LootRandomizer")

    RemoveHook("Engine.WillowInventory.PickupAssociated", "LootRandomizer")
    RemoveHook("WillowGame.WillowMissionItem.MissionDenyPickup", "LootRandomizer")


def _AcceptMission(caller: UObject, function: UFunction, params: FStruct) -> bool:
    missiondef = params.Mission
    registry = MissionDefinition.Registrants(missiondef)
    if not registry:
        return True

    delegates: List[Callable[[], None]] = []
    for mission_dropper in registry:
        for dropper in mission_dropper.location.droppers:
            if isinstance(dropper, MissionStatusDelegate):
                delegates.append(dropper.accepted)

    def play_kickoff(missiondef: UObject = missiondef):
        tracker = get_missiontracker()
        tracker.PlayKickoff(missiondef)
        tracker.SetKickoffHeard(missiondef)

    do_next_tick(play_kickoff, *delegates)
    return True


def _CompleteMission(caller: UObject, function: UFunction, params: FStruct) -> bool:
    missiondef = params.Mission
    registry = MissionDefinition.Registrants(missiondef)
    if not registry:
        return True

    pc = get_pc()
    playthrough = pc.GetCurrentPlaythrough()
    mission_index = pc.NativeGetMissionIndex(missiondef)
    mission_data = pc.MissionPlaythroughs[playthrough].MissionList[mission_index]
    mission_level = mission_data.GameStage
    alt_reward, _ = missiondef.ShouldGrantAlternateReward(tuple(mission_data.ObjectivesProgress))

    mission_dropper: Optional[MissionDefinition] = None

    delegates: List[Callable[[], None]] = []

    for a_mission_dropper in registry:
        for dropper in a_mission_dropper.location.droppers:
            if isinstance(dropper, MissionStatusDelegate):
                delegates.append(dropper.completed)

        if isinstance(a_mission_dropper, MissionDefinitionAlt) == alt_reward:
            mission_dropper = a_mission_dropper

    if not (mission_dropper and mission_dropper.location.item):
        return True
    
    def revert(): mission_dropper.reward.RewardItemPools = ()
    do_next_tick(*delegates, revert)

    pool = mission_dropper.location.prepare_pools(1)[0]
    mission_dropper.reward.RewardItemPools = (pool,)

    if mission_dropper.location.item == items.DudItem:
        return True

    for pri in GetEngine().GetCurrentWorldInfo().GRI.PRIArray:
        pc = pri.Owner

        bonuses = len(mission_dropper.location.rarities)
        if pc is get_pc():
            bonuses -= 1
        if not bonuses:
            continue

        if pc is get_pc() and (not options.RewardsTrainingSeen.CurrentValue):
            def training() -> None:
                show_dialog("Multiple Rewards", (
                    "The mission you just completed takes longer than average to complete. As a "
                    "reward, a bonus instance of its loot item has been added to your backpack."
                ), 5)
                options.RewardsTrainingSeen.CurrentValue = True
                options.SaveSettings()
            do_next_tick(training)

        def loot_callback(item: UObject, pc: UObject = pc) -> None:
            definition_data = item.DefinitionData
            definition_data.ManufacturerGradeIndex = mission_level
            definition_data.GameStage = mission_level
            definition_data = convert_struct(definition_data)

            if definition_data[0].Class.Name == "WeaponTypeDefinition":
                pc.GetPawnInventoryManager().ClientAddWeaponToBackpack(definition_data, 1)
            else:
                pc.GetPawnInventoryManager().ClientAddItemToBackpack(definition_data, 1, 1)

        for _ in range(bonuses):
            spawn_item(mission_dropper.location.item.pool, pc, loot_callback)

    return True


def _itemdef_make_repeatable(itemdef: UObject) -> bool:
    if not (itemdef and itemdef.MissionDirective):
        return False

    registry = MissionDefinition.Registrants(itemdef.MissionDirective)
    if not registry:
        return False
    
    for mission_dropper in registry:
        if not Tag.Excluded in mission_dropper.location.tags:
            break
    else:
        return False

    return mission_dropper.location.current_status in (
        Mission.Status.NotStarted, Mission.Status.Complete
    )


def _MissionDenyPickup(caller: UObject, function: UFunction, params: FStruct) -> bool:
    itemdef = caller.GetInventoryDefinition()
    if not _itemdef_make_repeatable(itemdef):
        return True

    # if get_missiontracker().GetMissionStatus(itemdef.MissionDirective) not in (0, 4):
    #     return True

    # Don't judge me; this is literally how the game does it.
    for pickup in FindAll("WillowPickup"):
        if pickup.Inventory and pickup.Inventory.GetInventoryDefinition() == itemdef:
            return True

    return False


def _PickupAssociated(caller: UObject, function: UFunction, params: FStruct) -> bool:
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

    reward_items: Sequence[UObject]
    reward_pools: Sequence[UObject]
    reward_xp_scale: int

    block_weapon: bool
    unlink_next: bool

    mission_weapon: UObject
    next_link: UObject
    repeatable: bool

    def __init__(self,
        path: str,
        block_weapon: bool = True,
        unlink_next: bool = False,
    ) -> None:
        self.block_weapon = block_weapon; self.unlink_next = unlink_next
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

        self.reward_xp_scale = self.reward.ExperienceRewardPercentage.BaseValueScaleConstant

        self.prepare_attributes()

    def disable(self) -> None:
        super().disable()

        self.reward.RewardItems = self.reward_items
        self.reward.RewardItemPools = self.reward_pools
        self.restore_xp()

        self.revert_attributes()

    def prepare_attributes(self) -> None:
        self.repeatable = self.uobject.bRepeatable

        if self.block_weapon:
            self.mission_weapon = self.uobject.MissionWeapon
            KeepAlive(self.mission_weapon)
            self.uobject.MissionWeapon = None

        if self.unlink_next:
            self.next_link = self.uobject.NextMissionInChain
            KeepAlive(self.next_link)
            self.uobject.NextMissionInChain = None

    def revert_attributes(self) -> None:
        if not Tag.Excluded in self.location.tags:
            self.uobject.bRepeatable = self.repeatable

        if self.block_weapon:
            self.uobject.MissionWeapon = self.mission_weapon

        if self.unlink_next:
            self.uobject.NextMissionInChain = self.next_link

    def remove_xp(self) -> None:
        self.reward.ExperienceRewardPercentage.BaseValueScaleConstant = 0

    def restore_xp(self) -> None:
        self.reward.ExperienceRewardPercentage.BaseValueScaleConstant = self.reward_xp_scale

    def make_repeatable(self) -> None:
        self.uobject.bRepeatable = True

    def revert_repeatable(self) -> None:
        self.uobject.bRepeatable = self.repeatable


class MissionDefinitionAlt(MissionDefinition):
    def __init__(self, path: str) -> None:
        super(MissionDefinition, self).__init__(path)

    @property
    def reward(self) -> FStruct:
        return self.uobject.AlternativeReward

    def prepare_attributes(self) -> None: pass
    def revert_attributes(self) -> None: pass
    def make_repeatable(self) -> None: pass
    def revert_repeatable(self) -> None: pass


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
        # TODO: tick until successful when client
        if spawner:
            spawner.SetPickupStatus(True)
            if spawner.MissionPickup:
                spawner.MissionPickup.SetPickupability(True)
                if not is_client():
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

    def apply(self) -> Optional[UObject]:
        giver = FindObject("MissionDirectivesDefinition", self.path)
        if not giver:
            return None

        missiondef = self.location.mission_definition.uobject

        matched_directive = False
        for directive in giver.MissionDirectives:
            if directive.MissionDefinition == missiondef:
                directive.bBeginsMission = self.begins
                directive.bEndsMission = self.ends
                matched_directive = True
                break

        if not matched_directive:
            directives = convert_struct(giver.MissionDirectives)
            directives.append((missiondef, self.begins, self.ends, 0))
            giver.MissionDirectives = directives

        if not is_client():
            get_missiontracker().RegisterMissionDirector(giver)
        return giver


class Mission(Location):
    mission_definition: MissionDefinition
    mission_definitions: Sequence[MissionDefinition]

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

        if not (self.tags & MissionTags):
            self.tags |= Tag.ShortMission
        if not (self.tags & ContentTags):
            self.tags |= Tag.BaseGame

        if not self.rarities:
            self.rarities = [100]
            if self.tags & Tag.LongMission:     self.rarities += (100,)
            if self.tags & Tag.VeryLongMission: self.rarities += (100,100,100)
            if self.tags & Tag.RaidEnemy:       self.rarities += (100,100,100)

        self.mission_definition, *_ = self.mission_definitions = tuple(
            dropper for dropper in self.droppers if isinstance(dropper, MissionDefinition)
        )

        if Tag.Excluded not in self.tags:
            self.mission_definition.make_repeatable()

    def disable(self) -> None:
        super().disable()
        if Tag.Excluded not in self.tags:
            self.mission_definition.revert_repeatable()

    @property
    def current_status(self) -> Status:
        status = get_missiontracker().GetMissionStatus(self.mission_definition.uobject)
        return Mission.Status(status)

    def __str__(self) -> str:
        return f"Mission: {self.name}"
