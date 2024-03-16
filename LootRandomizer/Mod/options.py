from __future__ import annotations

from unrealsdk import Log, FindObject, GetEngine #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct  #type: ignore

from Mods import ModMenu #type: ignore

from .defines import Tag, seeds_file, seeds_dir, show_dialog
from .seed import Seed
from . import defines, hints, seed

import os

from typing import Callable, Dict, List, Optional, Sequence, Set


mod_instance: ModMenu.SDKMod


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

    if seed.SelectedSeed:
        seed.SelectedSeed.revert()

    _SeedsList.commit_CurrentValue(_SeedsList.Choices[0])


def _SeedApplied() -> None:
    if Tag.EnableHints in seed.SelectedSeed.tags:
        _HintDisplay.Choices = ("None", "Vague", "Spoiler")
        _HintDisplay.StartingValue = _HintDisplay.Choices[1]
        _HintDisplay.CurrentValue = _HintDisplay.Choices[1]
    else:
        _HintDisplay.Choices = ("None",)
        _HintDisplay.StartingValue = _HintDisplay.Choices[0]
        _HintDisplay.CurrentValue = _HintDisplay.Choices[0]


def _NewSeedGenerateClicked() -> None:
    tags = Tag(0)

    for option in _NewSeedOptions.Children:
        if isinstance(option, SeedOption) and option.CurrentValue == "On":
            tags |= option.tag

    new_seed = Seed.Generate(tags)

    if not isinstance(_SeedsList.Choices, list):
        _SeedsList.Choices = []

    _SeedsList.Choices.append(new_seed.string)
    _SeedsList.commit_CurrentValue(new_seed.string)
    ModMenu.SaveModSettings(mod_instance)

    show_dialog(
        "Seed Generated and Applied",
        "You will now see the seed's randomization in your game.\n\n"
        "You can review information about the seed in the Select Seed section of the Mods menu in Options.",
        1
    )

    with open(seeds_file, 'a+') as file:
        file.write(new_seed.string + "\n")

    new_seed.apply()
    _SeedApplied()


def _SelectSeedApplyClicked() -> None:
    seed = Seed.FromString(_SeedsList._LootRandomizer_staged)

    try: seed.apply()
    except Exception as error:
        show_dialog("Cannot Apply Seed", str(error), 1)
        return

    _SeedsList.commit_CurrentValue()
    ModMenu.SaveModSettings(mod_instance)
    _SeedApplied()
    show_dialog("Seed Applied", "You will now see the seed's randomization in your game.")


def _SelectSeedGuideClicked() -> None:
    seed = Seed.FromString(_SeedsList._LootRandomizer_staged)
    os.startfile(seed.generate_guide())

def _SelectSeedHintsClicked() -> None:
    seed = Seed.FromString(_SeedsList._LootRandomizer_staged)
    if Tag.EnableHints in seed.tags:
        os.startfile(seed.generate_hints())
    else:
        show_dialog("Cannot Open Hints", f"Hints and spoilers are disabled for seed {seed.string}.")

def _SelectSeedSpoilersClicked() -> None:
    seed = Seed.FromString(_SeedsList._LootRandomizer_staged)
    if Tag.EnableHints in seed.tags:
        os.startfile(seed.generate_spoilers())
    else:
        show_dialog("Cannot Open Spoilers", f"Hints and spoilers are disabled for seed {seed.string}.")


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
        StartingValue: Optional[str] = None,
        Choices: Optional[Sequence[str]] = None,
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
        Choices: Optional[Sequence[str]] = None,
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


_NewSeedOptions = ModMenu.Options.Nested(
    Caption="New Seed",
    Description="Create a new seed. Each seed defines a shuffling of loot sources that is consistent each time you play the seed.",
    Children=()
)

_SelectSeedOptions = CallbackNested(
    Caption="Select Seed",
    Description="Select a seed from your list of saved seeds. Each seed defines a shuffling of loot sources that is consistent each time you play the seed.",
    Callback=_ReloadSeeds,
    Children=(
        _SeedsList,

        CallbackField(
            Caption="APPLY SEED",
            Description="Confirm selection of the above seed, and apply it to your game.",
            Callback=_SelectSeedApplyClicked
        ),
        CallbackField(
            Caption="OPEN SEED LOCATIONS",
            Description="Open the text file listing every location that can be checked for items in this seed.",
            Callback=_SelectSeedGuideClicked
        ),
        CallbackField(
            Caption="OPEN SEED HINTS",
            Description="Open the text file listing item hints for every location in this seed.",
            Callback=_SelectSeedHintsClicked
        ),
        CallbackField(
            Caption="OPEN SEED SPOILERS",
            Description="Open the text file listing the exact item at every location in this seed.",
            Callback=_SelectSeedSpoilersClicked
        ),
    )
)

_EditSeedFileButton = CallbackField(
    Caption="Edit Seeds",
    Description="Open your Seeds.txt file in a text editor so that you may add or remove seeds.",
    Callback=lambda: os.startfile(seeds_file)
)

_HintDisplay = CallbackSpinner(
    Caption="Hints",
    Description=(
        "How much information loot sources should reveal about their item drop. \"Vague\" will only"
        " describe rarity and type, while \"spoiler\" will name the exact item."
    ),
    Callback=lambda value: hints.UpdateHints(_HintDisplay.CurrentValue),
    Choices=("None", "Vague", "Spoiler"),
    StartingValue="Vague"
)

Options = (_NewSeedOptions, _SelectSeedOptions, _EditSeedFileButton, _HintDisplay)


class SeedHeader(ModMenu.Options.Field):
    def __init__(self, Caption: str) -> None:
        self.Caption = Caption; self.Description = ""; self.IsHidden = False

class SeedOption(ModMenu.Options.Spinner):
    tag: Tag
    def __init__(self, tag: Tag) -> None:
        if (tag & defines.ContentTags) and not (tag & OwnedContent):
            StartingValue = "Off"
            Choices = ("Off",)
        else:
            Choices = ("Off", "On")
            StartingValue = "On" if tag.default else "Off"
        
        super().__init__(tag.caption, tag.description, StartingValue, Choices)
        self.tag = tag


def Enable():
    global OwnedContent
    for tag in Tag:
        if tag.dlc_path and FindObject("DownloadableItemSetDefinition", tag.dlc_path).CanUse():
            OwnedContent |= tag

    if _SeedsList.CurrentValue != "":
        selected_seed = Seed.FromString(_SeedsList.CurrentValue)
        try:
            selected_seed.apply()
            _SeedApplied()
        except Exception as error:
            Log(error)
    
    categories: Dict[str, List[Tag]] = dict()
    for tag in Tag:
        tag_list = categories.setdefault(tag.category, [])
        tag_list.append(tag)

    _NewSeedOptions.Children = []

    for category, tags in categories.items():
        _NewSeedOptions.Children.append(SeedHeader(category))
        for tag in tags:
            _NewSeedOptions.Children.append(SeedOption(tag))

    _NewSeedOptions.Children.append(
        CallbackField("GENERATE SEED", "Confirm selections and and generate the new seed.", _NewSeedGenerateClicked)
    )

    RunHook("WillowGame.WillowScrollingList.OnClikEvent", "LootRandomizer", _WillowScrollingListOnClikEvent)


def Disable():
    RemoveHook("WillowGame.WillowScrollingList.OnClikEvent", "LootRandomizer")
