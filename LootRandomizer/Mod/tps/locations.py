from unrealsdk import Log, FindObject, KeepAlive
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct

from ..defines import *

from ..locations import Behavior, MapDropper
from ..enemies import Enemy, Pawn
from ..missions import Mission, MissionDefinition, MissionDefinitionAlt
from ..missions import MissionDropper, MissionStatusDelegate
from ..other import Other, Attachment

from typing import Dict, List, Optional, Sequence


class WorldUniques(MapDropper):
    paths = ("*",)
    blacklists: Dict[UObject, Sequence[UObject]]

    def enable(self) -> None:
        super().enable()

        self.blacklists = dict()

        for pool_path, blacklist_paths in {
            "GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_04_Rare": (
                "gd_cork_weap_assaultrifle.A_Weapons_Unique.AR_Vladof_3_OldPainful",
            ),
            "GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_04_Rare": (
                "GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Torgue_3_JackOCannon",
                "GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_Boomacorn",
            ),
            "GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_04_Rare": (
                "GD_Cork_Weap_SniperRifles.A_Weapons_Unique.Sniper_Vladof_3_TheMachine",
            ),
        }.items():
            pool = FindObject("ItemPoolDefinition", pool_path)
            if not pool:
                raise Exception(f"Could not find blacklisted world item pool {pool_path}")

            blacklist: List[UObject] = []
            for blacklist_path in blacklist_paths:
                blacklist_item = FindObject("WeaponBalanceDefinition", blacklist_path)
                if not blacklist_item:
                    raise Exception(f"Could not find blacklisted world item {blacklist_path}")
                KeepAlive(blacklist_item)
                blacklist.append(blacklist_item)
            
            self.blacklists[pool] = tuple(blacklist)

    def entered_map(self) -> None:
        for pool, blacklist in self.blacklists.items():
            pool.BalancedItems = tuple(
                convert_struct(balanced_item)
                for balanced_item in pool.BalancedItems
                if balanced_item.InvBalanceDefinition not in blacklist
            )


class LastRequests(MissionDropper, MapDropper):
    paths = ("Deadsurface_P",)

    def entered_map(self) -> None:
        tom = FindObject("WillowInteractiveObject", "Deadsurface_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_5")
        if not tom:
            raise Exception("Could not locate Tom for Last Requests")

        kernel = get_behaviorkernel()
        handle = (tom.ConsumerHandle.PID,)
        bpd = tom.InteractiveObjectDefinition.BehaviorProviderDefinition

        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Disable", 2)
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Default", 1)


class FriskedCorpse(MissionDropper, MapDropper):
    corpse: Optional[str]

    def __init__(self, map_name: str, corpse: str) -> None:
        super().__init__(map_name)
        self.corpse = corpse

    def entered_map(self) -> None:
        def hook(caller: UObject, function: UFunction, params: FStruct) -> bool:
            if UObject.PathName(caller) != self.corpse:
                return True

            mission = self.location.mission
            if not mission:
                raise Exception(f"No mission for corpse for {self.location.name}")

            if mission.current_status is not Mission.Status.Active:
                return True

            spawn_loot(
                self.location.prepare_pools(),
                mission.mission_definition.uobject,
                convert_struct(caller.Location)
            )
            return True

        RunHook("WillowGame.WillowInteractiveObject.UsedBy", f"LootRandomizer.{id(self)}", hook)

    def exited_map(self) -> None:
        RemoveHook("WillowGame.WillowInteractiveObject.UsedBy", f"LootRandomizer.{id(self)}")


