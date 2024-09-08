from unrealsdk import FindObject
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct

from .defines import *
from .locations import Location, RegistrantDropper

from typing import Optional, Sequence


def Enable() -> None:
    RunHook("WillowGame.Behavior_AttachItems.ApplyBehaviorToContext", "LootRandomizer", _Behavior_AttachItems)
    RunHook("WillowGame.PopulationFactoryVendingMachine.CreatePopulationActor", "LootRandomizer", _PopulationFactoryVendingMachine)
    RunHook("WillowGame.WillowPlayerController.GrantNewMarketingCodeBonuses", "LootRandomizer", _GrantNewMarketingCodeBonuses)
    RunHook("WillowGame.WillowPlayerController.CheckAllSideMissionsCompleteAchievement", "LootRandomizer", lambda c, f, p: False)

def Disable() -> None:
    RemoveHook("WillowGame.Behavior_AttachItems.ApplyBehaviorToContext", "LootRandomizer")
    RemoveHook("WillowGame.PopulationFactoryVendingMachine.CreatePopulationActor", "LootRandomizer")
    RemoveHook("WillowGame.WillowPlayerController.GrantNewMarketingCodeBonuses", "LootRandomizer")
    RemoveHook("WillowGame.WillowPlayerController.CheckAllSideMissionsCompleteAchievement", "LootRandomizer")


class Other(Location):
    def enable(self) -> None:
        super().enable()

        if not (self.tags & ContentTags):
            self.tags |= Tag.BaseGame
        if not (self.tags & OtherTags):
            self.tags |= Tag.Miscellaneous

        if not self.specified_rarities:
            self.rarities = [100]
            if self.tags & getattr(Tag, "Vendor", Tag.Excluded): self.rarities *= 8
            elif self.tags & Tag.LongMission: self.rarities += (100,)
            elif self.tags & Tag.VeryLongMission: self.rarities += (100,100,100)

    def __str__(self) -> str:
        return f"Other: {self.name}"


class VendingMachine(RegistrantDropper):
    Registries = dict()

    conditional: Optional[str]

    def __init__(self, path: str, conditional: Optional[str] = None) -> None:
        self.conditional = conditional
        super().__init__(path)

    def inject(self, balance: UObject) -> None:
        if self.conditional:
            conditional = FindObject("AttributeExpressionEvaluator", self.conditional)
            if conditional:
                conditional.Expression.ConstantOperand2 = -1

        pool = self.location.prepare_pools(1)[0]

        pool.Quantity.BaseValueConstant = len(self.location.rarities) - 1
        def revert(): pool.Quantity.BaseValueConstant = 1
        do_next_tick(revert)

        balance.DefaultLoot[0].ItemAttachments[0].ItemPool = pool
        balance.DefaultLoot[1].ItemAttachments[0].ItemPool = pool


class Attachment(RegistrantDropper):
    Registries = dict()

    configuration: int
    attachments: Sequence[int]

    def __init__(self, path: str, *attachments: int, configuration: int = 0) -> None:
        self.configuration = configuration; self.attachments = attachments if attachments else (0,)
        super().__init__(path)

    def inject(self, obj: UObject) -> None:
        pools = self.location.prepare_pools(len(self.attachments))

        for index, loot_configuration in enumerate(obj.Loot):
            if index != self.configuration:
                loot_configuration.Weight = (0, None, None, 0)

        obj_attachments = obj.Loot[self.configuration].ItemAttachments
        for index, pool in zip(self.attachments, pools):
            obj_attachments[index].ItemPool = pool


def _Behavior_AttachItems(caller: UObject, function: UFunction, params: FStruct) -> bool:
    obj = params.ContextObject
    if not obj and obj.BalanceDefinitionState:
        return True

    balance = obj.BalanceDefinitionState.BalanceDefinition
    if not balance:
        return True

    attachments = Attachment.Registrants(balance.Name)
    if attachments:
        next(iter(attachments)).inject(obj)

    return True

def _PopulationFactoryVendingMachine(caller: UObject, function: UFunction, params: FStruct) -> bool:
    balance = params.Opportunity.PopulationDef.ActorArchetypeList[0].SpawnFactory.ObjectBalanceDefinition
    if balance:
        vendors = VendingMachine.Registries.get(UObject.PathName(balance))
        if vendors:
            next(iter(vendors)).inject(balance)
    return True


def _GrantNewMarketingCodeBonuses(caller: UObject, function: UFunction, params: FStruct) -> bool:
    premier = FindObject("MarketingUnlockInventoryDefinition", "GD_Globals.Unlocks.MarketingUnlock_PremierClub")
    if premier:
        premier_items = tuple(premier.UnlockItems[0].UnlockItems)
        premier.UnlockItems[0].UnlockItems = ()
        def revert_premier(premier_items: Sequence[UObject] = premier_items):
            premier.UnlockItems[0].UnlockItems = premier_items
        do_next_tick(revert_premier)

    collectors = FindObject("MarketingUnlockInventoryDefinition", "GD_Globals.Unlocks.MarketingUnlock_Collectors")
    if collectors:
        collectors_items = tuple(collectors.UnlockItems[0].UnlockItems)
        collectors.UnlockItems[0].UnlockItems = ()
        def revert_collectors(collectors_items: Sequence[UObject] = collectors_items):
            collectors.UnlockItems[0].UnlockItems = collectors_items
        do_next_tick(revert_collectors)

    return True


"""
LOGIC:
    buttstallion w/ amulet requires amulet
    pot o' gold requires pot o' gold
    peak enemies past OP 0 requires moxxi's endowment
    haderax launcher chest requires toothpick + retainer

- pot of gold "boosters"

- haderax launcher chest
    # logic would require toothpick and retainer
- loot goon chests
- loot loader chests
- slot machines
- tina slot machines
- roland's armory
- Gobbler slag pistol
- digi peak chests
- Wam Bam loot injectors
    GD_Nasturtium_Lootables.InteractiveObjects.ObjectGrade_NastChest_Epic
    ^ Same as all Wam Bam red chests
- chest being stolen by yeti
- Caravan
    GD_Orchid_PlotDataMission04.Mission04.Balance_Orchid_CaravanChest
- halloween gun sacrifice
- dragon keep altar
- marcus statue suicide
- Scarlet Caravan
- Wedding balloon
    GD_Nasturtium_Lootables.IOs.IO_BossBalloons:BehaviorProviderDefinition_1.Behavior_SpawnItems_0
    GD_Nasturtium_Lootables.IOs.IO_BossBalloons:BehaviorProviderDefinition_1.Behavior_SpawnItems_2
    GD_Nasturtium_Lootables.IOs.IO_BossBalloons:BehaviorProviderDefinition_1.Behavior_SpawnItems_1
- Rotgut Fishing Chest
- Enemy("Mr. Miz",
    # GD_Aster_AmuletDoNothingData.VendingMachineGrades.ObjectGrade_VendingMachine_Pendant
    # note that logic requires amulet for buttstallion
tags=Tag.DragonKeep|Tag.LongMission),
- Butt Stallion Legendary Fart
    Behavior("GD_ButtStallion_Proto.Character.AIDef_ButtStallion_Proto:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_66"),

"""
