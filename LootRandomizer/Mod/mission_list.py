from unrealsdk import Log, FindAll, FindObject, GetEngine, UObject #type: ignore

from .defines import Tag, construct_object, get_pawns, construct_behaviorsequence_behavior
from .locations import Behavior, MapDropper

from .missions import get_tracker, Mission, PreventDestroy, MissionStatusDelegate
from .missions import MissionInventory, MissionObject, MissionPickup, MissionGiver

from typing import Optional


def Enable() -> None:
    for mission in Missions:
        mission.enable()

def Disable() -> None:
    for mission in Missions:
        mission.disable()


class DocMercy(MissionGiver):
    def __init__(self) -> None:
        super().__init__("Frost_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_413.MissionDirectivesDefinition_0", False, False, "Frost_P")
    
    def apply(self) -> UObject:
        giver = super().apply()
        get_tracker().UnregisterMissionDirector(giver)
        return giver


class Loader1340(MapDropper):
    def __init__(self) -> None:
        super().__init__("dam_p")

    def entered_map(self) -> None:
        toggle = FindObject("SeqAct_Toggle", "Dam_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Loader1340.SeqAct_Toggle_1")

        loaded0 = FindObject("SeqEvent_LevelLoaded", "Dam_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Loader1340.SeqEvent_LevelLoaded_0")
        loaded0.OutputLinks[0].Links[0].LinkedOp = toggle

        loaded1 = FindObject("SeqEvent_LevelLoaded", "Dam_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Loader1340.SeqEvent_LevelLoaded_1")
        loaded1.OutputLinks[0].Links[0].LinkedOp = toggle


class WillTheBandit(MapDropper):
    def __init__(self) -> None:
        super().__init__("tundraexpress_p")

    def entered_map(self) -> None:
        toggle = FindObject("SeqAct_Toggle", "TundraExpress_Combat.TheWorld:PersistentLevel.Main_Sequence.NoHardFeelings.SeqAct_Toggle_0")

        loaded0 = FindObject("SeqEvent_LevelLoaded", "TundraExpress_Combat.TheWorld:PersistentLevel.Main_Sequence.NoHardFeelings.SeqEvent_LevelLoaded_0")
        loaded0.OutputLinks[0].Links[0].LinkedOp = toggle
        loaded0.OutputLinks[0].Links[0].InputLinkIdx = 0

        loaded1 = FindObject("SeqEvent_LevelLoaded", "TundraExpress_Combat.TheWorld:PersistentLevel.Main_Sequence.NoHardFeelings.SeqEvent_LevelLoaded_1")
        loaded1.OutputLinks[0].Links[0].LinkedOp = toggle
        loaded1.OutputLinks[0].Links[0].InputLinkIdx = 0


class McShooty(MissionStatusDelegate, MapDropper):
    def __init__(self) -> None:
        super().__init__("Grass_Cliffs_P")

    def accepted(self) -> None:
        for pawn in get_pawns():
            if pawn.bIsDead and pawn.AIClass and pawn.AIClass.Name == "CharClass_Shootyface":
                pawn.bHidden = True
                pawn.CollisionType = 1

    def entered_map(self) -> None:
        destroyreal = FindObject("WillowSeqEvent_MissionRemoteEvent", "Grass_Cliffs_Dynamic.TheWorld:PersistentLevel.Main_Sequence.ShootMeInTheFace.WillowSeqEvent_MissionRemoteEvent_2")
        destroyreal.OutputLinks[0].Links = ()

        shooty_bpd = FindObject("BehaviorProviderDefinition", "GD_Shootyface.Character.CharClass_Shootyface:BehaviorProviderDefinition_0")
        shooty_bpd.BehaviorSequences[1].EventData2[0].OutputLinks.ArrayIndexAndLength = 327681
        shooty_bpd.BehaviorSequences[2].EventData2[0].OutputLinks.ArrayIndexAndLength = 0


class BFFs(MapDropper):
    def __init__(self) -> None:
        super().__init__("SanctuaryAir_P")

    def entered_map(self) -> None:
        toggle0 = FindObject("SeqAct_Toggle", "SanctuaryAir_Side.TheWorld:PersistentLevel.Main_Sequence.BFFs.SeqAct_Toggle_0")
        toggle1 = FindObject("SeqAct_Toggle", "SanctuaryAir_Side.TheWorld:PersistentLevel.Main_Sequence.BFFs.SeqAct_Toggle_1")

        loaded1 = FindObject("SeqEvent_LevelLoaded", "SanctuaryAir_Side.TheWorld:PersistentLevel.Main_Sequence.BFFs.SeqEvent_LevelLoaded_1")
        loaded1.OutputLinks[0].Links[0].LinkedOp = toggle1
        loaded1.OutputLinks[0].Links[1].LinkedOp = toggle0

        loaded2 = FindObject("SeqEvent_LevelLoaded", "SanctuaryAir_Side.TheWorld:PersistentLevel.Main_Sequence.BFFs.SeqEvent_LevelLoaded_2")
        loaded2.OutputLinks[0].Links[0].LinkedOp = toggle1

        loaded3 = FindObject("SeqEvent_LevelLoaded", "SanctuaryAir_Side.TheWorld:PersistentLevel.Main_Sequence.BFFs.SeqEvent_LevelLoaded_3")
        loaded3.OutputLinks[0].Links[0].LinkedOp = toggle0

        aiscripted = FindObject("WillowSeqAct_AIScripted", "SanctuaryAir_Side.TheWorld:PersistentLevel.Main_Sequence.BFFs.WillowSeqAct_AIScripted_0")
        aiscripted.InputLinks[0].bDisabled = True

        gamestage_region = FindObject("WillowRegionDefinition", "GD_GameStages.Zone3.Sanctuary_C")
        for path in (
            "SanctuaryAir_Side.TheWorld:PersistentLevel.WillowPopulationOpportunityPoint_1",
            "SanctuaryAir_Side.TheWorld:PersistentLevel.WillowPopulationOpportunityPoint_6",
            "SanctuaryAir_Side.TheWorld:PersistentLevel.WillowPopulationOpportunityPoint_7",
            "SanctuaryAir_Side.TheWorld:PersistentLevel.WillowPopulationOpportunityPoint_8",
        ):
            FindObject("WillowPopulationOpportunityPoint", path).GameStageRegion = gamestage_region


class PoeticLicense(MapDropper):
    def __init__(self) -> None:
        super().__init__("SanctuaryAir_P")

    def entered_map(self) -> None:
        daisy_den = FindObject("PopulationOpportunityDen", "SanctuaryAir_Dynamic.TheWorld:PersistentLevel.PopulationOpportunityDen_2")
        daisy_den.GameStageRegion = FindObject("WillowRegionDefinition", "GD_GameStages.Zone2.Cliffs_A")

        daisy_ai = FindObject("AIBehaviorProviderDefinition", "GD_Daisy.Character.AIDef_Daisy:AIBehaviorProviderDefinition_1")
        daisy_ai.BehaviorSequences[2].BehaviorData2[11].Behavior = construct_object("Behavior_Kill", daisy_ai)
        daisy_ai.BehaviorSequences[5].BehaviorData2[2].OutputLinks.ArrayIndexAndLength = 1

        seq_objective = FindObject("SeqAct_ApplyBehavior", "SanctuaryAir_Dynamic.TheWorld:PersistentLevel.Main_Sequence.PoeticLicense.SeqAct_ApplyBehavior_1")
        timetodie = FindObject("SeqEvent_RemoteEvent", "SanctuaryAir_Dynamic.TheWorld:PersistentLevel.Main_Sequence.PoeticLicense.SeqEvent_RemoteEvent_2")
        timetodie.OutputLinks[0].Links = ((seq_objective, 0),)


