from unrealsdk import Log, FindObject #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct  #type: ignore

from . import defines, locations
from .defines import Tag
from .locations import Interactive

from typing import Optional, Sequence


class Other(locations.Location):
    def __init__(
        self,
        name: str,
        *droppers: locations.Dropper,
        tags: Tag = Tag(0),
        rarities: Optional[Sequence[int]] = None
    ) -> None:
        if not tags & defines.ContentTags:
            tags |= Tag.BaseGame
        if not tags & defines.OtherTags:
            tags |= Tag.Miscellaneous

        if not rarities:
            if tags & Tag.Vendor:
                rarities = (100, 100, 100, 100)
            else:
                rarities = (100,)

        super().__init__(name, *droppers, tags=tags, rarities=rarities)

    def __str__(self) -> str:
        return f"Other: {self.name}"


class TundraSnowmanHead(locations.MapDropper):
    def __init__(self, *map_names: str) -> None:
        super().__init__("tundraexpress_p")

    def entered_map(self) -> None:
        def head_hurt(caller: UObject, function: UFunction, params: FStruct) -> bool:
            if UObject.PathName(caller) != "GD_Episode07Data.IO_SnowManHead:BehaviorProviderDefinition_0.Behavior_DamageSourceSwitch_14":
                return True

            pools = self.prepare_pools()
            pool = pools[0] if pools else None

            params.ContextObject.Loot[0].ItemAttachments[0].ItemPool = pool
            return True
        
        RunHook("WillowGame.Behavior_DamageSourceSwitch.ApplyBehaviorToContext", "LootRandomizer.TundraSnowmanHead", head_hurt)

    def exited_map(self) -> None:
        RemoveHook("WillowGame.Behavior_DamageSourceSwitch.ApplyBehaviorToContext", "LootRandomizer.TundraSnowmanHead")


class MimicChest(Interactive):
    def inject(self, interactive: UObject) -> None:
        pools = self.prepare_pools()

        attachments = interactive.Loot[6].ItemAttachments
        for index in range(4):
            attachments[index].ItemPool = pools[0] if pools else None


class DahlAbandonGrave(locations.MapDropper):
    def __init__(self) -> None:
        super().__init__("OldDust_P")

    def entered_map(self) -> None:
        grave_bpd = FindObject("BehaviorProviderDefinition", "GD_Anemone_Balance_Treasure.InteractiveObjects.InteractiveObj_Brothers_Pile:BehaviorProviderDefinition_13")
        grave_bpd.BehaviorSequences[2].BehaviorData2[3].Behavior = grave_bpd.BehaviorSequences[2].BehaviorData2[5].Behavior


class ButtstallionWithAmulet(locations.MapDropper):
    def __init__(self) -> None:
        super().__init__("BackBurner_P")

    def entered_map(self) -> None:
        butt_ai = FindObject("AIBehaviorProviderDefinition", "GD_Anem_ButtStallion.Character.AIDef_Anem_ButtStallion:AIBehaviorProviderDefinition_1")
        butt_ai.BehaviorSequences[5].BehaviorData2[20].Behavior = butt_ai.BehaviorSequences[5].BehaviorData2[26].Behavior
        butt_ai.BehaviorSequences[5].BehaviorData2[20].LinkedVariables.ArrayIndexAndLength = 0
        butt_ai.BehaviorSequences[5].BehaviorData2[20].OutputLinks.ArrayIndexAndLength = butt_ai.BehaviorSequences[5].BehaviorData2[26].OutputLinks.ArrayIndexAndLength


class GearysUnbreakableGear(Interactive):
    def inject(self, interactive: UObject) -> None:
        pools = self.prepare_pools()
        money = FindObject("ItemPoolDefinition", "GD_Itempools.AmmoAndResourcePools.Pool_Money_1_BIG")
        pool = pools[0] if pools else money

        for index, loot_configuration in enumerate(interactive.Loot):
            if index != 1:
                loot_configuration.Weight = (0, None, None, 0)

        attachments = interactive.Loot[1].ItemAttachments
        attachments[3].ItemPool = money
        for index in range(3):
            attachments[index].ItemPool = pool

"""

- haderax launcher chest
    # logic would require toothpick and retainer
- loot goon chests
- slot machines
- tina slot machines
- roland's armory
- Gobbler slag pistol
- digi peak chests
- Wam Bam loot injectors
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
