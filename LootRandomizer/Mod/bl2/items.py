from unrealsdk import Log, FindAll, FindObject, GetEngine
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct

from ..defines import *
from ..items import ItemPool, Item, ClassMod, BanditGrenade, MultiBarrelWeapon

from typing import Any, Sequence


class BlueAlignmentClassMod(Item):
    _original_parts: Sequence[Any]

    def initialize(self) -> None:
        super().initialize()
        spec_data = self.inventory.RuntimePartListCollection.AlphaPartData
        self._original_parts = convert_struct(spec_data.WeightedParts)

    def prepare(self) -> None:
        super().prepare()
        spec_data = self.inventory.RuntimePartListCollection.AlphaPartData
        spec_data.WeightedParts = tuple(
            self._original_parts[i] for i in (2, 3, 5, 6, 8, 9)
        )

    def revert(self) -> None:
        super().revert()
        spec_data = self.inventory.RuntimePartListCollection.AlphaPartData
        spec_data.WeightedParts = self._original_parts


class PurpleAlignmentClassMod(Item):
    _original_parts: Sequence[Any]

    def initialize(self) -> None:
        super().initialize()
        spec_data = self.inventory.RuntimePartListCollection.AlphaPartData
        self._original_parts = convert_struct(spec_data.WeightedParts)

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

    def __init__(
        self, path: str, index: int, weight: Character, tags: Tag = Tag(0)
    ) -> None:
        super().__init__(path, weight, tags)
        self.index = index

    def initialize(self) -> None:
        super().initialize()
        self._original_coms = tuple(self.inventory.ClassModDefinitions)

    def prepare(self) -> None:
        super().prepare()
        self.inventory.ClassModDefinitions = (
            self.inventory.ClassModDefinitions[self.index],
        )

    def revert(self) -> None:
        super().revert()
        self.inventory.ClassModDefinitions = self._original_coms


class HyperionPistol(Item):
    _original_barrels: Sequence[Any]

    def initialize(self) -> None:
        super().initialize()
        barrels = self.inventory.RuntimePartListCollection.BarrelPartData
        self._original_barrels = convert_struct(barrels.WeightedParts)

    def prepare(self) -> None:
        super().prepare()
        barrels = self.inventory.RuntimePartListCollection.BarrelPartData
        barrels.WeightedParts = tuple(self._original_barrels[:8])

    def revert(self) -> None:
        super().revert()
        barrels = self.inventory.RuntimePartListCollection.BarrelPartData
        barrels.WeightedParts = self._original_barrels


class PurpleRelic(Item):
    _original_grades: Sequence[Any]

    def initialize(self) -> None:
        super().initialize()
        parts = self.inventory.PartListCollection.ThetaPartData
        self._original_grades = convert_struct(parts.WeightedParts)

    def prepare(self) -> None:
        super().prepare()
        parts = self.inventory.PartListCollection.ThetaPartData
        parts.WeightedParts = tuple(self._original_grades[4:])

    def revert(self) -> None:
        super().revert()
        parts = self.inventory.PartListCollection.ThetaPartData
        parts.WeightedParts = self._original_grades


# fmt: off

