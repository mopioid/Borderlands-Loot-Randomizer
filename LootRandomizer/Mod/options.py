from __future__ import annotations

from unrealsdk import Log, FindObject
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct

from Mods import ModMenu

from . import options, hints, seed
from .defines import *
from .seed import Seed

import os

from typing import Callable, Dict, List, Optional, Sequence, Set, Union
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import LootRandomizer


mod_instance: LootRandomizer


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
        open(seeds_file, "w")

    listed_seeds: List[str] = []
    with open(seeds_file) as file:
        for line in file:
            line = line.strip()
            if line == "":
                continue

            try:
                listed_seed = Seed.FromString(line)
            except ValueError as error:
                Log(error)
                continue

            if listed_seed.string not in listed_seeds:
                listed_seeds.append(listed_seed.string)

    return listed_seeds if listed_seeds else ("",)


def _PrepareSelectSeed() -> None:
    _SeedsList.Choices = _LoadSeeds()

    if _CurrentSeed.CurrentValue in _SeedsList.Choices:
        return

    if seed.AppliedSeed:
        seed.AppliedSeed.unapply()

    _SeedsList.CurrentValue = _SeedsList.Choices[0]


def _SeedApplied() -> None:
    if Tag.EnableHints in seed.AppliedTags:
        HintDisplay.Choices = ("None", "Vague", "Spoiler")
        HintDisplay.StartingValue = "Vague"
    else:
        HintDisplay.Choices = ("None",)
        HintDisplay.StartingValue = HintDisplay.Choices[0]
        HintDisplay.CurrentValue = HintDisplay.Choices[0]


def HideSeedOptions() -> None:
    _NewSeedOptions.IsHidden = True
    _SelectSeedOptions.IsHidden = True
    _EditSeedFileButton.IsHidden = True


def ShowSeedOptions() -> None:
    _NewSeedOptions.IsHidden = False
    _SelectSeedOptions.IsHidden = False
    _EditSeedFileButton.IsHidden = False


def SaveSeedString(seed_string: str) -> None:
    with open(seeds_file, "a+") as file:
        file.seek(0, 0)
        seeds = file.read()

        if len(seeds) > 0 and seeds[-1] not in "\n\r":
            file.write("\n")

        if seed_string not in seeds:
            file.write(seed_string + "\n")


def _NewSeedGenerateClicked() -> None:
    # TODO: not saving new seed selection to settings
    tags = Tag(0)

    for option in _NewSeedOptions.Children:
        if isinstance(option, SeedOption) and option.CurrentValue == "On":
            tags |= option.tag

    new_seed = Seed.Generate(tags)

    if not isinstance(_SeedsList.Choices, list):
        _SeedsList.Choices = []

    _CurrentSeed.CurrentValue = new_seed.string

    SaveSettings()

    show_dialog(
        "Seed Generated and Applied",
        "You will now see the seed's randomization in your game.\n\n"
        "You can review information about the seed in Loot Randomizer options.",
        1,
    )

    SaveSeedString(new_seed.string)

    new_seed.apply()
    _SeedApplied()


def _SelectSeedApplyClicked() -> None:
    seed = Seed.FromString(_SeedsList.LootRandomizer_staged)

    try:
        seed.apply()
    except Exception as error:
        show_dialog("Cannot Apply Seed", str(error), 1)
        return

    _CurrentSeed.CurrentValue = _SeedsList.LootRandomizer_staged

    SaveSettings()
    _SeedApplied()
    show_dialog(
        "Seed Applied",
        "You will now see the seed's randomization in your game.",
    )


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
            f"Hints and spoilers are disabled for seed {seed_string}.",
        )
        return

    def confirmed(seed: Seed = seed.AppliedSeed) -> None:
        seed.populate_hints()
        show_dialog(
            "Filled In Tracker Hints",
            f"The hints for seed {seed.string} have been filled in.",
        )

    show_confirmation(
        "Fill In Tracker Hints?",
        (
            "This will add a hint for every location to the tracker for seed "
            f"{seed_string}. This can only be undone by deleting the tracker "
            "file to create a new one."
        ),
        confirmed,
    )


def _PopulateSpoilersClicked() -> None:
    if not seed.AppliedSeed:
        return

    seed_string = seed.AppliedSeed.string

    if Tag.EnableHints not in seed.AppliedTags:
        show_dialog(
            "Cannot Populate Spoilers",
            f"Hints and spoilers are disabled for seed {seed_string}.",
        )
        return

    def confirmed(seed: Seed = seed.AppliedSeed) -> None:
        seed.populate_spoilers()
        show_dialog(
            "Filled In Tracker Spoilers",
            f"The spoilers for seed {seed.string} have been filled in.",
        )

    show_confirmation(
        "Fill In Tracker Spoilers?",
        (
            "This will add a spoiler for every location to the tracker for "
            f"seed {seed_string}. This can only be undone by deleting the "
            "tracker file to create a new one."
        ),
        confirmed,
    )


