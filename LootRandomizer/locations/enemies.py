from __future__ import annotations

from unrealsdk import ConstructObject, Log, KeepAlive, GetEngine  #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct #type: ignore

from .. import options, locations
from ..locations import Behavior
from ..options import Tag, Probability, BalancedItem

from typing import List, Set, Sequence, Tuple


EnemyTags = (
    Tag.UniqueEnemy     |
    Tag.SlowEnemy       |
    Tag.RareEnemy       |
    Tag.RaidEnemy       |
    Tag.MissionEnemy    |
    Tag.DigistructEnemy |
    Tag.EvolvedEnemy
)

EnemyPoolTags = (
    Tag.SlowEnemy       |
    Tag.RareEnemy       |
    Tag.VeryRareEnemy   |
    Tag.EvolvedEnemy    |
    Tag.MissionEnemy    |
    Tag.LongMission     |
    Tag.VeryLongMission |
    Tag.RaidEnemy
)


def _convert_probability(original: FStruct) -> Probability:
    return (
        original.BaseValueConstant,
        original.BaseValueAttribute,
        original.InitializationDefinition,
        original.BaseValueScaleConstant
    )


PoolListEntry = Tuple[UObject, Probability]

def _rebuild_pool_list(original: Sequence[UObject], addenda: Sequence[PoolListEntry]) -> List[PoolListEntry]:
    pool_list = list(addenda)

    for pool in original:
        if not (pool.ItemPool and pool.ItemPool.bAutoReadyItems):
            continue

        path = UObject.PathName(pool.ItemPool)
        balanced_items: List[BalancedItem] = list()

        for item in pool.ItemPool.BalancedItems:
            balanced_items.append((
                item.ItmPoolDefinition,
                item.InvBalanceDefinition,
                _convert_probability(item.Probability),
                item.bDropOnDeath
            ))
            if item.bDropOnDeath:
                locations.modified_pools[path] = balanced_items
                item.bDropOnDeath = False

        pool_list.append((pool.ItemPool, _convert_probability(pool.PoolProbability)))

    return pool_list


class Pawn(locations.PathDropper):
    registry_class: str = "AIPawnBalanceDefinition"

    block_includes: bool

    def __init__(self, path: str, block_includes: bool = False) -> None:
        self.registry_path = path; self.block_includes = block_includes

    def inject(self, uobject: UObject) -> None:
        pools = self.location.get_pools()
        if self.block_includes:
            uobject.DefaultItemPoolIncludedLists = ()

        pools = [(pool, (1, None, None, 1)) for pool in pools]

        uobject.DefaultItemPoolList = _rebuild_pool_list(uobject.DefaultItemPoolList, pools)
        for playthrough in uobject.PlayThroughs:
            if list(playthrough.CustomItemPoolList):
                playthrough.CustomItemPoolList = _rebuild_pool_list(playthrough.CustomItemPoolList, pools)


class Leviathan(locations.MapDropper):
    map_name = "Orchid_WormBelly_P"

    def inject(self) -> None:
        def hook(caller: UObject, function: UFunction, params: FStruct) -> bool:
            if UObject.PathName(caller.MissionObjective) not in (
                # "GD_Orchid_SM_EndGameClone.M_Orchid_EndGame:KillBossWorm",
                "GD_Orchid_Plot_Mission09.M_Orchid_PlotMission09:KillBossWorm"
            ):
                return True

            pawn = GetEngine().GetCurrentWorldInfo().PawnList
            while pawn:
                if pawn.AIClass and pawn.AIClass.Name == "CharacterClass_Orchid_BossWorm":
                    break
                pawn = pawn.NextPawn

            spawner = ConstructObject("Behavior_SpawnLootAroundPoint")
            spawner.ItemPools = self.location.get_pools()
            spawner.SpawnVelocity = (-400, -1800, -400)
            spawner.SpawnVelocityRelativeTo = 1
            spawner.CustomLocation = ((1200, -66000, 3000), None, "")
            spawner.CircularScatterRadius = 200
            spawner.ApplyBehaviorToContext(pawn, (), None, None, None, ())

            return True

        RunHook("WillowGame.Behavior_UpdateMissionObjective.ApplyBehaviorToContext", f"LootRandomizer.{id(self)}", hook)
        
    def uninject(self) -> None:
        RemoveHook("WillowGame.Behavior_UpdateMissionObjective.ApplyBehaviorToContext", f"LootRandomizer.{id(self)}")


