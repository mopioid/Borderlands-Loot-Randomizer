from unrealsdk import Log, FindObject #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct  #type: ignore

from Mods import ModMenu #type: ignore

# try:
#     from Mods import UserFeedback #type: ignore
#     from .seed import SeedConfigurator
# except:
#     SeedConfigurator = None
#     import webbrowser

from .defines import Tag
from . import defines, seed, hints

import os

from typing import Callable, Optional, Sequence, Set


_seeds_file = os.path.join(os.path.dirname(__file__), "Seeds.txt")


mod_instance: ModMenu.SDKMod


OwnedContent = Tag.BaseGame


SeedsList = ModMenu.Options.Spinner(
    Caption="Seed",
    Description="",
    StartingValue="",
    Choices=[""]
)


class CallbackField(ModMenu.Options.Field):
    Callback: Callable[[], None]

    def __init__(self, Caption: str, Description: str, Callback: Callable[[], None]) -> None:
        self.Caption = Caption
        self.Description = f"{Description}<!-- {__package__}.{id(self)} -->"
        self.IsHidden = False
        self.Callback = Callback

        _options_buttons.add(self)

_options_buttons: Set[CallbackField] = set()


class CallbackNested(ModMenu.Options.Nested):
    Callback: Callable[[], None]

    def __init__(
        self,
        Caption: str,
        Description: str,
        Callback: Callable[[], None],
        Children: Sequence[ModMenu.Options.Base]
    ) -> None:
        super().__init__(Caption, f"{Description}<!-- {__package__}.{id(self)} -->", Children)
        self.Callback = Callback
        _options_buttons.add(self)

_options_buttons: Set[CallbackField] = set()


NewSeedOptions = ModMenu.Options.Nested(
    Caption="New Seed",
    Description="Create a new seed. Each seed defines a shuffling of loot sources that is consistent each time you play the seed.",
    Children=()
)

SelectSeedOptions = CallbackNested(
    Caption="Select Seed",
    Description="Select a seed from your list of saved seeds. Each seed defines a shuffling of loot sources that is consistent each time you play the seed.",
    Callback=lambda: LoadSeeds(),
    Children=(
        SeedsList,
        CallbackField(
            Caption="APPLY SEED",
            Description="Confirm selection of the above seed, and apply it to your game.",
            Callback=lambda: ApplySeedClicked()
        )
    )
)

EditSeedFileButton = CallbackField(
    Caption="Edit Seeds",
    Description="Open your Seeds.txt file in a text editor so that you may add or remove seeds.",
    Callback=lambda: os.startfile(os.path.normpath(_seeds_file))
)


class CallbackSpinner(ModMenu.Options.Spinner):
    Callback: Callable[[str], None]
    _lootrando_current_value: str = "Vague"

    def __init__(
        self,
        Caption: str,
        Description: str,
        Callback: Callable[[str], None],
        StartingValue: Optional[str] = None,
        Choices: Optional[Sequence[str]] = None,
        *,
        IsHidden: bool = False,
    ):
        super().__init__(Caption, Description, StartingValue, Choices, IsHidden=IsHidden)
        self.Callback = Callback

    @property
    def CurrentValue(self) -> str:
        return self._lootrando_current_value
    
    @CurrentValue.setter
    def CurrentValue(self, value: str) -> None:
        if value != self._lootrando_current_value:
            self._lootrando_current_value = value
            self.Callback(value)


HintDisplay = CallbackSpinner(
    Caption="Hints",
    Description=(
        "How much information loot sources should reveal about their item drop. \"Vague\" will only"
        " describe rarity and type, while \"spoiler\" will name the exact item."
    ),
    Callback=lambda value: hints.UpdateHints(),
    Choices=("None", "Vague", "Spoiler"),
    StartingValue="Vague"
)

Options = (NewSeedOptions, SelectSeedOptions, EditSeedFileButton, HintDisplay)


class SeedHeader(ModMenu.Options.Field):
    def __init__(self, Caption: str) -> None:
        self.Caption = Caption; self.Description = ""; self.IsHidden = False

