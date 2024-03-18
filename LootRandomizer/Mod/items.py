from __future__ import annotations

from unrealsdk import Log, FindObject, KeepAlive, UObject #type: ignore

from . import defines, seed
from .defines import BalancedItem, Probability, Tag, construct_object
from .hints import Hint

import enum

from typing import Any, Optional, Sequence, Union


class Character(enum.Enum):
    attr_init: UObject

    Assassin     = "GD_PlayerClassId.Assassin"
    Mercenary    = "GD_PlayerClassId.Mercenary"
    Siren        = "GD_PlayerClassId.Siren"
    Soldier      = "GD_PlayerClassId.Soldier"
    Psycho       = "GD_LilacPackageDef.PlayerClassId.Psycho"
    Mechromancer = "GD_TulipPackageDef.PlayerClassId.Mechromancer"


def Enable() -> None:
    for character in Character:
        class_id = FindObject("PlayerClassIdentifierDefinition", character.value)

        character.attr_init = construct_object("AttributeInitializationDefinition", "Init_" + character.name)
        KeepAlive(character.attr_init)

        pc_attr = construct_object("AttributeDefinition", character.attr_init)
        nopc_attr = construct_object("AttributeDefinition", character.attr_init)

        pc_attr.bIsSimpleAttribute = True
        pc_attr.ContextResolverChain = [construct_object("PlayerControllerAttributeContextResolver", pc_attr)]

        class_resolver = construct_object("PlayerClassAttributeValueResolver", pc_attr)
        class_resolver.PlayerClassId = class_id
        pc_attr.ValueResolverChain = [class_resolver]

        nopc_attr.bIsSimpleAttribute = True
        nopc_attr.ContextResolverChain = [construct_object("NoContextNeededAttributeContextResolver", nopc_attr)]

        classcount_resolver = construct_object("PlayerClassCountAttributeValueResolver", nopc_attr)
        classcount_resolver.PlayerClassId = class_id
        nopc_attr.ValueResolverChain = [classcount_resolver]

        character.attr_init.ValueFormula = (
            True,
            (1.0, pc_attr,   None, 1.0),
            (0.0, nopc_attr, None, 1.0),
            (1.0, None,      None, 1.0),
            (0.0, None,      None, 1.0),
        )


def Disable() -> None:
    for character in Character:
        if hasattr(character, "attr_init"):
            character.attr_init.ObjectFlags.A &= ~0x4000
            del character.attr_init


class ItemPool:
    name: str
    vague_hint: Hint

    items: Sequence[Item]
    fallback: Optional[Item]
    valid_items: Sequence[Item] 

    _pool: Optional[UObject] = None #ItemPoolDefinition
    _hint_presentation: Optional[UObject] = None #InventoryCardPresentationDefinition

    def __init__(
        self,
        name: str,
        vague_hint: Hint,
        *items: Item,
        fallback: Optional[Item] = None
    ) -> None:
        self.name = name
        self.vague_hint = vague_hint
        self.items = items
        self.fallback = fallback

    @property
    def pool(self) -> UObject: #ItemPoolDefinition
        if not self._pool:
            self._pool = construct_object("ItemPoolDefinition", "ItemPool_" + self.name)
            self._pool.bAutoReadyItems = False
            self._pool.BalancedItems = [item.balanced_item for item in self.valid_items]

        return self._pool
    
    def enable(self) -> None:
        seed_tags = seed.AppliedSeed.tags
        self.valid_items = [item for item in self.items if item.tags in seed_tags]

        if len(self.valid_items) < len(self.items):
            if self.fallback and self.fallback.tags in seed_tags:
                self.valid_items.append(self.fallback)

    def disable(self) -> None:
        self.valid_items = ()

    def prepare(self) -> None:
        if not self._pool:
            self.pool

        for item in self.valid_items:
            item.prepare()

    def revert(self) -> None:
        if self._pool:
            for item in self.valid_items:
                item.revert()


DudItem = ItemPool("Nothing", Hint.Dud)


class Item:
    path: str
    weight: Union[float, Character]
    tags: Tag

    inventory: Optional[UObject] = None

    _original_gamestages: Sequence[int]

    def __init__(
        self,
        path: str,
        weight: Union[float, Character] = 1.0,
        tags: Tag = Tag(0)
    ) -> None:
        if not (tags & defines.ContentTags):
            tags |= Tag.BaseGame
        self.path = path; self.tags = tags; self.weight = weight

    def initialize(self) -> None:
        self.inventory = FindObject("InventoryBalanceDefinition", self.path)
        self._original_gamestages = tuple(
            manufacturer.Grades[0].GameStageRequirement.MinGameStage
            for manufacturer in self.inventory.Manufacturers
        )

    @property
    def balanced_item(self) -> BalancedItem:
        if not self.inventory:
            self.initialize()

        if isinstance(self.weight, float):
            probability = (self.weight, None, None, 1.0)
        else:
            probability = (1.0, None, self.weight.attr_init, 1.0)

        return (None, self.inventory, probability, True)

    def prepare(self) -> None:
        for manufacturer in self.inventory.Manufacturers:
            manufacturer.Grades[0].GameStageRequirement.MinGameStage = 1

    def revert(self) -> None:
        for gamestage, manufacturer in zip(self._original_gamestages, self.inventory.Manufacturers):
            manufacturer.Grades[0].GameStageRequirement.MinGameStage = gamestage


