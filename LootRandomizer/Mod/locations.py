from __future__ import annotations

from unrealsdk import Log, FindAll, FindObject, GetEngine, KeepAlive  #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct  #type: ignore

from . import defines, options, hints, items, seed
from .defines import Tag, construct_object, get_pc
from .items import ItemPool

import random

from typing import Dict, List, Optional, Sequence, Set, TypeVar
try: from typing import Self
except: pass


pool_whitelist = (
    "Pool_Ammo_All_DropAlways", "Pool_Ammo_All_Emergency", "Pool_Ammo_All_NeedOnly", "Pool_Ammo_Grenades_BoomBoom", "Pool_Health_All",
    "Pool_Eridium_Bar", "Pool_Eridium_Stick", "Pool_Money", "Pool_Money_1_BIG", "Pool_Money_1or2",
    "Pool_Orchid_SeraphCrystals", "Pool_Iris_SeraphCrystals", "Pool_Sage_SeraphCrystals", "Pool_Aster_SeraphCrystals",
    "ItemPool_TorgueToken_Qty10", "ItemPool_TorgueToken_Qty100", "ItemPool_TorgueToken_Qty15", "ItemPool_TorgueToken_Qty25", "ItemPool_TorgueToken_Qty3", "ItemPool_TorgueToken_Qty5", "ItemPool_TorgueToken_Qty50", "ItemPool_TorgueToken_Qty7", "ItemPool_TorgueToken_Qty75", "ItemPool_TorgueToken_Single",
    "ItemPool_MoxxiPicture",
    # "Pool_EpicChest_Weapons_GunsAndGear", "Pool_ClassMod_02_Uncommon", "Pool_ClassMod_04_Rare", "Pool_ClassMod_05_VeryRare", "Pool_ClassMod_06_Legendary", "Pool_GrenadeMods_02_Uncommon", "Pool_GrenadeMods_04_Rare", "Pool_GrenadeMods_05_VeryRare", "Pool_GrenadeMods_06_Legendary", "Pool_GunsAndGear", "Pool_GunsAndGear_02_Uncommon", "Pool_GunsAndGear_02_UncommonsRaid", "Pool_GunsAndGear_04_Rare", "Pool_GunsAndGear_05_VeryRare", "Pool_GunsAndGearDropNumPlayersPlusOne", "Pool_Shields_All_02_Uncommon", "Pool_Shields_All_04_Rare", "Pool_Shields_All_05_VeryRare", "Pool_Shields_All_06_Legendary", "Pool_VehicleSkins_All", "Pool_Weapons_All", "Pool_Weapons_All_02_Uncommon", "Pool_Weapons_All_04_Rare", "Pool_Weapons_All_05_VeryRare", "Pool_Weapons_All_06_Legendary",
)


def Enable() -> None:
    # RunHook("Engine.GameInfo.PostCommitMapChange", "LootRandomizer", _PostCommitMapChange)
    RunHook("Engine.GameInfo.SetGameType", "LootRandomizer", _InitGame)
    RunHook("WillowGame.Behavior_SpawnItems.ApplyBehaviorToContext", "LootRandomizer", _Behavior_SpawnItems)
    RunHook("WillowGame.WillowPlayerController.ClientSetPawnLocation", "LootRandomizer", _SetPawnLocation)
    RunHook("Engine.Behavior_Destroy.ApplyBehaviorToContext", "LootRandomizer", _Behavior_Destroy)


def Disable() -> None:
    # RemoveHook("Engine.GameInfo.PostCommitMapChange", "LootRandomizer")
    RemoveHook("Engine.GameInfo.SetGameType", "LootRandomizer")
    RemoveHook("WillowGame.Behavior_SpawnItems.ApplyBehaviorToContext", "LootRandomizer")
    RemoveHook("WillowGame.WillowPlayerController.ClientSetPawnLocation", "LootRandomizer")
    RemoveHook("Engine.Behavior_Destroy.ApplyBehaviorToContext", "LootRandomizer")


