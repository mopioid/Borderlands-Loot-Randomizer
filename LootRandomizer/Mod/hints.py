from unrealsdk import FindObject, KeepAlive #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct  #type: ignore

from . import seed, options, items
from .defines import construct_object, set_command, show_dialog

import enum

from typing import Callable, Optional


class Hint(str, enum.Enum):
    formatter: Callable[[str], str]

    Dud = "Nothing"

    PurplePistol = "Purple Pistol"
    UniquePistol = "Unique Pistol"
    LegendaryPistol = "Legendary Pistol"

    PurpleAR = "Purple Assault Rifle"
    UniqueAR = "Unique Assault Rifle"
    LegendaryAR = "Legendary Assault Rifle"

    PurpleShotgun = "Purple Shotgun"
    UniqueShotgun = "Unique Shotgun"
    LegendaryShotgun = "Legendary Shotgun"

    PurpleSMG = "Purple SMG"
    UniqueSMG = "Unique SMG"
    LegendarySMG = "Legendary SMG"

    PurpleSniper = "Purple Sniper Rifle"
    UniqueSniper = "Unique Sniper Rifle"
    LegendarySniper = "Legendary Sniper Rifle"

    PurpleLauncher = "Purple Rocket Launcher"
    UniqueLauncher = "Unique Rocket Launcher"
    LegendaryLauncher = "Legendary Rocket Launcher"

    EtechWeapon = "E-tech Weapon"
    PearlescentWeapon = "Pearlescent Weapon"
    SeraphWeapon = "Seraph Weapon"
    EffervescentWeapon = "Effervescent Weapon"

    PurpleShield = "Purple Shield"
    UniqueShield = "Unique Shield"
    LegendaryShield = "Legendary Shield"

    BlueClassMod = "Blue Class Mod"
    PurpleClassMod = "Purple Class Mod"
    LegendaryClassMod = "Legendary Class Mod"

    PurpleGrenade = "Purple Grenade"
    UniqueGrenade = "Unique Grenade"
    LegendaryGrenade = "Legendary Grenade"

    PurpleRelic = "Purple Relic"
    UniqueRelic = "Unique Relic"
    EtechRelic = "E-tech Relic"

    SeraphItem = "Seraph Item"
    EffervescentItem = "Effervescent Item"


def _format_dud         (string: str) -> str: return f"<font color='#bc9898'>{string}</font>"
def _format_blue        (string: str) -> str: return f"<font color='#3c8eff'>{string}</font>"
def _format_purple      (string: str) -> str: return f"<font color='#a83fe5'>{string}</font>"
def _format_etech       (string: str) -> str: return f"<font color='#ca00a8'>{string}</font>"
def _format_legendary   (string: str) -> str: return f"<font color='#ffb400'>{string}</font>"
def _format_unique      (string: str) -> str: return f"<font color='#dc4646'>{string}</font>"
def _format_seraph      (string: str) -> str: return f"<font color='#ff9ab8'>{string}</font>"
def _format_pearlescent (string: str) -> str: return f"<font color='#00ffff'>{string}</font>"
def _format_effervescent(string: str) -> str:
    colors = ('#ffadad',  '#ffd6a5',  '#fdffb6',  '#caffbf',  '#9bf6ff',  '#a0c4ff',  '#bdb2ff', '#ffc6ff')

    index = 0
    formatted = ""
    for char in string:
        formatted += f"<font color='{colors[index]}'>{char}</font>"

        index += 1
        if index == len(colors):
            index = 0

    return formatted


Hint.Dud.formatter = _format_dud

Hint.BlueClassMod.formatter = _format_blue
Hint.PurpleClassMod.formatter = _format_purple
Hint.LegendaryClassMod.formatter = _format_legendary

Hint.PurpleShield.formatter = _format_purple
Hint.UniqueShield.formatter = _format_unique
Hint.LegendaryShield.formatter = _format_legendary

Hint.PurpleRelic.formatter = _format_purple
Hint.UniqueRelic.formatter = _format_unique
Hint.EtechRelic.formatter = _format_etech

