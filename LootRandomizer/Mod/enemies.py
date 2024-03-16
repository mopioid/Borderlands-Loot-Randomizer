from __future__ import annotations

from unrealsdk import Log  #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct #type: ignore

from . import defines, locations, missions, mission_list
from .defines import Tag

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

    for dropper in registry:
        if dropper.should_inject(caller):
            pools += [(pool, (1, None, None, 1)) for pool in dropper.prepare_pools()]
            break

    caller.ItemPoolList = pools

    caller.Weapon.bDropOnDeath = False
    for item in caller.EquippedItems:
        if item:
            item.bDropOnDeath = False

    return True


class Enemy(locations.Location):
    applied_tags: Tag = Tag(0)

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

        if not tags & defines.EnemyTags:
            tags |= Tag.UniqueEnemy

        if not rarities:
            rarities = []

            if tags & Tag.SlowEnemy:       rarities += (33,)
            if tags & Tag.MobFarm:         rarities += (3,)
            if tags & Tag.RareEnemy:       rarities += (33,)
            if tags & Tag.VeryRareEnemy:   rarities += (100,50,50)
            if tags & Tag.EvolvedEnemy:    rarities += (50,50)
            if tags & Tag.RaidEnemy:       rarities += (100,100,50,50)

            if tags & Tag.MissionEnemy:    rarities += (50,)
            if tags & Tag.LongMission:     rarities += (50,)
            if tags & Tag.VeryLongMission: rarities += (100,50)

            if not rarities:               rarities += (15,)

        super().__init__(name, *droppers, tags=tags, rarities=rarities)

    def apply_tags(self, tags: Tag) -> None:
        self.applied_tags = tags

    def __str__(self) -> str:
        return f"Enemy: {self.name}"


class Pawn(locations.Dropper):
    balance: str
    transform: Optional[int]
    evolved: Optional[int]

    def __init__(self,
        balance: str,
        *,
        transform: Optional[int] = None,
        evolved: Optional[int] = None
    ) -> None:
        self.balance = balance; self.transform = transform; self.evolved = evolved

        registry = balance_registry.setdefault(self.balance, set())
        registry.add(self)

        super().__init__()

    def should_inject(self, uobject: Optional[UObject] = None) -> bool:
        if uobject is None:
            raise ValueError(f"Pawn(\"{self.balance}\") for {self.location} asked to inject None")
        
        if not super().should_inject(uobject):
            return False

        if self.transform is not None:
            return self.transform == uobject.TransformType

        if self.evolved == uobject.TransformType:
            return Tag.EvolvedEnemy not in self.location.applied_tags

        return True