class Location:
    name: str
    droppers: Sequence[Dropper]
    tags: Tag
    content: Tag

    item: Optional[ItemPool] = None

    _rarities: Sequence[int]
    _hint_pool: Optional[UObject] = None

    def __init__(
        self,
        name: str,
        *droppers: Dropper,
        tags: Tag,
        content: Tag = Tag(0),
        rarities: Optional[Sequence[int]] = None
    ) -> None:
        for dropper in droppers:
            dropper.location = self # This is a circular reference; Location objects are static.

        if not (tags & defines.ContentTags):
            tags |= Tag.BaseGame

        if rarities is None:
            rarities = (100,)

        self.content = content if content else (tags & defines.ContentTags)

        self.name = name; self.droppers = droppers; self.tags = tags; self._rarities = rarities


    @property
    def rarities(self) -> Sequence[int]:
        return (0,) if self.item is items.DudItem else self._rarities
    
    @rarities.setter
    def rarities(self, rarities: Sequence[int]) -> None:
        self._rarities = rarities

    @property
    def hint_pool(self) -> UObject: #ItemPoolDefinition
        if not self._hint_pool:
            hint_inventory = construct_object(hints.inventory_template, "InvBal_Hint_" + self.name)

            useitem = construct_object(hints.useitem_template, hint_inventory)
            hint_inventory.InventoryDefinition = useitem
            defines.set_command(useitem, "ItemName", self.name)
            
            useitem.CustomPresentations = (construct_object(hints.custompresentation_template, useitem),)
            useitem.Presentation = construct_object(hints.presentation_template, useitem)

            self._hint_pool = construct_object("ItemPoolDefinition", "Pool_Hint_" + self.name)
            self._hint_pool.bAutoReadyItems = False
            self._hint_pool.BalancedItems = ((None, hint_inventory, (1, None, None, 1), True),)

            self.update_hint()
            self.toggle_hint(True)

        return self._hint_pool

    @property
    def hint_inventory(self) -> Optional[UObject]: #InventoryBalanceDefinition
        return self.hint_pool.BalancedItems[0].InvBalanceDefinition if self._hint_pool else None

    def update_hint(self) -> None:
        if not (self.hint_inventory and self.item):
            return

        useitem = self.hint_inventory.InventoryDefinition

        if self.item == items.DudItem:
            useitem.NonCompositeStaticMesh = hints.duditem_mesh
            useitem.PickupFlagIcon = hints.duditem_pickupflag

            hint_caption = "&nbsp;"
            hint_text = self.item.hint.formatter(random.choice(hints.DudDescriptions))
        else:
            useitem.NonCompositeStaticMesh = hints.hintitem_mesh
            useitem.PickupFlagIcon = hints.hintitem_pickupflag

            if options.HintDisplay.CurrentValue == "None":
                hint_caption = "&nbsp;"
                hint_text = "?"
            if options.HintDisplay.CurrentValue == "Vague":
                hint_caption = "Item Hint"
                hint_text = self.item.hint.formatter(self.item.hint)
            if options.HintDisplay.CurrentValue == "Spoiler":
                hint_caption = "Item Spoiler"
                hint_text = self.item.hint.formatter(self.item.name)

        defines.set_command(useitem.Presentation, "DescriptionLocReference", hint_caption)
        defines.set_command(useitem.CustomPresentations[0], "Description", hint_text)


    def toggle_hint(self, set_enabled: bool):
        if self.hint_inventory:
            self.hint_inventory.InventoryDefinition.PickupLifeSpan = 0 if set_enabled else 0.000001

    def prepare_pools(self, count: Optional[int] = None, pad: bool = True) -> Sequence[UObject]:
        padding = hints.padding_pool if pad else None

        if count is None:
            count = len(self.rarities)
        if not count:
            return ()

        if not self.item:
            return (padding,) * count

        if self.item is items.DudItem:
            if seed.AppliedSeed:
                seed.AppliedSeed.update_tracker(self, True)
            return (self.hint_pool,) * count

        self.item.prepare()

        pools: List[UObject] = []
        hint_seen = False
        item_seen = False

        for index in range(count):
            if index >= len(self.rarities):
                pools.append(padding)
            elif random.randint(1, 100) <= self.rarities[index]:
                pools.append(self.item.pool)
                item_seen = True
            else:
                pools.append(self.hint_pool)
                hint_seen = True

        if seed.AppliedSeed:
            if item_seen:
                seed.AppliedSeed.update_tracker(self, True)
            elif hint_seen:
                seed.AppliedSeed.update_tracker(self, False)
        
        random.shuffle(pools)
        return pools
    
    def enable(self) -> None:
        for dropper in self.droppers:
            dropper.enable()

    def disable(self) -> None:
        for dropper in self.droppers:
            dropper.disable()

    def __str__(self) -> str:
        raise NotImplementedError


