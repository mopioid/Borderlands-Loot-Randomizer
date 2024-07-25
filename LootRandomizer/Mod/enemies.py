from __future__ import annotations

from unrealsdk import Log, FindObject, GetEngine  #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct #type: ignore

from . import seed, defines, locations
from .missions import Mission
from .defines import Tag, construct_object, spawn_loot
from .locations import Dropper, Location, MapDropper, RegistrantDropper
from .items import ItemPool

from typing import Optional, Set, Sequence


def Enable() -> None:
    RunHook("WillowGame.WillowAIPawn.Died", "LootRandomizer", _pawn_died)

def Disable() -> None:
    RemoveHook("WillowGame.WillowAIPawn.Died", "LootRandomizer")


class Enemy(Location):
    mission: Optional[str]

    specified_tags: Tag
    specified_rarities: Optional[Sequence[int]]

    def __init__(
        self,
        name: str,
        *droppers: Dropper,
        tags: Tag = Tag(0),
        content: Tag = Tag(0),
        mission: Optional[str] = None,
        rarities: Optional[Sequence[int]] = None
    ) -> None:
        self.mission = mission
        self.specified_tags = tags
        self.specified_rarities = rarities
        super().__init__(name, *droppers, tags=tags, content=content, rarities=rarities)

    def enable(self) -> None:
        from . import catalog

        super().enable()

        tags = self.specified_tags
        rarities = self.specified_rarities

        if self.mission:
            tags |= Tag.MissionEnemy

            matched_mission: Optional[Mission] = None
            for location in catalog.Locations:
                if isinstance(location, Mission) and location.name == self.mission:
                    matched_mission = location
                    break

            if not matched_mission:
                raise ValueError(f"Failed to match mission {self.mission}")
            
            tags |= matched_mission.tags

        if not (tags & defines.EnemyTags):
            tags |= Tag.UniqueEnemy

        if not rarities:
            rarities = []

            if tags & Tag.SlowEnemy:       rarities += (33,)
            if tags & Tag.MobFarm:         rarities += (3,)
            if tags & Tag.RareEnemy:       rarities += (33,)
            if tags & Tag.VeryRareEnemy:   rarities += (100,50,50)
            if tags & Tag.EvolvedEnemy:    rarities += (50,50)
            if tags & Tag.RaidEnemy:       rarities += (100,100,100,50,50,50)

            if tags & Tag.MissionEnemy:    rarities += (50,)
            if tags & Tag.LongMission:     rarities += (50,)
            if tags & Tag.VeryLongMission: rarities += (100,50)

            if not rarities:               rarities += (15,)

        if not (tags in defines.ContentTags):
            tags |= Tag.BaseGame

        self.tags = tags; self.rarities = rarities


    def __str__(self) -> str:
        return f"Enemy: {self.name}"


class Pawn(RegistrantDropper):
    Registries = dict()

    balance: str
    transform: Optional[int]
    evolved: Optional[int]

    def __init__(self,
        *balance: str,
        transform: Optional[int] = None,
        evolved: Optional[int] = None
    ) -> None:
        self.transform = transform; self.evolved = evolved
        super().__init__(*balance)


    def should_inject(self, pawn: UObject) -> bool:
        if self.transform is not None:
            return self.transform == pawn.TransformType

        if self.evolved == pawn.TransformType:
            return not (seed.AppliedTags & Tag.EvolvedEnemy)

        return True


