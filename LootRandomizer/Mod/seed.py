from __future__ import annotations

from . import defines, options, items, hints, item_list, mission_list, enemy_list, other_list
from .defines import Tag, seeds_dir
from .locations import Location
from .items import ItemPool

from base64 import b32encode, b32decode
import random, os

from typing import Callable, List, Optional, Sequence


Version = 1


SelectedSeed: Optional[Seed] = None


def _stringify(data: bytes) -> str:
    string = b32encode(data).decode("ascii").strip("=").lower()
    return f"{string[0:5]}-{string[5:10]}-{string[10:15]}"


class Seed:
    data: bytes
    string: str

    version: int
    tags: Tag

    _locations: Optional[Sequence[Location]] = None
    _items: Optional[Sequence[ItemPool]] = None
    _item_count: int

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


    @property
    def locations(self) -> Sequence[Location]:
        if self._locations is None:
            self._locations = (
                *(enemy for enemy in enemy_list.Enemies if enemy.tags in self.tags),
                *(mission for mission in mission_list.Missions if mission.tags in self.tags),
                *(other for other in other_list.Others if other.tags in self.tags),
            )
        return self._locations

    @property
    def items(self) -> Sequence[ItemPool]:
        if self._items is None:
            randomizer = random.Random(self.data)

            self._items = [item for item in item_list.Items if item.items_for_tags(self.tags)]
            self._item_count = len(self._items)

            location_count = len(self.locations)
            item_count = len(self._items)

            if location_count < item_count:
                self._items = randomizer.sample(self._items, location_count)

            elif location_count == item_count:
                randomizer.shuffle(self._items)

            elif self.tags & Tag.DuplicateItems:
                self._items *= (location_count // item_count)
                self._items += randomizer.sample(self._items, location_count % item_count)
                randomizer.shuffle(self._items)

            else:
                self._items += [items.DudItem] * (location_count - item_count)
                randomizer.shuffle(self._items)
            
        return self._items
    

    def generate_file(self, name: str, formatter: Callable[[int, Location], str]) -> str:
        path = os.path.join(seeds_dir, f"{self.string} {name}.txt")
        if os.path.exists(path):
            return path

        with open(path, 'w') as file:
            self.items
            item_warning = " (not all accessible)" if self._item_count > len(self.locations) else ""

            file.write(
                f"{name} for Loot Randomizer Seed {self.string}\n\n"
                f"Total locations: {len(self.locations)}\n"
                f"Total items: {self._item_count}{item_warning}\n\n"
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


    def apply(self) -> None:
        global SelectedSeed

        if self.version != Version:
            raise Exception(
                f"Seed {self.string} is the incorrect version for this release of Loot Randomizer. "
                "If you would like to play it, please install a version of Loot Randomizer that "
                f"specifies a seed version of {self.version}."
            )
        
        missing_dlcs = ""
        for tag in Tag:
            if (tag in defines.ContentTags) and (tag in self.tags) and (tag not in options.OwnedContent):
                missing_dlcs += "\n &#x2022; " + tag.content_title

        if missing_dlcs != "":
            raise Exception(f"Seed {self.string} requires additional DLCs to play:{missing_dlcs}")

        if SelectedSeed:
            SelectedSeed.revert()

        SelectedSeed = self

        for location, item in zip(self.locations, self.items):
            item.apply_tags(self.tags)
            location.apply_tags(self.tags)
            location.item = item

    def revert(self) -> None:
        global SelectedSeed
        SelectedSeed = None
        
        for location in self.locations:
            location.item = None


def generate_wikis() -> None:
    from html import escape

    with open(os.path.join(seeds_dir, "locations wiki.txt"), 'w', encoding='utf-8') as file:
        def write_location(location: Location, type: str) -> None:
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

            file.write(f"| {type} | {escape(location.name)} | {rolls_string} | {settings_string} |\n")

        for content_tag in Tag:
            if not content_tag & defines.ContentTags:
                continue

            enemies  = tuple(   enemy for   enemy in   enemy_list.Enemies  if content_tag in   enemy.tags )
            missions = tuple( mission for mission in mission_list.Missions if content_tag in mission.tags )
            others   = tuple(   other for   other in   other_list.Others   if content_tag in   other.tags )

            if not (len(enemies) or len(missions) or len(others)):
                continue

            file.write(f"\n### {escape(content_tag.content_title)}\n")
            file.write("\n| **Type** | **Location** | **Rolls** | **Required Settings** |\n| - | - | - | - |\n")

            for enemy   in enemies:  write_location(enemy,   "Enemy"  )
            for mission in missions: write_location(mission, "Mission")
            for other   in others:   write_location(other,   "Other"  )

    with open(os.path.join(seeds_dir, "items wiki.txt"), 'w', encoding='utf-8') as file:
        for hint in hints.Hint:
            if hint is hints.Hint.Dud:
                continue

            file.write(f"\n### {escape(hint)}s\n")
            file.write("\n| **Item** | **Required Content** |\n| - | - |\n")

            for item in item_list.Items:
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