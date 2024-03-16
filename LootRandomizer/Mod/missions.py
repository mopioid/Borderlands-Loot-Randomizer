from __future__ import annotations

from unrealsdk import Log, FindObject, FindAll, GetEngine, KeepAlive #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct #type: ignore

from . import defines, locations
from .defines import Tag

from typing import Dict, List, Optional, Set


_mission_registry: Dict[str, Set[Mission]] = dict()
_missioninv_registry: Dict[str, MissionInventory] = dict()
_behaviordestroy_registry: Set[str] = set()


def Enable() -> None:
    RunHook("WillowGame.QuestAcceptGFxMovie.GetRewardPresentations", "LootRandomizer", lambda c,f,p: False)
    RunHook("WillowGame.StatusMenuExGFxMovie.GetRewardPresentations", "LootRandomizer", lambda c,f,p: False)
    RunHook("WillowGame.WillowPlayerController.TryPromptForFastForward", "LootRandomizer", lambda c,f,p: False)

    RunHook("WillowGame.WillowPlayerController.AcceptMission", "LootRandomizer", _AcceptMission)
    RunHook("WillowGame.WillowPlayerController.ServerCompleteMission", "LootRandomizer", _CompleteMission)

    RunHook("WillowGame.WillowMissionItem.MissionDenyPickup", "LootRandomizer", _MissionDenyPickup)
    RunHook("Engine.WillowInventory.PickupAssociated", "LootRandomizer", _PickupAssociated)
    RunHook("Engine.Behavior_Destroy.ApplyBehaviorToContext", "LootRandomizer", _Behavior_Destroy)


def Disable() -> None:
    RemoveHook("WillowGame.QuestAcceptGFxMovie.GetRewardPresentations", "LootRandomizer")
    RemoveHook("WillowGame.StatusMenuExGFxMovie.GetRewardPresentations", "LootRandomizer")
    RemoveHook("WillowGame.WillowPlayerController.TryPromptForFastForward", "LootRandomizer")

    RemoveHook("WillowGame.WillowPlayerController.AcceptMission", "LootRandomizer")
    RemoveHook("WillowGame.WillowPlayerController.ServerCompleteMission", "LootRandomizer")

    RemoveHook("Engine.WillowInventory.PickupAssociated", "LootRandomizer")
    RemoveHook("WillowGame.WillowMissionItem.MissionDenyPickup", "LootRandomizer")
    RemoveHook("Engine.Behavior_Destroy.ApplyBehaviorToContext", "LootRandomizer")


def get_tracker() -> UObject:
    return GetEngine().GetCurrentWorldInfo().GRI.MissionTracker


def _AcceptMission(caller: UObject, function: UFunction, params: FStruct) -> bool:
    missiondef = params.Mission
    registry = _mission_registry.get(UObject.PathName(missiondef))
    if not registry:
        return True

    tracker = get_tracker()

    for mission in registry:
        if tracker.GetMissionStatus(missiondef) == 4:
            mission.reward.ExperienceRewardPercentage.BaseValueScaleConstant = 0

    def play_kickoff(tracker=tracker, missiondef=missiondef):
        tracker.PlayKickoff(missiondef)
        tracker.SetKickoffHeard(missiondef)

    delegates = (dropper.accepted for dropper in mission.droppers if isinstance(dropper, MissionStatusDelegate))
    defines.do_next_tick(play_kickoff, *delegates)
    return True


def _CompleteMission(caller: UObject, function: UFunction, params: FStruct) -> bool:
    missiondef = params.Mission
    registry = _mission_registry.get(UObject.PathName(missiondef))
    if not registry:
        return True

    playthrough = caller.GetCurrentPlaythrough()
    mission_index = caller.NativeGetMissionIndex(missiondef)
    mission_data = caller.MissionPlaythroughs[playthrough].MissionList[mission_index]
    mission_level = mission_data.GameStage
    alt_reward, _ = missiondef.ShouldGrantAlternateReward(list(mission_data.ObjectivesProgress))

    for mission in registry:
        delegates = (dropper.completed for dropper in mission.droppers if isinstance(dropper, MissionStatusDelegate))
        if not mission.item:
            if delegates:
                defines.do_next_tick(*delegates)
            return True

        if mission.alt == alt_reward:
            mission.item.prepare()
            mission.reward.RewardItemPools = (mission.item.pool,)

            for pri in GetEngine().GetCurrentWorldInfo().GRI.PRIArray:
                pc = pri.Owner

                bonuses = len(mission.rarities)
                if pc is defines.get_pc() or mission.reward.ExperienceRewardPercentage.BaseValueScaleConstant != 0:
                    bonuses -= 1

                if not bonuses:
                    continue

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

            def post_complete(mission=mission, delegates=delegates) -> None:
                mission.reward.RewardItemPools = ()
                mission.item.revert()

            defines.do_next_tick(post_complete, *delegates)
        mission.reward.ExperienceRewardPercentage.BaseValueScaleConstant = 0

    return True


