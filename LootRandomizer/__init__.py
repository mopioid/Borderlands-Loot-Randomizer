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

    from Mods.LootRandomizer import options, seed, hints #type: ignore
    from Mods.LootRandomizer import items, locations, enemies, missions #type: ignore

    import sys, importlib
    for submodule_name in (
        "defines", "seed", "options", "hints", "items", "item_list",
        "locations", "missions", "mission_list", "enemies", "enemy_list", # "misc",
    ):
        importlib.reload(sys.modules["Mods.LootRandomizer." + submodule_name])

    # for module_name, module in sys.modules.items():
    #     if module_name.startswith("Mods.LootRandomizer."):
    #         importlib.reload(module)
else:
    from . import options, seed
    from . import items, hints, locations, enemies, missions

from typing import Sequence


class LootRandomizer(ModMenu.SDKMod):
    Name: str = "Loot Randomizer"
    Version: str = "1.0"
    Description: str = ""
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
        seed.Revert()

        options.Disable()
        missions.Disable()
        enemies.Disable()
        locations.Disable()
        items.Disable()
        hints.Disable()
        super().Disable()

        GetEngine().GamePlayers[0].Actor.ConsoleCommand("obj garbage")


_mod_instance = LootRandomizer()

if __name__ == "__main__":
    try: _mod_instance.__class__.__module__ = _this_module
    except: pass
    ModMenu.RegisterMod(_mod_instance)
    _mod_instance.Enable()
else:
    ModMenu.RegisterMod(_mod_instance)


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