from __future__ import annotations

import enum
from typing import Callable, List, Optional
from unrealsdk import UObject


CurrentVersion = 7
SupportedVersions = (1, 2, 3, 4, 5, 6, 7)


class Character(enum.Enum):
    attr_init: UObject

    Assassin = "GD_PlayerClassId.Assassin"
    Mercenary = "GD_PlayerClassId.Mercenary"
    Siren = "GD_PlayerClassId.Siren"
    Soldier = "GD_PlayerClassId.Soldier"
    Psycho = "GD_LilacPackageDef.PlayerClassId.Psycho"
    Mechromancer = "GD_TulipPackageDef.PlayerClassId.Mechromancer"


class Category(str, enum.Enum):
    Content = "Content"
    Missions = "Missions"
    Enemies = "Enemies"
    Other = "Other"
    Settings = "Settings"


class Tag(enum.IntFlag):
    def __contains__(self, other: enum.IntFlag) -> bool:
        return self & other == other

    category: Category
    default: bool
    caption: str
    description: str

    content_title: Optional[str]
    dlc_path: Optional[str]

    BaseGame = enum.auto()
    PiratesBooty = enum.auto()
    CampaignOfCarnage = enum.auto()
    HammerlocksHunt = enum.auto()
    DragonKeep = enum.auto()
    FightForSanctuary = enum.auto()
    BloodyHarvest = enum.auto()
    WattleGobbler = enum.auto()
    MercenaryDay = enum.auto()
    WeddingDayMassacre = enum.auto()
    SonOfCrawmerax = enum.auto()
    UVHMPack = enum.auto()
    DigistructPeak = enum.auto()

    ShortMission = enum.auto()
    LongMission = enum.auto()
    VeryLongMission = enum.auto()
    Slaughter = enum.auto()

    UniqueEnemy = enum.auto()
    SlowEnemy = enum.auto()
    RareEnemy = enum.auto()
    VeryRareEnemy = enum.auto()
    MobFarm = enum.auto()
    Raid = enum.auto()
    MissionLocation = enum.auto()
    EvolvedEnemy = enum.auto()
    DigistructEnemy = enum.auto()

    Vendor = enum.auto()
    Miscellaneous = enum.auto()

    DuplicateItems = enum.auto()
    EnableHints = enum.auto()

    VehicleMission = enum.auto()
    Freebie = enum.auto()

    Excluded = 0x1 << 36


TagList: List[Tag] = []

ContentTags = Tag(0)
MissionTags = Tag(0)
EnemyTags = Tag(0)
OtherTags = Tag(0)

# fmt: off

for tag, content_title, dlc_path in (
    (Tag.BaseGame,           "Borderlands 2",                              None),
    (Tag.PiratesBooty,       "Captain Scarlett and her Pirate's Booty",    "GD_OrchidPackageDef.ItemSetDef_Orchid"),
    (Tag.CampaignOfCarnage,  "Mr. Torgue's Campaign of Carnage",           "GD_IrisPackageDef.ItemSetDef_Iris"),
    (Tag.HammerlocksHunt,    "Sir Hammerlock's Big Game Hunt",             "GD_SagePackageDef.ItemSetDef_Sage"),
    (Tag.DragonKeep,         "Tiny Tina's Assault on Dragon Keep",         "GD_AsterPackageDef.ItemSetDef_Aster"),
    (Tag.FightForSanctuary,  "Commander Lilith & the Fight for Sanctuary", "GD_AnemonePackageDef.ItemSetDef_Anemone"),
    (Tag.BloodyHarvest,      "Headhunter 1: Bloody Harvest",               "GD_FlaxPackageDef.ItemSetDef_Flax"),
    (Tag.WattleGobbler,      "Headhunter 2: Wattle Gobbler",               "GD_AlliumPackageDef.ItemSetDef_Allium_TG"),
    (Tag.MercenaryDay,       "Headhunter 3: Mercenary Day",                "GD_AlliumPackageDef.ItemSetDef_Allium_Xmas"),
    (Tag.WeddingDayMassacre, "Headhunter 4: Wedding Day Massacre",         "GD_NasturtiumPackageDef.ItemSetDef_NasturtiumVday"),
    (Tag.SonOfCrawmerax,     "Headhunter 5: Son of Crawmerax",             "GD_NasturtiumPackageDef.ItemSetDef_NasturtiumEaster"),
    (Tag.UVHMPack,           "Ultimate Vault Hunter Upgrade Pack",         "GD_GladiolusPackageDef.ItemSetDef_Gladiolus"),
    (Tag.DigistructPeak,     "Ultimate Vault Hunter Upgrade Pack 2",       "GD_LobeliaPackageDef.CustomItemSetDef_Lobelia"),
):
    tag.content_title = content_title
    tag.dlc_path = dlc_path

