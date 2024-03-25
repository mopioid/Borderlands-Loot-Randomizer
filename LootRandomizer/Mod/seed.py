from __future__ import annotations

from unrealsdk import Log #type: ignore

from . import defines, options, items, hints, enemies, missions, catalog
from .defines import Tag, seeds_dir
from .locations import Location
from .items import ItemPool

from base64 import b32encode, b32decode
import random, os, importlib

from typing import Callable, List, Optional, Sequence, Set
from types import ModuleType


CurrentVersion = 3
SupportedVersions = (1,2,3)


AppliedSeed: Optional[Seed] = None
AppliedTags: Tag = Tag(0)


class SeedEntry:
    __slots__ = ("name", "tags")

    name: str
    tags: Tag

    def __init__(self, name: str, tags: Tag) -> None:
        self.name = name; self.tags = tags

    def match_item(self) -> ItemPool:
        for item in catalog.Items:
            if item.name == self.name:
                return item
        raise ValueError(f"Could not locate item for seed entry '{self.name}'")

    def match_location(self) -> Location:
        for location in catalog.Locations:
            if str(location) == self.name:
                return location
        raise ValueError(f"Could not locate location for seed entry '{self.name}'")


def _stringify(data: bytes) -> str:
    string = b32encode(data).decode("ascii").strip("=").lower()
    return f"{string[0:5]}-{string[5:10]}-{string[10:15]}"


