from unrealsdk import Log, ConstructObject, FindObject, GetEngine, KeepAlive, UPackage #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct #type: ignore

import enum, os

from typing import Any, Callable, Generator, Iterator, List, Optional, Tuple, Union


Probability = Tuple[float, UObject, UObject, float]
BalancedItem = Tuple[UObject, UObject, Probability, bool]


Package: UPackage = ConstructObject("Package", None, "LootRandomizer")
KeepAlive(Package)


seeds_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Seeds")
seeds_file = os.path.join(seeds_dir, "Seed List.txt")


class Category(str, enum.Enum):
    Content = "Content"
    Missions = "Missions"
    Enemies = "Enemies"
    Other = "Other"
    Settings = "Settings"


class Tag(enum.IntFlag):
    category: Category
    default: bool
    caption: str
    description: str

    content_title: Optional[str]
    dlc_path: Optional[str]

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

    Vendor             = enum.auto()
    Miscellaneous      = enum.auto()

    DuplicateItems     = enum.auto()
    EnableHints        = enum.auto()


ContentTags = Tag(0)
MissionTags = Tag(0)
EnemyTags   = Tag(0)
OtherTags   = Tag(0)

for tag, content_title, dlc_path in (
    ( Tag.BaseGame,           "Borderlands 2",                              None                                                  ),
    ( Tag.PiratesBooty,       "Captain Scarlett and her Pirate's Booty",    "GD_OrchidPackageDef.ItemSetDef_Orchid"               ),
    ( Tag.CampaignOfCarnage,  "Mr. Torgue's Campaign of Carnage",           "GD_IrisPackageDef.ItemSetDef_Iris"                   ),
    ( Tag.HammerlocksHunt,    "Sir Hammerlock's Big Game Hunt",             "GD_SagePackageDef.ItemSetDef_Sage"                   ),
    ( Tag.DragonKeep,         "Tiny Tina's Assault on Dragon Keep",         "GD_AsterPackageDef.ItemSetDef_Aster"                 ),
    ( Tag.FightForSanctuary,  "Commander Lilith & the Fight for Sanctuary", "GD_AnemonePackageDef.ItemSetDef_Anemone"             ),
    ( Tag.BloodyHarvest,      "Headhunter 1: Bloody Harvest",               "GD_FlaxPackageDef.ItemSetDef_Flax"                   ),
    ( Tag.WattleGobbler,      "Headhunter 2: Wattle Gobbler",               "GD_AlliumPackageDef.ItemSetDef_Allium_TG"            ),
    ( Tag.MercenaryDay,       "Headhunter 3: Mercenary Day",                "GD_AlliumPackageDef.ItemSetDef_Allium_Xmas"          ),
    ( Tag.WeddingDayMassacre, "Headhunter 4: Wedding Day Massacre",         "GD_NasturtiumPackageDef.ItemSetDef_NasturtiumVday"   ),
    ( Tag.SonOfCrawmerax,     "Headhunter 5: Son of Crawmerax",             "GD_NasturtiumPackageDef.ItemSetDef_NasturtiumEaster" ),
    ( Tag.UVHMPack,           "Ultimate Vault Hunter Upgrade Pack",         "GD_GladiolusPackageDef.ItemSetDef_Gladiolus"         ),
    ( Tag.DigistructPeak,     "Ultimate Vault Hunter Upgrade Pack 2",       "GD_LobeliaPackageDef.CustomItemSetDef_Lobelia"       ),
):
    tag.content_title = content_title; tag.dlc_path = dlc_path

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
    (Tag.UVHMPack,           Category.Content,  True,  "UVHM Pack",            f"Include items and from {Tag.UVHMPack.content_title}."),
    (Tag.DigistructPeak,     Category.Content,  True,  "Digistruct Peak",      f"Include items and locations from {Tag.DigistructPeak.content_title}."),

    (Tag.ShortMission,       Category.Missions, True,  "Short Missions",       "Assign items to short side missions."),
    (Tag.LongMission,        Category.Missions, True,  "Long Missions",        "Assign items to longer side missions. Longer mission turn-ins provide bonus loot options."),
    (Tag.VeryLongMission,    Category.Missions, False, "Very Long Missions",   "Assign items to very long side missions (including Headhunter missions). Very long mission turn-ins provide even more bonus loot options."),
    (Tag.Slaughter,          Category.Missions, False, "Slaughter Missions",   "Assign items to slaughter missions."),

    (Tag.UniqueEnemy,        Category.Enemies,  True,  "Unique Enemies",       "Assign items to refarmable enemies."),
    (Tag.SlowEnemy,          Category.Enemies,  True,  "Slow Enemies",         "Assign items to enemies which take longer than usual each kill. Slower enemies drop loot with greater frequency."),
    (Tag.RareEnemy,          Category.Enemies,  True,  "Rare Enemies",         "Assign items to enemies that are rare spawns. Rare enemies drop loot with greater frequency."),
    (Tag.VeryRareEnemy,      Category.Enemies,  False, "Very Rare Enemies",    "Assign items to enemies that are very rare spawns. Very rare enemies drop loot with much greater frequency."),
    (Tag.MobFarm,            Category.Enemies,  False, "Mob Farms",            "Assign items to mobs which have rare drops in the vanilla game. Mob farm enemies drop loot rarely (but not too rarely)."),
    (Tag.RaidEnemy,          Category.Enemies,  False, "Raid Enemies",         "Assign items to raid bosses. Raid bosses drop multiple loot instances guaranteed."),
    (Tag.MissionEnemy,       Category.Enemies,  False, "Mission Enemies",      "Assign items to enemies that are only available while doing (or re-doing) a mission."),
    (Tag.EvolvedEnemy,       Category.Enemies,  False, "Evolved Enemies",      "Assign items to enemies that are evolved forms of other enemies."),
    (Tag.DigistructEnemy,    Category.Enemies,  False, "Digistruct Enemies",   "Assign items to the versions of unique enemies that are encountered in Digistruct Peak."),

    (Tag.Vendor,             Category.Other,    False, "Special Vendors",      "Assign items to unique vendors to be purchasable with Seraph Crystals or Torgue Tokens."),
    (Tag.Miscellaneous,      Category.Other,    True,  "Miscellaneous",        "Assign items to miscellaneous loot locations (boxes that give unique items, etcetera)."),

    (Tag.DuplicateItems,     Category.Settings, False, "Duplicate Items",      "For seeds with more locations than items, random items can have multiple locations."),
    (Tag.EnableHints,        Category.Settings, True,  "Allow Hints",          "Whether this seed should generate a spoiler log, and also whether hints should be allowed while playing it."),
):
    tag.category = category; tag.default = default; tag.caption = caption; tag.description = description
    if not hasattr(tag, "content_title"): tag.content_title = None
    if not hasattr(tag, "dlc_path"):      tag.dlc_path      = None

    if category == Category.Content:  ContentTags |= tag
    if category == Category.Missions: MissionTags |= tag
    if category == Category.Enemies:  EnemyTags   |= tag
    if category == Category.Other:    OtherTags   |= tag


