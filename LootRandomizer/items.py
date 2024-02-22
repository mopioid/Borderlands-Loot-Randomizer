from __future__ import annotations

from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct #type: ignore
from unrealsdk import Log, ConstructObject, FindObject, KeepAlive #type: ignore

from . import options, hints
from .options import Tag, BalancedItem
from .hints import Hint

from typing import Optional, Sequence, Union
import enum


Items: Sequence[ItemPool] = []


class Character(enum.Enum):
    attr_init: UObject

    Assassin     = "GD_PlayerClassId.Assassin"
    Mercenary    = "GD_PlayerClassId.Mercenary"
    Siren        = "GD_PlayerClassId.Siren"
    Soldier      = "GD_PlayerClassId.Soldier"
    Psycho       = "GD_LilacPackageDef.PlayerClassId.Psycho"
    Mechromancer = "GD_TulipPackageDef.PlayerClassId.Mechromancer"


def Enable() -> None:
    global Items
    Items = [item_pool for item_pool in _item_pools if item_pool.validate()]

    for character in Character:
        class_id = FindObject("PlayerClassIdentifierDefinition", character.value)

        character.attr_init = ConstructObject("AttributeInitializationDefinition")
        KeepAlive(character.attr_init)

        pc_attr = ConstructObject("AttributeDefinition", Outer=character.attr_init)
        nopc_attr = ConstructObject("AttributeDefinition", Outer=character.attr_init)

        pc_attr.bIsSimpleAttribute = True
        pc_attr.ContextResolverChain = [ConstructObject("PlayerControllerAttributeContextResolver", Outer=pc_attr)]

        class_resolver = ConstructObject("PlayerClassAttributeValueResolver", Outer=pc_attr)
        class_resolver.PlayerClassId = class_id
        pc_attr.ValueResolverChain = [class_resolver]

        nopc_attr.bIsSimpleAttribute = True
        nopc_attr.ContextResolverChain = [ConstructObject("NoContextNeededAttributeContextResolver", Outer=nopc_attr)]

        classcount_resolver = ConstructObject("PlayerClassCountAttributeValueResolver", Outer=nopc_attr)
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

    global Items
    for pool in Items:
        pool.release()
    Items = []


class Item:
    path: str
    weight: Union[float, Character]
    dlc: Tag

    uobject: UObject = None

    def __init__(
        self,
        path: str,
        weight: Union[float, Character] = 1.0,
        dlc: Tag = Tag.BaseGame
    ) -> None:
        self.path = path
        self.weight = weight
        self.dlc = dlc

    def balanced_item(self) -> BalancedItem:
        if isinstance(self.weight, Character):
            probability = (1.0, None, self.weight.attr_init, 1.0)
        else:
            probability = (self.weight, None, None, 1.0)

        return (None, FindObject("InventoryBalanceDefinition", self.path), probability, True)

    def validate(self) -> bool:
        return self.dlc in options.SelectedTags


class ItemPool:
    name: str
    hint: Hint
    items: Sequence[Item]

    _uobject: Optional[UObject] = None #ItemPoolDefinition

    def __init__(self, name: str, hint: Hint, *items: Item) -> None:
        self.name = name; self.hint = hint; self.items = items

    @property
    def uobject(self) -> UObject: #ItemPoolDefinition
        if not self._uobject:
            self._uobject = ConstructObject("ItemPoolDefinition")
            KeepAlive(self._uobject)
            self._uobject.bAutoReadyItems = False
            self._uobject.BalancedItems = [item.balanced_item() for item in self.items]

        return self._uobject

    def validate(self) -> bool:
        [item for item in self.items if item.validate()]
        return bool(self.items)

    def release(self) -> None:
        if hasattr(self, "_uobject") and self._uobject:
            self._uobject.ObjectFlags.A &= ~0x4000
            self._uobject = None

    def get_hint(self) -> UObject: #InventoryCardPresentationDefinition
        if options.HintType.CurrentValue == "None":
            return hints.ConstructPresentation("...")        
        if options.HintType.CurrentValue == "Vague":
            return hints.ConstructPresentation("&nbsp;&#x2022;  " + self.hint)
        if options.HintType.CurrentValue == "Spoiler":
            return hints.ConstructPresentation("&nbsp;&#x2022;  " + self.name)
        return None
    

class ItemPoolPurpleWeapon(ItemPool):
    fallback: Item

    def __init__(self, name: str, hint: Hint, fallback: Item, *items: Item) -> None:
        self.name = name; self.hint = hint; self.fallback = fallback; self.items = items

    def validate(self) -> bool:
        super().validate()

        if Tag.DragonKeep not in options.SelectedTags:
            self.fallback.validate()
            self.items = (self.fallback, *self.items)

        return True


