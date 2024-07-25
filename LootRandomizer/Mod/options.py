from __future__ import annotations

from unrealsdk import Log, FindObject, GetEngine #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct  #type: ignore

from Mods import ModMenu #type: ignore

from .defines import Tag, seeds_file, seeds_dir, show_dialog, show_confirmation
from .seed import Seed
from . import defines, hints, seed

import os

from typing import Callable, Dict, List, Optional, Sequence, Set


mod_instance: ModMenu.SDKMod

def SaveSettings() -> None:
    ModMenu.SaveModSettings(mod_instance)


OwnedContent = Tag.BaseGame


def _LoadSeeds() -> Sequence[str]:
    if not os.path.exists(seeds_dir):
        os.mkdir(seeds_dir)
    elif not os.path.isdir(seeds_dir):
        Log(f"Could not open seeds directory at {seeds_dir}")
        return ("",)

    if os.path.exists(seeds_file):
        if not os.path.isfile(seeds_file):
            Log(f"Could not open seeds file at {seeds_file}")
            return ("",)
    else:
        open(seeds_file, 'w')

    listed_seeds: List[str] = []
    with open(seeds_file) as file:
        for line in file:
            line = line.strip()
            if line == "":
                continue

            try: listed_seed = Seed.FromString(line)
            except ValueError as error:
                Log(error)
                continue

            if listed_seed.string not in listed_seeds:
                listed_seeds.append(listed_seed.string)

    return listed_seeds if listed_seeds else ("",)


def _ReloadSeeds() -> None:
    _SeedsList._LootRandomizer_auto_commit = False
    selected_seed = _SeedsList.CurrentValue

    _SeedsList.Choices = _LoadSeeds()

    if selected_seed in _SeedsList.Choices:
        return

    if seed.AppliedSeed:
        seed.AppliedSeed.unapply()

    _SeedsList.commit_CurrentValue(_SeedsList.Choices[0])


def _SeedApplied() -> None:
    if Tag.EnableHints in seed.AppliedTags:
        HintDisplay.Choices = ("None", "Vague", "Spoiler")
        HintDisplay.StartingValue = "Vague"

    else:
        HintDisplay.Choices = ("None",)
        HintDisplay.StartingValue = HintDisplay.Choices[0]
        HintDisplay.CurrentValue = HintDisplay.Choices[0]


def SaveSeedString(seed_string: str) -> None:
    with open(seeds_file, 'a+') as file:
        file.seek(0, 0)
        seeds = file.read()

        if len(seeds) > 0 and seeds[-1] not in "\n\r":
            file.write("\n")

        if seed_string not in seeds:
            file.write(seed_string + "\n")


def _NewSeedGenerateClicked() -> None:
    tags = Tag(0)

    for option in NewSeedOptions.Children:
        if isinstance(option, SeedOption) and option.CurrentValue == "On":
            tags |= option.tag

    new_seed = Seed.Generate(tags)

    if not isinstance(_SeedsList.Choices, list):
        _SeedsList.Choices = []

    _SeedsList.Choices.append(new_seed.string)
    _SeedsList.commit_CurrentValue(new_seed.string)
    SaveSettings()

    show_dialog(
        "Seed Generated and Applied",
        "You will now see the seed's randomization in your game.\n\n"
        "You can review information about the seed in Loot Randomizer options.",
        1
    )

    SaveSeedString(new_seed.string)

    new_seed.apply()
    _SeedApplied()


def _SelectSeedApplyClicked() -> None:
    seed = Seed.FromString(_SeedsList._LootRandomizer_staged)

    try: seed.apply()
    except Exception as error:
        show_dialog("Cannot Apply Seed", str(error), 1)
        return

    _SeedsList.commit_CurrentValue()
    SaveSettings()
    _SeedApplied()
    show_dialog("Seed Applied", "You will now see the seed's randomization in your game.")


def _SeedTrackerClicked() -> None:
    if not seed.AppliedSeed:
        return
    os.startfile(seed.AppliedSeed.generate_tracker())

def _PopulateHintsClicked() -> None:
    if not seed.AppliedSeed:
        return

    seed_string = seed.AppliedSeed.string

    if Tag.EnableHints not in seed.AppliedTags:
        show_dialog(
            "Cannot Populate Hints",
            f"Hints and spoilers are disabled for seed {seed_string}."
        )
        return

    def confirmed(seed = seed.AppliedSeed) -> None:
        seed.populate_hints()
        show_dialog(
            "Filled In Tracker Hints",
            f"The hints for seed {seed.string} have been filled in."
        )

    show_confirmation(
        "Fill In Tracker Hints?",
        (
            f"This will add a hint for every location to the tracker for seed {seed_string}. "
            "This can only be undone by deleting the tracker file to create a new one."
        ),
        confirmed
    )