class MonsterTruck(locations.MapDropper):
    map_name = "Iris_Hub2_P"

    def inject(self) -> None:
        def hook(caller: UObject, function: UFunction, params: FStruct) -> bool:
            if not (caller.VehicleDef and caller.VehicleDef.Name == "Class_MonsterTruck_AIOnly"):
                return True

            spawner = ConstructObject("Behavior_SpawnLootAroundPoint")
            spawner.ItemPools = self.location.get_pools()
            spawner.ApplyBehaviorToContext(caller, (), None, None, None, ())
            return True

        RunHook("Engine.Pawn.Died", f"LootRandomizer.{id(self)}", hook)

    def uninject(self) -> None:
        RemoveHook("Engine.Pawn.Died", f"LootRandomizer.{id(self)}")


midget_pools: Sequence[UObject] = ()
wildlife_midget_pools: Sequence[UObject] = ()
wildlife_midget_paths: Set[str] = set()


def SpawnMidget(caller: UObject, function: UFunction, params: FStruct) -> bool:
    if UObject.PathName(caller) == "GD_Balance_Treasure.InteractiveObjectsTrap.MidgetHyperion.InteractiveObj_CardboardBox_MidgetHyperion:BehaviorProviderDefinition_1.Behavior_SpawnFromPopulationSystem_5":
        wildlife_midget_paths.add(UObject.PathName(params.SpawnedActor))
    return True

midget_balances = (
    "GD_Population_Midget.Balance.LootMidget.PawnBalance_Jimmy",
    "GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_CombatEngineer",
    "GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_Engineer",
    "GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_LoaderGUN",
    "GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_LoaderJET",
    "GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_LoaderWAR",
    "GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_Marauder",
    "GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_Goliath",
    "GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_Nomad",
    "GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_Psycho",
    "GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_Rat",
)

def MidgetDied(caller: UObject, function: UFunction, params: FStruct) -> bool:
    balance = caller.BalanceDefinitionState.BalanceDefinition
    if balance and UObject.PathName(balance) not in midget_balances:
        return True
    
    if UObject.PathName(caller) in wildlife_midget_paths:
        return True

    new_pools: List[Tuple[UObject, Probability]] = []
    for pool in midget_pools:
        new_pools.append((pool, (1, None, None, 1)))

    caller.ItemPoolList = new_pools
    return True


def WildlifeMidgetDied(caller: UObject, function: UFunction, params: FStruct) -> bool:
    if UObject.PathName(caller) not in wildlife_midget_paths:
        return True

    new_pools: List[Tuple[UObject, Probability]] = []
    for pool in wildlife_midget_pools:
        new_pools.append((pool, (1, None, None, 1)))

    caller.ItemPoolList = new_pools
    return True


class Midget(locations.Dropper):
    def register(self) -> None:
        global midget_pools
        midget_pools = self.location.get_pools()
        for pool in midget_pools:
            KeepAlive(pool)
        RunHook("WillowGame.Behavior_SpawnFromPopulationSystem.PublishBehaviorOutput", "LootRandomizer.Midget", SpawnMidget)
        RunHook("WillowGame.WillowAIPawn.Died", "LootRandomizer.Midget", MidgetDied)


    def unregister(self) -> None:
        Log("Midget.unregister called")
        global midget_pools
        for pool in midget_pools:
            pool.ObjectFlags.A &= ~0x4000
        midget_pools = ()
        RemoveHook("WillowGame.Behavior_SpawnFromPopulationSystem.PublishBehaviorOutput", "LootRandomizer.Midget")
        RemoveHook("WillowGame.WillowAIPawn.Died", "LootRandomizer.Midget")


