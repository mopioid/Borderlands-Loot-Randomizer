from __future__ import annotations

from unrealsdk import Log, FindObject, GetEngine #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct #type: ignore

from .. import options, locations
from ..options import Tag

from typing import Dict, List, Set


MissionTags = (
    Tag.ShortMission    |
    Tag.LongMission     |
    Tag.VeryLongMission |
    Tag.Slaughter       |
    Tag.RaidMission     
)

_purge_paths: Set[str] = set()
_double_reward_paths: Set[str] = set()


def Enable() -> None:
    global _purge_paths
    _purge_paths = set()

    RunHook("WillowGame.QuestAcceptGFxMovie.GetRewardPresentations", "LootRandomizer", lambda c,f,p: False)
    RunHook("WillowGame.StatusMenuExGFxMovie.GetRewardPresentations", "LootRandomizer", lambda c,f,p: False)
    RunHook("WillowGame.WillowPlayerController.TryPromptForFastForward", "LootRandomizer", lambda c,f,p: False)

    # TODO: Test Client
    RunHook("WillowGame.WillowPlayerController.AcceptMission", "LootRandomizer", _AcceptMission)
    RunHook("WillowGame.WillowPlayerController.ServerCompleteMission", "LootRandomizer", _CompleteMission)
    RunHook("WillowGame.QuestAcceptGFxMovie.AcceptReward", "LootRandomizer", _AcceptReward)


def Disable() -> None:
    global _purge_paths
    _purge_paths = set()

    RemoveHook("WillowGame.QuestAcceptGFxMovie.GetRewardPresentations", "LootRandomizer")
    RemoveHook("WillowGame.StatusMenuExGFxMovie.GetRewardPresentations", "LootRandomizer")
    RemoveHook("WillowGame.WillowPlayerController.TryPromptForFastForward", "LootRandomizer")

    RemoveHook("WillowGame.WillowPlayerController.AcceptMission", "LootRandomizer")
    RemoveHook("WillowGame.WillowPlayerController.ServerCompleteMission", "LootRandomizer")
    RemoveHook("WillowGame.QuestAcceptGFxMovie.AcceptReward", "LootRandomizer")


def _block_method(caller: UObject, function: UFunction, params: FStruct) -> bool:
    return False


def _AcceptMission(caller: UObject, function: UFunction, params: FStruct) -> bool:
    tracker = GetEngine().GetCurrentWorldInfo().GRI.MissionTracker
    #TODO: stop (return True) here if mission not in tracker

    RemoveHook("WillowGame.WillowPlayerController.AcceptMission", "LootRandomizer")
    if params.MissionDirector:
        caller.AcceptMission(params.Mission, params.MissionDirector.ObjectPointer)
    else:
        caller.AcceptMission(params.Mission)
    RunHook("WillowGame.WillowPlayerController.AcceptMission", "LootRandomizer", _AcceptMission)
    
    tracker.PlayKickoff(params.Mission)
    return False


def _CompleteMission(caller: UObject, function: UFunction, params: FStruct) -> bool:
    if UObject.PathName(params.Mission) not in _purge_paths:
        return True

    RemoveHook("WillowGame.WillowPlayerController.ServerCompleteMission", "LootRandomizer")
    caller.ServerCompleteMission(params.Mission, params.MissionDirector.ObjectPointer)
    RunHook("WillowGame.WillowPlayerController.ServerCompleteMission", "LootRandomizer", _CompleteMission)

    gri = GetEngine().GetCurrentWorldInfo().GRI
    pc = GetEngine().GamePlayers[0].Actor

    for mission_data in gri.MissionTracker.MissionList:
        if mission_data.MissionDef == params.Mission:
            mission_data.Status = 0
            mission_data.ObjectivesProgress = []
            mission_data.ActiveObjectiveSet = None
            mission_data.SubObjectiveSets = []

    mission_datas: List[FStruct] = []
    for mission_data in pc.MissionPlaythroughs[gri.GetCurrPlaythrough()].MissionList:
        if mission_data.MissionDef != params.Mission:
            mission_datas.append((
                mission_data.MissionDef,
                mission_data.Status,
                mission_data.ObjectivesProgress,
                mission_data.ActiveObjectiveSet,
                mission_data.SubObjectiveSets,
                mission_data.GameStage,
                mission_data.bNeedsRewards,
                mission_data.bHeardKickoff,
            ))
    pc.MissionPlaythroughs[gri.GetCurrPlaythrough()].MissionList = mission_datas

    return False


def _AcceptReward(caller: UObject, function: UFunction, params: FStruct) -> bool:
    mission = caller.MissionDefForRewardPage
    if UObject.PathName(mission) not in _double_reward_paths:
        return True

    Log("Found double mission reward turnin")

    RemoveHook("WillowGame.QuestAcceptGFxMovie.AcceptReward", "LootRandomizer")
    caller.AcceptReward(params.RewardChoice)
    RunHook("WillowGame.QuestAcceptGFxMovie.AcceptReward", "LootRandomizer", _AcceptReward)

    GetEngine().GamePlayers[0].Actor.ServerGrantMissionRewards(mission, False)

    return False


class Reward(locations.Dropper):
    path: str
    purge: bool

    uobject: UObject

    reward_items: List[UObject]
    reward_pools: List[UObject]

    @property
    def reward_attribute(self) -> FStruct:
        return self.uobject.Reward

    def __init__(self, path: str, purge: bool = False) -> None:
        self.path = path; self.purge = purge

    def register(self) -> None:
        self.uobject = FindObject("MissionDefinition", self.path)

        self.repeatable = self.uobject.bRepeatable
        self.reward_items = self.reward_attribute.RewardItems
        self.reward_pools = self.reward_attribute.RewardItemPools

        self.uobject.bRepeatable = True
        self.reward_attribute.RewardItems = []

        self.reward_attribute.RewardItemPools = self.location.get_pools()

        if self.location.tags & (Tag.VeryLongMission|Tag.RaidMission):
            _double_reward_paths.add(self.path)

        if self.purge:
            _purge_paths.add(self.path)


    def unregister(self) -> None:
        if self.uobject:
            self.uobject.bRepeatable = self.repeatable
            self.reward_attribute.RewardItems = self.reward_items
            self.reward_attribute.RewardItemPools = self.reward_pools

        _purge_paths.discard(self.path)
        _double_reward_paths.discard(self.path)


