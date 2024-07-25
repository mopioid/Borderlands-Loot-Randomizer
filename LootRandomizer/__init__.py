from unrealsdk import Log, GetEngine, UObject  #type: ignore

from Mods import ModMenu #type: ignore

from typing import Optional


if __name__ == "__main__":
    for mod in ModMenu.Mods:
        if mod.Name != "Loot Randomizer":
            continue

        if mod.IsEnabled:
            mod.Disable()
        ModMenu.Mods.remove(mod)
        _this_module = mod.__class__.__module__
        break

    from Mods.LootRandomizer.Mod import options, items, hints #type: ignore
    from Mods.LootRandomizer.Mod import locations, enemies, missions, other, catalog, seed #type: ignore

    import sys, importlib
    for submodule_name in (
        "defines", "seed", "options", "hints", "items", "locations", "missions", "enemies", "other",
        "catalog", "seedversions.v1", "seedversions.v2", "seedversions.v3", "seedversions.v4",
        "seedversions.v5",
    ):
        module = sys.modules.get("Mods.LootRandomizer.Mod." + submodule_name)
        if module:
            importlib.reload(module)
else:
    from .Mod import options, items, hints
    from .Mod import locations, enemies, missions, other, catalog, seed

from typing import Sequence


class LootRandomizer(ModMenu.SDKMod):
    Name: str = "Loot Randomizer"
    Version: str = "1.2"
    Description: str = "Create seeds to shuffle items into new farm locations."
    Author: str = "mopioid"
    Types: ModMenu.ModTypes = ModMenu.ModTypes.Gameplay
    SaveEnabledState: ModMenu.EnabledSaveType = ModMenu.EnabledSaveType.LoadOnMainMenu

    Options: Sequence[ModMenu.Options.Base] = options.Options


    def Enable(self):
        for location in catalog.Locations:
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
        for location in catalog.Locations:
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
    try: options.mod_instance.__class__.__module__ = _this_module
    except: pass
    ModMenu.RegisterMod(options.mod_instance)
    options.mod_instance.Enable()
else:
    ModMenu.RegisterMod(options.mod_instance)
