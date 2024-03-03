from unrealsdk import Log, ConstructObject, FindObject, GetEngine, KeepAlive, UPackage #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct #type: ignore

import enum

from typing import Any, Callable, Iterator, List, Optional, Tuple, Union


Probability = Tuple[float, UObject, UObject, float]
BalancedItem = Tuple[UObject, UObject, Probability, bool]


Package: UPackage = ConstructObject("Package", None, "LootRandomizer")


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

    UniqueEnemy        = enum.auto()
    SlowEnemy          = enum.auto()
    RareEnemy          = enum.auto()
    VeryRareEnemy      = enum.auto()
    MobFarm            = enum.auto()
    RaidEnemy          = enum.auto()
    MissionEnemy       = enum.auto()
    EvolvedEnemy       = enum.auto()
    DigistructEnemy    = enum.auto()

    SeraphVendor       = enum.auto()
    Miscellaneous      = enum.auto()

    DuplicateItems     = enum.auto()
    EnableHints        = enum.auto()


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

MissionTags = (
    Tag.ShortMission    |
    Tag.LongMission     |
    Tag.VeryLongMission |
    Tag.Slaughter       |
    Tag.RaidEnemy
)

EnemyTags = (
    Tag.UniqueEnemy     |
    Tag.SlowEnemy       |
    Tag.RareEnemy       |
    Tag.RaidEnemy       |
    Tag.MissionEnemy    |
    Tag.DigistructEnemy |
    Tag.EvolvedEnemy
)


class Hint(str, enum.Enum):
    # TODO
    ClassMod = "Class Mod"

    BlueClassMod = "Blue Class Mod"
    PurpleClassMod = "Purple Class Mod"
    LegendaryClassMod = "Legendary Class Mod"

    PurpleShield = "Purple Shield"
    UniqueShield = "Unique Shield"
    LegendaryShield = "Legendary Shield"

    PurpleRelic = "Purple Relic"
    UniqueRelic = "Unique Relic"
    EtechRelic = "E-tech Relic"

    PurpleGrenade = "Purple Grenade"
    UniqueGrenade = "Unique Grenade"
    LegendaryGrenade = "Legendary Grenade"

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

    SeraphItem = "Seraph Item"
    SeraphWeapon = "Seraph Weapon"

    EffervescentItem = "Effervescent Item"
    EffervescentWeapon = "Effervescent Weapon"


def console_command(command: str) -> None:
    GetEngine().GamePlayers[0].Actor.ConsoleCommand(command)

def set_command(uobject: UObject, attribute: str, value: str):
    console_command(f"set {UObject.PathName(uobject)} {attribute} {value}")


def convert_struct(fstruct: Any) -> Tuple[Any, ...]:
    iterator: Optional[Iterator] = None
    try: iterator = iter(fstruct)
    except: pass
    if iterator:
        return [convert_struct(value) for value in iterator]

    struct_type = getattr(fstruct, "structType", None)
    if struct_type is None:
        return fstruct

    values: List[Any] = []
    
    while struct_type:
        attribute = struct_type.Children
        while attribute:
            value = getattr(fstruct, attribute.GetName())
            values.append(convert_struct(value))
            attribute = attribute.Next
        struct_type = struct_type.SuperField

    return tuple(values)


def construct_object(basis: Union[str, UObject], name: Union[str, UObject, None] = None) -> UObject:
    path: Optional[str] = None
    class_name: str = basis

    kwargs = {'Class': basis, 'Outer': Package}

    if isinstance(name, str):
        name = "".join(char for char in name if char.isalnum() or char == "_")
        kwargs['Name'] = name
        path = f"{Package.Name}.{name}"
    elif name:
        kwargs['Outer'] = name

    if not isinstance(basis, str):
        kwargs['Template'] = basis
        kwargs['Class'] = basis.Class
        class_name = basis.Class.Name

    obj: Optional[UObject] = None
    if path:
        obj = FindObject(class_name, path)

    if not obj:
        obj = ConstructObject(**kwargs)
        KeepAlive(obj)

    return obj


def do_next_tick(*routines: Callable[[], None]) -> None:
    def tick(caller: UObject, function: UFunction, params: FStruct) -> bool:
        RemoveHook("Engine.Interaction.Tick", f"LootRandomizer.{id(tick)}")
        for routine in routines:
            routine()
        return True
    RunHook("Engine.Interaction.Tick", f"LootRandomizer.{id(tick)}", tick)
