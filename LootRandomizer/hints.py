from unrealsdk import ConstructObject, FindObject, GetEngine, KeepAlive #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct  #type: ignore

import enum

from typing import List, Tuple


# _inventory_template: UObject = None #InventoryBalanceDefinition
# _useitem_template: UObject = None #UsableItemDefinition
# _presentation_template: UObject = None #InventoryCardPresentationDefinition


def _set_command(uobject: UObject, attribute: str, value: str):
    GetEngine().GamePlayers[0].Actor.ConsoleCommand(f"set {UObject.PathName(uobject)} {attribute} {value}")


class Hint(str, enum.Enum):
    ClassMod = "Class Mod"

    PurpleShield = "Purple Shield"
    UniqueShield = "Unique Shield"
    LegendaryShield = "Legendary Shield"

    PurpleRelic = "Purple Relic"
    UniqueRelic = "Unique Relic"
    EtechRelic = "E-tech Relic"

    PurpleGrenade = "Purple Grenade"
    UniqueGrenade = "Unique Grenade"
    LegendaryGrenade = "Legendary Grenade"

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

    PearlescentWeapon = "Pearlescent Weapon"

    SeraphItem = "Seraph Item"
    SeraphWeapon = "Seraph Weapon"

    EffervescentItem = "Effervescent Item"
    EffervescentWeapon = "Effervescent Weapon"


def ConstructInventory(name: str) -> UObject: #InventoryBalanceDefinition
    original = FindObject("InventoryBalanceDefinition", "GD_ItemGrades.BuffDrink.ItemGrade_BuffDrink_Toughness")
    inventory = ConstructObject(original.Class, Template=original)

    inventory.Manufacturers = ((FindObject("ManufacturerDefinition", "GD_Currency.Manufacturers.Cash_Manufacturer"),),)

    useitem = ConstructObject(inventory.InventoryDefinition.Class, Template=inventory.InventoryDefinition)
    inventory.InventoryDefinition = useitem

    useitem.bPickupInBulk = False
    useitem.BehaviorProviderDefinition = None
    useitem.CalloutDefinition = None
    useitem.CustomPresentations = []
    useitem.OnUseConstraints = []
    useitem.NonCompositeStaticMesh = FindObject("StaticMesh", "prop_interactive.Meshes.DataRecorder_01_Active")
    useitem.PickupFlagIcon = FindObject("Texture2D", "fx_shared_items.Textures.ItemCards.sdu")
    # useitem.LootBeamColorOverride = (152, 152, 188, 255)
    _set_command(useitem, "ItemName", name + "?")

    original = FindObject("InteractionIconDefinition", "GD_InteractionIcons.Default.Icon_DefaultPickUp")
    useitem.PickupIconOverride = ConstructObject(original.Class, Template=original)
    _set_command(useitem.PickupIconOverride, "Text", "Dismiss")

    return inventory


def ConstructPresentation(text: str) -> UObject: #InventoryCardPresentationDefinition
    original = FindObject("InventoryCardPresentationDefinition", "GD_InventoryPresentations.Definitions.Credits")
    presentation = ConstructObject(original.Class, Template=original)

    _set_command(presentation, "DescriptionLocReference", text)
    # _set_command(presentation, "ZippyFrame", "personal")

    return presentation



"""
give each ItemPool a `hint` attribute

`Enemy`s request `ItemPool`s to generate ItemPoolDefinitions:
    self.item.construct_pool(name=self.name, rarity=10)

`ItemPool` then constructs the ItemPoolDefinitions and fills its BalancedItems such that it drops
the item with a (1/rarity) chance, and the hint item with a (rarity-1/rarity) chance
    
    
junk color: (152, 152, 188, 255)
junk mesh: Prop_Pickups.Meshes.PowerShotBuffCan
junk icon: fx_shared_items.Textures.ItemCards.Buff_Toughen-up
"""