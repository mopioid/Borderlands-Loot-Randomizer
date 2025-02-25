from unrealsdk import FindObject, KeepAlive, LoadPackage
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct

from . import seed, options
from .defines import *

from typing import Optional


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
    "0\x25 Loot By Volume",
    "It contains a small ship.",
    "You fell for one of the classic blunders.",
    "Sending out an SOS.",
    "Now about that beer I owed ya.",
    "Task failed successfully.",
    "The real loot was the friends we met along the way.",
    "Think this will give me superpowers?",
    "Consult your doctor if you experience nasuea, swelling, or shortness of breath.",
    "Send your complaints to<br>www.twitch.tv/mopioid",
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
    "Have you seen my gun?",
    "Reduce, Reuse, Recycle!",
    "Hey did you know there's a laser blowing up the moon?",
)


inventory_template: Optional[UObject] = None
useitem_template: Optional[UObject] = None
presentation_template: Optional[UObject] = None
custompresentation_template: Optional[UObject] = None

hintitem_mesh: Optional[UObject] = None
duditem_mesh: Optional[UObject] = None
hintitem_pickupflag: Optional[UObject] = None
duditem_pickupflag: Optional[UObject] = None

useitem_behavior: Optional[UObject] = None

padding_pool: UObject


def Enable() -> None:
    global inventory_template, useitem_template, presentation_template, custompresentation_template
    global hintitem_mesh, duditem_mesh, hintitem_pickupflag, duditem_pickupflag
    global useitem_behavior, padding_pool

    RunHook(
        "WillowGame.Behavior_LocalCustomEvent.ApplyBehaviorToContext",
        "LootRandomizer",
        _Behavior_LocalCustomEvent,
    )

    padding_pool = construct_object("ItemPoolDefinition", "Padding_ItemPool")

    original = FindObject(
        "InventoryBalanceDefinition",
        "GD_ItemGrades.BuffDrink.ItemGrade_BuffDrink_Toughness",
    )
    inventory_template = construct_object(original, "Hint_Inventory_Default")
    padding = construct_object(original, padding_pool)

    manufacturer = FindObject(
        "ManufacturerDefinition",
        "GD_Currency.Manufacturers.Cash_Manufacturer",
    )
    inventory_template.Manufacturers = [(manufacturer, [()])]
    grade = inventory_template.Manufacturers[0].Grades[0]  # type: ignore
    grade.GradeModifiers = (1, None)
    grade.GameStageRequirement = (1, 100)
    grade.MinSpawnProbabilityModifier = (0.5, None, None, 1)
    grade.MaxSpawnProbabilityModifier = (1, None, None, 1)

    original = FindObject(
        "UsableItemDefinition", "GD_BuffDrinks.A_Item.BuffDrink_Toughness"
    )
    useitem_template = construct_object(original, "Hint_Item_Default")

    useitem_template.PickupLifeSpan = 0
    useitem_template.bPickupInBulk = False
    useitem_template.CalloutDefinition = None
    useitem_template.CustomPresentations = ()
    useitem_template.OnUseConstraints = ()

    original = FindObject(
        "InteractionIconDefinition",
        "GD_InteractionIcons.Default.Icon_DefaultPickUp",
    )
    useitem_template.PickupIconOverride = construct_object(
        original, "Icon_DismissHint"
    )
    set_command(useitem_template.PickupIconOverride, "Text", "Dismiss")

    original = FindObject(
        "BehaviorProviderDefinition",
        "GD_Currency.A_Item.Currency:BehaviorProviderDefinition_0",
    )
    useitem_bpd = construct_object(original, "Hint_BehaviorProviderDefinition")
    useitem_template.BehaviorProviderDefinition = useitem_bpd

    original = FindObject(
        "InventoryCardPresentationDefinition",
        "GD_InventoryPresentations.Definitions.Credits",
    )
    presentation_template = construct_object(original, "Hint_Presentation")

    custompresentation_template = construct_object(
        "AttributePresentationDefinition", "Hint_Presentation_Default"
    )
    custompresentation_template.BasePriority = 2.0
    custompresentation_template.bDontDisplayNumber = True
    custompresentation_template.bEnableTextColor = False

    useitem_behavior = construct_object(
        "Behavior_LocalCustomEvent", useitem_bpd
    )
    useitem_bpd.BehaviorSequences[0].BehaviorData2[
        0
    ].Behavior = useitem_behavior

    hintitem_mesh = FindObject(
        "StaticMesh", "prop_interactive.Meshes.DataRecorder_01_Active"
    )
    if BL2:
        duditem_mesh = FindObject(
            "StaticMesh", "Prop_Details.Meshes.BeerBottle"
        )
    elif TPS:
        LoadPackage("Spaceport_P")
        duditem_mesh = FindObject("StaticMesh", "Prop_Details.BeerBottle")
        if not duditem_mesh:
            raise Exception("Could not locate beer bottle for dud items")
        KeepAlive(duditem_mesh)

    hintitem_pickupflag = FindObject(
        "Texture2D", "fx_shared_items.Textures.ItemCards.sdu"
    )
    duditem_pickupflag = FindObject(
        "Texture2D", "fx_shared_items.Textures.ItemCards.Buff_Toughen-up"
    )

    padding.InventoryDefinition = construct_object(useitem_template, padding)
    padding.InventoryDefinition.PickupLifeSpan = 0.000001
    padding_pool.BalancedItems = ((None, padding, (1, None, None, 1), True),)


