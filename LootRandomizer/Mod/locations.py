from __future__ import annotations

from unrealsdk import Log, GetEngine
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct

from . import options, hints, items, seed
from .defines import *
from .items import ItemPool

import random

from typing import (
    Any,
    Dict,
    Generator,
    List,
    Optional,
    Sequence,
    Set,
    Union,
    Type,
    TypeVar,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    # from typing import Self
    from .missions import Mission


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
    "ItemPool_TorgueToken_Qty10",
    "ItemPool_TorgueToken_Qty100",
    "ItemPool_TorgueToken_Qty15",
    "ItemPool_TorgueToken_Qty25",
    "ItemPool_TorgueToken_Qty3",
    "ItemPool_TorgueToken_Qty5",
    "ItemPool_TorgueToken_Qty50",
    "ItemPool_TorgueToken_Qty7",
    "ItemPool_TorgueToken_Qty75",
    "ItemPool_TorgueToken_Single",
    "ItemPool_MoxxiPicture",
    # "Pool_EpicChest_Weapons_GunsAndGear", "Pool_ClassMod_02_Uncommon", "Pool_ClassMod_04_Rare", "Pool_ClassMod_05_VeryRare", "Pool_ClassMod_06_Legendary", "Pool_GrenadeMods_02_Uncommon", "Pool_GrenadeMods_04_Rare", "Pool_GrenadeMods_05_VeryRare", "Pool_GrenadeMods_06_Legendary", "Pool_GunsAndGear", "Pool_GunsAndGear_02_Uncommon", "Pool_GunsAndGear_02_UncommonsRaid", "Pool_GunsAndGear_04_Rare", "Pool_GunsAndGear_05_VeryRare", "Pool_GunsAndGearDropNumPlayersPlusOne", "Pool_Shields_All_02_Uncommon", "Pool_Shields_All_04_Rare", "Pool_Shields_All_05_VeryRare", "Pool_Shields_All_06_Legendary", "Pool_VehicleSkins_All", "Pool_Weapons_All", "Pool_Weapons_All_02_Uncommon", "Pool_Weapons_All_04_Rare", "Pool_Weapons_All_05_VeryRare", "Pool_Weapons_All_06_Legendary",
)


def Enable() -> None:
    # RunHook("Engine.GameInfo.PostCommitMapChange", "LootRandomizer", _PostCommitMapChange)
    RunHook(
        "Engine.GameInfo.SetGameType",
        "LootRandomizer",
        _SetGameType,
    )
    RunHook(
        "WillowGame.Behavior_SpawnItems.ApplyBehaviorToContext",
        "LootRandomizer",
        _Behavior_SpawnItems,
    )
    RunHook(
        "WillowGame.WillowPlayerController.ClientSetPawnLocation",
        "LootRandomizer",
        _SetPawnLocation,
    )
    RunHook(
        "Engine.Behavior_Destroy.ApplyBehaviorToContext",
        "LootRandomizer",
        _Behavior_Destroy,
    )


def Disable() -> None:
    # RemoveHook("Engine.GameInfo.PostCommitMapChange", "LootRandomizer")
    RemoveHook(
        "Engine.GameInfo.SetGameType",
        "LootRandomizer",
    )
    RemoveHook(
        "WillowGame.Behavior_SpawnItems.ApplyBehaviorToContext",
        "LootRandomizer",
    )
    RemoveHook(
        "WillowGame.WillowPlayerController.ClientSetPawnLocation",
        "LootRandomizer",
    )
    RemoveHook(
        "Engine.Behavior_Destroy.ApplyBehaviorToContext",
        "LootRandomizer",
    )


