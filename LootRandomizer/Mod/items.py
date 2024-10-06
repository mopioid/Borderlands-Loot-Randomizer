from __future__ import annotations

from unrealsdk import Log, FindObject, KeepAlive, UObject

from .defines import *

from typing import Any, Optional, Sequence, Union, Tuple


Probability = Tuple[float, Optional[UObject], Optional[UObject], float]
BalancedItem = Tuple[Optional[UObject], UObject, Probability, bool]


def Enable() -> None:
    for character in Character:
        class_id = FindObject(
            "PlayerClassIdentifierDefinition", character.value
        )

        character.attr_init = construct_object(
            "AttributeInitializationDefinition", "Init_" + character.name
        )
        KeepAlive(character.attr_init)

        pc_attr = construct_object("AttributeDefinition", character.attr_init)
        nopc_attr = construct_object(
            "AttributeDefinition", character.attr_init
        )

        pc_attr.bIsSimpleAttribute = True
        pc_attr.ContextResolverChain = (
            construct_object(
                "PlayerControllerAttributeContextResolver", pc_attr
            ),
        )

        class_resolver = construct_object(
            "PlayerClassAttributeValueResolver", pc_attr
        )
        class_resolver.PlayerClassId = class_id
        pc_attr.ValueResolverChain = (class_resolver,)

        nopc_attr.bIsSimpleAttribute = True
        nopc_attr.ContextResolverChain = [
            construct_object(
                "NoContextNeededAttributeContextResolver", nopc_attr
            )
        ]

        classcount_resolver = construct_object(
            "PlayerClassCountAttributeValueResolver", nopc_attr
        )
        classcount_resolver.PlayerClassId = class_id
        nopc_attr.ValueResolverChain = (classcount_resolver,)

        character.attr_init.ValueFormula = (
            True,
            (1.0, pc_attr, None, 1.0),
            (0.0, nopc_attr, None, 1.0),
            (1.0, None, None, 1.0),
            (0.0, None, None, 1.0),
        )


def Disable() -> None:
    for character in Character:
        if hasattr(character, "attr_init"):
            character.attr_init.ObjectFlags.A &= ~0x4000
            del character.attr_init


class ItemPool:
    name: str
    hint: Hint
    tags: Tag = Tag(0)

    items: Sequence[Item]
    fallbacks: Sequence[Item]
    applied_items: Sequence[Item]

    _pool: Optional[UObject] = None  # ItemPoolDefinition
    _hint_presentation: Optional[UObject] = (
        None  # InventoryCardPresentationDefinition
    )

    def __init__(
        self,
        name: str,
        vague_hint: Hint,
        *items: Item,
        fallbacks: Sequence[Item] = (),
    ) -> None:
        self.name = name
        self.hint = vague_hint
        self.items = items
        self.fallbacks = fallbacks

        for item in items:
            self.tags |= item.content
        if len(fallbacks):
            self.tags |= fallbacks[0].content

    @property
    def pool(self) -> UObject:  # ItemPoolDefinition
        if not self._pool:
            self._pool = construct_object(
                "ItemPoolDefinition", "ItemPool_" + self.name
            )
            self._pool.bAutoReadyItems = False
            self._pool.BalancedItems = [
                item.balanced_item for item in self.applied_items
            ]

        return self._pool

    def apply(self, tags: Tag) -> None:
        # Log(*(item.content.name for item in self.items))
        self.applied_items = [
            item for item in self.items if item.content & tags
        ]

        if len(self.applied_items) < len(self.items):
            if len(self.fallbacks) and self.fallbacks[0].content in tags:
                self.applied_items += self.fallbacks

    def prepare(self) -> None:
        if not self._pool:
            self.pool

        for item in self.applied_items:
            item.prepare()

        do_next_tick(self.revert)

    def revert(self) -> None:
        if self._pool:
            for item in self.applied_items:
                item.revert()

    def __str__(self) -> str:
        return f"Item: {self.name}"


