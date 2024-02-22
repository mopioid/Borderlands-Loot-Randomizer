from __future__ import annotations

from unrealsdk import Log, UObject, FindObject #type: ignore

from Mods import ModMenu #type: ignore

from base64 import b32encode, b32decode
from struct import Struct
from random import getrandbits

import enum

from typing import Tuple


Probability = Tuple[float, UObject, UObject, float]
BalancedItem = Tuple[UObject, UObject, Probability, bool]


Version = 0


class Tag(enum.IntFlag):
    title: str
    path: str

    BaseGame           = enum.auto()
    PiratesBooty       = enum.auto()
    CampaignOfCarnage  = enum.auto()
    HammerlocksHunt    = enum.auto()
    DragonKeep         = enum.auto()
    FightForSanctuary  = enum.auto()
    BloodyHarvest      = enum.auto()
    WattleGobbler      = enum.auto()
    MercenaryDay       = enum.auto()
    WeddingDayMassacre = enum.auto()
    SonOfCrawmerax     = enum.auto()
    UVHMPack           = enum.auto()
    DigistructPeak     = enum.auto()
 
    ShortMission       = enum.auto()
    LongMission        = enum.auto()
    VeryLongMission    = enum.auto()
    Slaughter          = enum.auto()
    RaidMission        = enum.auto()

    UniqueEnemy        = enum.auto()
    SlowEnemy          = enum.auto()
    RareEnemy          = enum.auto()
    VeryRareEnemy      = enum.auto()
    RaidEnemy          = enum.auto()
    MissionEnemy       = enum.auto()
    EvolvedEnemy       = enum.auto()
    DigistructEnemy    = enum.auto()

    Other              = enum.auto()


ContentTags = Tag.BaseGame

for tag, title, path in (
    ( Tag.PiratesBooty,       "Captain Scarlett and her Pirate's Booty",    "GD_OrchidPackageDef.ItemSetDef_Orchid"               ),
    ( Tag.CampaignOfCarnage,  "Mr. Torgue's Campaign of Carnage",           "GD_IrisPackageDef.ItemSetDef_Iris"                   ),
    ( Tag.HammerlocksHunt,    "Sir Hammerlock's Big Game Hunt",             "GD_SagePackageDef.ItemSetDef_Sage"                   ),
    ( Tag.DragonKeep,         "Tiny Tina's Assault on Dragon Keep",         "GD_AsterPackageDef.ItemSetDef_Aster"                 ),
    ( Tag.FightForSanctuary,  "Commander Lilith & the Fight for Sanctuary", "GD_AnemonePackageDef.ItemSetDef_Anemone"             ),
    ( Tag.BloodyHarvest,      "Headhunter 1: Bloody Harvest",               "GD_AlliumPackageDef.ItemSetDef_Allium_TG"            ),
    ( Tag.WattleGobbler,      "Headhunter 2: Wattle Gobbler",               "GD_AlliumPackageDef.ItemSetDef_Allium_Xmas"          ),
    ( Tag.MercenaryDay,       "Headhunter 3: Mercenary Day",                "GD_FlaxPackageDef.ItemSetDef_Flax"                   ),
    ( Tag.WeddingDayMassacre, "Headhunter 4: Wedding Day Massacre",         "GD_NasturtiumPackageDef.ItemSetDef_NasturtiumEaster" ),
    ( Tag.SonOfCrawmerax,     "Headhunter 5: Son of Crawmerax",             "GD_NasturtiumPackageDef.ItemSetDef_NasturtiumVday"   ),
    ( Tag.UVHMPack,           "Ultimate Vault Hunter Upgrade Pack",         "GD_GladiolusPackageDef.ItemSetDef_Gladiolus"         ),
    ( Tag.DigistructPeak,     "Ultimate Vault Hunter Upgrade Pack 2",       "GD_LobeliaPackageDef.CustomItemSetDef_Lobelia"       ),
):
    tag.title = title
    tag.path = path
    ContentTags |= tag


OwnedContent: Tag = Tag.BaseGame

SelectedTags: Tag


HintType = ModMenu.Options.Spinner(
    Caption="Hints",
    Description=(
        "How much information loot sources should reveal about their item drop. \"Vague\" will only"
        " describe rarity and type, while \"spoiler\" will name the exact item."
    ),
    Choices=["None", "Vague", "Spoiler"],
    StartingValue="Vague"
)


def Enable():
    global OwnedContent, SelectedTags
    SelectedTags = Tag.BaseGame

    for tag in Tag:
        if hasattr(tag, "path") and FindObject("DownloadableItemSetDefinition", tag.path).CanUse():
            OwnedContent |= tag

    SelectedTags = Tag(~0)


def Disable():
    pass


_seed_struct = Struct("<IBI")

class Seed:
    value: int
    version: int
    tags: Tag

    def __init__(self, value: int, version: int, tags: Tag) -> None:
        if value   > (2 ** 32 - 1): raise ValueError
        if version > (2 **  8 - 1): raise ValueError
        if tags    > (2 ** 32 - 1): raise ValueError

        self.value = value; self.version = version; self.tags = tags

    @classmethod
    def Generate(cls, tags: Tag) -> Seed:
        return cls(getrandbits(32), Version, tags)

    @classmethod
    def FromString(cls, string: str) -> Seed:
        string = "".join(c.upper() for c in string if c.isalnum()) + "="
        try:
            data = b32decode(string)
            assert(len(data) == _seed_struct.size)
        except:
            raise ValueError

        value, version, tags = _seed_struct.unpack(data)
        return cls(value, version, Tag(tags))

    def to_string(self) -> str:
        data = _seed_struct.pack(self.value, self.version, self.tags)
        string = b32encode(data).decode("ascii").strip("=").lower()
        return f"{string[0:5]}-{string[5:10]}-{string[10:15]}"


"""
- toggle mission reward previews
    - option for just icon
    - option for full spoiler

"""