class Dick(MapDropper):
    paths = ("Deadsurface_P",)

    def entered_map(self) -> None:
        bpd = FindObject("BehaviorProviderDefinition", "GD_Co_LastRequests.M_LastRequests:BehaviorProviderDefinition_0")
        if not bpd:
            raise Exception("Could not located BPD for calling Nel a dick")
        
        bpd.BehaviorSequences[0].ConsolidatedOutputLinkData[0].ActivateDelay = 11.25
        bpd.BehaviorSequences[0].ConsolidatedOutputLinkData[1].ActivateDelay = 11.25

        def hook(caller: UObject, function: UFunction, params: FStruct) -> bool:
            if UObject.PathName(caller) != "GD_Co_LastRequests.M_LastRequests:Behavior_AddMissionDirectives_2":
                return True

            for pawn in get_pawns():
                if pawn.AIClass.Name == "CharClass_Nel":
                    break
            else:
                raise Exception("Could not find Nel for calling Nel a dick")

            location = (pawn.Location.X - 20, pawn.Location.Y + 20, pawn.Location.Z - 50)
            spawn_loot(self.location.prepare_pools(), pawn, location, (-370, 354, -10))

            RemoveHook("WillowGame.Behavior_AddMissionDirectives.ApplyBehaviorToContext", f"LootRandomizer.{id(self)}")
            return True

        RunHook("WillowGame.Behavior_AddMissionDirectives.ApplyBehaviorToContext", f"LootRandomizer.{id(self)}", hook)

    def exited_map(self) -> None:
        RemoveHook("WillowGame.Behavior_AddMissionDirectives.ApplyBehaviorToContext", f"LootRandomizer.{id(self)}")


class TorgueO(MapDropper):
    paths = ("Moonsurface_P",)

    def entered_map(self) -> None:
        def hook(caller: UObject, function: UFunction, params: FStruct) -> bool:
            if not (caller.AIClass and caller.AIClass.Name == "CharClass_UniqueCharger"):
                return True
            if params.InstigatedBy.Class.Name != "WillowPlayerController":
                return True

            behavior = FindObject("Behavior_RemoteCustomEvent", "GD_Cork_Weap_Pistol.FiringModes.Bullet_Pistol_Maliwan_MoxxisProbe:Behavior_RemoteCustomEvent_3")
            if not behavior:
                raise Exception("Could not find Probe behavior")

            behavior.ApplyBehaviorToContext(caller, (), None, params.InstigatedBy, None, ())
            return True

        RunHook("WillowGame.WillowAIPawn.TakeDamage", f"LootRandomizer.{id(self)}", hook)

    def exited_map(self) -> None:
        RemoveHook("WillowGame.WillowAIPawn.TakeDamage", f"LootRandomizer.{id(self)}")


class SwordInStone(MapDropper):
    paths = ("StantonsLiver_P",)

    def entered_map(self) -> None:
        bpd = FindObject("BehaviorProviderDefinition", "GD_Co_EasterEggs.Excalibastard.InteractiveObject_Excalibastard:BehaviorProviderDefinition_0")
        if not bpd:
            raise Exception("Could not find BPD for Sword In The Stone")
        bpd.BehaviorSequences[0].EventData2[0].OutputLinks.ArrayIndexAndLength = 327681


