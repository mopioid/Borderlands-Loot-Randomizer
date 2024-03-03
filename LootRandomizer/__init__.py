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

    from Mods.LootRandomizer import options, items, hints #type: ignore
    from Mods.LootRandomizer import locations, enemies, missions, mission_list #type: ignore

    import sys, importlib
    for submodule_name in (
        "defines", "seed", "options", "hints", "items", "item_list",
        "locations", "missions", "mission_list", "enemies", "enemy_list", # "misc",
    ):
        importlib.reload(sys.modules["Mods.LootRandomizer." + submodule_name])
else:
    from . import options, items, hints
    from . import locations, enemies, missions, mission_list

from typing import Sequence


class LootRandomizer(ModMenu.SDKMod):
    Name: str = "Loot Randomizer"
    Version: str = "1.0"
    # TODO
    Description: str = ""
    Author: str = "mopioid"
    Types: ModMenu.ModTypes = ModMenu.ModTypes.Gameplay
    SaveEnabledState: ModMenu.EnabledSaveType = ModMenu.EnabledSaveType.LoadOnMainMenu

    Options: Sequence[ModMenu.Options.Base] = options.Options


    def Enable(self):
        mission_list.Enable()
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
        mission_list.Disable()
        super().Disable()


options.mod_instance = LootRandomizer()

if __name__ == "__main__":
    try: options.mod_instance.__class__.__module__ = _this_module
    except: pass
    ModMenu.RegisterMod(options.mod_instance)
    options.mod_instance.Enable()
else:
    ModMenu.RegisterMod(options.mod_instance)


"""
Features:
- Every named enemy in the game made to be able to drop loot
- Every side mission in the game made able to be repeated
- Every enemy and mission hand tuned to adjust loot generosity
- Categories to disable certain loot locations (e.g. "rare enemies" or "very long missions")
- Hint items dropped by enemies to give an indiation of whether they are worth farming
- Seeds save item locations across game sessions, and also can be shared with friends

Compatibility:
- Works with any overhauls that do not add items to the game (e.g. UCP, BL2fix, Reborn)
- Works in co-op, with only the only host needing to run the mod
- Seeds can be generated to accomodate any combinations of DLCs
"""