def _PopulateSpoilersClicked() -> None:
    if not seed.AppliedSeed:
        return

    seed_string = seed.AppliedSeed.string

    if Tag.EnableHints not in seed.AppliedTags:
        show_dialog(
            "Cannot Populate Spoilers",
            f"Hints and spoilers are disabled for seed {seed_string}."
        )
        return

    def confirmed(seed = seed.AppliedSeed) -> None:
        seed.populate_spoilers()
        show_dialog(
            "Filled In Tracker Spoilers",
            f"The spoilers for seed {seed.string} have been filled in."
        )

    show_confirmation(
        "Fill In Tracker Spoilers?",
        (
            f"This will add a spoiler for every location to the tracker for seed {seed_string}. "
            "This can only be undone by deleting the tracker file to create a new one."
        ),
        confirmed
    )


def _ResetDismissedClicked() -> None:
    show_dialog("Dismissed Hints Reset", "All hints items will now appear again.")
    hints.ResetDismissed()


def _WillowScrollingListOnClikEvent(caller: UObject, function: UFunction, params: FStruct) -> bool:
    """
    Copied from ModMenu.OptionManager to detect clicking of menu items, modified to detect
    the descriptions of our "buttons."
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

    for button in _callback_options:
        if event_description == button.Description:
            button.Callback()

    return True


def _PostLogin(caller: UObject, function: UFunction, params: FStruct) -> bool:
    if params.NewPlayer == defines.get_pc():
        return True

    if seed.AppliedSeed and not defines.is_client():
        mod_instance.SendSeed(seed.AppliedSeed.string, PC = params.NewPlayer)

    return True


def _PostBeginPlay(caller: UObject, function: UFunction, params: FStruct) -> bool:
    NewSeedOptions.IsHidden = False
    SelectSeedOptions.IsHidden = False
    return True


_callback_options: Set[CallbackField] = set()


class CallbackField(ModMenu.Options.Field):
    Callback: Callable[[], None]

    def __init__(self, Caption: str, Description: str, Callback: Callable[[], None]) -> None:
        self.Caption = Caption
        self.Description = f"{Description}<!-- {__package__}.{id(self)} -->"
        self.IsHidden = False
        self.Callback = Callback

        _callback_options.add(self)


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
        _callback_options.add(self)


class CallbackSpinner(ModMenu.Options.Spinner):
    Callback: Callable[[str], None]
    _LootRandomizer_value: str

    def __init__(
        self,
        Caption: str,
        Description: str,
        Callback: Callable[[str], None],
        StartingValue: str,
        Choices: Sequence[str],
        *,
        IsHidden: bool = False,
    ):
        self.Callback = Callback
        self._LootRandomizer_value = StartingValue
        super().__init__(Caption, Description, StartingValue, Choices, IsHidden=IsHidden)

    @property
    def CurrentValue(self) -> str:
        return self._LootRandomizer_value
    
    @CurrentValue.setter
    def CurrentValue(self, value: str) -> None:
        if value != self._LootRandomizer_value:
            self._LootRandomizer_value = value
            self.Callback(value)


class SeedListSpinner(ModMenu.Options.Spinner):
    _LootRandomizer_value: str
    _LootRandomizer_staged: str
    _LootRandomizer_auto_commit: bool = True

    def __init__(
        self,
        Caption: str,
        Description: str,
        Choices: Sequence[str],
        *,
        IsHidden: bool = False,
    ):
        super().__init__(Caption, Description, Choices[0], Choices, IsHidden=IsHidden)
        self.StartingValue = ""
        self._LootRandomizer_value = ""
        self._LootRandomizer_staged = ""

    @property
    def CurrentValue(self) -> str:
        return self._LootRandomizer_value
    
    @CurrentValue.setter
    def CurrentValue(self, value: str) -> None:
        self._LootRandomizer_staged = value
        if self._LootRandomizer_auto_commit:
            self._LootRandomizer_value = value

    def commit_CurrentValue(self, value: Optional[str] = None) -> None:
        if value is None:
            self._LootRandomizer_value = self._LootRandomizer_staged
        else:
            self._LootRandomizer_staged = value
            self._LootRandomizer_value = value


_SeedsList = SeedListSpinner(
    Caption="Seed",
    Description="",
    Choices=_LoadSeeds()
)


NewSeedOptions = ModMenu.Options.Nested(
    Caption="New Seed",
    Description=(
        "Create a new seed. Each seed defines a shuffling of loot sources that is consistent each "
        "time you play the seed."
    ),
    Children=()
)

_EditSeedFileButton = CallbackField(
    Caption="Edit Seeds",
    Description="Open your Seeds.txt file in a text editor so that you may add or remove seeds.",
    Callback=lambda: os.startfile(seeds_file)
)

SelectSeedOptions = CallbackNested(
    Caption="Select Seed",
    Description=(
        "Select a seed from your list of saved seeds. Each seed defines a shuffling of loot "
        "sources that is consistent each time you play the seed."
    ),
    Callback=_ReloadSeeds,
    Children=(
        _SeedsList,

        CallbackField(
            Caption="APPLY SEED",
            Description="Confirm selection of the above seed, and apply it to your game.",
            Callback=_SelectSeedApplyClicked
        ),
    )
)

AutoLog = ModMenu.Options.Boolean(
    Caption="Automatically Track Drops",
    Description=(
        "When a location drops its hint or item, whether to automatically record that information "
        "in the seed's tracker."
    ),
    StartingValue=True
)

HintDisplay = CallbackSpinner(
    Caption="Hint Display",
    Description=(
        "How much information loot sources should reveal about their item drop. \"Vague\" will only"
        " describe rarity and type, while \"spoiler\" will name the exact item."
    ),
    Callback=lambda value: hints.UpdateHints(),
    Choices=("None", "Vague", "Spoiler"),
    StartingValue="Vague"
)

HintTrainingSeen = ModMenu.Options.Hidden(
    Caption="Seen Hint Training",
    StartingValue=False
)
DudTrainingSeen = ModMenu.Options.Hidden(
    Caption="Seen Dud Training",
    StartingValue=False
)
RewardsTrainingSeen = ModMenu.Options.Hidden(
    Caption="Seen Rewards Training",
    StartingValue=False
)


Options = (
    NewSeedOptions,
    _EditSeedFileButton,
    SelectSeedOptions,
    CallbackField(
        Caption="Open Seed Tracker",
        Description=(
            "Open the text file listing every location and what has been found in the selected "
            "seed."
        ),
        Callback=_SeedTrackerClicked
    ),
    ModMenu.Options.Nested(
        Caption="Configure Seed Tracker",
        Description="",
        Children=(
            AutoLog,
            CallbackField(
                Caption="FILL IN TRACKER HINTS",
                Description="Add a hint for every location to the tracker for the selected seed.",
                Callback=_PopulateHintsClicked
            ),
            CallbackField(
                Caption="FILL IN TRACKER SPOILERS",
                Description="Add a spoiler for every location to the tracker for the selected seed.",
                Callback=_PopulateSpoilersClicked
            ),
        )
    ),
    HintDisplay,
    CallbackField(
        Caption="Reset Dismissed Hints",
        Description="Revert every dismissed hint so that they drop in game again.",
        Callback=_ResetDismissedClicked
    ),

    HintTrainingSeen,
    DudTrainingSeen,
    RewardsTrainingSeen,
)


class SeedHeader(ModMenu.Options.Field):
    def __init__(self, Caption: str) -> None:
        self.Caption = Caption; self.Description = ""; self.IsHidden = False

class SeedOption(ModMenu.Options.Spinner):
    tag: Tag
    def __init__(self, tag: Tag) -> None:
        if (tag & defines.ContentTags) and not (tag & OwnedContent):
            StartingValue = "Off"
            Choices: Sequence[str] = ("Off",)
        else:
            Choices = ("Off", "On")
            StartingValue = "On" if tag.default else "Off"
        
        super().__init__(tag.caption, tag.description, StartingValue, Choices)
        self.tag = tag


def Enable():
    global OwnedContent
    for tag in Tag:
        dlc_path = getattr(tag, "dlc_path", None)
        if dlc_path and FindObject("DownloadableItemSetDefinition", tag.dlc_path).CanUse():
            OwnedContent |= tag

    if _SeedsList.CurrentValue != "":
        selected_seed = Seed.FromString(_SeedsList.CurrentValue)
        try:
            selected_seed.apply()
            _SeedApplied()
        except ValueError as error:
            Log(error)
    
    categories: Dict[str, List[Tag]] = dict() #type: ignore
    for tag in defines.TagList:
        if hasattr(tag, "category"):
            tag_list = categories.setdefault(tag.category, [])
            tag_list.append(tag)

    NewSeedOptions.Children = []

    for category, tags in categories.items():
        NewSeedOptions.Children.append(SeedHeader(category))
        for tag in tags:
            NewSeedOptions.Children.append(SeedOption(tag))

    NewSeedOptions.Children.append(
        CallbackField("GENERATE SEED", "Confirm selections and and generate the new seed.", _NewSeedGenerateClicked)
    )

    RunHook("WillowGame.WillowScrollingList.OnClikEvent", "LootRandomizer", _WillowScrollingListOnClikEvent)
    RunHook("WillowGame.WillowGameInfo.PostLogin", "LootRandomizer", _PostLogin)
    RunHook("WillowGame.WillowGameInfo.PostBeginPlay", "LootRandomizer", _PostBeginPlay)


def Disable():
    if seed.AppliedSeed:
        seed.AppliedSeed.unapply()

    RemoveHook("WillowGame.WillowScrollingList.OnClikEvent", "LootRandomizer")
    RemoveHook("WillowGame.WillowGameInfo.PostLogin", "LootRandomizer")
    RemoveHook("WillowGame.WillowGameInfo.PostBeginPlay", "LootRandomizer")