class ToArms(MapDropper):
    paths = ("Moon_P",)

    objective: UObject
    count_advancements: Dict[int, UObject]

    def enable(self) -> None:
        super().enable()
        objective = FindObject("MissionObjectiveDefinition", "GD_Co_ToArms.M_Co_ToArms:DonateWeapons10")
        adv1 = FindObject("Behavior_AdvanceObjectiveSet", "GD_Co_ToArms.M_Co_ToArms:Behavior_AdvanceObjectiveSet_243")
        adv2 = FindObject("Behavior_AdvanceObjectiveSet", "GD_Co_ToArms.M_Co_ToArms:Behavior_AdvanceObjectiveSet_250")
        adv3 = FindObject("Behavior_AdvanceObjectiveSet", "GD_Co_ToArms.M_Co_ToArms:Behavior_AdvanceObjectiveSet_255")
        adv4 = FindObject("Behavior_AdvanceObjectiveSet", "GD_Co_ToArms.M_Co_ToArms:Behavior_AdvanceObjectiveSet_254")
        adv5 = FindObject("Behavior_AdvanceObjectiveSet", "GD_Co_ToArms.M_Co_ToArms:Behavior_AdvanceObjectiveSet_252")

        if not (objective and adv1 and adv2 and adv3 and adv4 and adv5):
            raise Exception("Could not locate mission objective for To Arms")

        self.objective = objective
        self.objective.ObjectiveCount = 5

        self.count_advancements = {1: adv1, 2: adv2, 3: adv3, 4: adv4, 5: adv5}

    def entered_map(self) -> None:
        def open_hook(caller: UObject, function: UFunction, params: FStruct) -> bool:
            caller.MailBoxStorage.ChestSlots = 1
            return True
        RunHook("WillowGame.MailBoxGFxMovie.extInitMainPanel", f"LootRandomizer.{id(self)}", open_hook)
        
        def deposit_hook(caller: UObject, function: UFunction, params: FStruct) -> bool:
            if UObject.PathName(caller) != "GD_Co_ToArms.M_Co_ToArms:Behavior_MissionRemoteEvent_392":
                return True
            
            count = get_missiontracker().GetObjectiveCount(self.objective)
            advancement = self.count_advancements.get(count)
            if not advancement:
                raise Exception("Unexpected donation count for To Arms")

            advancement.ApplyBehaviorToContext(
                params.ContextObject, (), params.SelfObject,
                params.MyInstigatorObject, params.OtherEventParticipantObject, ()
            )

            return True
        RunHook("WillowGame.Behavior_MissionRemoteEvent.ApplyBehaviorToContext", f"LootRandomizer.{id(self)}", deposit_hook)

    def exited_map(self) -> None:
        RemoveHook("WillowGame.MailBoxGFxMovie.extInitMainPanel", f"LootRandomizer.{id(self)}")
        RemoveHook("WillowGame.Behavior_MissionRemoteEvent.ApplyBehaviorToContext", f"LootRandomizer.{id(self)}")


    def disable(self) -> None:
        self.objective.ObjectiveCount = 50


class PopRacing(MapDropper):
    paths = ("Moon_P",)

    def entered_map(self) -> None:
        loaded1 = FindObject("SeqEvent_LevelLoaded", "Moon_SideMissions.TheWorld:PersistentLevel.Main_Sequence.PopRacing.SeqEvent_LevelLoaded_1")
        loaded6 = FindObject("SeqEvent_LevelLoaded", "Moon_SideMissions.TheWorld:PersistentLevel.Main_Sequence.PopRacing.SeqEvent_LevelLoaded_6")
        if not (loaded1 and loaded6):
            raise Exception("Could not located loading sequences for Pop Racing")
        
        loaded1.OutputLinks[0].Links = ()
        loaded6.OutputLinks[0].Links = ()


class Zapped1(MissionDropper, MapDropper):
    paths = ("Moon_P",)

    def entered_map(self) -> None:
        if self.location.current_status not in (Mission.Status.NotStarted, Mission.Status.Complete):
            return

        box = FindObject("WillowInteractiveObject", "Moon_SideMissions.TheWorld:PersistentLevel.WillowInteractiveObject_114")
        if not box:
            raise Exception("Could not locate box for Zapped 1.0")

        kernel = get_behaviorkernel()
        handle = (box.ConsumerHandle.PID,)
        bpd = box.InteractiveObjectDefinition.BehaviorProviderDefinition

        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "AcceptedMission", 2)
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "MissionAvailable", 1)


class Boomshakalaka(MissionStatusDelegate, MapDropper):
    paths = ("Outlands_P2",)

    def entered_map(self) -> None:
        if self.location.current_status is Mission.Status.Active:
            self.set_hoop_collision(1) #COLLIDE_NoCollision

    def set_hoop_collision(self, collision: int) -> None:
        hoop = FindObject("WillowInteractiveObject", "Outlands_SideMissions2.TheWorld:PersistentLevel.WillowInteractiveObject_0")
        if not hoop:
            raise Exception("Could not locate hoop for Boomshakalaka")
        
        hoop.Behavior_ChangeCollision(collision) #COLLIDE_NoCollision
        for comp in hoop.AllComponents:
            if comp.Class.Name == "StaticMeshComponent":
                comp.Behavior_ChangeCollision(collision)

    def accepted(self) -> None:
        self.set_hoop_collision(1) #COLLIDE_NoCollision

    def completed(self) -> None:
        self.set_hoop_collision(2) #COLLIDE_BlockAll