Hint.PurpleGrenade.formatter = _format_purple
Hint.UniqueGrenade.formatter = _format_unique
Hint.LegendaryGrenade.formatter = _format_legendary

Hint.PurplePistol.formatter = _format_purple
Hint.UniquePistol.formatter = _format_unique
Hint.LegendaryPistol.formatter = _format_legendary

Hint.PurpleAR.formatter = _format_purple
Hint.UniqueAR.formatter = _format_unique
Hint.LegendaryAR.formatter = _format_legendary

Hint.PurpleShotgun.formatter = _format_purple
Hint.UniqueShotgun.formatter = _format_unique
Hint.LegendaryShotgun.formatter = _format_legendary

Hint.PurpleSMG.formatter = _format_purple
Hint.UniqueSMG.formatter = _format_unique
Hint.LegendarySMG.formatter = _format_legendary

Hint.PurpleSniper.formatter = _format_purple
Hint.UniqueSniper.formatter = _format_unique
Hint.LegendarySniper.formatter = _format_legendary

Hint.PurpleLauncher.formatter = _format_purple
Hint.UniqueLauncher.formatter = _format_unique
Hint.LegendaryLauncher.formatter = _format_legendary

Hint.EtechWeapon.formatter = _format_etech
Hint.PearlescentWeapon.formatter = _format_pearlescent

Hint.SeraphItem.formatter = _format_seraph
Hint.SeraphWeapon.formatter = _format_seraph

Hint.EffervescentItem.formatter = _format_effervescent
Hint.EffervescentWeapon.formatter = _format_effervescent


DudDescriptions = (
    "*Buzzer noise*",
    "We ain't found s***!",
    "*Hic*",
    "I got a rock.",
    "Your princess is in another castle.",
    "Wow, a whole buncha nothing!",
    "The label reads 'Dixie Wrecked Brand Moonshine.'",
    "Don't know what's in it, but who cares?",
    "Error 404: Loot not found.",
    "The sip, dude!",
    "0% Loot By Volume",
    "It contains a small ship.",
    "You fell for one of the classic blunders.",
    "Sending out an SOS.",
    "Now about that beer I owed ya!",
    "Task failed successfully.",
    "The real loot was the friends we met along the way.",
    "Think this will give me superpowers?",
    "Consult your doctor if you experience nasuea, swelling, or shortness of breath.",
    "Send your complaints to<br>www.twitch.tv/mopioid.",
    "Well, this is embarrassing.",
    "Drowns sorrows.",
    "Don't look at me like that.",
    "Try again in another seed.",
    "This is to indicate that the location named at the top of this item card has no drop.",
    "Go away.",
    "Signs point to no.",
    "Do not pass Go.",
    "I'm With Stupid ^",
    "I don't want to live on this planet anymore...",
    "GOOD. BUT WHERE IS GUN PILE?",
)


inventory_template: UObject = None
useitem_template: UObject = None
presentation_template: UObject = None
custompresentation_template: UObject = None

useitem_behavior: UObject = None

hintitem_mesh: UObject = None
duditem_mesh: UObject = None
hintitem_pickupflag: UObject = None
duditem_pickupflag: UObject = None


# TODO - make dud item for mission turnins (clone relic?)


