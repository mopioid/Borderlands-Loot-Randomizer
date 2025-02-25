from __future__ import annotations

from unrealsdk import Log
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct

from .defines import *
from . import locations, seed
from .locations import Location, RegistrantDropper

from typing import Any, Optional, List, Set


def Enable() -> None:
    RunHook("WillowGame.WillowAIPawn.Died", "LootRandomizer", _pawn_died)


def Disable() -> None:
    RemoveHook("WillowGame.WillowAIPawn.Died", "LootRandomizer")


class Enemy(Location):
    default_rarity: int = 15

    def enable(self) -> None:
        super().enable()

        if not (self.tags & EnemyTags):
            self.tags |= Tag.UniqueEnemy

        if self.specified_rarities:
            return

        self.rarities = []

        if self.tags & Tag.SlowEnemy:
            self.rarities += (33,)
        if self.tags & Tag.MobFarm:
            self.rarities += (3,)
        if self.tags & Tag.RareEnemy:
            self.rarities += (33,)
        if self.tags & Tag.VeryRareEnemy:
            self.rarities += (100, 50, 50)
        if self.tags & Tag.Raid:
            self.rarities += (100, 100, 100, 50, 50, 50)
        if self.tags & getattr(Tag, "EvolvedEnemy", Tag.Excluded):
            self.rarities += (50, 50)

        if self.tags & Tag.MissionLocation:
            self.rarities += (50,)
        if self.tags & Tag.LongMission:
            self.rarities += (50,)
        if self.tags & Tag.VeryLongMission:
            self.rarities += (100, 50)

        if not len(self.rarities):
            self.rarities += (15,)

    def __str__(self) -> str:
        return f"Enemy: {self.name}"


class Pawn(RegistrantDropper):
    Registries = dict()

    balance: str
    transform: Optional[int]
    evolved: Optional[int]

    def __init__(
        self,
        *balance: str,
        transform: Optional[int] = None,
        evolved: Optional[int] = None,
    ) -> None:
        self.transform = transform
        self.evolved = evolved
        super().__init__(*balance)

    def should_inject(self, pawn: UObject) -> bool:
        if self.transform is not None:
            return self.transform == pawn.TransformType

        if self.evolved == pawn.TransformType:
            evolved_tag = getattr(Tag, "EvolvedEnemy", Tag.Excluded)
            return not (seed.AppliedTags & evolved_tag)

        return True

    def inject(self, pools: List[Any]) -> None:
        pools += [
            (pool, (1, None, None, 1))
            for pool in self.location.prepare_pools()
        ]


_dead_pawns: Set[UObject] = set()


def _pawn_died(caller: UObject, _f: UFunction, _p: FStruct) -> bool:
    balance: Optional[UObject]
    balance = caller.BalanceDefinitionState.BalanceDefinition
    if not balance:
        return True

    balance_name = UObject.PathName(balance).split(".")[-1]
    registry = Pawn.Registrants(balance_name)
    if not registry:
        return True

    if caller in _dead_pawns:
        return False

    _dead_pawns.add(caller)
    do_next_tick(lambda: _dead_pawns.remove(caller))

    pools = [
        convert_struct(pool)
        for pool in caller.ItemPoolList
        if pool.ItemPool and pool.ItemPool.Name in pool_whitelist
    ]

    for dropper in registry:
        if dropper.should_inject(caller):
            dropper.inject(pools)
            caller.DoesVehicleAllowMeToDropLoot = True
            break

    caller.ItemPoolList = pools

    if caller.Weapon:
        caller.Weapon.bDropOnDeath = False
    for item in caller.EquippedItems:
        if item:
            item.bDropOnDeath = False

    return True