class SeedOption(ModMenu.Options.Spinner):
    tag: Tag
    def __init__(self, tag: Tag, Caption: str, Description: str) -> None:
        if (tag & defines.ContentTags) and not (tag & OwnedContent):
            StartingValue = "Off"
            Choices = ("Off")
        else:
            StartingValue = "On"
            Choices = ("Off", "On")
        
        super().__init__(Caption, Description, StartingValue, Choices)
        self.tag = tag


def Enable():
    global OwnedContent
    for tag in Tag:
        path = getattr(tag, "path", None)
        if path and FindObject("DownloadableItemSetDefinition", path).CanUse():
            OwnedContent |= tag

    LoadSeeds()
    selected_seed = seed.Seed.FromString(SeedsList.CurrentValue)
    seed.Apply(selected_seed)
    
    NewSeedOptions.Children = (
        SeedHeader("Content"),
        SeedOption(Tag.BaseGame,           "Base Game",            f"Include items and locations from Borderlands 2's base game."      ),
        SeedOption(Tag.PiratesBooty,       "Pirate's Booty",       f"Include items and locations from {Tag.PiratesBooty.title}."       ),
        SeedOption(Tag.CampaignOfCarnage,  "Campaign Of Carnage",  f"Include items and locations from {Tag.CampaignOfCarnage.title}."  ),
        SeedOption(Tag.HammerlocksHunt,    "Hammerlock's Hunt",    f"Include items and locations from {Tag.HammerlocksHunt.title}."    ),
        SeedOption(Tag.DragonKeep,         "Dragon Keep",          f"Include items and locations from {Tag.DragonKeep.title}."         ),
        SeedOption(Tag.FightForSanctuary,  "Fight For Sanctuary",  f"Include items and locations from {Tag.FightForSanctuary.title}."  ),
        SeedOption(Tag.BloodyHarvest,      "Bloody Harvest",       f"Include items and locations from {Tag.BloodyHarvest.title}."      ),
        SeedOption(Tag.WattleGobbler,      "Wattle Gobbler",       f"Include items and locations from {Tag.WattleGobbler.title}."      ),
        SeedOption(Tag.MercenaryDay,       "Mercenary Day",        f"Include items and locations from {Tag.MercenaryDay.title}."       ),
        SeedOption(Tag.WeddingDayMassacre, "Wedding Day Massacre", f"Include items and locations from {Tag.WeddingDayMassacre.title}." ),
        SeedOption(Tag.SonOfCrawmerax,     "Son Of Crawmerax",     f"Include items and locations from {Tag.SonOfCrawmerax.title}."     ),
        SeedOption(Tag.UVHMPack,           "UVHM Pack",            f"Include items and locations from {Tag.UVHMPack.title}."           ),
        SeedOption(Tag.DigistructPeak,     "Digistruct Peak",      f"Include items and locations from {Tag.DigistructPeak.title}."     ),

        # SeedHeader("Locations"),
        SeedHeader("Missions"),
        SeedOption(Tag.ShortMission,       "Short Missions",        "Include short side missions."),
        SeedOption(Tag.LongMission,        "Long Missions",         "Include longer side missions. Longer mission turn-ins provide bonus loot options."),
        SeedOption(Tag.VeryLongMission,    "Very Long Missions",    "Include very long side missions (including Headhunter missions). Very long mission turn-ins provide even more bonus loot options."),
        SeedOption(Tag.Slaughter,          "Slaughter Missions",    "Include slaughter missions."),
        # SeedOption(Tag.RaidMission,        "Raid Missions",         "Include missions for raid bosses and Digistruct Peak. Raid missions provide even more bonus loot options."),

        SeedHeader("Enemies"),
        SeedOption(Tag.UniqueEnemy,        "Unique Enemies",        "Include refarmable enemies."),
        SeedOption(Tag.SlowEnemy,          "Slow Enemies",          "Include enemies that take longer than usual for each kill. Slower enemies drop loot with greater frequency."),
        SeedOption(Tag.RareEnemy,          "Rare Enemies",          "Include enemies that are rare spawns. Rare enemies drop loot with greater frequency."),
        SeedOption(Tag.VeryRareEnemy,      "Very Rare Enemies",     "Include enemies that are very rare spawns. Very rare enemies drop loot with much greater frequency."),
        SeedOption(Tag.RaidEnemy,          "Raid Enemies",          "Include raid bosses. Raid bosses drop multiple loot instances guaranteed."),
        SeedOption(Tag.MissionEnemy,       "Mission Enemies",       "Include enemies that are only available while doing (or re-doing) a mission."),
        SeedOption(Tag.EvolvedEnemy,       "Evolved Enemies",       "Include enemies that are evolved forms of other enemies."),
        SeedOption(Tag.DigistructEnemy,    "Digistruct Enemies",    "Include the versions of unique enemies that are encountered in Digistruct Peak."),

        SeedHeader("Other"),
        SeedOption(Tag.Miscellaneous,      "Miscellaneous",         "Include miscellaneous loot locations (boxes that give unique items, etcetera)."),

        SeedHeader("Settings"),
        SeedOption(Tag.DuplicateItems,     "Duplicate Items",       "For seeds with more locations than items, random items can have multiple locations."),
        SeedOption(Tag.EnableHints,        "Allow Hints",           "Whether this seed should generate a spoiler log, and also whether hints should be allowed while playing it."),

        CallbackField("GENERATE SEED", "Confirm selections and and generate the new seed.", lambda: GenerateSeedClicked())
    )

    RunHook("WillowGame.WillowScrollingList.OnClikEvent", "LootRandomizer", _WillowScrollingListOnClikEvent)