class Location:
    name: str
    droppers: Sequence[Dropper]
    tags: Tag
    mission_name: Optional[str]
    content: Tag

    specified_tags: Tag
    specified_rarities: Optional[Sequence[int]]

    mission: Optional[Mission] = None
    item: Optional[ItemPool] = None

    _rarities: Sequence[int]
    _hint_pool: Optional[UObject] = None

    default_rarity: int = 100

    def __init__(
        self,
        name: str,
        *droppers: Dropper,
        tags: Tag = Tag(0),
        mission: Optional[str] = None,
        content: Tag = Tag(0),
        rarities: Optional[Sequence[int]] = None,
    ) -> None:
        for dropper in droppers:
            dropper.location = self  # This is a circular reference; Location objects are static.

        self.name = name
        self.droppers = droppers
        self.tags = tags
        self.mission_name = mission
        self.content = content if content else (tags & ContentTags)
        self.specified_tags = tags
        self.specified_rarities = rarities

    @property
    def rarities(self) -> Sequence[int]:
        return (0,) if self.item is items.DudItem else self._rarities

    @rarities.setter
    def rarities(self, rarities: Sequence[int]) -> None:
        self._rarities = rarities

    def enable(self) -> None:
        for dropper in self.droppers:
            dropper.enable()

        self.tags = self.specified_tags
        rarities: List[int] = (
            list(self.specified_rarities) if self.specified_rarities
            else [self.default_rarity]
        )

        if self.mission_name:
            self.tags |= Tag.MissionLocation

            from .missions import Mission

            if BL2:
                from .bl2.locations import Locations
            elif TPS:
                from .tps.locations import Locations
            else:
                raise

            for location in Locations:
                if (
                    isinstance(location, Mission)
                    and location.name == self.mission_name
                ):
                    self.mission = location
                    break
            else:
                raise ValueError(
                    f"Failed to match mission {self.mission_name}"
                )

            self.tags |= self.mission.tags
            self.content = self.mission.content

            if not self.specified_rarities:
                if self.tags & Tag.LongMission:
                    rarities += (self.default_rarity,)
                if self.tags & Tag.VeryLongMission:
                    rarities += (self.default_rarity,) * 2
        else:
            self.content = self.tags & ContentTags

        if not self.content:
            self.tags |= Tag.BaseGame
            self.content = Tag.BaseGame

        self.rarities = rarities

    def disable(self) -> None:
        for dropper in self.droppers:
            dropper.disable()

    @property
    def hint_pool(self) -> UObject:  # ItemPoolDefinition
        if not self._hint_pool:
            hint_inventory = construct_object(
                hints.inventory_template, "InvBal_Hint_" + self.name
            )

            useitem = construct_object(hints.useitem_template, hint_inventory)
            hint_inventory.InventoryDefinition = useitem
            set_command(useitem, "ItemName", f'"{self.name}"')

            useitem.CustomPresentations = (
                construct_object(hints.custompresentation_template, useitem),
            )
            useitem.Presentation = construct_object(
                hints.presentation_template, useitem
            )

            self._hint_pool = construct_object(
                "ItemPoolDefinition", "Pool_Hint_" + self.name
            )
            self._hint_pool.bAutoReadyItems = False
            self._hint_pool.BalancedItems = (
                (None, hint_inventory, (1, None, None, 1), True),
            )

            self.update_hint()
            self.toggle_hint(True)

        return self._hint_pool

    @property
    def hint_inventory(
        self,
    ) -> Optional[UObject]:  # InventoryBalanceDefinition
        return (
            self.hint_pool.BalancedItems[0].InvBalanceDefinition
            if self._hint_pool
            else None
        )

    def update_hint(self) -> None:
        if not (self.hint_inventory and self.item):
            return

        useitem = self.hint_inventory.InventoryDefinition

        if self.item == items.DudItem:
            useitem.NonCompositeStaticMesh = hints.duditem_mesh
            useitem.PickupFlagIcon = hints.duditem_pickupflag

            hint_caption = "&nbsp;"
            hint_text = self.item.hint.formatter(
                random.choice(hints.DudDescriptions)
            )
        else:
            useitem.NonCompositeStaticMesh = hints.hintitem_mesh
            useitem.PickupFlagIcon = hints.hintitem_pickupflag

            if options.HintDisplay.CurrentValue == "Vague":
                hint_caption = "Item Hint"
                hint_text = self.item.hint.formatter(self.item.hint)
            elif options.HintDisplay.CurrentValue == "Spoiler":
                hint_caption = "Item Spoiler"
                hint_text = self.item.hint.formatter(self.item.name)
            else:
                hint_caption = "&nbsp;"
                hint_text = "?"

        set_command(
            useitem.Presentation, "DescriptionLocReference", hint_caption
        )
        set_command(useitem.CustomPresentations[0], "Description", hint_text)

    def toggle_hint(self, set_enabled: bool):
        if self.hint_inventory:
            self.hint_inventory.InventoryDefinition.PickupLifeSpan = (
                0 if set_enabled else 0.000001
            )

    def prepare_pools(self, count: Optional[int] = None) -> Sequence[UObject]:
        if count is None:
            count = len(self.rarities)
        if not count:
            return ()

        if not self.item:
            return (hints.padding_pool,) * count

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
                pools.append(hints.padding_pool)
            elif random.randrange(100) < self.rarities[index]:
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

    def __str__(self) -> str:
        raise NotImplementedError

    @property
    def tracker_name(self) -> str:
        return str(self)


class Dropper:
    location: Location

    def enable(self) -> None:
        pass

    def disable(self) -> None:
        pass


Self = TypeVar("Self", bound="RegistrantDropper")