class Radio1340(MapDropper):
    def __init__(self) -> None:
        super().__init__("Sanctuary_P", "SanctuaryAir_P")

    def entered_map(self) -> None:
        def hook(caller: UObject, function: UFunction, params: FStruct) -> bool:
            if (not caller.InteractiveObjectDefinition) or caller.InteractiveObjectDefinition.Name != "IO_MoxieRadio":
                return True

            tracker = defines.get_missiontracker()
            objective = FindObject("MissionObjectiveDefinition", "GD_Z3_OutOfBody.M_OutOfBody:DestroyRadio")
            if not tracker.IsMissionObjectiveActive(objective):
                return True

            gamestage_region = FindObject("WillowRegionDefinition", "GD_GameStages.Zone1.Dam")
            _, level, _ = gamestage_region.GetRegionGameStage()

            caller.ManuallyBalanceToRegionDef = gamestage_region
            caller.ExpLevel = caller.GameStage = level

            spawn_loot(
                self.location.prepare_pools(),
                caller,
                (3539, 5261, 3703),
            )

            RemoveHook("WillowGame.WillowInteractiveObject.TakeDamage", f"LootRandomizer.{id(self)}")
            return True

        RunHook("WillowGame.WillowInteractiveObject.TakeDamage", f"LootRandomizer.{id(self)}", hook)

    def exited_map(self) -> None:
        RemoveHook("WillowGame.WillowInteractiveObject.TakeDamage", f"LootRandomizer.{id(self)}")


class Leviathan(MapDropper):
    def __init__(self) -> None:
        super().__init__("Orchid_WormBelly_P")

    def entered_map(self) -> None:
        def hook(caller: UObject, function: UFunction, params: FStruct) -> bool:
            if UObject.PathName(caller.MissionObjective) != "GD_Orchid_Plot_Mission09.M_Orchid_PlotMission09:KillBossWorm":
                return True

            pawn = GetEngine().GetCurrentWorldInfo().PawnList
            while pawn:
                if pawn.AIClass and pawn.AIClass.Name == "CharacterClass_Orchid_BossWorm":
                    break
                pawn = pawn.NextPawn

            spawn_loot(
                self.location.prepare_pools(),
                pawn,
                (1200, -66000, 3000),
                (-400, -1800, -400),
                200
            )
            return True

        RunHook("WillowGame.Behavior_UpdateMissionObjective.ApplyBehaviorToContext", f"LootRandomizer.{id(self)}", hook)
        
    def exited_map(self) -> None:
        RemoveHook("WillowGame.Behavior_UpdateMissionObjective.ApplyBehaviorToContext", f"LootRandomizer.{id(self)}")


class MonsterTruckDriver(Pawn):
    def should_inject(self, pawn: UObject) -> bool:
        if UObject.PathName(pawn.MySpawnPoint) != "Iris_Hub2_Combat.TheWorld:PersistentLevel.WillowPopulationPoint_52":
            return False
        pawn.DoesVehicleAllowMeToDropLoot = True
        return True


class PetesBurner(Pawn):
    def should_inject(self, pawn: UObject) -> bool:
        return (
            pawn.Allegiance.Name == "Iris_Allegiance_DragonGang"
            and locations.map_name == "Iris_DL2_P".casefold()
        )


_doctorsorders_midgets: Set[str] = set()

def _spawn_midget(caller: UObject, function: UFunction, params: FStruct) -> bool:
    if UObject.PathName(caller) == "GD_Balance_Treasure.InteractiveObjectsTrap.MidgetHyperion.InteractiveObj_CardboardBox_MidgetHyperion:BehaviorProviderDefinition_1.Behavior_SpawnFromPopulationSystem_5":
        _doctorsorders_midgets.add(UObject.PathName(params.SpawnedActor))
    return True


class Midget(Pawn):
    def should_inject(self, pawn: UObject) -> bool:
        return (
            (UObject.PathName(pawn) not in _doctorsorders_midgets) and
            (UObject.PathName(pawn.MySpawnPoint) != "OldDust_Mission_Side.TheWorld:PersistentLevel.WillowPopulationPoint_26")
        )


class DoctorsOrdersMidget(Pawn):
    def should_inject(self, pawn: UObject) -> bool:
        return UObject.PathName(pawn) in _doctorsorders_midgets


