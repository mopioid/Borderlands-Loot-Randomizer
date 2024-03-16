from __future__ import annotations

from unrealsdk import Log, FindAll, FindObject, GetEngine, KeepAlive  #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct  #type: ignore

from . import defines, options, hints, items
from .defines import Tag, Probability, construct_object
from .items import ItemPool

import random

from typing import Dict, List, Optional, Sequence, Set, Tuple

ItemPoolList = List[Tuple[UObject, Probability]]


map_name: str = "menumap"
map_registry: Dict[str, Set[MapDropper]] = dict()

behavior_registry: Dict[str, Set[Behavior]] = dict()
interactive_registry: Dict[str, Interactive] = dict()
vending_registry: Dict[str, VendingMachine] = dict()


pool_whitelist = (
    "Pool_Ammo_All_DropAlways", "Pool_Ammo_All_Emergency", "Pool_Ammo_All_NeedOnly", "Pool_Ammo_Grenades_BoomBoom", "Pool_Health_All",
    "Pool_Eridium_Bar", "Pool_Eridium_Stick", "Pool_Money", "Pool_Money_1_BIG", "Pool_Money_1or2",
    "Pool_Orchid_SeraphCrystals", "Pool_Iris_SeraphCrystals", "Pool_Sage_SeraphCrystals", "Pool_Aster_SeraphCrystals",
    # "Pool_EpicChest_Weapons_GunsAndGear", "Pool_ClassMod_02_Uncommon", "Pool_ClassMod_04_Rare", "Pool_ClassMod_05_VeryRare", "Pool_ClassMod_06_Legendary", "Pool_GrenadeMods_02_Uncommon", "Pool_GrenadeMods_04_Rare", "Pool_GrenadeMods_05_VeryRare", "Pool_GrenadeMods_06_Legendary", "Pool_GunsAndGear", "Pool_GunsAndGear_02_Uncommon", "Pool_GunsAndGear_02_UncommonsRaid", "Pool_GunsAndGear_04_Rare", "Pool_GunsAndGear_05_VeryRare", "Pool_GunsAndGearDropNumPlayersPlusOne", "Pool_Shields_All_02_Uncommon", "Pool_Shields_All_04_Rare", "Pool_Shields_All_05_VeryRare", "Pool_Shields_All_06_Legendary", "Pool_VehicleSkins_All", "Pool_Weapons_All", "Pool_Weapons_All_02_Uncommon", "Pool_Weapons_All_04_Rare", "Pool_Weapons_All_05_VeryRare", "Pool_Weapons_All_06_Legendary",
)


def Enable() -> None:
    # RunHook("Engine.GameInfo.PostCommitMapChange", "LootRandomizer", _PostCommitMapChange)
    RunHook("Engine.GameInfo.SetGameType", "LootRandomizer", _InitGame)
    RunHook("WillowGame.Behavior_SpawnItems.ApplyBehaviorToContext", "LootRandomizer", _Behavior_SpawnItems)
    RunHook("WillowGame.WillowInteractiveObject.UsedBy", "LootRandomizer", _UsedBy)
    RunHook("WillowGame.WillowPlayerController.ClientSetPawnLocation", "LootRandomizer", _SetPawnLocation)
    RunHook("WillowGame.WillowPlayerController.GrantNewMarketingCodeBonuses", "LootRandomizer", _GrantNewMarketingCodeBonuses)
    RunHook("WillowGame.PopulationFactoryVendingMachine.CreatePopulationActor", "LootRandomizer", _PopulationFactoryVendingMachine)


def Disable() -> None:
    # RemoveHook("Engine.GameInfo.PostCommitMapChange", "LootRandomizer")
    RemoveHook("Engine.GameInfo.SetGameType", "LootRandomizer")
    RemoveHook("WillowGame.Behavior_SpawnItems.ApplyBehaviorToContext", "LootRandomizer")
    RemoveHook("WillowGame.WillowInteractiveObject.UsedBy", "LootRandomizer")
    RemoveHook("WillowGame.WillowPlayerController.ClientSetPawnLocation", "LootRandomizer")
    RemoveHook("WillowGame.WillowPlayerController.GrantNewMarketingCodeBonuses", "LootRandomizer")
    RemoveHook("WillowGame.PopulationFactoryVendingMachine.CreatePopulationActor", "LootRandomizer")


