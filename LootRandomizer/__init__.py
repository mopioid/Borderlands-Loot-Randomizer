from unrealsdk import Log, GetEngine  #type: ignore

from Mods import ModMenu #type: ignore

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
    from Mods.LootRandomizer.Mod import locations, enemies, missions #type: ignore

    import sys, importlib
    for submodule_name in (
        "defines", "seed", "options", "hints", "items", "locations", "missions", "enemies", "other",
        "seedversions.v1", "seedversions.v2"
    ):
        module = sys.modules.get("Mods.LootRandomizer.Mod." + submodule_name)
        if module:
            importlib.reload(module)
else:
    from .Mod import options, items, hints
    from .Mod import locations, enemies, missions

from typing import Sequence


class LootRandomizer(ModMenu.SDKMod):
    Name: str = "Loot Randomizer"
    Version: str = "1.0"
    Description: str = "Shuffles every item into new farm locations."
    Author: str = "mopioid"
    Types: ModMenu.ModTypes = ModMenu.ModTypes.Gameplay
    SaveEnabledState: ModMenu.EnabledSaveType = ModMenu.EnabledSaveType.LoadOnMainMenu

    Options: Sequence[ModMenu.Options.Base] = options.Options


    def Enable(self):
        hints.Enable()
        items.Enable()
        locations.Enable()
        enemies.Enable()
        missions.Enable()
        options.Enable()
        super().Enable()


    def Disable(self):
        options.Disable()
        missions.Disable()
        enemies.Disable()
        locations.Disable()
        items.Disable()
        hints.Disable()
        super().Disable()


options.mod_instance = LootRandomizer()

if __name__ == "__main__":
    try: options.mod_instance.__class__.__module__ = _this_module
    except: pass
    ModMenu.RegisterMod(options.mod_instance)
    options.mod_instance.Enable()
else:
    ModMenu.RegisterMod(options.mod_instance)