for tag, category, default, caption, description in (
    (Tag.BaseGame,           Category.Content,  True,  "Base Game",            f"Include items and locations from Borderlands 2's base game."),
    (Tag.PiratesBooty,       Category.Content,  True,  "Pirate's Booty",       f"Include items and locations from {Tag.PiratesBooty.content_title}."),
    (Tag.CampaignOfCarnage,  Category.Content,  True,  "Campaign Of Carnage",  f"Include items and locations from {Tag.CampaignOfCarnage.content_title}."),
    (Tag.HammerlocksHunt,    Category.Content,  True,  "Hammerlock's Hunt",    f"Include items and locations from {Tag.HammerlocksHunt.content_title}."),
    (Tag.DragonKeep,         Category.Content,  True,  "Dragon Keep",          f"Include items and locations from {Tag.DragonKeep.content_title}."),
    (Tag.FightForSanctuary,  Category.Content,  True,  "Fight For Sanctuary",  f"Include items and locations from {Tag.FightForSanctuary.content_title}."),
    (Tag.BloodyHarvest,      Category.Content,  True,  "Bloody Harvest",       f"Include items and locations from {Tag.BloodyHarvest.content_title}."),
    (Tag.WattleGobbler,      Category.Content,  True,  "Wattle Gobbler",       f"Include items and locations from {Tag.WattleGobbler.content_title}."),
    (Tag.MercenaryDay,       Category.Content,  True,  "Mercenary Day",        f"Include items and locations from {Tag.MercenaryDay.content_title}."),
    (Tag.WeddingDayMassacre, Category.Content,  True,  "Wedding Day Massacre", f"Include items and locations from {Tag.WeddingDayMassacre.content_title}."),
    (Tag.SonOfCrawmerax,     Category.Content,  True,  "Son Of Crawmerax",     f"Include items and locations from {Tag.SonOfCrawmerax.content_title}."),
    (Tag.UVHMPack,           Category.Content,  True,  "UVHM Pack",            f"Include items from {Tag.UVHMPack.content_title}."),
    (Tag.DigistructPeak,     Category.Content,  True,  "Digistruct Peak",      f"Include items and locations from {Tag.DigistructPeak.content_title}."),

    (Tag.ShortMission,       Category.Missions, True,  "Short Missions",       "Assign items to short side missions."),
    (Tag.LongMission,        Category.Missions, True,  "Long Missions",        "Assign items to longer side missions. Longer mission turn-ins provide bonus loot options."),
    (Tag.VeryLongMission,    Category.Missions, False, "Very Long Missions",   "Assign items to very long side missions (including Headhunter missions). Very long mission turn-ins provide even more bonus loot options."),
    (Tag.VehicleMission,     Category.Missions, True,  "Vehicle Missions",     "Assign items to missions primarily involving driving vehicles."),
    (Tag.Slaughter,          Category.Missions, False, "Slaughter Missions",   "Assign items to slaughter missions."),

    (Tag.UniqueEnemy,        Category.Enemies,  True,  "Unique Enemies",       "Assign items to refarmable enemies."),
    (Tag.SlowEnemy,          Category.Enemies,  True,  "Slow Enemies",         "Assign items to enemies which take longer than usual each kill. Slower enemies drop loot with greater frequency."),
    (Tag.RareEnemy,          Category.Enemies,  True,  "Rare Enemies",         "Assign items to enemies that are rare spawns. Rare enemies drop loot with greater frequency."),
    (Tag.VeryRareEnemy,      Category.Enemies,  False, "Very Rare Enemies",    "Assign items to enemies that are very rare spawns. Very rare enemies drop loot with much greater frequency."),
    (Tag.MobFarm,            Category.Enemies,  False, "Mob Farms",            "Assign items to mobs which have rare drops in the vanilla game. Mob farm enemies drop loot rarely (but not too rarely)."),
    (Tag.EvolvedEnemy,       Category.Enemies,  False, "Evolved Enemies",      "Assign items to enemies that are evolved forms of other enemies."),
    (Tag.DigistructEnemy,    Category.Enemies,  False, "Digistruct Enemies",   "Assign items to the versions of unique enemies that are encountered in Digistruct Peak."),

    (Tag.Raid,               Category.Other,    False, "Raids",                "Assign items to locations that are a part of raids. Raid locations drop many loot instances guaranteed."),
    (Tag.MissionLocation,    Category.Other,    False, "Mission Locations",    "Assign items to locations that are only available while doing (or re-doing) a mission."),
    (Tag.Vendor,             Category.Other,    False, "Special Vendors",      "Assign items to unique vendors to be purchasable with Seraph Crystals or Torgue Tokens."),
    (Tag.Freebie,            Category.Other,    True,  "Freebies",             "Assign items to locations that don't involve any enemies."),
    (Tag.Miscellaneous,      Category.Other,    True,  "Miscellaneous",        "Assign items to miscellaneous loot locations (boxes that give unique items, etcetera)."),

    (Tag.DuplicateItems,     Category.Settings, False, "Duplicate Items",      "For seeds with more locations than items, random items can have multiple locations."),
    (Tag.EnableHints,        Category.Settings, True,  "Allow Hints",          "Whether this seed should generate a spoiler log, and also whether hints should be allowed while playing it."),
):
    
    # fmt: on

    tag.category = category
    tag.default = default
    tag.caption = caption
    tag.description = description

    TagList.append(tag)

    if category == Category.Content:
        ContentTags |= tag
    if category == Category.Missions:
        MissionTags |= tag
    if category == Category.Enemies:
        EnemyTags |= tag
    if category == Category.Other:
        OtherTags |= tag


