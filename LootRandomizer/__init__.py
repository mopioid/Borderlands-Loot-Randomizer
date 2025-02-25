from unrealsdk import UObject

from Mods import ModMenu


if __name__ == "__main__":
    for mod in ModMenu.Mods:
        if mod.Name == "Loot Randomizer":
            ModMenu.Mods.remove(mod)
            _this_module = mod.__class__.__module__
            if mod.IsEnabled:
                mod.Disable()
            break

    if ModMenu.Game.GetCurrent() == ModMenu.Game.BL2:
        game_module_name = "bl2"
    elif ModMenu.Game.GetCurrent() == ModMenu.Game.TPS:
        game_module_name = "tps"
    else:
        raise

    submodule_names = (
        "defines",
        "options",
        "hints",
        "items",
        "locations",
        "missions",
        "enemies",
        "other",
        game_module_name,
        game_module_name + ".items",
        game_module_name + ".locations",
        *(f"{game_module_name}.v{version}" for version in range(1, 32)),
        "seed",
    )

    import sys, importlib

    for submodule_name in submodule_names:
        module = sys.modules.get("Mods.LootRandomizer.Mod." + submodule_name)
        if module:
            importlib.reload(module)


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

from typing import Optional


class LootRandomizer(ModMenu.SDKMod):
    Name = "Loot Randomizer"
    Version = "1.5.5"
    Description = "Create seeds to shuffle items into new farm locations."
    Author = "mopioid"
    SupportedGames = ModMenu.Game.BL2 | ModMenu.Game.TPS
    Types = ModMenu.ModTypes.Gameplay
    SaveEnabledState = ModMenu.EnabledSaveType.LoadOnMainMenu

    Options = options.Options

    def Enable(self):
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
        super().Disable()

    @ModMenu.ClientMethod
    def SendSeed(self, seed_string: str, PC: Optional[UObject] = None) -> None:
        host_seed = seed.Seed.FromString(seed_string)
        host_seed.apply()
        options.HideSeedOptions()
        options.SaveSeedString(seed_string)

    @ModMenu.ClientMethod
    def SendTracker(self, entry: str, drop: bool) -> None:
        if seed.AppliedSeed:
            location = seed.SeedEntry(entry).match_location()
            seed.AppliedSeed.update_tracker(location, drop)


options.mod_instance = LootRandomizer()

if __name__ == "__main__":
    options.mod_instance.__class__.__module__ = _this_module  # type: ignore
    ModMenu.RegisterMod(options.mod_instance)
    options.mod_instance.Enable()
else:
    ModMenu.RegisterMod(options.mod_instance)
