from __future__ import annotations

from unrealsdk import Log, FindAll, FindObject, GetEngine, KeepAlive  #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct  #type: ignore

from . import defines, options, hints
from .defines import Tag, Probability, construct_object
from .items import ItemPool

from typing import Dict, List, Optional, Sequence, Set, Tuple

ItemPoolList = List[Tuple[UObject, Probability]]


map_name: str = "menumap"
map_registry: Dict[str, Set[MapDropper]] = dict()

behavior_registry: Dict[str, Set[Behavior]] = dict()
interactive_registry: Dict[str, Set[Interactive]] = dict()

pool_whitelist = (
    "Pool_Ammo_All_DropAlways",
    "Pool_Ammo_All_Emergency",
    "Pool_Ammo_All_NeedOnly",
    "Pool_Ammo_Grenades_BoomBoom",
    "Pool_Health_All",

    "Pool_Eridium_Bar",
    "Pool_Eridium_Stick",

    "Pool_Money",
    "Pool_Money_1_BIG",
    "Pool_Money_1or2",

    "Pool_Orchid_SeraphCrystals",
    "Pool_Iris_SeraphCrystals",
    "Pool_Sage_SeraphCrystals",
    "Pool_Aster_SeraphCrystals",

    # "Pool_EpicChest_Weapons_GunsAndGear",
    # "Pool_ClassMod_02_Uncommon",
    # "Pool_ClassMod_04_Rare",
    # "Pool_ClassMod_05_VeryRare",
    # "Pool_ClassMod_06_Legendary",
    # "Pool_GrenadeMods_02_Uncommon",
    # "Pool_GrenadeMods_04_Rare",
    # "Pool_GrenadeMods_05_VeryRare",
    # "Pool_GrenadeMods_06_Legendary",
    # "Pool_GunsAndGear",
    # "Pool_GunsAndGear_02_Uncommon",
    # "Pool_GunsAndGear_02_UncommonsRaid",
    # "Pool_GunsAndGear_04_Rare",
    # "Pool_GunsAndGear_05_VeryRare",
    # "Pool_GunsAndGearDropNumPlayersPlusOne",
    # "Pool_Shields_All_02_Uncommon",
    # "Pool_Shields_All_04_Rare",
    # "Pool_Shields_All_05_VeryRare",
    # "Pool_Shields_All_06_Legendary",
    # "Pool_VehicleSkins_All",
    # "Pool_Weapons_All",
    # "Pool_Weapons_All_02_Uncommon",
    # "Pool_Weapons_All_04_Rare",
    # "Pool_Weapons_All_05_VeryRare",
    # "Pool_Weapons_All_06_Legendary",
)


def Enable() -> None:
    RunHook("Engine.GameInfo.PostCommitMapChange", "LootRandomizer", _PostCommitMapChange)
    RunHook("Engine.GameInfo.SetGameType", "LootRandomizer", _InitGame)
    RunHook("WillowGame.Behavior_SpawnItems.ApplyBehaviorToContext", "LootRandomizer", _Behavior_SpawnItems)
    RunHook("WillowGame.WillowInteractiveObject.UsedBy", "LootRandomizer", _UsedBy)


def Disable() -> None:
    RemoveHook("Engine.GameInfo.PostCommitMapChange", "LootRandomizer")
    RemoveHook("Engine.GameInfo.SetGameType", "LootRandomizer")
    RemoveHook("WillowGame.Behavior_SpawnItems.ApplyBehaviorToContext", "LootRandomizer")
    RemoveHook("WillowGame.WillowInteractiveObject.UsedBy", "LootRandomizer")