class WrittenByTheVictor(MapDropper):
    def __init__(self) -> None:
        super().__init__("HyperionCity_P")

    def entered_map(self) -> None:
        missionevent = FindObject("WillowSeqEvent_MissionRemoteEvent", "HyperionCity_Dynamic.TheWorld:PersistentLevel.Main_Sequence.WrittenByVictor.WillowSeqEvent_MissionRemoteEvent_1")
        missionevent.OutputLinks[0].Links = ()


class GreatEscape(MissionStatusDelegate, MapDropper):
    def __init__(self) -> None:
        super().__init__("CraterLake_P")

    def completed(self) -> None:
        self.location.uobject.bRepeatable = False

    def entered_map(self) -> None:
        self.location.uobject.bRepeatable = True

        pawn = GetEngine().GetCurrentWorldInfo().PawnList
        while pawn:
            if pawn.AIClass and pawn.AIClass.Name == "CharClass_Ulysses":
                get_tracker().RegisterMissionDirector(pawn)
                break
            pawn = pawn.NextPawn

        ulysses_loaded = FindObject("SeqEvent_LevelLoaded", "CraterLake_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Ulysess.SeqEvent_LevelLoaded_0")
        ulysses_loaded.OutputLinks[0].Links = ()

        ulysses_savestate = FindObject("SeqEvent_RemoteEvent", "CraterLake_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Ulysess.SeqEvent_RemoteEvent_1")
        ulysses_savestate.OutputLinks[0].Links = ()


class MessageInABottle(MapDropper, MissionStatusDelegate):
    path: str
    def __init__(self, path: Optional[str], map_name: str) -> None:
        self.path = path
        super().__init__(map_name)

    def accepted(self) -> None:
        for chest in FindAll("WillowInteractiveObject"):
            if UObject.PathName(chest.InteractiveObjectDefinition) == "GD_Orchid_SM_Message_Data.MO_Orchid_XMarksTheSpot":
                directive = (self.location.uobject, False, True)
                chest.AddMissionDirective(directive, True)


    def entered_map(self) -> None:
        bottle_bpd = FindObject("BehaviorProviderDefinition", "GD_Orchid_SM_Message_Data.MessageBottle.MO_Orchid_MessageBottle:BehaviorProviderDefinition_3")
        bottle_active = FindObject("Behavior_ChangeRemoteBehaviorSequenceState", "GD_Orchid_Plot.M_Orchid_PlotMission01:Behavior_ChangeRemoteBehaviorSequenceState_6")

        bottle_bpd.BehaviorSequences[1].BehaviorData2[0].Behavior = bottle_active
        bottle_bpd.BehaviorSequences[1].BehaviorData2[0].OutputLinks.ArrayIndexAndLength = 0

        if self.path:
            chest_state = FindObject("BehaviorSequenceEnableByMission", self.path)
            chest_state.MissionStatesToLinkTo.bComplete = False


class RollInsight(MissionGiver):
    def apply(self) -> UObject:
        directives = super().apply()

        die = FindObject("WillowInteractiveObject", "Village_Mission.TheWorld:PersistentLevel.WillowInteractiveObject_297")
        handle = (die.ConsumerHandle.PID,)
        bpd = die.InteractiveObjectDefinition.BehaviorProviderDefinition

        kernel = FindObject("BehaviorKernel", "GearboxFramework.Default__BehaviorKernel")
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Complete", 2)
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "TurnIn", 1)

        die.SetMissionDirectivesUsability(1)
        get_tracker().RegisterMissionDirector(die)

        return directives


class LostSouls(MissionGiver):
    def apply(self) -> UObject:
        directives = super().apply()
        for pawn in get_pawns():
            if pawn.MissionDirectives == directives:
                handle = (pawn.ConsumerHandle.PID,)
                bpd = pawn.AIClass.AIDef.BehaviorProviderDefinition
                kernel = FindObject("BehaviorKernel", "GearboxFramework.Default__BehaviorKernel")
                kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Mission", 1)
                pawn.SetUsable(True, None, 0)
                get_tracker().RegisterMissionDirector(pawn)

    def entered_map(self) -> None:
        if get_tracker().GetMissionStatus(self.location.uobject) == 4:
            skel_den = FindObject("PopulationOpportunityDen", "Dead_Forest_Mission.TheWorld:PersistentLevel.PopulationOpportunityDen_19")
            skel_den.IsEnabled = True
            knight_den = FindObject("PopulationOpportunityDen", "Dead_Forest_Mission.TheWorld:PersistentLevel.PopulationOpportunityDen_13")
            knight_den.IsEnabled = False


class MyDeadBrother(MapDropper):
    def __init__(self) -> None:
        super().__init__("Dungeon_P")

    def entered_map(self) -> None:
        if get_tracker().GetMissionStatus(self.location.uobject) != 4:
            return

        simon_enabled = FindObject("BehaviorSequenceEnableByMission", "GD_Wizard_DeadBrotherSimon_Proto2.Character.CharClass_Wizard_DeadBrotherSimon_Proto2:BehaviorProviderDefinition_5.BehaviorSequenceEnableByMission_9")
        simon_enabled.MissionStatesToLinkTo.bComplete = True

        simon_talking = FindObject("BehaviorSequenceEnableByMission", "GD_Wizard_DeadBrotherSimon_Proto2.Character.CharClass_Wizard_DeadBrotherSimon_Proto2:BehaviorProviderDefinition_5.BehaviorSequenceEnableByMission_7")
        simon_talking.MissionStatesToLinkTo.bComplete = False

        simon_bpd = FindObject("BehaviorProviderDefinition", "GD_Wizard_DeadBrotherSimon_Proto2.Character.CharClass_Wizard_DeadBrotherSimon_Proto2:BehaviorProviderDefinition_5")

        simon_bpd.BehaviorSequences[4].BehaviorData2[1].Behavior = construct_behaviorsequence_behavior(
            "GD_Wizard_DeadBrotherSimon_Proto2", "Character", "CharClass_Wizard_DeadBrotherSimon_Proto2", "BehaviorProviderDefinition_5",
            sequence="TurnInSimon", outer=simon_bpd
        )

        simon_den = FindObject("PopulationOpportunityDen", "Dungeon_Mission.TheWorld:PersistentLevel.PopulationOpportunityDen_68")
        simon_den.IsEnabled = True


class OddestCouple(MissionObject):
    def apply(self) -> UObject:
        door = super().apply()
        handle = (door.ConsumerHandle.PID,)
        bpd = door.InteractiveObjectDefinition.BehaviorProviderDefinition

        kernel = FindObject("BehaviorKernel", "GearboxFramework.Default__BehaviorKernel")
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "S020_Brain", 1)
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "S020_TurnIn", 1)


class EchoesOfThePast(MissionObject):
    def apply(self) -> UObject:
        echo = super().apply()
        handle = (echo.ConsumerHandle.PID,)
        bpd = echo.InteractiveObjectDefinition.BehaviorProviderDefinition

        kernel = FindObject("BehaviorKernel", "GearboxFramework.Default__BehaviorKernel")
        kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "S080_MissionGiver", 1)


class GrandmaStoryRaid(MapDropper):
    def __init__(self) -> None:
        super().__init__("Hunger_P")

    def entered_map(self) -> None:
        granma_ai = FindObject("AIBehaviorProviderDefinition", "GD_Allium_TorgueGranma.Character.AIDef_Torgue:AIBehaviorProviderDefinition_0")
        granma_ai.BehaviorSequences[1].EventData2[0].OutputLinks.ArrayIndexAndLength = 655361
        granma_ai.BehaviorSequences[1].EventData2[3].OutputLinks.ArrayIndexAndLength = 655361



