from __future__ import annotations

from unrealsdk import Log, FindAll, FindObject, GetEngine, KeepAlive  #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct  #type: ignore

from . import defines, options, hints
from .defines import Tag, Probability, construct_object
from .items import ItemPool

import random

from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple

ItemPoolList = List[Tuple[UObject, Probability]]


map_name: str = "menumap"
map_registry: Dict[str, Set[MapDropper]] = dict()

behavior_registry: Dict[str, Set[Behavior]] = dict()
interactive_registry: Dict[str, Set[Interactive]] = dict()

pool_whitelist = (
    "Pool_Ammo_All_DropAlways", "Pool_Ammo_All_Emergency", "Pool_Ammo_All_NeedOnly", "Pool_Ammo_Grenades_BoomBoom", "Pool_Health_All",
    "Pool_Eridium_Bar", "Pool_Eridium_Stick", "Pool_Money", "Pool_Money_1_BIG", "Pool_Money_1or2",
    "Pool_Orchid_SeraphCrystals", "Pool_Iris_SeraphCrystals", "Pool_Sage_SeraphCrystals", "Pool_Aster_SeraphCrystals",
    # "Pool_EpicChest_Weapons_GunsAndGear", "Pool_ClassMod_02_Uncommon", "Pool_ClassMod_04_Rare", "Pool_ClassMod_05_VeryRare", "Pool_ClassMod_06_Legendary", "Pool_GrenadeMods_02_Uncommon", "Pool_GrenadeMods_04_Rare", "Pool_GrenadeMods_05_VeryRare", "Pool_GrenadeMods_06_Legendary", "Pool_GunsAndGear", "Pool_GunsAndGear_02_Uncommon", "Pool_GunsAndGear_02_UncommonsRaid", "Pool_GunsAndGear_04_Rare", "Pool_GunsAndGear_05_VeryRare", "Pool_GunsAndGearDropNumPlayersPlusOne", "Pool_Shields_All_02_Uncommon", "Pool_Shields_All_04_Rare", "Pool_Shields_All_05_VeryRare", "Pool_Shields_All_06_Legendary", "Pool_VehicleSkins_All", "Pool_Weapons_All", "Pool_Weapons_All_02_Uncommon", "Pool_Weapons_All_04_Rare", "Pool_Weapons_All_05_VeryRare", "Pool_Weapons_All_06_Legendary",
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

    item: Optional[ItemPool] = None
    _hint_pool: Optional[UObject] = None

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


    @property
    def hint_pool(self) -> UObject: #ItemPoolDefinition
        if not self._hint_pool:
            hint_inventory = construct_object(hints.inventory_template, "InvBal_Hint_" + self.name)

            useitem = construct_object(hints.useitem_template, hint_inventory)
            hint_inventory.InventoryDefinition = useitem
            defines.set_command(useitem, "ItemName", self.name)

            useitem.Presentation = construct_object(hints.presentation_template, useitem)

            self._hint_pool = construct_object("ItemPoolDefinition", "Pool_Hint_" + self.name)
            self._hint_pool.bAutoReadyItems = False
            self._hint_pool.BalancedItems = ((None, hint_inventory, (1, None, None, 1), True),)

            self.update_hint(True)

        return self._hint_pool


    def update_hint(self, set_enabled: Optional[bool] = None) -> None:
        if not (self.item and self._hint_pool):
            return

        useitem = self.hint_pool.BalancedItems[0].InvBalanceDefinition.InventoryDefinition
        if set_enabled is not None:
            useitem.PickupLifeSpan = 0 if set_enabled else 0.000001

        if options.HintDisplay.CurrentValue == "None":
            hint_text = "&nbsp;?"
        if options.HintDisplay.CurrentValue == "Vague":
            hint_text = "&nbsp;&#x2022;&nbsp;&nbsp;" + self.item.vague_hint.value
        if options.HintDisplay.CurrentValue == "Spoiler":
            hint_text = "&nbsp;&#x2022;&nbsp;&nbsp;" + self.item.name

        defines.set_command(useitem.Presentation, "DescriptionLocReference", hint_text)
        

class Dropper:
    location: Location


class MapDropper(Dropper):
    map_names: Sequence[str]

    def __init__(self) -> None:
        for map_name in self.map_names:
            registry = map_registry.setdefault(map_name, set())
            registry.add(self)

    def entered_map(self) -> None:
        raise NotImplementedError

    def exited_map(self) -> None:
        pass


class Behavior(Dropper):
    path: str
    inject: bool

    def __init__(self, path: str, inject: bool = True) -> None:
        self.path = path; self.inject = inject
        registry = behavior_registry.setdefault(self.path, set())
        registry.add(self)


class Interactive(Dropper):
    path: str

    def __init__(self, path: str, inject: bool = True) -> None:
        self.path = path; self.inject = inject
        registry = interactive_registry.setdefault(self.path, set())
        registry.add(self)

    def should_inject(self, iteractive: UObject) -> bool:
        return True


def MapChanged(new_map_name: str) -> None:
    global map_name
    for map_dropper in map_registry.get(map_name, ()):
        map_dropper.exited_map()
    
    map_name = new_map_name
    for map_dropper in map_registry.get(map_name, ()):
        map_dropper.entered_map()


def _PostCommitMapChange(caller: UObject, function: UFunction, params: FStruct) -> bool:
    MapChanged(GetEngine().GetCurrentWorldInfo().GetMapName())
    return True


def _InitGame(caller: UObject, function: UFunction, params: FStruct) -> bool:
    if params.MapName == "MenuMap":
        MapChanged("menumap")
    return True


def prepare_dropper_pools(droppers: Sequence[Dropper]) -> Tuple[Sequence[UObject], Callable[[], None]]:
    pools: List[UObject] = []
    modified_items: List[ItemPool] = []

    for dropper in droppers:
        item = dropper.location.item
        if not item:
            continue

        for rarity in dropper.location.rarities:
            if random.randint(1, rarity) == 1:
                pools.append(item.pool)
                item.prepare()
                modified_items.append(item)
            else:
                pools.append(dropper.location.hint_pool)

    def revert_items(items: Sequence[ItemPool] = modified_items) -> None:
        for item in items:
            item.revert()

    return pools, revert_items


def _Behavior_SpawnItems(caller: UObject, function: UFunction, params: FStruct) -> bool:
    registry = behavior_registry.get(UObject.PathName(caller))
    if not registry:
        return True
    
    original_list = defines.convert_struct(tuple(caller.ItemPoolList))
    pools = [pool for pool in original_list if pool[0] and pool[0].Name in pool_whitelist]

    droppers = [dropper for dropper in registry if dropper.inject]
    inject_pools, revert_items = prepare_dropper_pools(droppers)

    caller.ItemPoolList = pools + inject_pools

    cleaned_itempoollistdefs = dict()
    
    def clean_itempoollistdef(itempoollistdef: UObject) -> None:
        if not itempoollistdef:
            return

        for nested_itempoollistdef in itempoollistdef.ItemPoolIncludedLists:
            clean_itempoollistdef(nested_itempoollistdef)

        if itempoollistdef not in cleaned_itempoollistdefs:
            pools = defines.convert_struct(tuple(itempoollistdef.ItemPools))
            cleaned_itempoollistdefs[itempoollistdef] = pools
            itempoollistdef.ItemPools = [
                pool for pool in pools
                if pool[0] and pool[0].Name in pool_whitelist
            ]

    for itempoollistdef in caller.ItemPoolIncludedLists:
        clean_itempoollistdef(itempoollistdef)

    def revert_pools(cleaned_itempoollistdefs=cleaned_itempoollistdefs) -> None:
        caller.ItemPoolList = original_list
        for itempoollistdef, pools in cleaned_itempoollistdefs.items():
            itempoollistdef.ItemPools = pools

    defines.do_next_tick(revert_pools, revert_items)

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
- roland's armory

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

"Butt Stallion Gemstone Fart"
    Behavior("GD_ButtStallion_Proto.Character.AIDef_ButtStallion_Proto:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_66"),
"Butt Stallion Legendary Fart"
    Behavior("GD_ButtStallion_Proto.Character.AIDef_ButtStallion_Proto:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_66"),

Gwen's Head Box
def CreatePopulationActor(caller: UObject, function: UFunction, params: FStruct) -> bool:
    if caller.ObjectBalanceDefinition.Name != "ObjectGrade_WhatsInTheBox":
        return True
    
    caller.ObjectBalanceDefinition.DefaultLoot[0].ItemAttachments[0].ItemPool = FindObject("ItemPoolDefinition", "GD_Itempools.Runnables.Pool_Talos")
    return True

RemoveHook("WillowGame.PopulationFactoryInteractiveObject.CreatePopulationActor", "Test")
RunHook("WillowGame.PopulationFactoryInteractiveObject.CreatePopulationActor", "Test", CreatePopulationActor)
"""