def Enable() -> None:
    global inventory_template, useitem_template, presentation_template, custompresentation_template
    global useitem_behavior, hintitem_mesh, duditem_mesh, hintitem_pickupflag, duditem_pickupflag

    RunHook("WillowGame.Behavior_LocalCustomEvent.ApplyBehaviorToContext", "LootRandomizer", _Behavior_LocalCustomEvent)

    original = FindObject("InventoryBalanceDefinition", "GD_ItemGrades.BuffDrink.ItemGrade_BuffDrink_Toughness")
    inventory_template = construct_object(original, "Hint_Inventory_Default")

    inventory_template.Manufacturers = ((
        FindObject("ManufacturerDefinition", "GD_Currency.Manufacturers.Cash_Manufacturer"),
    ),)

    original = FindObject("UsableItemDefinition", "GD_BuffDrinks.A_Item.BuffDrink_Toughness")
    useitem_template = construct_object(original, "Hint_Item_Default")

    useitem_template.bPickupInBulk = False
    useitem_template.CalloutDefinition = None
    useitem_template.CustomPresentations = ()
    useitem_template.OnUseConstraints = ()

    original = FindObject("InteractionIconDefinition", "GD_InteractionIcons.Default.Icon_DefaultPickUp")
    useitem_template.PickupIconOverride = construct_object(original, "Icon_DismissHint")
    set_command(useitem_template.PickupIconOverride, "Text", "Dismiss")

    original = FindObject("BehaviorProviderDefinition", "GD_Currency.A_Item.Currency:BehaviorProviderDefinition_0")
    useitem_bpd = construct_object(original, "Hint_BehaviorProviderDefinition")
    useitem_template.BehaviorProviderDefinition = useitem_bpd

    original = FindObject("InventoryCardPresentationDefinition", "GD_InventoryPresentations.Definitions.Credits")    
    presentation_template = construct_object(original, "Hint_Presentation")

    custompresentation_template = construct_object("AttributePresentationDefinition", "Hint_Presentation_Default")
    custompresentation_template.BasePriority = 2.0
    custompresentation_template.bDontDisplayNumber = True
    custompresentation_template.bEnableTextColor = False

    useitem_behavior = construct_object("Behavior_LocalCustomEvent", useitem_bpd)
    useitem_bpd.BehaviorSequences[0].BehaviorData2[0].Behavior = useitem_behavior

    hintitem_mesh = FindObject("StaticMesh", "prop_interactive.Meshes.DataRecorder_01_Active")
    duditem_mesh = FindObject("StaticMesh", "Prop_Details.Meshes.BeerBottle")
    hintitem_pickupflag = FindObject("Texture2D", "fx_shared_items.Textures.ItemCards.sdu")
    duditem_pickupflag = FindObject("Texture2D", "fx_shared_items.Textures.ItemCards.Buff_Toughen-up")


def Disable() -> None:
    RemoveHook("WillowGame.Behavior_LocalCustomEvent.ApplyBehaviorToContext", "LootRandomizer")


def UpdateHints() -> None:
    if useitem_template and seed.AppliedSeed:
        for location in seed.AppliedSeed.locations:
            location.update_hint()

def ResetDismissed() -> None:
    if useitem_template and seed.AppliedSeed:
        for location in seed.AppliedSeed.locations:
            location.toggle_hint(True)

def _Behavior_LocalCustomEvent(caller: UObject, function: UFunction, params: FStruct) -> bool:
    if caller is not useitem_behavior:
        return True

    matched_location = None

    hint_inventory = params.SelfObject.DefinitionData.BalanceDefinition
    for location in seed.AppliedSeed.locations: #type: ignore
        if location.hint_inventory is hint_inventory:
            matched_location = location
            break

    if not matched_location:
        return False
    
    if (matched_location.item != items.DudItem) and (not options.HintTrainingSeen.CurrentValue):
        options.HintTrainingSeen.CurrentValue = True
        show_dialog(
            "Item Hints",
            (
                "The object you just found is an item hint, indicating that the specified loot "
                "source does indeed drop loot in your seed.\n\n"

                "You can configure the amount of information provided by loot hints via "
                "Options > Mods > Loot Randomizer > Hint Display.\n\n"

                "To dismiss hints or duds for a given source, simply interact with them. You may "
                "reset your dismissed hints via\n"
                "Options > Mods > Loot Randomizer > Reset Dismissed Hints.\n\n"
            ),
            5
        )
    elif (matched_location.item == items.DudItem) and (not options.DudTrainingSeen.CurrentValue):
        options.DudTrainingSeen.CurrentValue = True
        show_dialog(
            "Dud Items",
            (
                "The object you just found is a dud item, indicating that the specified loot "
                "source is included in your seed, but was not assigned an item.\n\n"

                "To dismiss hints or duds for a given source, simply interact with them. You may "
                "reset your dismissed hints via\n"
                "Options > Mods > Loot Randomizer > Reset Dismissed Hints.\n\n"
            ),
            5
        )
    else:
        location.toggle_hint(False)

    return False