class RegistrantDropper(Dropper):
    Registries: Dict[str, Set[RegistrantDropper]]

    @classmethod
    def Registrants(cls: Type[Self], *paths: Union[str, UObject]) -> Set[Self]:
        def iterate_paths() -> Generator[Self, None, None]:
            if len(paths):
                for path in paths:
                    if isinstance(path, UObject):
                        path = str(UObject.PathName(path))
                    for registrant in cls.Registries.get(path.casefold(), ()):
                        yield registrant  # type: ignore
            else:
                for registry in cls.Registries.values():
                    for registrant in registry:
                        yield registrant  # type: ignore

        return set(iterate_paths())

    paths: Sequence[str]

    def __init__(self, *paths: str) -> None:
        if len(paths):
            self.paths = paths

        if not hasattr(self, "paths"):
            raise Exception(
                f"No paths specified for {self.__class__.__name__}"
            )

    def enable(self) -> None:
        for path in self.paths:
            registry = self.Registries.setdefault(path.casefold(), set())
            registry.add(self)

    def disable(self) -> None:
        for path in self.paths:
            registry = self.Registries.get(path.casefold())
            if registry:
                registry.discard(self)
                if not registry:
                    del self.Registries[path.casefold()]


class MapDropper(RegistrantDropper):
    Registries = dict()

    def entered_map(self) -> None:
        raise NotImplementedError

    def exited_map(self) -> None:
        pass


_menu_name: str = "menumap".casefold()
_loader_name: str = "loader".casefold()
map_name: str = _menu_name


def MapChanged(new_map_name: str) -> None:
    global map_name

    for map_dropper in MapDropper.Registrants("*", map_name):
        map_dropper.exited_map()

    map_name = new_map_name
    for map_dropper in MapDropper.Registrants("*", map_name):
        map_dropper.entered_map()


def _SetPawnLocation(caller: UObject, _f: UFunction, params: FStruct) -> bool:
    new_map_name = str(
        GetEngine().GetCurrentWorldInfo().GetMapName()
    ).casefold()
    if new_map_name in (map_name, _loader_name):
        return True

    def wait_missiontracker(new_map_name: str = new_map_name) -> bool:
        if get_pc().WorldInfo.GRI and get_pc().WorldInfo.GRI.MissionTracker:
            MapChanged(new_map_name)
            return False
        return True

    tick_while(wait_missiontracker)

    return True


def _SetGameType(caller: UObject, _f: UFunction, params: FStruct) -> bool:
    if map_name != _menu_name and params.MapName.casefold() == _menu_name:
        MapChanged(_menu_name)
    return True


# def _PostCommitMapChange(caller: UObject, _f: UFunction, params: FStruct) -> bool:
#     return True


class Behavior(RegistrantDropper):
    Registries = dict()

    inject: bool

    def __init__(self, *paths: str, inject: bool = True) -> None:
        self.inject = inject
        super().__init__(*paths)


def _Behavior_SpawnItems(
    caller: UObject, _f: UFunction, params: FStruct
) -> bool:
    registrars = Behavior.Registrants(caller)
    if not registrars:
        return True

    original_poollist = convert_struct(tuple(caller.ItemPoolList))
    poollist = [
        pool
        for pool in original_poollist
        if pool[0] and pool[0].Name in pool_whitelist
    ]

    for dropper in registrars:
        if dropper.inject:
            poollist += [
                (pool, (1, None, None, 1))
                for pool in dropper.location.prepare_pools()
            ]
            break

    caller.ItemPoolList = poollist

    cleaned_poollistdefs: Dict[UObject, Any] = dict()

    def clean_poollistdef(poollistdef: Optional[UObject]) -> None:
        if not poollistdef:
            return

        for nested_itempoollistdef in poollistdef.ItemPoolIncludedLists:
            clean_poollistdef(nested_itempoollistdef)

        if poollistdef not in cleaned_poollistdefs:
            pools = convert_struct(tuple(poollistdef.ItemPools))
            cleaned_poollistdefs[poollistdef] = pools
            poollistdef.ItemPools = [
                pool
                for pool in pools
                if pool[0] and pool[0].Name in pool_whitelist
            ]

    for poollistdef in caller.ItemPoolIncludedLists:
        clean_poollistdef(poollistdef)

    def revert_pools(
        original_poollist: Any = original_poollist,
        cleaned_poollistdefs: Dict[UObject, Any] = cleaned_poollistdefs,
    ) -> None:
        caller.ItemPoolList = original_poollist
        for itempoollistdef, pools in cleaned_poollistdefs.items():
            itempoollistdef.ItemPools = pools

    do_next_tick(revert_pools)
    return True


class PreventDestroy(RegistrantDropper):
    Registries = dict()


def _Behavior_Destroy(caller: UObject, _f: UFunction, params: FStruct) -> bool:
    return len(PreventDestroy.Registrants(caller)) == 0