class Location:
    name: str
    droppers: Sequence[Dropper]
    tags: Tag
    rarities: Sequence[int]

    item: ItemPool
    hint_inventory: Optional[UObject] = None

    _pools: Optional[Sequence[UObject]] = None

    def __init__(
        self,
        name: str,
        *droppers: Dropper,
        tags: Tag,
        rarities: Sequence[int] = (1,)
    ) -> None:
        self.name = name; self.droppers = droppers; self.tags = tags; self.rarities = rarities
        for dropper in droppers:
            dropper.location = self # This is a circular reference; Location objects are static.

    def apply(self, item: ItemPool) -> None:
        if not isinstance(item, ItemPool):
            raise ValueError
        self.item = item
        for dropper in self.droppers:
            dropper.register()

    def revert(self) -> None:
        for dropper in self.droppers:
            dropper.unregister()

        if self._pools:
            for pool in self._pools:
                if pool is not self.item.pool:
                    pool.ObjectFlags.A &= ~0x4000
            self._pools = None

        if hasattr(self, "item"):
            del self.item

    def construct_hint_inventory(self) -> UObject: #InventoryBalanceDefinition
        if not self.hint_inventory:
            self.hint_inventory = construct_object(hints.inventory_template, "Hint_Inventory_" + self.name)
            KeepAlive(self.hint_inventory)

            useitem = construct_object(hints.useitem_template, self.hint_inventory)
            self.hint_inventory.InventoryDefinition = useitem
            defines.set_command(useitem, "ItemName", self.name)

            useitem.Presentation = construct_object(hints.presentation_template, useitem)

        self.update_hint(True)
        return self.hint_inventory

    def update_hint(self, set_enabled: Optional[bool] = None) -> None:
        if not (hasattr(self, "item") and self.hint_inventory):
            return

        if options.HintDisplay.CurrentValue == "None":
            hint_text = "&nbsp;?"
        if options.HintDisplay.CurrentValue == "Vague":
            hint_text = "&nbsp;&#x2022;&nbsp;&nbsp;" + self.item.vague_hint.value
        if options.HintDisplay.CurrentValue == "Spoiler":
            hint_text = "&nbsp;&#x2022;&nbsp;&nbsp;" + self.item.name

        if set_enabled is not None:
            self.hint_inventory.InventoryDefinition.PickupLifeSpan = 0 if set_enabled else 0.000001

        presentation = self.hint_inventory.InventoryDefinition.Presentation
        defines.set_command(presentation, "DescriptionLocReference", hint_text)
        

    @property
    def pools(self) -> Sequence[UObject]: #ItemPoolDefinition
        if self._pools is not None:
            return self._pools
        
        self._pools = list()
        
        for rarity in self.rarities:
            if rarity == 1:
                self._pools.append(self.item.pool)
                continue

            pool = construct_object("ItemPoolDefinition")
            KeepAlive(pool)
            pool.bAutoReadyItems = False
            pool.BalancedItems = [
                (self.item.pool, None, (1, None, None, 1), True),
                (None, self.construct_hint_inventory(), (rarity - 1, None, None, 1), True),
            ]
            self._pools.append(pool)

        return self._pools


class Dropper:
    location: Location

    def register(self) -> None:
        pass

    def unregister(self) -> None:
        pass


class MapDropper(Dropper):
    map_names: Sequence[str]
    in_map: bool = False

    def register(self) -> None:
        for map_name in self.map_names:
            registry = map_registry.setdefault(map_name, set())
            registry.add(self)

    def unregister(self) -> None:
        for map_name in self.map_names:
            registry = map_registry.get(map_name)
            if registry:
                registry.discard(self)
                if not registry:
                    del map_registry[map_name]

    def inject(self) -> None:
        raise NotImplementedError

    def uninject(self) -> None:
        pass


class Behavior(Dropper):
    path: str
    inject: bool

    def __init__(self, path: str, inject: bool = True) -> None:
        self.path = path; self.inject = inject

    def register(self) -> None:
        registry = behavior_registry.setdefault(self.path, set())
        registry.add(self)

    def unregister(self) -> None:
        registry = behavior_registry.get(map_name)
        if registry:
            registry.discard(self)
            if not registry:
                del behavior_registry[map_name]


class Interactive(Dropper):
    path: str

    def __init__(self, path: str, inject: bool = True) -> None:
        self.path = path; self.inject = inject

    def register(self) -> None:
        registry = interactive_registry.setdefault(self.path, set())
        registry.add(self)

    def unregister(self) -> None:
        registry = interactive_registry.get(map_name)
        if registry:
            registry.discard(self)
            if not registry:
                del interactive_registry[map_name]

    def should_inject(self, iteractive: UObject) -> bool:
        return True


def MapChanged(new_map_name: str) -> None:
    global map_name
    for map_dropper in map_registry.get(map_name, ()):
        map_dropper.in_map = False
        map_dropper.uninject()
    
    map_name = new_map_name
    for map_dropper in map_registry.get(map_name, ()):
        map_dropper.in_map = True
        map_dropper.inject()


def _PostCommitMapChange(caller: UObject, function: UFunction, params: FStruct) -> bool:
    MapChanged(GetEngine().GetCurrentWorldInfo().GetMapName())
    return True


def _InitGame(caller: UObject, function: UFunction, params: FStruct) -> bool:
    if params.MapName == "MenuMap":
        MapChanged("menumap")
    return True


