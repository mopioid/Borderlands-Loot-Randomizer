from unrealsdk import FindObject, KeepAlive #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct  #type: ignore

from . import seed
from .defines import construct_object, set_command


inventory_template: UObject = None
useitem_template: UObject = None
presentation_template: UObject = None
useitem_behavior: UObject = None


def Enable() -> None:
    global inventory_template, useitem_template, presentation_template, useitem_behavior

    RunHook("WillowGame.Behavior_LocalCustomEvent.ApplyBehaviorToContext", "LootRandomizer", _Behavior_LocalCustomEvent)

    presentation_template = FindObject("InventoryCardPresentationDefinition", "GD_InventoryPresentations.Definitions.Credits")
    inventory_template = FindObject("InventoryBalanceDefinition", "LootRandomizer.Hint_Inventory_Default")
    if inventory_template:
        useitem_template = FindObject("UsableItemDefinition", "LootRandomizer.Hint_Item_Default")
        useitem_behavior = useitem_template.BehaviorProviderDefinition.BehaviorSequences[0].BehaviorData2[0].Behavior
        return

    original = FindObject("InventoryBalanceDefinition", "GD_ItemGrades.BuffDrink.ItemGrade_BuffDrink_Toughness")
    inventory_template = construct_object(original, "Hint_Inventory_Default")
    KeepAlive(inventory_template)

    inventory_template.Manufacturers = ((
        FindObject("ManufacturerDefinition", "GD_Currency.Manufacturers.Cash_Manufacturer"),
    ),)

    original = FindObject("UsableItemDefinition", "GD_BuffDrinks.A_Item.BuffDrink_Toughness")
    useitem_template = construct_object(original, "Hint_Item_Default")
    KeepAlive(useitem_template)

    useitem_template.bPickupInBulk = False
    useitem_template.CalloutDefinition = None
    useitem_template.CustomPresentations = ()
    useitem_template.OnUseConstraints = ()
    useitem_template.NonCompositeStaticMesh = FindObject("StaticMesh", "prop_interactive.Meshes.DataRecorder_01_Active")
    useitem_template.PickupFlagIcon = FindObject("Texture2D", "fx_shared_items.Textures.ItemCards.sdu")
    # useitem_template.LootBeamColorOverride = (152, 152, 188, 255)

    original = FindObject("InteractionIconDefinition", "GD_InteractionIcons.Default.Icon_DefaultPickUp")
    useitem_template.PickupIconOverride = construct_object(original, "Icon_DismissHint")
    set_command(useitem_template.PickupIconOverride, "Text", "Dismiss")

    original = FindObject("BehaviorProviderDefinition", "GD_Currency.A_Item.Currency:BehaviorProviderDefinition_0")
    useitem_bpd = construct_object(original, "Hint_BehaviorProviderDefinition")
    useitem_template.BehaviorProviderDefinition = useitem_bpd

    useitem_behavior = construct_object("Behavior_LocalCustomEvent", useitem_bpd)
    useitem_bpd.BehaviorSequences[0].BehaviorData2[0].Behavior = useitem_behavior


def Disable() -> None:
    RemoveHook("WillowGame.Behavior_LocalCustomEvent.ApplyBehaviorToContext", "LootRandomizer")


def UpdateHints() -> None:
    for location in seed.Locations:
        location.update_hint()


def _Behavior_LocalCustomEvent(caller: UObject, function: UFunction, params: FStruct) -> bool:
    if caller is not useitem_behavior:
        return True

    hint_inventory = params.SelfObject.DefinitionData.BalanceDefinition
    for location in seed.Locations:
        if location.hint_inventory is hint_inventory:
            location.update_hint(False)
    return False