def Disable():
    seed.Revert()

    RemoveHook("WillowGame.WillowScrollingList.OnClikEvent", "LootRandomizer")


def LoadSeeds() -> None:
    selected_seed = SeedsList.CurrentValue
    SeedsList.Choices = []

    with open(_seeds_file) as file:
        for line in file:
            try: old_seed = seed.Seed.FromString(line)
            except: continue
            SeedsList.Choices.append(old_seed.to_string())

    if not SeedsList.Choices:
        SeedsList.Choices.append("")
        SeedsList.CurrentValue = ""
    elif selected_seed in SeedsList.Choices:
        SeedsList.CurrentValue = selected_seed
    else:
        SeedsList.CurrentValue = SeedsList.Choices[0]


def GenerateSeedClicked() -> None:
    tags = Tag(0)

    for option in NewSeedOptions.Children:
        if isinstance(option, SeedOption) and option.CurrentValue == "On":
            tags |= option.tag

    new_seed = seed.Seed.Generate(tags)
    new_seed_string = new_seed.to_string()

    SeedsList.Choices.append(new_seed_string)
    SeedsList.CurrentValue = new_seed_string
    ModMenu.SaveModSettings(mod_instance)

    with open(_seeds_file, 'a+') as file:
        file.writelines(new_seed.to_string() + "\n")

    seed.Apply(new_seed)


def ApplySeedClicked() -> None:
    selected_seed = seed.Seed.FromString(SeedsList.CurrentValue)
    seed.Apply(selected_seed)


def _WillowScrollingListOnClikEvent(caller: UObject, function: UFunction, params: FStruct) -> bool:
    """
    Copied from ModMenu.OptionManager to detect clicking of menu items, modified to detect
    the description of our configurator "button."
    """
    if params.Data.Type != "itemClick":
        return True

    provider = None
    for obj in caller.DataProviderStack:
        provider = obj.DataProvider.ObjectPointer
    if provider is None or provider.GetDescription is None:
        return True

    event_id = caller.IndexToEventId[params.Data.Index]
    event_description = provider.GetDescription(event_id)

    for button in _options_buttons:
        if event_description == button.Description:
            button.Callback()

    return True


"""

- option for duplicate items versus dud items

"""