def _ResetDismissedClicked() -> None:
    show_dialog(
        "Dismissed Hints Reset", "All hints items will now appear again."
    )
    hints.ResetDismissed()


def _WillowScrollingListOnClikEvent(
    caller: UObject, _f: UFunction, params: FStruct
) -> bool:
    """
    Copied from ModMenu.OptionManager to detect clicking of menu items, modified
    to detect the descriptions of our "buttons."
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


def _PostLogin(caller: UObject, _f: UFunction, params: FStruct) -> bool:
    if params.NewPlayer == get_pc():
        return True

    if seed.AppliedSeed and not is_client():
        mod_instance.SendSeed(seed.AppliedSeed.string, PC=params.NewPlayer)

    return True


def _PostBeginPlay(caller: UObject, _f: UFunction, params: FStruct) -> bool:
    ShowSeedOptions()
    return True


_callback_options: Set[Union[CallbackField, CallbackNested]] = set()


class CallbackField(ModMenu.Options.Field):
    Callback: Callable[[], None]

    def __init__(
        self, Caption: str, Description: str, Callback: Callable[[], None]
    ) -> None:
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
        Children: Sequence[ModMenu.Options.Base],
    ) -> None:
        super().__init__(
            Caption,
            f"{Description}<!-- {__package__}.{id(self)} -->",
            Children,
        )
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
        super().__init__(
            Caption, Description, StartingValue, Choices, IsHidden=IsHidden
        )

    @property
    def CurrentValue(self) -> str:
        return self._LootRandomizer_value

    @CurrentValue.setter
    def CurrentValue(self, value: str) -> None:
        if value != self._LootRandomizer_value:
            self._LootRandomizer_value = value
            self.Callback(value)


class SeedListSpinner(ModMenu.Options.Spinner):
    LootRandomizer_staged: str

    def __init__(self):
        choices = _LoadSeeds()
        super().__init__(
            Caption="Seed",
            Description="",
            StartingValue=choices[0],
            Choices=choices,
        )
        self.LootRandomizer_staged = choices[0]

    @property
    def CurrentValue(self) -> str:
        if _CurrentSeed.CurrentValue in self.Choices:
            return _CurrentSeed.CurrentValue
        else:
            return _LoadSeeds()[0]

    @CurrentValue.setter
    def CurrentValue(self, value: str) -> None:
        self.LootRandomizer_staged = value


_SeedsList = SeedListSpinner()
_BL2Seed = ModMenu.Options.Hidden(
    Caption="BL2 Seed", Description="", StartingValue=""
)
_TPSSeed = ModMenu.Options.Hidden(
    Caption="TPS Seed", Description="", StartingValue=""
)
if BL2:
    _CurrentSeed = _BL2Seed
elif TPS:
    _CurrentSeed = _TPSSeed
else:
    raise

_NewSeedOptions = ModMenu.Options.Nested(
    Caption="New Seed",
    Description=(
        "Create a new seed. Each seed defines a shuffling of loot sources that "
        "is consistent each time you play it."
    ),
    Children=(),
)

_EditSeedFileButton = CallbackField(
    Caption="Edit Seeds",
    Description=(
        "Open your Seeds.txt file in a text editor so that you may add or "
        "remove seeds."
    ),
    Callback=lambda: os.startfile(seeds_file),
)

_SelectSeedOptions = CallbackNested(
    Caption="Select Seed",
    Description=(
        "Select a seed from your list of saved seeds. Each seed defines a "
        "shuffling of loot sources that is consistent each time you play it."
    ),
    Callback=_PrepareSelectSeed,
    Children=(
        _SeedsList,
        CallbackField(
            Caption="APPLY SEED",
            Description=(
                "Confirm selection of the above seed, and apply it to your "
                "game."
            ),
            Callback=_SelectSeedApplyClicked,
        ),
        _BL2Seed,
        _TPSSeed,
    ),
)

AutoLog = ModMenu.Options.Boolean(
    Caption="Automatically Track Drops",
    Description=(
        "When a location drops its hint or item, whether to automatically "
        "record that information in the seed's tracker."
    ),
    StartingValue=True,
)

HintDisplay = CallbackSpinner(
    Caption="Hint Display",
    Description=(
        "How much information loot sources should reveal about their item drop."
        ' "Vague" will only describe rarity and type, while "spoiler" will name'
        " the exact item."
    ),
    Callback=lambda value: hints.UpdateHints(),
    Choices=("None", "Vague", "Spoiler"),
    StartingValue="Vague",
)

HintTrainingSeen = ModMenu.Options.Hidden(
    Caption="Seen Hint Training", StartingValue=False
)
DudTrainingSeen = ModMenu.Options.Hidden(
    Caption="Seen Dud Training", StartingValue=False
)
RewardsTrainingSeen = ModMenu.Options.Hidden(
    Caption="Seen Rewards Training", StartingValue=False
)


Options: Sequence[ModMenu.Options.Base] = (
    _NewSeedOptions,
    _SelectSeedOptions,
    _EditSeedFileButton,
    CallbackField(
        Caption="Open Seed Tracker",
        Description=(
            "Open the text file listing every location and what has been found "
            "in the selected seed."
        ),
        Callback=_SeedTrackerClicked,
    ),
    ModMenu.Options.Nested(
        Caption="Configure Seed Tracker",
        Description="",
        Children=(
            AutoLog,
            CallbackField(
                Caption="FILL IN TRACKER HINTS",
                Description=(
                    "Add a hint for every location to the tracker for the "
                    "selected seed."
                ),
                Callback=_PopulateHintsClicked,
            ),
            CallbackField(
                Caption="FILL IN TRACKER SPOILERS",
                Description=(
                    "Add a spoiler for every location to the tracker for the "
                    "selected seed."
                ),
                Callback=_PopulateSpoilersClicked,
            ),
        ),
    ),
    HintDisplay,
    CallbackField(
        Caption="Reset Dismissed Hints",
        Description=(
            "Revert every dismissed hint so that they drop in game again."
        ),
        Callback=_ResetDismissedClicked,
    ),
    HintTrainingSeen,
    DudTrainingSeen,
    RewardsTrainingSeen,
)


class SeedHeader(ModMenu.Options.Field):
    def __init__(self, Caption: str) -> None:
        self.Caption = Caption
        self.Description = ""
        self.IsHidden = False


class SeedOption(ModMenu.Options.Spinner):
    tag: Tag

    def __init__(self, tag: Tag) -> None:
        if (tag & ContentTags) and not (tag & OwnedContent):
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
        if not tag in ContentTags:
            continue
        dlc_path: Optional[str] = getattr(tag, "dlc_path", None)
        if not dlc_path:
            OwnedContent |= tag
        else:
            dlc = FindObject("DownloadableItemSetDefinition", dlc_path)
            if not dlc:
                raise Exception(f"Missing DLC object for {tag.name}")
            if dlc_path and bool(dlc.CanUse()):
                OwnedContent |= tag

    if _CurrentSeed.CurrentValue not in _SeedsList.Choices:
        _CurrentSeed.CurrentValue = ""

    if _CurrentSeed.CurrentValue != "":
        selected_seed = Seed.FromString(_SeedsList.CurrentValue)
        try:
            selected_seed.apply()
            _SeedApplied()
        except ValueError as error:
            Log(error)

    categories: Dict[str, List[Tag]] = dict()
    for tag in TagList:
        if hasattr(tag, "category"):
            tag_list = categories.setdefault(tag.category, [])
            tag_list.append(tag)

    _NewSeedOptions.Children = []

    for category, tags in categories.items():
        _NewSeedOptions.Children.append(SeedHeader(category))
        for tag in tags:
            _NewSeedOptions.Children.append(SeedOption(tag))

    _NewSeedOptions.Children.append(
        CallbackField(
            "GENERATE SEED",
            "Confirm selections and and generate the new seed.",
            _NewSeedGenerateClicked,
        )
    )

    RunHook(
        "WillowGame.WillowScrollingList.OnClikEvent",
        "LootRandomizer",
        _WillowScrollingListOnClikEvent,
    )
    RunHook(
        "WillowGame.WillowGameInfo.PostLogin", "LootRandomizer", _PostLogin
    )
    RunHook(
        "WillowGame.WillowGameInfo.PostBeginPlay",
        "LootRandomizer",
        _PostBeginPlay,
    )


def Disable():
    if seed.AppliedSeed:
        seed.AppliedSeed.unapply()

    RemoveHook("WillowGame.WillowScrollingList.OnClikEvent", "LootRandomizer")
    RemoveHook("WillowGame.WillowGameInfo.PostLogin", "LootRandomizer")
    RemoveHook("WillowGame.WillowGameInfo.PostBeginPlay", "LootRandomizer")