def _MissionDenyPickup(caller: UObject, function: UFunction, params: FStruct) -> bool:
    itemdef = caller.GetInventoryDefinition()
    if not itemdef:
        return True

    missioninv = _missioninv_registry.get(UObject.PathName(itemdef))
    if not missioninv:
        return True

    if get_tracker().GetMissionStatus(missioninv.location.uobject) not in (0, 4):
        return True

    # Don't judge me; this is literally how the game does it.
    for pickup in FindAll("WillowPickup"):
        if pickup.Inventory and pickup.Inventory.GetInventoryDefinition() == itemdef:
            return True

    return False


def _PickupAssociated(caller: UObject, function: UFunction, params: FStruct) -> bool:
    itemdef = caller.GetInventoryDefinition()
    if not (itemdef and UObject.PathName(itemdef) in _missioninv_registry):
        return True
    
    def enable_pickup(pickup = params.Pickup):
        pickup.SetPickupability(True)
        GetEngine().GetCurrentWorldInfo().GRI.MissionTracker.RegisterMissionDirector(pickup)
    defines.do_next_tick(enable_pickup)
    return True


def _Behavior_Destroy(caller: UObject, function: UFunction, params: FStruct) -> bool:
    return UObject.PathName(caller) not in _behaviordestroy_registry


class PreventDestroy(locations.Dropper):
    path: str
    def __init__(self, path) -> None:
        self.path = path
        _behaviordestroy_registry.add(path)


class Mission(locations.Location):
    path: str
    alt: bool
    block_weapon: bool

    uobject: UObject

    repeatable: bool
    mission_weapon: UObject

    reward_items: List[UObject]
    reward_pools: List[UObject]
    reward_xp_scale: Optional[int] = None

    def __init__(
        self,
        name: str,
        path: str,
        *droppers: locations.Dropper,
        alt: bool = False,
        block_weapon: bool = False,
        tags=Tag.BaseGame|Tag.ShortMission
    ) -> None:
        self.path = path; self.alt = alt; self.block_weapon = block_weapon

        if not tags & (defines.MissionTags | Tag.RaidEnemy):
            tags |= Tag.ShortMission

        rarities: List[int] = [100]

        if   tags & Tag.LongMission:     rarities += (100,)
        elif tags & Tag.VeryLongMission: rarities += (100,100)
        if   tags & Tag.RaidEnemy:       rarities += (100,100)

        registry = _mission_registry.setdefault(path, set())
        registry.add(self)

        super().__init__(name, *droppers, tags=tags, rarities=rarities)

    @property
    def reward(self) -> FStruct:
        return self.uobject.AlternativeReward if self.alt else self.uobject.Reward

    def enable(self) -> None:
        for dropper in self.droppers:
            dropper.enable()

        self.uobject = FindObject("MissionDefinition", self.path)

        if not self.alt:
            self.repeatable = self.uobject.bRepeatable
            self.uobject.bRepeatable = True

        self.reward_items = tuple(self.reward.RewardItems)
        for item in self.reward_items:
            KeepAlive(item)
        self.reward.RewardItems = ()

        self.reward_pools = tuple(self.reward.RewardItemPools)
        for pool in self.reward_pools:
            KeepAlive(pool)
        self.reward.RewardItemPools = ()

        self.reward_xp_scale = self.reward.ExperienceRewardPercentage.BaseValueScaleConstant

        if self.block_weapon:
            self.mission_weapon = self.uobject.MissionWeapon
            KeepAlive(self.mission_weapon)
            self.uobject.MissionWeapon = None

    def disable(self) -> None:
        for dropper in self.droppers:
            dropper.disable()

        if not self.alt:
            self.uobject.bRepeatable = self.repeatable

        self.reward.RewardItems = self.reward_items
        self.reward.RewardItemPools = self.reward_pools
        self.reward.ExperienceRewardPercentage.BaseValueScaleConstant = self.reward_xp_scale

        if self.block_weapon:
            self.uobject.MissionWeapon = self.mission_weapon

    def __str__(self) -> str:
        return f"Mission: {self.name}"


class MissionInventory(locations.Dropper):
    path: str
    def __init__(self, path: str) -> None:
        self.path = path
        _missioninv_registry[path] = self


class MissionStatusDelegate:
    def accepted(self) -> None:
        pass

    def completed(self) -> None:
        pass


class MissionObject(locations.MapDropper, MissionStatusDelegate):
    path: str

    def __init__(self, path: str, *map_names: str) -> None:
        self.path = path
        super().__init__(*map_names)

    def apply(self) -> UObject:
        obj = FindObject("WillowInteractiveObject", self.path)
        obj.SetUsability(True, 0)
        obj.SetMissionDirectivesUsability(1)
        get_tracker().RegisterMissionDirector(obj)
        return obj
    
    def entered_map(self) -> None:
        if get_tracker().GetMissionStatus(self.location.uobject) != 0:
            self.apply()

    def completed(self) -> None:
        self.apply()


class MissionPickup(MissionObject):
    def apply(self) -> UObject:
        spawner = FindObject("WillowMissionPickupSpawner", self.path)
        spawner.SetPickupStatus(True)
        spawner.MissionPickup.SetPickupability(True)
        get_tracker().RegisterMissionDirector(spawner.MissionPickup)
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

        get_tracker().RegisterMissionDirector(giver)
        return giver