class Seed:
    data: bytes
    string: str

    version: int
    tags: Tag

    version_module: ModuleType

    locations: Sequence[Location]
    items: Sequence[ItemPool]
    item_count: int

    def __init__(self, data: bytes, version: int, tags: Tag, string: str) -> None:
        self.data = data; self.version = version; self.tags = tags; self.string = string

    @classmethod
    def Generate(cls, tags: Tag, version: int = CurrentVersion) -> Seed:
        value = random.getrandbits(30) << 42
        value |= tags.value << 6
        value |= version

        data = value.to_bytes(length=9, byteorder='big')

        return cls(data, version, tags, _stringify(data))

    @classmethod
    def FromString(cls, string: str) -> Seed:
        try:
            data = b32decode("".join(char.upper() for char in string if char.isalnum()) + "=")
            assert(len(data) == 9)
        except:
            raise ValueError("Failed to read seed with invalid format: " + string)

        value = int.from_bytes(bytes=data, byteorder='big')
        version = (2 ** 6 - 1) & value
        tags = (2 ** 36 - 1) & (value >> 6)

        return cls(data, version, Tag(tags), _stringify(data))


    def apply(self) -> None:
        global AppliedSeed, AppliedTags

        if self.version not in SupportedVersions:
            raise ValueError(
                f"Seed {self.string} is the incorrect version for this release of Loot Randomizer. "
                "If you would like to play it, please install a version of Loot Randomizer that "
                f"specifies a seed version of {self.version}."
            )
        
        missing_dlcs = ""
        for tag in Tag:
            content_title = getattr(tag, "content_title", None)
            if content_title and (tag & self.tags) and not (tag & options.OwnedContent):
                missing_dlcs += "\n &#x2022; " + content_title

        if missing_dlcs != "":
            raise ValueError(f"Seed {self.string} requires additional DLCs to play:{missing_dlcs}")

        if AppliedSeed:
            AppliedSeed.unapply()

        AppliedSeed = self
        AppliedTags = self.tags

        self.version_module = importlib.import_module(f".seedversions.v{self.version}", __package__)
        version_items: Sequence[SeedEntry] = self.version_module.Items
        version_locations: Sequence[SeedEntry] = self.version_module.Locations

        self.items = [entry.match_item() for entry in version_items if entry.tags & self.tags]
        self.locations = tuple(entry.match_location() for entry in version_locations if entry.tags in self.tags)

        for item in self.items:
            item.apply(self.tags)

        location_count = len(self.locations)
        item_count = self.item_count = len(self.items)

        randomizer = random.Random(self.data)

        if location_count < item_count:
            self.items = randomizer.sample(self.items, location_count)

        elif location_count == item_count:
            randomizer.shuffle(self.items)

        elif self.tags & Tag.DuplicateItems:
            self.items *= (location_count // item_count)
            self.items += randomizer.sample(self.items, location_count % item_count)
            randomizer.shuffle(self.items)

        else:
            self.items += [items.DudItem] * (location_count - item_count)
            randomizer.shuffle(self.items)

        for location, item in zip(self.locations, self.items):
            location.item = item

        for location in self.locations:
            location.update_hint()
            location.toggle_hint(True)

        self.generate_tracker()


    def unapply(self) -> None:
        global AppliedSeed, AppliedTags
        AppliedSeed = None
        AppliedTags = Tag(0)

        for location in self.locations:
            location.item = None


    def generate_tracker(self) -> str:
        path = os.path.join(seeds_dir, f"{self.string}.txt")
        if os.path.exists(path):
            return path

        with open(path, 'w') as file:
            item_warning = " (not all accessible)" if self.item_count > len(self.locations) else ""

            file.write(
                f"Loot Randomizer Seed {self.string}\n\n"
                f"Total locations: {len(self.locations)}\n"
                f"Total items: {self.item_count}{item_warning}\n\n"
            )
            for tag in Tag:
                caption = getattr(tag, "caption", None)
                if caption:
                    file.write(f"{tag.caption}: {'On' if (tag in self.tags) else 'Off'}\n")

            for tag in Tag:
                if not tag & defines.ContentTags & self.tags:
                    continue

                locations = tuple(location for location in self.locations if tag in location.tags)
                if not len(locations):
                    continue

                file.write(f"\n{tag.content_title}\n")

                for location in locations:
                    file.write(f"{location}\n")
        
        return path


    def update_tracker(self, location: Location, drop: bool) -> None:
        if not (location.item and options.AutoLog.CurrentValue):
            return
        
        if options.HintDisplay.CurrentValue == 'None' and not drop:
            return

        location_name = str(location)
        
        path = self.generate_tracker()

        with open(path, 'r') as file:
            lines = file.readlines()

        for index in range(len(lines)):
            if not lines[index].startswith(location_name):
                continue

            line = lines[index].strip()
            item_name = location.item.name

            if line.endswith(item_name):
                return

            if drop or options.HintDisplay.CurrentValue == 'Spoiler':
                lines[index] = f"{location_name} - {item_name}\n"
                break
            
            hint_name = location.item.vague_hint.value
            if line[len(location_name):].endswith(hint_name):
                return
            
            lines[index] = f"{location_name} - {hint_name}\n"
            break

        with open(path, 'w') as file:
            file.writelines(lines)


    def populate_tracker(self, formatter: Callable[[ItemPool], str]) -> None:
        path = self.generate_tracker()

        with open(path, 'r') as file:
            log = file.readlines()

        for location, item in zip(self.locations, self.items):
            location_name = str(location)
            for index in range(len(log)):
                if log[index].startswith(location_name):
                    if not log[index].strip().endswith(item.name):
                        log[index] = f"{location_name} - {formatter(item)}\n"

        with open(path, 'w') as file:
            file.writelines(log)


    def populate_hints(self) -> None:
        self.populate_tracker(lambda item: item.vague_hint.value)

    def populate_spoilers(self) -> None:
        self.populate_tracker(lambda item: item.name)


def generate_wikis(version: int) -> None:
    from html import escape

    dummy_seed = Seed.Generate(defines.AllTags)
    dummy_seed.apply()
    version_items: Sequence[SeedEntry] = dummy_seed.version_module.Items
    version_locations: Sequence[SeedEntry] = dummy_seed.version_module.Locations

    with open(os.path.join(seeds_dir, "locations wiki.txt"), 'w', encoding='utf-8') as file:
        for content_tag in Tag:
            content_title = getattr(content_tag, "content_title", None)
            if not content_title:
                continue

            locations = tuple(
                location.match_location() for location in version_locations if content_tag & location.tags
            )
            if not locations:
                continue

            file.write(f"\n### {escape(content_title)}\n")
            file.write("\n| **Type** | **Location** | **Rolls** | **Required Settings** |\n| - | - | - | - |\n")

            for location in locations:
                rolls: List[str] = []
                for rarity in reversed(sorted(location._rarities)):
                    rolls.append(f"<kbd>{rarity}%</kbd>")

                if len(rolls) <= 4:
                    rolls_string = ' '.join(rolls)
                else:
                    rolls_string = f"{' '.join(rolls[:4])}<br />{' '.join(rolls[4:])}"

                settings: List[str] = []
                for tag in Tag:
                    caption = getattr(tag, "caption", None)
                    if caption == None:
                        continue
                    if (tag not in defines.ContentTags) and (tag in location.tags):
                        settings.append(f"<kbd>{escape(tag.caption)}</kbd>")

                if len(settings) <= 2:
                    settings_string = ' '.join(settings)
                else:
                    settings_string = f"{' '.join(settings[:2])}<br />{' '.join(settings[2:])}"

                if isinstance(location, enemies.Enemy): category = "Enemy"
                elif isinstance(location, missions.Mission): category = "Mission"
                else: category = "Other"

                file.write(f"| {category} | {escape(location.name)} | {rolls_string} | {settings_string} |\n")
                

    with open(os.path.join(seeds_dir, "items wiki.txt"), 'w', encoding='utf-8') as file:
        for hint in hints.Hint:
            if hint is hints.Hint.Dud:
                continue

            file.write(f"\n### {escape(hint)}s\n")
            file.write("\n| **Item** | **Required Content** |\n| - | - |\n")

            for item_entry in version_items:
                item = item_entry.match_item()
                if item.vague_hint is not hint:
                    continue

                content: List[str] = []

                for tag in Tag:
                    if tag & defines.ContentTags:
                        if tag & item.tags:
                            content.append(f"<kbd>{escape(tag.caption)}</kbd>")

                file.write(f"| {escape(item.name)} | {' or '.join(content)} |\n")


def generate_seedversion() -> None:
    with open(os.path.join(defines.mod_dir, "Mod", "seedversions", f"v{CurrentVersion}.py"), 'w', encoding='utf-8') as file:
        file.write(
            "from ..seed import SeedEntry\n"
            "from ..defines import Tag\n"
            "\n\n"
            "Items = (\n"
        )

        for item in catalog.Items:
            tag_string = "|".join(f"Tag.{tag.name}" for tag in Tag if (tag & item.tags))
            file.write(f"    SeedEntry(\"{item.name}\", {tag_string}),\n")

        file.write(f")\n\n\n")
        file.write(f"Locations = (\n")

        for location in catalog.Locations:
            tag_string = "|".join(f"Tag.{tag.name}" for tag in Tag if tag in location.tags)
            file.write(f"    SeedEntry(\"{location}\", {tag_string}),\n")

        file.write(f")\n")
