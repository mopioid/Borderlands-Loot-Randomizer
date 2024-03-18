from __future__ import annotations

from unrealsdk import Log #type: ignore

from . import defines, options, items, hints, enemies, missions, other
from .defines import Tag, seeds_dir
from .locations import Location
from .items import ItemPool

from base64 import b32encode, b32decode
import random, os, importlib

from typing import Callable, List, Optional, Sequence
from types import ModuleType


Version = 2
SupportedVersions = (1,2)


AppliedSeed: Optional[Seed] = None


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
    def Generate(cls, tags: Tag) -> Seed:
        value = random.getrandbits(30) << 42
        value |= tags.value << 6
        value |= Version

        data = value.to_bytes(length=9, byteorder='big')

        return cls(data, Version, tags, _stringify(data))

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
        global AppliedSeed

        if self.version not in SupportedVersions:
            raise ValueError(
                f"Seed {self.string} is the incorrect version for this release of Loot Randomizer. "
                "If you would like to play it, please install a version of Loot Randomizer that "
                f"specifies a seed version of {self.version}."
            )
        
        missing_dlcs = ""
        for tag in Tag:
            if (tag in defines.ContentTags) and (tag in self.tags) and (tag not in options.OwnedContent):
                missing_dlcs += "\n &#x2022; " + tag.content_title

        if missing_dlcs != "":
            raise ValueError(f"Seed {self.string} requires additional DLCs to play:{missing_dlcs}")

        if AppliedSeed:
            AppliedSeed.revert()

        AppliedSeed = self

        self.version_module = importlib.import_module(f".seedversions.v{self.version}", __package__)
        version_locations = self.version_module.Locations
        version_items = self.version_module.Items

        for location in version_locations:
            location.enable()
        for item in version_items:
            item.enable()

        self.locations = tuple(location for location in version_locations if location.tags in self.tags)
        self.items = [item for item in version_items if item.valid_items]

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

        for location in version_locations:
            location.update_hint()
            location.toggle_hint(True)


    def revert(self) -> None:
        global AppliedSeed
        AppliedSeed = None

        for location in self.locations:
            location.item = None

        for location in self.version_module.Locations:
            location.disable()
        for item in self.version_module.Items:
            item.disable()


    def generate_file(self, name: str, formatter: Callable[[int, Location], str]) -> str:
        path = os.path.join(seeds_dir, f"{self.string} {name}.txt")
        if os.path.exists(path):
            return path

        with open(path, 'w') as file:
            self.items
            item_warning = " (not all accessible)" if self.item_count > len(self.locations) else ""

            file.write(
                f"{name} for Loot Randomizer Seed {self.string}\n\n"
                f"Total locations: {len(self.locations)}\n"
                f"Total items: {self.item_count}{item_warning}\n\n"
            )
            for tag in Tag:
                file.write(f"{tag.caption}: {'On' if (tag in self.tags) else 'Off'}\n")

            for tag in Tag:
                if not tag & defines.ContentTags & self.tags:
                    continue

                entries = tuple(
                    (item, location) for item, location in zip(self.items, self.locations)
                    if tag in location.tags
                )
                if not len(entries):
                    continue

                file.write(f"\n{tag.content_title}\n")

                for item, location in entries:
                    file.write(formatter(item, location) + "\n")
        
        return path


    def generate_guide(self) -> str:
        return self.generate_file("Locations", lambda item, location: str(location))

    def generate_hints(self) -> str:
        return self.generate_file("Hints", lambda item, location: f"{location}\t-\t{item.vague_hint}")

    def generate_spoilers(self) -> str:
        return self.generate_file("Spoilers", lambda item, location: f"{location}\t-\t{item.name}")


def generate_wikis(version: int) -> None:
    from html import escape

    all_tags = Tag(0)
    for tag in Tag:
        all_tags |= tag

    dummy_seed = Seed.Generate(all_tags)
    dummy_seed.apply()

    with open(os.path.join(seeds_dir, "locations wiki.txt"), 'w', encoding='utf-8') as file:
        for content_tag in Tag:
            if not content_tag & defines.ContentTags:
                continue

            locations = tuple(location for location in dummy_seed.locations if content_tag & location.tags)
            if not locations:
                continue

            file.write(f"\n### {escape(content_tag.content_title)}\n")
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

            for item in dummy_seed.version_module.Items:
                if item.vague_hint is not hint:
                    continue

                content = ""
                fallback_content = ""

                for tag in Tag:
                    if tag & defines.ContentTags:
                        if tag in item.items[0].tags:
                            content = f"<kbd>{escape(tag.caption)}</kbd>"
                        elif item.fallback and tag in item.fallback.tags:
                            fallback_content = f"or <kbd>{escape(tag.caption)}</kbd>"

                file.write(f"| {escape(item.name)} | {content}{fallback_content} |\n")
