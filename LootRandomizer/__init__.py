from unrealsdk import Log, GetEngine  #type: ignore

from Mods import ModMenu #type: ignore

if __name__ == "__main__":
    from Mods.LootRandomizer import options, items, locations #type: ignore

    import sys, importlib
    for module_name, module in sys.modules.items():
        if module_name.startswith("Mods.LootRandomizer."):
            importlib.reload(module)
else:
    from . import options, items, hints, locations

from typing import Sequence


class LootRandomizer(ModMenu.SDKMod):
    Name: str = "Loot Randomizer"
    Version: str = "1.0"
    Description: str = ""
    Author: str = "mopioid"
    Types: ModMenu.ModTypes = ModMenu.ModTypes.Gameplay
    SaveEnabledState: ModMenu.EnabledSaveType = ModMenu.EnabledSaveType.LoadOnMainMenu

    Options: Sequence[ModMenu.Options.Base] = (options.HintType,)


    def Enable(self):
        super().Enable()

        options.Enable()
        items.Enable()
        locations.Enable()

        for item in items.Items:
            if item.name == "World Burn":
                break

        locations.Apply()
        for location in locations.Locations:
            location.apply(item)


    def Disable(self):
        super().Disable()

        options.Disable()
        items.Disable()
        locations.Disable()

        GetEngine().GamePlayers[0].Actor.ConsoleCommand("obj garbage")


_mod_instance = LootRandomizer()

if __name__ == "__main__":
    for mod in ModMenu.Mods:
        if mod.Name == _mod_instance.Name:
            if mod.IsEnabled:
                mod.Disable()
            ModMenu.Mods.remove(mod)
            _mod_instance.__class__.__module__ = mod.__class__.__module__
            break

    ModMenu.RegisterMod(_mod_instance)
    _mod_instance.Enable()
else:
    ModMenu.RegisterMod(_mod_instance)


"""

disable Sky Rocket and VH Relic in starting gear

"""