class DunksWatson(MapDropper):
    paths = ("Outlands_P2",)

    def entered_map(self) -> None:
        def hook(caller: UObject, function: UFunction, params: FStruct) -> bool:
            if UObject.PathName(caller) != "Outlands_SideMissions2.TheWorld:PersistentLevel.Main_Sequence.Boomshakalaka.SeqAct_ApplyBehavior_4.Behavior_RemoteCustomEvent_0":
                return True

            mission = self.location.mission
            if not mission:
                raise Exception("No mission for Dunks Watson")
            
            for pawn in get_pawns():
                if pawn.AIClass.Name == "CharClass_Superballa":
                    break
            else:
                raise Exception("Could not locate Dunks Watson")
            
            Log(f"dunks sick ups: {pawn.Location.Z}")

            spawn_loot(
                self.location.prepare_pools(),
                mission.mission_definition.uobject,
                (-14540.578125, 106299.593750, 8647.15625),
                (0, 0, -4800)
            )
            return True
        RunHook("WillowGame.Behavior_RemoteCustomEvent.ApplyBehaviorToContext", f"LootRandomizer.{id(self)}", hook)

    def exited_map(self) -> None:
        RemoveHook("WillowGame.Behavior_RemoteCustomEvent.ApplyBehaviorToContext", f"LootRandomizer.{id(self)}")


class SpaceSlam(MissionStatusDelegate, MapDropper):
    paths = ("Outlands_P2",)

    def apply(self) -> None:
        for pawn in get_pawns():
            if pawn.AIClass and pawn.AIClass.Name == "CharClass_Tog":
                pawn.SetUsable(True, None, 0)
                break
        else:
            raise Exception("Could not locate Tog for Space Slam")

    def entered_map(self) -> None:
        self.apply()
    
    def completed(self) -> None:
        self.apply()


class DAHLTraining(MapDropper):
    paths = ("MoonSlaughter_P",)

    def entered_map(self) -> None:
        loaded = FindObject("SeqEvent_LevelLoaded", "MoonSlaughter_Combat.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_LevelLoaded_2")
        tr4nu = FindObject("WillowInteractiveObject", "MoonSlaughter_Combat.TheWorld:PersistentLevel.WillowInteractiveObject_1")

        if not (loaded and tr4nu):
            raise Exception("Could not locate objects for DAHL Combat Training")

        loaded.OutputLinks[0].Links = ()

        kernel = get_behaviorkernel()
        handle = (tr4nu.ConsumerHandle.PID,)
        bpd = tr4nu.InteractiveObjectDefinition.BehaviorProviderDefinition

        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Disabled", 2)
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Enabled", 1)


