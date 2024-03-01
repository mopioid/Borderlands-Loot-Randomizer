from __future__ import annotations

from unrealsdk import Log, GetEngine  #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct #type: ignore


from . import defines, locations, missions, mission_list
from .defines import Tag, construct_object

from typing import Dict, Optional, Set, Sequence


_enemy_tags = (
    Tag.UniqueEnemy     |
    Tag.SlowEnemy       |
    Tag.RareEnemy       |
    Tag.RaidEnemy       |
    Tag.MissionEnemy    |
    Tag.DigistructEnemy |
    Tag.EvolvedEnemy
)

_enemy_tag_rarities = {
    Tag.SlowEnemy:       (3,),
    Tag.RareEnemy:       (3,),
    Tag.VeryRareEnemy:   (1,2,2),
    Tag.EvolvedEnemy:    (2,3),
    Tag.MissionEnemy:    (5,),
    Tag.LongMission:     (2,),
    Tag.VeryLongMission: (1,2),
    Tag.RaidEnemy:       (1,1,2,2),
}

def Enable() -> None:
    RunHook("WillowGame.WillowAIPawn.Died", "LootRandomizer", _pawn_died)

def Disable() -> None:
    RemoveHook("WillowGame.WillowAIPawn.Died", "LootRandomizer")


aiclass_registry: Dict[str, Set[Pawn]] = dict()


def _pawn_died(caller: UObject, function: UFunction, params: FStruct) -> bool:
    aiclass = caller.BalanceDefinitionState.BalanceDefinition
    aiclass = UObject.PathName(aiclass).split(".")[-1]
    if not aiclass:
        return True
    
    registry = aiclass_registry.get(aiclass)
    if not registry:
        return True
    
    pools = [
        defines.convert_struct(pool) for pool in caller.ItemPoolList
        if pool.ItemPool and pool.ItemPool.Name in locations.pool_whitelist
    ]

    droppers = [dropper for dropper in registry if dropper.should_inject(caller)]
    inject_pools, revert_items = locations.prepare_dropper_pools(droppers)

    caller.ItemPoolList = pools + inject_pools

    defines.do_next_tick(revert_items)
    return True


class Pawn(locations.MapDropper):
    map_names = ()
    in_map = True
    transform: Optional[bool]

    def __init__(self, aiclass: str, transform: Optional[int] = None) -> None:
        self.aiclass = aiclass; self.transform = transform
        super().__init__()

    def register(self) -> None:
        super().register()
        registry = aiclass_registry.setdefault(self.aiclass, set())
        registry.add(self)

    def unregister(self) -> None:
        super().unregister()
        registry = aiclass_registry.get(self.aiclass)
        if registry:
            registry.discard(self)
            if not registry:
                del aiclass_registry[self.aiclass]

    def should_inject(self, pawn: UObject) -> bool:
        return self.transform is None or self.transform == pawn.TransformType


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
        if not tags & _enemy_tags:
            tags |= Tag.UniqueEnemy

        if rarities is None:
            rarities = list()
            for tag, tag_rarities in _enemy_tag_rarities.items():
                if tag & tags:
                    for rarity in tag_rarities:
                        rarities.append(rarity)

            if not len(rarities):
                rarities.append(10)

        super().__init__(name, *droppers, tags=tags, rarities=rarities)


class Leviathan(locations.MapDropper):
    map_names = ("Orchid_WormBelly_P",)

    def inject(self) -> None:
        def hook(caller: UObject, function: UFunction, params: FStruct) -> bool:
            if UObject.PathName(caller.MissionObjective) not in (
                # "GD_Orchid_SM_EndGameClone.M_Orchid_EndGame:KillBossWorm",
                "GD_Orchid_Plot_Mission09.M_Orchid_PlotMission09:KillBossWorm"
            ):
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
        
    def uninject(self) -> None:
        RemoveHook("WillowGame.Behavior_UpdateMissionObjective.ApplyBehaviorToContext", f"LootRandomizer.{id(self)}")


class MonsterTruck(locations.MapDropper):
    map_names = ("Iris_Hub2_P",)

    def inject(self) -> None:
        def hook(caller: UObject, function: UFunction, params: FStruct) -> bool:
            if not (caller.VehicleDef and caller.VehicleDef.Name == "Class_MonsterTruck_AIOnly"):
                return True

            spawner = construct_object("Behavior_SpawnLootAroundPoint")
            spawner.ItemPools = self.location.pools

            self.location.item.prepare()
            spawner.ApplyBehaviorToContext(caller, (), None, None, None, ())
            self.location.item.revert()

        RunHook("Engine.Pawn.Died", f"LootRandomizer.{id(self)}", hook)

    def uninject(self) -> None:
        RemoveHook("Engine.Pawn.Died", f"LootRandomizer.{id(self)}")


_mission_midgets: Set[str] = set()

midget_aiclasses = (
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
    "PawnBalance_LootMidget_Rat",
)

def _spawn_midget(caller: UObject, function: UFunction, params: FStruct) -> bool:
    if UObject.PathName(caller) in (
        "GD_Balance_Treasure.InteractiveObjectsTrap.MidgetHyperion.InteractiveObj_CardboardBox_MidgetHyperion:BehaviorProviderDefinition_1.Behavior_SpawnFromPopulationSystem_5",
    ):
        _mission_midgets.add(UObject.PathName(params.SpawnedActor))
    return True


class Midget(Pawn):
    def should_inject(self, pawn: UObject) -> bool:
        return super().should_inject(pawn) and (
            (UObject.PathName(pawn) not in _mission_midgets) and
            (UObject.PathName(pawn.MySpawnPoint) != "OldDust_Mission_Side.TheWorld:PersistentLevel.WillowPopulationPoint_26")
        )


class MissionMidget(Pawn):
    in_map = False

    def __init__(self, aiclass: str, map_name: str) -> None:
        super().__init__(aiclass)
        self.map_names = (map_name,)

    def should_inject(self, pawn: UObject) -> None:
        return super().should_inject(pawn) and self.in_map and (
            (UObject.PathName(pawn) in _mission_midgets) or
            (UObject.PathName(pawn.MySpawnPoint) == "OldDust_Mission_Side.TheWorld:PersistentLevel.WillowPopulationPoint_26")
        )

    def inject(self) -> None:
        pass


class MissionMidgetSource(locations.MapDropper):
    map_names = ("PandoraPark_P", "OldDust_P")

    def inject(self) -> None:
        _mission_midgets.clear()
        RunHook("WillowGame.Behavior_SpawnFromPopulationSystem.PublishBehaviorOutput", f"LootRandomizer.{id(self)}", _spawn_midget)

    def uninject(self) -> None:
        _mission_midgets.clear()
        RemoveHook("WillowGame.Behavior_SpawnFromPopulationSystem.PublishBehaviorOutput", f"LootRandomizer.{id(self)}")
