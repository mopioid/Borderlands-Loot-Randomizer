from __future__ import annotations

import enum
from typing import Callable, List, Optional
from unrealsdk import UObject


CurrentVersion = 3
SupportedVersions = (1, 3)


class Character(enum.Enum):
    attr_init: UObject

    Gladiator = "GD_PlayerClassId.Gladiator"
    Enforcer = "GD_PlayerClassId.Enforcer"
    Lawbringer = "GD_PlayerClassId.Lawbringer"
    Prototype = "GD_PlayerClassId.Prototype"
    Doppelganger = "GD_QuincePackageDef.PlayerClassId.Doppel"
    Baroness = "GD_CrocusPackageDef.PlayerClassId.Baroness"


class Category(str, enum.Enum):
    Content = "Content"
    Missions = "Missions"
    Enemies = "Enemies"
    Other = "Other"
    Settings = "Settings"


class Tag(enum.IntFlag):
    def __contains__(self, other: enum.IntFlag) -> bool:
        return int(self) & int(other) == int(other)

    category: Category
    default: bool
    caption: str
    description: str

    content_title: Optional[str]
    dlc_path: Optional[str]

    BaseGame = enum.auto()
    Holodome = enum.auto()
    ClaptasticVoyage = enum.auto()
    ShockDrop = enum.auto()
    Holiday = enum.auto()

    ShortMission = enum.auto()
    LongMission = enum.auto()
    VeryLongMission = enum.auto()
    Slaughter = enum.auto()
    VehicleMission = enum.auto()

    UniqueEnemy = enum.auto()
    SlowEnemy = enum.auto()
    RareEnemy = enum.auto()
    VeryRareEnemy = enum.auto()
    MobFarm = enum.auto()
    Raid = enum.auto()
    MissionLocation = enum.auto()

    Miscellaneous = enum.auto()

    DuplicateItems = enum.auto()
    EnableHints = enum.auto()

    Freebie = enum.auto()

    Excluded = 0x1 << 36


TagList: List[Tag] = []

ContentTags = Tag(0)
MissionTags = Tag(0)
EnemyTags = Tag(0)
OtherTags = Tag(0)

# fmt: off

for tag, content_title, dlc_path in (
    ( Tag.BaseGame, "Borderlands: The Pre-Sequel", None),
    ( Tag.Holodome, "The Holodome Onslaught", "GD_PetuniaPackageDef.CustomItemSetDef_Petunia"),
    ( Tag.ClaptasticVoyage, "Claptastic Voyage and Ultimate Vault Hunter Upgrade Pack 2", "GD_MarigoldPackageDef.CustomItemSetDef_Marigold"),
    ( Tag.ShockDrop, "Shock Drop Slaughter Pit", "GD_FreesiaPackageDef.ItemSet_Freesia"),
    ( Tag.Holiday, "Holiday Events", None),
):
    tag.content_title = content_title; tag.dlc_path = dlc_path

for tag, category, default, caption, description in (
    (Tag.BaseGame,           Category.Content,  True,  "Base Game",          f"Include items and locations from Borderlands: The Pre-Sequel's base game."),
    (Tag.ShockDrop,          Category.Content,  True,  "Shock Drop",         f"Include items and locations from {Tag.ShockDrop.content_title}."),
    (Tag.ClaptasticVoyage,   Category.Content,  True,  "Claptastic Voyage",  f"Include items and locations from {Tag.ClaptasticVoyage.content_title}."),
    (Tag.Holodome,           Category.Content,  True,  "Holodome",           f"Include items and locations from {Tag.Holodome.content_title}."),
    (Tag.Holiday,            Category.Content,  True,  "Holiday Events",     f"Include items and locations from holiday events. Holiday events can be toggled at any time from the Fast Travel menu."),

    (Tag.ShortMission,       Category.Missions, True,  "Short Missions",     "Assign items to short side missions."),
    (Tag.LongMission,        Category.Missions, True,  "Long Missions",      "Assign items to longer side missions. Longer mission turn-ins provide bonus loot options."),
    (Tag.VeryLongMission,    Category.Missions, True,  "Very Long Missions", "Assign items to very long side missions (including Headhunter missions). Very long mission turn-ins provide even more bonus loot options."),
    (Tag.VehicleMission,     Category.Missions, True,  "Vehicle Missions",   "Assign items to missions primarily involving driving vehicles."),
    (Tag.Slaughter,          Category.Missions, True,  "Slaughter Missions", "Assign items to slaughter missions."),

    (Tag.UniqueEnemy,        Category.Enemies,  True,  "Unique Enemies",     "Assign items to refarmable enemies."),
    (Tag.SlowEnemy,          Category.Enemies,  True,  "Slow Enemies",       "Assign items to enemies which take longer than usual each kill. Slower enemies drop loot with greater frequency."),
    (Tag.RareEnemy,          Category.Enemies,  True,  "Rare Enemies",       "Assign items to enemies that are rare spawns. Rare enemies drop loot with greater frequency."),
    (Tag.VeryRareEnemy,      Category.Enemies,  True,  "Very Rare Enemies",  "Assign items to enemies that are very rare spawns. Very rare enemies drop loot with much greater frequency."),
    (Tag.MobFarm,            Category.Enemies,  True,  "Mob Farms",          "Assign items to mobs which have rare drops in the vanilla game. Mob farm enemies drop loot rarely (but not too rarely)."),

    (Tag.Raid,               Category.Other,    True,  "Raids",              "Assign items to locations that are a part of raids. Raid locations drop many loot instances guaranteed."),
    (Tag.MissionLocation,    Category.Other,    True,  "Mission Locations",  "Assign items to locations that are only available while doing (or re-doing) a mission."),
    (Tag.Freebie,            Category.Other,    True,  "Freebies",           "Assign items to locations that don't involve any enemies."),
    (Tag.Miscellaneous,      Category.Other,    True,  "Miscellaneous",      "Assign items to miscellaneous loot locations (boxes that give unique items, etcetera)."),

    (Tag.DuplicateItems,     Category.Settings, False, "Duplicate Items",    "For seeds with more locations than items, random items can have multiple locations."),
    (Tag.EnableHints,        Category.Settings, True,  "Allow Hints",        "Whether this seed should generate a spoiler log, and also whether hints should be allowed while playing it."),
):
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

    EnemyTags |= Tag.MissionLocation

