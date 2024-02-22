from __future__ import annotations

from unrealsdk import Log, GetEngine, FindAll, FindClass, FindObject  #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct  #type: ignore

from .. import options, hints
from ..options import Tag, BalancedItem, Probability
from ..items import ItemPool

from typing import Dict, List, Optional, Sequence, Set, Tuple


Locations: Sequence[Location] = ()


path_registries: Dict[str, Dict[str, PathDropper]] = dict()

map_name: str = "menumap"
map_registry: Dict[str, Set[MapDropper]] = dict()

modified_pools: Dict[str, List[BalancedItem]] = dict()


class Location:
    name: str
    droppers: Sequence[Dropper] = ()
    tags: Tag

    item: ItemPool

    def __init__(self, name: str, *droppers: Dropper, tags: Tag) -> None:
        self.name = name; self.droppers = droppers; self.tags = tags
        for dropper in droppers:
            dropper.location = self # This is a circular reference; Location objects are static.

    def apply(self, item: ItemPool) -> None:
        self.item = item
        for dropper in self.droppers:
            dropper.register()

    def revert(self) -> None:
        del self.item
        for dropper in self.droppers:
            dropper.unregister()

    def get_hint(self) -> UObject: #InventoryBalanceDefinition
        hint = hints.ConstructInventory(self.name)
        hint.InventoryDefinition.Presentation = self.item.get_hint()
        return hint

    def get_pools(self) -> Sequence[UObject]: #ItemPoolDefinition
        return (self.item.uobject,)


class Dropper:
    location: Location

    def register(self) -> None:
        pass

    def unregister(self) -> None:
        pass


class MapDropper(Dropper):
    map_name: str

    def register(self) -> None:
        registry = map_registry.setdefault(self.map_name, set())
        registry.add(self)

    def unregister(self) -> None:
        registry = map_registry.get(self.map_name)
        if registry:
            registry.discard(self)
            if not registry:
                del map_registry[self.map_name]

    def inject(self) -> None:
        raise NotImplementedError

    def uninject(self) -> None:
        pass


class PathDropper(Dropper):
    registry_class: str
    registry_path:  str

    def register(self) -> None:
        registry = path_registries.setdefault(self.registry_class, dict())
        registry[self.registry_path] = self

    def unregister(self) -> None:
        registry = path_registries.get(self.registry_class)
        if registry and registry.get(self.registry_path):
            del registry[self.registry_path]
            if not registry:
                del path_registries[self.registry_class]

    def inject(self, uobject: UObject) -> None:
        raise NotImplementedError
    

class Behavior(PathDropper):
    registry_class: str = "Behavior_SpawnItems"

    mode: Optional[bool]
    block_included: bool

    def __init__(
        self,
        path: str,
        mode: Optional[bool] = None,
        block_included: bool = False
    ) -> None:
        self.registry_path = path
        self.mode = mode
        self.block_included = block_included

    def inject(self, uobject: UObject = None) -> None:
        if self.mode is True:
            uobject.ItemPoolList = [(pool, (1, None, None, 1)) for pool in self.location.get_pools()]
        elif self.mode is False:
            uobject.ItemPoolList = ()

        if self.block_included:
            uobject.ItemPoolIncludedLists = ()



def MapChanged(new_map_name: str) -> None:
    global map_name
    for map_dropper in map_registry.get(map_name, ()):
        map_dropper.uninject()
    
    map_name = new_map_name
    for map_dropper in map_registry.get(map_name, ()):
        map_dropper.inject()

    for class_name, registry in path_registries.items():
        for uobject in FindAll(class_name):
            path_dropper = registry.get(UObject.PathName(uobject))
            if path_dropper:
                path_dropper.inject(uobject)



def _PostCommitMapChange(caller: UObject, function: UFunction, params: FStruct) -> bool:
    MapChanged(GetEngine().GetCurrentWorldInfo().GetMapName())
    return True


def _InitGame(caller: UObject, function: UFunction, params: FStruct) -> bool:
    if params.MapName == "MenuMap":
        MapChanged("menumap")
    return True


def Enable() -> None:
    missions.Enable()
    RunHook("Engine.GameInfo.PostCommitMapChange", "LootRandomizer", _PostCommitMapChange)
    RunHook("Engine.GameInfo.SetGameType", "LootRandomizer", _InitGame)


def Disable() -> None:
    Revert()
    missions.Disable()
    RemoveHook("Engine.GameInfo.PostCommitMapChange", "LootRandomizer")
    RemoveHook("Engine.GameInfo.SetGameType", "LootRandomizer")


def Apply() -> None:
    Revert()

    global Locations
    Locations = (
        *(location for location in  enemies.Locations if location.tags in options.SelectedTags),
        *(location for location in missions.Locations if location.tags in options.SelectedTags)
    )


def Revert() -> None:
    global Locations, modified_pools
    for location in Locations:
        location.revert()
    Locations = ()

    for path, balanced_items in modified_pools.items():
        pool = FindObject("ItemPoolDefinition", path)
        if pool:
            pool.BalancedItems = balanced_items
    modified_pools = dict()


from . import enemies, missions



"""
- shuffle mission weapons?

- Mammaril

- Snowman head
    GD_Episode07Data.WeaponPools.Pool_Weapons_Ep7_FireGuns
    GD_Episode07Data.BalanceDefs.BD_Ep7_SnowManHead_Ammo

- Gwen's head box
    GD_EasterEggs.WeaponPools.Pool_Weapons_Gwen_Unique

- Lascaux
    Env_IceCanyon.WeaponPools.Pool_Weapon_CaveGun

- Moonshiner 

- Scarlet Caravan
    GD_Orchid_PlotDataMission04.Mission04.Balance_Orchid_CaravanChest

- tipping moxxi
- thumpson pile
- mimic chests + mimic

"""



"""Gwen's Head Box"""
# def CreatePopulationActor(caller: UObject, function: UFunction, params: FStruct) -> bool:
#     if caller.ObjectBalanceDefinition.Name != "ObjectGrade_WhatsInTheBox":
#         return True
    
#     caller.ObjectBalanceDefinition.DefaultLoot[0].ItemAttachments[0].ItemPool = FindObject("ItemPoolDefinition", "GD_Itempools.Runnables.Pool_Talos")
#     return True

# RemoveHook("WillowGame.PopulationFactoryInteractiveObject.CreatePopulationActor", "Test")
# RunHook("WillowGame.PopulationFactoryInteractiveObject.CreatePopulationActor", "Test", CreatePopulationActor)