Missions = (
    Mission("This Town Ain't Big Enough", "GD_Z1_ThisTown.M_ThisTown"),
    Mission("Shielded Favors", "GD_Episode02.M_Ep2b_Henchman"),
    Mission("Symbiosis", "GD_Z1_Symbiosis.M_Symbiosis"),
    Mission("Bad Hair Day (Turn in Hammerlock)", "GD_Z1_BadHairDay.M_BadHairDay"),
    Mission("Bad Hair Day (Turn in Claptrap)", "GD_Z1_BadHairDay.M_BadHairDay", alt=True),
    Mission("Handsome Jack Here!", "GD_Z1_HandsomeJackHere.M_HandsomeJackHere",
        #  MissionGiver("GD_Hammerlock.Character.Pawn_Hammerlock:MissionDirectivesDefinition_1", True, True, "SouthernShelf_P", "Sanctuary_P", "SanctuaryAir_P"),
        MissionInventory("GD_Z1_HandsomeJackHereData.ItemDefs.ID_MO_HandsomeJackHere_MissionGiver"),
    ),
        # bandit camp enemies dont drop echo again
    Mission("Claptrap's Secret Stash", "GD_Z1_ClapTrapStash.M_ClapTrapStash"),
    Mission("Do No Harm", "GD_Z1_Surgery.M_PerformSurgery"),
    Mission("Rock, Paper, Genocide: Fire Weapons!", "GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Fire"),
    Mission("Rock, Paper, Genocide: Shock Weapons!", "GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Shock"),
    Mission("Rock, Paper, Genocide: Corrosive Weapons!", "GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Corrosive"),
    Mission("Rock, Paper, Genocide: Slag Weapons!", "GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Amp"),
    Mission("The Name Game", "GD_Z1_NameGame.M_NameGame", tags=Tag.LongMission),
    Mission("Assassinate the Assassins", "GD_Z1_Assasinate.M_AssasinateTheAssassins", tags=Tag.LongMission),
    Mission("Medical Mystery", "GD_Z3_MedicalMystery.M_MedicalMystery"),
    Mission("Medical Mystery: X-Com-municate", "GD_Z3_MedicalMystery2.M_MedicalMystery2",
        MissionGiver("GD_Zed.Character.Pawn_Zed:MissionDirectivesDefinition_1", True, True, "Sanctuary_P", "SanctuaryAir_P"),
        DocMercy(),
    tags=Tag.LongMission),
    Mission("Neither Rain nor Sleet nor Skags", "gd_z3_neitherrainsleet.M_NeitherRainSleetSkags"),
    Mission("In Memoriam", "GD_Z1_InMemoriam.M_InMemoriam"),
    Mission("Cult Following: Eternal Flame", "GD_Z1_ChildrenOfPhoenix.M_EternalFlame"),
    Mission("Cult Following: False Idols", "GD_Z1_ChildrenOfPhoenix.M_FalseIdols"),
    Mission("Cult Following: Lighting the Match", "GD_Z1_ChildrenOfPhoenix.M_LightingTheMatch"),
    Mission("Cult Following: The Enkindling", "GD_Z1_ChildrenOfPhoenix.M_TheEnkindling",
        PreventDestroy("GD_IncineratorVanya.Character.AIDef_IncineratorVanya:AIBehaviorProviderDefinition_1.Behavior_Destroy_0"),
    tags=Tag.LongMission),
    Mission("No Vacancy", "GD_Z1_NoVacancy.BalanceDefs.M_NoVacancy",
        MissionGiver("Frost_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_32.MissionDirectivesDefinition_0", True, True, "Frost_P")
    ),
        # echo giver disappears
    Mission("Too Close For Missiles", "gd_z3_toocloseformissiles.M_TooCloseForMissiles"),
    Mission("Positive Self Image", "GD_Z3_PositiveSelfImage.M_PositiveSelfImage"),
    Mission("Splinter Group", "GD_Z2_SplinterGroup.M_SplinterGroup"),
    Mission("Out of Body Experience (Turn in Marcus)", "GD_Z3_OutOfBody.M_OutOfBody",
        MissionInventory("GD_Z3_OutOfBodyData.ItemDefs.ID_MO_OutOfBody_AICore"),
        Loader1340(),
    tags=Tag.LongMission), # purge=True
    Mission("Out of Body Experience (Turn in Dr. Zed)", "GD_Z3_OutOfBody.M_OutOfBody", alt=True, tags=Tag.LongMission), # purge=True
        # Construct/War Loader 1340 dont respawn without savequit
    Mission("Mighty Morphin'", "GD_Z1_MightyMorphin.M_MightyMorphin"),
    Mission("No Hard Feelings", "gd_z1_nohardfeelings.M_NoHardFeelings",
        MissionInventory("GD_Z1_NoHardFeelingsData.BalanceDefs.ID_MO_NoHardFeelings_DataLog"),
        WillTheBandit(),
    ), # purge=True
        # Will doesnt respawn
    Mission("You Are Cordially Invited: Party Prep", "GD_Z1_CordiallyInvited.M_CordiallyInvited"),
    Mission("You Are Cordially Invited: RSVP", "GD_Z1_CordiallyInvited.M_CordiallyInvited02", tags=Tag.LongMission),
        # Respawn Fleshstick withour map reload (remove LongMission tag)
    Mission("You Are Cordially Invited: Tea Party", "GD_Z1_CordiallyInvited.M_CordiallyInvited03"),
    Mission("Mine, All Mine", "GD_Z1_MineAllMine.M_MineAllMine", tags=Tag.LongMission),
    Mission("The Pretty Good Train Robbery", "GD_Z1_TrainRobbery.M_TrainRobbery"),
        # Train chests do not reset without relog
    Mission("The Good, the Bad, and the Mordecai", "GD_Z3_GoodBadMordecai.M_GoodBadMordecai", tags=Tag.Slaughter),
    Mission("Bandit Slaughter: Round 1", "GD_Z1_BanditSlaughter.M_BanditSlaughter1", tags=Tag.Slaughter),
    Mission("Bandit Slaughter: Round 2", "GD_Z1_BanditSlaughter.M_BanditSlaughter2", tags=Tag.Slaughter),
    Mission("Bandit Slaughter: Round 3", "GD_Z1_BanditSlaughter.M_BanditSlaughter3", tags=Tag.Slaughter|Tag.LongMission),
    Mission("Bandit Slaughter: Round 4", "GD_Z1_BanditSlaughter.M_BanditSlaughter4", tags=Tag.Slaughter|Tag.LongMission),
    Mission("Bandit Slaughter: Round 5", "GD_Z1_BanditSlaughter.M_BanditSlaughter5", tags=Tag.Slaughter|Tag.VeryLongMission),
        # double-check repeating mission with no save-quit
    Mission("Won't Get Fooled Again", "GD_Z1_WontGetFooled.M_WontGetFooled"),
    Mission("Claptrap's Birthday Bash!", "GD_Z2_ClaptrapBirthdayBash.M_ClaptrapBirthdayBash"),
        # No pizza or noisemaker prompts on repeat
    Mission("Slap-Happy", "GD_Z2_SlapHappy.M_SlapHappy"),
    Mission("Hidden Journals", "GD_Z3_HiddenJournals.M_HiddenJournals"),
    Mission("Torture Chairs", "GD_Z1_HiddenJournalsFurniture.M_HiddenJournalsFurniture"),
    Mission("Arms Dealing", "GD_Z2_ArmsDealer.M_ArmsDealer"),
    Mission("Stalker of Stalkers", "GD_Z2_TaggartBiography.M_TaggartBiography"),
    Mission("Best Mother's Day Ever", "GD_Z2_MothersDayGift.BalanceDefs.M_MothersDayGift",
        #  MissionGiver("Grass_P.TheWorld:PersistentLevel.WillowInteractiveObject_20.MissionDirectivesDefinition_1", True, True, "Grass_P"),
        MissionInventory("GD_Z2_MothersDayGiftData.ItemDefs.ID_TaggartMomGift"),
    ),
        # stalkers dont drop echo again
    Mission("The Overlooked: Medicine Man", "GD_Z2_Overlooked.M_Overlooked", tags=Tag.LongMission),
    Mission("The Overlooked: Shields Up", "GD_Z2_Overlooked2.M_Overlooked2"),
    Mission("The Overlooked: This Is Only a Test", "GD_Z2_Overlooked3.M_Overlooked3",
        MissionObject("Grass_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_48", "Grass_P"),
    tags=Tag.LongMission),
        # karima door disabled after "only a test"
    Mission("Clan War: Starting the War", "GD_Z2_MeetWithEllie.M_MeetWithEllie"),
    Mission("Clan War: First Place", "GD_Z2_RiggedRace.M_RiggedRace"),
    Mission("Clan War: Reach the Dead Drop", "GD_Z2_LuckysDirtyMoney.M_FamFeudDeadDrop"),
    Mission("Clan War: End of the Rainbow", "GD_Z2_LuckysDirtyMoney.M_LuckysDirtyMoney",
        MissionObject("Luckys_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_2788", "Luckys_P"),
    ),
        # Echo uninteractable without first repeating "dead drop"
    Mission("Clan War: Trailer Trashing", "GD_Z2_TrailerTrashin.M_TrailerTrashin"),
        # Gas tanks do not reset without relog
    Mission("Clan War: Wakey Wakey", "GD_Z2_WakeyWakey.M_WakeyWakey"),
    Mission("Clan War: Zafords vs. Hodunks (Kill Hodunks)", "GD_Z2_DuelingBanjos.M_DuelingBanjos"),
    Mission("Clan War: Zafords vs. Hodunks (Kill Zafords)", "GD_Z2_DuelingBanjos.M_DuelingBanjos", alt=True),
    Mission("Minecart Mischief", "gd_z1_minecartmischief.M_MinecartMischief",
        MissionPickup("Caverns_Dynamic.TheWorld:PersistentLevel.WillowMissionPickupSpawner_0", "Caverns_P"),
    tags=Tag.LongMission), # purge=True
        # echo giver disappears
    Mission("Safe and Sound (Turn in Marcus)", "GD_Z2_SafeAndSound.M_SafeAndSound"),
    Mission("Safe and Sound (Turn in Moxxi)", "GD_Z2_SafeAndSound.M_SafeAndSound", alt=True),
    Mission("Perfectly Peaceful", "GD_Z1_PerfectlyPeaceful.M_PerfectlyPeaceful"),
    Mission("Swallowed Whole", "GD_Z3_SwallowedWhole.M_SwallowedWhole"),
    Mission("The Cold Shoulder", "GD_Z3_ColdShoulder.M_ColdShoulder"),
    Mission("Note for Self-Person", "gd_z2_notetoself.M_NoteToSelf",
        MissionInventory("gd_z2_notetoselfdata.ItemDefs.ID_MO_NoteToSelf_Echo"),
    ),
        # Goliath respawns, no mission drop
    Mission("Creature Slaughter: Round 1", "GD_Z2_CreatureSlaughter.M_CreatureSlaughter_1", tags=Tag.Slaughter),
        # Victory dialog plays upon completing last wave, but no objective update
    Mission("Creature Slaughter: Round 2", "GD_Z2_CreatureSlaughter.M_CreatureSlaughter_2", tags=Tag.Slaughter),
        # UBA Varkid doesnt respawn in last wave
    Mission("Creature Slaughter: Round 3", "GD_Z2_CreatureSlaughter.M_CreatureSlaughter_3", tags=Tag.Slaughter|Tag.LongMission),
        # Victory dialog plays upon completing last wave, but no objective update
    Mission("Creature Slaughter: Round 4", "GD_Z2_CreatureSlaughter.M_CreatureSlaughter_4", tags=Tag.Slaughter|Tag.LongMission),
        # Victory dialog plays and objective updates upon completing last wave, but no turn-in
    Mission("Creature Slaughter: Round 5", "GD_Z2_CreatureSlaughter.M_CreatureSlaughter_5", tags=Tag.Slaughter|Tag.VeryLongMission),
        # Fire Thresher doesnt respawn in last wave
    Mission("Doctor's Orders", "GD_Z2_DoctorsOrders.M_DoctorsOrders"),
        # Stalker crates with final ECHO arent accessible on repeat
    Mission("Animal Rights", "GD_Z2_FreeWilly.M_FreeWilly"),
        # Neither animals nor guards respawn on repeat
    Mission("Rakkaholics Anonymous (Turn in Mordecai)", "GD_Z2_Rakkaholics.M_Rakkaholics"),
    Mission("Rakkaholics Anonymous (Turn in Moxxi)", "GD_Z2_Rakkaholics.M_Rakkaholics", alt=True),
    Mission("The Ice Man Cometh", "GD_Z1_IceManCometh.M_IceManCometh"),
        # Dynamite interactable but invisible on repeat
    Mission("Shoot This Guy in the Face", "GD_Z1_ShootMeInTheFace.M_ShootMeInTheFace",
        McShooty(),
        MissionGiver("GD_Shootyface.Character.Pawn_Shootyface:MissionDirectivesDefinition_1", True, True, "Grass_Cliffs_P"),
        MissionGiver("Grass_Cliffs_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_725.MissionDirectivesDefinition_0", False, False, "Grass_Cliffs_P"),
    ),
    Mission("Rocko's Modern Strife", "GD_Z2_RockosModernStrife.M_RockosModernStrife"),
    Mission("Defend Slab Tower", "GD_Z2_DefendSlabTower.M_DefendSlabTower"),
        # On repeat, loader waves spawn before other objectives, softlock if killed first
    Mission("Hyperion Contract #873", "GD_Z3_HyperionContract873.M_HyperionContract873"),
    Mission("3:10 to Kaboom", "GD_Z2_BlowTheBridge.M_BlowTheBridge"),
        # Must fail mission once before repeating to be able to place bomb cart
    Mission("Breaking the Bank", "GD_Z2_TheBankJob.M_TheBankJob"),
        # On repeat, skag pile already broken
    Mission("Showdown", "GD_Z2_KillTheSheriff.M_KillTheSheriff"),
    Mission("Animal Rescue: Medicine", "GD_Z2_Skagzilla2.M_Skagzilla2_Pup",
        MissionGiver("GD_SkagzillaAdult.Character.Pawn_SkagzillaAdult:MissionDirectivesDefinition_0", True, True, "Grass_Lynchwood_P"),
    ),
        # Not re-offered from Dukino after initial completion
    Mission("Animal Rescue: Food", "GD_Z2_Skagzilla2.M_Skagzilla2_Adult"),
        # On repeat, cannot place food
    Mission("Animal Rescue: Shelter", "GD_Z2_Skagzilla2.M_Skagzilla2_Den"),
        # On repeat, Dukino sotflocks already in shelter until savequit
    Mission("Poetic License", "GD_Z2_PoeticLicense.M_PoeticLicense", PoeticLicense()),
        # On repeat, traveling to thousand cuts gives 2/3 photos
        # LOOT DAISY: Daisy should stay outside, no dialog, not gun sound, just die
    Mission("The Bane", "GD_Z3_Bane.M_Bane",
        MissionPickup("SanctuaryAir_Dynamic.TheWorld:PersistentLevel.WillowMissionPickupSpawner_3", "SanctuaryAir_P"),
    tags=Tag.LongMission),
        # ECHO that gives mission doesnt respawn
    Mission("Hell Hath No Fury", "GD_Z2_HellHathNo.M_FloodingHyperionCity"),
        # On repeat, foreman doesnt respawn
    Mission("Statuesque", "GD_Z2_HyperionStatue.M_MonumentsVandalism", tags=Tag.LongMission),
        # On repeat, third statue softlocks, not progressing to "here's your prize" enemy wave
    Mission("Home Movies", "GD_Z2_HomeMovies.M_HomeMovies"),
    Mission("Written by the Victor", "GD_Z2_WrittenByVictor.M_WrittenByVictor", WrittenByTheVictor()), # purge=True
        # On repeat, history buttons are disabled
        # After all dialog plays after first turn-in, button becomes disabled
    Mission("Bearer of Bad News", "GD_Z1_BearerBadNews.M_BearerBadNews"),
    Mission("BFFs", "GD_Z1_BFFs.M_BFFs", BFFs()), # purge=True
        # After completion, cannot interact with Sam to reaccpet mission
        # After save quit, Sam not spawned to give mission
    Mission("Demon Hunter", "GD_Z2_DemonHunter.M_DemonHunter"),
        # On repeat, mom no spawn without savequit
    Mission("Monster Mash (Part 1)", "GD_Z3_MonsterMash1.M_MonsterMash1"),
    Mission("Monster Mash (Part 2)", "GD_Z3_MonsterMash2.M_MonsterMash2"),
    Mission("Monster Mash (Part 3)", "GD_Z3_MonsterMash3.M_MonsterMash3", tags=Tag.LongMission),
        # Only 29 skrakk and 1 spycho total spawn
    Mission("Kill Yourself (Do it)", "GD_Z3_KillYourself.M_KillYourself"),
        # Killing self doesnt trigger on repeat
    Mission("Kill Yourself (Don't do it)", "GD_Z3_KillYourself.M_KillYourself", alt=True),
    Mission("Customer Service", "GD_Z3_CustomerService.M_CustomerService"),
        # Mailboxes unopenable on repeat
    Mission("To Grandmother's House We Go", "GD_Z3_GrandmotherHouse.M_GrandmotherHouse"),
    Mission("A Real Boy: Clothes Make the Man", "GD_Z2_ARealBoy.M_ARealBoy_Clothes"),
        # On repeat, Mal unable to accept so many clothes
    Mission("A Real Boy: Face Time", "GD_Z2_ARealBoy.M_ARealBoy_ArmLeg"),
        # On repeat, topmost two limbs (legs) do not respawn
    Mission("A Real Boy: Human", "GD_Z2_ARealBoy.M_ARealBoy_Human"),
        # On repeat, mal unprepared for combat
    Mission("Hyperion Slaughter: Round 1", "GD_Z3_RobotSlaughter.M_RobotSlaughter_1", tags=Tag.Slaughter),
    Mission("Hyperion Slaughter: Round 2", "GD_Z3_RobotSlaughter.M_RobotSlaughter_2", tags=Tag.Slaughter),
    Mission("Hyperion Slaughter: Round 3", "GD_Z3_RobotSlaughter.M_RobotSlaughter_3", tags=Tag.Slaughter|Tag.LongMission),
    Mission("Hyperion Slaughter: Round 4", "GD_Z3_RobotSlaughter.M_RobotSlaughter_4", tags=Tag.Slaughter|Tag.LongMission),
    Mission("Hyperion Slaughter: Round 5", "GD_Z3_RobotSlaughter.M_RobotSlaughter_5", tags=Tag.Slaughter|Tag.VeryLongMission),
    Mission("The Lost Treasure", "GD_Z3_LostTreasure.M_LostTreasure",
        MissionObject("CraterLake_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_38", "CraterLake_P"),
    tags=Tag.VeryLongMission), # purge=True
        # Box with mission giving ECHO unopenable after completion
    Mission("The Great Escape", "GD_Z3_GreatEscape.M_GreatEscape", GreatEscape()), # purge=True
        # Beacon doesnt spawn on repeat
        # Ulysses stays dead after save quit
    Mission("The Chosen One", "GD_Z3_ChosenOne.M_ChosenOne"),
    Mission("Capture the Flags", "GD_Z3_CaptureTheFlags.M_CaptureTheFlags", tags=Tag.VeryLongMission),
    Mission("This Just In", "GD_Z3_ThisJustIn.M_ThisJustIn"),
    Mission("Uncle Teddy (Turn in Una)", "GD_Z3_UncleTeddy.M_UncleTeddy"),
    Mission("Uncle Teddy (Turn in Hyperion)", "GD_Z3_UncleTeddy.M_UncleTeddy", alt=True),
        # ECHO boxes dont reclose on repeat
    Mission("Get to Know Jack", "GD_Z3_YouDontKnowJack.M_YouDontKnowJack"),
        # ECHO rakk doesnt respawn on repeat
    Mission("Hungry Like the Skag", "GD_Z3_HungryLikeSkag.M_HungryLikeSkag",
        MissionInventory("GD_Z3_HungryLikeSkagData.ItemDefs.ID_MO_HungryLikeSkag_MissionGiver"),
    ), # purge=True
        # Skags dont drop mission pickup after completion
    Mission("You. Will. Die. (Seriously.)", "GD_Z2_ThresherRaid.M_ThresherRaid"),
        # Terra no respawn after first completion

    Mission("Message in a Bottle (Oasis)", "GD_Orchid_SM_Message.M_Orchid_MessageInABottle1",
        MessageInABottle(None, "Orchid_OasisTown_P"),
    tags=Tag.PiratesBooty), # purge=True
        # On repeat, bottle uninteractable without savequit
    Mission("Burying the Past", "GD_Orchid_SM_BuryPast.M_Orchid_BuryingThePast", tags=Tag.PiratesBooty),
    Mission("Man's Best Friend", "GD_Orchid_SM_MansBestFriend.M_Orchid_MansBestFriend", tags=Tag.PiratesBooty),
    Mission("Fire Water", "GD_Orchid_SM_FireWater.M_Orchid_FireWater", tags=Tag.PiratesBooty),
    Mission("Giving Jocko A Leg Up", "GD_Orchid_SM_JockoLegUp.M_Orchid_JockoLegUp", tags=Tag.PiratesBooty),
    Mission("Wingman", "GD_Orchid_SM_Wingman.M_Orchid_Wingman", tags=Tag.PiratesBooty),
    Mission("Smells Like Victory", "GD_Orchid_SM_Smells.M_Orchid_SmellsLikeVictory", tags=Tag.PiratesBooty),
        # Shiv-spike doesnt respawn without savequit
    Mission("Declaration Against Independents", "GD_Orchid_SM_Declaration.M_Orchid_DeclarationAgainstIndependents", tags=Tag.PiratesBooty),
        # Not enough union vehicles spawn unless savequit
    Mission("Ye Scurvy Dogs", "GD_Orchid_SM_Scurvy.M_Orchid_ScurvyDogs", tags=Tag.PiratesBooty),
        # Fruits unshootable unless savequit
    Mission("Message in a Bottle (Wurmwater)", "GD_Orchid_SM_Message.M_Orchid_MessageInABottle2",
        MessageInABottle("GD_Orchid_SM_Message_Data.MO_Orchid_XMarksTheSpot:BehaviorProviderDefinition_2.BehaviorSequenceEnableByMission_13", "Orchid_SaltFlats_P"),
    tags=Tag.PiratesBooty), # purge=True
        # Bottle uninteractable after completion
    Mission("Message in a Bottle (Hayter's Folly)", "GD_Orchid_SM_Message.M_Orchid_MessageInABottle3",
        MessageInABottle("GD_Orchid_SM_Message_Data.MO_Orchid_XMarksTheSpot:BehaviorProviderDefinition_2.BehaviorSequenceEnableByMission_23", "Orchid_Caves_P"),
    tags=Tag.PiratesBooty), # purge=True
        # Bottle uninteractable after completion
    Mission("Grendel", "GD_Orchid_SM_Grendel.M_Orchid_Grendel", tags=Tag.PiratesBooty),
        # Grendel doesnt respawn without savequit
    Mission("Just Desserts for Desert Deserters", "GD_Orchid_SM_Deserters.M_Orchid_Deserters", tags=Tag.PiratesBooty),
        # Deserters dont respawn without savequit
    Mission("Message in a Bottle (The Rustyards)", "GD_Orchid_SM_Message.M_Orchid_MessageInABottle4",
        MessageInABottle("GD_Orchid_SM_Message_Data.MO_Orchid_XMarksTheSpot:BehaviorProviderDefinition_2.BehaviorSequenceEnableByMission_16", "Orchid_ShipGraveyard_P"),
    tags=Tag.PiratesBooty), # purge=True
        # Bottle uninteractable after completion
    Mission("I Know It When I See It", "GD_Orchid_SM_KnowIt.M_Orchid_KnowItWhenSeeIt", tags=Tag.PiratesBooty),
    Mission("Don't Copy That Floppy", "GD_Orchid_SM_FloppyCopy.M_Orchid_DontCopyThatFloppy", tags=Tag.PiratesBooty),
        # Not enough floppy pirates spawn without savequit
    Mission("Freedom of Speech", "GD_Orchid_SM_Freedom.M_Orchid_FreedomOfSpeech", tags=Tag.PiratesBooty),
        # DJ Tanner doesnt respawn until savequit
    Mission("Message In A Bottle (Magnys Lighthouse)", "GD_Orchid_SM_Message.M_Orchid_MessageInABottle6",
        MessageInABottle("GD_Orchid_SM_Message_Data.MO_Orchid_XMarksTheSpot:BehaviorProviderDefinition_2.BehaviorSequenceEnableByMission_7", "Orchid_Spire_P"),
    tags=Tag.PiratesBooty), # purge=True
    Mission("Faster Than the Speed of Love", "GD_Orchid_SM_Race.M_Orchid_Race", tags=Tag.PiratesBooty),
    Mission("Catch-A-Ride, and Also Tetanus", "GD_Orchid_SM_Tetanus.M_Orchid_CatchRideTetanus", tags=Tag.PiratesBooty),
    Mission("Treasure of the Sands", "GD_Orchid_SM_EndGameClone.M_Orchid_EndGame", tags=Tag.PiratesBooty|Tag.VeryLongMission),
        # Roscoe/Scarlett dont respawn until savequit
    Mission("Hyperius the Invincible", "GD_Orchid_Raid.M_Orchid_Raid1", tags=Tag.PiratesBooty|Tag.RaidEnemy|Tag.LongMission),
    Mission("Master Gee the Invincible", "GD_Orchid_Raid.M_Orchid_Raid3", tags=Tag.PiratesBooty|Tag.RaidEnemy),

    Mission("Tier 2 Battle: Appetite for Destruction", "GD_IrisEpisode02_Battle.M_IrisEp2Battle_CoP2", tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Tier 3 Battle: Appetite for Destruction", "GD_IrisEpisode02_Battle.M_IrisEp2Battle_CoP3", tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Tier 3 Rematch: Appetite for Destruction", "GD_IrisEpisode02_Battle.M_IrisEp2Battle_CoPR3", tags=Tag.CampaignOfCarnage|Tag.Slaughter),
        # When tiers repeated concurrently, killing all enemies doesnt complete wave 4
    Mission("Tier 2 Battle: Bar Room Blitz", "GD_IrisEpisode03_Battle.M_IrisEp3Battle_BarFight2", tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Tier 3 Battle: Bar Room Blitz", "GD_IrisEpisode03_Battle.M_IrisEp3Battle_BarFight3", tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Tier 3 Rematch: Bar Room Blitz", "GD_IrisEpisode03_Battle.M_IrisEp3Battle_BarFightR3", tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Totally Recall", "GD_IrisDL2_ProductRecall.M_IrisDL2_ProductRecall", tags=Tag.CampaignOfCarnage),
    Mission("Mother-Lover (Turn in Scooter)", "GD_IrisDL2_DontTalkAbtMama.M_IrisDL2_DontTalkAbtMama", tags=Tag.CampaignOfCarnage),
    Mission("Mother-Lover (Turn in Moxxi)", "GD_IrisDL2_DontTalkAbtMama.M_IrisDL2_DontTalkAbtMama", alt=True, tags=Tag.CampaignOfCarnage),
    Mission("Tier 2 Battle: The Death Race", "GD_IrisEpisode04_Battle.M_IrisEp4Battle_Race2", tags=Tag.CampaignOfCarnage),
    Mission("Tier 3 Battle: The Death Race", "GD_IrisEpisode04_Battle.M_IrisEp4Battle_Race4", tags=Tag.CampaignOfCarnage),
    Mission("Tier 3 Rematch: The Death Race", "GD_IrisEpisode04_Battle.M_IrisEp4Battle_RaceR4", tags=Tag.CampaignOfCarnage),
    Mission("Number One Fan", "GD_IrisDL2_PumpkinHead.M_IrisDL2_PumpkinHead", tags=Tag.CampaignOfCarnage),
        # Sully doesnt respawn without savequit
    Mission("Walking the Dog", "GD_IrisHUB_WalkTheDog.M_IrisHUB_WalkTheDog", tags=Tag.CampaignOfCarnage|Tag.LongMission),
    Mission("Monster Hunter", "GD_IrisHUB_MonsterHunter.M_IrisHUB_MonsterHunter", tags=Tag.CampaignOfCarnage),
    Mission("Gas Guzzlers (Turn in Hammerlock)", "GD_IrisHUB_GasGuzzlers.M_IrisHUB_GasGuzzlers", tags=Tag.CampaignOfCarnage|Tag.LongMission),
    Mission("Gas Guzzlers (Turn in Scooter)", "GD_IrisHUB_GasGuzzlers.M_IrisHUB_GasGuzzlers", alt=True, tags=Tag.CampaignOfCarnage|Tag.LongMission),
    Mission("Everybody Wants to be Wanted", "GD_IrisHUB_Wanted.M_IrisHUB_Wanted", tags=Tag.CampaignOfCarnage),
    Mission("Interview with a Vault Hunter", "GD_IrisHUB_SmackTalk.M_IrisHUB_SmackTalk", tags=Tag.CampaignOfCarnage),
    Mission("Matter Of Taste", "GD_IrisHUB_MatterOfTaste.M_IrisHUB_MatterOfTaste", tags=Tag.CampaignOfCarnage|Tag.LongMission),
        # Staff enemies do not respawn without savequit
    Mission("Tier 2 Battle: Twelve O' Clock High", "GD_IrisEpisode05_Battle.M_IrisEp5Battle_FlyboyGyro2", tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Tier 3 Battle: Twelve O' Clock High", "GD_IrisEpisode05_Battle.M_IrisEp5Battle_FlyboyGyro3", tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Tier 3 Rematch: Twelve O' Clock High", "GD_IrisEpisode05_Battle.M_IrisEp5Battle_FlyboyGyroR3", tags=Tag.CampaignOfCarnage|Tag.Slaughter),
        # Timer doesnt trigger for all tiers when repeated concurrently
        # Not enough buzzards spawn when repeated concurrently
    Mission("My Husband the Skag (Kill Uriah)", "GD_IrisDL3_MySkag.M_IrisDL3_MySkag", tags=Tag.CampaignOfCarnage),
    Mission("My Husband the Skag (Spare Uriah)", "GD_IrisDL3_MySkag.M_IrisDL3_MySkag", alt=True, tags=Tag.CampaignOfCarnage),
        # Skags dont respawn without savequit
    Mission("Say That To My Face", "GD_IrisDL3_PSYouSuck.M_IrisDL3_PSYouSuck", tags=Tag.CampaignOfCarnage),
    Mission("Commercial Appeal", "GD_IrisDL3_CommAppeal.M_IrisDL3_CommAppeal", tags=Tag.CampaignOfCarnage|Tag.LongMission),
    Mission("Pete the Invincible", "GD_IrisRaidBoss.M_Iris_RaidPete", tags=Tag.CampaignOfCarnage|Tag.RaidEnemy),
        # Pete doesnt respawn without savequit

    Mission("An Acquired Taste", "GD_Sage_SM_AcquiredTaste.M_Sage_AcquiredTaste", tags=Tag.HammerlocksHunt),
    Mission("Still Just a Borok in a Cage", "GD_Sage_SM_BorokCage.M_Sage_BorokCage", tags=Tag.HammerlocksHunt),
    Mission("Egg on Your Face", "GD_Sage_SM_EggOnFace.M_Sage_EggOnFace", tags=Tag.HammerlocksHunt|Tag.LongMission),
        # Cage still closed without savequit
    Mission("Palling Around", "GD_Sage_SM_PallingAround.M_Sage_PallingAround", tags=Tag.HammerlocksHunt),
        # Bulwark doesnt respawn without savequit
    Mission("I Like My Monsters Rare", "GD_Sage_SM_RareSpawns.M_Sage_RareSpawns", tags=Tag.HammerlocksHunt|Tag.VeryLongMission),
    Mission("Ol' Pukey", "GD_Sage_SM_OldPukey.M_Sage_OldPukey", tags=Tag.HammerlocksHunt|Tag.LongMission),
        # Pukey no AI without savequit
    Mission("Nakayama-rama", "GD_Sage_SM_Nakarama.M_Sage_Nakayamarama", tags=Tag.HammerlocksHunt|Tag.LongMission),
        # Only 2 echos respawn without savequit
    Mission("The Rakk Dahlia Murder", "GD_Sage_SM_DahliaMurder.M_Sage_DahliaMurder", tags=Tag.HammerlocksHunt),
        # Rakkanoth doesnt respawn without savequit
    Mission("Urine, You're Out", "GD_Sage_SM_Urine.M_Sage_Urine", tags=Tag.HammerlocksHunt|Tag.VeryLongMission),
        # Urine not reinteractable without savequit
    Mission("Follow The Glow", "GD_Sage_SM_FollowGlow.M_Sage_FollowGlow", tags=Tag.HammerlocksHunt),
        # Dribbles wave fight doesnt reset without savequit
    Mission("Big Feet", "GD_Sage_SM_BigFeet.M_Sage_BigFeet", tags=Tag.HammerlocksHunt),
    Mission("Now You See It", "GD_Sage_SM_NowYouSeeIt.M_Sage_NowYouSeeIt", tags=Tag.HammerlocksHunt|Tag.LongMission),
    Mission("Voracidous the Invincible", "GD_Sage_Raid.M_Sage_Raid", tags=Tag.HammerlocksHunt|Tag.RaidEnemy|Tag.LongMission),

    Mission("Fake Geek Guy", "GD_Aster_FakeGeekGuy.M_FakeGeekGuy", tags=Tag.DragonKeep),
        # Questions dont respawn until savequit
    Mission("Roll Insight", "GD_Aster_RollInsight.M_RollInsight",
        RollInsight("Village_Mission.TheWorld:PersistentLevel.WillowInteractiveObject_297.MissionDirectivesDefinition_1", True, True, "Village_P"),
    tags=Tag.DragonKeep), # purge=True
        # Die stays in place of bartlesby after completion, and also until savequit with purge
    Mission("Ell in Shining Armor (Skimpy Armor)", "GD_Aster_EllieDress.M_EllieDress", tags=Tag.DragonKeep),
    Mission("Ell in Shining Armor (Bulky Armor)", "GD_Aster_EllieDress.M_EllieDress", alt=True, tags=Tag.DragonKeep),
    Mission("Tree Hugger", "GD_Aster_TreeHugger.M_TreeHugger", tags=Tag.DragonKeep|Tag.LongMission),
    Mission("Lost Souls", "GD_Aster_DemonicSouls.M_DemonicSouls",
        LostSouls("GD_Knight_LostSoulsNPC_Proto2.Character.Pawn_Knight_LostSoulsNPC_Proto2:MissionDirectivesDefinition_1", True, True, "Dead_Forest_P"),
    tags=Tag.DragonKeep), # purge=True
        # Dark Souls guy stays revived  after completion, and also until savequit with purge
    Mission("Critical Fail", "GD_Aster_CriticalFail.M_CriticalFail", tags=Tag.DragonKeep),
        # Huts dont respawn without savequit
    Mission("MMORPGFPS", "GD_Aster_MMORPGFPS.M_MMORPGFPS", tags=Tag.DragonKeep|Tag.LongMission),
        # Knights dont respawn unless savequit
    Mission("The Sword in The Stoner", "GD_Aster_SwordInStone.M_SwordInStoner", tags=Tag.DragonKeep|Tag.LongMission),
        # Stoner doesnt respawn without savequit
    Mission("The Beard Makes The Man", "GD_Aster_ClapTrapBeard.M_ClapTrapBeard", block_weapon=True, tags=Tag.DragonKeep|Tag.LongMission),
        # Forge doesnt reset without savequit
    Mission("My Kingdom for a Wand", "GD_Aster_ClaptrapWand.M_WandMakesTheMan", tags=Tag.DragonKeep),
    Mission("The Claptrap's Apprentice", "GD_Aster_ClaptrapApprentice.M_ClaptrapApprentice", tags=Tag.DragonKeep),
        # After turn in, claptrap animates disappearing and then only returns after savequit
    Mission("Loot Ninja", "GD_Aster_LootNinja.M_LootNinja",
        MissionGiver("GD_Aster_Torgue.Character.Pawn_Torgue:MissionDirectivesDefinition_1", True, True, "Village_P"),
    tags=Tag.DragonKeep), # purge=True
        # After turn in, Sir Gallow does not spawn to give mission
    Mission("Winter is a Bloody Business", "GD_Aster_WinterIsComing.M_WinterIsComing", tags=Tag.DragonKeep|Tag.LongMission),
    Mission("My Dead Brother (Kill Edgar)", "GD_Aster_DeadBrother.M_MyDeadBrother", MyDeadBrother(), tags=Tag.DragonKeep|Tag.LongMission), # purge=True
    Mission("My Dead Brother (Kill Simon)", "GD_Aster_DeadBrother.M_MyDeadBrother", alt=True, tags=Tag.DragonKeep|Tag.LongMission), # purge=True
    Mission("The Amulet (Buy Miz's Amulet)", "GD_Aster_AmuletDoNothing.M_AmuletDoNothing", tags=Tag.DragonKeep|Tag.LongMission),
    Mission("The Amulet (Punch Miz In The Face)", "GD_Aster_AmuletDoNothing.M_AmuletDoNothing", alt=True, tags=Tag.DragonKeep|Tag.LongMission),
        # Upon reaccepting mission, Miz has no behavior
    Mission("Pet Butt Stallion", "GD_Aster_PetButtStallion.M_PettButtStallion", tags=Tag.DragonKeep),
    Mission("Feed Butt Stallion", "GD_Aster_FeedButtStallion.M_FeedButtStallion", tags=Tag.DragonKeep),
    Mission("Raiders of the Last Boss", "GD_Aster_RaidBoss.M_Aster_RaidBoss", tags=Tag.DragonKeep|Tag.RaidEnemy),
    Mission("Post-Crumpocalyptic", "GD_Aster_Post-Crumpocalyptic.M_Post-Crumpocalyptic", tags=Tag.DragonKeep|Tag.VeryLongMission),
    Mission("Find Murderlin's Temple", "GD_Aster_TempleSlaughter.M_TempleSlaughterIntro", tags=Tag.DragonKeep),
    Mission("Magic Slaughter: Round 1", "GD_Aster_TempleSlaughter.M_TempleSlaughter1", tags=Tag.DragonKeep|Tag.Slaughter),

    Mission("Magic Slaughter: Round 2", "GD_Aster_TempleSlaughter.M_TempleSlaughter2", tags=Tag.DragonKeep|Tag.Slaughter),
    Mission("Magic Slaughter: Round 3", "GD_Aster_TempleSlaughter.M_TempleSlaughter3", tags=Tag.DragonKeep|Tag.Slaughter|Tag.LongMission),
    Mission("Magic Slaughter: Round 4", "GD_Aster_TempleSlaughter.M_TempleSlaughter4", tags=Tag.DragonKeep|Tag.Slaughter|Tag.LongMission),
    Mission("Magic Slaughter: Round 5", "GD_Aster_TempleSlaughter.M_TempleSlaughter5", tags=Tag.DragonKeep|Tag.Slaughter|Tag.VeryLongMission),
    Mission("Magic Slaughter: Badass Round", "GD_Aster_TempleSlaughter.M_TempleSlaughter6Badass", tags=Tag.DragonKeep|Tag.Slaughter|Tag.VeryLongMission),
    Mission("The Magic of Childhood", "GD_Aster_TempleTower.M_TempleTower", tags=Tag.DragonKeep|Tag.Slaughter|Tag.LongMission|Tag.Slaughter),

    Mission("Space Cowboy", "GD_Anemone_Side_SpaceCowboy.M_Anemone_SpaceCowboy", tags=Tag.FightForSanctuary|Tag.LongMission),
        # Midget toilet porn doesnt respawn without savequit
    Mission("Hypocritical Oath", "GD_Anemone_Side_HypoOathPart1.M_HypocriticalOathPart1", tags=Tag.FightForSanctuary),
        # Experiment doesnt respawn without savequit
    Mission("Cadeuceus", "GD_Anemone_Side_HypoOathPart2.M_HypocriticalOathPart2", tags=Tag.FightForSanctuary),
        # Experiment doesnt respawn without savequit
    Mission("The Vaughnguard", "GD_Anemone_Side_VaughnPart1.M_Anemone_VaughnPart1", tags=Tag.FightForSanctuary),
        # Recruits dont respawn without savequit
    Mission("The Hunt is Vaughn", "GD_Anemone_Side_VaughnPart2.M_Anemone_VaughnPart2", tags=Tag.FightForSanctuary),
    Mission("A Most Cacophonous Lure", "GD_Anemone_Side_RaidBoss.M_Anemone_CacophonousLure", tags=Tag.FightForSanctuary|Tag.RaidEnemy),
        # Haderax doesnt respawn without savequit
    Mission("Claptocurrency", "GD_Anemone_Side_Claptocurrency.M_Claptocurrency", tags=Tag.FightForSanctuary),
        # On repeat, cannot place blocks without savequit
    Mission("The Oddest Couple", "GD_Anemone_Side_OddestCouple.M_Anemone_OddestCouple",
        OddestCouple("OldDust_Mission_Side.TheWorld:PersistentLevel.WillowInteractiveObject_2", "OldDust_P"),
    tags=Tag.FightForSanctuary),
        # Earl's door becomes uninteractable after completion
    Mission("Sirentology", "GD_Anemone_Side_Sirentology.M_Anemone_Sirentology", tags=Tag.FightForSanctuary|Tag.LongMission),
    Mission("My Brittle Pony", "GD_Anemone_Side_MyBrittlePony.M_Anemone_MyBrittlePony", tags=Tag.FightForSanctuary|Tag.LongMission),
        # Brick and enemy waves dont respawn without savequit
    Mission("BFFFs", "GD_Anemone_Side_EyeSnipers.M_Anemone_EyeOfTheSnipers", tags=Tag.FightForSanctuary),
        # Lieutenants dont respawn without savequit
    Mission("Chief Executive Overlord", "GD_Anemone_Side_VaughnPart3.M_Anemone_VaughnPart3", tags=Tag.FightForSanctuary),
    Mission("Echoes of the Past", "GD_Anemone_Side_Echoes.M_Anemone_EchoesOfThePast",
        EchoesOfThePast("ResearchCenter_MissionSide.TheWorld:PersistentLevel.WillowInteractiveObject_1", "ResearchCenter_P"),
    tags=Tag.FightForSanctuary), # purge=True
        # ECHO mission giver not interactable after completion

    Mission("The Hunger Pangs",
        "GD_Allium_TG_Plot_Mission01.M_Allium_ThanksgivingMission01",
        MissionGiver("GD_Allium_Torgue.Character.Pawn_Allium_Torgue:MissionDirectivesDefinition_1", True, True, "Hunger_P"),
    tags=Tag.WattleGobbler|Tag.VeryLongMission),
        # On reaccept, no sequence until after savequit
    Mission("Grandma Flexington's Story",
        "GD_Allium_GrandmaFlexington.M_ListenToGrandma",
        Behavior("GD_Allium_TorgueGranma.Character.AIDef_Torgue:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_6"),
    tags=Tag.WattleGobbler|Tag.LongMission),
    Mission("Grandma Flexington's Story: Raid Difficulty", "GD_Allium_Side_GrandmaRaid.M_ListenToGrandmaRaid",
        Behavior("GD_Allium_TorgueGranma.Character.AIDef_Torgue:AIBehaviorProviderDefinition_0.Behavior_SpawnItems_3"),
        GrandmaStoryRaid(),
    tags=Tag.WattleGobbler|Tag.RaidEnemy|Tag.VeryLongMission),
        # Grandma not interactable without savequit after completion

    Mission("Get Frosty",
        "GD_Allium_KillSnowman.M_KillSnowman",
        MissionGiver("Xmas_Mission.TheWorld:PersistentLevel.WillowAIPawn_28.MissionDirectivesDefinition_0", True, True, "Xmas_P"),
    tags=Tag.MercenaryDay|Tag.VeryLongMission),
        # On reaccept, no marcus AI until after savequit
    Mission("Special Delivery", "GD_Allium_Delivery.M_Delivery", tags=Tag.MercenaryDay),
        # Toys dont respawn until savequit; resetting dens works
    
    Mission("The Bloody Harvest",
        "GD_FlaxMissions.M_BloodHarvest",
        MissionGiver("Pumpkin_Patch_Dynamic.TheWorld:PersistentLevel.WillowAIPawn_5.MissionDirectivesDefinition_0", True, True, "Pumpkin_Patch_P"),
    tags=Tag.BloodyHarvest|Tag.VeryLongMission),
    Mission("Trick or Treat", "GD_FlaxMissions.M_TrickOrTreat", tags=Tag.BloodyHarvest),
        # Not all candies collectable again until savequit

    Mission("Fun, Sun, and Guns",
        "GD_Nast_Easter_Plot_M01.M_Nast_Easter",
        MissionGiver("GD_Nasturtium_Hammerlock.Character.Pawn_Hammerlock:MissionDirectivesDefinition_1", True, True, "Easter_P"),
    tags=Tag.SonOfCrawmerax|Tag.VeryLongMission),
    Mission("Victims of Vault Hunters", "GD_Nast_Easter_Mission_Side01.M_Nast_Easter_Side01", tags=Tag.SonOfCrawmerax|Tag.LongMission),
        # Evidence locations dont reset without savequit

    Mission("A Match Made on Pandora",
        "GD_Nast_Vday_Mission_Plot.M_Nast_Vday",
        MissionGiver("GD_Nasturtium_Moxxi.Character.Pawn_Moxxi:MissionDirectivesDefinition_1", True, True, "Distillery_P"),
    tags=Tag.WeddingDayMassacre|Tag.VeryLongMission),
    Mission("Learning to Love", "GD_Nast_Vday_Mission_Side01.M_Nast_Vday_Side01",
        MissionGiver("GD_Nasturtium_Moxxi.Character.Pawn_Moxxi:MissionDirectivesDefinition_1", True, True, "Distillery_P"),
    tags=Tag.WeddingDayMassacre|Tag.LongMission), # purge=True
        # Innuendobot is dead until savequit after purge

    Mission("Dr. T and the Vault Hunters", "GD_Lobelia_UnlockDoor.M_Lobelia_UnlockDoor", tags=Tag.DigistructPeak),
    Mission("A History of Simulated Violence", "GD_Lobelia_TestingZone.M_TestingZone", tags=Tag.DigistructPeak|Tag.VeryLongMission|Tag.RaidEnemy),
    Mission("More History of Simulated Violence", "GD_Lobelia_TestingZone.M_TestingZoneRepeatable", tags=Tag.DigistructPeak|Tag.VeryLongMission|Tag.RaidEnemy),
)