class SpaceCowboyMidget(Pawn):
    def should_inject(self, pawn: UObject) -> bool:
        return UObject.PathName(pawn.MySpawnPoint) == "OldDust_Mission_Side.TheWorld:PersistentLevel.WillowPopulationPoint_26"

class DoctorsOrdersMidgetRegistry(MapDropper):
    def __init__(self) -> None:
        super().__init__("PandoraPark_P")

    def entered_map(self) -> None:
        _doctorsorders_midgets.clear()
        RunHook("WillowGame.Behavior_SpawnFromPopulationSystem.PublishBehaviorOutput", f"LootRandomizer.{id(self)}", _spawn_midget)

    def exited_map(self) -> None:
        _doctorsorders_midgets.clear()
        RemoveHook("WillowGame.Behavior_SpawnFromPopulationSystem.PublishBehaviorOutput", f"LootRandomizer.{id(self)}")


class Haderax(MapDropper):
    def __init__(self, *map_names: str) -> None:
        super().__init__("SandwormLair_P")

    def entered_map(self) -> None:
        digicrate = FindObject("InteractiveObjectBalanceDefinition", "GD_Anemone_Lobelia_DahDigi.LootableGradesUnique.ObjectGrade_DalhEpicCrate_Digi")
        # digicrate_peakopener = FindObject("InteractiveObjectBalanceDefinition", "GD_Anemone_Lobelia_DahDigi.LootableGradesUnique.ObjectGrade_DalhEpicCrate_Digi_PeakOpener")
        digicrate_shield = FindObject("InteractiveObjectBalanceDefinition", "GD_Anemone_Lobelia_DahDigi.LootableGradesUnique.ObjectGrade_DalhEpicCrate_Digi_Shield")
        digicrate_artifact = FindObject("InteractiveObjectBalanceDefinition", "GD_Anemone_Lobelia_DahDigi.LootableGradesUnique.ObjectGrade_DalhEpicCrate_Digi_Articfact")

        digicrate.DefaultInteractiveObject = None
        # digicrate_peakopener.DefaultInteractiveObject = None
        digicrate_shield.DefaultInteractiveObject = None
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
        rarities: Optional[Sequence[int]] = None
    ) -> None:
        self.fallback = fallback
        super().__init__(name, *droppers, tags=tags, rarities=rarities)

    def enable(self) -> None:
        from . import catalog

        super().enable()

        for location in catalog.Locations:
            if isinstance(location, Enemy) and location.name == self.fallback:
                self.fallback_enemy = location

        if not self.fallback_enemy:
            raise Exception(f"Failed to find fallback enemy for {self}")

    @property
    def item(self) -> Optional[ItemPool]:
        return self._item if self._item else self.fallback_enemy.item

    @item.setter
    def item(self, item: ItemPool) -> None:
        self._item = item

    @property
    def hint_pool(self) -> UObject: #ItemPoolDefinition
        return super().hint_pool if self._item else self.fallback_enemy.hint_pool


def _pawn_died(caller: UObject, function: UFunction, params: FStruct) -> bool:
    balance = caller.BalanceDefinitionState.BalanceDefinition
    balance = UObject.PathName(balance).split(".")[-1]
    if not balance:
        return True
    
    registry = Pawn.Registries.get(balance)
    if not registry:
        return True
    
    pools = [
        defines.convert_struct(pool) for pool in caller.ItemPoolList
        if pool.ItemPool and pool.ItemPool.Name in locations.pool_whitelist
    ]

    for dropper in registry:
        if dropper.should_inject(caller):
            pools += [(pool, (1, None, None, 1)) for pool in dropper.location.prepare_pools()]
            break

    caller.ItemPoolList = pools

    if caller.Weapon:
        caller.Weapon.bDropOnDeath = False
    for item in caller.EquippedItems:
        if item:
            item.bDropOnDeath = False

    return True


"""
TODO:
    Fix leviathan's loot fling with smol items
    Radio #1340 can be damaged multiple times during objective
"""