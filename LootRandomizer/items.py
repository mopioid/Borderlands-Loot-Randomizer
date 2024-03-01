from __future__ import annotations

from unrealsdk import Log, FindObject, KeepAlive, UObject #type: ignore

from . import defines, options, seed
from .defines import BalancedItem, Probability, Tag, Hint, construct_object
from typing import Optional, Sequence, Union
import enum


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


class Item:
    path: str
    weight: Union[float, Character]
    tags: Tag

    _inventory: Optional[UObject] = None
    _balanced_item: Optional[BalancedItem] = None

    def __init__(
        self,
        path: str,
        weight: Union[float, Character] = 1.0,
        tags: Tag = Tag.BaseGame
    ) -> None:
        self.path = path; self.tags = tags; self.weight = weight

    def initialize(self) -> None:
        self._inventory = FindObject("InventoryBalanceDefinition", self.path)
        
        if isinstance(self.weight, float):
            probability = (self.weight, None, None, 1.0)
        else:
            probability = (1.0, None, self.weight.attr_init, 1.0)

        self._balanced_item = (None, self.inventory, probability, True)

    @property
    def inventory(self) -> BalancedItem:
        if not self._inventory:
            self.initialize()
        return self._inventory

    @property
    def balanced_item(self) -> BalancedItem:
        if not self._balanced_item:
            self.initialize()
        return self._balanced_item

    def validate(self) -> bool:
        return not (self.tags & ~seed.SelectedTags)
    
    def prepare(self) -> None:
        pass

    def revert(self) -> None:
        pass


class PurpleRelic(Item):
    _original_weight: Probability

    def initialize(self) -> None:
        super().initialize()
        weights = self.inventory.PartListCollection.ConsolidatedAttributeInitData
        self._original_weight = defines.convert_struct(weights[3])

    def prepare(self) -> None:
        weights = self.inventory.PartListCollection.ConsolidatedAttributeInitData
        weights[3] = (0, None, None, 0)

    def revert(self) -> None:
        weights = self.inventory.PartListCollection.ConsolidatedAttributeInitData
        weights[3] = self._original_weight


class BlueAlignmentCOM(Item):
    _original_parts: Probability

    def initialize(self) -> None:
        super().initialize()
        spec_data = self.inventory.RuntimePartListCollection.AlphaPartData
        self._original_parts = defines.convert_struct(spec_data.WeightedParts)

    def prepare(self) -> None:
        spec_data = self.inventory.RuntimePartListCollection.AlphaPartData
        spec_data.WeightedParts = [self._original_parts[i] for i in (2, 3, 5, 6, 8, 9)]

    def revert(self) -> None:
        spec_data = self.inventory.RuntimePartListCollection.AlphaPartData
        spec_data.WeightedParts = self._original_parts


class PurpleAlignmentCOM(Item):
    _original_parts: Probability

    def initialize(self) -> None:
        super().initialize()
        spec_data = self.inventory.RuntimePartListCollection.AlphaPartData
        self._original_parts = defines.convert_struct(spec_data.WeightedParts)

    def prepare(self) -> None:
        spec_data = self.inventory.RuntimePartListCollection.AlphaPartData
        spec_data.WeightedParts = [self._original_parts[i] for i in (10, 11, 12, 13, 14, 15, 16, 17, 18)]

    def revert(self) -> None:
        spec_data = self.inventory.RuntimePartListCollection.AlphaPartData
        spec_data.WeightedParts = self._original_parts


class LegendaryCOM(Item):
    index: int

    _original_coms: Probability

    def __init__(
        self,
        path: str,
        index: int,
        weight: Union[float, Character] = 1.0,
        tags: Tag = Tag.BaseGame
    ) -> None:
        super().__init__(path, weight, tags)
        self.index = index

    def initialize(self) -> None:
        super().initialize()
        self._original_coms = self.inventory.ClassModDefinitions

    def prepare(self) -> None:
        self.inventory.ClassModDefinitions = (self.inventory.ClassModDefinitions[self.index],)

    def revert(self) -> None:
        self.inventory.ClassModDefinitions = self._original_coms


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
        if self._pool:
            return self._pool

        self._pool = construct_object("ItemPoolDefinition", "ItemPool_" + self.name)
        KeepAlive(self._pool)
        self._pool.bAutoReadyItems = False
        self._pool.BalancedItems = [item.balanced_item for item in self.valid_items]

        return self._pool
    
    def validate(self) -> bool:
        self.valid_items = [item for item in self.items if item.validate()]
        if self.fallback and self.fallback.validate() and not (Tag.DragonKeep & seed.SelectedTags):
            self.valid_items.append(self.fallback)

        return bool(self.valid_items)

    def release(self) -> None:
        if hasattr(self, "valid_items"):
            del self.valid_items
        if self._pool:
            self._pool.ObjectFlags.A &= ~0x4000
            self._pool = None

    def prepare(self) -> None:
        for item in self.valid_items:
            item.prepare()

    def revert(self) -> None:
        for item in self.valid_items:
            item.revert()