class Location:
    name: str
    droppers: Sequence[Dropper]
    tags: Tag

    item: Optional[ItemPool] = None

    _rarities: Sequence[int]
    _hint_pool: Optional[UObject] = None

    def __init__(
        self,
        name: str,
        *droppers: Dropper,
        tags: Tag,
        rarities: Sequence[int] = (100,)
    ) -> None:
        if not tags & defines.ContentTags:
            tags |= Tag.BaseGame

        self.name = name; self.droppers = droppers; self.tags = tags; self._rarities = rarities
        for dropper in droppers:
            dropper.location = self # This is a circular reference; Location objects are static.

    @property
    def rarities(self) -> Sequence[int]:
        return (0,) if self.item is items.DudItem else self._rarities

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

            self.update_hint(True)

        return self._hint_pool

    @property
    def hint_inventory(self) -> Optional[UObject]: #InventoryBalanceDefinition
        return self.hint_pool.BalancedItems[0].InvBalanceDefinition if self._hint_pool else None

    def update_hint(self, set_enabled: Optional[bool] = None) -> None:
        if not self.hint_inventory:
            return

        useitem = self.hint_inventory.InventoryDefinition
        if set_enabled is not None:
            useitem.PickupLifeSpan = 0 if set_enabled else 0.000001

        if not self.item:
            return

        if self.item == items.DudItem:
            useitem.NonCompositeStaticMesh = hints.duditem_mesh
            useitem.PickupFlagIcon = hints.duditem_pickupflag

            hint_caption = "&nbsp;"
            hint_text = self.item.vague_hint.formatter(random.choice(hints.DudDescriptions))
        else:
            useitem.NonCompositeStaticMesh = hints.hintitem_mesh
            useitem.PickupFlagIcon = hints.hintitem_pickupflag

            if options._HintDisplay.CurrentValue == "None":
                hint_caption = "&nbsp;"
                hint_text = "?"
            if options._HintDisplay.CurrentValue == "Vague":
                hint_caption = "Item Hint"
                hint_text = self.item.vague_hint.formatter(self.item.vague_hint)
            if options._HintDisplay.CurrentValue == "Spoiler":
                hint_caption = "Item Spoiler"
                hint_text = self.item.vague_hint.formatter(self.item.name)

        defines.set_command(useitem.Presentation, "DescriptionLocReference", hint_caption)
        defines.set_command(useitem.CustomPresentations[0], "Description", hint_text)
        

    def apply_tags(self, tags: Tag) -> None:
        pass

    def __str__(self) -> str:
        raise NotImplementedError


class Dropper:
    location: Location

    def should_inject(self, uobject: Optional[UObject] = None) -> bool:
        return self.location.item is not None

    def prepare_pools(self) -> Sequence[UObject]:
        if not self.location.item:
            return ()

        self.location.item.prepare()
        defines.do_next_tick(self.location.item.revert)

        pools: List[UObject] = []

        for rarity in self.location.rarities:
            if rarity >= random.randint(1, 100):
                pools.append(self.location.item.pool)
            else:
                pools.append(self.location.hint_pool)
        
        return pools
    
    def enable(self) -> None:
        pass

    def disable(self) -> None:
        pass


class MapDropper(Dropper):
    map_names: Sequence[str] = ()

    def __init__(self, *map_names: str) -> None:
        if map_names:
            self.map_names = map_names

        for map_name in self.map_names:
            registry = map_registry.setdefault(map_name.lower(), set())
            registry.add(self)

    def entered_map(self) -> None:
        raise NotImplementedError

    def exited_map(self) -> None:
        pass


class Behavior(Dropper):
    path: str
    _inject: bool

    def __init__(self, path: str, inject: bool = True) -> None:
        self.path = path; self._inject = inject
        registry = behavior_registry.setdefault(self.path, set())
        registry.add(self)

    def should_inject(self, uobject: Optional[UObject] = None) -> bool:
        return super().should_inject() and self._inject