class Dropper:
    location: Location

    def enable(self) -> None:
        pass

    def disable(self) -> None:
        pass


class RegistrantDropper(Dropper):
    Registries: Dict[str, Set[Self]]

    paths: Sequence[str]

    def __init__(self, *paths: str) -> None:
        self.paths = paths

    def enable(self) -> None:
        for path in self.paths:
            registry = self.Registries.setdefault(path, set())
            registry.add(self) #type: ignore

    def disable(self) -> None:
        for path in self.paths:
            registry = self.Registries.get(path)
            if registry:
                registry.discard(self) #type: ignore
                if not registry:
                    del self.Registries[path]


class MapDropper(RegistrantDropper):
    Registries = dict()

    def __init__(self, *map_names: str) -> None:
        super().__init__(*(map_name.casefold() for map_name in map_names))

    def entered_map(self) -> None:
        raise NotImplementedError

    def exited_map(self) -> None:
        pass


class Behavior(RegistrantDropper):
    Registries = dict()

    inject: bool

    def __init__(self, *paths: str, inject: bool = True) -> None:
        self.inject = inject
        super().__init__(*paths)


class PreventDestroy(RegistrantDropper):
    Registries = dict()


map_name: str = "menumap"

def MapChanged(new_map_name: str) -> None:
    global map_name

    for map_dropper in MapDropper.Registries.get(map_name, ()):
        map_dropper.exited_map()
    
    map_name = new_map_name
    for map_dropper in MapDropper.Registries.get(map_name, ()):
        map_dropper.entered_map()


# def _PostCommitMapChange(caller: UObject, function: UFunction, params: FStruct) -> bool:
#     return True

def _SetPawnLocation(caller: UObject, function: UFunction, params: FStruct) -> bool:
    new_map_name = str(GetEngine().GetCurrentWorldInfo().GetMapName()).casefold()
    if new_map_name == map_name:
        return True

    def wait_missiontracker() -> bool:
        if get_pc().WorldInfo.GRI and get_pc().WorldInfo.GRI.MissionTracker:
            MapChanged(new_map_name)
            return False
        return True
    defines.tick_while(wait_missiontracker)

    return True


def _InitGame(caller: UObject, function: UFunction, params: FStruct) -> bool:
    if params.MapName == "MenuMap":
        MapChanged("menumap")
    return True


def _Behavior_SpawnItems(caller: UObject, function: UFunction, params: FStruct) -> bool:
    registry = Behavior.Registries.get(UObject.PathName(caller))
    if not registry:
        return True
    
    original_poollist = defines.convert_struct(tuple(caller.ItemPoolList))
    poollist = [pool for pool in original_poollist if pool[0] and pool[0].Name in pool_whitelist]

    for dropper in registry:
        if dropper.inject:
            poollist += [(pool, (1, None, None, 1)) for pool in dropper.location.prepare_pools()]
            break

    caller.ItemPoolList = poollist

    cleaned_poollistdefs = dict()
    def clean_poollistdef(poollistdef: UObject) -> None:
        if not poollistdef:
            return

        for nested_itempoollistdef in poollistdef.ItemPoolIncludedLists:
            clean_poollistdef(nested_itempoollistdef)

        if poollistdef not in cleaned_poollistdefs:
            pools = defines.convert_struct(tuple(poollistdef.ItemPools))
            cleaned_poollistdefs[poollistdef] = pools
            poollistdef.ItemPools = [
                pool for pool in pools
                if pool[0] and pool[0].Name in pool_whitelist
            ]

    for poollistdef in caller.ItemPoolIncludedLists:
        clean_poollistdef(poollistdef)

    def revert_pools(original_poollist=original_poollist, cleaned_poollistdefs=cleaned_poollistdefs) -> None:
        caller.ItemPoolList = original_poollist
        for itempoollistdef, pools in cleaned_poollistdefs.items():
            itempoollistdef.ItemPools = pools

    defines.do_next_tick(revert_pools)
    return True


def _Behavior_Destroy(caller: UObject, function: UFunction, params: FStruct) -> bool:
    return UObject.PathName(caller) not in PreventDestroy.Registries
