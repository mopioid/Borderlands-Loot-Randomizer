from unrealsdk import UObject

from Mods import ModMenu

if __name__ == "__main__":
    for mod in ModMenu.Mods:
        if mod.Name != "Loot Randomizer":
            continue

        if mod.IsEnabled:
            mod.Disable()
        ModMenu.Mods.remove(mod)
        _this_module = mod.__class__.__module__
        break

    # TODO: remove
    from Mods.LootRandomizer.Mod import seed

    seed.generate_seedversion()
    # seed.generate_wikis(1)

    import sys, importlib

    for submodule_name in (
        "defines",
        "options",
        "hints",
        "items",
        "locations",
        "enemies",
        "missions",
        "other",
        "seed" "bl2",
        "bl2.items",
        "bl2.locations",
        "bl2.v1",
        "bl2.v2",
        "bl2.v3",
        "bl2.v4",
        "bl2.v5",
        "tps",
        "tps.items",
        "tps.locations",
        "tps.v1",
    ):
        module = sys.modules.get("Mods.LootRandomizer.Mod." + submodule_name)
        if module:
            importlib.reload(module)


from typing import Optional, Sequence

from Mods.LootRandomizer.Mod.defines import *
from Mods.LootRandomizer.Mod import (
    options,
    hints,
    items,
    locations,
    enemies,
    missions,
    other,
    seed,
)

if BL2:
    from Mods.LootRandomizer.Mod.bl2.locations import Locations
elif TPS:
    from Mods.LootRandomizer.Mod.tps.locations import Locations
else:
    raise Exception(
        f"Loot Randomizer is not available for {ModMenu.Game.GetCurrent().name}"
    )


class LootRandomizer(ModMenu.SDKMod):
    Name: str = "Loot Randomizer"
    Version: str = "1.6"
    Description: str = "Create seeds to shuffle items into new farm locations."
    Author: str = "mopioid"
    SupportedGames: ModMenu.Game = ModMenu.Game.BL2 | ModMenu.Game.TPS
    Types: ModMenu.ModTypes = ModMenu.ModTypes.Gameplay
    SaveEnabledState: ModMenu.EnabledSaveType = (
        ModMenu.EnabledSaveType.LoadOnMainMenu
    )

    Options: Sequence[ModMenu.Options.Base] = options.Options

    def Enable(self):
        for location in Locations:
            location.enable()
        hints.Enable()
        items.Enable()
        locations.Enable()
        enemies.Enable()
        missions.Enable()
        other.Enable()
        options.Enable()
        super().Enable()

    def Disable(self):
        options.Disable()
        other.Disable()
        missions.Disable()
        enemies.Disable()
        locations.Disable()
        items.Disable()
        hints.Disable()
        for location in Locations:
            location.disable()
        super().Disable()

    @ModMenu.ClientMethod
    def SendSeed(self, seed_string: str, PC: Optional[UObject] = None) -> None:
        host_seed = seed.Seed.FromString(seed_string)
        host_seed.apply()
        options.NewSeedOptions.IsHidden = True
        options.SelectSeedOptions.IsHidden = True
        options.SaveSeedString(seed_string)

    @ModMenu.ClientMethod
    def SendTracker(self, entry: str, drop: bool) -> None:
        if seed.AppliedSeed:
            location = seed.SeedEntry(entry).match_location()
            seed.AppliedSeed.update_tracker(location, drop)


options.mod_instance = LootRandomizer()

if __name__ == "__main__":
    try:
        options.mod_instance.__class__.__module__ = _this_module  # type: ignore
    except:
        pass
    ModMenu.RegisterMod(options.mod_instance)
    options.mod_instance.Enable()
else:
    ModMenu.RegisterMod(options.mod_instance)
