from __future__ import annotations
from . import locations

from unrealsdk import Log, FindObject, GetEngine, KeepAlive #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct #type: ignore

from . import defines
from .defines import Tag

from typing import List, Set


MissionTags = (
    Tag.ShortMission    |
    Tag.LongMission     |
    Tag.VeryLongMission |
    Tag.Slaughter       |
    Tag.RaidEnemy
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
    block_mission_item: bool

    uobject: UObject

    reward_items: List[UObject]
    reward_pools: List[UObject]

    @property
    def reward_attribute(self) -> FStruct:
        return self.uobject.Reward

    def __init__(self, path: str, purge: bool = False, block_mission_item: bool = False) -> None:
        self.path = path; self.purge = purge; self.block_mission_item = block_mission_item

    def register(self) -> None:
        self.uobject = FindObject("MissionDefinition", self.path)

        self.repeatable = self.uobject.bRepeatable

        self.reward_items = self.reward_attribute.RewardItems
        for item in self.reward_items:
            KeepAlive(item)

        self.reward_pools = self.reward_attribute.RewardItemPools
        for pool in self.reward_pools:
            KeepAlive(pool)

        self.uobject.bRepeatable = True
        self.reward_attribute.RewardItems = []

        self.reward_attribute.RewardItemPools = self.location.pools

        #TODO
        if self.block_mission_item:
            self.uobject

        if self.location.tags & (Tag.VeryLongMission|Tag.RaidEnemy):
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
    def __init__(
        self,
        name: str,
        *droppers: locations.Dropper,
        tags=Tag.BaseGame|Tag.ShortMission
    ) -> None:
        if not tags & defines.ContentTags:
            tags |= Tag.BaseGame
        if not tags & MissionTags:
            tags |= Tag.ShortMission

        if tags & (Tag.LongMission|Tag.VeryLongMission|Tag.RaidEnemy):
            rarities = (1, 1)
        else:
            rarities = (1,)

        super().__init__(name, *droppers, tags=tags, rarities=rarities)


_mcshooty_pawn: UObject = None


class McShooty(locations.MapDropper):
    map_names = ("Grass_Cliffs_P",)

    def register(self) -> None:
        super().register()
        GetEngine().GamePlayers[0].Actor.ConsoleCommand(f"set GD_Z1_ShootMeInTheFace.M_ShootMeInTheFace:Behavior_MissionRemoteEvent_21 EventName \"\"")

    def unregister(self) -> None:
        super().unregister()
        GetEngine().GamePlayers[0].Actor.ConsoleCommand(f"set GD_Z1_ShootMeInTheFace.M_ShootMeInTheFace:Behavior_MissionRemoteEvent_21 EventName ShootyFace_DestroyPop")

        global _mcshooty_pawn
        _mcshooty_pawn = None


    def inject(self) -> None:
        RunHook("WillowGame.WillowAIPawn.Behavior_ChangeUsability", "LootRandomizer.McShooty", PawnBehavior_ChangeUsability)
        RunHook("Engine.Pawn.TakeDamage", "LootRandomizer.McShooty", TakeDamage)
        RunHook("WillowGame.PopulationFactoryBalancedAIPawn.SetupBalancedPopulationActor", "LootRandomizer.McShooty", SetupBalancedPopulationActor)

        shooty_giver = FindObject("MissionDirectivesDefinition", "GD_Shootyface.Character.Pawn_Shootyface:MissionDirectivesDefinition_1")
        shooty_giver.MissionDirectives[0].bEndsMission = True

        shooty_ender = FindObject("MissionDirectivesDefinition", "Grass_Cliffs_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_725.MissionDirectivesDefinition_0")
        shooty_ender.MissionDirectives[0].bEndsMission = False

        shooty_dead = FindObject("BehaviorSequenceEnableByMission", "GD_Shootyface.Character.CharClass_Shootyface:BehaviorProviderDefinition_0.BehaviorSequenceEnableByMission_1")
        shooty_dead.MissionStatesToLinkTo.bReadyToTurnIn = False
        shooty_dead.MissionStatesToLinkTo.bComplete = False

    def uninject(self) -> None:
        RemoveHook("WillowGame.WillowAIPawn.Behavior_ChangeUsability", "LootRandomizer.McShooty")
        RemoveHook("Engine.Pawn.TakeDamage", "LootRandomizer.McShooty")
        RemoveHook("WillowGame.PopulationFactoryBalancedAIPawn.SetupBalancedPopulationActor", "LootRandomizer.McShooty")


def SetupBalancedPopulationActor(caller: UObject, function: UFunction, params: FStruct) -> bool:
    if params.SpawnedPawn.AIClass and params.SpawnedPawn.AIClass.Name == "CharClass_Shootyface":
        global _mcshooty_pawn
        _mcshooty_pawn = params.SpawnedPawn
        RemoveHook("WillowGame.PopulationFactoryBalancedAIPawn.SetupBalancedPopulationActor", "LootRandomizer.McShooty")
    return True

def PawnBehavior_ChangeUsability(caller: UObject, function: UFunction, params: FStruct) -> bool:
    return caller is not _mcshooty_pawn

def TakeDamage(caller: UObject, function: UFunction, params: FStruct) -> bool:
    if caller is not _mcshooty_pawn:
        return True
    
    hit = params.HitInfo

    RemoveHook("Engine.Pawn.TakeDamage", "LootRandomizer.McShooty")
    caller.TakeDamage(
        0,
        params.InstigatedBy, # Controller
        (params.HitLocation.X, params.HitLocation.Y, params.HitLocation.Z), # Vector
        (params.Momentum.X, params.Momentum.Y, params.Momentum.Z), # Vector
        params.DamageType, # class<DamageType> 
        (hit.Material, hit.PhysMaterial, hit.Item, hit.LevelIndex, hit.BoneName, hit.HitComponent),
        params.DamageCauser.ObjectPointer, # optional IDamageCauser
        params.Pipeline # optional DamagePipeline
    )
    RunHook("Engine.Pawn.TakeDamage", "LootRandomizer.McShooty", TakeDamage)

    if params.Pipeline.DamageSummary.bWasCrit:
        head_bpd = caller.BodyClass.HitRegionList[0].BehaviorProviderDefinition
        objective_behavior = head_bpd.BehaviorSequences[0].BehaviorData2[6].Behavior
        objective_behavior.ApplyBehaviorToContext(caller, (), caller, None, None, (), None)

    return False


class MissionGiver(locations.MapDropper):
    path: str
    index: int
    begins: bool
    ends: bool

    def __init__(
        self,
        map_name: str,
        path: str,
        index: int,
        begins: bool,
        ends: bool
    ) -> None:
        self.map_names = (map_name,)
        self.path = path; self.index = index
        self.begins = begins; self.ends = ends
        super().__init__()

    def inject(self) -> None:
        giver = FindObject("MissionDirectivesDefinition", self.path)
        directive = giver.MissionDirectives[self.index]
        directive.bBeginsMission = self.begins
        directive.bEndsMission = self.ends

"""
- revert mcshooty's enemy status after completion
- block non-face-shooting dialog on crit

"""
