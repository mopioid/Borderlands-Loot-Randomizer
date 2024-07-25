from unrealsdk import Log, FindObject #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct  #type: ignore

from . import defines
from .defines import Tag, do_next_tick
from .locations import Dropper, Location, MapDropper, RegistrantDropper

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
    def __init__(
        self,
        name: str,
        *droppers: Dropper,
        tags: Tag = Tag(0),
        content: Tag = Tag(0),
        rarities: Optional[Sequence[int]] = None
    ) -> None:
        if not tags & defines.ContentTags:
            tags |= Tag.BaseGame
        if not tags & defines.OtherTags:
            tags |= Tag.Miscellaneous

        if not rarities:
            rarities = [100]
            if   tags & Tag.Vendor:          rarities *= 8
            elif tags & Tag.LongMission:     rarities += (100,)
            elif tags & Tag.VeryLongMission: rarities += (100,100,100)

        super().__init__(name, *droppers, tags=tags, content=content, rarities=rarities)

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
            conditional.Expression.ConstantOperand2 = -1

        pool = self.location.prepare_pools(1, False)[0]

        if pool:
            pool.Quantity.BaseValueConstant = len(self.location.rarities) - 1
            def revert(): pool.Quantity.BaseValueConstant = 1
            defines.do_next_tick(revert)

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


class MichaelMamaril(MapDropper):
    def __init__(self) -> None:
        super().__init__("Sanctuary_P")

    def entered_map(self) -> None:
        switch = FindObject("SeqAct_RandomSwitch", "Sanctuary_Dynamic.TheWorld:PersistentLevel.Main_Sequence.SeqAct_RandomSwitch_0")
        switch.LinkCount = 2


class MichaelMAirmaril(MapDropper):
    def __init__(self) -> None:
        super().__init__("SanctuaryAir_P")

    def entered_map(self) -> None:
        switch = FindObject("SeqAct_RandomSwitch", "SanctuaryAir_Dynamic.TheWorld:PersistentLevel.Main_Sequence.SeqAct_RandomSwitch_0")
        switch.LinkCount = 2


class DahlAbandonGrave(MapDropper):
    def __init__(self) -> None:
        super().__init__("OldDust_P")

    def entered_map(self) -> None:
        grave_bpd = FindObject("BehaviorProviderDefinition", "GD_Anemone_Balance_Treasure.InteractiveObjects.InteractiveObj_Brothers_Pile:BehaviorProviderDefinition_13")
        grave_bpd.BehaviorSequences[2].BehaviorData2[3].Behavior = grave_bpd.BehaviorSequences[2].BehaviorData2[5].Behavior


class ButtstallionWithAmulet(MapDropper):
    def __init__(self) -> None:
        super().__init__("BackBurner_P")

    def entered_map(self) -> None:
        butt_ai = FindObject("AIBehaviorProviderDefinition", "GD_Anem_ButtStallion.Character.AIDef_Anem_ButtStallion:AIBehaviorProviderDefinition_1")
        butt_ai.BehaviorSequences[5].BehaviorData2[20].Behavior = butt_ai.BehaviorSequences[5].BehaviorData2[26].Behavior
        butt_ai.BehaviorSequences[5].BehaviorData2[20].LinkedVariables.ArrayIndexAndLength = 0
        butt_ai.BehaviorSequences[5].BehaviorData2[20].OutputLinks.ArrayIndexAndLength = butt_ai.BehaviorSequences[5].BehaviorData2[26].OutputLinks.ArrayIndexAndLength


def _Behavior_AttachItems(caller: UObject, function: UFunction, params: FStruct) -> bool:
    obj = params.ContextObject
    if not obj and obj.BalanceDefinitionState:
        return True

    balance = obj.BalanceDefinitionState.BalanceDefinition
    if not balance:
        return True

    attachments = Attachment.Registries.get(balance.Name)
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
    collectors = FindObject("MarketingUnlockInventoryDefinition", "GD_Globals.Unlocks.MarketingUnlock_Collectors")

    premier_items = tuple(premier.UnlockItems[0].UnlockItems)
    collectors_items = tuple(collectors.UnlockItems[0].UnlockItems)

    premier.UnlockItems[0].UnlockItems = ()
    collectors.UnlockItems[0].UnlockItems = ()

    def revert_unlocks(premier_items = premier_items, collectors_items = collectors_items) -> None:
        premier.UnlockItems[0].UnlockItems = premier_items
        collectors.UnlockItems[0].UnlockItems = collectors_items

    do_next_tick(revert_unlocks)
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
