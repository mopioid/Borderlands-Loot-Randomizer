from .defines import Tag, Hint
from .items import Character, ItemPool, Item
from .items import PurpleRelic, BlueAlignmentCOM, PurpleAlignmentCOM, LegendaryCOM

Items = (
    ItemPool("Blue Class Mod", Hint.ClassMod,
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_03_Rare", Character.Assassin),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_03_Rare", Character.Mercenary),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_03_Rare", Character.Siren),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_03_Rare", Character.Soldier),
        Item("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_03_Rare", Character.Psycho),
        Item("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_03_Rare", Character.Mechromancer),
    ),
    ItemPool("Purple Class Mod", Hint.ClassMod,
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_04_VeryRare", Character.Assassin),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_04_VeryRare", Character.Mercenary),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_04_VeryRare", Character.Siren),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_04_VeryRare", Character.Soldier),
        Item("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_04_VeryRare", Character.Psycho),
        Item("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_04_VeryRare", Character.Mechromancer),
    ),
    ItemPool("Blue Alignment Class Mod", Hint.ClassMod,
        BlueAlignmentCOM("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Assassin", Character.Assassin),
        BlueAlignmentCOM("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Merc", Character.Mercenary),
        BlueAlignmentCOM("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Siren", Character.Siren),
        BlueAlignmentCOM("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Soldier", Character.Soldier),
        BlueAlignmentCOM("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Psycho", Character.Psycho),
        BlueAlignmentCOM("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Mechromancer", Character.Mechromancer),
    ),
    ItemPool("Purple Alignment Class Mod", Hint.ClassMod,
        PurpleAlignmentCOM("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Assassin", Character.Assassin),
        PurpleAlignmentCOM("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Merc", Character.Mercenary),
        PurpleAlignmentCOM("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Siren", Character.Siren),
        PurpleAlignmentCOM("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Soldier", Character.Soldier),
        PurpleAlignmentCOM("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Psycho", Character.Psycho),
        PurpleAlignmentCOM("GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Mechromancer", Character.Mechromancer),
    ),
    ItemPool("Legendary Hunter/Berserker/Siren/Soldier/Psycho/Mechromancer", Hint.ClassMod,
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_05_Legendary", Character.Assassin),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_05_Legendary", Character.Mercenary),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_05_Legendary", Character.Siren),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_05_Legendary", Character.Soldier),
        Item("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_05_Legendary", Character.Psycho),
        Item("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_05_Legendary", Character.Mechromancer),
    ),
    ItemPool("Slayer Of Terramorphous", Hint.ClassMod,
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_06_SlayerOfTerramorphous", Character.Assassin),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_06_SlayerOfTerramorphous", Character.Mercenary),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_06_SlayerOfTerramorphous", Character.Siren),
        Item("GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_06_SlayerOfTerramorphous", Character.Soldier),
        Item("GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_06_SlayerOfTerramorphous", Character.Psycho),
        Item("GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_06_SlayerOfTerramorphous", Character.Mechromancer),
    ),
    ItemPool("Legendary Killer/Gunzerker/Binder/Engineer/Sickle/Anarchist", Hint.ClassMod,
        LegendaryCOM("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Assassin_05_Legendary", 0, Character.Assassin, Tag.DigistructPeak),
        LegendaryCOM("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Merc_05_Legendary", 0, Character.Mercenary, Tag.DigistructPeak),
        LegendaryCOM("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Siren_05_Legendary", 0, Character.Siren, Tag.DigistructPeak),
        LegendaryCOM("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Soldier_05_Legendary", 0, Character.Soldier, Tag.DigistructPeak),
        LegendaryCOM("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Psycho_05_Legendary", 0, Character.Psycho, Tag.DigistructPeak),
        LegendaryCOM("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Mechromancer_05_Legendary", 0, Character.Mechromancer, Tag.DigistructPeak),
    ),
    ItemPool("Legendary Ninja/Hoarder/Cat/Pointman/Torch/Catalyst", Hint.ClassMod,
        LegendaryCOM("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Assassin_05_Legendary", 1, Character.Assassin, Tag.DigistructPeak),
        LegendaryCOM("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Merc_05_Legendary", 1, Character.Mercenary, Tag.DigistructPeak),
        LegendaryCOM("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Siren_05_Legendary", 1, Character.Siren, Tag.DigistructPeak),
        LegendaryCOM("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Soldier_05_Legendary", 1, Character.Soldier, Tag.DigistructPeak),
        LegendaryCOM("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Psycho_05_Legendary", 1, Character.Psycho, Tag.DigistructPeak),
        LegendaryCOM("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Mechromancer_05_Legendary", 1, Character.Mechromancer, Tag.DigistructPeak),
    ),
    ItemPool("Legendary Sniper/Titan/Nurse/Ranger/Reaper/Roboteer", Hint.ClassMod,
        LegendaryCOM("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Assassin_05_Legendary", 2, Character.Assassin, Tag.DigistructPeak),
        LegendaryCOM("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Merc_05_Legendary", 2, Character.Mercenary, Tag.DigistructPeak),
        LegendaryCOM("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Siren_05_Legendary", 2, Character.Siren, Tag.DigistructPeak),
        LegendaryCOM("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Soldier_05_Legendary", 2, Character.Soldier, Tag.DigistructPeak),
        LegendaryCOM("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Psycho_05_Legendary", 2, Character.Psycho, Tag.DigistructPeak),
        LegendaryCOM("GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Mechromancer_05_Legendary", 2, Character.Mechromancer, Tag.DigistructPeak),
    ),

    ItemPool("Aggression Relic", Hint.PurpleRelic,
        PurpleRelic("GD_Artifacts.A_Item.A_AggressionA_Rare"),
        PurpleRelic("GD_Artifacts.A_Item.A_AggressionB_Rare"),
        PurpleRelic("GD_Artifacts.A_Item.A_AggressionC_Rare"),
        PurpleRelic("GD_Artifacts.A_Item.A_AggressionD_Rare"),
        PurpleRelic("GD_Artifacts.A_Item.A_AggressionE_Rare"),
        PurpleRelic("GD_Artifacts.A_Item.A_AggressionF_Rare"),
    ),
    ItemPool("Allegiance Relic", Hint.PurpleRelic,
        PurpleRelic("GD_Artifacts.A_Item.A_AllegianceA_Rare"),
        PurpleRelic("GD_Artifacts.A_Item.A_AllegianceB_Rare"),
        PurpleRelic("GD_Artifacts.A_Item.A_AllegianceC_Rare"),
        PurpleRelic("GD_Artifacts.A_Item.A_AllegianceD_Rare"),
        PurpleRelic("GD_Artifacts.A_Item.A_AllegianceE_Rare"),
        PurpleRelic("GD_Artifacts.A_Item.A_AllegianceF_Rare"),
        PurpleRelic("GD_Artifacts.A_Item.A_AllegianceG_Rare"),
        PurpleRelic("GD_Artifacts.A_Item.A_AllegianceH_Rare"),
    ),
    ItemPool("Elemental Relic", Hint.PurpleRelic,
        PurpleRelic("GD_Artifacts.A_Item.A_Elemental_Rare", 2.0),
        PurpleRelic("GD_Artifacts.A_Item.A_Elemental_Status_Rare", 3.0),
    ),
    ItemPool("Proficiency Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_Proficiency_Rare")),
    ItemPool("Protection Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_Protection_Rare")),
    ItemPool("Resistance Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_Resistance_Rare")),
    ItemPool("Stockpile Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_Stockpile_Rare")),
    ItemPool("Strength Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_Strength_Rare")),
    ItemPool("Tenacity Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_Tenacity_Rare")),
    ItemPool("Vitality Relic", Hint.PurpleRelic, PurpleRelic("GD_Artifacts.A_Item.A_Vitality_Rare")),

    ItemPool("The Afterburner", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_Afterburner")),
    ItemPool("Deputy's Badge", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_Deputy")),
    ItemPool("Moxxi's Endowment", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_Endowment")),
    ItemPool("Lucrative Opportunity", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_Opportunity")),
    ItemPool("Sheriff's Badge", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_Sheriff")),
    ItemPool("Blood of Terramorphous", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_Terramorphous")),
    ItemPool("Vault Hunter's Relic", Hint.UniqueRelic, Item("GD_Artifacts.A_Item_Unique.A_VaultHunter")),

    ItemPool("Fire Burst/Tesla/Corrosive Cloud", Hint.PurpleGrenade, Item("GD_GrenadeMods.A_Item.GM_AreaEffect_4_VeryRare")),
    ItemPool("Bouncing Betty", Hint.PurpleGrenade, Item("GD_GrenadeMods.A_Item.GM_BouncingBetty_4_VeryRare")),
    ItemPool("MIRV", Hint.PurpleGrenade, Item("GD_GrenadeMods.A_Item.GM_Mirv_4_VeryRare")),
    ItemPool("Singularity", Hint.PurpleGrenade, Item("GD_GrenadeMods.A_Item.GM_Singularity_4_VeryRare")),
    ItemPool("Grenade", Hint.PurpleGrenade, Item("GD_GrenadeMods.A_Item.GM_Standard_4_VeryRare")),
    ItemPool("Transfusion", Hint.PurpleGrenade, Item("GD_GrenadeMods.A_Item.GM_Transfusion_4_VeryRare")),

    ItemPool("Fuster Cluck", Hint.UniqueGrenade, Item("GD_GrenadeMods.A_Item_Custom.GM_FusterCluck")),
    ItemPool("Kiss of Death", Hint.UniqueGrenade, Item("GD_GrenadeMods.A_Item_Custom.GM_KissOfDeath")),
    ItemPool("Sky Rocket", Hint.UniqueGrenade, Item("GD_GrenadeMods.A_Item_Custom.GM_SkyRocket")),
    ItemPool("Breath of Terramorphous", Hint.UniqueGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_FlameSpurt")),

    ItemPool("Bonus Package", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_BonusPackage")),
    ItemPool("Bouncing Bonny", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_BouncingBonny")),
    ItemPool("Fastball", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_Fastball")),
    ItemPool("Fire Bee", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_FireBee")),
    ItemPool("Leech", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_Leech")),
    ItemPool("Nasty Surprise", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_NastySurprise")),
    ItemPool("Pandemic", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_Pandemic")),
    ItemPool("Quasar", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_Quasar")),
    ItemPool("Rolling Thunder", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_RollingThunder")),
    ItemPool("Storm Front", Hint.LegendaryGrenade, Item("GD_GrenadeMods.A_Item_Legendary.GM_StormFront")),

    ItemPool("Shield", Hint.PurpleShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_04_VeryRare")),
    ItemPool("Absorb Shield", Hint.PurpleShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_04_VeryRare")),
    ItemPool("Adaptive Shield", Hint.PurpleShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_04_VeryRare")),
    ItemPool("Amplify Shield", Hint.PurpleShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Impact_04_VeryRare")),
    ItemPool("Booster Shield", Hint.PurpleShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_04_VeryRare")),
    ItemPool("Maylay Shield", Hint.PurpleShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_04_VeryRare")),
    ItemPool("Nova Shield", Hint.PurpleShield,
        Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Explosive_04_VeryRare"),
        Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Fire_04_VeryRare"),
        Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Shock_04_VeryRare"),
        Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Acid_04_VeryRare"),
    ),
    ItemPool("Spike Shield", Hint.PurpleShield,
        Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Explosive_04_VeryRare"),
        Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Fire_04_VeryRare"),
        Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Shock_04_VeryRare"),
        Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Acid_04_VeryRare"),
    ),
    ItemPool("Turtle Shield", Hint.PurpleShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Juggernaut_04_VeryRare")),

    ItemPool("1340 Shield", Hint.UniqueShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_1340")),
    ItemPool("Aequitas", Hint.UniqueShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_Equitas")),
    ItemPool("Pot O' Gold", Hint.UniqueShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_PotOGold")),
    ItemPool("Deadly Bloom", Hint.UniqueShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Explosive_DeadlyBloom")),
    ItemPool("Order", Hint.UniqueShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_Order")),
    ItemPool("Cracked Sash", Hint.UniqueShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_CrackedSash")),
    ItemPool("Love Thumper", Hint.UniqueShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_04_LoveThumper")),

    ItemPool("The Sham", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryNormal")),
    ItemPool("The Transformer", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryShock")),
    ItemPool("Whisky Tango Foxtrot", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_05_Legendary")),
    ItemPool("Neogenator", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_05_Legendary")),
    ItemPool("The Bee", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Impact_05_Legendary")),
    ItemPool("Fabled Tortoise", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Juggernaut_05_Legendary")),
    ItemPool("Flame of the Firehawk", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Phoenix")),
    ItemPool("Black Hole", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Singularity")),
    ItemPool("Hide of Terramorphous", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_ThresherRaid")),
    ItemPool("Impaler", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Acid_05_Legendary")),
    ItemPool("The Cradle", Hint.LegendaryShield, Item("GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_05_Legendary")),

    ItemPool("Bandit Assault Rifle", Hint.PurpleAR,
        Item("GD_Aster_Weapons.AssaultRifles.AR_Bandit_4_Quartz", tags=Tag.DragonKeep),
        Item("GD_Weap_AssaultRifle.A_Weapons.AR_Bandit_5_Alien", 1/6),
        fallback=Item("GD_Weap_AssaultRifle.A_Weapons.AR_Bandit_4_VeryRare"),
    ),
    ItemPool("Dahl Assault Rifle", Hint.PurpleAR,
        Item("GD_Aster_Weapons.AssaultRifles.AR_Dahl_4_Emerald", tags=Tag.DragonKeep),
        Item("GD_Weap_AssaultRifle.A_Weapons.AR_Dahl_5_Alien", 1/6),
        fallback=Item("GD_Weap_AssaultRifle.A_Weapons.AR_Dahl_4_VeryRare"),
    ),
    ItemPool("Jakobs Assault Rifle", Hint.PurpleAR,
        Item("GD_Aster_Weapons.AssaultRifles.AR_Jakobs_4_Citrine", tags=Tag.DragonKeep),
        fallback=Item("GD_Weap_AssaultRifle.A_Weapons.AR_Jakobs_4_VeryRare"),
    ),
    ItemPool("Torgue Assault Rifle", Hint.PurpleAR,
        Item("GD_Aster_Weapons.AssaultRifles.AR_Torgue_4_Rock", tags=Tag.DragonKeep),
        fallback=Item("GD_Weap_AssaultRifle.A_Weapons.AR_Torgue_4_VeryRare"),
    ),
    ItemPool("Vladof Assault Rifle", Hint.PurpleAR,
        Item("GD_Aster_Weapons.AssaultRifles.AR_Vladof_4_Garnet", tags=Tag.DragonKeep),
        Item("GD_Weap_AssaultRifle.A_Weapons.AR_Vladof_5_Alien", 1/6),
        fallback=Item("GD_Weap_AssaultRifle.A_Weapons.AR_Vladof_4_VeryRare"),
    ),

    ItemPool("Bandit Rocket Launcher", Hint.PurpleLauncher,
        Item("GD_Weap_Launchers.A_Weapons.RL_Bandit_4_VeryRare"),
        Item("GD_Weap_Launchers.A_Weapons.RL_Bandit_5_Alien", 1/5),
    ),
    ItemPool("Tediore Rocket Launcher", Hint.PurpleLauncher,
        Item("GD_Weap_Launchers.A_Weapons.RL_Tediore_4_VeryRare"),
        Item("GD_Weap_Launchers.A_Weapons.RL_Tediore_5_Alien", 1/5),
    ),
    ItemPool("Vladof Rocket Launcher", Hint.PurpleLauncher,
        Item("GD_Weap_Launchers.A_Weapons.RL_Vladof_4_VeryRare"),
        Item("GD_Weap_Launchers.A_Weapons.RL_Vladof_5_Alien", 1/5),
    ),
    ItemPool("Maliwan Rocket Launcher", Hint.PurpleLauncher,
        Item("GD_Weap_Launchers.A_Weapons.RL_Maliwan_4_VeryRare"),
        Item("GD_Weap_Launchers.A_Weapons.RL_Maliwan_5_Alien", 1/5),
    ),
    ItemPool("Torgue Rocket Launcher", Hint.PurpleLauncher, Item("GD_Weap_Launchers.A_Weapons.RL_Torgue_4_VeryRare")),

    ItemPool("Bandit Pistol", Hint.PurplePistol,
        Item("GD_Aster_Weapons.Pistols.Pistol_Bandit_4_Quartz", tags=Tag.DragonKeep),
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Bandit_5_Alien", 1/4),
        fallback=Item("GD_Weap_Pistol.A_Weapons.Pistol_Bandit_4_VeryRare"),
    ),
    ItemPool("Tediore Pistol", Hint.PurplePistol,
        Item("GD_Aster_Weapons.Pistols.Pistol_Tediore_4_CubicZerconia", tags=Tag.DragonKeep),
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Tediore_5_Alien", 1/4),
        fallback=Item("GD_Weap_Pistol.A_Weapons.Pistol_Tediore_4_VeryRare"),
    ),
    ItemPool("Dahl Pistol", Hint.PurplePistol,
        Item("GD_Aster_Weapons.Pistols.Pistol_Dahl_4_Emerald", tags=Tag.DragonKeep),
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Dahl_5_Alien", 1/4),
        fallback=Item("GD_Weap_Pistol.A_Weapons.Pistol_Dahl_4_VeryRare"),
    ),
    ItemPool("Vladof Pistol", Hint.PurplePistol,
        Item("GD_Aster_Weapons.Pistols.Pistol_Vladof_4_Garnet", tags=Tag.DragonKeep),
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Vladof_5_Alien", 1/4),
        fallback=Item("GD_Weap_Pistol.A_Weapons.Pistol_Vladof_4_VeryRare"),
    ),
    ItemPool("Torgue Pistol", Hint.PurplePistol,
        Item("GD_Aster_Weapons.Pistols.Pistol_Torgue_4_Rock", tags=Tag.DragonKeep),
        fallback=Item("GD_Weap_Pistol.A_Weapons.Pistol_Torgue_4_VeryRare"),
    ),
    ItemPool("Maliwan Pistol", Hint.PurplePistol,
        Item("GD_Aster_Weapons.Pistols.Pistol_Maliwan_4_Aquamarine", tags=Tag.DragonKeep),
        Item("GD_Weap_Pistol.A_Weapons.Pistol_Maliwan_5_Alien", 1/4),
        fallback=Item("GD_Weap_Pistol.A_Weapons.Pistol_Maliwan_4_VeryRare"),
    ),
    ItemPool("Jakobs Pistol", Hint.PurplePistol,
        Item("GD_Aster_Weapons.Pistols.Pistol_Jakobs_4_Citrine", tags=Tag.DragonKeep),
        fallback=Item("GD_Weap_Pistol.A_Weapons.Pistol_Jakobs_4_VeryRare"),
    ),
    ItemPool("Hyperion Pistol", Hint.PurplePistol,
        Item("GD_Aster_Weapons.Pistols.Pistol_Hyperion_4_Diamond", tags=Tag.DragonKeep),
        fallback=Item("GD_Weap_Pistol.A_Weapons.Pistol_Hyperion_4_VeryRare"),
        # Item("GD_Weap_Pistol.A_Weapons.Pistol_Hyperion_5_Alien", 1/4),
    ),

    ItemPool("Bandit Shotgun", Hint.PurpleShotgun,
        Item("GD_Aster_Weapons.Shotguns.SG_Bandit_4_Quartz", tags=Tag.DragonKeep),
        Item("GD_Weap_Shotgun.A_Weapons.SG_Bandit_5_Alien", 1/5),
        fallback=Item("GD_Weap_Shotgun.A_Weapons.SG_Bandit_4_VeryRare"),
    ),
    ItemPool("Tediore Shotgun", Hint.PurpleShotgun,
        Item("GD_Aster_Weapons.Shotguns.SG_Tediore_4_CubicZerconia", tags=Tag.DragonKeep),
        Item("GD_Weap_Shotgun.A_Weapons.SG_Tediore_5_Alien", 1/5),
        fallback=Item("GD_Weap_Shotgun.A_Weapons.SG_Tediore_4_VeryRare"),
    ),
    ItemPool("Torgue Shotgun", Hint.PurpleShotgun,
        Item("GD_Aster_Weapons.Shotguns.SG_Torgue_4_Rock", tags=Tag.DragonKeep),
        fallback=Item("GD_Weap_Shotgun.A_Weapons.SG_Torgue_4_VeryRare"),
    ),
    ItemPool("Jakobs Shotgun", Hint.PurpleShotgun,
        Item("GD_Aster_Weapons.Shotguns.SG_Jakobs_4_Citrine", tags=Tag.DragonKeep),
        fallback=Item("GD_Weap_Shotgun.A_Weapons.SG_Jakobs_4_VeryRare"),
    ),
    ItemPool("Hyperion Shotgun", Hint.PurpleShotgun,
        Item("GD_Aster_Weapons.Shotguns.SG_Hyperion_4_Diamond", tags=Tag.DragonKeep),
        Item("GD_Weap_Shotgun.A_Weapons.SG_Hyperion_5_Alien", 1/5),
        fallback=Item("GD_Weap_Shotgun.A_Weapons.SG_Hyperion_4_VeryRare"),
    ),

    ItemPool("Bandit SMG", Hint.PurpleSMG,
        Item("GD_Aster_Weapons.SMGs.SMG_Bandit_4_Quartz", tags=Tag.DragonKeep),
        Item("GD_Weap_SMG.A_Weapons.SMG_Bandit_5_Alien", 1/5),
        fallback=Item("GD_Weap_SMG.A_Weapons.SMG_Bandit_4_VeryRare"),
    ),
    ItemPool("Tediore SMG", Hint.PurpleSMG,
        Item("GD_Aster_Weapons.SMGs.SMG_Tediore_4_CubicZerconia", tags=Tag.DragonKeep),
        Item("GD_Weap_SMG.A_Weapons.SMG_Tediore_5_Alien", 1/5),
        fallback=Item("GD_Weap_SMG.A_Weapons.SMG_Tediore_4_VeryRare"),
    ),
    ItemPool("Dahl SMG", Hint.PurpleSMG,
        Item("GD_Aster_Weapons.SMGs.SMG_Dahl_4_Emerald", tags=Tag.DragonKeep),
        Item("GD_Weap_SMG.A_Weapons.SMG_Dahl_5_Alien", 1/5),
        fallback=Item("GD_Weap_SMG.A_Weapons.SMG_Dahl_4_VeryRare"),
    ),
    ItemPool("Maliwan SMG", Hint.PurpleSMG,
        Item("GD_Aster_Weapons.SMGs.SMG_Maliwan_4_Aquamarine", tags=Tag.DragonKeep),
        Item("GD_Weap_SMG.A_Weapons.SMG_Maliwan_5_Alien", 1/5),
        fallback=Item("GD_Weap_SMG.A_Weapons.SMG_Maliwan_4_VeryRare"),
    ),
    ItemPool("Hyperion SMG", Hint.PurpleSMG,
        Item("GD_Aster_Weapons.SMGs.SMG_Hyperion_4_Diamond", tags=Tag.DragonKeep),
        Item("GD_Weap_SMG.A_Weapons.SMG_Hyperion_5_Alien", 1/5),
        fallback=Item("GD_Weap_SMG.A_Weapons.SMG_Hyperion_4_VeryRare"),
    ),

    ItemPool("Dahl Sniper Rifle", Hint.PurpleSniper,
        Item("GD_Aster_Weapons.Snipers.SR_Dahl_4_Emerald", tags=Tag.DragonKeep),
        Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Dahl_5_Alien", 1/5),
        fallback=Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Dahl_4_VeryRare"),
    ),
    ItemPool("Vladof Sniper Rifle", Hint.PurpleSniper,
        Item("GD_Aster_Weapons.Snipers.SR_Vladof_4_Garnet", tags=Tag.DragonKeep),
        Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Vladof_5_Alien", 1/5),
        fallback=Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Vladof_4_VeryRare"),
    ),
    ItemPool("Maliwan Sniper Rifle", Hint.PurpleSniper,
        Item("GD_Aster_Weapons.Snipers.SR_Maliwan_4_Aquamarine", tags=Tag.DragonKeep),
        Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Maliwan_5_Alien", 1/5),
        fallback=Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Maliwan_4_VeryRare"),
    ),
    ItemPool("Jakobs Sniper Rifle", Hint.PurpleSniper,
        Item("GD_Aster_Weapons.Snipers.SR_Jakobs_4_Citrine", tags=Tag.DragonKeep),
        fallback=Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Jakobs_4_VeryRare"),
    ),
    ItemPool("Hyperion Sniper Rifle", Hint.PurpleSniper,
        Item("GD_Aster_Weapons.Snipers.SR_Hyperion_4_Diamond", tags=Tag.DragonKeep),
        Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Hyperion_5_Alien", 1/5),
        fallback=Item("GD_Weap_SniperRifles.A_Weapons.Sniper_Hyperion_4_VeryRare"),
    ),

    ItemPool("Lascaux", Hint.UniqueSMG, Item("GD_Weap_SMG.A_Weapons_Unique.SMG_Dahl_3_Lascaux")),
    ItemPool("Bad Touch", Hint.UniqueSMG, Item("GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_BadTouch")),
    ItemPool("Good Touch", Hint.UniqueSMG, Item("GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_GoodTouch")),
    ItemPool("Commerce", Hint.UniqueSMG, Item("GD_Weap_SMG.A_Weapons_Unique.SMG_Hyperion_3_Commerce")),
    ItemPool("Bone Shredder", Hint.UniqueSMG, Item("GD_Weap_SMG.A_Weapons_Unique.SMG_Bandit_3_BoneShredder")),
    ItemPool("Chulainn", Hint.UniqueSMG, Item("GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_Chulainn")),
    ItemPool("Bane", Hint.UniqueSMG, Item("GD_Weap_SMG.A_Weapons_Unique.SMG_Hyperion_3_Bane")),

    ItemPool("Gwen's Head", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_GwensHead")),
    ItemPool("Judge", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Judge")),
    ItemPool("Tinderbox", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Bandit_3_Tenderbox")),
    ItemPool("Law", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Law")),
    ItemPool("Teapot", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_Teapot")),
    ItemPool("Fibber", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_Fibber")),
    ItemPool("Rubi", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Maliwan_3_Rubi")),
    ItemPool("Veritas", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Vladof_3_Veritas")),
    ItemPool("Dahlminator", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_Dahlminator")),
    ItemPool("Lady Fist", Hint.UniquePistol, Item("GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_LadyFist")),

    ItemPool("Fremington's Edge", Hint.UniqueSniper, Item("GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_FremingtonsEdge")),
    ItemPool("Buffalo", Hint.UniqueSniper, Item("GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Jakobs_3_Buffalo")),
    ItemPool("Trespasser", Hint.UniqueSniper, Item("GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Jakobs_3_Tresspasser")),
    ItemPool("Sloth", Hint.UniqueSniper, Item("GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Dahl_3_Sloth")),
    ItemPool("Morningstar", Hint.UniqueSniper, Item("GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_Morningstar")),
    ItemPool("Chère-amie", Hint.UniqueSniper, Item("GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Maliwan_3_ChereAmie")),

    ItemPool("Dog", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_Dog")),
    ItemPool("Teeth of Terramorphous", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_Teeth")),
    ItemPool("Blockhead", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Tediore_3_Blockhead")),
    ItemPool("Landscaper", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Torgue_3_Landscaper")),
    ItemPool("Triquetra", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_3_Triquetra")),
    ItemPool("Heart Breaker", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_HeartBreaker")),
    ItemPool("Octo", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Tediore_3_Octo")),
    ItemPool("RokSalt", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_RokSalt")),
    ItemPool("Shotgun 1340", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_Shotgun1340")),
    ItemPool("Tidal Wave", Hint.UniqueShotgun, Item("GD_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_3_TidalWave")),

    ItemPool("Hive", Hint.UniqueLauncher, Item("GD_Weap_Launchers.A_Weapons_Unique.RL_Maliwan_3_TheHive")),
    ItemPool("Creamer", Hint.UniqueLauncher, Item("GD_Weap_Launchers.A_Weapons_Unique.RL_Torgue_3_Creamer")),
    ItemPool("Roaster", Hint.UniqueLauncher, Item("GD_Weap_Launchers.A_Weapons_Unique.RL_Bandit_3_Roaster")),

    ItemPool("Hail", Hint.UniqueAR, Item("GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Vladof_3_Hail")),
    ItemPool("Scorpio", Hint.UniqueAR, Item("GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Dahl_3_Scorpio")),
    ItemPool("Evil Smasher", Hint.UniqueAR, Item("GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Torgue_3_EvilSmasher")),
    ItemPool("Stomper", Hint.UniqueAR, Item("GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Jakobs_3_Stomper")),

    ItemPool("Sledge's Shotgun", Hint.LegendaryShotgun, Item("GD_Weap_Shotgun.A_Weapons_Legendary.SG_Bandit_5_SledgesShotgun")),
    ItemPool("Striker", Hint.LegendaryShotgun, Item("GD_Weap_Shotgun.A_Weapons_Legendary.SG_Jakobs_5_Striker")),
    ItemPool("Deliverance", Hint.LegendaryShotgun, Item("GD_Weap_Shotgun.A_Weapons_Legendary.SG_Tediore_5_Deliverance")),
    ItemPool("Flakker", Hint.LegendaryShotgun, Item("GD_Weap_Shotgun.A_Weapons_Legendary.SG_Torgue_5_Flakker")),
    ItemPool("Conference Call", Hint.LegendaryShotgun, Item("GD_Weap_Shotgun.A_Weapons_Legendary.SG_Hyperion_5_ConferenceCall")),

    ItemPool("Nukem", Hint.LegendaryLauncher, Item("GD_Weap_Launchers.A_Weapons_Legendary.RL_Torgue_5_Nukem")),
    ItemPool("Pyrophobia", Hint.LegendaryLauncher, Item("GD_Weap_Launchers.A_Weapons_Legendary.RL_Maliwan_5_Pyrophobia")),
    ItemPool("Bunny", Hint.LegendaryLauncher, Item("GD_Weap_Launchers.A_Weapons_Legendary.RL_Tediore_5_Bunny")),
    ItemPool("Badaboom", Hint.LegendaryLauncher, Item("GD_Weap_Launchers.A_Weapons_Legendary.RL_Bandit_5_BadaBoom")),
    ItemPool("Mongol", Hint.LegendaryLauncher, Item("GD_Weap_Launchers.A_Weapons_Legendary.RL_Vladof_5_Mongol")),
    ItemPool("Norfleet", Hint.LegendaryLauncher, Item("GD_Weap_Launchers.A_Weapons_Unique.RL_Maliwan_Alien_Norfleet")),

    ItemPool("Bitch", Hint.LegendarySMG, Item("GD_Weap_SMG.A_Weapons_Legendary.SMG_Hyperion_5_Bitch")),
    ItemPool("Emperor", Hint.LegendarySMG, Item("GD_Weap_SMG.A_Weapons_Legendary.SMG_Dahl_5_Emperor")),
    ItemPool("Baby Maker", Hint.LegendarySMG, Item("GD_Weap_SMG.A_Weapons_Legendary.SMG_Tediore_5_BabyMaker")),
    ItemPool("Hellfire", Hint.LegendarySMG, Item("GD_Weap_SMG.A_Weapons_Legendary.SMG_Maliwan_5_HellFire")),
    ItemPool("Slagga", Hint.LegendarySMG, Item("GD_Weap_SMG.A_Weapons_Legendary.SMG_Bandit_5_Slagga")),

    ItemPool("Thunderball Fists", Hint.LegendaryPistol, Item("GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Maliwan_5_ThunderballFists")),
    ItemPool("Hornet", Hint.LegendaryPistol, Item("GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Dahl_5_Hornet")),
    ItemPool("Gub", Hint.LegendaryPistol, Item("GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Bandit_5_Gub")),
    ItemPool("Maggie", Hint.LegendaryPistol, Item("GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Jakobs_5_Maggie")),
    ItemPool("Infinity", Hint.LegendaryPistol, Item("GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Vladof_5_Infinity")),
    ItemPool("Gunerang", Hint.LegendaryPistol, Item("GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Tediore_5_Gunerang")),
    ItemPool("Unkempt Harold", Hint.LegendaryPistol, Item("GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Torgue_5_Calla")),
    ItemPool("Logan's Gun", Hint.LegendaryPistol, Item("GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Hyperion_5_LogansGun")),

    ItemPool("Lyudmila", Hint.LegendarySniper, Item("GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Vladof_5_Lyudmila")),
    ItemPool("Skullmasher", Hint.LegendarySniper, Item("GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Jakobs_5_Skullmasher")),
    ItemPool("Invader", Hint.LegendarySniper, Item("GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Hyperion_5_Invader")),
    ItemPool("Pitchfork", Hint.LegendarySniper, Item("GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Dahl_5_Pitchfork")),
    ItemPool("Volcano", Hint.LegendarySniper, Item("GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Maliwan_5_Volcano")),
    ItemPool("Longbow", Hint.LegendarySniper, Item("GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_Longbow")),

    ItemPool("Madhous!", Hint.LegendaryAR, Item("GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Bandit_5_Madhouse")),
    ItemPool("Hammer Buster", Hint.LegendaryAR, Item("GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Jakobs_5_HammerBuster")),
    ItemPool("Veruc", Hint.LegendaryAR, Item("GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Dahl_5_Veruc")),
    ItemPool("KerBlaster", Hint.LegendaryAR, Item("GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Torgue_5_KerBlaster")),
    ItemPool("Shredifier", Hint.LegendaryAR, Item("GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Vladof_5_Sherdifier")),

    
    ItemPool("Hector's Paradise", Hint.LegendaryPistol, Item("GD_Anemone_Weapons.A_Weapons_Legendary.Pistol_Dahl_5_Hector_Hornet", tags=Tag.FightForSanctuary)),
    ItemPool("Unicornsplosion", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.Shotguns.SG_Torgue_3_SwordSplosion_Unico", tags=Tag.FightForSanctuary)),
    ItemPool("M2828 Thumpson", Hint.LegendaryAR, Item("GD_Anemone_Weapons.AssaultRifle.Brothers.AR_Jakobs_5_Brothers", tags=Tag.FightForSanctuary)),
    ItemPool("Nirvana", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.A_Weapons_Legendary.SMG_Maliwan_5_HellFire", tags=Tag.FightForSanctuary)),
    ItemPool("Hot Mama", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.sniper.Sniper_Jakobs_6_Chaude_Mama", tags=Tag.FightForSanctuary)),
    ItemPool("Infection Cleaner", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.SMG.SMG_Tediore_6_Infection_Cleaner", tags=Tag.FightForSanctuary)),
    ItemPool("Amigo Sincero", Hint.LegendarySniper, Item("GD_Anemone_Weapons.A_Weapons_Unique.Sniper_Jakobs_3_Morde_Lt", tags=Tag.FightForSanctuary)),
    ItemPool("Overcompensator", Hint.LegendaryShotgun, Item("GD_Anemone_Weapons.Shotgun.Overcompensator.SG_Hyperion_6_Overcompensator", tags=Tag.FightForSanctuary)),
    ItemPool("Peak Opener", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.AssaultRifle.PeakOpener.AR_Torgue_5_PeakOpener", tags=Tag.FightForSanctuary)),
    ItemPool("Toothpick", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.AssaultRifle.AR_Dahl_6_Toothpick", tags=Tag.FightForSanctuary)),
    ItemPool("World Burn", Hint.EffervescentWeapon, Item("GD_Anemone_Weapons.Rocket_Launcher.WorldBurn.RL_Torgue_5_WorldBurn", tags=Tag.FightForSanctuary)),

    ItemPool("Winter is Over", Hint.UniqueRelic, Item("GD_Anemone_Relics.A_Item.A_Elemental_Status_Rare", tags=Tag.FightForSanctuary)),
    ItemPool("Hard Carry", Hint.EffervescentItem, Item("GD_Anemone_Relics.A_Item_Unique.A_Deputy", tags=Tag.FightForSanctuary)),
    ItemPool("Mouthwash", Hint.EffervescentItem, Item("GD_Anemone_Relics.A_Item_Unique.A_Sheriff", tags=Tag.FightForSanctuary)),

    ItemPool("Antifection", Hint.EffervescentItem, Item("GD_Anemone_GrenadeMods.A_Item_Legendary.GM_Antifection", tags=Tag.FightForSanctuary)),
    ItemPool("The Electric Chair", Hint.EffervescentItem, Item("GD_Anemone_GrenadeMods.A_Item_Legendary.GM_StormFront", tags=Tag.FightForSanctuary)),

    ItemPool("Retainer", Hint.EffervescentItem, Item("GD_Anemone_Balance_Treasure.Shields.ItemGrade_Gear_Shield_Worming", tags=Tag.FightForSanctuary)),
    ItemPool("Easy Mode", Hint.EffervescentItem, Item("GD_Anemone_ItemPools.Shields.ItemGrade_Gear_Shield_Nova_Singularity_Peak", tags=Tag.FightForSanctuary)),

    ItemPool("Ogre", Hint.LegendaryAR, Item("GD_Aster_Weapons.AssaultRifles.AR_Bandit_3_Ogre", tags=Tag.DragonKeep)),
    ItemPool("Grog Nozzle", Hint.UniquePistol, Item("GD_Aster_Weapons.Pistols.Pistol_Maliwan_3_GrogNozzle", tags=Tag.DragonKeep)),
    ItemPool("Crit", Hint.UniqueSMG, Item("GD_Aster_Weapons.SMGs.SMG_Maliwan_3_Crit", tags=Tag.DragonKeep)),
    ItemPool("Omen", Hint.SeraphWeapon, Item("GD_Aster_RaidWeapons.Shotguns.Aster_Seraph_Omen_Balance", tags=Tag.DragonKeep)),
    ItemPool("Stinger", Hint.SeraphWeapon, Item("GD_Aster_RaidWeapons.Pistols.Aster_Seraph_Stinger_Balance", tags=Tag.DragonKeep)),
    ItemPool("Seeker", Hint.SeraphWeapon, Item("GD_Aster_RaidWeapons.AssaultRifles.Aster_Seraph_Seeker_Balance", tags=Tag.DragonKeep)),
    ItemPool("Florentine", Hint.SeraphWeapon, Item("GD_Aster_RaidWeapons.SMGs.Aster_Seraph_Florentine_Balance", tags=Tag.DragonKeep)),
    ItemPool("SWORDSPLOSION!!!", Hint.UniqueShotgun, Item("GD_Aster_Weapons.Shotguns.SG_Torgue_3_SwordSplosion", tags=Tag.DragonKeep)),
    ItemPool("Orc", Hint.UniqueSMG, Item("GD_Aster_Weapons.SMGs.SMG_Bandit_3_Orc", tags=Tag.DragonKeep)),

    ItemPool("Mysterious Amulet", Hint.UniqueRelic, Item("GD_Aster_Artifacts.A_Item_Unique.A_MysteryAmulet", tags=Tag.DragonKeep)),
    ItemPool("Shadow of the Seraphs", Hint.SeraphItem, Item("GD_Aster_Artifacts.A_Item_Unique.A_SeraphShadow", tags=Tag.DragonKeep)),

    ItemPool("Chain Lightning", Hint.LegendaryGrenade, Item("GD_Aster_GrenadeMods.A_Item.GM_ChainLightning", tags=Tag.DragonKeep)),
    ItemPool("Fireball", Hint.UniqueGrenade, Item("GD_Aster_GrenadeMods.A_Item.GM_Fireball", tags=Tag.DragonKeep)),
    ItemPool("Fire Storm", Hint.LegendaryGrenade, Item("GD_Aster_GrenadeMods.A_Item.GM_FireStorm", tags=Tag.DragonKeep)),
    ItemPool("Lightning Bolt", Hint.UniqueGrenade, Item("GD_Aster_GrenadeMods.A_Item.GM_LightningBolt", tags=Tag.DragonKeep)),
    ItemPool("Magic Missile (x2)", Hint.UniqueGrenade, Item("GD_Aster_GrenadeMods.A_Item.GM_MagicMissile", tags=Tag.DragonKeep)),
    ItemPool("Magic Missile (x4)", Hint.UniqueGrenade, Item("GD_Aster_GrenadeMods.A_Item.GM_MagicMissileRare", tags=Tag.DragonKeep)),

    ItemPool("Blockade", Hint.SeraphItem, Item("GD_Aster_ItemGrades.Shields.Aster_Seraph_Blockade_Shield_Balance", tags=Tag.DragonKeep)),
    ItemPool("Antagonist", Hint.SeraphItem, Item("GD_Aster_ItemGrades.Shields.Aster_Seraph_Antagonist_Shield_Balance", tags=Tag.DragonKeep)),

    ItemPool("Heart of the Ancients", Hint.EtechRelic,
        Item("GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityAssault_VeryRare", tags=Tag.UVHMPack),
        Item("GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityLauncher_VeryRare", tags=Tag.UVHMPack),
        Item("GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityPistol_VeryRare", tags=Tag.UVHMPack),
        Item("GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityShotgun_VeryRare", tags=Tag.UVHMPack),
        Item("GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacitySMG_VeryRare", tags=Tag.UVHMPack),
        Item("GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacitySniper_VeryRare", tags=Tag.UVHMPack),
    ),
    ItemPool("Bone of the Ancients", Hint.EtechRelic, Item("GD_Gladiolus_Artifacts.A_Item.A_ElementalProficiency_VeryRare", tags=Tag.UVHMPack)),
    ItemPool("Skin of the Ancients", Hint.EtechRelic, Item("GD_Gladiolus_Artifacts.A_Item.A_ResistanceProtection_VeryRare", tags=Tag.UVHMPack)),
    ItemPool("Blood of the Ancients", Hint.EtechRelic, Item("GD_Gladiolus_Artifacts.A_Item.A_VitalityStockpile_VeryRare", tags=Tag.UVHMPack)),

    ItemPool("Unforgiven", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.Pistol.Pistol_Jakobs_6_Unforgiven", tags=Tag.UVHMPack)),
    ItemPool("Stalker", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.Pistol.Pistol_Vladof_6_Stalker", tags=Tag.UVHMPack)),
    ItemPool("Sawbar", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.AssaultRifle.AR_Bandit_6_Sawbar", tags=Tag.UVHMPack)),
    ItemPool("Bearcat", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.AssaultRifle.AR_Dahl_6_Bearcat", tags=Tag.UVHMPack)),
    ItemPool("Avenger", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.SMG.SMG_Tediore_6_Avenger", tags=Tag.UVHMPack)),
    ItemPool("Butcher", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.Shotgun.SG_Hyperion_6_Butcher", tags=Tag.UVHMPack)),
    ItemPool("Storm", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.sniper.Sniper_Maliwan_6_Storm", tags=Tag.UVHMPack)),
    ItemPool("Tunguska", Hint.PearlescentWeapon, Item("GD_Gladiolus_Weapons.Launchers.RL_Torgue_6_Tunguska", tags=Tag.UVHMPack)),

    ItemPool("Big Boom Blaster", Hint.SeraphItem, Item("GD_Iris_SeraphItems.BigBoomBlaster.Iris_Seraph_Shield_Booster_Balance", tags=Tag.CampaignOfCarnage)),
    ItemPool("Hoplite", Hint.SeraphItem, Item("GD_Iris_SeraphItems.Hoplite.Iris_Seraph_Shield_Juggernaut_Balance", tags=Tag.CampaignOfCarnage)),
    ItemPool("Pun-chee", Hint.SeraphItem, Item("GD_Iris_SeraphItems.Pun-chee.Iris_Seraph_Shield_Pun-chee_Balance", tags=Tag.CampaignOfCarnage)),
    ItemPool("Sponge", Hint.SeraphItem, Item("GD_Iris_SeraphItems.Sponge.Iris_Seraph_Shield_Sponge_Balance", tags=Tag.CampaignOfCarnage)),

    ItemPool("Crossfire", Hint.SeraphItem, Item("GD_Iris_SeraphItems.Crossfire.Iris_Seraph_GrenadeMod_Crossfire_Balance", tags=Tag.CampaignOfCarnage)),
    ItemPool("Meteor Shower", Hint.SeraphItem, Item("GD_Iris_SeraphItems.MeteorShower.Iris_Seraph_GrenadeMod_MeteorShower_Balance", tags=Tag.CampaignOfCarnage)),
    ItemPool("O-Negative", Hint.SeraphItem, Item("GD_Iris_SeraphItems.ONegative.Iris_Seraph_GrenadeMod_ONegative_Balance", tags=Tag.CampaignOfCarnage)),

    ItemPool("Might of the Seraphs", Hint.SeraphItem, Item("GD_Iris_SeraphItems.Might.Iris_Seraph_Artifact_Might_Balance", tags=Tag.CampaignOfCarnage)),

    ItemPool("Slow Hand", Hint.UniqueShotgun, Item("GD_Iris_Weapons.Shotguns.SG_Hyperion_3_SlowHand", tags=Tag.CampaignOfCarnage)),
    ItemPool("Pocket Rocket", Hint.UniquePistol, Item("GD_Iris_Weapons.Pistols.Pistol_Torgue_3_PocketRocket", tags=Tag.CampaignOfCarnage)),
    ItemPool("Cobra", Hint.UniqueSniper, Item("GD_Iris_Weapons.SniperRifles.Sniper_Jakobs_3_Cobra", tags=Tag.CampaignOfCarnage)),
    ItemPool("Boom Puppy", Hint.UniqueAR, Item("GD_Iris_Weapons.AssaultRifles.AR_Torgue_3_BoomPuppy", tags=Tag.CampaignOfCarnage)),
    ItemPool("Kitten", Hint.UniqueAR, Item("GD_Iris_Weapons.AssaultRifles.AR_Vladof_3_Kitten", tags=Tag.CampaignOfCarnage)),

    ItemPool("Carnage", Hint.PearlescentWeapon, Item("GD_Lobelia_Weapons.Shotguns.SG_Torgue_6_Carnage", tags=Tag.DigistructPeak)),
    ItemPool("Wanderlust", Hint.PearlescentWeapon, Item("GD_Lobelia_Weapons.Pistol.Pistol_Maliwan_6_Wanderlust", tags=Tag.DigistructPeak)),
    ItemPool("Godfinger", Hint.PearlescentWeapon, Item("GD_Lobelia_Weapons.sniper.Sniper_Jakobs_6_Godfinger", tags=Tag.DigistructPeak)),
    ItemPool("Bekah", Hint.PearlescentWeapon, Item("GD_Lobelia_Weapons.AssaultRifles.AR_Jakobs_6_Bekah", tags=Tag.DigistructPeak)),

    ItemPool("Captain Blade's Otto Idol", Hint.UniqueRelic, Item("GD_Orchid_Artifacts.A_Item_Unique.A_Blade", tags=Tag.PiratesBooty)),
    ItemPool("Blood of the Seraphs", Hint.SeraphItem, Item("GD_Orchid_Artifacts.A_Item_Unique.A_SeraphBloodRelic", tags=Tag.PiratesBooty)),

    ItemPool("Midnight Star", Hint.UniqueGrenade, Item("GD_Orchid_GrenadeMods.A_Item_Custom.GM_Blade", tags=Tag.PiratesBooty)),

    ItemPool("Evolution", Hint.SeraphItem, Item("GD_Orchid_RaidWeapons.Shield.Anshin.Orchid_Seraph_Anshin_Shield_Balance", tags=Tag.PiratesBooty)),
    ItemPool("Manly Man Shield", Hint.UniqueShield, Item("GD_Orchid_Shields.A_Item_Custom.S_BladeShield", tags=Tag.PiratesBooty)),

    ItemPool("Greed", Hint.UniquePistol, Item("GD_Orchid_BossWeapons.Pistol.Pistol_Jakobs_ScarletsGreed", tags=Tag.PiratesBooty)),
    ItemPool("12 Pounder", Hint.UniqueLauncher, Item("GD_Orchid_BossWeapons.Launcher.RL_Torgue_3_12Pounder", tags=Tag.PiratesBooty)),
    ItemPool("Little Evie", Hint.UniquePistol, Item("GD_Orchid_BossWeapons.Pistol.Pistol_Maliwan_3_LittleEvie", tags=Tag.PiratesBooty)),
    ItemPool("Stinkpot", Hint.UniqueAR, Item("GD_Orchid_BossWeapons.AssaultRifle.AR_Jakobs_3_Stinkpot", tags=Tag.PiratesBooty)),
    ItemPool("Devastator", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.Pistol.Devastator.Orchid_Seraph_Devastator_Balance", tags=Tag.PiratesBooty)),
    ItemPool("Tattler", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.SMG.Tattler.Orchid_Seraph_Tattler_Balance", tags=Tag.PiratesBooty)),
    ItemPool("Retcher", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.Shotgun.Spitter.Orchid_Seraph_Spitter_Balance", tags=Tag.PiratesBooty)),
    ItemPool("Actualizer", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.SMG.Actualizer.Orchid_Seraph_Actualizer_Balance", tags=Tag.PiratesBooty)),
    ItemPool("Seraphim", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.AssaultRifle.Seraphim.Orchid_Seraph_Seraphim_Balance", tags=Tag.PiratesBooty)),
    ItemPool("Patriot", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.sniper.Patriot.Orchid_Seraph_Patriot_Balance", tags=Tag.PiratesBooty)),
    ItemPool("Ahab", Hint.SeraphWeapon, Item("GD_Orchid_RaidWeapons.RPG.Ahab.Orchid_Seraph_Ahab_Balance", tags=Tag.PiratesBooty)),
    ItemPool("Rapier", Hint.UniqueAR, Item("GD_Orchid_BossWeapons.AssaultRifle.AR_Vladof_3_Rapier", tags=Tag.PiratesBooty)),
    ItemPool("Jolly Roger", Hint.UniqueShotgun, Item("GD_Orchid_BossWeapons.Shotgun.SG_Bandit_3_JollyRoger", tags=Tag.PiratesBooty)),
    ItemPool("Orphan Maker", Hint.UniqueShotgun, Item("GD_Orchid_BossWeapons.Shotgun.SG_Jakobs_3_OrphanMaker", tags=Tag.PiratesBooty)),
    ItemPool("Sand Hawk", Hint.UniqueSMG, Item("GD_Orchid_BossWeapons.SMG.SMG_Dahl_3_SandHawk", tags=Tag.PiratesBooty)),
    ItemPool("Pimpernel", Hint.UniqueSniper, Item("GD_Orchid_BossWeapons.SniperRifles.Sniper_Maliwan_3_Pimpernel", tags=Tag.PiratesBooty)),

    ItemPool("Breath of the Seraphs", Hint.SeraphItem, Item("GD_Sage_Artifacts.A_Item.A_SeraphBreath", tags=Tag.HammerlocksHunt)),

    ItemPool("The Rough Rider", Hint.UniqueShield, Item("GD_Sage_Shields.A_Item_Custom.S_BucklerShield", tags=Tag.HammerlocksHunt)),

    ItemPool("Hawk Eye", Hint.SeraphWeapon, Item("GD_Sage_RaidWeapons.sniper.Sage_Seraph_HawkEye_Balance", tags=Tag.HammerlocksHunt)),
    ItemPool("Infection", Hint.SeraphWeapon, Item("GD_Sage_RaidWeapons.Pistol.Sage_Seraph_Infection_Balance", tags=Tag.HammerlocksHunt)),
    ItemPool("Interfacer", Hint.SeraphWeapon, Item("GD_Sage_RaidWeapons.Shotgun.Sage_Seraph_Interfacer_Balance", tags=Tag.HammerlocksHunt)),
    ItemPool("Lead Storm", Hint.SeraphWeapon, Item("GD_Sage_RaidWeapons.AssaultRifle.Sage_Seraph_LeadStorm_Balance", tags=Tag.HammerlocksHunt)),
    ItemPool("Rex", Hint.UniquePistol, Item("GD_Sage_Weapons.Pistols.Pistol_Jakobs_3_Rex", tags=Tag.HammerlocksHunt)),
    ItemPool("Hydra", Hint.UniqueShotgun, Item("GD_Sage_Weapons.Shotgun.SG_Jakobs_3_Hydra", tags=Tag.HammerlocksHunt)),
    ItemPool("Damned Cowboy", Hint.UniqueAR, Item("GD_Sage_Weapons.AssaultRifle.AR_Jakobs_3_DamnedCowboy", tags=Tag.HammerlocksHunt)),
    ItemPool("Elephant Gun", Hint.UniqueSniper, Item("GD_Sage_Weapons.SniperRifles.Sniper_Jakobs_3_ElephantGun", tags=Tag.HammerlocksHunt)),
    ItemPool("CHOPPER", Hint.UniqueAR, Item("GD_Sage_Weapons.AssaultRifle.AR_Bandit_3_Chopper", tags=Tag.HammerlocksHunt)),
    ItemPool("Yellow Jacket", Hint.UniqueSMG, Item("GD_Sage_Weapons.SMG.SMG_Hyperion_3_YellowJacket", tags=Tag.HammerlocksHunt)),
    ItemPool("Twister", Hint.UniqueShotgun, Item("GD_Sage_Weapons.Shotgun.SG_Jakobs_3_Twister", tags=Tag.HammerlocksHunt)),
)



"""
- minimum levels for items
    example: blood of the ancients
        GD_Orchid_Artifacts.A_Item_Unique.A_SeraphBloodRelic
        Manufacturers  GradeModifiers GameStageRequirement


InventoryBalanceDefinition'GD_Artifacts.A_Item.A_Stockpile' Manufacturers: 
(
    (Manufacturer=ManufacturerDefinition'GD_Manufacturers.Artifacts.Artifact_TypeA',Grades=((GradeModifiers=(ExpLevel=0,CustomInventoryDefinition=None),GameStageRequirement=(MinGameStage=1,MaxGameStage=100),MinSpawnProbabilityModifier=(BaseValueConstant=1.000000,BaseValueAttribute=None,InitializationDefinition=None,BaseValueScaleConstant=1.000000),MaxSpawnProbabilityModifier=(BaseValueConstant=1.000000,BaseValueAttribute=None,InitializationDefinition=None,BaseValueScaleConstant=1.000000)))),
    (Manufacturer=ManufacturerDefinition'GD_Manufacturers.Artifacts.Artifact_TypeB',Grades=((GradeModifiers=(ExpLevel=0,CustomInventoryDefinition=None),GameStageRequirement=(MinGameStage=18,MaxGameStage=100),MinSpawnProbabilityModifier=(BaseValueConstant=1.000000,BaseValueAttribute=None,InitializationDefinition=None,BaseValueScaleConstant=1.000000),MaxSpawnProbabilityModifier=(BaseValueConstant=1.000000,BaseValueAttribute=None,InitializationDefinition=None,BaseValueScaleConstant=1.000000)))),
    (Manufacturer=ManufacturerDefinition'GD_Manufacturers.Artifacts.Artifact_TypeC',Grades=((GradeModifiers=(ExpLevel=0,CustomInventoryDefinition=None),GameStageRequirement=(MinGameStage=30,MaxGameStage=100),MinSpawnProbabilityModifier=(BaseValueConstant=1.000000,BaseValueAttribute=None,InitializationDefinition=None,BaseValueScaleConstant=1.000000),MaxSpawnProbabilityModifier=(BaseValueConstant=1.000000,BaseValueAttribute=None,InitializationDefinition=None,BaseValueScaleConstant=1.000000))))
)
InventoryBalanceDefinition'GD_Artifacts.A_Item.A_Stockpile_Rare' Manufacturers: 
(
    (Manufacturer=ManufacturerDefinition'GD_Manufacturers.Artifacts.Artifact_TypeA',Grades=((GradeModifiers=(ExpLevel=0,CustomInventoryDefinition=None),GameStageRequirement=(MinGameStage=1,MaxGameStage=100),MinSpawnProbabilityModifier=(BaseValueConstant=1.000000,BaseValueAttribute=None,InitializationDefinition=None,BaseValueScaleConstant=1.000000),MaxSpawnProbabilityModifier=(BaseValueConstant=1.000000,BaseValueAttribute=None,InitializationDefinition=None,BaseValueScaleConstant=1.000000)))),
    (Manufacturer=ManufacturerDefinition'GD_Manufacturers.Artifacts.Artifact_TypeB',Grades=((GradeModifiers=(ExpLevel=0,CustomInventoryDefinition=None),GameStageRequirement=(MinGameStage=18,MaxGameStage=100),MinSpawnProbabilityModifier=(BaseValueConstant=1.000000,BaseValueAttribute=None,InitializationDefinition=None,BaseValueScaleConstant=1.000000),MaxSpawnProbabilityModifier=(BaseValueConstant=1.000000,BaseValueAttribute=None,InitializationDefinition=None,BaseValueScaleConstant=1.000000)))),
    (Manufacturer=ManufacturerDefinition'GD_Manufacturers.Artifacts.Artifact_TypeC',Grades=((GradeModifiers=(ExpLevel=0,CustomInventoryDefinition=None),GameStageRequirement=(MinGameStage=30,MaxGameStage=100),MinSpawnProbabilityModifier=(BaseValueConstant=1.000000,BaseValueAttribute=None,InitializationDefinition=None,BaseValueScaleConstant=1.000000),MaxSpawnProbabilityModifier=(BaseValueConstant=1.000000,BaseValueAttribute=None,InitializationDefinition=None,BaseValueScaleConstant=1.000000))))
)
InventoryBalanceDefinition'GD_Gladiolus_Artifacts.A_Item.A_VitalityStockpile_VeryRare' Manufacturers: 
(
    (Manufacturer=ManufacturerDefinition'GD_Manufacturers.Artifacts.Artifact_TypeB',Grades=((GradeModifiers=(ExpLevel=0,CustomInventoryDefinition=None),GameStageRequirement=(MinGameStage=18,MaxGameStage=100),MinSpawnProbabilityModifier=(BaseValueConstant=1.000000,BaseValueAttribute=None,InitializationDefinition=None,BaseValueScaleConstant=1.000000),MaxSpawnProbabilityModifier=(BaseValueConstant=1.000000,BaseValueAttribute=None,InitializationDefinition=None,BaseValueScaleConstant=1.000000)))),
    (Manufacturer=ManufacturerDefinition'GD_Manufacturers.Artifacts.Artifact_TypeC',Grades=((GradeModifiers=(ExpLevel=0,CustomInventoryDefinition=None),GameStageRequirement=(MinGameStage=30,MaxGameStage=100),MinSpawnProbabilityModifier=(BaseValueConstant=1.000000,BaseValueAttribute=None,InitializationDefinition=None,BaseValueScaleConstant=1.000000),MaxSpawnProbabilityModifier=(BaseValueConstant=1.000000,BaseValueAttribute=None,InitializationDefinition=None,BaseValueScaleConstant=1.000000))))
)
InventoryBalanceDefinition'GD_Orchid_Artifacts.A_Item_Unique.A_SeraphBloodRelic' Manufacturers: 
(
    (Manufacturer=ManufacturerDefinition'GD_Manufacturers.Artifacts.Artifact_TypeA',Grades=((GradeModifiers=(ExpLevel=0,CustomInventoryDefinition=None),GameStageRequirement=(MinGameStage=50,MaxGameStage=100),MinSpawnProbabilityModifier=(BaseValueConstant=1.000000,BaseValueAttribute=None,InitializationDefinition=None,BaseValueScaleConstant=1.000000),MaxSpawnProbabilityModifier=(BaseValueConstant=1.000000,BaseValueAttribute=None,InitializationDefinition=None,BaseValueScaleConstant=1.000000))))
)



GD_Orchid_BossWeapons.RPG.Ahab.Orchid_Boss_Ahab_Balance_NODROP
GD_Orchid_SeraphCrystal.ItemGrades.ItemGrade_SeraphCrystal

GD_Iris_ItemPools.BalDefs.BalDef_ClassMod_Torgue_Common
GD_Iris_MoxxiPicture.ItemGrades.ItemGrade_MoxxiPicture1
GD_Iris_MoxxiPicture.ItemGrades.ItemGrade_MoxxiPicture2
GD_Iris_MoxxiPicture.ItemGrades.ItemGrade_MoxxiPicture3
GD_Iris_SeraphCrystal.ItemGrades.ItemGrade_Iris_SeraphCrystal
GD_Iris_SeraphItems.Misc.ItemGrade_BoosterShield_SeraphShieldChargerPickup
GD_Iris_TorgueToken.ItemGrades.ItemGrade_TorgueToken
GD_IrisDL3_CommAppealData.MW_CommAppeal_Torgue
GD_IrisEpisode05_BattleData.BalanceDefs.BD_Iris_GyroBanjo
GD_IrisEpisode05_BattleData.BalanceDefs.BD_Iris_GyroBanjo2
GD_IrisEpisode05_BattleData.BalanceDefs.BD_Iris_GyroBanjo3
GD_IrisEpisode05_BattleData.BalanceDefs.BD_Iris_GyroBanjoR3

GD_Sage_HarpoonGun.Balance.Sage_HarpoonGun_Balance
GD_Sage_SeraphCrystal.ItemGrades.ItemGrade_SeraphCrystal

GD_Aster_ClapTrapBeardData.MW_ClaptrapBeard_GrogNozzle
GD_Aster_SeraphCrystal.ItemGrades.ItemGrade_SeraphCrystal

GD_Anemone_GrenadeMods.A_Item_Legendary.GM_Antifection_Turret
GD_Anemone_GrenadeMods.A_Item.GM_Standard_3_Rare_Flamer
GD_Anemone_Lt_Hoffman.A_Weapons.Sniper_Vladof_4_VeryRare_Hoffman
GD_Anemone_Plot_Mission010.BalanceDefs.BD_Anemone_E01_M010_EchoLogs
GD_Anemone_Plot_Mission010.BalanceDefs.BD_Anemone_M010_Documents
GD_Anemone_Plot_Mission020.BalanceDefs.BD_E01_M020_InfectedBrains
GD_Anemone_Plot_Mission020.BalanceDefs.BD_E02_M020_TalonPlaceholder
GD_Anemone_Plot_Mission020.BalanceDefs.BD_InfectedBodyPart
GD_Anemone_Plot_Mission020.BalanceDefs.BD_M020_InfectedFlowerSample
GD_Anemone_Plot_Mission020.BalanceDefs.BD_TannisDevice
GD_Anemone_Plot_Mission025.BalanceDefs.BD_EllieTool
GD_Anemone_Plot_Mission025.BalanceDefs.BD_InfectedHead
GD_Anemone_Plot_Mission040.BalanceDefs.BD_Explosive
GD_Anemone_Plot_Mission040.BalanceDefs.BD_ID_PowerCore
GD_Anemone_Plot_Mission040.BalanceDefs.BD_StabilizerFin
GD_Anemone_Plot_Mission050.BalanceDefs.BD_Antidote
GD_Anemone_Plot_Mission050.BalanceDefs.BD_CassiusBlood
GD_Anemone_Plot_Mission050.BalanceDefs.BD_MordecaiBloodSample
GD_Anemone_Plot_Mission060.BalanceDefs.BD_BeerBottle
GD_Anemone_Plot_Mission060.BalanceDefs.BD_EridiumBar
GD_Anemone_Side_Claptocurrency.BalanceDefs.BD_BechoWaffers
GD_Anemone_Side_Claptocurrency.BalanceDefs.BD_BlockAndChain
GD_Anemone_Side_Echoes.BalanceDefs.BD_LostHectorEcho
GD_Anemone_Side_Echoes.BalanceDefs.BD_LostHectorECHO02
GD_Anemone_Side_Echoes.BalanceDefs.BD_LostHectorEcho03
GD_Anemone_Side_EyeSnipers.BalanceDefs.BD_LtAngvarRifleParts
GD_Anemone_Side_EyeSnipers.BalanceDefs.BD_LtBolsonRifleParts
GD_Anemone_Side_EyeSnipers.BalanceDefs.BD_LtHoffmanRifleParts
GD_Anemone_Side_EyeSnipers.BalanceDefs.BD_LtTetraRifleParts
GD_Anemone_Side_EyeSnipers.BalanceDefs.BD_MordecaisGift
GD_Anemone_Side_EyeSnipers.BalanceDefs.BD_NewPandorianRifleParts
GD_Anemone_Side_HypoOathPart1.BalanceDefs.BD_DrZedAntidote
GD_Anemone_Side_HypoOathPart1.BalanceDefs.BD_InfectedBodyPart
GD_Anemone_Side_HypoOathPart2.BalanceDefs.BD_DrZedAntidote
GD_Anemone_Side_HypoOathPart2.BalanceDefs.BD_InfectedBodyPart
GD_Anemone_Side_OddestCouple.BalanceDefs.BD_Cannedfood
GD_Anemone_Side_OddestCouple.BalanceDefs.BD_Cannedfood02
GD_Anemone_Side_OddestCouple.BalanceDefs.BD_Cannedfood03
GD_Anemone_Side_OddestCouple.BalanceDefs.BD_Cannedfood04
GD_Anemone_Side_SpaceCowboy.BalanceDefs.BD_NudieMagazine01
GD_Anemone_Side_SpaceCowboy.BalanceDefs.BD_NudieMagazine02
GD_Anemone_Side_SpaceCowboy.BalanceDefs.BD_NudieMagazine03
GD_Anemone_Side_SpaceCowboy.BalanceDefs.BD_ScooterECHO
GD_Anemone_Side_VaughnPart1.BalanceDefs.BD_Vaughnsflag
GD_Anemone_Side_VaughnPart2.BalanceDefs.BD_SandwormQueenTrophy
GD_Anemone_Side_VaughnPart2.BalanceDefs.BD_SandwormQueenTrophy02
GD_Anemone_Side_VaughnPart3.ItemDefs.BD_ArtifactOfPower
GD_Anemone_Weap_SniperRifles.A_Weapons.Sniper_Jakobs
GD_Anemone_Weap_SniperRifles.A_Weapons.Sniper_Jakobs_2_Uncommon
GD_Anemone_Weap_SniperRifles.A_Weapons.Sniper_Jakobs_3_Rare
GD_Anemone_Weap_SniperRifles.A_Weapons.Sniper_Jakobs_4_VeryRare
GD_Anemone_Weapons.A_Weapons_Legendary.Pistol_Vladof_5_Infinity_DD
GD_Anemone_Weapons.A_Weapons_Unique.Pistol_The_Gremlins
GD_Anemone_Weapons.A_Weapons_Unique.RL_Maliwan_Alien_Norfleet_Fire_100
GD_Anemone_Weapons.A_Weapons.Pistol_Vladof_4_VeryRare
GD_Anemone_Weapons.A_Weapons.SG_Torgue_7_Effervecemt
GD_Anemone_Weapons.AssaultRifle.PeakOpener.AR_PeakOpener
GD_Anemone_Weapons.Rocket_Launcher.RL_Maliwan_5_Pyrophobia
GD_Anemone_Weapons.Testing_Resist_100.100_Fire

GD_Allium_TG_Plot_M01Data.Weapons.Weapon_JabberSlagWeapon

GD_Flax_Items.Item.BalDef_Candy_Blue
GD_Flax_Items.Item.BalDef_Candy_Green
GD_Flax_Items.Item.BalDef_Candy_Red
GD_Flax_Items.Item.BalDef_Candy_Yellow
GD_Flax_Items.Item.BalDef_Wisp

GD_Artifacts.A_Item.A_AggressionA
GD_Artifacts.A_Item.A_AggressionB
GD_Artifacts.A_Item.A_AggressionC
GD_Artifacts.A_Item.A_AggressionD
GD_Artifacts.A_Item.A_AggressionE
GD_Artifacts.A_Item.A_AggressionF
GD_Artifacts.A_Item.A_AllegianceA
GD_Artifacts.A_Item.A_AllegianceB
GD_Artifacts.A_Item.A_AllegianceC
GD_Artifacts.A_Item.A_AllegianceD
GD_Artifacts.A_Item.A_AllegianceE
GD_Artifacts.A_Item.A_AllegianceF
GD_Artifacts.A_Item.A_AllegianceG
GD_Artifacts.A_Item.A_AllegianceH
GD_Artifacts.A_Item.A_Elemental
GD_Artifacts.A_Item.A_Elemental_Status
GD_Artifacts.A_Item.A_Proficiency
GD_Artifacts.A_Item.A_Protection
GD_Artifacts.A_Item.A_Resistance
GD_Artifacts.A_Item.A_Stockpile
GD_Artifacts.A_Item.A_Strength
GD_Artifacts.A_Item.A_Tenacity
GD_Artifacts.A_Item.A_Vitality

GD_CustomItems.Items.CustomItem_AmmoSDU_CombatRifle
GD_CustomItems.Items.CustomItem_AmmoSDU_CombatRifle_NextLvl
GD_CustomItems.Items.CustomItem_AmmoSDU_Grenades
GD_CustomItems.Items.CustomItem_AmmoSDU_Grenades_NextLvl
GD_CustomItems.Items.CustomItem_AmmoSDU_Launcher
GD_CustomItems.Items.CustomItem_AmmoSDU_Launcher_NextLvl
GD_CustomItems.Items.CustomItem_AmmoSDU_RepeaterPistol
GD_CustomItems.Items.CustomItem_AmmoSDU_RepeaterPistol_NextLvl
GD_CustomItems.Items.CustomItem_AmmoSDU_Shotgun
GD_CustomItems.Items.CustomItem_AmmoSDU_Shotgun_NextLvl
GD_CustomItems.Items.CustomItem_AmmoSDU_SMG
GD_CustomItems.Items.CustomItem_AmmoSDU_SMG_NextLvl
GD_CustomItems.Items.CustomItem_AmmoSDU_SniperRifle
GD_CustomItems.Items.CustomItem_AmmoSDU_SniperRifle_NextLvl
GD_CustomItems.Items.CustomItem_SDU_Bank

GD_DefaultProfiles.IntroEchos.BD_AssassinIntroEcho
GD_DefaultProfiles.IntroEchos.BD_GunzerkerIntroEcho
GD_DefaultProfiles.IntroEchos.BD_SirenIntroEcho
GD_DefaultProfiles.IntroEchos.BD_SoldierIntroEcho

GD_GrenadeMods.A_Item_Custom.GM_BouncingBetty_Uncommon_Bandit
GD_GrenadeMods.A_Item_Custom.GM_Mirv_Uncommon_Bandit
GD_GrenadeMods.A_Item_Custom.GM_Standard_Uncommon_Bandit
GD_GrenadeMods.A_Item.GM_AreaEffect
GD_GrenadeMods.A_Item.GM_AreaEffect_2_Uncommon
GD_GrenadeMods.A_Item.GM_AreaEffect_3_Rare
GD_GrenadeMods.A_Item.GM_BouncingBetty
GD_GrenadeMods.A_Item.GM_BouncingBetty_2_Uncommon
GD_GrenadeMods.A_Item.GM_BouncingBetty_3_Rare
GD_GrenadeMods.A_Item.GM_Mirv
GD_GrenadeMods.A_Item.GM_Mirv_2_Uncommon
GD_GrenadeMods.A_Item.GM_Mirv_3_Rare
GD_GrenadeMods.A_Item.GM_Singularity
GD_GrenadeMods.A_Item.GM_Singularity_2_Uncommon
GD_GrenadeMods.A_Item.GM_Singularity_3_Rare
GD_GrenadeMods.A_Item.GM_Standard
GD_GrenadeMods.A_Item.GM_Standard_2_Uncommon
GD_GrenadeMods.A_Item.GM_Standard_3_Rare
GD_GrenadeMods.A_Item.GM_Transfusion
GD_GrenadeMods.A_Item.GM_Transfusion_2_Uncommon
GD_GrenadeMods.A_Item.GM_Transfusion_3_Rare

GD_ItemGrades.Ammo_Boss.ItemGrade_Ammo_CombatRifle
GD_ItemGrades.Ammo_Boss.ItemGrade_Ammo_Grenade
GD_ItemGrades.Ammo_Boss.ItemGrade_Ammo_RepeaterPistol
GD_ItemGrades.Ammo_Boss.ItemGrade_Ammo_Shotgun
GD_ItemGrades.Ammo_Boss.ItemGrade_Ammo_SMG
GD_ItemGrades.Ammo_Boss.ItemGrade_Ammo_SniperRifle
GD_ItemGrades.Ammo.ItemGrade_Ammo_CombatRifle
GD_ItemGrades.Ammo.ItemGrade_Ammo_Grenade
GD_ItemGrades.Ammo.ItemGrade_Ammo_RepeaterPistol
GD_ItemGrades.Ammo.ItemGrade_Ammo_RocketLauncher
GD_ItemGrades.Ammo.ItemGrade_Ammo_Shotgun
GD_ItemGrades.Ammo.ItemGrade_Ammo_SMG
GD_ItemGrades.Ammo.ItemGrade_Ammo_SniperRifle

GD_ItemGrades.BuffDrink.ItemGrade_BuffDrink_HealingInstant
GD_ItemGrades.BuffDrink.ItemGrade_BuffDrink_HealingRegen
GD_ItemGrades.BuffDrink.ItemGrade_BuffDrink_Toughness

GD_ItemGrades.Currency.ItemGrade_Currency_Crystal
GD_ItemGrades.Currency.ItemGrade_Currency_Eridium_Bar
GD_ItemGrades.Currency.ItemGrade_Currency_Eridium_Stick
GD_ItemGrades.Currency.ItemGrade_Currency_Money_Big
GD_ItemGrades.Currency.ItemGrade_Currency_Money_Little

GD_ItemGrades.Gear.ItemGrade_Gear_Shield

GD_ItemGrades.Misc.ItemGrade_BoosterShield_ShieldChargerPickup
GD_Shields.Pickups.ItemGrade_BoosterShield_LegendaryShieldChargerPickup

GD_ItemGrades.StorageDeckUpgrades.ItemGrade_SDU_Ammo
GD_ItemGrades.StorageDeckUpgrades.ItemGrade_SDU_Ammo_EarlierVersion
GD_ItemGrades.StorageDeckUpgrades.ItemGrade_SDU_Backpack
GD_ItemGrades.StorageDeckUpgrades.ItemGrade_SDU_Bank
GD_ItemGrades.StorageDeckUpgrades.ItemGrade_SDU_WeaponEquipSlot

GD_ItemGrades.ClassMods.BalDef_ClassMod_AllParts
GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin
GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_01_Common
GD_ItemGrades.ClassMods.BalDef_ClassMod_Assassin_02_Uncommon
GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary
GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_01_Common
GD_ItemGrades.ClassMods.BalDef_ClassMod_Mercenary_02_Uncommon
GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren
GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_01_Common
GD_ItemGrades.ClassMods.BalDef_ClassMod_Siren_02_Uncommon
GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier
GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_01_Common
GD_ItemGrades.ClassMods.BalDef_ClassMod_Soldier_02_Uncommon
GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho
GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_01_Common
GD_Lilac_ClassMods.BalanceDefs.BalDef_ClassMod_Psycho_02_Uncommon
GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer
GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_01_Common
GD_Tulip_ItemGrades.ClassMods.BalDef_ClassMod_Mechromancer_02_Uncommon

GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_Absorption_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_Booster_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_Chimera_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_Impact_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_Impact_Hyperion_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_Juggernaut_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_Juggernaut_Pangolin_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_NovaAcid_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_NovaExplosive_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_NovaFire_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_NovaShock_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_Roid_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_SpikeAcid_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_SpikeExplosive_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_SpikeFire_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_SpikeShock_Dahl_02_Uncommon
GD_ItemGrades.MissionRewards.ItemGrade_Gear_Shield_Standard_Dahl_02_Uncommon

GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Impact_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Impact_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Impact_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Juggernaut_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Juggernaut_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Juggernaut_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Acid_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Acid_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Acid_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Acid_05_Legendary
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Explosive_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Explosive_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Explosive_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Fire_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Fire_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Fire_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Fire_05_Legendary
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Shock_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Shock_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Shock_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Shock_05_Legendary
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_05_Legendary
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Acid_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Acid_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Acid_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Explosive_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Explosive_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Explosive_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Explosive_05_Legendary
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Fire_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Fire_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Fire_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Fire_05_Legendary
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Shock_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Shock_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Shock_03_Rare
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Shock_05_Legendary
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_01_Common
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_02_Uncommon
GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_03_Rare

GD_Population_Marauder.ItemBalance.GM_AreaEffect_1_NoInterp
GD_Population_Marauder.ItemBalance.GM_AreaEffect_2_Uncommon_NoInterp
GD_Population_Marauder.ItemBalance.GM_BouncingBetty_1_NoInterp
GD_Population_Marauder.ItemBalance.GM_BouncingBetty_2_Uncommon_NoInterp
GD_Population_Marauder.ItemBalance.GM_Mirv_1_NoInterp
GD_Population_Marauder.ItemBalance.GM_Mirv_2_Uncommon_NoInterp
GD_Population_Marauder.ItemBalance.GM_Singularity_1_NoInterp
GD_Population_Marauder.ItemBalance.GM_Singularity_2_Uncommon_NoInterp
GD_Population_Marauder.ItemBalance.GM_Standard_1_NoInterp
GD_Population_Marauder.ItemBalance.GM_Standard_2_Uncommon_NoInterp
GD_Population_Marauder.ItemBalance.GM_Transfusion_1_NoInterp
GD_Population_Marauder.ItemBalance.GM_Transfusion_2_Uncommon_NoInterp

GD_Weap_AssaultRifle.A_Weapons_Elemental.AR_Bandit_2_Fire
GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Dahl_1_GBX
GD_Weap_AssaultRifle.A_Weapons.AR_Bandit
GD_Weap_AssaultRifle.A_Weapons.AR_Bandit_2_Uncommon
GD_Weap_AssaultRifle.A_Weapons.AR_Bandit_3_Rare
GD_Weap_AssaultRifle.A_Weapons.AR_Bandit_3_Rare_Alien
GD_Weap_AssaultRifle.A_Weapons.AR_Bandit_4_VeryRare
GD_Weap_AssaultRifle.A_Weapons.AR_Dahl
GD_Weap_AssaultRifle.A_Weapons.AR_Dahl_2_Uncommon
GD_Weap_AssaultRifle.A_Weapons.AR_Dahl_3_Rare
GD_Weap_AssaultRifle.A_Weapons.AR_Dahl_4_VeryRare
GD_Weap_AssaultRifle.A_Weapons.AR_Jakobs
GD_Weap_AssaultRifle.A_Weapons.AR_Jakobs_2_Uncommon
GD_Weap_AssaultRifle.A_Weapons.AR_Jakobs_3_Rare
GD_Weap_AssaultRifle.A_Weapons.AR_Jakobs_4_VeryRare
GD_Weap_AssaultRifle.A_Weapons.AR_Torgue
GD_Weap_AssaultRifle.A_Weapons.AR_Torgue_2_Uncommon
GD_Weap_AssaultRifle.A_Weapons.AR_Torgue_3_Rare
GD_Weap_AssaultRifle.A_Weapons.AR_Torgue_4_VeryRare
GD_Weap_AssaultRifle.A_Weapons.AR_Vladof
GD_Weap_AssaultRifle.A_Weapons.AR_Vladof_2_Uncommon
GD_Weap_AssaultRifle.A_Weapons.AR_Vladof_3_Rare
GD_Weap_AssaultRifle.A_Weapons.AR_Vladof_4_VeryRare
GD_Weap_Launchers.A_Weapons.RL_Bandit
GD_Weap_Launchers.A_Weapons.RL_Bandit_2_Uncommon
GD_Weap_Launchers.A_Weapons.RL_Bandit_3_Rare
GD_Weap_Launchers.A_Weapons.RL_Maliwan
GD_Weap_Launchers.A_Weapons.RL_Maliwan_2_Uncommon
GD_Weap_Launchers.A_Weapons.RL_Maliwan_3_Rare
GD_Weap_Launchers.A_Weapons.RL_Tediore
GD_Weap_Launchers.A_Weapons.RL_Tediore_2_Uncommon
GD_Weap_Launchers.A_Weapons.RL_Tediore_3_Rare
GD_Weap_Launchers.A_Weapons.RL_Torgue
GD_Weap_Launchers.A_Weapons.RL_Torgue_2_Uncommon
GD_Weap_Launchers.A_Weapons.RL_Torgue_3_Rare
GD_Weap_Launchers.A_Weapons.RL_Vladof
GD_Weap_Launchers.A_Weapons.RL_Vladof_2_Uncommon
GD_Weap_Launchers.A_Weapons.RL_Vladof_3_Rare
GD_Weap_Pistol.A_Weapons_Elemental.Pistol_Maliwan_2_Corrosive
GD_Weap_Pistol.A_Weapons_Elemental.Pistol_Maliwan_2_Fire
GD_Weap_Pistol.A_Weapons_Elemental.Pistol_Maliwan_2_Shock
GD_Weap_Pistol.A_Weapons_Elemental.Pistol_Maliwan_2_Slag
GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_Starter
GD_Weap_Pistol.A_Weapons.Pistol_Bandit
GD_Weap_Pistol.A_Weapons.Pistol_Bandit_2_Uncommon
GD_Weap_Pistol.A_Weapons.Pistol_Bandit_3_Rare
GD_Weap_Pistol.A_Weapons.Pistol_Bandit_4_VeryRare
GD_Weap_Pistol.A_Weapons.Pistol_Dahl
GD_Weap_Pistol.A_Weapons.Pistol_Dahl_2_Uncommon
GD_Weap_Pistol.A_Weapons.Pistol_Dahl_3_Rare
GD_Weap_Pistol.A_Weapons.Pistol_Dahl_4_VeryRare
GD_Weap_Pistol.A_Weapons.Pistol_Hyperion
GD_Weap_Pistol.A_Weapons.Pistol_Hyperion_2_Uncommon
GD_Weap_Pistol.A_Weapons.Pistol_Hyperion_3_Rare
GD_Weap_Pistol.A_Weapons.Pistol_Hyperion_4_VeryRare
GD_Weap_Pistol.A_Weapons.Pistol_Hyperion_5_Alien
GD_Weap_Pistol.A_Weapons.Pistol_Jakobs
GD_Weap_Pistol.A_Weapons.Pistol_Jakobs_2_Uncommon
GD_Weap_Pistol.A_Weapons.Pistol_Jakobs_3_Rare
GD_Weap_Pistol.A_Weapons.Pistol_Jakobs_4_VeryRare
GD_Weap_Pistol.A_Weapons.Pistol_Maliwan
GD_Weap_Pistol.A_Weapons.Pistol_Maliwan_2_Uncommon
GD_Weap_Pistol.A_Weapons.Pistol_Maliwan_3_Rare
GD_Weap_Pistol.A_Weapons.Pistol_Maliwan_4_VeryRare
GD_Weap_Pistol.A_Weapons.Pistol_Tediore
GD_Weap_Pistol.A_Weapons.Pistol_Tediore_2_Uncommon
GD_Weap_Pistol.A_Weapons.Pistol_Tediore_3_Rare
GD_Weap_Pistol.A_Weapons.Pistol_Tediore_4_VeryRare
GD_Weap_Pistol.A_Weapons.Pistol_Torgue
GD_Weap_Pistol.A_Weapons.Pistol_Torgue_2_Uncommon
GD_Weap_Pistol.A_Weapons.Pistol_Torgue_3_Rare
GD_Weap_Pistol.A_Weapons.Pistol_Torgue_4_VeryRare
GD_Weap_Pistol.A_Weapons.Pistol_Vladof
GD_Weap_Pistol.A_Weapons.Pistol_Vladof_2_Uncommon
GD_Weap_Pistol.A_Weapons.Pistol_Vladof_3_Rare
GD_Weap_Pistol.A_Weapons.Pistol_Vladof_4_VeryRare
GD_Weap_Shotgun.A_Weapons.SG_Bandit
GD_Weap_Shotgun.A_Weapons.SG_Bandit_2_Uncommon
GD_Weap_Shotgun.A_Weapons.SG_Bandit_3_Rare
GD_Weap_Shotgun.A_Weapons.SG_Bandit_4_VeryRare
GD_Weap_Shotgun.A_Weapons.SG_Hyperion
GD_Weap_Shotgun.A_Weapons.SG_Hyperion_2_Uncommon
GD_Weap_Shotgun.A_Weapons.SG_Hyperion_3_Rare
GD_Weap_Shotgun.A_Weapons.SG_Hyperion_4_VeryRare
GD_Weap_Shotgun.A_Weapons.SG_Jakobs
GD_Weap_Shotgun.A_Weapons.SG_Jakobs_2_Uncommon
GD_Weap_Shotgun.A_Weapons.SG_Jakobs_3_Rare
GD_Weap_Shotgun.A_Weapons.SG_Jakobs_4_VeryRare
GD_Weap_Shotgun.A_Weapons.SG_Tediore
GD_Weap_Shotgun.A_Weapons.SG_Tediore_2_Uncommon
GD_Weap_Shotgun.A_Weapons.SG_Tediore_3_Rare
GD_Weap_Shotgun.A_Weapons.SG_Tediore_4_VeryRare
GD_Weap_Shotgun.A_Weapons.SG_Torgue
GD_Weap_Shotgun.A_Weapons.SG_Torgue_2_Uncommon
GD_Weap_Shotgun.A_Weapons.SG_Torgue_3_Rare
GD_Weap_Shotgun.A_Weapons.SG_Torgue_4_VeryRare
GD_Weap_SMG.A_Weapons_Unique.SMG_Gearbox_1
GD_Weap_SMG.A_Weapons.SMG_Bandit
GD_Weap_SMG.A_Weapons.SMG_Bandit_2_Uncommon
GD_Weap_SMG.A_Weapons.SMG_Bandit_3_Rare
GD_Weap_SMG.A_Weapons.SMG_Bandit_4_VeryRare
GD_Weap_SMG.A_Weapons.SMG_Dahl
GD_Weap_SMG.A_Weapons.SMG_Dahl_2_Uncommon
GD_Weap_SMG.A_Weapons.SMG_Dahl_3_Rare
GD_Weap_SMG.A_Weapons.SMG_Dahl_4_VeryRare
GD_Weap_SMG.A_Weapons.SMG_Hyperion
GD_Weap_SMG.A_Weapons.SMG_Hyperion_2_Uncommon
GD_Weap_SMG.A_Weapons.SMG_Hyperion_3_Rare
GD_Weap_SMG.A_Weapons.SMG_Hyperion_4_VeryRare
GD_Weap_SMG.A_Weapons.SMG_Maliwan
GD_Weap_SMG.A_Weapons.SMG_Maliwan_2_Uncommon
GD_Weap_SMG.A_Weapons.SMG_Maliwan_3_Rare
GD_Weap_SMG.A_Weapons.SMG_Maliwan_4_VeryRare
GD_Weap_SMG.A_Weapons.SMG_Tediore
GD_Weap_SMG.A_Weapons.SMG_Tediore_2_Uncommon
GD_Weap_SMG.A_Weapons.SMG_Tediore_3_Rare
GD_Weap_SMG.A_Weapons.SMG_Tediore_4_VeryRare
GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Gearbox_1
GD_Weap_SniperRifles.A_Weapons.Sniper_Dahl
GD_Weap_SniperRifles.A_Weapons.Sniper_Dahl_2_Uncommon
GD_Weap_SniperRifles.A_Weapons.Sniper_Dahl_3_Rare
GD_Weap_SniperRifles.A_Weapons.Sniper_Dahl_4_VeryRare
GD_Weap_SniperRifles.A_Weapons.Sniper_Hyperion
GD_Weap_SniperRifles.A_Weapons.Sniper_Hyperion_2_Uncommon
GD_Weap_SniperRifles.A_Weapons.Sniper_Hyperion_3_Rare
GD_Weap_SniperRifles.A_Weapons.Sniper_Hyperion_4_VeryRare
GD_Weap_SniperRifles.A_Weapons.Sniper_Jakobs
GD_Weap_SniperRifles.A_Weapons.Sniper_Jakobs_2_Uncommon
GD_Weap_SniperRifles.A_Weapons.Sniper_Jakobs_3_Rare
GD_Weap_SniperRifles.A_Weapons.Sniper_Jakobs_4_VeryRare
GD_Weap_SniperRifles.A_Weapons.Sniper_Maliwan
GD_Weap_SniperRifles.A_Weapons.Sniper_Maliwan_2_Uncommon
GD_Weap_SniperRifles.A_Weapons.Sniper_Maliwan_3_Rare
GD_Weap_SniperRifles.A_Weapons.Sniper_Maliwan_4_VeryRare
GD_Weap_SniperRifles.A_Weapons.Sniper_Vladof
GD_Weap_SniperRifles.A_Weapons.Sniper_Vladof_2_Uncommon
GD_Weap_SniperRifles.A_Weapons.Sniper_Vladof_3_Rare
GD_Weap_SniperRifles.A_Weapons.Sniper_Vladof_4_VeryRare
GD_Z1_CordiallyInvitedData.MW_Teapot
GD_Z1_RockPaperGenocideData.MW_RockPaper_Corrosive
GD_Z1_RockPaperGenocideData.MW_RockPaper_Fire
GD_Z1_RockPaperGenocideData.MW_RockPaper_Shock
GD_Z1_RockPaperGenocideData.MW_RockPaper_Slag
GD_Z2_TrailerTrashinData.FlareGun
GD_Z3_MedicalMystery2Data.MW_MedicalMystery_AlienGun

"""
