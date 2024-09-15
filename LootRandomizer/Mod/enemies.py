from __future__ import annotations

from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct

from .defines import *
from . import locations, seed
from .locations import Location, RegistrantDropper

from typing import Optional, Sequence


def Enable() -> None:
    RunHook("WillowGame.WillowAIPawn.Died", "LootRandomizer", _pawn_died)


def Disable() -> None:
    RemoveHook("WillowGame.WillowAIPawn.Died", "LootRandomizer")

class Enemy(Location):
    default_rarity: int = 15

    def enable(self) -> None:
        super().enable()

        # TODO: fix rarity assignments by tag

        if not (self.tags & EnemyTags):
            self.tags |= Tag.UniqueEnemy

        if self.specified_rarities:
            return

        rarities = list(self.rarities)

        if self.mission_name:
            rarities = [50] * len(rarities)

        if self.tags & Tag.SlowEnemy:
            rarities += (33,)
        if self.tags & Tag.MobFarm:
            rarities += (3,)
        if self.tags & Tag.RareEnemy:
            rarities = (33,)
            if self.mission_name:
                rarities *= 2
        if self.tags & Tag.VeryRareEnemy:
            rarities = (100, 50, 50)
            if self.mission_name:
                rarities *= 3
        if self.tags & Tag.EvolvedEnemy:
            rarities = (50, 50)
            if self.mission_name:
                rarities *= 2
        if self.tags & Tag.RaidEnemy:
            rarities += (100, 100, 100, 50, 50, 50)

        self.rarities = rarities

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
            return not (seed.AppliedTags & Tag.EvolvedEnemy)

        return True


def _pawn_died(caller: UObject, _f: UFunction, params: FStruct) -> bool:
    balance: Optional[UObject] = (
        caller.BalanceDefinitionState.BalanceDefinition
    )
    if not balance:
        return True

    balance_name = UObject.PathName(balance).split(".")[-1]
    registry = Pawn.Registrants(balance_name)
    if not registry:
        return True

    caller.DoesVehicleAllowMeToDropLoot = True

    pools = [
        convert_struct(pool)
        for pool in caller.ItemPoolList
        if pool.ItemPool and pool.ItemPool.Name in locations.pool_whitelist
    ]

    for dropper in registry:
        if dropper.should_inject(caller):
            pools += [
                (pool, (1, None, None, 1))
                for pool in dropper.location.prepare_pools()
            ]
            break

    caller.ItemPoolList = pools

    if caller.Weapon:
        caller.Weapon.bDropOnDeath = False
    for item in caller.EquippedItems:
        if item:
            item.bDropOnDeath = False

    return True