class AltReward(Reward):
    @property
    def reward_attribute(self) -> FStruct:
        return self.uobject.AlternativeReward


class Mission(locations.Location):
    def __init__(self, name: str, *droppers: locations.Dropper, tags=Tag.BaseGame|Tag.ShortMission) -> None:
        super().__init__(name, *droppers, tags=tags)

        if not self.tags & options.ContentTags:
            self.tags |= Tag.BaseGame
        if not tags & MissionTags:
            self.tags |= Tag.ShortMission

    def get_pools(self) -> locations.Sequence:
        if self.tags & (Tag.LongMission|Tag.VeryLongMission|Tag.RaidMission):
            return (self.item.uobject, self.item.uobject)
        return (self.item.uobject,)


from .mcshooty import McShooty


Locations = (
    Mission("This Town Ain't Big Enough", Reward("GD_Z1_ThisTown.M_ThisTown")),
    Mission("Shielded Favors", Reward("GD_Episode02.M_Ep2b_Henchman")),
    Mission("Symbiosis", Reward("GD_Z1_Symbiosis.M_Symbiosis")),
    Mission("Bad Hair Day (Turn in Hammerlock)", Reward("GD_Z1_BadHairDay.M_BadHairDay")),
    Mission("Bad Hair Day (Turn in Claptrap)", AltReward("GD_Z1_BadHairDay.M_BadHairDay")),
    Mission("Handsome Jack Here!", Reward("GD_Z1_HandsomeJackHere.M_HandsomeJackHere", purge=True)),
        # bandit camp enemies dont drop echo again
    Mission("Claptrap's Secret Stash", Reward("GD_Z1_ClapTrapStash.M_ClapTrapStash")),
    Mission("Do No Harm", Reward("GD_Z1_Surgery.M_PerformSurgery")),
    Mission("Rock, Paper, Genocide: Fire Weapons!", Reward("GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Fire")),
    Mission("Rock, Paper, Genocide: Shock Weapons!", Reward("GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Shock")),
    Mission("Rock, Paper, Genocide: Corrosive Weapons!", Reward("GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Corrosive")),
    Mission("Rock, Paper, Genocide: Slag Weapons!", Reward("GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Amp")),
    Mission("The Name Game", Reward("GD_Z1_NameGame.M_NameGame"), tags=Tag.LongMission),
    Mission("Assassinate the Assassins", Reward("GD_Z1_Assasinate.M_AssasinateTheAssassins"), tags=Tag.LongMission),
    Mission("Medical Mystery", Reward("GD_Z3_MedicalMystery.M_MedicalMystery")),
    # Mission("Medical Mystery: X-Com-municate", Reward("GD_Z3_MedicalMystery2.M_MedicalMystery2"), tags=Tag.LongMission),
        # Mission completion required for farming Doc Mercy
        # mercy corpse "!" uninteractable after first completion
        # GD_Zed.Character.Pawn_Zed:MissionDirectivesDefinition_1.MissionDirectives[3].bBeginsMission True
        # Frost_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_413.MissionDirectivesDefinition_0.MissionDirectives[1].bBeginsMission False
    Mission("Neither Rain nor Sleet nor Skags", Reward("gd_z3_neitherrainsleet.M_NeitherRainSleetSkags")),
    Mission("In Memoriam", Reward("GD_Z1_InMemoriam.M_InMemoriam")),
    Mission("Cult Following: Eternal Flame", Reward("GD_Z1_ChildrenOfPhoenix.M_EternalFlame")),
    Mission("Cult Following: False Idols", Reward("GD_Z1_ChildrenOfPhoenix.M_FalseIdols")),
    Mission("Cult Following: Lighting the Match", Reward("GD_Z1_ChildrenOfPhoenix.M_LightingTheMatch")),
    Mission("Cult Following: The Enkindling", Reward("GD_Z1_ChildrenOfPhoenix.M_TheEnkindling"), tags=Tag.LongMission),
    # Mission("No Vacancy", Reward("GD_Z1_NoVacancy.BalanceDefs.M_NoVacancy")),
        # Mission completion required for Happy Pig bounty board etc
        # echo giver disappears
    Mission("Too Close For Missiles", Reward("gd_z3_toocloseformissiles.M_TooCloseForMissiles")),
    Mission("Positive Self Image", Reward("GD_Z3_PositiveSelfImage.M_PositiveSelfImage")),
    Mission("Splinter Group", Reward("GD_Z2_SplinterGroup.M_SplinterGroup")),
    Mission("Out of Body Experience (Turn in Marcus)", Reward("GD_Z3_OutOfBody.M_OutOfBody", purge=True), tags=Tag.LongMission),
    Mission("Out of Body Experience (Turn in Dr. Zed)", AltReward("GD_Z3_OutOfBody.M_OutOfBody", purge=True), tags=Tag.LongMission),
        # Construct/War Loader 1340 dont respawn without savequit
    Mission("Mighty Morphin'", Reward("GD_Z1_MightyMorphin.M_MightyMorphin")),
    Mission("No Hard Feelings", Reward("gd_z1_nohardfeelings.M_NoHardFeelings", purge=True)),
        # Will doesnt respawn
    Mission("You Are Cordially Invited: Party Prep", Reward("GD_Z1_CordiallyInvited.M_CordiallyInvited")),
    Mission("You Are Cordially Invited: RSVP", Reward("GD_Z1_CordiallyInvited.M_CordiallyInvited02"), tags=Tag.LongMission),
        # Respawn Fleshstick withour map reload (remove LongMission tag)
    Mission("You Are Cordially Invited: Tea Party", Reward("GD_Z1_CordiallyInvited.M_CordiallyInvited03")),
    Mission("Mine, All Mine", Reward("GD_Z1_MineAllMine.M_MineAllMine"), tags=Tag.LongMission),
    Mission("The Pretty Good Train Robbery", Reward("GD_Z1_TrainRobbery.M_TrainRobbery")),
        # Train chests do not reset without relog
    Mission("The Good, the Bad, and the Mordecai", Reward("GD_Z3_GoodBadMordecai.M_GoodBadMordecai"), tags=Tag.Slaughter),
    Mission("Bandit Slaughter: Round 1", Reward("GD_Z1_BanditSlaughter.M_BanditSlaughter1"), tags=Tag.Slaughter),
    Mission("Bandit Slaughter: Round 2", Reward("GD_Z1_BanditSlaughter.M_BanditSlaughter2"), tags=Tag.Slaughter),
    Mission("Bandit Slaughter: Round 3", Reward("GD_Z1_BanditSlaughter.M_BanditSlaughter3"), tags=Tag.Slaughter),
    Mission("Bandit Slaughter: Round 4", Reward("GD_Z1_BanditSlaughter.M_BanditSlaughter4"), tags=Tag.Slaughter),
    Mission("Bandit Slaughter: Round 5", Reward("GD_Z1_BanditSlaughter.M_BanditSlaughter5"), tags=Tag.Slaughter),
        # double-check repeating mission with no save-quit

    Mission("Won't Get Fooled Again", Reward("GD_Z1_WontGetFooled.M_WontGetFooled")),
    Mission("Claptrap's Birthday Bash!", Reward("GD_Z2_ClaptrapBirthdayBash.M_ClaptrapBirthdayBash")),
        # No pizza or noisemaker prompts on repeat
    Mission("Slap-Happy", Reward("GD_Z2_SlapHappy.M_SlapHappy")),
    Mission("Hidden Journals", Reward("GD_Z3_HiddenJournals.M_HiddenJournals")),
    Mission("Torture Chairs", Reward("GD_Z1_HiddenJournalsFurniture.M_HiddenJournalsFurniture")),
    Mission("Arms Dealing", Reward("GD_Z2_ArmsDealer.M_ArmsDealer")),
    Mission("Stalker of Stalkers", Reward("GD_Z2_TaggartBiography.M_TaggartBiography")),
    # Mission("Best Mother's Day Ever", Reward("GD_Z2_MothersDayGift.BalanceDefs.M_MothersDayGift")),
        # Mission completion required for farming Henry
        # stalkers dont drop echo again
    Mission("The Overlooked: Medicine Man", Reward("GD_Z2_Overlooked.M_Overlooked"), tags=Tag.LongMission),
    Mission("The Overlooked: Shields Up", Reward("GD_Z2_Overlooked2.M_Overlooked2")),
    Mission("The Overlooked: This Is Only a Test", Reward("GD_Z2_Overlooked3.M_Overlooked3"), tags=Tag.LongMission),
        # karima door disabled after "only a test"
    Mission("Clan War: Starting the War", Reward("GD_Z2_MeetWithEllie.M_MeetWithEllie")),
    Mission("Clan War: First Place", Reward("GD_Z2_RiggedRace.M_RiggedRace")),
    Mission("Clan War: Reach the Dead Drop", Reward("GD_Z2_LuckysDirtyMoney.M_FamFeudDeadDrop")),
    Mission("Clan War: End of the Rainbow", Reward("GD_Z2_LuckysDirtyMoney.M_LuckysDirtyMoney")),
        # Echo uninteractable without first repeating "dead drop"
        # MissionDirectivesDefinition'Luckys_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_2788.MissionDirectivesDefinition_0'
    Mission("Clan War: Trailer Trashing", Reward("GD_Z2_TrailerTrashin.M_TrailerTrashin")),
        # Gas tanks do not reset without relog
    Mission("Clan War: Wakey Wakey", Reward("GD_Z2_WakeyWakey.M_WakeyWakey")),
    Mission("Clan War: Zafords vs. Hodunks (Turn in Mick Zaford)", Reward("GD_Z2_DuelingBanjos.M_DuelingBanjos")),
    Mission("Clan War: Zafords vs. Hodunks (Turn in Jimbo Hodunk)", AltReward("GD_Z2_DuelingBanjos.M_DuelingBanjos")),
    Mission("Minecart Mischief", Reward("gd_z1_minecartmischief.M_MinecartMischief", purge=True), tags=Tag.LongMission),
        # echo giver disappears
    Mission("Safe and Sound (Turn in Marcus)", Reward("GD_Z2_SafeAndSound.M_SafeAndSound")),
    Mission("Safe and Sound (Turn in Moxxi)", AltReward("GD_Z2_SafeAndSound.M_SafeAndSound")),
    Mission("Perfectly Peaceful", Reward("GD_Z1_PerfectlyPeaceful.M_PerfectlyPeaceful")),
    Mission("Swallowed Whole", Reward("GD_Z3_SwallowedWhole.M_SwallowedWhole")),
    Mission("The Cold Shoulder", Reward("GD_Z3_ColdShoulder.M_ColdShoulder")),
    # Mission("Note for Self-Person", Reward("gd_z2_notetoself.M_NoteToSelf")),
        # Goliath respawns, no mission drop
        # Mission completion required for farming Smashhead
    Mission("Creature Slaughter: Round 1", Reward("GD_Z2_CreatureSlaughter.M_CreatureSlaughter_1"), tags=Tag.Slaughter),
        # Victory dialog plays upon completing last wave, but no objective update
    Mission("Creature Slaughter: Round 2", Reward("GD_Z2_CreatureSlaughter.M_CreatureSlaughter_2"), tags=Tag.Slaughter),
        # UBA Varkid doesnt respawn in last wave
    Mission("Creature Slaughter: Round 3", Reward("GD_Z2_CreatureSlaughter.M_CreatureSlaughter_3"), tags=Tag.Slaughter),
        # Victory dialog plays upon completing last wave, but no objective update
    Mission("Creature Slaughter: Round 4", Reward("GD_Z2_CreatureSlaughter.M_CreatureSlaughter_4"), tags=Tag.Slaughter),
        # Victory dialog plays and objective updates upon completing last wave, but no turn-in
    Mission("Creature Slaughter: Round 5", Reward("GD_Z2_CreatureSlaughter.M_CreatureSlaughter_5"), tags=Tag.Slaughter),
        # Fire Thresher doesnt respawn in last wave
    Mission("Doctor's Orders", Reward("GD_Z2_DoctorsOrders.M_DoctorsOrders")),
        # Loot midget box with echo doesnt re-close after complete
        # Stalker crates with final ECHO arent accessible on repeat
    Mission("Animal Rights", Reward("GD_Z2_FreeWilly.M_FreeWilly")),
        # Neither animals nor guards respawn on repeat
    Mission("Rakkaholics Anonymous (Turn in Mordecai)", Reward("GD_Z2_Rakkaholics.M_Rakkaholics")),
    Mission("Rakkaholics Anonymous (Turn in Moxxi)", AltReward("GD_Z2_Rakkaholics.M_Rakkaholics")),
    Mission("The Ice Man Cometh", Reward("GD_Z1_IceManCometh.M_IceManCometh")),
        # Dynamite interactable but invisible on repeat
    Mission("Shoot This Guy in the Face", Reward("GD_Z1_ShootMeInTheFace.M_ShootMeInTheFace"), McShooty()),
    Mission("Rocko's Modern Strife", Reward("GD_Z2_RockosModernStrife.M_RockosModernStrife")),
    Mission("Defend Slab Tower", Reward("GD_Z2_DefendSlabTower.M_DefendSlabTower")),
        # On repeat, loader waves spawn before other objectives, softlock if killed first
    Mission("Hyperion Contract #873", Reward("GD_Z3_HyperionContract873.M_HyperionContract873")),
    Mission("3:10 to Kaboom", Reward("GD_Z2_BlowTheBridge.M_BlowTheBridge")),
        # On repeat, cannot place bomb cart
    Mission("Breaking the Bank", Reward("GD_Z2_TheBankJob.M_TheBankJob")),
        # On repeat, skag pile already broken
    Mission("Showdown", Reward("GD_Z2_KillTheSheriff.M_KillTheSheriff")),
    # Mission("Animal Rescue: Medicine", Reward("GD_Z2_Skagzilla2.M_Skagzilla2_Pup")),
        # Not re-offered from Dukino after initial completion
    Mission("Animal Rescue: Food", Reward("GD_Z2_Skagzilla2.M_Skagzilla2_Adult")),
        # On repeat, cannot place food
    Mission("Animal Rescue: Shelter", Reward("GD_Z2_Skagzilla2.M_Skagzilla2_Den")),
        # On repeat, Dukino sotflocks already in shelter
    Mission("Poetic License", Reward("GD_Z2_PoeticLicense.M_PoeticLicense")),
        # On repeat, traveling to thousand cuts gives 2/3 photos
        # LOOT DAISY: Daisy should stay outside, no dialog, not gun sound, just die
    # Mission("The Bane", Reward("GD_Z3_Bane.M_Bane"), tags=Tag.LongMission),
        # Mission giving ECHO disappears
    Mission("Hell Hath No Fury", Reward("GD_Z2_HellHathNo.M_FloodingHyperionCity")),
        # On repeat, foreman doesnt respawn
    Mission("Statuesque", Reward("GD_Z2_HyperionStatue.M_MonumentsVandalism"), tags=Tag.LongMission),
        # On repeat, third statue softlocks, not progressing to "here's your prize" enemy wave
    Mission("Home Movies", Reward("GD_Z2_HomeMovies.M_HomeMovies")),
    Mission("Written by the Victor", Reward("GD_Z2_WrittenByVictor.M_WrittenByVictor", purge=True)),
        # On repeat, history buttons are disabled
        # After all dialog plays after first turn-in, button becomes disabled
    Mission("Bearer of Bad News", Reward("GD_Z1_BearerBadNews.M_BearerBadNews")),
    Mission("BFFs", Reward("GD_Z1_BFFs.M_BFFs", purge=True)),
        # After completion, cannot interact with Sam to reaccpet mission
        # After save quit, Sam not spawned to give mission
        # Jim will drop item
    Mission("Demon Hunter", Reward("GD_Z2_DemonHunter.M_DemonHunter")),
        # On repeat, mom no spawn without savequit
    # Mission("Geary's Unbreakable Gear", Reward(""), tags=Tag.LongMission),
        # Make each of the three rakk chests give guaranteed item
    Mission("Monster Mash (Part 1)", Reward("GD_Z3_MonsterMash1.M_MonsterMash1")),
    Mission("Monster Mash (Part 2)", Reward("GD_Z3_MonsterMash2.M_MonsterMash2")),
    Mission("Monster Mash (Part 3)", Reward("GD_Z3_MonsterMash3.M_MonsterMash3"), tags=Tag.LongMission),
        # Only 29 skrakk and 1 spycho total spawn
    Mission("Kill Yourself (Do it)", Reward("GD_Z3_KillYourself.M_KillYourself")),
        # Killing self doesnt trigger on repeat
    Mission("Kill Yourself (Don't do it)", AltReward("GD_Z3_KillYourself.M_KillYourself")),
    Mission("Customer Service", Reward("GD_Z3_CustomerService.M_CustomerService")),
        # Mailboxes unopenable on repeat
    Mission("To Grandmother's House We Go", Reward("GD_Z3_GrandmotherHouse.M_GrandmotherHouse")),
    Mission("A Real Boy: Clothes Make the Man", Reward("GD_Z2_ARealBoy.M_ARealBoy_Clothes")),
        # On repeat, Mal unable to accept so many clothes
    Mission("A Real Boy: Face Time", Reward("GD_Z2_ARealBoy.M_ARealBoy_ArmLeg")),
        # On repeat, topmost two limbs (legs) do not respawn
    Mission("A Real Boy: Human", Reward("GD_Z2_ARealBoy.M_ARealBoy_Human")),
        # On repeat, mal unprepared for combat
    Mission("Hyperion Slaughter: Round 1", Reward("GD_Z3_RobotSlaughter.M_RobotSlaughter_1"), tags=Tag.Slaughter),
    Mission("Hyperion Slaughter: Round 2", Reward("GD_Z3_RobotSlaughter.M_RobotSlaughter_2"), tags=Tag.Slaughter),
    Mission("Hyperion Slaughter: Round 3", Reward("GD_Z3_RobotSlaughter.M_RobotSlaughter_3"), tags=Tag.Slaughter),
    Mission("Hyperion Slaughter: Round 4", Reward("GD_Z3_RobotSlaughter.M_RobotSlaughter_4"), tags=Tag.Slaughter),
    Mission("Hyperion Slaughter: Round 5", Reward("GD_Z3_RobotSlaughter.M_RobotSlaughter_5"), tags=Tag.Slaughter),
    Mission("The Lost Treasure", Reward("GD_Z3_LostTreasure.M_LostTreasure", purge=True), tags=Tag.LongMission),
        # Mission ECHO box unopenable after completion
    Mission("The Great Escape", Reward("GD_Z3_GreatEscape.M_GreatEscape", purge=True)),
        # Beacon doesnt spawn on repeat
        # Ulysses stays dead after save quit
    Mission("The Chosen One", Reward("GD_Z3_ChosenOne.M_ChosenOne")),
    Mission("Capture the Flags", Reward("GD_Z3_CaptureTheFlags.M_CaptureTheFlags"), tags=Tag.LongMission),
    Mission("This Just In", Reward("GD_Z3_ThisJustIn.M_ThisJustIn")),
    Mission("Uncle Teddy (Turn in Una)", Reward("GD_Z3_UncleTeddy.M_UncleTeddy")),
    Mission("Uncle Teddy (Turn in Hyperion)", AltReward("GD_Z3_UncleTeddy.M_UncleTeddy")),
        # ECHO boxes dont reclose on repeat
    Mission("Get to Know Jack", Reward("GD_Z3_YouDontKnowJack.M_YouDontKnowJack")),
        # ECHO rakk doesnt respawn on repeat
    Mission("Hungry Like the Skag", Reward("GD_Z3_HungryLikeSkag.M_HungryLikeSkag", purge=True)),
        # Skags dont drop mission pickup after completion
    Mission("You. Will. Die. (Seriously.)", Reward("GD_Z2_ThresherRaid.M_ThresherRaid")),
        # Terra no respawn after first completion


    Mission("Message in a Bottle (Oasis)", Reward("GD_Orchid_SM_Message.M_Orchid_MessageInABottle1", purge=True), tags=Tag.PiratesBooty),
        # On repeat, bottle uninteractable without savequit
    Mission("Burying the Past", Reward("GD_Orchid_SM_BuryPast.M_Orchid_BuryingThePast"), tags=Tag.PiratesBooty),
    Mission("Man's Best Friend", Reward("GD_Orchid_SM_MansBestFriend.M_Orchid_MansBestFriend"), tags=Tag.PiratesBooty),
    Mission("Fire Water", Reward("GD_Orchid_SM_FireWater.M_Orchid_FireWater"), tags=Tag.PiratesBooty),
    Mission("Giving Jocko A Leg Up", Reward("GD_Orchid_SM_JockoLegUp.M_Orchid_JockoLegUp"), tags=Tag.PiratesBooty),
    Mission("Wingman", Reward("GD_Orchid_SM_Wingman.M_Orchid_Wingman"), tags=Tag.PiratesBooty),
    Mission("Smells Like Victory", Reward("GD_Orchid_SM_Smells.M_Orchid_SmellsLikeVictory"), tags=Tag.PiratesBooty),
        # Shiv-spike doesnt respawn without savequit
    Mission("Declaration Against Independents", Reward("GD_Orchid_SM_Declaration.M_Orchid_DeclarationAgainstIndependents"), tags=Tag.PiratesBooty),
        # Not enough union vehicles spawn unless savequit
    Mission("Ye Scurvy Dogs", Reward("GD_Orchid_SM_Scurvy.M_Orchid_ScurvyDogs"), tags=Tag.PiratesBooty),
        # Fruits unshootable unless savequit
    Mission("Message in a Bottle (Wurmwater)", Reward("GD_Orchid_SM_Message.M_Orchid_MessageInABottle2", purge=True), tags=Tag.PiratesBooty),
        # Bottle uninteractable after completion
    Mission("Message in a Bottle (Hayter's Folly)", Reward("GD_Orchid_SM_Message.M_Orchid_MessageInABottle3", purge=True), tags=Tag.PiratesBooty),
        # Bottle uninteractable after completion
    Mission("Grendel", Reward("GD_Orchid_SM_Grendel.M_Orchid_Grendel"), tags=Tag.PiratesBooty),
        # Grendel doesnt respawn without savequit
    Mission("Just Desserts for Desert Deserters", Reward("GD_Orchid_SM_Deserters.M_Orchid_Deserters"), tags=Tag.PiratesBooty),
        # Deserters dont respawn without savequit
    Mission("Message in a Bottle (The Rustyards)", Reward("GD_Orchid_SM_Message.M_Orchid_MessageInABottle4", purge=True), tags=Tag.PiratesBooty),
        # Bottle uninteractable after completion
    Mission("I Know It When I See It", Reward("GD_Orchid_SM_KnowIt.M_Orchid_KnowItWhenSeeIt"), tags=Tag.PiratesBooty),
    Mission("Don't Copy That Floppy", Reward("GD_Orchid_SM_FloppyCopy.M_Orchid_DontCopyThatFloppy"), tags=Tag.PiratesBooty),
        # Not enough floppy pirates spawn without savequit
    Mission("Freedom of Speech", Reward("GD_Orchid_SM_Freedom.M_Orchid_FreedomOfSpeech"), tags=Tag.PiratesBooty),
        # DJ Tanner doesnt respawn until savequit
    Mission("Message In A Bottle (Magnys Lighthouse)", Reward("GD_Orchid_SM_Message.M_Orchid_MessageInABottle6", purge=True), tags=Tag.PiratesBooty),
    Mission("Faster Than the Speed of Love", Reward("GD_Orchid_SM_Race.M_Orchid_Race"), tags=Tag.PiratesBooty),
    Mission("Catch-A-Ride, and Also Tetanus", Reward("GD_Orchid_SM_Tetanus.M_Orchid_CatchRideTetanus"), tags=Tag.PiratesBooty),
    Mission("Treasure of the Sands", Reward("GD_Orchid_SM_EndGameClone.M_Orchid_EndGame"), tags=Tag.PiratesBooty|Tag.VeryLongMission),
        # Roscoe/Scarlett dont respawn until savequit
    Mission("Hyperius the Invincible", Reward("GD_Orchid_Raid.M_Orchid_Raid1"), tags=Tag.PiratesBooty|Tag.RaidMission|Tag.LongMission),
    Mission("Master Gee the Invincible", Reward("GD_Orchid_Raid.M_Orchid_Raid3"), tags=Tag.PiratesBooty|Tag.RaidMission),

    Mission("Tier 2 Battle: Bar Room Blitz", Reward("GD_IrisEpisode03_Battle.M_IrisEp3Battle_BarFight2"), tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Tier 3 Battle: Bar Room Blitz", Reward("GD_IrisEpisode03_Battle.M_IrisEp3Battle_BarFight3"), tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Tier 3 Rematch: Bar Room Blitz", Reward("GD_IrisEpisode03_Battle.M_IrisEp3Battle_BarFightR3"), tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Totally Recall", Reward("GD_IrisDL2_ProductRecall.M_IrisDL2_ProductRecall"), tags=Tag.CampaignOfCarnage),
    Mission("Tier 2 Battle: The Death Race", Reward("GD_IrisEpisode04_Battle.M_IrisEp4Battle_Race2"), tags=Tag.CampaignOfCarnage),
    Mission("Tier 3 Battle: The Death Race", Reward("GD_IrisEpisode04_Battle.M_IrisEp4Battle_Race4"), tags=Tag.CampaignOfCarnage),
    Mission("Tier 3 Rematch: The Death Race", Reward("GD_IrisEpisode04_Battle.M_IrisEp4Battle_RaceR4"), tags=Tag.CampaignOfCarnage),
    Mission("Tier 2 Battle: Twelve O' Clock High", Reward("GD_IrisEpisode05_Battle.M_IrisEp5Battle_FlyboyGyro2"), tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Tier 3 Battle: Twelve O' Clock High", Reward("GD_IrisEpisode05_Battle.M_IrisEp5Battle_FlyboyGyro3"), tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Tier 3 Rematch: Twelve O' Clock High", Reward("GD_IrisEpisode05_Battle.M_IrisEp5Battle_FlyboyGyroR3"), tags=Tag.CampaignOfCarnage|Tag.Slaughter),
        # Timer doesnt trigger for all tiers when repeated concurrently
        # Not enough buzzards spawn when repeated concurrently
    Mission("Tier 2 Battle: Appetite for Destruction", Reward("GD_IrisEpisode02_Battle.M_IrisEp2Battle_CoP2"), tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Tier 3 Battle: Appetite for Destruction", Reward("GD_IrisEpisode02_Battle.M_IrisEp2Battle_CoP3"), tags=Tag.CampaignOfCarnage|Tag.Slaughter),
    Mission("Tier 3 Rematch: Appetite for Destruction", Reward("GD_IrisEpisode02_Battle.M_IrisEp2Battle_CoPR3"), tags=Tag.CampaignOfCarnage|Tag.Slaughter),
        # When tiers repeated concurrently, killing all enemies doesnt complete wave 4
    Mission("Mother-Lover (Turn in Scooter)", Reward("GD_IrisDL2_DontTalkAbtMama.M_IrisDL2_DontTalkAbtMama"), tags=Tag.CampaignOfCarnage),
    Mission("Mother-Lover (Turn in Moxxi)", AltReward("GD_IrisDL2_DontTalkAbtMama.M_IrisDL2_DontTalkAbtMama"), tags=Tag.CampaignOfCarnage),
    Mission("Everybody Wants to be Wanted", Reward("GD_IrisHUB_Wanted.M_IrisHUB_Wanted"), tags=Tag.CampaignOfCarnage),
    Mission("Interview with a Vault Hunter", Reward("GD_IrisHUB_SmackTalk.M_IrisHUB_SmackTalk"), tags=Tag.CampaignOfCarnage),
    Mission("Walking the Dog", Reward("GD_IrisHUB_WalkTheDog.M_IrisHUB_WalkTheDog"), tags=Tag.CampaignOfCarnage|Tag.LongMission),
    Mission("My Husband the Skag (Kill Uriah)", Reward("GD_IrisDL3_MySkag.M_IrisDL3_MySkag"), tags=Tag.CampaignOfCarnage),
    Mission("My Husband the Skag (Spare Uriah)", AltReward("GD_IrisDL3_MySkag.M_IrisDL3_MySkag"), tags=Tag.CampaignOfCarnage),
        # Skags dont respawn without savequit
    Mission("Say That To My Face", Reward("GD_IrisDL3_PSYouSuck.M_IrisDL3_PSYouSuck"), tags=Tag.CampaignOfCarnage),
    Mission("Commercial Appeal", Reward("GD_IrisDL3_CommAppeal.M_IrisDL3_CommAppeal"), tags=Tag.CampaignOfCarnage|Tag.LongMission),
    Mission("Pete the Invincible", Reward("GD_IrisRaidBoss.M_Iris_RaidPete"), tags=Tag.CampaignOfCarnage|Tag.RaidMission),
        # Pete doesnt respawn without savequit
    Mission("Number One Fan", Reward("GD_IrisDL2_PumpkinHead.M_IrisDL2_PumpkinHead"), tags=Tag.CampaignOfCarnage),
        # Sully doesnt respawn without savequit
    Mission("Monster Hunter", Reward("GD_IrisHUB_MonsterHunter.M_IrisHUB_MonsterHunter"), tags=Tag.CampaignOfCarnage),
    Mission("Gas Guzzlers (Turn in Hammerlock)", Reward("GD_IrisHUB_GasGuzzlers.M_IrisHUB_GasGuzzlers"), tags=Tag.CampaignOfCarnage|Tag.LongMission),
    Mission("Gas Guzzlers (Turn in Scooter)", AltReward("GD_IrisHUB_GasGuzzlers.M_IrisHUB_GasGuzzlers"), tags=Tag.CampaignOfCarnage|Tag.LongMission),
    Mission("Matter Of Taste", Reward("GD_IrisHUB_MatterOfTaste.M_IrisHUB_MatterOfTaste"), tags=Tag.CampaignOfCarnage|Tag.LongMission),
        # Staff enemies do not respawn without savequit

    Mission("An Acquired Taste", Reward("GD_Sage_SM_AcquiredTaste.M_Sage_AcquiredTaste"), tags=Tag.HammerlocksHunt),
    Mission("Big Feet", Reward("GD_Sage_SM_BigFeet.M_Sage_BigFeet"), tags=Tag.HammerlocksHunt),
    Mission("Still Just a Borok in a Cage", Reward("GD_Sage_SM_BorokCage.M_Sage_BorokCage"), tags=Tag.HammerlocksHunt),
    Mission("The Rakk Dahlia Murder", Reward("GD_Sage_SM_DahliaMurder.M_Sage_DahliaMurder"), tags=Tag.HammerlocksHunt),
    Mission("Egg on Your Face", Reward("GD_Sage_SM_EggOnFace.M_Sage_EggOnFace"), tags=Tag.HammerlocksHunt),
    Mission("Follow The Glow", Reward("GD_Sage_SM_FollowGlow.M_Sage_FollowGlow"), tags=Tag.HammerlocksHunt),
    Mission("Nakayama-rama", Reward("GD_Sage_SM_Nakarama.M_Sage_Nakayamarama"), tags=Tag.HammerlocksHunt),
    Mission("Now You See It", Reward("GD_Sage_SM_NowYouSeeIt.M_Sage_NowYouSeeIt"), tags=Tag.HammerlocksHunt),
    Mission("Ol' Pukey", Reward("GD_Sage_SM_OldPukey.M_Sage_OldPukey"), tags=Tag.HammerlocksHunt),
    Mission("Palling Around", Reward("GD_Sage_SM_PallingAround.M_Sage_PallingAround"), tags=Tag.HammerlocksHunt),
    Mission("I Like My Monsters Rare", Reward("GD_Sage_SM_RareSpawns.M_Sage_RareSpawns"), tags=Tag.HammerlocksHunt),
    Mission("Urine, You're Out", Reward("GD_Sage_SM_Urine.M_Sage_Urine"), tags=Tag.HammerlocksHunt),
    Mission("Voracidous the Invincible", Reward("GD_Sage_Raid.M_Sage_Raid"), tags=Tag.HammerlocksHunt),

    Mission("The Amulet", Reward("GD_Aster_AmuletDoNothing.M_AmuletDoNothing"), tags=Tag.DragonKeep),
    Mission("The Claptrap's Apprentice", Reward("GD_Aster_ClaptrapApprentice.M_ClaptrapApprentice"), tags=Tag.DragonKeep),
    Mission("The Beard Makes The Man", Reward("GD_Aster_ClapTrapBeard.M_ClapTrapBeard"), tags=Tag.DragonKeep),
    Mission("My Kingdom for a Wand", Reward("GD_Aster_ClaptrapWand.M_WandMakesTheMan"), tags=Tag.DragonKeep),
    Mission("Critical Fail", Reward("GD_Aster_CriticalFail.M_CriticalFail"), tags=Tag.DragonKeep),
    Mission("My Dead Brother", Reward("GD_Aster_DeadBrother.M_MyDeadBrother"), tags=Tag.DragonKeep),
    Mission("Lost Souls", Reward("GD_Aster_DemonicSouls.M_DemonicSouls"), tags=Tag.DragonKeep),
    Mission("Ell in Shining Armor", Reward("GD_Aster_EllieDress.M_EllieDress"), tags=Tag.DragonKeep),
    Mission("Fake Geek Guy", Reward("GD_Aster_FakeGeekGuy.M_FakeGeekGuy"), tags=Tag.DragonKeep),
    Mission("Feed Butt Stallion", Reward("GD_Aster_FeedButtStallion.M_FeedButtStallion"), tags=Tag.DragonKeep),
    Mission("Loot Ninja", Reward("GD_Aster_LootNinja.M_LootNinja"), tags=Tag.DragonKeep),
    Mission("MMORPGFPS", Reward("GD_Aster_MMORPGFPS.M_MMORPGFPS"), tags=Tag.DragonKeep),
    Mission("Pet Butt Stallion", Reward("GD_Aster_PetButtStallion.M_PettButtStallion"), tags=Tag.DragonKeep),
    Mission("Post-Crumpocalyptic", Reward("GD_Aster_Post-Crumpocalyptic.M_Post-Crumpocalyptic"), tags=Tag.DragonKeep),
    Mission("Raiders of the Last Boss", Reward("GD_Aster_RaidBoss.M_Aster_RaidBoss"), tags=Tag.DragonKeep),
    Mission("Roll Insight", Reward("GD_Aster_RollInsight.M_RollInsight"), tags=Tag.DragonKeep),
    Mission("Tree Hugger", Reward("GD_Aster_TreeHugger.M_TreeHugger"), tags=Tag.DragonKeep),
    Mission("Winter is a Bloody Business", Reward("GD_Aster_WinterIsComing.M_WinterIsComing"), tags=Tag.DragonKeep|Tag.Slaughter),
    Mission("Magic Slaughter: Round 1", Reward("GD_Aster_TempleSlaughter.M_TempleSlaughter1"), tags=Tag.DragonKeep|Tag.Slaughter),
    Mission("Magic Slaughter: Round 2", Reward("GD_Aster_TempleSlaughter.M_TempleSlaughter2"), tags=Tag.DragonKeep|Tag.Slaughter),
    Mission("Magic Slaughter: Round 3", Reward("GD_Aster_TempleSlaughter.M_TempleSlaughter3"), tags=Tag.DragonKeep|Tag.Slaughter),
    Mission("Magic Slaughter: Round 4", Reward("GD_Aster_TempleSlaughter.M_TempleSlaughter4"), tags=Tag.DragonKeep|Tag.Slaughter),
    Mission("Magic Slaughter: Round 5", Reward("GD_Aster_TempleSlaughter.M_TempleSlaughter5"), tags=Tag.DragonKeep|Tag.Slaughter),
    Mission("Magic Slaughter: Badass Round", Reward("GD_Aster_TempleSlaughter.M_TempleSlaughter6Badass"), tags=Tag.DragonKeep),
    Mission("The Magic of Childhood", Reward("GD_Aster_TempleTower.M_TempleTower"), tags=Tag.DragonKeep),
    Mission("Find Murderlin's Temple", Reward("GD_Aster_TempleSlaughter.M_TempleSlaughterIntro"), tags=Tag.DragonKeep),
    Mission("The Sword in The Stoner", Reward("GD_Aster_SwordInStone.M_SwordInStoner"), tags=Tag.DragonKeep),

    Mission("Claptocurrency", Reward("GD_Anemone_Side_Claptocurrency.M_Claptocurrency"), tags=Tag.FightForSanctuary),
    Mission("BFFFs", Reward("GD_Anemone_Side_EyeSnipers.M_Anemone_EyeOfTheSnipers"), tags=Tag.FightForSanctuary),
    Mission("Hypocritical Oath", Reward("GD_Anemone_Side_HypoOathPart1.M_HypocriticalOathPart1"), tags=Tag.FightForSanctuary),
    Mission("Cadeuceus", Reward("GD_Anemone_Side_HypoOathPart2.M_HypocriticalOathPart2"), tags=Tag.FightForSanctuary),
    Mission("My Brittle Pony", Reward("GD_Anemone_Side_MyBrittlePony.M_Anemone_MyBrittlePony"), tags=Tag.FightForSanctuary),
    Mission("The Oddest Couple", Reward("GD_Anemone_Side_OddestCouple.M_Anemone_OddestCouple"), tags=Tag.FightForSanctuary),
    Mission("A Most Cacophonous Lure", Reward("GD_Anemone_Side_RaidBoss.M_Anemone_CacophonousLure"), tags=Tag.FightForSanctuary),
    Mission("Sirentology", Reward("GD_Anemone_Side_Sirentology.M_Anemone_Sirentology"), tags=Tag.FightForSanctuary),
    Mission("Space Cowboy", Reward("GD_Anemone_Side_SpaceCowboy.M_Anemone_SpaceCowboy"), tags=Tag.FightForSanctuary),
    Mission("The Vaughnguard", Reward("GD_Anemone_Side_VaughnPart1.M_Anemone_VaughnPart1"), tags=Tag.FightForSanctuary),
    Mission("The Hunt is Vaughn", Reward("GD_Anemone_Side_VaughnPart2.M_Anemone_VaughnPart2"), tags=Tag.FightForSanctuary),
    Mission("Chief Executive Overlord", Reward("GD_Anemone_Side_VaughnPart3.M_Anemone_VaughnPart3"), tags=Tag.FightForSanctuary),
    Mission("Echoes of the Past", Reward("GD_Anemone_Side_Echoes.M_Anemone_EchoesOfThePast"), tags=Tag.FightForSanctuary),

    Mission("Grandma Flexington's Story", Reward("GD_Allium_GrandmaFlexington.M_ListenToGrandma"), tags=Tag.WattleGobbler|Tag.LongMission),
        # replace $1 to provide yet additional item copy
    Mission("Grandma Flexington's Story: Raid Difficulty", Reward("GD_Allium_Side_GrandmaRaid.M_ListenToGrandmaRaid"), tags=Tag.WattleGobbler|Tag.RaidMission|Tag.VeryLongMission),
        # replace purple launcher to provide yet additional item copy
    Mission("Special Delivery", Reward("GD_Allium_Delivery.M_Delivery"), tags=Tag.MercenaryDay),
    Mission("Trick or Treat", Reward("GD_FlaxMissions.M_TrickOrTreat"), tags=Tag.BloodyHarvest),
    Mission("Victims of Vault Hunters", Reward("GD_Nast_Easter_Mission_Side01.M_Nast_Easter_Side01"), tags=Tag.SonOfCrawmerax),
    Mission("Learning to Love", Reward("GD_Nast_Vday_Mission_Side01.M_Nast_Vday_Side01"), tags=Tag.WeddingDayMassacre),

    Mission("A History of Simulated Violence", Reward("GD_Lobelia_TestingZone.M_TestingZone"), tags=Tag.DigistructPeak|Tag.VeryLongMission|Tag.RaidMission),
    Mission("More History of Simulated Violence", Reward("GD_Lobelia_TestingZone.M_TestingZoneRepeatable"), tags=Tag.DigistructPeak|Tag.VeryLongMission|Tag.RaidMission),
)


"""
- gearys unbreakable gear
"""