class WildlifeMidget(locations.MapDropper):
    map_name = "PandoraPark_P"

    def register(self) -> None:
        super().register()
        global wildlife_midget_pools
        wildlife_midget_pools = self.location.get_pools()
        for pool in wildlife_midget_pools:
            KeepAlive(pool)

    def unregister(self) -> None:
        super().unregister()
        global wildlife_midget_pools
        for pool in wildlife_midget_pools:
            pool.ObjectFlags.A &= ~0x4000
        wildlife_midget_pools = ()

    def inject(self) -> None:
        global wildlife_midget_paths
        wildlife_midget_paths = set()
        RunHook("WillowGame.Behavior_SpawnFromPopulationSystem.PublishBehaviorOutput", "LootRandomizer.WildlifeMidget", SpawnMidget)
        RunHook("WillowGame.WillowAIPawn.Died", "LootRandomizer.WildlifeMidget", WildlifeMidgetDied)

    def uninject(self) -> None:
        wildlife_midget_paths.clear()
        RemoveHook("WillowGame.Behavior_SpawnFromPopulationSystem.PublishBehaviorOutput", "LootRandomizer.WildlifeMidget")
        RemoveHook("WillowGame.WillowAIPawn.Died", "LootRandomizer.WildlifeMidget")


class Enemy(locations.Location):
    def __init__(
        self,
        name: str,
        *droppers: locations.Dropper,
        tags: Tag = Tag.BaseGame|Tag.UniqueEnemy,
    ) -> None:
        super().__init__(name, *droppers, tags=tags)

        if not self.tags & options.ContentTags:
            self.tags |= Tag.BaseGame
        if not self.tags & EnemyTags:
            self.tags |= Tag.UniqueEnemy


    def get_pools(self) -> Sequence[UObject]: #ItemPoolDefinition
        hint = self.get_hint()
        item = self.item.uobject

        pools: List[UObject] = []

        def add_pool(rarity: int) -> None: #ItemPoolDefinition
            pool = ConstructObject("ItemPoolDefinition")
            pool.bAutoReadyItems = False
            pool.BalancedItems = [
                (item, None, (         1, None, None, 1), True),
                (None, hint, (rarity - 1, None, None, 1), True),
            ]
            pools.append(pool)

        if not self.tags & EnemyPoolTags:
            add_pool(10)
            return pools

        if Tag.SlowEnemy in self.tags:
            add_pool(3)

        if Tag.RareEnemy in self.tags:
            add_pool(3)

        if Tag.VeryRareEnemy in self.tags:
            add_pool(1); add_pool(3); add_pool(3); add_pool(3)

        if Tag.EvolvedEnemy in self.tags:
            add_pool(3); add_pool(3)

        if Tag.MissionEnemy in self.tags and not (Tag.LongMission|Tag.VeryLongMission) & self.tags:
            add_pool(6)

        if Tag.LongMission in self.tags:
            add_pool(3)

        if Tag.VeryLongMission in self.tags:
            add_pool(1); add_pool(3)

        if Tag.RaidEnemy in self.tags:
            add_pool(1); add_pool(1); add_pool(3); add_pool(3)

        return pools