def Disable() -> None:
    RemoveHook(
        "WillowGame.Behavior_LocalCustomEvent.ApplyBehaviorToContext",
        "LootRandomizer",
    )


def UpdateHints() -> None:
    if useitem_template and seed.AppliedSeed:
        for location in seed.AppliedSeed.locations:
            location.update_hint()


def ResetDismissed() -> None:
    if useitem_template and seed.AppliedSeed:
        for location in seed.AppliedSeed.locations:
            location.toggle_hint(True)


def _Behavior_LocalCustomEvent(
    caller: UObject, _f: UFunction, params: FStruct
) -> bool:
    from . import items

    if caller is not useitem_behavior:
        return True

    matched_location = None

    hint_inventory = params.SelfObject.DefinitionData.BalanceDefinition
    for location in seed.AppliedSeed.locations:  # type: ignore
        if location.hint_inventory is hint_inventory:
            matched_location = location
            break

    if not matched_location:
        return False

    if (matched_location.item != items.DudItem) and (
        not options.HintTrainingSeen.CurrentValue
    ):
        show_dialog(
            "Item Hints",
            (
                "The object you just found is an item hint, indicating that the specified loot source "
                "does indeed drop loot in your seed.\n\n"
                "You can configure the amount of information provided by loot hints via "
                "Options > Mods > Loot Randomizer > Hint Display.\n\n"
                "To dismiss hints or duds for a given source, simply interact with them. You may reset "
                "your dismissed hints via\n"
                "Options > Mods > Loot Randomizer > Reset Dismissed Hints.\n\n"
            ),
            5,
        )
        options.HintTrainingSeen.CurrentValue = True
        options.SaveSettings()

    elif (matched_location.item == items.DudItem) and (
        not options.DudTrainingSeen.CurrentValue
    ):
        show_dialog(
            "Dud Items",
            (
                "The object you just found is a dud item, indicating that the specified loot "
                "source is included in your seed, but was not assigned an item.\n\n"
                "To dismiss hints or duds for a given source, simply interact with them. You may "
                "reset your dismissed hints via\n"
                "Options > Mods > Loot Randomizer > Reset Dismissed Hints.\n\n"
            ),
            5,
        )
        options.DudTrainingSeen.CurrentValue = True
        options.SaveSettings()

    else:
        matched_location.toggle_hint(False)

    return False