class Hint(str, enum.Enum):
    formatter: Callable[[str], str]

    def __str__(self) -> str:
        return self.value

    Dud = "Nothing"

    PurplePistol = "Purple Pistol"
    UniquePistol = "Unique Pistol"
    LegendaryPistol = "Legendary Pistol"

    PurpleAR = "Purple Assault Rifle"
    UniqueAR = "Unique Assault Rifle"
    LegendaryAR = "Legendary Assault Rifle"

    PurpleShotgun = "Purple Shotgun"
    UniqueShotgun = "Unique Shotgun"
    LegendaryShotgun = "Legendary Shotgun"

    PurpleSMG = "Purple SMG"
    UniqueSMG = "Unique SMG"
    LegendarySMG = "Legendary SMG"

    PurpleSniper = "Purple Sniper Rifle"
    UniqueSniper = "Unique Sniper Rifle"
    LegendarySniper = "Legendary Sniper Rifle"

    PurpleLauncher = "Purple Rocket Launcher"
    UniqueLauncher = "Unique Rocket Launcher"
    LegendaryLauncher = "Legendary Rocket Launcher"

    EtechWeapon = "E-tech Weapon"
    PearlescentWeapon = "Pearlescent Weapon"
    SeraphWeapon = "Seraph Weapon"
    EffervescentWeapon = "Effervescent Weapon"

    PurpleShield = "Purple Shield"
    UniqueShield = "Unique Shield"
    LegendaryShield = "Legendary Shield"

    BlueClassMod = "Blue Class Mod"
    PurpleClassMod = "Purple Class Mod"
    LegendaryClassMod = "Legendary Class Mod"

    PurpleGrenade = "Purple Grenade"
    UniqueGrenade = "Unique Grenade"
    LegendaryGrenade = "Legendary Grenade"

    PurpleRelic = "Purple Relic"
    UniqueRelic = "Unique Relic"
    EtechRelic = "E-tech Relic"

    SeraphItem = "Seraph Item"
    EffervescentItem = "Effervescent Item"