_item_pools = (
    ItemPool("Class Mod (Blue)", Hint.ClassMod,
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_03_Rare", Character.Assassin),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_03_Rare", Character.Mercenary),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_03_Rare", Character.Siren),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_03_Rare", Character.Soldier),
        Item("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_03_Rare", Character.Psycho),
        Item("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_03_Rare", Character.Mechromancer),
    ),
    ItemPool("Class Mod (Purple)", Hint.ClassMod,
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_04_VeryRare", Character.Assassin),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_04_VeryRare", Character.Mercenary),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_04_VeryRare", Character.Siren),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_04_VeryRare", Character.Soldier),
        Item("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_04_VeryRare", Character.Psycho),
        Item("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_04_VeryRare", Character.Mechromancer),
    ),
    ItemPool("Class Mod (Alignment)", Hint.ClassMod,
        Item("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Assassin", Character.Assassin),
        Item("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Merc", Character.Mercenary),
        Item("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Siren", Character.Siren),
        Item("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Soldier", Character.Soldier),
        Item("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Psycho", Character.Psycho),
        Item("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Mechromancer", Character.Mechromancer),
    ),
    ItemPool("Class Mod (Legendary)", Hint.ClassMod,
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_05_Legendary", Character.Assassin),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_06_SlayerOfTerramorphous", Character.Assassin),
        Item("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Assassin_05_Legendary", Character.Assassin, Tag.DigistructPeak),
        Item("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Assassin_05_Legendary", Character.Assassin, Tag.DigistructPeak),
        Item("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Assassin_05_Legendary", Character.Assassin, Tag.DigistructPeak),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_05_Legendary", Character.Mercenary),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_06_SlayerOfTerramorphous", Character.Mercenary),
        Item("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Merc_05_Legendary", Character.Mercenary, Tag.DigistructPeak),
        Item("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Merc_05_Legendary", Character.Mercenary, Tag.DigistructPeak),
        Item("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Merc_05_Legendary", Character.Mercenary, Tag.DigistructPeak),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_05_Legendary", Character.Siren),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_06_SlayerOfTerramorphous", Character.Siren),
        Item("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Siren_05_Legendary", Character.Siren, Tag.DigistructPeak),
        Item("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Siren_05_Legendary", Character.Siren, Tag.DigistructPeak),
        Item("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Siren_05_Legendary", Character.Siren, Tag.DigistructPeak),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_05_Legendary", Character.Soldier),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_06_SlayerOfTerramorphous", Character.Soldier),
        Item("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Soldier_05_Legendary", Character.Soldier, Tag.DigistructPeak),
        Item("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Soldier_05_Legendary", Character.Soldier, Tag.DigistructPeak),
        Item("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Soldier_05_Legendary", Character.Soldier, Tag.DigistructPeak),
        Item("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_05_Legendary", Character.Psycho),
        Item("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_06_SlayerOfTerramorphous", Character.Psycho),
        Item("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Psycho_05_Legendary", Character.Psycho, Tag.DigistructPeak),
        Item("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Psycho_05_Legendary", Character.Psycho, Tag.DigistructPeak),
        Item("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Psycho_05_Legendary", Character.Psycho, Tag.DigistructPeak),
        Item("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_05_Legendary", Character.Mechromancer),
        Item("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_06_SlayerOfTerramorphous", Character.Mechromancer),
        Item("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Mechromancer_05_Legendary", Character.Mechromancer, Tag.DigistructPeak),
        Item("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Mechromancer_05_Legendary", Character.Mechromancer, Tag.DigistructPeak),
        Item("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Mechromancer_05_Legendary", Character.Mechromancer, Tag.DigistructPeak),
    ),

    ItemPool("Aggression Relic", Hint.PurpleRelic,
        Item("GD_Artifacts.A_Item.A_AggressionA_Rare"),
        Item("GD_Artifacts.A_Item.A_AggressionB_Rare"),
        Item("GD_Artifacts.A_Item.A_AggressionC_Rare"),
        Item("GD_Artifacts.A_Item.A_AggressionD_Rare"),
        Item("GD_Artifacts.A_Item.A_AggressionE_Rare"),
        Item("GD_Artifacts.A_Item.A_AggressionF_Rare"),
    ),
    ItemPool("Allegiance Relic", Hint.PurpleRelic,
        Item("GD_Artifacts.A_Item.A_AllegianceA_Rare"),
        Item("GD_Artifacts.A_Item.A_AllegianceB_Rare"),
        Item("GD_Artifacts.A_Item.A_AllegianceC_Rare"),
        Item("GD_Artifacts.A_Item.A_AllegianceD_Rare"),
        Item("GD_Artifacts.A_Item.A_AllegianceE_Rare"),
        Item("GD_Artifacts.A_Item.A_AllegianceF_Rare"),
        Item("GD_Artifacts.A_Item.A_AllegianceG_Rare"),
        Item("GD_Artifacts.A_Item.A_AllegianceH_Rare"),
    ),
    ItemPool("Elemental Relic", Hint.PurpleRelic,
        Item("GD_Artifacts.A_Item.A_Elemental_Rare", 2.0),
        Item("GD_Artifacts.A_Item.A_Elemental_Status_Rare", 3.0),
    ),
    ItemPool("Proficiency Relic", Hint.PurpleRelic, Item("GD_Artifacts.A_Item.A_Proficiency_Rare")),
    ItemPool("Protection Relic", Hint.PurpleRelic, Item("GD_Artifacts.A_Item.A_Protection_Rare")),
    ItemPool("Resistance Relic", Hint.PurpleRelic, Item("GD_Artifacts.A_Item.A_Resistance_Rare")),
    ItemPool("Stockpile Relic", Hint.PurpleRelic, Item("GD_Artifacts.A_Item.A_Stockpile_Rare")),
    ItemPool("Strength Relic", Hint.PurpleRelic, Item("GD_Artifacts.A_Item.A_Strength_Rare")),
    ItemPool("Tenacity Relic", Hint.PurpleRelic, Item("GD_Artifacts.A_Item.A_Tenacity_Rare")),
    ItemPool("Vitality Relic", Hint.PurpleRelic, Item("GD_Artifacts.A_Item.A_Vitality_Rare")),

    ItemPool("The Afterburner", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_Afterburner")),
    ItemPool("Deputy's Badge", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_Deputy")),
    ItemPool("Moxxi's Endowment", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_Endowment")),
    ItemPool("Lucrative Opportunity", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_Opportunity")),
    ItemPool("Sheriff's Badge", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_Sheriff")),
    ItemPool("Blood of Terramorphous", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_Terramorphous")),
    ItemPool("Vault Hunter's Relic", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_VaultHunter")),

    ItemPool("Fire Burst/Tesla/Corrosive Cloud", Hint.PurpleGrenade, Item("GD_GrenadeMods.A_Item.GM_AreaEffect_4_VeryRare")),
    ItemPool("Bouncing Betty", Hint.PurpleGrenade, Item("GD_GrenadeMods.A_Item.GM_BouncingBetty_4_VeryRare")),
    ItemPool("MIRV", Hint.PurpleGrenade, Item("GD_GrenadeMods.A_Item.GM_Mirv_4_VeryRare")),
    ItemPool("Singularity", Hint.PurpleGrenade, Item("GD_GrenadeMods.A_Item.GM_Singularity_4_VeryRare")),
    ItemPool("Grenade", Hint.PurpleGrenade, Item("GD_GrenadeMods.A_Item.GM_Standard_4_VeryRare")),
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

    ItemPoolPurpleWeapon("Bandit Assault Rifle", Hint.PurpleAR,
        Item("GD_Weap_AssaultRifle.A_Weapons.AR_Bandit_4_VeryRare"),
        Item("GD_Aster_Weapons.AssaultRifles.AR_Bandit_4_Quartz", dlc=Tag.DragonKeep),
        Item("GD_Weap_AssaultRifle.A_Weapons.AR_Bandit_5_Alien", 1/6),
    ),
    ItemPoolPurpleWeapon("Dahl Assault Rifle", Hint.PurpleAR,
        Item("GD_Weap_AssaultRifle.A_Weapons.AR_Dahl_4_VeryRare"),
        Item("GD_Aster_Weapons.AssaultRifles.AR_Dahl_4_Emerald", dlc=Tag.DragonKeep),
        Item("GD_Weap_AssaultRifle.A_Weapons.AR_Dahl_5_Alien", 1/6),
    ),
    ItemPoolPurpleWeapon("Jakobs Assault Rifle", Hint.PurpleAR,
        Item("GD_Weap_AssaultRifle.A_Weapons.AR_Jakobs_4_VeryRare"),
        Item("GD_Aster_Weapons.AssaultRifles.AR_Jakobs_4_Citrine", dlc=Tag.DragonKeep),
    ),
    ItemPoolPurpleWeapon("Torgue Assault Rifle", Hint.PurpleAR,
        Item("GD_Weap_AssaultRifle.A_Weapons.AR_Torgue_4_VeryRare"),
        Item("GD_Aster_Weapons.AssaultRifles.AR_Torgue_4_Rock", dlc=Tag.DragonKeep),
    ),
    ItemPoolPurpleWeapon("Vladof Assault Rifle", Hint.PurpleAR,
        Item("GD_Weap_AssaultRifle.A_Weapons.AR_Vladof_4_VeryRare"),
        Item("GD_Aster_Weapons.AssaultRifles.AR_Vladof_4_Garnet", dlc=Tag.DragonKeep),
        Item("GD_Weap_AssaultRifle.A_Weapons.AR_Vladof_5_Alien", 1/6),
    ),

    ItemPool("Bandit Rocket Launcher", Hint.PurpleLauncher,
        Item("GD_Weap_Launchers.A_Weapons.RL_Bandit_4_VeryRare"),
        Item("GD_Weap_Launchers.A_Weapons.RL_Bandit_5_Alien", 1/5),
    ),
    ItemPool("Tediore Rocket Launcher", Hint.PurpleLauncher,
        Item("GD_Weap_Launchers.A_Weapons.RL_Tediore_4_VeryRare"),
        Item("GD_Weap_Launchers.A_Weapons.RL_Tediore_5_Alien", 1/5),
    ),
    ItemPool("Vladof Rocket Launcher", Hint.PurpleLauncher,
        Item("GD_Weap_Launchers.A_Weapons.RL_Vladof_4_VeryRare"),
        Item("GD_Weap_Launchers.A_Weapons.RL_Vladof_5_Alien", 1/5),
    ),
    ItemPool("Maliwan Rocket Launcher", Hint.PurpleLauncher,
        Item("GD_Weap_Launchers.A_Weapons.RL_Maliwan_4_VeryRare"),
        Item("GD_Weap_Launchers.A_Weapons.RL_Maliwan_5_Alien", 1/5),
    ),
    ItemPool("Torgue Rocket Launcher", Hint.PurpleLauncher, Item("GD_Weap_Launchers.A_Weapons.RL_Torgue_4_VeryRare")),

    ItemPoolPurpleWeapon("Bandit Pistol", Hint.PurplePistol,
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Bandit_4_VeryRare"),
        Item("GD_Aster_Weapons.Pistols.Pistol_Bandit_4_Quartz", dlc=Tag.DragonKeep),
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Bandit_5_Alien", 1/4),
    ),
    ItemPoolPurpleWeapon("Tediore Pistol", Hint.PurplePistol,
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Tediore_4_VeryRare"),
        Item("GD_Aster_Weapons.Pistols.Pistol_Tediore_4_CubicZerconia", dlc=Tag.DragonKeep),
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Tediore_5_Alien", 1/4),
    ),
    ItemPoolPurpleWeapon("Dahl Pistol", Hint.PurplePistol,
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Dahl_4_VeryRare"),
        Item("GD_Aster_Weapons.Pistols.Pistol_Dahl_4_Emerald", dlc=Tag.DragonKeep),
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Dahl_5_Alien", 1/4),
    ),
    ItemPoolPurpleWeapon("Vladof Pistol", Hint.PurplePistol,
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Vladof_4_VeryRare"),
        Item("GD_Aster_Weapons.Pistols.Pistol_Vladof_4_Garnet", dlc=Tag.DragonKeep),
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Vladof_5_Alien", 1/4),
    ),
    ItemPoolPurpleWeapon("Torgue Pistol", Hint.PurplePistol,
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Torgue_4_VeryRare"),
        Item("GD_Aster_Weapons.Pistols.Pistol_Torgue_4_Rock", dlc=Tag.DragonKeep),
    ),
    ItemPoolPurpleWeapon("Maliwan Pistol", Hint.PurplePistol,
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Maliwan_4_VeryRare"),
        Item("GD_Aster_Weapons.Pistols.Pistol_Maliwan_4_Aquamarine", dlc=Tag.DragonKeep),
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Maliwan_5_Alien", 1/4),
    ),
    ItemPoolPurpleWeapon("Jakobs Pistol", Hint.PurplePistol,
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Jakobs_4_VeryRare"),
        Item("GD_Aster_Weapons.Pistols.Pistol_Jakobs_4_Citrine", dlc=Tag.DragonKeep),
    ),
    ItemPoolPurpleWeapon("Hyperion Pistol", Hint.PurplePistol,
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Hyperion_4_VeryRare"),
        Item("GD_Aster_Weapons.Pistols.Pistol_Hyperion_4_Diamond", dlc=Tag.DragonKeep),
        # Item("GD_Weap_Pistol.A_Weapons.Pistol_Hyperion_5_Alien", 1/4),
    ),

    ItemPoolPurpleWeapon("Bandit Shotgun", Hint.PurpleShotgun,
        Item("GD_Weap_Shotgun.A_Weapons.SG_Bandit_4_VeryRare"),
        Item("GD_Aster_Weapons.Shotguns.SG_Bandit_4_Quartz", dlc=Tag.DragonKeep),
        Item("GD_Weap_Shotgun.A_Weapons.SG_Bandit_5_Alien", 1/5),
    ),
    ItemPoolPurpleWeapon("Tediore Shotgun", Hint.PurpleShotgun,
        Item("GD_Weap_Shotgun.A_Weapons.SG_Tediore_4_VeryRare"),
        Item("GD_Aster_Weapons.Shotguns.SG_Tediore_4_CubicZerconia", dlc=Tag.DragonKeep),
        Item("GD_Weap_Shotgun.A_Weapons.SG_Tediore_5_Alien", 1/5),
    ),
    ItemPoolPurpleWeapon("Torgue Shotgun", Hint.PurpleShotgun,
        Item("GD_Weap_Shotgun.A_Weapons.SG_Torgue_4_VeryRare"),
        Item("GD_Aster_Weapons.Shotguns.SG_Torgue_4_Rock", dlc=Tag.DragonKeep),
    ),
    ItemPoolPurpleWeapon("Jakobs Shotgun", Hint.PurpleShotgun,
        Item("GD_Weap_Shotgun.A_Weapons.SG_Jakobs_4_VeryRare"),
        Item("GD_Aster_Weapons.Shotguns.SG_Jakobs_4_Citrine", dlc=Tag.DragonKeep),
    ),
    ItemPoolPurpleWeapon("Hyperion Shotgun", Hint.PurpleShotgun,
        Item("GD_Weap_Shotgun.A_Weapons.SG_Hyperion_4_VeryRare"),
        Item("GD_Aster_Weapons.Shotguns.SG_Hyperion_4_Diamond", dlc=Tag.DragonKeep),
        Item("GD_Weap_Shotgun.A_Weapons.SG_Hyperion_5_Alien", 1/5),
    ),

    ItemPoolPurpleWeapon("Bandit SMG", Hint.PurpleSMG,
        Item("GD_Weap_SMG.A_Weapons.SMG_Bandit_4_VeryRare"),
        Item("GD_Aster_Weapons.SMGs.SMG_Bandit_4_Quartz", dlc=Tag.DragonKeep),
        Item("GD_Weap_SMG.A_Weapons.SMG_Bandit_5_Alien", 1/5),
    ),
    ItemPoolPurpleWeapon("Tediore SMG", Hint.PurpleSMG,
        Item("GD_Weap_SMG.A_Weapons.SMG_Tediore_4_VeryRare"),
        Item("GD_Aster_Weapons.SMGs.SMG_Tediore_4_CubicZerconia", dlc=Tag.DragonKeep),
        Item("GD_Weap_SMG.A_Weapons.SMG_Tediore_5_Alien", 1/5),
    ),
    ItemPoolPurpleWeapon("Dahl SMG", Hint.PurpleSMG,
        Item("GD_Weap_SMG.A_Weapons.SMG_Dahl_4_VeryRare"),
        Item("GD_Aster_Weapons.SMGs.SMG_Dahl_4_Emerald", dlc=Tag.DragonKeep),
        Item("GD_Weap_SMG.A_Weapons.SMG_Dahl_5_Alien", 1/5),
    ),
    ItemPoolPurpleWeapon("Maliwan SMG", Hint.PurpleSMG,
        Item("GD_Weap_SMG.A_Weapons.SMG_Maliwan_4_VeryRare"),
        Item("GD_Aster_Weapons.SMGs.SMG_Maliwan_4_Aquamarine", dlc=Tag.DragonKeep),
        Item("GD_Weap_SMG.A_Weapons.SMG_Maliwan_5_Alien", 1/5),
    ),
    ItemPoolPurpleWeapon("Hyperion SMG", Hint.PurpleSMG,
        Item("GD_Weap_SMG.A_Weapons.SMG_Hyperion_4_VeryRare"),
        Item("GD_Aster_Weapons.SMGs.SMG_Hyperion_4_Diamond", dlc=Tag.DragonKeep),
        Item("GD_Weap_SMG.A_Weapons.SMG_Hyperion_5_Alien", 1/5),
    ),

    ItemPoolPurpleWeapon("Dahl Sniper Rifle", Hint.PurpleSniper,
        Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Dahl_4_VeryRare"),
        Item("GD_Aster_Weapons.Snipers.SR_Dahl_4_Emerald", dlc=Tag.DragonKeep),
        Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Dahl_5_Alien", 1/5),
    ),
    ItemPoolPurpleWeapon("Vladof Sniper Rifle", Hint.PurpleSniper,
        Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Vladof_4_VeryRare"),
        Item("GD_Aster_Weapons.Snipers.SR_Vladof_4_Garnet", dlc=Tag.DragonKeep),
        Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Vladof_5_Alien", 1/5),
    ),
    ItemPoolPurpleWeapon("Maliwan Sniper Rifle", Hint.PurpleSniper,
        Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Maliwan_4_VeryRare"),
        Item("GD_Aster_Weapons.Snipers.SR_Maliwan_4_Aquamarine", dlc=Tag.DragonKeep),
        Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Maliwan_5_Alien", 1/5),
    ),
    ItemPoolPurpleWeapon("Jakobs Sniper Rifle", Hint.PurpleSniper,
        Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Jakobs_4_VeryRare"),
        Item("GD_Aster_Weapons.Snipers.SR_Jakobs_4_Citrine", dlc=Tag.DragonKeep),
    ),
    ItemPoolPurpleWeapon("Hyperion Sniper Rifle", Hint.PurpleSniper,
        Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Hyperion_4_VeryRare"),
        Item("GD_Aster_Weapons.Snipers.SR_Hyperion_4_Diamond", dlc=Tag.DragonKeep),
        Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Hyperion_5_Alien", 1/5),
    ),

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
    ItemPool("Fibber", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_Fibber")),
    ItemPool("Rubi", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Maliwan_3_Rubi")),
    ItemPool("Veritas", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Vladof_3_Veritas")),
    ItemPool("Dahlminator", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_Dahlminator")),
    ItemPool("Lady Fist", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_LadyFist")),

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

    
    ItemPool("Hector's Paradise", Hint.LegendaryPistol, Item("GD_Anemone_Weapons.A_Weapons_Legendary.Pistol_Dahl_5_Hector_Hornet", dlc=Tag.FightForSanctuary)),
    ItemPool("Unicornsplosion", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.Shotguns.SG_Torgue_3_SwordSplosion_Unico", dlc=Tag.FightForSanctuary)),
    ItemPool("M2828 Thumpson", Hint.LegendaryAR, Item("GD_Anemone_Weapons.AssaultRifle.Brothers.AR_Jakobs_5_Brothers", dlc=Tag.FightForSanctuary)),
    ItemPool("Nirvana", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.A_Weapons_Legendary.SMG_Maliwan_5_HellFire", dlc=Tag.FightForSanctuary)),
    ItemPool("Hot Mama", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.sniper.Sniper_Jakobs_6_Chaude_Mama", dlc=Tag.FightForSanctuary)),
    ItemPool("Infection Cleaner", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.SMG.SMG_Tediore_6_Infection_Cleaner", dlc=Tag.FightForSanctuary)),
    ItemPool("Amigo Sincero", Hint.LegendarySniper, Item("GD_Anemone_Weapons.A_Weapons_Unique.Sniper_Jakobs_3_Morde_Lt", dlc=Tag.FightForSanctuary)),
    ItemPool("Overcompensator", Hint.LegendaryShotgun, Item("GD_Anemone_Weapons.Shotgun.Overcompensator.SG_Hyperion_6_Overcompensator", dlc=Tag.FightForSanctuary)),
    ItemPool("Peak Opener", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.AssaultRifle.PeakOpener.AR_Torgue_5_PeakOpener", dlc=Tag.FightForSanctuary)),
    ItemPool("Toothpick", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.AssaultRifle.AR_Dahl_6_Toothpick", dlc=Tag.FightForSanctuary)),
    ItemPool("World Burn", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.Rocket_Launcher.WorldBurn.RL_Torgue_5_WorldBurn", dlc=Tag.FightForSanctuary)),

    ItemPool("Winter is Over", Hint.UniqueRelic, Item("GD_Anemone_Relics.A_Item.A_Elemental_Status_Rare", dlc=Tag.FightForSanctuary)),
    ItemPool("Hard Carry", Hint.EffervescentItem, Item("GD_Anemone_Relics.A_Item_Unique.A_Deputy", dlc=Tag.FightForSanctuary)),
    ItemPool("Mouthwash", Hint.EffervescentItem, Item("GD_Anemone_Relics.A_Item_Unique.A_Sheriff", dlc=Tag.FightForSanctuary)),

    ItemPool("Antifection", Hint.EffervescentItem, Item("GD_Anemone_GrenadeMods.A_Item_Legendary.GM_Antifection", dlc=Tag.FightForSanctuary)),
    ItemPool("The Electric Chair", Hint.EffervescentItem, Item("GD_Anemone_GrenadeMods.A_Item_Legendary.GM_StormFront", dlc=Tag.FightForSanctuary)),

    ItemPool("Retainer", Hint.EffervescentItem, Item("GD_Anemone_Balance_Treasure.Shields.ItemGrade_Gear_Shield_Worming", dlc=Tag.FightForSanctuary)),
    ItemPool("Easy Mode", Hint.EffervescentItem, Item("GD_Anemone_ItemPools.Shields.ItemGrade_Gear_Shield_Nova_Singularity_Peak", dlc=Tag.FightForSanctuary)),

    ItemPool("Ogre", Hint.LegendaryAR, Item("GD_Aster_Weapons.AssaultRifles.AR_Bandit_3_Ogre", dlc=Tag.DragonKeep)),
    ItemPool("Grog Nozzle", Hint.UniquePistol, Item("GD_Aster_Weapons.Pistols.Pistol_Maliwan_3_GrogNozzle", dlc=Tag.DragonKeep)),
    ItemPool("Crit", Hint.UniqueSMG, Item("GD_Aster_Weapons.SMGs.SMG_Maliwan_3_Crit", dlc=Tag.DragonKeep)),
    ItemPool("Omen", Hint.SeraphWeapon, Item("GD_Aster_RaidWeapons.Shotguns.Aster_Seraph_Omen_Balance", dlc=Tag.DragonKeep)),
    ItemPool("Stinger", Hint.SeraphWeapon, Item("GD_Aster_RaidWeapons.Pistols.Aster_Seraph_Stinger_Balance", dlc=Tag.DragonKeep)),
    ItemPool("Seeker", Hint.SeraphWeapon, Item("GD_Aster_RaidWeapons.AssaultRifles.Aster_Seraph_Seeker_Balance", dlc=Tag.DragonKeep)),
    ItemPool("Florentine", Hint.SeraphWeapon, Item("GD_Aster_RaidWeapons.SMGs.Aster_Seraph_Florentine_Balance", dlc=Tag.DragonKeep)),
    ItemPool("SWORDSPLOSION!!!", Hint.UniqueShotgun, Item("GD_Aster_Weapons.Shotguns.SG_Torgue_3_SwordSplosion", dlc=Tag.DragonKeep)),
    ItemPool("Orc", Hint.UniqueSMG, Item("GD_Aster_Weapons.SMGs.SMG_Bandit_3_Orc", dlc=Tag.DragonKeep)),

    ItemPool("Mysterious Amulet", Hint.UniqueRelic, Item("GD_Aster_Artifacts.A_Item_Unique.A_MysteryAmulet", dlc=Tag.DragonKeep)),
    ItemPool("Shadow of the Seraphs", Hint.SeraphItem, Item("GD_Aster_Artifacts.A_Item_Unique.A_SeraphShadow", dlc=Tag.DragonKeep)),

    ItemPool("Chain Lightning", Hint.LegendaryGrenade, Item("GD_Aster_GrenadeMods.A_Item.GM_ChainLightning", dlc=Tag.DragonKeep)),
    ItemPool("Fireball", Hint.UniqueGrenade, Item("GD_Aster_GrenadeMods.A_Item.GM_Fireball", dlc=Tag.DragonKeep)),
    ItemPool("Fire Storm", Hint.LegendaryGrenade, Item("GD_Aster_GrenadeMods.A_Item.GM_FireStorm", dlc=Tag.DragonKeep)),
    ItemPool("Lightning Bolt", Hint.UniqueGrenade, Item("GD_Aster_GrenadeMods.A_Item.GM_LightningBolt", dlc=Tag.DragonKeep)),
    ItemPool("Magic Missile (x2)", Hint.UniqueGrenade, Item("GD_Aster_GrenadeMods.A_Item.GM_MagicMissile", dlc=Tag.DragonKeep)),
    ItemPool("Magic Missile (x4)", Hint.UniqueGrenade, Item("GD_Aster_GrenadeMods.A_Item.GM_MagicMissileRare", dlc=Tag.DragonKeep)),

    ItemPool("Blockade", Hint.SeraphItem, Item("GD_Aster_ItemGrades.Shields.Aster_Seraph_Blockade_Shield_Balance", dlc=Tag.DragonKeep)),
    ItemPool("Antagonist", Hint.SeraphItem, Item("GD_Aster_ItemGrades.Shields.Aster_Seraph_Antagonist_Shield_Balance", dlc=Tag.DragonKeep)),

    ItemPool("Heart of the Ancients", Hint.EtechRelic,
        Item("GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityAssault_VeryRare", dlc=Tag.UVHMPack),
        Item("GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityLauncher_VeryRare", dlc=Tag.UVHMPack),
        Item("GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityPistol_VeryRare", dlc=Tag.UVHMPack),
        Item("GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityShotgun_VeryRare", dlc=Tag.UVHMPack),
        Item("GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacitySMG_VeryRare", dlc=Tag.UVHMPack),
        Item("GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacitySniper_VeryRare", dlc=Tag.UVHMPack),
    ),
    ItemPool("Bone of the Ancients", Hint.EtechRelic, Item("GD_Gladiolus_Artifacts.A_Item.A_ElementalProficiency_VeryRare", dlc=Tag.UVHMPack)),
    ItemPool("Skin of the Ancients", Hint.EtechRelic, Item("GD_Gladiolus_Artifacts.A_Item.A_ResistanceProtection_VeryRare", dlc=Tag.UVHMPack)),
    ItemPool("Blood of the Ancients", Hint.EtechRelic, Item("GD_Gladiolus_Artifacts.A_Item.A_VitalityStockpile_VeryRare", dlc=Tag.UVHMPack)),

    ItemPool("Unforgiven", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.Pistol.Pistol_Jakobs_6_Unforgiven", dlc=Tag.UVHMPack)),
    ItemPool("Stalker", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.Pistol.Pistol_Vladof_6_Stalker", dlc=Tag.UVHMPack)),
    ItemPool("Sawbar", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.AssaultRifle.AR_Bandit_6_Sawbar", dlc=Tag.UVHMPack)),
    ItemPool("Bearcat", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.AssaultRifle.AR_Dahl_6_Bearcat", dlc=Tag.UVHMPack)),
    ItemPool("Avenger", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.SMG.SMG_Tediore_6_Avenger", dlc=Tag.UVHMPack)),
    ItemPool("Butcher", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.Shotgun.SG_Hyperion_6_Butcher", dlc=Tag.UVHMPack)),
    ItemPool("Storm", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.sniper.Sniper_Maliwan_6_Storm", dlc=Tag.UVHMPack)),
    ItemPool("Tunguska", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.Launchers.RL_Torgue_6_Tunguska", dlc=Tag.UVHMPack)),

    ItemPool("Big Boom Blaster", Hint.SeraphItem, Item("GD_Iris_SeraphItems.BigBoomBlaster.Iris_Seraph_Shield_Booster_Balance", dlc=Tag.CampaignOfCarnage)),
    ItemPool("Hoplite", Hint.SeraphItem, Item("GD_Iris_SeraphItems.Hoplite.Iris_Seraph_Shield_Juggernaut_Balance", dlc=Tag.CampaignOfCarnage)),
    ItemPool("Pun-chee", Hint.SeraphItem, Item("GD_Iris_SeraphItems.Pun-chee.Iris_Seraph_Shield_Pun-chee_Balance", dlc=Tag.CampaignOfCarnage)),
    ItemPool("Sponge", Hint.SeraphItem, Item("GD_Iris_SeraphItems.Sponge.Iris_Seraph_Shield_Sponge_Balance", dlc=Tag.CampaignOfCarnage)),

    ItemPool("Crossfire", Hint.SeraphItem, Item("GD_Iris_SeraphItems.Crossfire.Iris_Seraph_GrenadeMod_Crossfire_Balance", dlc=Tag.CampaignOfCarnage)),
    ItemPool("Meteor Shower", Hint.SeraphItem, Item("GD_Iris_SeraphItems.MeteorShower.Iris_Seraph_GrenadeMod_MeteorShower_Balance", dlc=Tag.CampaignOfCarnage)),
    ItemPool("O-Negative", Hint.SeraphItem, Item("GD_Iris_SeraphItems.ONegative.Iris_Seraph_GrenadeMod_ONegative_Balance", dlc=Tag.CampaignOfCarnage)),

    ItemPool("Might of the Seraphs", Hint.SeraphItem, Item("GD_Iris_SeraphItems.Might.Iris_Seraph_Artifact_Might_Balance", dlc=Tag.CampaignOfCarnage)),

    ItemPool("Slow Hand", Hint.UniqueShotgun, Item("GD_Iris_Weapons.Shotguns.SG_Hyperion_3_SlowHand", dlc=Tag.CampaignOfCarnage)),
    ItemPool("Pocket Rocket", Hint.UniquePistol, Item("GD_Iris_Weapons.Pistols.Pistol_Torgue_3_PocketRocket", dlc=Tag.CampaignOfCarnage)),
    ItemPool("Cobra", Hint.UniqueSniper, Item("GD_Iris_Weapons.SniperRifles.Sniper_Jakobs_3_Cobra", dlc=Tag.CampaignOfCarnage)),
    ItemPool("Boom Puppy", Hint.UniqueAR, Item("GD_Iris_Weapons.AssaultRifles.AR_Torgue_3_BoomPuppy", dlc=Tag.CampaignOfCarnage)),
    ItemPool("Kitten", Hint.UniqueAR, Item("GD_Iris_Weapons.AssaultRifles.AR_Vladof_3_Kitten", dlc=Tag.CampaignOfCarnage)),

    ItemPool("Carnage", Hint.PearlescentWeapon, Item("GD_Lobelia_Weapons.Shotguns.SG_Torgue_6_Carnage", dlc=Tag.DigistructPeak)),
    ItemPool("Wanderlust", Hint.PearlescentWeapon, Item("GD_Lobelia_Weapons.Pistol.Pistol_Maliwan_6_Wanderlust", dlc=Tag.DigistructPeak)),
    ItemPool("Godfinger", Hint.PearlescentWeapon, Item("GD_Lobelia_Weapons.sniper.Sniper_Jakobs_6_Godfinger", dlc=Tag.DigistructPeak)),
    ItemPool("Bekah", Hint.PearlescentWeapon, Item("GD_Lobelia_Weapons.AssaultRifles.AR_Jakobs_6_Bekah", dlc=Tag.DigistructPeak)),

    ItemPool("Captain Blade's Otto Idol", Hint.UniqueRelic, Item("GD_Orchid_Artifacts.A_Item_Unique.A_Blade", dlc=Tag.PiratesBooty)),
    ItemPool("Blood of the Seraphs", Hint.SeraphItem, Item("GD_Orchid_Artifacts.A_Item_Unique.A_SeraphBloodRelic", dlc=Tag.PiratesBooty)),

    ItemPool("Midnight Star", Hint.UniqueGrenade, Item("GD_Orchid_GrenadeMods.A_Item_Custom.GM_Blade", dlc=Tag.PiratesBooty)),

    ItemPool("Evolution", Hint.SeraphItem, Item("GD_Orchid_RaidWeapons.Shield.Anshin.Orchid_Seraph_Anshin_Shield_Balance", dlc=Tag.PiratesBooty)),
    ItemPool("Manly Man Shield", Hint.UniqueShield, Item("GD_Orchid_Shields.A_Item_Custom.S_BladeShield", dlc=Tag.PiratesBooty)),

    ItemPool("Greed", Hint.UniquePistol, Item("GD_Orchid_BossWeapons.Pistol.Pistol_Jakobs_ScarletsGreed", dlc=Tag.PiratesBooty)),
    ItemPool("12 Pounder", Hint.UniqueLauncher, Item("GD_Orchid_BossWeapons.Launcher.RL_Torgue_3_12Pounder", dlc=Tag.PiratesBooty)),
    ItemPool("Little Evie", Hint.UniquePistol, Item("GD_Orchid_BossWeapons.Pistol.Pistol_Maliwan_3_LittleEvie", dlc=Tag.PiratesBooty)),
    ItemPool("Stinkpot", Hint.UniqueAR, Item("GD_Orchid_BossWeapons.AssaultRifle.AR_Jakobs_3_Stinkpot", dlc=Tag.PiratesBooty)),
    ItemPool("Devastator", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.Pistol.Devastator.Orchid_Seraph_Devastator_Balance", dlc=Tag.PiratesBooty)),
    ItemPool("Tattler", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.SMG.Tattler.Orchid_Seraph_Tattler_Balance", dlc=Tag.PiratesBooty)),
    ItemPool("Retcher", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.Shotgun.Spitter.Orchid_Seraph_Spitter_Balance", dlc=Tag.PiratesBooty)),
    ItemPool("Actualizer", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.SMG.Actualizer.Orchid_Seraph_Actualizer_Balance", dlc=Tag.PiratesBooty)),
    ItemPool("Seraphim", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.AssaultRifle.Seraphim.Orchid_Seraph_Seraphim_Balance", dlc=Tag.PiratesBooty)),
    ItemPool("Patriot", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.sniper.Patriot.Orchid_Seraph_Patriot_Balance", dlc=Tag.PiratesBooty)),
    ItemPool("Ahab", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.RPG.Ahab.Orchid_Seraph_Ahab_Balance", dlc=Tag.PiratesBooty)),
    ItemPool("Rapier", Hint.UniqueAR, Item("GD_Orchid_BossWeapons.AssaultRifle.AR_Vladof_3_Rapier", dlc=Tag.PiratesBooty)),
    ItemPool("Jolly Roger", Hint.UniqueShotgun, Item("GD_Orchid_BossWeapons.Shotgun.SG_Bandit_3_JollyRoger", dlc=Tag.PiratesBooty)),
    ItemPool("Orphan Maker", Hint.UniqueShotgun, Item("GD_Orchid_BossWeapons.Shotgun.SG_Jakobs_3_OrphanMaker", dlc=Tag.PiratesBooty)),
    ItemPool("Sand Hawk", Hint.UniqueSMG, Item("GD_Orchid_BossWeapons.SMG.SMG_Dahl_3_SandHawk", dlc=Tag.PiratesBooty)),
    ItemPool("Pimpernel", Hint.UniqueSniper, Item("GD_Orchid_BossWeapons.SniperRifles.Sniper_Maliwan_3_Pimpernel", dlc=Tag.PiratesBooty)),

    ItemPool("Breath of the Seraphs", Hint.SeraphItem, Item("GD_Sage_Artifacts.A_Item.A_SeraphBreath", dlc=Tag.HammerlocksHunt)),

    ItemPool("The Rough Rider", Hint.UniqueShield, Item("GD_Sage_Shields.A_Item_Custom.S_BucklerShield", dlc=Tag.HammerlocksHunt)),

    ItemPool("Hawk Eye", Hint.SeraphWeapon, Item("GD_Sage_RaidWeapons.sniper.Sage_Seraph_HawkEye_Balance", dlc=Tag.HammerlocksHunt)),
    ItemPool("Infection", Hint.SeraphWeapon, Item("GD_Sage_RaidWeapons.Pistol.Sage_Seraph_Infection_Balance", dlc=Tag.HammerlocksHunt)),
    ItemPool("Interfacer", Hint.SeraphWeapon, Item("GD_Sage_RaidWeapons.Shotgun.Sage_Seraph_Interfacer_Balance", dlc=Tag.HammerlocksHunt)),
    ItemPool("Lead Storm", Hint.SeraphWeapon, Item("GD_Sage_RaidWeapons.AssaultRifle.Sage_Seraph_LeadStorm_Balance", dlc=Tag.HammerlocksHunt)),
    ItemPool("Rex", Hint.UniquePistol, Item("GD_Sage_Weapons.Pistols.Pistol_Jakobs_3_Rex", dlc=Tag.HammerlocksHunt)),
    ItemPool("Hydra", Hint.UniqueShotgun, Item("GD_Sage_Weapons.Shotgun.SG_Jakobs_3_Hydra", dlc=Tag.HammerlocksHunt)),
    ItemPool("Damned Cowboy", Hint.UniqueAR, Item("GD_Sage_Weapons.AssaultRifle.AR_Jakobs_3_DamnedCowboy", dlc=Tag.HammerlocksHunt)),
    ItemPool("Elephant Gun", Hint.UniqueSniper, Item("GD_Sage_Weapons.SniperRifles.Sniper_Jakobs_3_ElephantGun", dlc=Tag.HammerlocksHunt)),
    ItemPool("CHOPPER", Hint.UniqueAR, Item("GD_Sage_Weapons.AssaultRifle.AR_Bandit_3_Chopper", dlc=Tag.HammerlocksHunt)),
    ItemPool("Yellow Jacket", Hint.UniqueSMG, Item("GD_Sage_Weapons.SMG.SMG_Hyperion_3_YellowJacket", dlc=Tag.HammerlocksHunt)),
    ItemPool("Twister", Hint.UniqueShotgun, Item("GD_Sage_Weapons.Shotgun.SG_Jakobs_3_Twister", dlc=Tag.HammerlocksHunt)),
)



"""
GD_Orchid_BossWeapons.RPG.Ahab.Orchid_Boss_Ahab_Balance_NODROP
GD_Orchid_SeraphCrystal.ItemGrades.ItemGrade_SeraphCrystal

GD_Iris_ItemPools.BalDefs.BalDef_ClassMod_Torgue_Common
GD_Iris_MoxxiPicture.ItemGrades.ItemGrade_MoxxiPicture1
GD_Iris_MoxxiPicture.ItemGrades.ItemGrade_MoxxiPicture2
GD_Iris_MoxxiPicture.ItemGrades.ItemGrade_MoxxiPicture3
GD_Iris_SeraphCrystal.ItemGrades.ItemGrade_Iris_SeraphCrystal
GD_Iris_SeraphItems.Misc.ItemGrade_BoosterShield_SeraphShieldChargerPickup
GD_Iris_TorgueToken.ItemGrades.ItemGrade_TorgueToken
GD_IrisDL3_CommAppealData.MW_CommAppeal_Torgue
GD_IrisEpisode05_BattleData.BalanceDefs.BD_Iris_GyroBanjo
GD_IrisEpisode05_BattleData.BalanceDefs.BD_Iris_GyroBanjo2
GD_IrisEpisode05_BattleData.BalanceDefs.BD_Iris_GyroBanjo3
GD_IrisEpisode05_BattleData.BalanceDefs.BD_Iris_GyroBanjoR3

GD_Sage_HarpoonGun.Balance.Sage_HarpoonGun_Balance
GD_Sage_SeraphCrystal.ItemGrades.ItemGrade_SeraphCrystal

GD_Aster_ClapTrapBeardData.MW_ClaptrapBeard_GrogNozzle
GD_Aster_SeraphCrystal.ItemGrades.ItemGrade_SeraphCrystal

GD_Anemone_GrenadeMods.A_Item_Legendary.GM_Antifection_Turret
GD_Anemone_GrenadeMods.A_Item.GM_Standard_3_Rare_Flamer
GD_Anemone_Lt_Hoffman.A_Weapons.Sniper_Vladof_4_VeryRare_Hoffman
GD_Anemone_Plot_Mission010.BalanceDefs.BD_Anemone_E01_M010_EchoLogs
GD_Anemone_Plot_Mission010.BalanceDefs.BD_Anemone_M010_Documents
GD_Anemone_Plot_Mission020.BalanceDefs.BD_E01_M020_InfectedBrains
GD_Anemone_Plot_Mission020.BalanceDefs.BD_E02_M020_TalonPlaceholder
GD_Anemone_Plot_Mission020.BalanceDefs.BD_InfectedBodyPart
GD_Anemone_Plot_Mission020.BalanceDefs.BD_M020_InfectedFlowerSample
GD_Anemone_Plot_Mission020.BalanceDefs.BD_TannisDevice
GD_Anemone_Plot_Mission025.BalanceDefs.BD_EllieTool
GD_Anemone_Plot_Mission025.BalanceDefs.BD_InfectedHead
GD_Anemone_Plot_Mission040.BalanceDefs.BD_Explosive
GD_Anemone_Plot_Mission040.BalanceDefs.BD_ID_PowerCore
GD_Anemone_Plot_Mission040.BalanceDefs.BD_StabilizerFin
GD_Anemone_Plot_Mission050.BalanceDefs.BD_Antidote
GD_Anemone_Plot_Mission050.BalanceDefs.BD_CassiusBlood
GD_Anemone_Plot_Mission050.BalanceDefs.BD_MordecaiBloodSample
GD_Anemone_Plot_Mission060.BalanceDefs.BD_BeerBottle
GD_Anemone_Plot_Mission060.BalanceDefs.BD_EridiumBar
GD_Anemone_Side_Claptocurrency.BalanceDefs.BD_BechoWaffers
GD_Anemone_Side_Claptocurrency.BalanceDefs.BD_BlockAndChain
GD_Anemone_Side_Echoes.BalanceDefs.BD_LostHectorEcho
GD_Anemone_Side_Echoes.BalanceDefs.BD_LostHectorECHO02
GD_Anemone_Side_Echoes.BalanceDefs.BD_LostHectorEcho03
GD_Anemone_Side_EyeSnipers.BalanceDefs.BD_LtAngvarRifleParts
GD_Anemone_Side_EyeSnipers.BalanceDefs.BD_LtBolsonRifleParts
GD_Anemone_Side_EyeSnipers.BalanceDefs.BD_LtHoffmanRifleParts
GD_Anemone_Side_EyeSnipers.BalanceDefs.BD_LtTetraRifleParts
GD_Anemone_Side_EyeSnipers.BalanceDefs.BD_MordecaisGift
GD_Anemone_Side_EyeSnipers.BalanceDefs.BD_NewPandorianRifleParts
GD_Anemone_Side_HypoOathPart1.BalanceDefs.BD_DrZedAntidote
GD_Anemone_Side_HypoOathPart1.BalanceDefs.BD_InfectedBodyPart
GD_Anemone_Side_HypoOathPart2.BalanceDefs.BD_DrZedAntidote
GD_Anemone_Side_HypoOathPart2.BalanceDefs.BD_InfectedBodyPart
GD_Anemone_Side_OddestCouple.BalanceDefs.BD_Cannedfood
GD_Anemone_Side_OddestCouple.BalanceDefs.BD_Cannedfood02
GD_Anemone_Side_OddestCouple.BalanceDefs.BD_Cannedfood03
GD_Anemone_Side_OddestCouple.BalanceDefs.BD_Cannedfood04
GD_Anemone_Side_SpaceCowboy.BalanceDefs.BD_NudieMagazine01
GD_Anemone_Side_SpaceCowboy.BalanceDefs.BD_NudieMagazine02
GD_Anemone_Side_SpaceCowboy.BalanceDefs.BD_NudieMagazine03
GD_Anemone_Side_SpaceCowboy.BalanceDefs.BD_ScooterECHO
GD_Anemone_Side_VaughnPart1.BalanceDefs.BD_Vaughnsflag
GD_Anemone_Side_VaughnPart2.BalanceDefs.BD_SandwormQueenTrophy
GD_Anemone_Side_VaughnPart2.BalanceDefs.BD_SandwormQueenTrophy02
GD_Anemone_Side_VaughnPart3.ItemDefs.BD_ArtifactOfPower
GD_Anemone_Weap_SniperRifles.A_Weapons.Sniper_Jakobs
GD_Anemone_Weap_SniperRifles.A_Weapons.Sniper_Jakobs_2_Uncommon
GD_Anemone_Weap_SniperRifles.A_Weapons.Sniper_Jakobs_3_Rare
GD_Anemone_Weap_SniperRifles.A_Weapons.Sniper_Jakobs_4_VeryRare
GD_Anemone_Weapons.A_Weapons_Legendary.Pistol_Vladof_5_Infinity_DD
GD_Anemone_Weapons.A_Weapons_Unique.Pistol_The_Gremlins
GD_Anemone_Weapons.A_Weapons_Unique.RL_Maliwan_Alien_Norfleet_Fire_100
GD_Anemone_Weapons.A_Weapons.Pistol_Vladof_4_VeryRare
GD_Anemone_Weapons.A_Weapons.SG_Torgue_7_Effervecemt
GD_Anemone_Weapons.AssaultRifle.PeakOpener.AR_PeakOpener
GD_Anemone_Weapons.Rocket_Launcher.RL_Maliwan_5_Pyrophobia
GD_Anemone_Weapons.Testing_Resist_100.100_Fire

GD_Allium_TG_Plot_M01Data.Weapons.Weapon_JabberSlagWeapon

GD_Flax_Items.Item.BalDef_Candy_Blue
GD_Flax_Items.Item.BalDef_Candy_Green
GD_Flax_Items.Item.BalDef_Candy_Red
GD_Flax_Items.Item.BalDef_Candy_Yellow
GD_Flax_Items.Item.BalDef_Wisp

GD_Artifacts.A_Item.A_AggressionA
GD_Artifacts.A_Item.A_AggressionB
GD_Artifacts.A_Item.A_AggressionC
GD_Artifacts.A_Item.A_AggressionD
GD_Artifacts.A_Item.A_AggressionE
GD_Artifacts.A_Item.A_AggressionF
GD_Artifacts.A_Item.A_AllegianceA
GD_Artifacts.A_Item.A_AllegianceB
GD_Artifacts.A_Item.A_AllegianceC
GD_Artifacts.A_Item.A_AllegianceD
GD_Artifacts.A_Item.A_AllegianceE
GD_Artifacts.A_Item.A_AllegianceF
GD_Artifacts.A_Item.A_AllegianceG
GD_Artifacts.A_Item.A_AllegianceH
GD_Artifacts.A_Item.A_Elemental
GD_Artifacts.A_Item.A_Elemental_Status
GD_Artifacts.A_Item.A_Proficiency
GD_Artifacts.A_Item.A_Protection
GD_Artifacts.A_Item.A_Resistance
GD_Artifacts.A_Item.A_Stockpile
GD_Artifacts.A_Item.A_Strength
GD_Artifacts.A_Item.A_Tenacity
GD_Artifacts.A_Item.A_Vitality

GD_CustomItems.Items.CustomItem_AmmoSDU_CombatRifle
GD_CustomItems.Items.CustomItem_AmmoSDU_CombatRifle_NextLvl
GD_CustomItems.Items.CustomItem_AmmoSDU_Grenades
GD_CustomItems.Items.CustomItem_AmmoSDU_Grenades_NextLvl
GD_CustomItems.Items.CustomItem_AmmoSDU_Launcher
GD_CustomItems.Items.CustomItem_AmmoSDU_Launcher_NextLvl
GD_CustomItems.Items.CustomItem_AmmoSDU_RepeaterPistol
GD_CustomItems.Items.CustomItem_AmmoSDU_RepeaterPistol_NextLvl
GD_CustomItems.Items.CustomItem_AmmoSDU_Shotgun
GD_CustomItems.Items.CustomItem_AmmoSDU_Shotgun_NextLvl
GD_CustomItems.Items.CustomItem_AmmoSDU_SMG
GD_CustomItems.Items.CustomItem_AmmoSDU_SMG_NextLvl
GD_CustomItems.Items.CustomItem_AmmoSDU_SniperRifle
GD_CustomItems.Items.CustomItem_AmmoSDU_SniperRifle_NextLvl
GD_CustomItems.Items.CustomItem_SDU_Bank

GD_DefaultProfiles.IntroEchos.BD_AssassinIntroEcho
GD_DefaultProfiles.IntroEchos.BD_GunzerkerIntroEcho
GD_DefaultProfiles.IntroEchos.BD_SirenIntroEcho
GD_DefaultProfiles.IntroEchos.BD_SoldierIntroEcho

GD_GrenadeMods.A_Item_Custom.GM_BouncingBetty_Uncommon_Bandit
GD_GrenadeMods.A_Item_Custom.GM_Mirv_Uncommon_Bandit
GD_GrenadeMods.A_Item_Custom.GM_Standard_Uncommon_Bandit
GD_GrenadeMods.A_Item.GM_AreaEffect
GD_GrenadeMods.A_Item.GM_AreaEffect_2_Uncommon
GD_GrenadeMods.A_Item.GM_AreaEffect_3_Rare
GD_GrenadeMods.A_Item.GM_BouncingBetty
GD_GrenadeMods.A_Item.GM_BouncingBetty_2_Uncommon
GD_GrenadeMods.A_Item.GM_BouncingBetty_3_Rare
GD_GrenadeMods.A_Item.GM_Mirv
GD_GrenadeMods.A_Item.GM_Mirv_2_Uncommon
GD_GrenadeMods.A_Item.GM_Mirv_3_Rare
GD_GrenadeMods.A_Item.GM_Singularity
GD_GrenadeMods.A_Item.GM_Singularity_2_Uncommon
GD_GrenadeMods.A_Item.GM_Singularity_3_Rare
GD_GrenadeMods.A_Item.GM_Standard
GD_GrenadeMods.A_Item.GM_Standard_2_Uncommon
GD_GrenadeMods.A_Item.GM_Standard_3_Rare
GD_GrenadeMods.A_Item.GM_Transfusion
GD_GrenadeMods.A_Item.GM_Transfusion_2_Uncommon
GD_GrenadeMods.A_Item.GM_Transfusion_3_Rare

GD_ItemGrades.Ammo_Boss.ItemGrade_Ammo_CombatRifle
GD_ItemGrades.Ammo_Boss.ItemGrade_Ammo_Grenade
GD_ItemGrades.Ammo_Boss.ItemGrade_Ammo_RepeaterPistol
GD_ItemGrades.Ammo_Boss.ItemGrade_Ammo_Shotgun
GD_ItemGrades.Ammo_Boss.ItemGrade_Ammo_SMG
GD_ItemGrades.Ammo_Boss.ItemGrade_Ammo_SniperRifle
GD_ItemGrades.Ammo.ItemGrade_Ammo_CombatRifle
GD_ItemGrades.Ammo.ItemGrade_Ammo_Grenade
GD_ItemGrades.Ammo.ItemGrade_Ammo_RepeaterPistol
GD_ItemGrades.Ammo.ItemGrade_Ammo_RocketLauncher
GD_ItemGrades.Ammo.ItemGrade_Ammo_Shotgun
GD_ItemGrades.Ammo.ItemGrade_Ammo_SMG
GD_ItemGrades.Ammo.ItemGrade_Ammo_SniperRifle

GD_ItemGrades.BuffDrink.ItemGrade_BuffDrink_HealingInstant
GD_ItemGrades.BuffDrink.ItemGrade_BuffDrink_HealingRegen
GD_ItemGrades.BuffDrink.ItemGrade_BuffDrink_Toughness

GD_ItemGrades.Currency.ItemGrade_Currency_Crystal
GD_ItemGrades.Currency.ItemGrade_Currency_Eridium_Bar
GD_ItemGrades.Currency.ItemGrade_Currency_Eridium_Stick
GD_ItemGrades.Currency.ItemGrade_Currency_Money_Big
GD_ItemGrades.Currency.ItemGrade_Currency_Money_Little

GD_ItemGrades.Gear.ItemGrade_Gear_Shield

GD_ItemGrades.Misc.ItemGrade_BoosterShield_ShieldChargerPickup
GD_Shields.Pickups.ItemGrade_BoosterShield_LegendaryShieldChargerPickup

GD_ItemGrades.StorageDeckUpgrades.ItemGrade_SDU_Ammo
GD_ItemGrades.StorageDeckUpgrades.ItemGrade_SDU_Ammo_EarlierVersion
GD_ItemGrades.StorageDeckUpgrades.ItemGrade_SDU_Backpack
GD_ItemGrades.StorageDeckUpgrades.ItemGrade_SDU_Bank
GD_ItemGrades.StorageDeckUpgrades.ItemGrade_SDU_WeaponEquipSlot

GD_ItemGrades.ClassMods.BalDef_ClassMod_AllParts
GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin
GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_01_Common
GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_02_Uncommon
GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary
GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_01_Common
GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_02_Uncommon
GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren
GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_01_Common
GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_02_Uncommon
GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier
GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_01_Common
GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_02_Uncommon
GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho
GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_01_Common
GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_02_Uncommon
GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer
GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_01_Common
GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_02_Uncommon

GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_Absorption_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_Booster_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_Chimera_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_Impact_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_Impact_Hyperion_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_Juggernaut_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_Juggernaut_Pangolin_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_NovaAcid_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_NovaExplosive_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_NovaFire_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_NovaShock_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_Roid_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_SpikeAcid_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_SpikeExplosive_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_SpikeFire_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_SpikeShock_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_Standard_Dahl_02_Uncommon

GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Impact_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Impact_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Impact_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Juggernaut_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Juggernaut_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Juggernaut_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Acid_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Acid_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Acid_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Acid_05_Legendary
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Explosive_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Explosive_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Explosive_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Fire_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Fire_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Fire_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Fire_05_Legendary
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Shock_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Shock_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Shock_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Shock_05_Legendary
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_05_Legendary
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Acid_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Acid_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Acid_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Explosive_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Explosive_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Explosive_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Explosive_05_Legendary
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Fire_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Fire_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Fire_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Fire_05_Legendary
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Shock_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Shock_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Shock_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Shock_05_Legendary
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_03_Rare

GD_Population_Marauder.ItemBalance.GM_AreaEffect_1_NoInterp
GD_Population_Marauder.ItemBalance.GM_AreaEffect_2_Uncommon_NoInterp
GD_Population_Marauder.ItemBalance.GM_BouncingBetty_1_NoInterp
GD_Population_Marauder.ItemBalance.GM_BouncingBetty_2_Uncommon_NoInterp
GD_Population_Marauder.ItemBalance.GM_Mirv_1_NoInterp
GD_Population_Marauder.ItemBalance.GM_Mirv_2_Uncommon_NoInterp
GD_Population_Marauder.ItemBalance.GM_Singularity_1_NoInterp
GD_Population_Marauder.ItemBalance.GM_Singularity_2_Uncommon_NoInterp
GD_Population_Marauder.ItemBalance.GM_Standard_1_NoInterp
GD_Population_Marauder.ItemBalance.GM_Standard_2_Uncommon_NoInterp
GD_Population_Marauder.ItemBalance.GM_Transfusion_1_NoInterp
GD_Population_Marauder.ItemBalance.GM_Transfusion_2_Uncommon_NoInterp

GD_Weap_AssaultRifle.A_Weapons_Elemental.AR_Bandit_2_Fire
GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Dahl_1_GBX
GD_Weap_AssaultRifle.A_Weapons.AR_Bandit
GD_Weap_AssaultRifle.A_Weapons.AR_Bandit_2_Uncommon
GD_Weap_AssaultRifle.A_Weapons.AR_Bandit_3_Rare
GD_Weap_AssaultRifle.A_Weapons.AR_Bandit_3_Rare_Alien
GD_Weap_AssaultRifle.A_Weapons.AR_Bandit_4_VeryRare
GD_Weap_AssaultRifle.A_Weapons.AR_Dahl
GD_Weap_AssaultRifle.A_Weapons.AR_Dahl_2_Uncommon
GD_Weap_AssaultRifle.A_Weapons.AR_Dahl_3_Rare
GD_Weap_AssaultRifle.A_Weapons.AR_Dahl_4_VeryRare
GD_Weap_AssaultRifle.A_Weapons.AR_Jakobs
GD_Weap_AssaultRifle.A_Weapons.AR_Jakobs_2_Uncommon
GD_Weap_AssaultRifle.A_Weapons.AR_Jakobs_3_Rare
GD_Weap_AssaultRifle.A_Weapons.AR_Jakobs_4_VeryRare
GD_Weap_AssaultRifle.A_Weapons.AR_Torgue
GD_Weap_AssaultRifle.A_Weapons.AR_Torgue_2_Uncommon
GD_Weap_AssaultRifle.A_Weapons.AR_Torgue_3_Rare
GD_Weap_AssaultRifle.A_Weapons.AR_Torgue_4_VeryRare
GD_Weap_AssaultRifle.A_Weapons.AR_Vladof
GD_Weap_AssaultRifle.A_Weapons.AR_Vladof_2_Uncommon
GD_Weap_AssaultRifle.A_Weapons.AR_Vladof_3_Rare
GD_Weap_AssaultRifle.A_Weapons.AR_Vladof_4_VeryRare
GD_Weap_Launchers.A_Weapons.RL_Bandit
GD_Weap_Launchers.A_Weapons.RL_Bandit_2_Uncommon
GD_Weap_Launchers.A_Weapons.RL_Bandit_3_Rare
GD_Weap_Launchers.A_Weapons.RL_Maliwan
GD_Weap_Launchers.A_Weapons.RL_Maliwan_2_Uncommon
GD_Weap_Launchers.A_Weapons.RL_Maliwan_3_Rare
GD_Weap_Launchers.A_Weapons.RL_Tediore
GD_Weap_Launchers.A_Weapons.RL_Tediore_2_Uncommon
GD_Weap_Launchers.A_Weapons.RL_Tediore_3_Rare
GD_Weap_Launchers.A_Weapons.RL_Torgue
GD_Weap_Launchers.A_Weapons.RL_Torgue_2_Uncommon
GD_Weap_Launchers.A_Weapons.RL_Torgue_3_Rare
GD_Weap_Launchers.A_Weapons.RL_Vladof
GD_Weap_Launchers.A_Weapons.RL_Vladof_2_Uncommon
GD_Weap_Launchers.A_Weapons.RL_Vladof_3_Rare
GD_Weap_Pistol.A_Weapons_Elemental.Pistol_Maliwan_2_Corrosive
GD_Weap_Pistol.A_Weapons_Elemental.Pistol_Maliwan_2_Fire
GD_Weap_Pistol.A_Weapons_Elemental.Pistol_Maliwan_2_Shock
GD_Weap_Pistol.A_Weapons_Elemental.Pistol_Maliwan_2_Slag
GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_Starter
GD_Weap_Pistol.A_Weapons.Pistol_Bandit
GD_Weap_Pistol.A_Weapons.Pistol_Bandit_2_Uncommon
GD_Weap_Pistol.A_Weapons.Pistol_Bandit_3_Rare
GD_Weap_Pistol.A_Weapons.Pistol_Bandit_4_VeryRare
GD_Weap_Pistol.A_Weapons.Pistol_Dahl
GD_Weap_Pistol.A_Weapons.Pistol_Dahl_2_Uncommon
GD_Weap_Pistol.A_Weapons.Pistol_Dahl_3_Rare
GD_Weap_Pistol.A_Weapons.Pistol_Dahl_4_VeryRare
GD_Weap_Pistol.A_Weapons.Pistol_Hyperion
GD_Weap_Pistol.A_Weapons.Pistol_Hyperion_2_Uncommon
GD_Weap_Pistol.A_Weapons.Pistol_Hyperion_3_Rare
GD_Weap_Pistol.A_Weapons.Pistol_Hyperion_4_VeryRare
GD_Weap_Pistol.A_Weapons.Pistol_Hyperion_5_Alien
GD_Weap_Pistol.A_Weapons.Pistol_Jakobs
GD_Weap_Pistol.A_Weapons.Pistol_Jakobs_2_Uncommon
GD_Weap_Pistol.A_Weapons.Pistol_Jakobs_3_Rare
GD_Weap_Pistol.A_Weapons.Pistol_Jakobs_4_VeryRare
GD_Weap_Pistol.A_Weapons.Pistol_Maliwan
GD_Weap_Pistol.A_Weapons.Pistol_Maliwan_2_Uncommon
GD_Weap_Pistol.A_Weapons.Pistol_Maliwan_3_Rare
GD_Weap_Pistol.A_Weapons.Pistol_Maliwan_4_VeryRare
GD_Weap_Pistol.A_Weapons.Pistol_Tediore
GD_Weap_Pistol.A_Weapons.Pistol_Tediore_2_Uncommon
GD_Weap_Pistol.A_Weapons.Pistol_Tediore_3_Rare
GD_Weap_Pistol.A_Weapons.Pistol_Tediore_4_VeryRare
GD_Weap_Pistol.A_Weapons.Pistol_Torgue
GD_Weap_Pistol.A_Weapons.Pistol_Torgue_2_Uncommon
GD_Weap_Pistol.A_Weapons.Pistol_Torgue_3_Rare
GD_Weap_Pistol.A_Weapons.Pistol_Torgue_4_VeryRare
GD_Weap_Pistol.A_Weapons.Pistol_Vladof
GD_Weap_Pistol.A_Weapons.Pistol_Vladof_2_Uncommon
GD_Weap_Pistol.A_Weapons.Pistol_Vladof_3_Rare
GD_Weap_Pistol.A_Weapons.Pistol_Vladof_4_VeryRare
GD_Weap_Shotgun.A_Weapons.SG_Bandit
GD_Weap_Shotgun.A_Weapons.SG_Bandit_2_Uncommon
GD_Weap_Shotgun.A_Weapons.SG_Bandit_3_Rare
GD_Weap_Shotgun.A_Weapons.SG_Bandit_4_VeryRare
GD_Weap_Shotgun.A_Weapons.SG_Hyperion
GD_Weap_Shotgun.A_Weapons.SG_Hyperion_2_Uncommon
GD_Weap_Shotgun.A_Weapons.SG_Hyperion_3_Rare
GD_Weap_Shotgun.A_Weapons.SG_Hyperion_4_VeryRare
GD_Weap_Shotgun.A_Weapons.SG_Jakobs
GD_Weap_Shotgun.A_Weapons.SG_Jakobs_2_Uncommon
GD_Weap_Shotgun.A_Weapons.SG_Jakobs_3_Rare
GD_Weap_Shotgun.A_Weapons.SG_Jakobs_4_VeryRare
GD_Weap_Shotgun.A_Weapons.SG_Tediore
GD_Weap_Shotgun.A_Weapons.SG_Tediore_2_Uncommon
GD_Weap_Shotgun.A_Weapons.SG_Tediore_3_Rare
GD_Weap_Shotgun.A_Weapons.SG_Tediore_4_VeryRare
GD_Weap_Shotgun.A_Weapons.SG_Torgue
GD_Weap_Shotgun.A_Weapons.SG_Torgue_2_Uncommon
GD_Weap_Shotgun.A_Weapons.SG_Torgue_3_Rare
GD_Weap_Shotgun.A_Weapons.SG_Torgue_4_VeryRare
GD_Weap_SMG.A_Weapons_Unique.SMG_Gearbox_1
GD_Weap_SMG.A_Weapons.SMG_Bandit
GD_Weap_SMG.A_Weapons.SMG_Bandit_2_Uncommon
GD_Weap_SMG.A_Weapons.SMG_Bandit_3_Rare
GD_Weap_SMG.A_Weapons.SMG_Bandit_4_VeryRare
GD_Weap_SMG.A_Weapons.SMG_Dahl
GD_Weap_SMG.A_Weapons.SMG_Dahl_2_Uncommon
GD_Weap_SMG.A_Weapons.SMG_Dahl_3_Rare
GD_Weap_SMG.A_Weapons.SMG_Dahl_4_VeryRare
GD_Weap_SMG.A_Weapons.SMG_Hyperion
GD_Weap_SMG.A_Weapons.SMG_Hyperion_2_Uncommon
GD_Weap_SMG.A_Weapons.SMG_Hyperion_3_Rare
GD_Weap_SMG.A_Weapons.SMG_Hyperion_4_VeryRare
GD_Weap_SMG.A_Weapons.SMG_Maliwan
GD_Weap_SMG.A_Weapons.SMG_Maliwan_2_Uncommon
GD_Weap_SMG.A_Weapons.SMG_Maliwan_3_Rare
GD_Weap_SMG.A_Weapons.SMG_Maliwan_4_VeryRare
GD_Weap_SMG.A_Weapons.SMG_Tediore
GD_Weap_SMG.A_Weapons.SMG_Tediore_2_Uncommon
GD_Weap_SMG.A_Weapons.SMG_Tediore_3_Rare
GD_Weap_SMG.A_Weapons.SMG_Tediore_4_VeryRare
GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Gearbox_1
GD_Weap_SniperRifles.A_Weapons.Sniper_Dahl
GD_Weap_SniperRifles.A_Weapons.Sniper_Dahl_2_Uncommon
GD_Weap_SniperRifles.A_Weapons.Sniper_Dahl_3_Rare
GD_Weap_SniperRifles.A_Weapons.Sniper_Dahl_4_VeryRare
GD_Weap_SniperRifles.A_Weapons.Sniper_Hyperion
GD_Weap_SniperRifles.A_Weapons.Sniper_Hyperion_2_Uncommon
GD_Weap_SniperRifles.A_Weapons.Sniper_Hyperion_3_Rare
GD_Weap_SniperRifles.A_Weapons.Sniper_Hyperion_4_VeryRare
GD_Weap_SniperRifles.A_Weapons.Sniper_Jakobs
GD_Weap_SniperRifles.A_Weapons.Sniper_Jakobs_2_Uncommon
GD_Weap_SniperRifles.A_Weapons.Sniper_Jakobs_3_Rare
GD_Weap_SniperRifles.A_Weapons.Sniper_Jakobs_4_VeryRare
GD_Weap_SniperRifles.A_Weapons.Sniper_Maliwan
GD_Weap_SniperRifles.A_Weapons.Sniper_Maliwan_2_Uncommon
GD_Weap_SniperRifles.A_Weapons.Sniper_Maliwan_3_Rare
GD_Weap_SniperRifles.A_Weapons.Sniper_Maliwan_4_VeryRare
GD_Weap_SniperRifles.A_Weapons.Sniper_Vladof
GD_Weap_SniperRifles.A_Weapons.Sniper_Vladof_2_Uncommon
GD_Weap_SniperRifles.A_Weapons.Sniper_Vladof_3_Rare
GD_Weap_SniperRifles.A_Weapons.Sniper_Vladof_4_VeryRare
GD_Z1_CordiallyInvitedData.MW_Teapot
GD_Z1_RockPaperGenocideData.MW_RockPaper_Corrosive
GD_Z1_RockPaperGenocideData.MW_RockPaper_Fire
GD_Z1_RockPaperGenocideData.MW_RockPaper_Shock
GD_Z1_RockPaperGenocideData.MW_RockPaper_Slag
GD_Z2_TrailerTrashinData.FlareGun
GD_Z3_MedicalMystery2Data.MW_MedicalMystery_AlienGun

"""