Items = (
    ItemPool("Blue Infiltrator / Beast / Banshee / Engineer / Slab / Roboteer", Hint.BlueClassMod,
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_03_Rare", 0, Character.Assassin),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_03_Rare", 0, Character.Mercenary),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_03_Rare", 0, Character.Siren),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_03_Rare", 0, Character.Soldier),
        ClassMod("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_03_Rare", 0, Character.Psycho),
        ClassMod("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_03_Rare", 0, Character.Mechromancer),
    ),
    ItemPool("Blue Killer / Berserker / Binder / Grenadier / Meat / Zapper", Hint.BlueClassMod,
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_03_Rare", 1, Character.Assassin),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_03_Rare", 1, Character.Mercenary),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_03_Rare", 1, Character.Siren),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_03_Rare", 1, Character.Soldier),
        ClassMod("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_03_Rare", 1, Character.Psycho),
        ClassMod("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_03_Rare", 1, Character.Mechromancer),
    ),
    ItemPool("Blue Ninja / War Dog / Cat / Gunner / Crunch / Jill of All Trades", Hint.BlueClassMod,
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_03_Rare", 2, Character.Assassin),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_03_Rare", 2, Character.Mercenary),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_03_Rare", 2, Character.Siren),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_03_Rare", 2, Character.Soldier),
        ClassMod("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_03_Rare", 2, Character.Psycho),
        ClassMod("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_03_Rare", 2, Character.Mechromancer),
    ),
    ItemPool("Blue Professional / Devastator / Fox / Pointman / Toast / Punk", Hint.BlueClassMod,
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_03_Rare", 3, Character.Assassin),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_03_Rare", 3, Character.Mercenary),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_03_Rare", 3, Character.Siren),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_03_Rare", 3, Character.Soldier),
        ClassMod("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_03_Rare", 3, Character.Psycho),
        ClassMod("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_03_Rare", 3, Character.Mechromancer),
    ),
    ItemPool("Blue Shot / Raider / Matriarch / Rifleman / Torch / Anarchist", Hint.BlueClassMod,
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_03_Rare", 4, Character.Assassin),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_03_Rare", 4, Character.Mercenary),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_03_Rare", 4, Character.Siren),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_03_Rare", 4, Character.Soldier),
        ClassMod("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_03_Rare", 4, Character.Psycho),
        ClassMod("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_03_Rare", 4, Character.Mechromancer),
    ),
    ItemPool("Blue Sniper / Renegade / Nurse / Shock Trooper / Sickle / Technophile", Hint.BlueClassMod,
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_03_Rare", 5, Character.Assassin),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_03_Rare", 5, Character.Mercenary),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_03_Rare", 5, Character.Siren),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_03_Rare", 5, Character.Soldier),
        ClassMod("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_03_Rare", 5, Character.Psycho),
        ClassMod("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_03_Rare", 5, Character.Mechromancer),
    ),
    ItemPool("Blue Spy / Tank / Trickster / Specialist / Wound / Prodigy", Hint.BlueClassMod,
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_03_Rare", 6, Character.Assassin),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_03_Rare", 6, Character.Mercenary),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_03_Rare", 6, Character.Siren),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_03_Rare", 6, Character.Soldier),
        ClassMod("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_03_Rare", 6, Character.Psycho),
        ClassMod("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_03_Rare", 6, Character.Mechromancer),
    ),
    ItemPool("Blue Stalker / Titan / Warder / Tactician / Blister / Catalyst", Hint.BlueClassMod,
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_03_Rare", 7, Character.Assassin),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_03_Rare", 7, Character.Mercenary),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_03_Rare", 7, Character.Siren),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_03_Rare", 7, Character.Soldier),
        ClassMod("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_03_Rare", 7, Character.Psycho),
        ClassMod("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_03_Rare", 7, Character.Mechromancer),
    ),
    ItemPool("Blue Survivor / Hoarder / Witch / Veteran / Reaper / Sweetheart", Hint.BlueClassMod,
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_03_Rare", 8, Character.Assassin),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_03_Rare", 8, Character.Mercenary),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_03_Rare", 8, Character.Siren),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_03_Rare", 8, Character.Soldier),
        ClassMod("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_03_Rare", 8, Character.Psycho),
        ClassMod("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_03_Rare", 8, Character.Mechromancer),
    ),
    ItemPool("Purple Infiltrator / Beast / Banshee / Engineer / Slab / Roboteer", Hint.PurpleClassMod,
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_04_VeryRare", 0, Character.Assassin),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_04_VeryRare", 0, Character.Mercenary),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_04_VeryRare", 0, Character.Siren),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_04_VeryRare", 0, Character.Soldier),
        ClassMod("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_04_VeryRare", 0, Character.Psycho),
        ClassMod("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_04_VeryRare", 0, Character.Mechromancer),
    ),
    ItemPool("Purple Killer / Berserker / Binder / Grenadier / Meat / Zapper", Hint.PurpleClassMod,
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_04_VeryRare", 1, Character.Assassin),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_04_VeryRare", 1, Character.Mercenary),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_04_VeryRare", 1, Character.Siren),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_04_VeryRare", 1, Character.Soldier),
        ClassMod("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_04_VeryRare", 1, Character.Psycho),
        ClassMod("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_04_VeryRare", 1, Character.Mechromancer),
    ),
    ItemPool("Purple Ninja / War Dog / Cat / Gunner / Crunch / Jill of All Trades", Hint.PurpleClassMod,
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_04_VeryRare", 2, Character.Assassin),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_04_VeryRare", 2, Character.Mercenary),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_04_VeryRare", 2, Character.Siren),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_04_VeryRare", 2, Character.Soldier),
        ClassMod("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_04_VeryRare", 2, Character.Psycho),
        ClassMod("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_04_VeryRare", 2, Character.Mechromancer),
    ),
    ItemPool("Purple Professional / Devastator / Fox / Pointman / Toast / Punk", Hint.PurpleClassMod,
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_04_VeryRare", 3, Character.Assassin),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_04_VeryRare", 3, Character.Mercenary),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_04_VeryRare", 3, Character.Siren),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_04_VeryRare", 3, Character.Soldier),
        ClassMod("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_04_VeryRare", 3, Character.Psycho),
        ClassMod("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_04_VeryRare", 3, Character.Mechromancer),
    ),
    ItemPool("Purple Shot / Raider / Matriarch / Rifleman / Torch / Anarchist", Hint.PurpleClassMod,
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_04_VeryRare", 4, Character.Assassin),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_04_VeryRare", 4, Character.Mercenary),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_04_VeryRare", 4, Character.Siren),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_04_VeryRare", 4, Character.Soldier),
        ClassMod("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_04_VeryRare", 4, Character.Psycho),
        ClassMod("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_04_VeryRare", 4, Character.Mechromancer),
    ),
    ItemPool("Purple Sniper / Renegade / Nurse / Shock Trooper / Sickle / Technophile", Hint.PurpleClassMod,
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_04_VeryRare", 5, Character.Assassin),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_04_VeryRare", 5, Character.Mercenary),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_04_VeryRare", 5, Character.Siren),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_04_VeryRare", 5, Character.Soldier),
        ClassMod("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_04_VeryRare", 5, Character.Psycho),
        ClassMod("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_04_VeryRare", 5, Character.Mechromancer),
    ),
    ItemPool("Purple Spy / Tank / Trickster / Specialist / Wound / Prodigy", Hint.PurpleClassMod,
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_04_VeryRare", 6, Character.Assassin),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_04_VeryRare", 6, Character.Mercenary),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_04_VeryRare", 6, Character.Siren),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_04_VeryRare", 6, Character.Soldier),
        ClassMod("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_04_VeryRare", 6, Character.Psycho),
        ClassMod("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_04_VeryRare", 6, Character.Mechromancer),
    ),
    ItemPool("Purple Stalker / Titan / Warder / Tactician / Blister / Catalyst", Hint.PurpleClassMod,
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_04_VeryRare", 7, Character.Assassin),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_04_VeryRare", 7, Character.Mercenary),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_04_VeryRare", 7, Character.Siren),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_04_VeryRare", 7, Character.Soldier),
        ClassMod("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_04_VeryRare", 7, Character.Psycho),
        ClassMod("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_04_VeryRare", 7, Character.Mechromancer),
    ),
    ItemPool("Purple Survivor / Hoarder / Witch / Veteran / Reaper / Sweetheart", Hint.PurpleClassMod,
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_04_VeryRare", 8, Character.Assassin),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_04_VeryRare", 8, Character.Mercenary),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_04_VeryRare", 8, Character.Siren),
        ClassMod("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_04_VeryRare", 8, Character.Soldier),
        ClassMod("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_04_VeryRare", 8, Character.Psycho),
        ClassMod("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_04_VeryRare", 8, Character.Mechromancer),
    ),
    ItemPool("Blue Rogue / Monk / Cleric / Ranger / Barbarian / Necromancer", Hint.BlueClassMod,
        BlueAlignmentClassMod("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Assassin", Character.Assassin, Tag.DragonKeep),
        BlueAlignmentClassMod("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Merc", Character.Mercenary, Tag.DragonKeep),
        BlueAlignmentClassMod("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Siren", Character.Siren, Tag.DragonKeep),
        BlueAlignmentClassMod("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Soldier", Character.Soldier, Tag.DragonKeep),
        BlueAlignmentClassMod("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Psycho", Character.Psycho, Tag.DragonKeep),
        BlueAlignmentClassMod("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Mechromancer", Character.Mechromancer, Tag.DragonKeep),
    ),
    ItemPool("Purple Rogue / Monk / Cleric / Ranger / Barbarian / Necromancer", Hint.PurpleClassMod,
        PurpleAlignmentClassMod("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Assassin", Character.Assassin, Tag.DragonKeep),
        PurpleAlignmentClassMod("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Merc", Character.Mercenary, Tag.DragonKeep),
        PurpleAlignmentClassMod("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Siren", Character.Siren, Tag.DragonKeep),
        PurpleAlignmentClassMod("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Soldier", Character.Soldier, Tag.DragonKeep),
        PurpleAlignmentClassMod("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Psycho", Character.Psycho, Tag.DragonKeep),
        PurpleAlignmentClassMod("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Mechromancer", Character.Mechromancer, Tag.DragonKeep),
    ),
    ItemPool("Legendary Hunter / Berserker / Siren / Soldier / Psycho / Mechromancer", Hint.LegendaryClassMod,
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_05_Legendary", Character.Assassin),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_05_Legendary", Character.Mercenary),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_05_Legendary", Character.Siren),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_05_Legendary", Character.Soldier),
        Item("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_05_Legendary", Character.Psycho),
        Item("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_05_Legendary", Character.Mechromancer),
    ),
    ItemPool("Slayer Of Terramorphous", Hint.LegendaryClassMod,
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_06_SlayerOfTerramorphous", Character.Assassin),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_06_SlayerOfTerramorphous", Character.Mercenary),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_06_SlayerOfTerramorphous", Character.Siren),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_06_SlayerOfTerramorphous", Character.Soldier),
        Item("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_06_SlayerOfTerramorphous", Character.Psycho),
        Item("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_06_SlayerOfTerramorphous", Character.Mechromancer),
    ),
    ItemPool("Legendary Killer / Gunzerker / Binder / Engineer / Sickle / Anarchist", Hint.LegendaryClassMod,
        Gen2ClassMod("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Assassin_05_Legendary", 0, Character.Assassin, Tag.DigistructPeak),
        Gen2ClassMod("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Merc_05_Legendary", 0, Character.Mercenary, Tag.DigistructPeak),
        Gen2ClassMod("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Siren_05_Legendary", 0, Character.Siren, Tag.DigistructPeak),
        Gen2ClassMod("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Soldier_05_Legendary", 0, Character.Soldier, Tag.DigistructPeak),
        Gen2ClassMod("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Psycho_05_Legendary", 0, Character.Psycho, Tag.DigistructPeak),
        Gen2ClassMod("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Mechromancer_05_Legendary", 0, Character.Mechromancer, Tag.DigistructPeak),
    ),
    ItemPool("Legendary Ninja / Hoarder / Cat / Pointman / Torch / Catalyst", Hint.LegendaryClassMod,
        Gen2ClassMod("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Assassin_05_Legendary", 1, Character.Assassin, Tag.DigistructPeak),
        Gen2ClassMod("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Merc_05_Legendary", 1, Character.Mercenary, Tag.DigistructPeak),
        Gen2ClassMod("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Siren_05_Legendary", 1, Character.Siren, Tag.DigistructPeak),
        Gen2ClassMod("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Soldier_05_Legendary", 1, Character.Soldier, Tag.DigistructPeak),
        Gen2ClassMod("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Psycho_05_Legendary", 1, Character.Psycho, Tag.DigistructPeak),
        Gen2ClassMod("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Mechromancer_05_Legendary", 1, Character.Mechromancer, Tag.DigistructPeak),
    ),
    ItemPool("Legendary Sniper / Titan / Nurse / Ranger / Reaper / Roboteer", Hint.LegendaryClassMod,
        Gen2ClassMod("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Assassin_05_Legendary", 2, Character.Assassin, Tag.DigistructPeak),
        Gen2ClassMod("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Merc_05_Legendary", 2, Character.Mercenary, Tag.DigistructPeak),
        Gen2ClassMod("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Siren_05_Legendary", 2, Character.Siren, Tag.DigistructPeak),
        Gen2ClassMod("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Soldier_05_Legendary", 2, Character.Soldier, Tag.DigistructPeak),
        Gen2ClassMod("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Psycho_05_Legendary", 2, Character.Psycho, Tag.DigistructPeak),
        Gen2ClassMod("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Mechromancer_05_Legendary", 2, Character.Mechromancer, Tag.DigistructPeak),
    ),

    ItemPool("Aggression Relic", Hint.PurpleRelic,
        PurpleRelic("GD_Artifacts.A_Item.A_AggressionA_Rare"),
        PurpleRelic("GD_Artifacts.A_Item.A_AggressionB_Rare"),
        PurpleRelic("GD_Artifacts.A_Item.A_AggressionC_Rare"),
        PurpleRelic("GD_Artifacts.A_Item.A_AggressionD_Rare"),
        PurpleRelic("GD_Artifacts.A_Item.A_AggressionE_Rare"),
        PurpleRelic("GD_Artifacts.A_Item.A_AggressionF_Rare"),
    ),
    ItemPool("Elemental Relic", Hint.PurpleRelic,
        PurpleRelic("GD_Artifacts.A_Item.A_Elemental_Rare", 2.0),
        PurpleRelic("GD_Artifacts.A_Item.A_Elemental_Status_Rare", 3.0),
    ),
    ItemPool("Proficiency Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_Proficiency_Rare")),
    ItemPool("Protection Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_Protection_Rare")),
    ItemPool("Resistance Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_Resistance_Rare")),
    ItemPool("Stockpile Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_Stockpile_Rare")),
    ItemPool("Strength Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_Strength_Rare")),
    ItemPool("Tenacity Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_Tenacity_Rare")),
    ItemPool("Vitality Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_Vitality_Rare")),
    ItemPool("Bandit Allegiance Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_AllegianceA_Rare")),
    ItemPool("Dahl Allegiance Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_AllegianceB_Rare")),
    ItemPool("Hyperion Allegiance Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_AllegianceC_Rare")),
    ItemPool("Jakobs Allegiance Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_AllegianceD_Rare")),
    ItemPool("Maliwan Allegiance Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_AllegianceE_Rare")),
    ItemPool("Tediore Allegiance Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_AllegianceF_Rare")),
    ItemPool("Torgue Allegiance Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_AllegianceG_Rare")),
    ItemPool("Vladof Allegiance Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_AllegianceH_Rare")),

    ItemPool("The Afterburner", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_Afterburner")),
    ItemPool("Deputy's Badge", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_Deputy")),
    ItemPool("Moxxi's Endowment", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_Endowment")),
    ItemPool("Lucrative Opportunity", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_Opportunity")),
    ItemPool("Sheriff's Badge", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_Sheriff")),
    ItemPool("Blood of Terramorphous", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_Terramorphous")),
    ItemPool("Vault Hunter's Relic", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_VaultHunter")),

    ItemPool("Fire Burst / Tesla / Corrosive Cloud", Hint.PurpleGrenade, Item("GD_GrenadeMods.A_Item.GM_AreaEffect_4_VeryRare")),
    ItemPool("Bouncing Betty", Hint.PurpleGrenade, BanditGrenade("GD_GrenadeMods.A_Item.GM_BouncingBetty_4_VeryRare", 1)),
    ItemPool("Jumpin Biddy", Hint.PurpleGrenade, BanditGrenade("GD_GrenadeMods.A_Item.GM_BouncingBetty_4_VeryRare", 0)),
    ItemPool("MIRV", Hint.PurpleGrenade, BanditGrenade("GD_GrenadeMods.A_Item.GM_Mirv_4_VeryRare", 1)),
    ItemPool("Mruv / Mrvur / Murrv / Muvr / Muvv", Hint.PurpleGrenade, BanditGrenade("GD_GrenadeMods.A_Item.GM_Mirv_4_VeryRare", 0)),
    ItemPool("Singularity", Hint.PurpleGrenade, Item("GD_GrenadeMods.A_Item.GM_Singularity_4_VeryRare")),
    ItemPool("Grenade", Hint.PurpleGrenade, BanditGrenade("GD_GrenadeMods.A_Item.GM_Standard_4_VeryRare", 1)),
    ItemPool("gurnade", Hint.PurpleGrenade, BanditGrenade("GD_GrenadeMods.A_Item.GM_Standard_4_VeryRare", 0)),
    ItemPool("Transfusion", Hint.PurpleGrenade, Item("GD_GrenadeMods.A_Item.GM_Transfusion_4_VeryRare")),

    ItemPool("Fuster Cluck", Hint.UniqueGrenade, Item("GD_GrenadeMods.A_Item_Custom.GM_FusterCluck")),
    ItemPool("Kiss of Death", Hint.UniqueGrenade, Item("GD_GrenadeMods.A_Item_Custom.GM_KissOfDeath")),
    ItemPool("Sky Rocket", Hint.UniqueGrenade, Item("GD_GrenadeMods.A_Item_Custom.GM_SkyRocket")),
    ItemPool("Breath of Terramorphous", Hint.UniqueGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_FlameSpurt")),

    ItemPool("Bonus Package", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_BonusPackage")),
    ItemPool("Bouncing Bonny", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_BouncingBonny")),
    ItemPool("Fastball", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_Fastball")),
    ItemPool("Fire Bee", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_FireBee")),
    ItemPool("Leech", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_Leech")),
    ItemPool("Nasty Surprise", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_NastySurprise")),
    ItemPool("Pandemic", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_Pandemic")),
    ItemPool("Quasar", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_Quasar")),
    ItemPool("Rolling Thunder", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_RollingThunder")),
    ItemPool("Storm Front", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_StormFront")),

    ItemPool("Shield", Hint.PurpleShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_04_VeryRare")),
    ItemPool("Absorb Shield", Hint.PurpleShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_04_VeryRare")),
    ItemPool("Adaptive Shield", Hint.PurpleShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_04_VeryRare")),
    ItemPool("Amplify Shield", Hint.PurpleShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Impact_04_VeryRare")),
    ItemPool("Booster Shield", Hint.PurpleShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_04_VeryRare")),
    ItemPool("Maylay Shield", Hint.PurpleShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_04_VeryRare")),
    ItemPool("Nova Shield", Hint.PurpleShield,
        Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Explosive_04_VeryRare"),
        Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Fire_04_VeryRare"),
        Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Shock_04_VeryRare"),
        Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Acid_04_VeryRare"),
    ),
    ItemPool("Spike Shield", Hint.PurpleShield,
        Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Explosive_04_VeryRare"),
        Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Fire_04_VeryRare"),
        Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Shock_04_VeryRare"),
        Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Acid_04_VeryRare"),
    ),
    ItemPool("Turtle Shield", Hint.PurpleShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Juggernaut_04_VeryRare")),

    ItemPool("1340 Shield", Hint.UniqueShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_1340")),
    ItemPool("Aequitas", Hint.UniqueShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_Equitas")),
    ItemPool("Pot O' Gold", Hint.UniqueShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_PotOGold")),
    ItemPool("Deadly Bloom", Hint.UniqueShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Explosive_DeadlyBloom")),
    ItemPool("Order", Hint.UniqueShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_Order")),
    ItemPool("Cracked Sash", Hint.UniqueShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_CrackedSash")),
    ItemPool("Love Thumper", Hint.UniqueShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_04_LoveThumper")),

    ItemPool("The Sham", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryNormal")),
    ItemPool("The Transformer", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryShock")),
    ItemPool("Whisky Tango Foxtrot", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_05_Legendary")),
    ItemPool("Neogenator", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_05_Legendary")),
    ItemPool("The Bee", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Impact_05_Legendary")),
    ItemPool("Fabled Tortoise", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Juggernaut_05_Legendary")),
    ItemPool("Flame of the Firehawk", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Phoenix")),
    ItemPool("Black Hole", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Singularity")),
    ItemPool("Hide of Terramorphous", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_ThresherRaid")),
    ItemPool("Impaler", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Acid_05_Legendary")),
    ItemPool("The Cradle", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_05_Legendary")),

    ItemPool("Bandit Assault Rifle", Hint.PurpleAR,
        Item("GD_Aster_Weapons.AssaultRifles.AR_Bandit_4_Quartz", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_AssaultRifle.A_Weapons.AR_Bandit_4_VeryRare"),
    ),
    ItemPool("Dahl Assault Rifle", Hint.PurpleAR,
        Item("GD_Aster_Weapons.AssaultRifles.AR_Dahl_4_Emerald", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_AssaultRifle.A_Weapons.AR_Dahl_4_VeryRare"),
    ),
    ItemPool("Jakobs Assault Rifle", Hint.PurpleAR,
        Item("GD_Aster_Weapons.AssaultRifles.AR_Jakobs_4_Citrine", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_AssaultRifle.A_Weapons.AR_Jakobs_4_VeryRare"),
    ),
    ItemPool("Torgue Assault Rifle", Hint.PurpleAR,
        Item("GD_Aster_Weapons.AssaultRifles.AR_Torgue_4_Rock", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_AssaultRifle.A_Weapons.AR_Torgue_4_VeryRare"),
    ),
    ItemPool("Vladof Assault Rifle", Hint.PurpleAR,
        Item("GD_Aster_Weapons.AssaultRifles.AR_Vladof_4_Garnet", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_AssaultRifle.A_Weapons.AR_Vladof_4_VeryRare"),
    ),
    ItemPool("E-tech Assault Rifle", Hint.EtechWeapon,
        Item("GD_Weap_AssaultRifle.A_Weapons.AR_Bandit_5_Alien"),
        Item("GD_Weap_AssaultRifle.A_Weapons.AR_Dahl_5_Alien"),
        Item("GD_Weap_AssaultRifle.A_Weapons.AR_Vladof_5_Alien"),
    ),

    ItemPool("Bandit Rocket Launcher", Hint.PurpleLauncher, Item("GD_Weap_Launchers.A_Weapons.RL_Bandit_4_VeryRare")),
    ItemPool("Tediore Rocket Launcher", Hint.PurpleLauncher, Item("GD_Weap_Launchers.A_Weapons.RL_Tediore_4_VeryRare")),
    ItemPool("Vladof Rocket Launcher", Hint.PurpleLauncher, Item("GD_Weap_Launchers.A_Weapons.RL_Vladof_4_VeryRare")),
    ItemPool("Maliwan Rocket Launcher", Hint.PurpleLauncher, Item("GD_Weap_Launchers.A_Weapons.RL_Maliwan_4_VeryRare")),
    ItemPool("Torgue Rocket Launcher", Hint.PurpleLauncher, Item("GD_Weap_Launchers.A_Weapons.RL_Torgue_4_VeryRare")),
    ItemPool("E-tech Rocket Launcher", Hint.EtechWeapon,
        Item("GD_Weap_Launchers.A_Weapons.RL_Bandit_5_Alien"),
        Item("GD_Weap_Launchers.A_Weapons.RL_Tediore_5_Alien"),
        Item("GD_Weap_Launchers.A_Weapons.RL_Vladof_5_Alien"),
        Item("GD_Weap_Launchers.A_Weapons.RL_Maliwan_5_Alien"),
    ),

    ItemPool("Bandit Pistol", Hint.PurplePistol,
        Item("GD_Aster_Weapons.Pistols.Pistol_Bandit_4_Quartz", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_Pistol.A_Weapons.Pistol_Bandit_4_VeryRare"),
    ),
    ItemPool("Tediore Pistol", Hint.PurplePistol,
        Item("GD_Aster_Weapons.Pistols.Pistol_Tediore_4_CubicZerconia", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_Pistol.A_Weapons.Pistol_Tediore_4_VeryRare"),
    ),
    ItemPool("Dahl Pistol", Hint.PurplePistol,
        Item("GD_Aster_Weapons.Pistols.Pistol_Dahl_4_Emerald", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_Pistol.A_Weapons.Pistol_Dahl_4_VeryRare"),
    ),
    ItemPool("Vladof Pistol", Hint.PurplePistol,
        Item("GD_Aster_Weapons.Pistols.Pistol_Vladof_4_Garnet", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_Pistol.A_Weapons.Pistol_Vladof_4_VeryRare"),
    ),
    ItemPool("Torgue Pistol", Hint.PurplePistol,
        Item("GD_Aster_Weapons.Pistols.Pistol_Torgue_4_Rock", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_Pistol.A_Weapons.Pistol_Torgue_4_VeryRare"),
    ),
    ItemPool("Maliwan Pistol", Hint.PurplePistol,
        Item("GD_Aster_Weapons.Pistols.Pistol_Maliwan_4_Aquamarine", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_Pistol.A_Weapons.Pistol_Maliwan_4_VeryRare"),
    ),
    ItemPool("Jakobs Pistol", Hint.PurplePistol,
        Item("GD_Aster_Weapons.Pistols.Pistol_Jakobs_4_Citrine", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_Pistol.A_Weapons.Pistol_Jakobs_4_VeryRare"),
    ),
    ItemPool("Hyperion Pistol", Hint.PurplePistol,
        HyperionPistol("GD_Aster_Weapons.Pistols.Pistol_Hyperion_4_Diamond", content=Tag.DragonKeep),
        fallback=HyperionPistol("GD_Weap_Pistol.A_Weapons.Pistol_Hyperion_4_VeryRare"),
    ),
    ItemPool("E-tech Pistol", Hint.EtechWeapon,
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Bandit_5_Alien"),
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Tediore_5_Alien"),
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Dahl_5_Alien"),
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Vladof_5_Alien"),
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Maliwan_5_Alien"),
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Hyperion_5_Alien"),
    ),

    ItemPool("Bandit Shotgun", Hint.PurpleShotgun,
        Item("GD_Aster_Weapons.Shotguns.SG_Bandit_4_Quartz", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_Shotgun.A_Weapons.SG_Bandit_4_VeryRare"),
    ),
    ItemPool("Tediore Shotgun", Hint.PurpleShotgun,
        Item("GD_Aster_Weapons.Shotguns.SG_Tediore_4_CubicZerconia", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_Shotgun.A_Weapons.SG_Tediore_4_VeryRare"),
    ),
    ItemPool("Torgue Shotgun", Hint.PurpleShotgun,
        Item("GD_Aster_Weapons.Shotguns.SG_Torgue_4_Rock", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_Shotgun.A_Weapons.SG_Torgue_4_VeryRare"),
    ),
    ItemPool("Jakobs Shotgun", Hint.PurpleShotgun,
        Item("GD_Aster_Weapons.Shotguns.SG_Jakobs_4_Citrine", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_Shotgun.A_Weapons.SG_Jakobs_4_VeryRare"),
    ),
    ItemPool("Hyperion Shotgun", Hint.PurpleShotgun,
        Item("GD_Aster_Weapons.Shotguns.SG_Hyperion_4_Diamond", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_Shotgun.A_Weapons.SG_Hyperion_4_VeryRare"),
    ),
    ItemPool("E-tech Shotgun", Hint.EtechWeapon,
        Item("GD_Weap_Shotgun.A_Weapons.SG_Bandit_5_Alien"),
        Item("GD_Weap_Shotgun.A_Weapons.SG_Tediore_5_Alien"),
        Item("GD_Weap_Shotgun.A_Weapons.SG_Hyperion_5_Alien"),
    ),

    ItemPool("Bandit SMG", Hint.PurpleSMG,
        Item("GD_Aster_Weapons.SMGs.SMG_Bandit_4_Quartz", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_SMG.A_Weapons.SMG_Bandit_4_VeryRare"),
    ),
    ItemPool("Tediore SMG", Hint.PurpleSMG,
        Item("GD_Aster_Weapons.SMGs.SMG_Tediore_4_CubicZerconia", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_SMG.A_Weapons.SMG_Tediore_4_VeryRare"),
    ),
    ItemPool("Dahl SMG", Hint.PurpleSMG,
        Item("GD_Aster_Weapons.SMGs.SMG_Dahl_4_Emerald", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_SMG.A_Weapons.SMG_Dahl_4_VeryRare"),
    ),
    ItemPool("Maliwan SMG", Hint.PurpleSMG,
        Item("GD_Aster_Weapons.SMGs.SMG_Maliwan_4_Aquamarine", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_SMG.A_Weapons.SMG_Maliwan_4_VeryRare"),
    ),
    ItemPool("Hyperion SMG", Hint.PurpleSMG,
        Item("GD_Aster_Weapons.SMGs.SMG_Hyperion_4_Diamond", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_SMG.A_Weapons.SMG_Hyperion_4_VeryRare"),
    ),
    ItemPool("E-tech SMG", Hint.EtechWeapon,
        Item("GD_Weap_SMG.A_Weapons.SMG_Tediore_5_Alien"),
        Item("GD_Weap_SMG.A_Weapons.SMG_Bandit_5_Alien"),
        Item("GD_Weap_SMG.A_Weapons.SMG_Dahl_5_Alien"),
        Item("GD_Weap_SMG.A_Weapons.SMG_Maliwan_5_Alien"),
        Item("GD_Weap_SMG.A_Weapons.SMG_Hyperion_5_Alien"),
    ),

    ItemPool("Dahl Sniper Rifle", Hint.PurpleSniper,
        Item("GD_Aster_Weapons.Snipers.SR_Dahl_4_Emerald", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Dahl_4_VeryRare"),
    ),
    ItemPool("Vladof Sniper Rifle", Hint.PurpleSniper,
        Item("GD_Aster_Weapons.Snipers.SR_Vladof_4_Garnet", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Vladof_4_VeryRare"),
    ),
    ItemPool("Maliwan Sniper Rifle", Hint.PurpleSniper,
        Item("GD_Aster_Weapons.Snipers.SR_Maliwan_4_Aquamarine", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Maliwan_4_VeryRare"),
    ),
    ItemPool("Jakobs Sniper Rifle", Hint.PurpleSniper,
        Item("GD_Aster_Weapons.Snipers.SR_Jakobs_4_Citrine", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Jakobs_4_VeryRare"),
    ),
    ItemPool("Hyperion Sniper Rifle", Hint.PurpleSniper,
        Item("GD_Aster_Weapons.Snipers.SR_Hyperion_4_Diamond", content=Tag.DragonKeep),
        fallback=Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Hyperion_4_VeryRare"),
    ),
    ItemPool("E-tech Sniper Rifle", Hint.EtechWeapon,
        Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Dahl_5_Alien"),
        Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Vladof_5_Alien"),
        Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Maliwan_5_Alien"),
        Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Hyperion_5_Alien"),
    ),

    ItemPool("Gearbox SMG", Hint.UniqueSMG, Item("GD_Weap_SMG.A_Weapons_Unique.SMG_Gearbox_1")),
    ItemPool("Lascaux", Hint.UniqueSMG, Item("GD_Weap_SMG.A_Weapons_Unique.SMG_Dahl_3_Lascaux")),
    ItemPool("Bad Touch", Hint.UniqueSMG, Item("GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_BadTouch")),
    ItemPool("Good Touch", Hint.UniqueSMG, Item("GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_GoodTouch")),
    ItemPool("Commerce", Hint.UniqueSMG, Item("GD_Weap_SMG.A_Weapons_Unique.SMG_Hyperion_3_Commerce")),
    ItemPool("Bone Shredder", Hint.UniqueSMG, Item("GD_Weap_SMG.A_Weapons_Unique.SMG_Bandit_3_BoneShredder")),
    ItemPool("Chulainn", Hint.UniqueSMG, Item("GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_Chulainn")),
    ItemPool("Bane", Hint.UniqueSMG, Item("GD_Weap_SMG.A_Weapons_Unique.SMG_Hyperion_3_Bane")),

    ItemPool("Gwen's Head", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_GwensHead")),
    ItemPool("Judge", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Judge")),
    ItemPool("Tinderbox", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Bandit_3_Tenderbox")),
    ItemPool("Law", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Law")),
    ItemPool("Teapot", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_Teapot")),
    ItemPool("Shotgun Fibber", Hint.UniquePistol, MultiBarrelWeapon("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_Fibber", 0)),
    ItemPool("Ricochet Fibber", Hint.UniquePistol, MultiBarrelWeapon("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_Fibber", 1)),
    ItemPool("Crit Fibber", Hint.UniquePistol, MultiBarrelWeapon("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_Fibber", 2)),
    ItemPool("Rubi", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Maliwan_3_Rubi")),
    ItemPool("Veritas", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Vladof_3_Veritas")),
    ItemPool("Dahlminator", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_Dahlminator")),
    ItemPool("Lady Fist", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_LadyFist")),

    ItemPool("Gearbox Sniper Rifle", Hint.UniqueSniper, Item("GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Gearbox_1")),
    ItemPool("Fremington's Edge", Hint.UniqueSniper, Item("GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_FremingtonsEdge")),
    ItemPool("Buffalo", Hint.UniqueSniper, Item("GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Jakobs_3_Buffalo")),
    ItemPool("Trespasser", Hint.UniqueSniper, Item("GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Jakobs_3_Tresspasser")),
    ItemPool("Sloth", Hint.UniqueSniper, Item("GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Dahl_3_Sloth")),
    ItemPool("Morningstar", Hint.UniqueSniper, Item("GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_Morningstar")),
    ItemPool("Chère-amie", Hint.UniqueSniper, Item("GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Maliwan_3_ChereAmie")),

    ItemPool("Dog", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_Dog")),
    ItemPool("Teeth of Terramorphous", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_Teeth")),
    ItemPool("Blockhead", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Tediore_3_Blockhead")),
    ItemPool("Landscaper", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Torgue_3_Landscaper")),
    ItemPool("Triquetra", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_3_Triquetra")),
    ItemPool("Heart Breaker", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_HeartBreaker")),
    ItemPool("Octo", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Tediore_3_Octo")),
    ItemPool("RokSalt", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_RokSalt")),
    ItemPool("Shotgun 1340", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_Shotgun1340")),
    ItemPool("Tidal Wave", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_3_TidalWave")),

    ItemPool("Hive", Hint.UniqueLauncher, Item("GD_Weap_Launchers.A_Weapons_Unique.RL_Maliwan_3_TheHive")),
    ItemPool("Creamer", Hint.UniqueLauncher, Item("GD_Weap_Launchers.A_Weapons_Unique.RL_Torgue_3_Creamer")),
    ItemPool("Roaster", Hint.UniqueLauncher, Item("GD_Weap_Launchers.A_Weapons_Unique.RL_Bandit_3_Roaster")),

    ItemPool("Gearbox Assault Rifle", Hint.UniqueAR, Item("GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Dahl_1_GBX")),
    ItemPool("Hail", Hint.UniqueAR, Item("GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Vladof_3_Hail")),
    ItemPool("Scorpio", Hint.UniqueAR, Item("GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Dahl_3_Scorpio")),
    ItemPool("Evil Smasher", Hint.UniqueAR, Item("GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Torgue_3_EvilSmasher")),
    ItemPool("Stomper", Hint.UniqueAR, Item("GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Jakobs_3_Stomper")),

    ItemPool("Sledge's Shotgun", Hint.LegendaryShotgun, Item("GD_Weap_Shotgun.A_Weapons_Legendary.SG_Bandit_5_SledgesShotgun")),
    ItemPool("Striker", Hint.LegendaryShotgun, Item("GD_Weap_Shotgun.A_Weapons_Legendary.SG_Jakobs_5_Striker")),
    ItemPool("Deliverance", Hint.LegendaryShotgun, Item("GD_Weap_Shotgun.A_Weapons_Legendary.SG_Tediore_5_Deliverance")),
    ItemPool("Flakker", Hint.LegendaryShotgun, Item("GD_Weap_Shotgun.A_Weapons_Legendary.SG_Torgue_5_Flakker")),
    ItemPool("Conference Call", Hint.LegendaryShotgun, Item("GD_Weap_Shotgun.A_Weapons_Legendary.SG_Hyperion_5_ConferenceCall")),

    ItemPool("Nukem", Hint.LegendaryLauncher, Item("GD_Weap_Launchers.A_Weapons_Legendary.RL_Torgue_5_Nukem")),
    ItemPool("Pyrophobia", Hint.LegendaryLauncher, Item("GD_Weap_Launchers.A_Weapons_Legendary.RL_Maliwan_5_Pyrophobia")),
    ItemPool("Bunny", Hint.LegendaryLauncher, Item("GD_Weap_Launchers.A_Weapons_Legendary.RL_Tediore_5_Bunny")),
    ItemPool("Badaboom", Hint.LegendaryLauncher, Item("GD_Weap_Launchers.A_Weapons_Legendary.RL_Bandit_5_BadaBoom")),
    ItemPool("Mongol", Hint.LegendaryLauncher, Item("GD_Weap_Launchers.A_Weapons_Legendary.RL_Vladof_5_Mongol")),
    ItemPool("Norfleet", Hint.LegendaryLauncher, Item("GD_Weap_Launchers.A_Weapons_Unique.RL_Maliwan_Alien_Norfleet")),

    ItemPool("Bitch", Hint.LegendarySMG, Item("GD_Weap_SMG.A_Weapons_Legendary.SMG_Hyperion_5_Bitch")),
    ItemPool("Emperor", Hint.LegendarySMG, Item("GD_Weap_SMG.A_Weapons_Legendary.SMG_Dahl_5_Emperor")),
    ItemPool("Baby Maker", Hint.LegendarySMG, Item("GD_Weap_SMG.A_Weapons_Legendary.SMG_Tediore_5_BabyMaker")),
    ItemPool("Hellfire", Hint.LegendarySMG, Item("GD_Weap_SMG.A_Weapons_Legendary.SMG_Maliwan_5_HellFire")),
    ItemPool("Slagga", Hint.LegendarySMG, Item("GD_Weap_SMG.A_Weapons_Legendary.SMG_Bandit_5_Slagga")),

    ItemPool("Thunderball Fists", Hint.LegendaryPistol, Item("GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Maliwan_5_ThunderballFists")),
    ItemPool("Hornet", Hint.LegendaryPistol, Item("GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Dahl_5_Hornet")),
    ItemPool("Gub", Hint.LegendaryPistol, Item("GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Bandit_5_Gub")),
    ItemPool("Maggie", Hint.LegendaryPistol, Item("GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Jakobs_5_Maggie")),
    ItemPool("Infinity", Hint.LegendaryPistol, Item("GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Vladof_5_Infinity")),
    ItemPool("Gunerang", Hint.LegendaryPistol, Item("GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Tediore_5_Gunerang")),
    ItemPool("Unkempt Harold", Hint.LegendaryPistol, Item("GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Torgue_5_Calla")),
    ItemPool("Logan's Gun", Hint.LegendaryPistol, Item("GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Hyperion_5_LogansGun")),

    ItemPool("Lyudmila", Hint.LegendarySniper, Item("GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Vladof_5_Lyudmila")),
    ItemPool("Skullmasher", Hint.LegendarySniper, Item("GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Jakobs_5_Skullmasher")),
    ItemPool("Invader", Hint.LegendarySniper, Item("GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Hyperion_5_Invader")),
    ItemPool("Pitchfork", Hint.LegendarySniper, Item("GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Dahl_5_Pitchfork")),
    ItemPool("Volcano", Hint.LegendarySniper, Item("GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Maliwan_5_Volcano")),
    ItemPool("Longbow", Hint.LegendarySniper, Item("GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_Longbow")),

    ItemPool("Madhous!", Hint.LegendaryAR, Item("GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Bandit_5_Madhouse")),
    ItemPool("Hammer Buster", Hint.LegendaryAR, Item("GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Jakobs_5_HammerBuster")),
    ItemPool("Veruc", Hint.LegendaryAR, Item("GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Dahl_5_Veruc")),
    ItemPool("KerBlaster", Hint.LegendaryAR, Item("GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Torgue_5_KerBlaster")),
    ItemPool("Shredifier", Hint.LegendaryAR, Item("GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Vladof_5_Sherdifier")),


    ItemPool("Captain Blade's Otto Idol", Hint.UniqueRelic, Item("GD_Orchid_Artifacts.A_Item_Unique.A_Blade", content=Tag.PiratesBooty)),
    ItemPool("Blood of the Seraphs", Hint.SeraphItem, Item("GD_Orchid_Artifacts.A_Item_Unique.A_SeraphBloodRelic", content=Tag.PiratesBooty)),

    ItemPool("Midnight Star", Hint.UniqueGrenade, Item("GD_Orchid_GrenadeMods.A_Item_Custom.GM_Blade", content=Tag.PiratesBooty)),

    ItemPool("Evolution", Hint.SeraphItem, Item("GD_Orchid_RaidWeapons.Shield.Anshin.Orchid_Seraph_Anshin_Shield_Balance", content=Tag.PiratesBooty)),
    ItemPool("Manly Man Shield", Hint.UniqueShield, Item("GD_Orchid_Shields.A_Item_Custom.S_BladeShield", content=Tag.PiratesBooty)),

    ItemPool("Greed", Hint.UniquePistol, Item("GD_Orchid_BossWeapons.Pistol.Pistol_Jakobs_ScarletsGreed", content=Tag.PiratesBooty)),
    ItemPool("12 Pounder", Hint.UniqueLauncher, Item("GD_Orchid_BossWeapons.Launcher.RL_Torgue_3_12Pounder", content=Tag.PiratesBooty)),
    ItemPool("Little Evie", Hint.UniquePistol, Item("GD_Orchid_BossWeapons.Pistol.Pistol_Maliwan_3_LittleEvie", content=Tag.PiratesBooty)),
    ItemPool("Stinkpot", Hint.UniqueAR, Item("GD_Orchid_BossWeapons.AssaultRifle.AR_Jakobs_3_Stinkpot", content=Tag.PiratesBooty)),
    ItemPool("Devastator", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.Pistol.Devastator.Orchid_Seraph_Devastator_Balance", content=Tag.PiratesBooty)),
    ItemPool("Tattler", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.SMG.Tattler.Orchid_Seraph_Tattler_Balance", content=Tag.PiratesBooty)),
    ItemPool("Retcher", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.Shotgun.Spitter.Orchid_Seraph_Spitter_Balance", content=Tag.PiratesBooty)),
    ItemPool("Actualizer", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.SMG.Actualizer.Orchid_Seraph_Actualizer_Balance", content=Tag.PiratesBooty)),
    ItemPool("Seraphim", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.AssaultRifle.Seraphim.Orchid_Seraph_Seraphim_Balance", content=Tag.PiratesBooty)),
    ItemPool("Patriot", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.sniper.Patriot.Orchid_Seraph_Patriot_Balance", content=Tag.PiratesBooty)),
    ItemPool("Ahab", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.RPG.Ahab.Orchid_Seraph_Ahab_Balance", content=Tag.PiratesBooty)),
    ItemPool("Rapier", Hint.UniqueAR, Item("GD_Orchid_BossWeapons.AssaultRifle.AR_Vladof_3_Rapier", content=Tag.PiratesBooty)),
    ItemPool("Jolly Roger", Hint.UniqueShotgun, Item("GD_Orchid_BossWeapons.Shotgun.SG_Bandit_3_JollyRoger", content=Tag.PiratesBooty)),
    ItemPool("Orphan Maker", Hint.UniqueShotgun, Item("GD_Orchid_BossWeapons.Shotgun.SG_Jakobs_3_OrphanMaker", content=Tag.PiratesBooty)),
    ItemPool("Sand Hawk", Hint.UniqueSMG, Item("GD_Orchid_BossWeapons.SMG.SMG_Dahl_3_SandHawk", content=Tag.PiratesBooty)),
    ItemPool("Pimpernel", Hint.UniqueSniper, Item("GD_Orchid_BossWeapons.SniperRifles.Sniper_Maliwan_3_Pimpernel", content=Tag.PiratesBooty)),

    
    ItemPool("Big Boom Blaster", Hint.SeraphItem, Item("GD_Iris_SeraphItems.BigBoomBlaster.Iris_Seraph_Shield_Booster_Balance", content=Tag.CampaignOfCarnage)),
    ItemPool("Hoplite", Hint.SeraphItem, Item("GD_Iris_SeraphItems.Hoplite.Iris_Seraph_Shield_Juggernaut_Balance", content=Tag.CampaignOfCarnage)),
    ItemPool("Pun-chee", Hint.SeraphItem, Item("GD_Iris_SeraphItems.Pun-chee.Iris_Seraph_Shield_Pun-chee_Balance", content=Tag.CampaignOfCarnage)),
    ItemPool("Sponge", Hint.SeraphItem, Item("GD_Iris_SeraphItems.Sponge.Iris_Seraph_Shield_Sponge_Balance", content=Tag.CampaignOfCarnage)),

    ItemPool("Crossfire", Hint.SeraphItem, Item("GD_Iris_SeraphItems.Crossfire.Iris_Seraph_GrenadeMod_Crossfire_Balance", content=Tag.CampaignOfCarnage)),
    ItemPool("Meteor Shower", Hint.SeraphItem, Item("GD_Iris_SeraphItems.MeteorShower.Iris_Seraph_GrenadeMod_MeteorShower_Balance", content=Tag.CampaignOfCarnage)),
    ItemPool("O-Negative", Hint.SeraphItem, Item("GD_Iris_SeraphItems.ONegative.Iris_Seraph_GrenadeMod_ONegative_Balance", content=Tag.CampaignOfCarnage)),

    ItemPool("Might of the Seraphs", Hint.SeraphItem, Item("GD_Iris_SeraphItems.Might.Iris_Seraph_Artifact_Might_Balance", content=Tag.CampaignOfCarnage)),

    ItemPool("Slow Hand", Hint.UniqueShotgun, Item("GD_Iris_Weapons.Shotguns.SG_Hyperion_3_SlowHand", content=Tag.CampaignOfCarnage)),
    ItemPool("Pocket Rocket", Hint.UniquePistol, Item("GD_Iris_Weapons.Pistols.Pistol_Torgue_3_PocketRocket", content=Tag.CampaignOfCarnage)),
    ItemPool("Cobra", Hint.UniqueSniper, Item("GD_Iris_Weapons.SniperRifles.Sniper_Jakobs_3_Cobra", content=Tag.CampaignOfCarnage)),
    ItemPool("Boom Puppy", Hint.UniqueAR, Item("GD_Iris_Weapons.AssaultRifles.AR_Torgue_3_BoomPuppy", content=Tag.CampaignOfCarnage)),
    ItemPool("Kitten", Hint.UniqueAR, Item("GD_Iris_Weapons.AssaultRifles.AR_Vladof_3_Kitten", content=Tag.CampaignOfCarnage)),


    ItemPool("Breath of the Seraphs", Hint.SeraphItem, Item("GD_Sage_Artifacts.A_Item.A_SeraphBreath", content=Tag.HammerlocksHunt)),

    ItemPool("The Rough Rider", Hint.UniqueShield, Item("GD_Sage_Shields.A_Item_Custom.S_BucklerShield", content=Tag.HammerlocksHunt)),

    ItemPool("Hawk Eye", Hint.SeraphWeapon, Item("GD_Sage_RaidWeapons.sniper.Sage_Seraph_HawkEye_Balance", content=Tag.HammerlocksHunt)),
    ItemPool("Infection", Hint.SeraphWeapon, Item("GD_Sage_RaidWeapons.Pistol.Sage_Seraph_Infection_Balance", content=Tag.HammerlocksHunt)),
    ItemPool("Interfacer", Hint.SeraphWeapon, Item("GD_Sage_RaidWeapons.Shotgun.Sage_Seraph_Interfacer_Balance", content=Tag.HammerlocksHunt)),
    ItemPool("Lead Storm", Hint.SeraphWeapon, Item("GD_Sage_RaidWeapons.AssaultRifle.Sage_Seraph_LeadStorm_Balance", content=Tag.HammerlocksHunt)),
    ItemPool("Rex", Hint.UniquePistol, Item("GD_Sage_Weapons.Pistols.Pistol_Jakobs_3_Rex", content=Tag.HammerlocksHunt)),
    ItemPool("Hydra", Hint.UniqueShotgun, Item("GD_Sage_Weapons.Shotgun.SG_Jakobs_3_Hydra", content=Tag.HammerlocksHunt)),
    ItemPool("Damned Cowboy", Hint.UniqueAR, Item("GD_Sage_Weapons.AssaultRifle.AR_Jakobs_3_DamnedCowboy", content=Tag.HammerlocksHunt)),
    ItemPool("Elephant Gun", Hint.UniqueSniper, Item("GD_Sage_Weapons.SniperRifles.Sniper_Jakobs_3_ElephantGun", content=Tag.HammerlocksHunt)),
    ItemPool("CHOPPER", Hint.UniqueAR, Item("GD_Sage_Weapons.AssaultRifle.AR_Bandit_3_Chopper", content=Tag.HammerlocksHunt)),
    ItemPool("Yellow Jacket", Hint.UniqueSMG, Item("GD_Sage_Weapons.SMG.SMG_Hyperion_3_YellowJacket", content=Tag.HammerlocksHunt)),
    ItemPool("Twister", Hint.UniqueShotgun, Item("GD_Sage_Weapons.Shotgun.SG_Jakobs_3_Twister", content=Tag.HammerlocksHunt)),

    ItemPool("Ogre", Hint.LegendaryAR, Item("GD_Aster_Weapons.AssaultRifles.AR_Bandit_3_Ogre", content=Tag.DragonKeep)),
    ItemPool("Grog Nozzle", Hint.UniquePistol, Item("GD_Aster_Weapons.Pistols.Pistol_Maliwan_3_GrogNozzle", content=Tag.DragonKeep)),
    ItemPool("Crit", Hint.UniqueSMG, Item("GD_Aster_Weapons.SMGs.SMG_Maliwan_3_Crit", content=Tag.DragonKeep)),
    ItemPool("Omen", Hint.SeraphWeapon, Item("GD_Aster_RaidWeapons.Shotguns.Aster_Seraph_Omen_Balance", content=Tag.DragonKeep)),
    ItemPool("Stinger", Hint.SeraphWeapon, Item("GD_Aster_RaidWeapons.Pistols.Aster_Seraph_Stinger_Balance", content=Tag.DragonKeep)),
    ItemPool("Seeker", Hint.SeraphWeapon, Item("GD_Aster_RaidWeapons.AssaultRifles.Aster_Seraph_Seeker_Balance", content=Tag.DragonKeep)),
    ItemPool("Florentine", Hint.SeraphWeapon, Item("GD_Aster_RaidWeapons.SMGs.Aster_Seraph_Florentine_Balance", content=Tag.DragonKeep)),
    ItemPool("SWORDSPLOSION!!!", Hint.UniqueShotgun, Item("GD_Aster_Weapons.Shotguns.SG_Torgue_3_SwordSplosion", content=Tag.DragonKeep)),
    ItemPool("Orc", Hint.UniqueSMG, Item("GD_Aster_Weapons.SMGs.SMG_Bandit_3_Orc", content=Tag.DragonKeep)),

    ItemPool("Mysterious Amulet", Hint.UniqueRelic, Item("GD_Aster_Artifacts.A_Item_Unique.A_MysteryAmulet", content=Tag.DragonKeep)),
    ItemPool("Shadow of the Seraphs", Hint.SeraphItem, Item("GD_Aster_Artifacts.A_Item_Unique.A_SeraphShadow", content=Tag.DragonKeep)),

    ItemPool("Chain Lightning", Hint.LegendaryGrenade, Item("GD_Aster_GrenadeMods.A_Item.GM_ChainLightning", content=Tag.DragonKeep)),
    ItemPool("Fireball", Hint.UniqueGrenade, Item("GD_Aster_GrenadeMods.A_Item.GM_Fireball", content=Tag.DragonKeep)),
    ItemPool("Fire Storm", Hint.LegendaryGrenade, Item("GD_Aster_GrenadeMods.A_Item.GM_FireStorm", content=Tag.DragonKeep)),
    ItemPool("Lightning Bolt", Hint.UniqueGrenade, Item("GD_Aster_GrenadeMods.A_Item.GM_LightningBolt", content=Tag.DragonKeep)),
    ItemPool("Blue Magic Missile", Hint.UniqueGrenade, Item("GD_Aster_GrenadeMods.A_Item.GM_MagicMissile", content=Tag.DragonKeep)),
    ItemPool("Purple Magic Missile", Hint.UniqueGrenade, Item("GD_Aster_GrenadeMods.A_Item.GM_MagicMissileRare", content=Tag.DragonKeep)),

    ItemPool("Blockade", Hint.SeraphItem, Item("GD_Aster_ItemGrades.Shields.Aster_Seraph_Blockade_Shield_Balance", content=Tag.DragonKeep)),
    ItemPool("Antagonist", Hint.SeraphItem, Item("GD_Aster_ItemGrades.Shields.Aster_Seraph_Antagonist_Shield_Balance", content=Tag.DragonKeep)),

    ItemPool("Hector's Paradise", Hint.LegendaryPistol, Item("GD_Anemone_Weapons.A_Weapons_Legendary.Pistol_Dahl_5_Hector_Hornet", content=Tag.FightForSanctuary)),
    ItemPool("Unicornsplosion", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.Shotguns.SG_Torgue_3_SwordSplosion_Unico", content=Tag.FightForSanctuary)),
    ItemPool("M2828 Thumpson", Hint.LegendaryAR, Item("GD_Anemone_Weapons.AssaultRifle.Brothers.AR_Jakobs_5_Brothers", content=Tag.FightForSanctuary)),
    ItemPool("Nirvana", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.A_Weapons_Legendary.SMG_Maliwan_5_HellFire", content=Tag.FightForSanctuary)),
    ItemPool("Hot Mama", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.sniper.Sniper_Jakobs_6_Chaude_Mama", content=Tag.FightForSanctuary)),
    ItemPool("Infection Cleaner", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.SMG.SMG_Tediore_6_Infection_Cleaner", content=Tag.FightForSanctuary)),
    ItemPool("Amigo Sincero", Hint.LegendarySniper, Item("GD_Anemone_Weapons.A_Weapons_Unique.Sniper_Jakobs_3_Morde_Lt", content=Tag.FightForSanctuary)),
    ItemPool("Overcompensator", Hint.LegendaryShotgun, Item("GD_Anemone_Weapons.Shotgun.Overcompensator.SG_Hyperion_6_Overcompensator", content=Tag.FightForSanctuary)),
    ItemPool("Peak Opener", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.AssaultRifle.PeakOpener.AR_Torgue_5_PeakOpener", content=Tag.FightForSanctuary)),
    ItemPool("Toothpick", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.AssaultRifle.AR_Dahl_6_Toothpick", content=Tag.FightForSanctuary)),
    ItemPool("World Burn", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.Rocket_Launcher.WorldBurn.RL_Torgue_5_WorldBurn", content=Tag.FightForSanctuary)),

    ItemPool("Winter is Over", Hint.UniqueRelic, Item("GD_Anemone_Relics.A_Item.A_Elemental_Status_Rare", content=Tag.FightForSanctuary)),
    ItemPool("Hard Carry", Hint.EffervescentItem, Item("GD_Anemone_Relics.A_Item_Unique.A_Deputy", content=Tag.FightForSanctuary)),
    ItemPool("Mouthwash", Hint.EffervescentItem, Item("GD_Anemone_Relics.A_Item_Unique.A_Sheriff", content=Tag.FightForSanctuary)),

    ItemPool("Antifection", Hint.EffervescentItem, Item("GD_Anemone_GrenadeMods.A_Item_Legendary.GM_Antifection", content=Tag.FightForSanctuary)),
    ItemPool("The Electric Chair", Hint.EffervescentItem, Item("GD_Anemone_GrenadeMods.A_Item_Legendary.GM_StormFront", content=Tag.FightForSanctuary)),

    ItemPool("Retainer", Hint.EffervescentItem, Item("GD_Anemone_Balance_Treasure.Shields.ItemGrade_Gear_Shield_Worming", content=Tag.FightForSanctuary)),
    ItemPool("Easy Mode", Hint.EffervescentItem, Item("GD_Anemone_ItemPools.Shields.ItemGrade_Gear_Shield_Nova_Singularity_Peak", content=Tag.FightForSanctuary)),


    ItemPool("Heart of the Ancients", Hint.EtechRelic,
        Item("GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityAssault_VeryRare", content=Tag.UVHMPack),
        Item("GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityLauncher_VeryRare", content=Tag.UVHMPack),
        Item("GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityPistol_VeryRare", content=Tag.UVHMPack),
        Item("GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityShotgun_VeryRare", content=Tag.UVHMPack),
        Item("GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacitySMG_VeryRare", content=Tag.UVHMPack),
        Item("GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacitySniper_VeryRare", content=Tag.UVHMPack),
    ),
    ItemPool("Bone of the Ancients", Hint.EtechRelic, Item("GD_Gladiolus_Artifacts.A_Item.A_ElementalProficiency_VeryRare", content=Tag.UVHMPack)),
    ItemPool("Skin of the Ancients", Hint.EtechRelic, Item("GD_Gladiolus_Artifacts.A_Item.A_ResistanceProtection_VeryRare", content=Tag.UVHMPack)),
    ItemPool("Blood of the Ancients", Hint.EtechRelic, Item("GD_Gladiolus_Artifacts.A_Item.A_VitalityStockpile_VeryRare", content=Tag.UVHMPack)),

    ItemPool("Unforgiven", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.Pistol.Pistol_Jakobs_6_Unforgiven", content=Tag.UVHMPack)),
    ItemPool("Stalker", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.Pistol.Pistol_Vladof_6_Stalker", content=Tag.UVHMPack)),
    ItemPool("Sawbar", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.AssaultRifle.AR_Bandit_6_Sawbar", content=Tag.UVHMPack)),
    ItemPool("Bearcat", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.AssaultRifle.AR_Dahl_6_Bearcat", content=Tag.UVHMPack)),
    ItemPool("Avenger", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.SMG.SMG_Tediore_6_Avenger", content=Tag.UVHMPack)),
    ItemPool("Butcher", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.Shotgun.SG_Hyperion_6_Butcher", content=Tag.UVHMPack)),
    ItemPool("Storm", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.sniper.Sniper_Maliwan_6_Storm", content=Tag.UVHMPack)),
    ItemPool("Tunguska", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.Launchers.RL_Torgue_6_Tunguska", content=Tag.UVHMPack)),


    ItemPool("Carnage", Hint.PearlescentWeapon, Item("GD_Lobelia_Weapons.Shotguns.SG_Torgue_6_Carnage", content=Tag.DigistructPeak)),
    ItemPool("Wanderlust", Hint.PearlescentWeapon, Item("GD_Lobelia_Weapons.Pistol.Pistol_Maliwan_6_Wanderlust", content=Tag.DigistructPeak)),
    ItemPool("Godfinger", Hint.PearlescentWeapon, Item("GD_Lobelia_Weapons.sniper.Sniper_Jakobs_6_Godfinger", content=Tag.DigistructPeak)),
    ItemPool("Bekah", Hint.PearlescentWeapon, Item("GD_Lobelia_Weapons.AssaultRifles.AR_Jakobs_6_Bekah", content=Tag.DigistructPeak)),
)