class PurpleRelic(Item):
    _original_weight: Probability

    def initialize(self) -> None:
        super().initialize()
        weights = self.inventory.PartListCollection.ConsolidatedAttributeInitData
        self._original_weight = defines.convert_struct(weights[3])

    def prepare(self) -> None:
        super().prepare()
        weights = self.inventory.PartListCollection.ConsolidatedAttributeInitData
        weights[3] = (0, None, None, 0)

    def revert(self) -> None:
        super().revert()
        weights = self.inventory.PartListCollection.ConsolidatedAttributeInitData
        weights[3] = self._original_weight


class ClassMod(Item):
    index: int
    _original_coms: Sequence[Any]

    def __init__(self, path: str, index: int, weight: Character, tags: Tag = Tag(0)) -> None:
        super().__init__(path, weight, tags)
        self.index = index

    def initialize(self) -> None:
        super().initialize()
        self._original_coms = tuple(self.inventory.BaseDefinition.ClassModDefinitions)

    def prepare(self) -> None:
        super().prepare()
        self.inventory.BaseDefinition.ClassModDefinitions = (
            self.inventory.BaseDefinition.ClassModDefinitions[self.index],
        )

    def revert(self) -> None:
        super().revert()
        self.inventory.BaseDefinition.ClassModDefinitions = self._original_coms


class BlueAlignmentClassMod(Item):
    _original_parts: Sequence[Any]

    def initialize(self) -> None:
        super().initialize()
        spec_data = self.inventory.RuntimePartListCollection.AlphaPartData
        self._original_parts = defines.convert_struct(spec_data.WeightedParts)

    def prepare(self) -> None:
        super().prepare()
        spec_data = self.inventory.RuntimePartListCollection.AlphaPartData
        spec_data.WeightedParts = tuple(self._original_parts[i] for i in (2, 3, 5, 6, 8, 9))

    def revert(self) -> None:
        super().revert()
        spec_data = self.inventory.RuntimePartListCollection.AlphaPartData
        spec_data.WeightedParts = self._original_parts


class PurpleAlignmentClassMod(Item):
    _original_parts: Sequence[Any]

    def initialize(self) -> None:
        super().initialize()
        spec_data = self.inventory.RuntimePartListCollection.AlphaPartData
        self._original_parts = defines.convert_struct(spec_data.WeightedParts)

    def prepare(self) -> None:
        super().prepare()
        spec_data = self.inventory.RuntimePartListCollection.AlphaPartData
        spec_data.WeightedParts = tuple(self._original_parts[10:19])

    def revert(self) -> None:
        super().revert()
        spec_data = self.inventory.RuntimePartListCollection.AlphaPartData
        spec_data.WeightedParts = self._original_parts


class Gen2ClassMod(Item):
    index: int
    _original_coms: Sequence[Any]

    def __init__(self, path: str, index: int, weight: Character, tags: Tag = Tag(0)) -> None:
        super().__init__(path, weight, tags)
        self.index = index

    def initialize(self) -> None:
        super().initialize()
        self._original_coms = tuple(self.inventory.ClassModDefinitions)

    def prepare(self) -> None:
        super().prepare()
        self.inventory.ClassModDefinitions = self.inventory.ClassModDefinitions[self.index],

    def revert(self) -> None:
        super().revert()
        self.inventory.ClassModDefinitions = self._original_coms


class Fibber(Item):
    index: int
    _original_barrels: Sequence[Any]

    def __init__(self, path: str, index: int, tags: Tag = Tag(0)) -> None:
        super().__init__(path, 1.0, tags)
        self.index = index

    def initialize(self) -> None:
        super().initialize()
        barrels = self.inventory.RuntimePartListCollection.BarrelPartData
        self._original_barrels = defines.convert_struct(barrels.WeightedParts)

    def prepare(self) -> None:
        super().prepare()
        barrels = self.inventory.RuntimePartListCollection.BarrelPartData
        barrels.WeightedParts = (self._original_barrels[self.index],)

    def revert(self) -> None:
        super().revert()
        barrels = self.inventory.RuntimePartListCollection.BarrelPartData
        barrels.WeightedParts = self._original_barrels


class BanditGrenade(Item):
    index: int

    def __init__(self, path: str, index: int, tags: Tag = Tag(0)) -> None:
        super().__init__(path, 1.0, tags)
        self.index = index

    def prepare(self) -> None:
        super().prepare()
        self.inventory.Manufacturers[self.index].Grades[0].GameStageRequirement.MaxGameStage = 0

    def revert(self) -> None:
        super().revert()
        self.inventory.Manufacturers[self.index].Grades[0].GameStageRequirement.MaxGameStage = 100


class HyperionPistol(Item):
    _original_barrels: Sequence[Any]

    def initialize(self) -> None:
        super().initialize()
        barrels = self.inventory.RuntimePartListCollection.BarrelPartData
        self._original_barrels = defines.convert_struct(barrels.WeightedParts)

    def prepare(self) -> None:
        super().prepare()
        barrels = self.inventory.RuntimePartListCollection.BarrelPartData
        barrels.WeightedParts = tuple(self._original_barrels[:8])

    def revert(self) -> None:
        super().revert()
        barrels = self.inventory.RuntimePartListCollection.BarrelPartData
        barrels.WeightedParts = self._original_barrels