class Interactive(Dropper):
    path: str

    def __init__(self, path: str) -> None:
        self.path = path
        if interactive_registry.get(path):
            raise ValueError(f"Dropper already exists for '{path}'")
        interactive_registry[path] = self

    def inject(self, interactive: UObject) -> None:
        pools = self.prepare_pools()
        pool = pools[0] if pools else None
        interactive.Loot[0].ItemAttachments[0].ItemPool = pool


class VendingMachine(Dropper):
    path: str

    def __init__(self, path: str) -> None:
        self.path = path
        if vending_registry.get(path):
            raise ValueError(f"Dropper already exists for '{path}'")
        vending_registry[path] = self


def MapChanged(new_map_name: str) -> None:
    global map_name
    if new_map_name == map_name:
        return

    for map_dropper in map_registry.get(map_name, ()):
        map_dropper.exited_map()
    
    map_name = new_map_name
    for map_dropper in map_registry.get(map_name, ()):
        map_dropper.entered_map()


# def _PostCommitMapChange(caller: UObject, function: UFunction, params: FStruct) -> bool:
#     MapChanged(GetEngine().GetCurrentWorldInfo().GetMapName().lower())
#     return True

def _SetPawnLocation(caller: UObject, function: UFunction, params: FStruct) -> bool:
    MapChanged(GetEngine().GetCurrentWorldInfo().GetMapName().lower())
    return True


def _InitGame(caller: UObject, function: UFunction, params: FStruct) -> bool:
    if params.MapName == "MenuMap":
        MapChanged("menumap")
    return True


def _Behavior_SpawnItems(caller: UObject, function: UFunction, params: FStruct) -> bool:
    registry = behavior_registry.get(UObject.PathName(caller))
    if not registry:
        return True
    
    original_poollist = defines.convert_struct(tuple(caller.ItemPoolList))
    poollist = [pool for pool in original_poollist if pool[0] and pool[0].Name in pool_whitelist]

    for dropper in registry:
        if dropper.should_inject(caller):
            poollist += [(pool, (1, None, None, 1)) for pool in dropper.prepare_pools()]
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


def _UsedBy(caller: UObject, function: UFunction, params: FStruct) -> bool:
    balance = caller.BalanceDefinitionState.BalanceDefinition
    if not balance:
        return True
    
    dropper = interactive_registry.get(balance.Name)
    if dropper:
        dropper.inject(caller)

    return True


def _PopulationFactoryVendingMachine(caller: UObject, function: UFunction, params: FStruct) -> bool:
    balance = params.Opportunity.PopulationDef.ActorArchetypeList[0].SpawnFactory.ObjectBalanceDefinition

    dropper = vending_registry.get(UObject.PathName(balance))
    if not dropper:
        return True
    
    pools = dropper.prepare_pools()
    pool = pools[0] if pools else None

    balance.DefaultLoot[0].ItemAttachments[0].ItemPool = None
    balance.DefaultLoot[1].ItemAttachments[0].ItemPool = pool

    return True


def _GrantNewMarketingCodeBonuses(caller: UObject, function: UFunction, params: FStruct) -> bool:
    premier = FindObject("MarketingUnlockInventoryDefinition", "GD_Globals.Unlocks.MarketingUnlock_PremierClub")
    collectors = FindObject("MarketingUnlockInventoryDefinition", "GD_Globals.Unlocks.MarketingUnlock_Collectors")

    premier_items = tuple(premier.UnlockItems[0].UnlockItems)
    collectors_items = tuple(collectors.UnlockItems[0].UnlockItems)

    premier.UnlockItems[0].UnlockItems = ()
    collectors.UnlockItems[0].UnlockItems = ()

    def revert_unlocks(premier_items = premier_items, collectors_items = collectors_items) -> None:
        premier.UnlockItems[0].UnlockItems = premier_items
        collectors.UnlockItems[0].UnlockItems = collectors_items

    defines.do_next_tick(revert_unlocks)
    return True