def _Behavior_SpawnItems(caller: UObject, function: UFunction, params: FStruct) -> bool:
    registry = behavior_registry.get(UObject.PathName(caller))
    if not registry:
        return True
    
    original_list = defines.convert_struct(list(caller.ItemPoolList))
    pools = [pool for pool in original_list if pool[0] and pool[0].Name in pool_whitelist]

    droppers = [dropper for dropper in registry if dropper.inject]
    for dropper in droppers:
        dropper.location.item.prepare()
        pools += [(pool, (1, None, None, 1)) for pool in dropper.location.pools]

    caller.ItemPoolList = pools

    cleaned_itempoollistdefs = dict()
    
    def clean_itempoollistdef(itempoollistdef: UObject) -> None:
        if not itempoollistdef:
            return

        for nested_itempoollistdef in itempoollistdef.ItemPoolIncludedLists:
            clean_itempoollistdef(nested_itempoollistdef)

        if itempoollistdef not in cleaned_itempoollistdefs:
            pools = defines.convert_struct(list(itempoollistdef.ItemPools))
            cleaned_itempoollistdefs[itempoollistdef] = pools
            itempoollistdef.ItemPools = [
                pool for pool in pools
                if pool[0] and pool[0].Name in pool_whitelist
            ]

    for itempoollistdef in caller.ItemPoolIncludedLists:
        clean_itempoollistdef(itempoollistdef)

    def revert(droppers=droppers, cleaned_itempoollistdefs=cleaned_itempoollistdefs) -> None:
        for dropper in droppers:
            dropper.location.item.revert()

        caller.ItemPoolList = original_list

        for itempoollistdef, pools in cleaned_itempoollistdefs.items():
            itempoollistdef.ItemPools = pools

    defines.do_next_tick(revert)

    return True


def _UsedBy(caller: UObject, function: UFunction, params: FStruct) -> bool:
    balance = caller.BalanceDefinitionState.BalanceDefinition
    if not balance:
        return True
    
    registry = interactive_registry.get(balance.Name)
    if not registry:
        return True

    droppers = [dropper for dropper in registry if dropper.should_inject(caller)]
    if not droppers:
        return True



    return True

"""
- seraph vendors / torgue vendors
    raid 

- Tundra snowman head
    GD_Episode07Data.WeaponPools.Pool_Weapons_Ep7_FireGuns
    GD_Episode07Data.BalanceDefs.BD_Ep7_SnowManHead_Ammo
- Gwen's head box
    GD_EasterEggs.WeaponPools.Pool_Weapons_Gwen_Unique
- Lascaux pool
    Env_IceCanyon.WeaponPools.Pool_Weapon_CaveGun
- tipping moxxi
- thumpson pile
- mimic chests + mimic
- buttstallion with amulet
- loot goon chests
- slot machines
- tina slot machines

- chest being stolen by yeti
- leprechaun
    GD_Nast_Leprechaun.Character.CharClass_Nast_Leprechaun:BehaviorProviderDefinition_5.Behavior_SpawnItems_26
    GD_Nast_Leprechaun.Character.CharClass_Nast_Leprechaun:BehaviorProviderDefinition_5.Behavior_SpawnItems_27
- digi peak chests
- Gobbler slag pistol
- Wam Bam loot injectors
- Mammaril
- Caravan
- haderax chest
- halloween gun sacrifice
- dragon keep altar
- marcus statue suicide
- Scarlet Caravan
    GD_Orchid_PlotDataMission04.Mission04.Balance_Orchid_CaravanChest
- Wedding balloon
    GD_Nasturtium_Lootables.IOs.IO_BossBalloons:BehaviorProviderDefinition_1.Behavior_SpawnItems_0
    GD_Nasturtium_Lootables.IOs.IO_BossBalloons:BehaviorProviderDefinition_1.Behavior_SpawnItems_2
    GD_Nasturtium_Lootables.IOs.IO_BossBalloons:BehaviorProviderDefinition_1.Behavior_SpawnItems_1
- Rotgut Fishing Chest

disable Sky Rocket and VH Relic in starting gear

"""

# "Butt Stallion Gemstone Fart"
#     Behavior("GD_ButtStallion_Proto.Character.AIDef_ButtStallion_Proto:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_66"),
# "Butt Stallion Legendary Fart"
#     Behavior("GD_ButtStallion_Proto.Character.AIDef_ButtStallion_Proto:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_66"),


"""Gwen's Head Box"""
# def CreatePopulationActor(caller: UObject, function: UFunction, params: FStruct) -> bool:
#     if caller.ObjectBalanceDefinition.Name != "ObjectGrade_WhatsInTheBox":
#         return True
    
#     caller.ObjectBalanceDefinition.DefaultLoot[0].ItemAttachments[0].ItemPool = FindObject("ItemPoolDefinition", "GD_Itempools.Runnables.Pool_Talos")
#     return True

# RemoveHook("WillowGame.PopulationFactoryInteractiveObject.CreatePopulationActor", "Test")
# RunHook("WillowGame.PopulationFactoryInteractiveObject.CreatePopulationActor", "Test", CreatePopulationActor)
