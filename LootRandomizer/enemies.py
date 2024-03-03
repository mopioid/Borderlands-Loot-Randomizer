from __future__ import annotations

from unrealsdk import Log, GetEngine  #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct #type: ignore


from . import defines, locations, missions, mission_list
from .defines import Tag, construct_object

from typing import Dict, Optional, Set, Sequence


def Enable() -> None:
    RunHook("WillowGame.WillowAIPawn.Died", "LootRandomizer", _pawn_died)

def Disable() -> None:
    RemoveHook("WillowGame.WillowAIPawn.Died", "LootRandomizer")


balance_registry: Dict[str, Set[Pawn]] = dict()


def _pawn_died(caller: UObject, function: UFunction, params: FStruct) -> bool:
    balance = caller.BalanceDefinitionState.BalanceDefinition
    balance = UObject.PathName(balance).split(".")[-1]
    if not balance:
        return True
    
    registry = balance_registry.get(balance)
    if not registry:
        return True
    
    pools = [
        defines.convert_struct(pool) for pool in caller.ItemPoolList
        if pool.ItemPool and pool.ItemPool.Name in locations.pool_whitelist
    ]

    droppers = [dropper for dropper in registry if dropper.should_inject(caller)]
    inject_pools, revert_items = locations.prepare_dropper_pools(droppers)

    caller.ItemPoolList = pools + [(pool, (1, None, None, 1)) for pool in inject_pools]

    defines.do_next_tick(revert_items)
    return True


class Enemy(locations.Location):
    def __init__(
        self,
        name: str,
        *droppers: locations.Dropper,
        tags: Tag = Tag(0),
        mission: Optional[str] = None,
        rarities: Optional[Sequence[int]] = None
    ) -> None:
        if mission:
            tags |= Tag.MissionEnemy

            matched_mission: Optional[missions.Mission] = None
            for listed_mission in mission_list.Missions:
                if listed_mission.name == mission:
                    matched_mission = listed_mission
                    break

            if not matched_mission:
                raise ValueError(mission)
            
            tags |= matched_mission.tags

        if not tags & defines.ContentTags:
            tags |= Tag.BaseGame
        if not tags & defines.EnemyTags:
            tags |= Tag.UniqueEnemy

        if not rarities:
            rarities = []

            if   tags & Tag.SlowEnemy:       rarities += (3,)
            if   tags & Tag.RareEnemy:       rarities += (3,)
            if   tags & Tag.VeryRareEnemy:   rarities += (1,2,2)
            if   tags & Tag.EvolvedEnemy:    rarities += (2,3)
            if   tags & Tag.RaidEnemy:       rarities += (1,1,2,2)

            if   tags & Tag.LongMission:     rarities += (2,)
            elif tags & Tag.VeryLongMission: rarities += (1,2)
            elif tags & Tag.MissionEnemy:    rarities += (5,)

            if   not rarities:               rarities += (8,)

        super().__init__(name, *droppers, tags=tags, rarities=rarities)


class Pawn(locations.Dropper):
    transform: Optional[bool]

    def __init__(self, balance: str, transform: Optional[int] = None) -> None:
        self.balance = balance; self.transform = transform

        registry = balance_registry.setdefault(self.balance, set())
        registry.add(self)

        super().__init__()

    def should_inject(self, pawn: UObject) -> bool:
        return self.transform is None or self.transform == pawn.TransformType


class Leviathan(locations.MapDropper):
    map_names = ("Orchid_WormBelly_P",)

    def entered_map(self) -> None:
        def hook(caller: UObject, function: UFunction, params: FStruct) -> bool:
            if UObject.PathName(caller.MissionObjective) != "GD_Orchid_Plot_Mission09.M_Orchid_PlotMission09:KillBossWorm":
                return True

            pawn = GetEngine().GetCurrentWorldInfo().PawnList
            while pawn:
                if pawn.AIClass and pawn.AIClass.Name == "CharacterClass_Orchid_BossWorm":
                    break
                pawn = pawn.NextPawn

            spawner = construct_object("Behavior_SpawnLootAroundPoint")

            spawner.ItemPools = self.location.pools
            spawner.SpawnVelocity = (-400, -1800, -400)
            spawner.SpawnVelocityRelativeTo = 1
            spawner.CustomLocation = ((1200, -66000, 3000), None, "")
            spawner.CircularScatterRadius = 200

            self.location.item.prepare()
            spawner.ApplyBehaviorToContext(pawn, (), None, None, None, ())
            self.location.item.revert()

            return True

        RunHook("WillowGame.Behavior_UpdateMissionObjective.ApplyBehaviorToContext", f"LootRandomizer.{id(self)}", hook)
        
    def exited_map(self) -> None:
        RemoveHook("WillowGame.Behavior_UpdateMissionObjective.ApplyBehaviorToContext", f"LootRandomizer.{id(self)}")


class MonsterTruck(locations.MapDropper):
    map_names = ("Iris_Hub2_P",)

    def entered_map(self) -> None:
        def hook(caller: UObject, function: UFunction, params: FStruct) -> bool:
            if not (caller.VehicleDef and caller.VehicleDef.Name == "Class_MonsterTruck_AIOnly"):
                return True

            spawner = construct_object("Behavior_SpawnLootAroundPoint")
            spawner.ItemPools = self.location.pools

            self.location.item.prepare()
            spawner.ApplyBehaviorToContext(caller, (), None, None, None, ())
            self.location.item.revert()

        RunHook("Engine.Pawn.Died", f"LootRandomizer.{id(self)}", hook)

    def exited_map(self) -> None:
        RemoveHook("Engine.Pawn.Died", f"LootRandomizer.{id(self)}")


_doctorsorders_midgets: Set[str] = set()

def _spawn_midget(caller: UObject, function: UFunction, params: FStruct) -> bool:
    if UObject.PathName(caller) == "GD_Balance_Treasure.InteractiveObjectsTrap.MidgetHyperion.InteractiveObj_CardboardBox_MidgetHyperion:BehaviorProviderDefinition_1.Behavior_SpawnFromPopulationSystem_5":
        _doctorsorders_midgets.add(UObject.PathName(params.SpawnedActor))
    return True

class Midget(Pawn):
    def should_inject(self, pawn: UObject) -> bool:
        return (
            UObject.PathName(pawn) not in _doctorsorders_midgets and
            UObject.PathName(pawn.MySpawnPoint) != "OldDust_Mission_Side.TheWorld:PersistentLevel.WillowPopulationPoint_26"
        )

class DoctorsOrdersMidget(Pawn):
    def should_inject(self, pawn: UObject) -> None:
        return UObject.PathName(pawn) in _doctorsorders_midgets

class SpaceCowboyMidget(Pawn):
    def should_inject(self, pawn: UObject) -> None:
        return UObject.PathName(pawn.MySpawnPoint) == "OldDust_Mission_Side.TheWorld:PersistentLevel.WillowPopulationPoint_26"

class DoctorsOrdersMidgetRegistry(locations.MapDropper):
    map_names = ("PandoraPark_P",)

    def entered_map(self) -> None:
        _doctorsorders_midgets.clear()
        RunHook("WillowGame.Behavior_SpawnFromPopulationSystem.PublishBehaviorOutput", f"LootRandomizer.{id(self)}", _spawn_midget)

    def exited_map(self) -> None:
        _doctorsorders_midgets.clear()
        RemoveHook("WillowGame.Behavior_SpawnFromPopulationSystem.PublishBehaviorOutput", f"LootRandomizer.{id(self)}")