def _format_dud(string: str) -> str:
    return f"<font color='#bc9898'>{string}</font>"


def _format_blue(string: str) -> str:
    return f"<font color='#3c8eff'>{string}</font>"


def _format_purple(string: str) -> str:
    return f"<font color='#a83fe5'>{string}</font>"


def _format_etech(string: str) -> str:
    return f"<font color='#ca00a8'>{string}</font>"


def _format_legendary(string: str) -> str:
    return f"<font color='#ffb400'>{string}</font>"


def _format_unique(string: str) -> str:
    return f"<font color='#dc4646'>{string}</font>"


def _format_seraph(string: str) -> str:
    return f"<font color='#ff9ab8'>{string}</font>"


def _format_pearlescent(string: str) -> str:
    return f"<font color='#00ffff'>{string}</font>"


def _format_effervescent(string: str) -> str:
    colors = (
        "ffadad",
        "ffd6a5",
        "fdffb6",
        "caffbf",
        "9bf6ff",
        "a0c4ff",
        "bdb2ff",
        "ffc6ff",
    )
    return "".join(
        f"<font color='#{colors[index % len(colors)]}'>{character}</font>"
        for index, character in enumerate(string)
    )


Hint.Dud.formatter = _format_dud

Hint.BlueClassMod.formatter = _format_blue
Hint.PurpleClassMod.formatter = _format_purple
Hint.LegendaryClassMod.formatter = _format_legendary

Hint.PurpleShield.formatter = _format_purple
Hint.UniqueShield.formatter = _format_unique
Hint.LegendaryShield.formatter = _format_legendary

Hint.PurpleRelic.formatter = _format_purple
Hint.UniqueRelic.formatter = _format_unique
Hint.EtechRelic.formatter = _format_etech

Hint.PurpleGrenade.formatter = _format_purple
Hint.UniqueGrenade.formatter = _format_unique
Hint.LegendaryGrenade.formatter = _format_legendary

Hint.PurplePistol.formatter = _format_purple
Hint.UniquePistol.formatter = _format_unique
Hint.LegendaryPistol.formatter = _format_legendary

Hint.PurpleAR.formatter = _format_purple
Hint.UniqueAR.formatter = _format_unique
Hint.LegendaryAR.formatter = _format_legendary

Hint.PurpleShotgun.formatter = _format_purple
Hint.UniqueShotgun.formatter = _format_unique
Hint.LegendaryShotgun.formatter = _format_legendary

Hint.PurpleSMG.formatter = _format_purple
Hint.UniqueSMG.formatter = _format_unique
Hint.LegendarySMG.formatter = _format_legendary

Hint.PurpleSniper.formatter = _format_purple
Hint.UniqueSniper.formatter = _format_unique
Hint.LegendarySniper.formatter = _format_legendary

Hint.PurpleLauncher.formatter = _format_purple
Hint.UniqueLauncher.formatter = _format_unique
Hint.LegendaryLauncher.formatter = _format_legendary

Hint.EtechWeapon.formatter = _format_etech
Hint.PearlescentWeapon.formatter = _format_pearlescent

Hint.SeraphItem.formatter = _format_seraph
Hint.SeraphWeapon.formatter = _format_seraph

Hint.EffervescentItem.formatter = _format_effervescent
Hint.EffervescentWeapon.formatter = _format_effervescent


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
)