Locations = (
    Enemy("Knuckle Dragger", Pawn("GD_Population_PrimalBeast.Balance.Unique.PawnBalance_PrimalBeast_KnuckleDragger")),
    Enemy("Midgemong", Pawn("GD_Population_PrimalBeast.Balance.Unique.PawnBalance_PrimalBeast_Warmong")),
    Enemy("Boom", Pawn("GD_Population_Marauder.Balance.PawnBalance_BoomBoom")),
    Enemy("Bewm", Pawn("GD_Population_Marauder.Balance.PawnBalance_Boom")),
    Enemy("Captain Flynt", Pawn("GD_Population_Nomad.Balance.Unique.PawnBalance_Flynt"), tags=Tag.SlowEnemy),
    Enemy("Savage Lee", Pawn("GD_Population_Psycho.Balance.Unique.PawnBalance_SavageLee")),
    Enemy("Doc Mercy", Pawn("GD_Population_Nomad.Balance.Unique.PawnBalance_MrMercy")),
    Enemy("Assassin Wot", Pawn("GD_Population_Marauder.Balance.Unique.PawnBalance_Assassin1")),
    Enemy("Assassin Oney", Pawn("GD_Population_Nomad.Balance.Unique.PawnBalance_Assassin2")),
    Enemy("Assassin Reeth", Pawn("GD_Population_Psycho.Balance.Unique.PawnBalance_Assassin3"), tags=Tag.SlowEnemy),
    Enemy("Assassin Rouf", Pawn("GD_Population_Rat.Balance.Unique.PawnBalance_Assassin4"), tags=Tag.SlowEnemy),
    Enemy("Boll", Pawn("GD_Z1_InMemoriamData.Balance.PawnBalance_Boll")),
    Enemy("Scorch", Pawn("GD_Population_SpiderAnt.Balance.Unique.PawnBalance_SpiderantScorch")),
    Enemy("Incinerator Clayton", Pawn("GD_Population_Psycho.Balance.Unique.PawnBalance_IncineratorVanya_Combat"), tags=Tag.SlowEnemy),
    Enemy("Shirtless Man", Pawn("GD_Population_Marauder.Balance.Unique.PawnBalance_ShirtlessMan"), tags=Tag.MissionEnemy),
    Enemy("The Black Queen", Pawn("GD_Population_SpiderAnt.Balance.Unique.PawnBalance_SpiderantBlackQueen"), tags=Tag.SlowEnemy|Tag.RareEnemy),
    Enemy("Bad Maw", Pawn("GD_Population_Nomad.Balance.PawnBalance_BadMaw")),
    Enemy("Mad Mike", Pawn("GD_Population_Nomad.Balance.Unique.PawnBalance_MadMike"), tags=Tag.SlowEnemy),
    Enemy("Lee", Pawn("GD_Population_Rat.Balance.Unique.PawnBalance_Lee")),
    Enemy("Dan", Pawn("GD_Population_Rat.Balance.Unique.PawnBalance_Dan")),
    Enemy("Loader #1340",
        Pawn("GD_Population_Constructor.Balance.Unique.PawnBalance_Constructor_1340"),
        Pawn("GD_Population_Loader.Balance.Unique.PawnBalance_LoaderWAR_1340"),
    tags=Tag.MissionEnemy|Tag.LongMission),
    Enemy("Ralph", Pawn("GD_Population_Rat.Balance.Unique.PawnBalance_Ralph")),
    Enemy("Mick", Pawn("GD_Population_Rat.Balance.Unique.PawnBalance_Mick")),
    Enemy("Flinter", Pawn("GD_Population_Rat.Balance.Unique.PawnBalance_RatEasterEgg")),
    Enemy("Wilhelm", Pawn("GD_Population_Loader.Balance.Unique.PawnBalance_Willhelm")),
    Enemy("Mutated Badass Varkid", Pawn("GD_Population_BugMorph.Balance.PawnBalance_BugMorphBadass_Mutated"), tags=Tag.MissionEnemy),
    Enemy("Madame Von Bartlesby", Pawn("GD_Population_BugMorph.Balance.Unique.PawnBalance_SirReginald")),
    Enemy("Flesh-Stick", Pawn("GD_Population_Psycho.Balance.Unique.PawnBalance_FleshStick"), tags=Tag.MissionEnemy),
    Enemy("Prospector Zeke", Pawn("GD_Population_Nomad.Balance.Unique.PawnBalance_Prospector"), tags=Tag.SlowEnemy),
    Enemy("Mobley", Pawn("GD_Population_Marauder.Balance.Unique.PawnBalancaw_Mobley")),
    Enemy("Gettle", Pawn("GD_Population_Engineer.Balance.Unique.PawnBalance_Gettle")),
    Enemy("Badass Creeper", Pawn("GD_Population_Creeper.Balance.PawnBalance_CreeperBadass"), tags=Tag.SlowEnemy),
    Enemy("Henry", Pawn("GD_Population_Stalker.Balance.Unique.PawnBalance_Henry")),
    Enemy("Requisition Officer", Pawn("GD_Population_Engineer.Balance.Unique.PawnBalance_RequisitionOfficer"), tags=Tag.MissionEnemy),
    Enemy("Old Slappy", Pawn("GD_Population_Thresher.Balance.Unique.PawnBalance_Slappy")),
    Enemy("Bagman", Pawn("GD_Population_Engineer.Balance.Unique.PawnBalance_Leprechaun"), tags=Tag.MissionEnemy),
    Enemy("Mick Zaford", Pawn("GD_Population_Marauder.Balance.Unique.PawnBalance_MickZaford_Combat")),
    Enemy("Tector Hodunk", Pawn("GD_Population_Marauder.Balance.Unique.PawnBalance_TectorHodunk_Combat")),
    Enemy("Blue", Pawn("GD_Population_Crystalisk.Balance.Unique.PawnBalance_Blue")),
    Enemy("Sinkhole", Pawn("GD_Population_Stalker.Balance.Unique.PawnBalance_Stalker_SwallowedWhole")),
    Enemy("Shorty", Pawn("GD_Population_Midget.Balance.Unique.PawnBalance_Midge")),
    Enemy("Laney White", Pawn("GD_Population_Rat.Balance.Unique.PawnBalance_Laney")),
    Enemy("Smash-Head", Pawn("GD_Population_Goliath.Balance.Unique.PawnBalance_SmashHead"), tags=Tag.SlowEnemy),
    Enemy("Rakkman", Pawn("GD_Population_Psycho.Balance.Unique.PawnBalance_RakkMan"), tags=Tag.SlowEnemy),
    Enemy("Tumbaa", Pawn("GD_Population_Skag.Balance.Unique.PawnBalance_Tumbaa"), tags=Tag.RareEnemy),
    Enemy("Pimon", Pawn("GD_Population_Stalker.Balance.Unique.PawnBalance_Stalker_Simon"), tags=Tag.RareEnemy),
    Enemy("Son of Mothrakk", Pawn("GD_Population_Rakk.Balance.Unique.PawnBalance_SonMothrakk"), tags=Tag.SlowEnemy),
    Enemy("Muscles", Pawn("GD_Population_Bruiser.Balance.PawnBalance_Bruiser_Muscles"), tags=Tag.VeryRareEnemy),
    Enemy("The Sheriff of Lynchwood", Pawn("GD_Population_Sheriff.Balance.PawnBalance_Sheriff")),
    Enemy("Deputy Winger", Pawn("GD_Population_Sheriff.Balance.PawnBalance_Deputy")),
    Enemy("Mad Dog", Pawn("GD_Population_Psycho.Balance.Unique.PawnBalance_MadDog"), tags=Tag.SlowEnemy),
    Enemy("McNally", Pawn("GD_Population_Psycho.Balance.Unique.PawnBalance_McNally")),
    Enemy("Foreman Rusty", Pawn("GD_Population_Engineer.Balance.Unique.PawnBalance_Foreman")),
    Enemy("BNK-3R", Behavior("GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_4", mode=True), tags=Tag.SlowEnemy),
    Enemy("Jim Kepler", Pawn("GD_BFF_Jim.Population.BD_BFF_Jim"), tags=Tag.MissionEnemy),
    Enemy("Dukino's Mom", Pawn("GD_Population_Skag.Balance.Unique.PawnBalance_Skagzilla")),
    Enemy("Donkey Mong", Pawn("GD_Population_PrimalBeast.Balance.Unique.PawnBalance_PrimalBeast_DonkeyMong"), tags=Tag.RareEnemy),
    Enemy("King Mong", Pawn("GD_Population_PrimalBeast.Balance.Unique.PawnBalance_PrimalBeast_KingMong"), tags=Tag.RareEnemy),
    Enemy("Geary", Pawn("GD_EasterEggs.Balance.Unique.PawnBalance_Smagal"), tags=Tag.SlowEnemy),
    Enemy("Mortar", Pawn("GD_Population_Rat.Balance.Unique.PawnBalance_Mortar")),
    Enemy("Hunter Hellquist", Pawn("GD_Population_Engineer.Balance.Unique.PawnBalance_DJHyperion")),
    Enemy("Bone Head 2.0", Pawn("GD_Population_Loader.Balance.Unique.PawnBalance_BoneHead2")),
    Enemy("Saturn", Pawn("GD_Population_Loader.Balance.Unique.PawnBalance_LoaderGiant")),
    Enemy("The Warrior",
        Behavior("Boss_Volcano_Combat_Monster.TheWorld:PersistentLevel.Main_Sequence.SeqAct_ApplyBehavior_16.Behavior_SpawnItems_6", mode=True),
        Behavior("Boss_Volcano_Combat_Monster.TheWorld:PersistentLevel.Main_Sequence.SeqAct_ApplyBehavior_31.Behavior_SpawnItems_6", mode=True),
        Behavior("Boss_Volcano_Combat_Monster.TheWorld:PersistentLevel.Main_Sequence.SeqAct_ApplyBehavior_59.Behavior_SpawnItems_6", mode=True),
    tags=Tag.SlowEnemy),
    Enemy("Terramorphous the Invincible",
        Pawn("GD_Population_Thresher.Balance.Unique.PawnBalance_ThresherRaid"),
        Behavior("GD_ThresherShared.Anims.Anim_Raid_Death1:BehaviorProviderDefinition_29.Behavior_SpawnItems_46", mode=False),
        Behavior("GD_ThresherShared.Anims.Anim_Raid_Death1:BehaviorProviderDefinition_29.Behavior_SpawnItems_47", mode=False),
    tags=Tag.RaidEnemy|Tag.SlowEnemy),

    Enemy("Tinkles", Pawn("GD_Orchid_Pop_StalkerPet.PawnBalance_Orchid_StalkerPet"), tags=Tag.PiratesBooty),
    Enemy("The Big Sleep", Pawn("GD_Orchid_Pop_Sandman.Balance.PawnBalance_Orchid_BigSleep"), tags=Tag.PiratesBooty),
    Enemy("Sandman", Pawn("GD_Orchid_Pop_Sandman.Balance.PawnBalance_Orchid_Sandman_Solo"), tags=Tag.PiratesBooty),
    Enemy("Grendel", Pawn("GD_Orchid_Pop_Grendel.PawnBalance_Orchid_Grendel"), tags=Tag.PiratesBooty),
    Enemy("Benny the Booster", Pawn("GD_Orchid_Pop_Deserters.Deserter1.PawnBalance_Orchid_Deserter1"), tags=Tag.PiratesBooty),
    Enemy("Deckhand", Pawn("GD_Orchid_Pop_Deserters.Deserter2.PawnBalance_Orchid_Deserter2"), tags=Tag.PiratesBooty),
    Enemy("Toothless Terry", Pawn("GD_Orchid_Pop_Deserters.Deserter3.PawnBalance_Orchid_Deserter3"), tags=Tag.PiratesBooty|Tag.SlowEnemy|Tag.MissionEnemy|Tag.LongMission),
    Enemy("P3RV-E", Pawn("GD_Orchid_Pop_Pervbot.PawnBalance_Orchid_Pervbot"), tags=Tag.PiratesBooty|Tag.SlowEnemy),
    Enemy("H3RL-E", Pawn("GD_Orchid_Pop_LoaderBoss.Balance.PawnBalance_Orchid_LoaderBoss"), tags=Tag.PiratesBooty|Tag.SlowEnemy),
    Enemy("DJ Tanner", Pawn("GD_Orchid_Pop_PirateRadioGuy.PawnBalance_Orchid_PirateRadioGuy"), tags=Tag.PiratesBooty|Tag.SlowEnemy),
    Enemy("Lieutenant White", Pawn("GD_Orchid_Pop_ScarlettCrew.Balance.PawnBalance_Orchid_PirateHenchman"), tags=Tag.PiratesBooty|Tag.MissionEnemy|Tag.VeryLongMission),
    Enemy("Lieutenant Hoffman", Pawn("GD_Orchid_Pop_ScarlettCrew.Balance.PawnBalance_Orchid_PirateHenchman2"), tags=Tag.PiratesBooty|Tag.MissionEnemy|Tag.VeryLongMission),
    Enemy("Mr. Bubbles", Pawn("GD_Orchid_Pop_BubblesLilSis.Balance.PawnBalance_Orchid_Bubbles"), tags=Tag.PiratesBooty|Tag.RareEnemy),
    Enemy("Lil' Sis", Behavior("GD_Orchid_LittleSis.Character.AIDef_Orchid_LittleSis:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_85", mode=True), tags=Tag.PiratesBooty|Tag.RareEnemy),
    Enemy("Captain Scarlett", Behavior("GD_Orchid_PirateQueen_Combat.Animation.Anim_Farewell:BehaviorProviderDefinition_0.Behavior_SpawnItems_10", mode=True), tags=Tag.PiratesBooty|Tag.MissionEnemy|Tag.VeryLongMission),
    Enemy("Leviathan", Leviathan(), tags=Tag.PiratesBooty|Tag.SlowEnemy|Tag.MissionEnemy|Tag.VeryLongMission),
    Enemy("Hyperius the Invincible",
        Pawn("GD_Orchid_Pop_RaidEngineer.PawnBalance_Orchid_RaidEngineer"),
        Behavior("GD_Orchid_RaidEngineer.Death.BodyDeath_Orchid_RaidEngineer:BehaviorProviderDefinition_6.Behavior_SpawnItems_203", block_included=True),
        Behavior("GD_Orchid_RaidEngineer.Death.BodyDeath_Orchid_RaidEngineer:BehaviorProviderDefinition_6.Behavior_SpawnItems_204", block_included=True),
    tags=Tag.PiratesBooty|Tag.RaidEnemy),
        # To restore lootsplosion, modify (and on Disable(), revert) GD_Orchid_ItemPools.Raid.PoolList_Orchid_Raid1_Items
    Enemy("Master Gee the Invincible",
        Pawn("GD_Orchid_Pop_RaidShaman.Balance.PawnBalance_Orchid_RaidShaman"),
        Behavior("GD_Orchid_RaidShaman.Character.AIDef_Orchid_RaidShaman:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_102", block_included=True),
        Behavior("GD_Orchid_RaidShaman.Character.AIDef_Orchid_RaidShaman:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_103", block_included=True),
        Behavior("GD_Orchid_RaidShaman.Character.AIDef_Orchid_RaidShaman:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_257", block_included=True),
        Behavior("Transient.Behavior_SpawnItems_Orchid_MasterGeeDeath", block_included=True),
    tags=Tag.PiratesBooty|Tag.RaidEnemy|Tag.SlowEnemy),

    Enemy("Arena Goliath", Pawn("GD_Iris_Population_Goliath.Balance.Iris_PawnBalance_ArenaGoliath"), tags=Tag.CampaignOfCarnage|Tag.MissionEnemy),
    Enemy("Hamhock the Ham", Pawn("GD_Iris_Population_Biker.Balance.Unique.Iris_PawnBalance_BB_Hamlock"), tags=Tag.CampaignOfCarnage|Tag.MissionEnemy),
    Enemy("Anonymous Troll Face", Pawn("GD_Iris_Population_Biker.Balance.Unique.Iris_PawnBalance_SayFaceTroll"), tags=Tag.CampaignOfCarnage|Tag.MissionEnemy),
    Enemy("Sully the Stabber", Pawn("GD_Iris_Population_Marauder.Balance.Iris_PawnBalance_SullyTheStabber"), tags=Tag.CampaignOfCarnage|Tag.SlowEnemy|Tag.MissionEnemy),
    Enemy("Motor Momma", Pawn("GD_Iris_Population_MotorMama.Balance.Iris_PawnBalance_MotorMama"), tags=Tag.CampaignOfCarnage|Tag.SlowEnemy),
    Enemy("Badassasarus Rex/Piston",
        Pawn("GD_Iris_Population_TAS.Balance.Iris_PawnBalance_Truckasaurus"),
        Pawn("GD_Iris_Population_PistonBoss.Balance.Iris_PawnBalance_PistonBoss"),
        Pawn("GD_Iris_Population_TAS.Balance.Iris_PawnBalance_Truckasaurus_Runable"),
    tags=Tag.CampaignOfCarnage|Tag.SlowEnemy),
    Enemy("Pyro Pete the Invincible",
        Pawn("GD_Iris_Population_RaidPete.Balance.Iris_PawnBalance_RaidPete"),
        Behavior("GD_Iris_Raid_PyroPete.Death.BodyDeath_Iris_Raid_PyroPete:BehaviorProviderDefinition_6.Behavior_SpawnItems_5", block_included=True),
        Behavior("GD_Iris_Raid_PyroPete.Death.BodyDeath_Iris_Raid_PyroPete:BehaviorProviderDefinition_6.Behavior_SpawnItems_6", block_included=True),
        Behavior("GD_Iris_Raid_PyroPete.Death.BodyDeath_Iris_Raid_PyroPete:BehaviorProviderDefinition_6.Behavior_SpawnItems_7", block_included=True),
        Behavior("GD_Iris_Raid_PyroPete.Death.BodyDeath_Iris_Raid_PyroPete:BehaviorProviderDefinition_6.Behavior_SpawnItems_8", block_included=True),
        Behavior("GD_Iris_Raid_PyroPete.Death.BodyDeath_Iris_Raid_PyroPete:BehaviorProviderDefinition_6.Behavior_SpawnItems_9", mode=False, block_included=True),
    tags=Tag.CampaignOfCarnage|Tag.RaidEnemy),
    Enemy("The Monster Truck", MonsterTruck(), tags=Tag.CampaignOfCarnage|Tag.MissionEnemy),
    Enemy("Chubby Rakk (Gas Guzzlers)", Pawn("GD_Iris_Population_Rakk.Balance.Iris_PawnBalance_RakkChubby"), tags=Tag.CampaignOfCarnage|Tag.MissionEnemy),
    Enemy("BuffGamer G", Pawn("GD_Iris_Population_Biker.Balance.Unique.Iris_PawnBalance_BB_JohnnyAbs"), tags=Tag.CampaignOfCarnage|Tag.MissionEnemy|Tag.LongMission),
    Enemy("Game Critic Extraordinaire", Pawn("GD_Iris_Population_Biker.Balance.Unique.Iris_PawnBalance_BB_TonyGlutes"), tags=Tag.CampaignOfCarnage|Tag.MissionEnemy|Tag.LongMission),


    # Enemy("Chubby/Tubby", Pawn(""), tags=Tag.VeryRareEnemy),
    Enemy("Loot Midget", Midget(), tags=Tag.RareEnemy),
    Enemy("Loot Midget (Doctor's Orders)", WildlifeMidget(), tags=Tag.MissionEnemy),
    # Enemy("Loot Midget (Space Cowboy)", Pawn(""), tags=Tag.FightForSanctuary|Tag.MissionEnemy),

    Enemy("Lt. Hoffman", Pawn("GD_Anemone_Pop_NP.Balance.PawnBalance_NP_Lt_Hoffman"), tags=Tag.FightForSanctuary),
)


"""
multiple duplicate loot rolls based on category
guaranteed "hint" item drop

- loot midgets (collectively)
    - doctor's orders + space cowboy midgets = Tag.MissionEnemy
    - all other loot midgets = Tag.RareEnemy

- tubbies (collectively)
- RoG giants? (collectively)

- goliath = Tag.EvolvedEnemy
    - plant goliath
    - corrosive goliath
    - blaster goliath
    - heavy goliath
    - badass goliath
    - midget goliath
    - loot midget goliath
    - snow goliath
    - digger goliath
    - arena goliath

- OOO = Tag.EvolvedEnemy|Tag.RareEnemy
- ulti varkid = Tag.EvolvedEnemy|Tag.RareEnemy
- vermi = Tag.EvolvedEnemy|Tag.RaidEnemy|Tag.RareEnemy
- iron god = Tag.EvolvedEnemy|Tag.RaidEnemy

OOO
    - GD_Native_Badass.Anims.Anim_Badass_Warcry:BehaviorProviderDefinition_0.Behavior_AIChangeInventory_38
        - NewItemPoolList
        - NewItemPoolIncludedLists
    - 

Geary
    - Tag.SlowEnemy
    - Additionally give guaranteed item drop from each easter egg chest

"""