# fmt: on


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

    PurpleLaser = "Purple Laser"
    UniqueLaser = "Unique Laser"
    LegendaryLaser = "Legendary Laser"

    PurpleLauncher = "Purple Rocket Launcher"
    UniqueLauncher = "Unique Rocket Launcher"

    PurpleShield = "Purple Shield"
    UniqueShield = "Unique Shield"
    LegendaryShield = "Legendary Shield"

    ClassMod = "Class Mod"
    LegendaryClassMod = "Legendary Class Mod"

    PurpleGrenade = "Purple Grenade"
    UniqueGrenade = "Unique Grenade"
    LegendaryGrenade = "Legendary Grenade"

    PurpleOz = "Purple Oz Kit"
    UniqueOz = "Unique Oz Kit"
    LegendaryOz = "Legendary Oz Kit"


def _format_dud(string: str) -> str:
    return f"<font color='#bc9898'>{string}</font>"


def _format_blue(string: str) -> str:
    return f"<font color='#3c8eff'>{string}</font>"


def _format_purple(string: str) -> str:
    return f"<font color='#a83fe5'>{string}</font>"


def _format_legendary(string: str) -> str:
    return f"<font color='#ffb400'>{string}</font>"


def _format_unique(string: str) -> str:
    return f"<font color='#dc4646'>{string}</font>"


# def _format_glitch(string: str) -> str:
#     return f"<font color='#ffa4e7'>{string}</font>"


Hint.Dud.formatter = _format_dud

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

Hint.PurpleLaser.formatter = _format_purple
Hint.UniqueLaser.formatter = _format_unique
Hint.LegendaryLaser.formatter = _format_legendary

Hint.PurpleLauncher.formatter = _format_purple
Hint.UniqueLauncher.formatter = _format_unique

Hint.PurpleShield.formatter = _format_purple
Hint.UniqueShield.formatter = _format_unique
Hint.LegendaryShield.formatter = _format_legendary

Hint.ClassMod.formatter = _format_blue
Hint.LegendaryClassMod.formatter = _format_legendary

Hint.PurpleGrenade.formatter = _format_purple
Hint.UniqueGrenade.formatter = _format_unique
Hint.LegendaryGrenade.formatter = _format_legendary

Hint.PurpleOz.formatter = _format_purple
Hint.UniqueOz.formatter = _format_unique
Hint.LegendaryOz.formatter = _format_legendary


pool_whitelist = (
    "Pool_Ammo_All_DropAlways",
    "Pool_Ammo_All_Emergency",
    "Pool_Ammo_All_NeedOnly",
    "Pool_Ammo_Grenades_BoomBoom",
    "Pool_Health_All",
    "Pool_Money",
    "Pool_Money_1_BIG",
    "Pool_Money_1or2",
    "Pool_Moonstone",
    "Pool_Moonstone_Cluster",
    "Pool_Oxygen_Instant",
    "IP_NovaNoProblemEcho",
)
