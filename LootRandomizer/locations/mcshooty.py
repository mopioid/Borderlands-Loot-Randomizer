from __future__ import annotations

from unrealsdk import Log, FindObject, GetEngine #type: ignore
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct #type: ignore

from .. import locations


_mcshooty_pawn: UObject = None


class McShooty(locations.MapDropper):
    map_name = "Grass_Cliffs_P"

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

        # global _mcshooty_sequence, _mcshooty_pawn
        # _mcshooty_sequence = FindObject("Sequence", "Grass_Cliffs_Dynamic.TheWorld:PersistentLevel.Main_Sequence.ShootMeInTheFace")
        # _mcshooty_pawn.MissionDirectives.MissionDirectives[0].bEndsMission = True
        # _mcshooty_sequence.SequenceObjects[5].MissionDirectives[0].bEndsMission = False
        # shooty_dead = _mcshooty_pawn.AIClass.BehaviorProviderDefinition.BehaviorSequences[2].CustomEnableCondition


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

    RemoveHook("Engine.Pawn.TakeDamage", "LootRandomizer.McShooty")
    caller.TakeDamage(
        0,
        params.InstigatedBy, # Controller
        (params.HitLocation.X, params.HitLocation.Y, params.HitLocation.Z), # Vector
        (params.Momentum.X, params.Momentum.Y, params.Momentum.Z), # Vector
        params.DamageType, # class<DamageType> 
        (
            params.HitInfo.Material,
            params.HitInfo.PhysMaterial,
            params.HitInfo.Item,
            params.HitInfo.LevelIndex,
            params.HitInfo.BoneName,
            params.HitInfo.HitComponent,
        ),
        params.DamageCauser.ObjectPointer, # optional IDamageCauser
        params.Pipeline # optional DamagePipeline
    )
    RunHook("Engine.Pawn.TakeDamage", "LootRandomizer.McShooty", TakeDamage)

    if params.Pipeline.DamageSummary.bWasCrit:
        head_bpd = caller.BodyClass.HitRegionList[0].BehaviorProviderDefinition
        objective_behavior = head_bpd.BehaviorSequences[0].BehaviorData2[6].Behavior
        objective_behavior.ApplyBehaviorToContext(caller, (), caller, None, None, (), None)

    return False


"""
- revert mcshooty's enemy status after completion
- block non-face-shooting dialog on crit

"""