from unrealsdk import FindObject, Log
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct

from .defines import *
from . import locations, hints
from .locations import Location, RegistrantDropper

from typing import Optional, Sequence, Tuple


def Enable() -> None:
    RunHook(
        "WillowGame.Behavior_AttachItems.ApplyBehaviorToContext",
        "LootRandomizer",
        _Behavior_AttachItems,
    )
    RunHook(
        "WillowGame.Behavior_DropItems.ApplyBehaviorToContext",
        "LootRandomizer",
        _Behavior_AttachItems,
    )
    RunHook(
        "WillowGame.Behavior_GFxMoviePlay.ApplyBehaviorToContext",
        "LootRandomizer",
        _Behavior_GFxMoviePlay,
    )
    # RunHook(
    #     "WillowGame.PopulationFactoryVendingMachine.CreatePopulationActor",
    #     "LootRandomizer",
    #     _PopulationFactoryVendingMachine,
    # )


def Disable() -> None:
    RemoveHook(
        "WillowGame.Behavior_AttachItems.ApplyBehaviorToContext",
        "LootRandomizer",
    )
    RemoveHook(
        "WillowGame.Behavior_DropItems.ApplyBehaviorToContext",
        "LootRandomizer",
    )
    RemoveHook(
        "WillowGame.PopulationFactoryVendingMachine.CreatePopulationActor",
        "LootRandomizer",
    )


class Other(Location):
    def enable(self) -> None:
        super().enable()

        if not (self.tags & ContentTags):
            self.tags |= Tag.BaseGame
        if not (self.tags & (OtherTags ^ Tag.Freebie)):
            self.tags |= Tag.Miscellaneous

        if not self.specified_rarities:
            self.rarities = [100]
            if self.tags & getattr(Tag, "Vendor", Tag.Excluded):
                self.rarities *= 8
            elif self.tags & Tag.LongMission:
                self.rarities += (100,)
            elif self.tags & Tag.VeryLongMission:
                self.rarities += (100, 100, 100)

    def __str__(self) -> str:
        return f"Other: {self.name}"


class VendingMachine(RegistrantDropper):
    Registries = dict()

    conditional: Optional[str]

    def __init__(self, path: str, conditional: Optional[str] = None) -> None:
        self.conditional = conditional
        super().__init__(path)

    def inject(self, machine: UObject) -> None:
        item = self.location.item

        if not item:
            machine.ClearInventory()
            return

        current_loot = tuple(machine.Loot[0].ItemAttachments)
        if len(current_loot) > 1 and current_loot[0].ItemPool == item.pool:
            return

        pool = self.location.prepare_pools(1)[0]

        pool.Quantity.BaseValueConstant = len(self.location.rarities) - 1

        def revert():
            pool.Quantity.BaseValueConstant = 1

        do_next_tick(revert)

        machine.Loot[0].ItemAttachments[0].ItemPool = pool
        machine.Loot[1].ItemAttachments[0].ItemPool = pool

        machine.ClearInventory()
        machine.GenerateInventory()


class Attachment(RegistrantDropper):
    Registries = dict()

    configuration: int
    attachments: Sequence[int]

    def __init__(
        self, path: str, *attachments: int, configuration: int = 0
    ) -> None:
        self.configuration = configuration
        self.attachments = attachments
        super().__init__(path)

    def should_inject(self, obj: UObject) -> bool:
        return True

    def inject(self, obj: UObject) -> None:
        for attachment_index, loot_configuration in enumerate(obj.Loot):
            if attachment_index != self.configuration:
                loot_configuration.Weight = (0, None, None, 0)

        obj_attachments = tuple(obj.Loot[self.configuration].ItemAttachments)

        attachments = (
            self.attachments
            if len(self.attachments)
            else tuple(range(len(obj_attachments)))
        )
        pools = self.location.prepare_pools(len(attachments))

        for attachment_index, obj_attachment in enumerate(obj_attachments):
            if obj_attachment.InvBalanceDefinition:
                obj_attachment.InvBalanceDefinition = None
            try:
                pool_index = attachments.index(attachment_index)
                obj_attachment.ItemPool = pools[pool_index]
                obj_attachment.PoolProbability = (1, None, None, 1)
            except ValueError:
                original_pool = obj_attachment.ItemPool
                if original_pool and original_pool.Name not in pool_whitelist:
                    obj_attachment.ItemPool = hints.padding_pool


class PositionalChest(Attachment):
    map_name: str
    position: Tuple[int, int, int]

    def __init__(
        self, path: str, map_name: str, x: int, y: int, z: int
    ) -> None:
        self.map_name = map_name.casefold()
        self.position = x, y, z
        super().__init__(path, configuration=0)

    def should_inject(self, obj: UObject) -> bool:
        position = (
            int(obj.Location.X),
            int(obj.Location.Y),
            int(obj.Location.Z),
        )
        return (
            position == self.position and locations.map_name == self.map_name
        )


def _Behavior_AttachItems(
    caller: UObject, _f: UFunction, params: FStruct
) -> bool:
    obj = params.ContextObject
    if not obj and obj.BalanceDefinitionState:
        return True

    balance = obj.BalanceDefinitionState.BalanceDefinition
    if not balance:
        return True

    balance_name = UObject.PathName(balance).split(".")[-1]
    attachments = Attachment.Registrants(balance_name)
    for attachment in attachments:
        if attachment.should_inject(obj):
            attachment.inject(obj)
            break

    return True


def _Behavior_GFxMoviePlay(
    caller: UObject, _f: UFunction, params: FStruct
) -> bool:
    machine = params.SelfObject
    if not (machine and machine.Class.Name == "WillowVendingMachine"):
        return True

    balance = machine.BalanceDefinitionState.BalanceDefinition
    if not balance:
        return True

    vendors = VendingMachine.Registrants(balance)
    if vendors:
        next(iter(vendors)).inject(machine)

    return True


# def _PopulationFactoryVendingMachine(
#     caller: UObject, _f: UFunction, params: FStruct
# ) -> bool:
#     balance = params.Opportunity.PopulationDef.ActorArchetypeList[
#         0
#     ].SpawnFactory.ObjectBalanceDefinition
#     if balance:
#         vendors = VendingMachine.Registrants(balance)
#         if vendors:
#             next(iter(vendors)).inject(balance)
#     return True