Locations = (
    Other("World Uniques", WorldUniques(), tags=Tag.Excluded),
    Enemy("Flame Knuckle",
        Pawn("PawnBalance_DahlPowersuit_Knuckle"),
        Pawn("PawnBalance_DahlSergeantFlameKnuckle"),
    tags=Tag.Excluded),

    Mission("Tales from Elpis", MissionDefinition("GD_Co_TalesFromElpis.M_TalesFromElpis")),
    Enemy("Son of Flamey", Pawn("PawnBalance_SonFlamey")),
    Enemy("Grandson of Flamey", Pawn("PawnBalance_GrandsonFlamey")),
    Enemy("Badass Kraggon", Pawn("PawnBalance_ElementalSpitterBadass"), tags=Tag.VeryRareEnemy),
    Enemy("Phonic Kraggon", Pawn("PawnBalance_ElementalPhonic"), tags=Tag.RareEnemy),
    Mission("Land Among the Stars", MissionDefinition("GD_Co_Motivation.M_Motivation")),
    Mission("Follow Your Heart", MissionDefinition("GD_Co_FollowYourHeart.M_FollowYourHeart"), tags=Tag.LongMission),
    Enemy("Deadlift", Pawn("PawnBalance_SpacemanDeadlift"), tags=Tag.SlowEnemy),
    Mission("Last Requests",
        MissionDefinition("GD_Co_LastRequests.M_LastRequests"),
        LastRequests(),
    tags=Tag.LongMission),
    # Tom's Corpse not interactible after completion
    Enemy("Tom Thorson",
        FriskedCorpse("Deadsurface_P", "Deadsurface_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_5"),
    mission="Last Requests"),
    Enemy("Squat", Pawn("PawnBalance_Squat"), mission="Last Requests"),
    Enemy("Nel (Called a Dick)", Dick(), mission="Last Requests"),
    Enemy("Nel", Pawn("PawnBalance_Nel"), tags=Tag.SlowEnemy),
    Mission("Nova? No Problem!", MissionDefinition("GD_Co_NovaNoProblem.M_NovaNoProblem")),
    Other("Janey's Chest", Attachment("BD_DahlShockChest"), mission="Nova? No Problem!"),
    Mission("Torgue-o! Torgue-o! (Turn in Janey)", MissionDefinition("GD_Co_ToroToro.M_ToroToro"), TorgueO()),
    Mission("Torgue-o! Torgue-o! (Turn in Lava)", MissionDefinitionAlt("GD_Co_ToroToro.M_ToroToro"), TorgueO()),
    Enemy("Antagonized Kraggon", Pawn("PawnBalance_UniqueCharger"), mission="Torgue-o! Torgue-o! (Turn in Janey)", rarities=(5,)),
    Mission("Wherefore Art Thou?", MissionDefinition("GD_Co_WhereforeArtThou.M_Co_WhereforeArtThou"), tags=Tag.LongMission|Tag.VehicleMission),
    Enemy("Maureen", Pawn("PawnBalance_MaureenRider"), mission="Wherefore Art Thou?"),
    Mission("All the Little Creatures", MissionDefinition("gd_cork_allthelittlecreatures.M_AllTheLittleCreatures")),
    Enemy("Even-More-Disgusting Tork", Pawn("PawnBalance_NotCuteBadassTork")),
    Other("Sword in the Stone",
        SwordInStone(),
        Behavior("GD_Co_EasterEggs.Excalibastard.InteractiveObject_Excalibastard:BehaviorProviderDefinition_0.Behavior_SpawnItems_44"),
    tags=Tag.Miscellaneous),
    Enemy("Swagman", Pawn("PawnBalance_ScavWastelandWalker")),
    Mission("Recruitment Drive", MissionDefinition("GD_Cork_Resistors.M_Resistors"), tags=Tag.VehicleMission),
    Enemy("Magma Rivers", Pawn("PawnBalance_LittleDarksiderBadassBandit")),
    Enemy("Wally Wrong", Pawn("PawnBalance_DarksiderBadassBandit")),
    Enemy("Fair Dinkum", Pawn("PawnBalance_DarksiderBadassPsycho")),
    Mission("The Empty Billabong", MissionDefinition("GD_Co_EmptyBillabong.M_EmptyBillaBong")),
    Enemy("Jolly Swagman",
        FriskedCorpse("ComFacility_P", "ComFacility_SideMissions.TheWorld:PersistentLevel.WillowInteractiveObject_4"),
    mission="The Empty Billabong"),
    Enemy("Red", Pawn("PawnBalance_Ned")),
    Enemy("Belly", Pawn("PawnBalance_Kelly")),
    Mission("Grinders", MissionDefinition("GD_Cork_Grinding.M_Cork_Grinding"), tags=Tag.VeryLongMission),
    Enemy("Rooster Booster", Pawn("PawnBalance_RoosterBooster")),
    Mission("To Arms!", ToArms(), MissionDefinition("GD_Co_ToArms.M_Co_ToArms"), tags=Tag.VeryLongMission),
    Enemy("PLA Member Tim Pot", Pawn("PawnBalance_TimPot"), mission="To Arms!"),
    Enemy("PLA Member Tom Pot", Pawn("PawnBalance_TomPot"), mission="To Arms!"),
    Enemy("PLA Member Tum Pot", Pawn("PawnBalance_TumPot"), mission="To Arms!"),
    Mission("Bunch of Ice Holes (Turn in Nurse Nina)", MissionDefinition("GD_Co_IceHoles.M_Co_IceHoles")),
    Mission("Bunch of Ice Holes (Turn in B4R-BOT)", MissionDefinitionAlt("GD_Co_IceHoles.M_Co_IceHoles")),
    Enemy("Giant Shuggurath of Ice", Pawn("PawnBalance_GiantCryoHive")),
    Mission("Pop Racing", MissionDefinition("GD_Co_PopRacing.M_Co_PopRacing"), PopRacing(), tags=Tag.VehicleMission),
    Enemy("Lunestalker Snr", Pawn("PawnBalance_LunestalkerSnrRider")),
    Mission("Zapped 1.0", MissionDefinition("GD_Co_Zapped.M_Co_Zapped1", block_weapon=False), Zapped1()),
    Mission("Zapped 2.0", MissionDefinition("GD_Co_Zapped.M_Co_Zapped2", block_weapon=False)),
    Mission("Zapped 3.0", MissionDefinition("GD_Co_Zapped.M_Co_Zapped3", block_weapon=False)),
    Mission("Boomshakalaka", MissionDefinition("GD_Co_Boomshakalaka.M_Boomshakalaka"), Boomshakalaka()),
    Enemy("Dunks Watson", DunksWatson(), mission="Boomshakalaka"),
    Mission("Space Slam", MissionDefinition("GD_Co_SpaceSlam.M_SpaceSlam"), SpaceSlam()),
    Enemy("Tork Dredger", Pawn("PawnBalance_TorkDredger"), tags=Tag.RareEnemy),

    Mission("Boarding Party", MissionDefinition("GD_Co_Boarding_Party.M_BoardingParty")),
    Mission("Cleanliness Uprising", MissionDefinition("GD_Co_Cleanliness_Uprising.M_Cleanliness_Uprising")),
    Mission("The Bestest Story Ever Told", MissionDefinition("GD_Co_CorkRaid.M_CorkRaid")),
    Mission("An Urgent Message", MissionDefinition("GD_Co_Detention.M_Detention")),
    Mission("Don't Shoot the Messenger", MissionDefinition("GD_Co_DontShootMessenger.MissionDef.M_DontShootMsgr")),
    Mission("Guardian Hunter", MissionDefinition("GD_Co_GuardianHunter.MissionDef.M_GuardianHunter")),
    Mission("Sterwin Forever", MissionDefinition("GD_Co_GuardianHunter.MissionDef.M_SterwinForever")),
    Mission("Home Delivery", MissionDefinition("GD_Co_HomeDelivery.M_HomeDelivery")),
    Mission("Hot Head", MissionDefinition("GD_Co_Hot_Head.M_Hot_Head")),
    Mission("Kill Meg", MissionDefinition("GD_Co_Kill_Meg.M_Kill_Meg")),
    Mission("Paint Job", MissionDefinition("GD_Co_Paint_Job.M_Paint_Job")),
    Mission("Handsome AI", MissionDefinition("GD_Co_PushButtonMission.M_PushButtonMission")),
    Mission("Return of Captain Chef", MissionDefinition("GD_Co_ReturnOfCapnChef.M_ReturnOfCaptainChef")),
    Mission("Rough Love", MissionDefinition("GD_Co_RoughLove.M_Co_RoughLove")),
    Mission("The Secret Chamber", MissionDefinition("GD_Co_SecretChamber.M_SecretChamber")),
    Mission("To the Moon", MissionDefinition("GD_Co_Side_EngineerMoonShot.M_EngineerMoonShot")),
    Mission("Things That Go Boom", MissionDefinition("GD_Co_Side_Exploders.M_Exploders")),
    Mission("Fresh Air", MissionDefinition("GD_Co_Side_FreshAir.M_FreshAir")),
    Mission("Lab 19", MissionDefinition("GD_Co_Side_Lab19.M_Lab19")),
    Mission("Lock and Load", MissionDefinition("GD_Co_Side_LockAndLoad.M_LockAndLoad")),
    Mission("Infinite Loop", MissionDefinition("GD_Co_Side_Loop.M_InfiniteLoop")),
    Mission("Picking Up the Pieces", MissionDefinition("GD_Co_Side_PickingUp.M_PickingUpThePieces")),
    Mission("Red, Then Dead", MissionDefinition("GD_Co_Side_Reshirt.M_RedShirt")),
    Mission("It Ain't Rocket Surgery", MissionDefinition("GD_Co_Side_RocketSurgery.M_RocketSurgery")),
    Mission("The Don", MissionDefinition("GD_Co_Side_TheDon.M_TheDon")),
    Mission("These are the Bots", MissionDefinition("GD_Co_Side_TheseAreTheBots.M_TheseAreTheBots")),
    Mission("Z8N-TP", MissionDefinition("GD_Co_Side_Z8MTRP.M_Z8nTRP")),
    Mission("Sub-Level 13", MissionDefinition("GD_Co_SubLevel13.M_Co_SubLevel13Part1")),
    Mission("Sub-Level 13: Part 2", MissionDefinition("GD_Co_SubLevel13.M_Co_SubLevel13Part2")),
    Mission("Treasures of ECHO Madre", MissionDefinition("GD_Co_TreasuresofECHO.M_Co_TreasuresofECHO")),
    Mission("Voice Over", MissionDefinition("GD_Co_VoiceOver.M_VoiceOver")),
    Mission("The Voyage of Captain Chef", MissionDefinition("GD_Co_VoyageOfCaptainChef.M_VoyageOfCaptainChef")),
    Mission("Wiping the Slate", MissionDefinition("GD_Co_WipingSlate.M_WipingSlate")),
    Mission("Nothing is Never an Option", MissionDefinition("GD_Co_YouAskHowHigh.M_Co_YouAskHowHigh")),
    Mission("Another Pickle", MissionDefinition("GD_Cork_AnotherPickle.M_Cork_AnotherPickle")),
    Mission("Quarantine: Back On Schedule", MissionDefinition("GD_Cork_BackOnSchedule.M_BackOnSchedule")),
    Mission("Don't Get Cocky", MissionDefinition("GD_Cork_DontGetCocky.M_DontGetCocky")),
    Mission("Eradicate!", MissionDefinition("GD_Cork_Eradicate.M_Eradicate")),
    Mission("In Perfect Hibernation", MissionDefinition("GD_Cork_PerfectHibernation.M_PerfectHibernation")),
    Mission("Quarantine: Infestation", MissionDefinition("GD_Cork_Quarantine.M_Quarantine")),
    Mission("No Such Thing as a Free Launch", MissionDefinition("GD_Cork_Rocketeering.M_Rocketeering")),
    Mission("Trouble with Space Hurps", MissionDefinition("GD_Cork_TroubleWithSpaceHurps.M_TroubleWithSpaceHurps")),
    Mission("l33t h4X0rz", MissionDefinition("GD_Ma_Side_H4X0rz.M_Ma_Side_H4X0rz_Repeat")),
    Mission("A Deadlier Game", MissionDefinition("GD_Ma_Side_BadTrap.M_Ma_Side_BadTrap")),
    Mission("Byte Club", MissionDefinition("GD_Ma_Side_ByteClub.M_Ma_Side_ByteClub")),
    Mission("Chip's Data Mining Adventure", MissionDefinition("GD_Ma_Side_CookieDataMining.M_Ma_Side_CookieDataMining")),
    Mission("3G0-TP", MissionDefinition("GD_Ma_Side_EgoTrap.M_Ma_Side_EgoTrap")),
    Mission("1D-TP", MissionDefinition("GD_Ma_Side_IdTrap.M_Ma_Side_IdTrap")),
    Mission("Rose Tinting", MissionDefinition("GD_Ma_Side_MINAC.M_Ma_Side_MINAC")),
    Mission("Corrosion of Dignity", MissionDefinition("GD_Ma_Side_ShredOfDignity.M_Ma_Side_ShredOfDignity")),
    Mission("Spyware Who Came in from the Cold", MissionDefinition("GD_Ma_Side_SpywareInFromCold.M_Ma_Side_SpywareInFromCold")),
    Mission("You Can Stop the Music", MissionDefinition("GD_Ma_Side_StopTheMusic.M_Ma_Side_StopTheMusic")),
    Mission("The Sum of Some Fears", MissionDefinition("GD_Ma_Side_SumOfSomeFears.M_Ma_Side_SumOfSomeFears")),
    Mission("5UP4-3G0-TP", MissionDefinition("GD_Ma_Side_SuperEgoTrap.M_Ma_Side_SuperEgoTrap")),
    Mission("The Temple of Boom", MissionDefinition("GD_Ma_Side_TempleOfBoom.M_Ma_Side_TempleofBoom")),
    Mission("h4X0rz", MissionDefinition("GD_Ma_Side_H4X0rz.M_Ma_Side_H4X0rz")),
    Mission("Digistructed Madness: Round 1", MissionDefinition("GD_EridianSlaughter.MissionDef.M_EridianSlaughter01")),
    Mission("Digistructed Madness: Round 2", MissionDefinition("GD_EridianSlaughter.MissionDef.M_EridianSlaughter02")),
    Mission("Digistructed Madness: Round 3", MissionDefinition("GD_EridianSlaughter.MissionDef.M_EridianSlaughter03")),
    Mission("Digistructed Madness: Round 4", MissionDefinition("GD_EridianSlaughter.MissionDef.M_EridianSlaughter04")),
    Mission("Digistructed Madness: Round 5", MissionDefinition("GD_EridianSlaughter.MissionDef.M_EridianSlaughter05")),
    Mission("Digistructed Madness: The Badass Round", MissionDefinition("GD_EridianSlaughter.MissionDef.M_EridianSlaughter_Badass")),

    Mission("DAHL Combat Training: Round 1",
        MissionDefinition("GD_Co_MoonSlaughter.M_Co_MoonSlaughter01", unlink_next=True),
        DAHLTraining(),
    tags=Tag.ShockDrop|Tag.Slaughter|Tag.LongMission),
    Mission("DAHL Combat Training: Round 2",
        MissionDefinition("GD_Co_MoonSlaughter.M_Co_MoonSlaughter02", unlink_next=True),
    tags=Tag.ShockDrop|Tag.Slaughter|Tag.LongMission),
    Mission("DAHL Combat Training: Round 3",
        MissionDefinition("GD_Co_MoonSlaughter.M_Co_MoonSlaughter03", unlink_next=True),
    tags=Tag.ShockDrop|Tag.Slaughter|Tag.LongMission),
    Mission("DAHL Combat Training: Round 4",
        MissionDefinition("GD_Co_MoonSlaughter.M_Co_MoonSlaughter04", unlink_next=True),
    tags=Tag.ShockDrop|Tag.Slaughter|Tag.LongMission),
    Mission("DAHL Combat Training: Round 5",
        MissionDefinition("GD_Co_MoonSlaughter.M_Co_MoonSlaughter05", unlink_next=True),
    tags=Tag.ShockDrop|Tag.Slaughter|Tag.LongMission),
)

"""
TODO:
check corpse drop levels
remove shock drop mission auto-accept

nova no problem safe?
outlands slam plate chest?
"""