class Item:
    path: str
    weight: Union[float, Character]
    content: Tag

    _inventory: Optional[UObject] = None
    _original_gamestages: Sequence[int]

    def __init__(
        self,
        path: str,
        weight: Union[float, Character] = 1.0,
        content: Tag = Tag(0),
    ) -> None:
        if not (content & ContentTags):
            content |= Tag.BaseGame
        self.path = path
        self.content = content
        self.weight = weight

    def initialize(self) -> None:
        self._inventory = FindObject("InventoryBalanceDefinition", self.path)
        self._original_gamestages = tuple(
            manufacturer.Grades[0].GameStageRequirement.MinGameStage
            for manufacturer in self.inventory.Manufacturers
        )

    @property
    def inventory(self) -> UObject:  # InventoryBalanceDefinition
        if not self._inventory:
            self.initialize()
        return self._inventory  # type: ignore

    @property
    def balanced_item(self) -> BalancedItem:
        probability: Probability
        if isinstance(self.weight, float):
            probability = (self.weight, None, None, 1.0)
        elif isinstance(self.weight, Character):
            probability = (1.0, None, self.weight.attr_init, 1.0)
        else:
            raise Exception(f"Unknown weight '{self.weight}' for {self.path}")

        return (None, self.inventory, probability, True)

    def prepare(self) -> None:
        for manufacturer in self.inventory.Manufacturers:
            manufacturer.Grades[0].GameStageRequirement.MinGameStage = 1

    def revert(self) -> None:
        for gamestage, manufacturer in zip(
            self._original_gamestages, self.inventory.Manufacturers
        ):
            manufacturer.Grades[0].GameStageRequirement.MinGameStage = (
                gamestage
            )


class ClassMod(Item):
    index: int
    _original_coms: Sequence[Any]

    def __init__(
        self, path: str, index: int, weight: Character, content: Tag = Tag(0)
    ) -> None:
        super().__init__(path, weight, content)
        self.index = index

    def initialize(self) -> None:
        super().initialize()
        self._original_coms = tuple(
            self.inventory.BaseDefinition.ClassModDefinitions
        )

    def prepare(self) -> None:
        super().prepare()
        base_def = self.inventory.BaseDefinition
        com_defs = tuple(base_def.ClassModDefinitions)
        if len(com_defs) > self.index:
            base_def.ClassModDefinitions = (com_defs[self.index],)

    def revert(self) -> None:
        super().revert()
        self.inventory.BaseDefinition.ClassModDefinitions = self._original_coms


class BanditGrenade(Item):
    index: int

    def __init__(self, path: str, index: int, content: Tag = Tag(0)) -> None:
        super().__init__(path, 1.0, content)
        self.index = index

    def prepare(self) -> None:
        super().prepare()
        self.inventory.Manufacturers[self.index].Grades[
            0
        ].GameStageRequirement.MaxGameStage = 0

    def revert(self) -> None:
        super().revert()
        self.inventory.Manufacturers[self.index].Grades[
            0
        ].GameStageRequirement.MaxGameStage = 100


class MultiBarrelWeapon(Item):
    index: int
    _original_barrels: Sequence[Any]

    def __init__(self, path: str, index: int, content: Tag = Tag(0)) -> None:
        super().__init__(path, 1.0, content)
        self.index = index

    def initialize(self) -> None:
        super().initialize()
        barrels = self.inventory.RuntimePartListCollection.BarrelPartData
        self._original_barrels = convert_struct(barrels.WeightedParts)

    def prepare(self) -> None:
        super().prepare()
        barrels = self.inventory.RuntimePartListCollection.BarrelPartData
        barrels.WeightedParts = (self._original_barrels[self.index],)

    def revert(self) -> None:
        super().revert()
        barrels = self.inventory.RuntimePartListCollection.BarrelPartData
        barrels.WeightedParts = self._original_barrels


DudItem = ItemPool("Nothing", Hint.Dud)
