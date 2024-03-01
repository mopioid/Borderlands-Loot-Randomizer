from __future__ import annotations

from . import item_list, mission_list, enemy_list
from .defines import Tag
from .locations import Location
from .items import ItemPool

from base64 import b32encode, b32decode
from struct import Struct
import random

from typing import Sequence


Version = 0

SelectedTags = Tag(~0)

Items: Sequence[ItemPool] = ()
Locations: Sequence[Location] = ()


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
        return cls(random.getrandbits(32), Version, tags)

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


def Apply(seed: Seed) -> None:
    global Locations, Items, SelectedTags

    Revert()

    # seed = Seed.Generate(Tag(~0))
    SelectedTags = seed.tags
    
    missing_tags = ~SelectedTags

    Locations = (
        *(location for location in   enemy_list.Enemies  if not (location.tags & missing_tags)),
        *(location for location in mission_list.Missions if not (location.tags & missing_tags))
    )

    Items = [item for item in item_list.Items if item.validate()]

    randomizer = random.Random(seed.value)

    item_deficit = len(Locations) - len(Items)

    if item_deficit < 0:
        Items = randomizer.sample(Items, len(Locations))
    else:
        if seed.tags & Tag.DuplicateItems:
            extras = randomizer.sample(Items, item_deficit)
        else:
            #TODO: pad surplus with dud item
            # extras = [dud_item] * surplus
            pass
        Items += extras
        randomizer.shuffle(Items)

    for location, item in zip(Locations, Items):
        location.apply(item)


def Revert() -> None:
    global Locations, Items

    for location in Locations:
        location.revert()
    Locations = ()

    for pool in Items:
        pool.release()
    Items = ()