def get_pc() -> UObject:
    return GetEngine().GamePlayers[0].Actor


def set_command(uobject: UObject, attribute: str, value: str):
    get_pc().ConsoleCommand(f"set {UObject.PathName(uobject)} {attribute} {value}")


def convert_struct(fstruct: Any) -> Any:
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
    def hook(caller: UObject, function: UFunction, params: FStruct) -> bool:
        RemoveHook("Engine.Interaction.Tick", f"LootRandomizer.{id(routines)}")
        for routine in routines:
            routine()
        return True
    RunHook("Engine.Interaction.Tick", f"LootRandomizer.{id(routines)}", hook)


def spawn_item(pool: UObject, context: UObject, callback: Callable[[UObject], None]) -> None:
    spawner = ConstructObject("Behavior_SpawnLootAroundPoint")
    spawner.ItemPools = (pool,)
    spawner.SpawnVelocityRelativeTo = 1
    spawner.CustomLocation = ((float('inf'), float('inf'), float('inf')), None, "")

    def hook(caller: UObject, function: UFunction, params: FStruct) -> bool:
        if caller is spawner:
            if len(params.SpawnedLoot):
                callback(params.SpawnedLoot[0].Inv)
            RemoveHook("WillowGame.Behavior_SpawnLootAroundPoint.PlaceSpawnedItems", f"LootRandomizer.{id(spawner)}")
        return True
    RunHook("WillowGame.Behavior_SpawnLootAroundPoint.PlaceSpawnedItems", f"LootRandomizer.{id(spawner)}", hook)

    spawner.ApplyBehaviorToContext(context, (), None, None, None, ())


def get_pawns() -> Generator[UObject, None, None]:
    pawn = GetEngine().GetCurrentWorldInfo().PawnList
    while pawn:
        yield pawn
        pawn = pawn.NextPawn


def construct_behaviorsequence_behavior(
    *path_components: str,
    sequence: str,
    enables: bool = True,
    outer: UObject,
):
    path_components = ("",) * (6 - len(path_components)) + path_components

    pathname_value = "(" + "".join(
        f"PathComponentNames[{index}]={path_component},"
        for index, path_component in enumerate(path_components)
    ) + "IsSubobjectMask=16)"

    behavior = construct_object("Behavior_ChangeRemoteBehaviorSequenceState", outer)
    behavior.Action = 1 if enables else 2
    set_command(behavior, "SequenceName", sequence)
    set_command(behavior, "ProviderDefinitionPathName", pathname_value)
    return behavior


def show_dialog(title: str, message: str, duration: float = 0) -> None:
    get_pc().GFxUIManager.ShowTrainingDialog(message, title, duration, 0, False)
