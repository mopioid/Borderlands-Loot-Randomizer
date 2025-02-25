from __future__ import annotations

from unrealsdk import (
    ConstructObject,
    FindObject,
    GetEngine,
    KeepAlive,
    Log,
    UClass,
)
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct

import os

from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from typing import TYPE_CHECKING
from Mods.ModMenu import Game

BL2 = Game.GetCurrent() is Game.BL2
TPS = Game.GetCurrent() is Game.TPS

if TYPE_CHECKING:
    from .bl2 import *
elif BL2:
    from .bl2 import *
elif TPS:
    from .tps import *
else:
    raise


mod_dir = os.path.dirname(os.path.dirname(__file__))
seeds_dir = os.path.join(mod_dir, "Seeds")
seeds_file = os.path.join(seeds_dir, "Seed List.txt")


__all__ = (
    "BL2",
    "TPS",
    "CurrentVersion",
    "SupportedVersions",
    "Character",
    "Category",
    "Hint",
    "Tag",
    "TagList",
    "ContentTags",
    "MissionTags",
    "EnemyTags",
    "OtherTags",
    "pool_whitelist",
    "Package",
    "mod_dir",
    "seeds_dir",
    "seeds_file",
    "get_pc",
    "get_missiontracker",
    "get_behaviorkernel",
    "get_pawns",
    "get_pawn",
    "is_client",
    "set_command",
    "convert_struct",
    "construct_object",
    "do_next_tick",
    "tick_while",
    "spawn_loot",
    "spawn_item",
    "construct_behaviorsequence_behavior",
    "show_dialog",
    "show_confirmation",
    "BPD",
)


Package: UObject = ConstructObject("Package", None, "LootRandomizer")
KeepAlive(Package)


def get_pc() -> UObject:
    return GetEngine().GamePlayers[0].Actor


def get_missiontracker() -> UObject:
    return get_pc().WorldInfo.GRI.MissionTracker


def get_behaviorkernel() -> UObject:
    return get_pc().GetWillowGlobals().TheBehaviorKernel


def get_pawns() -> Generator[UObject, None, None]:
    pawn = GetEngine().GetCurrentWorldInfo().PawnList
    while pawn:
        yield pawn
        pawn = pawn.NextPawn


def get_pawn(aiclass: str) -> Union[UObject, None]:
    for pawn in get_pawns():
        if pawn.AIClass and pawn.AIClass.Name == aiclass:
            return pawn
    return None


def is_client() -> UObject:
    return GetEngine().GetCurrentWorldInfo().NetMode == 3


def set_command(uobject: UObject, attribute: str, value: str):
    get_pc().ConsoleCommand(
        f"set {UObject.PathName(uobject)} {attribute} {value}"
    )


def convert_struct(fstruct: Any) -> Any:
    iterator: Optional[Iterator[Any]] = None
    try:
        iterator = iter(fstruct)
        try:
            int(fstruct)
            iterator = None
        except:
            pass
    except:
        pass

    if iterator:
        return [convert_struct(value) for value in iterator]

    struct_type = getattr(fstruct, "structType", None)
    if struct_type is None:
        return fstruct

    values: List[Any] = []

    while struct_type:
        attribute = struct_type.Children
        while attribute:
            value = getattr(fstruct, attribute.GetName())
            values.append(convert_struct(value))
            attribute = attribute.Next
        struct_type = struct_type.SuperField

    return tuple(values)


def construct_object(
    basis: Optional[Union[str, UObject, UClass]],
    name: Union[str, UObject, None] = None,
) -> UObject:
    if not basis:
        raise Exception(
            f"Attempted to construct object '{name}' with None basis"
        )

    path: Optional[str] = None
    class_name = basis

    kwargs: Dict[str, Any] = {"Class": basis, "Outer": Package}

    if isinstance(name, str):
        name = "".join(char for char in name if char.isalnum() or char == "_")
        kwargs["Name"] = name
        path = f"{Package.Name}.{name}"
    elif name:
        kwargs["Outer"] = name

    if not isinstance(basis, str):
        kwargs["Template"] = basis
        kwargs["Class"] = basis.Class
        class_name = str(basis.Class.Name)

    obj: Optional[UObject] = None
    if path and (
        isinstance(class_name, str) or isinstance(class_name, UClass)
    ):
        obj = FindObject(class_name, path)

    if not obj:
        obj = ConstructObject(**kwargs)  # type: ignore
        KeepAlive(obj)

    return obj


def do_next_tick(*routines: Callable[[], None]) -> None:
    if not routines:
        return

    def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
        RemoveHook("Engine.Interaction.Tick", f"LootRandomizer.{id(routines)}")
        for routine in routines:
            routine()
        return True

    RunHook("Engine.Interaction.Tick", f"LootRandomizer.{id(routines)}", hook)


def tick_while(routine: Callable[[], bool]) -> None:
    if not routine():
        return

    def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
        result = False
        try:
            result = routine()
        finally:
            if not result:
                RemoveHook(
                    "Engine.Interaction.Tick", f"LootRandomizer.{id(routine)}"
                )
            return True

    RunHook("Engine.Interaction.Tick", f"LootRandomizer.{id(routine)}", hook)


def spawn_loot(
    pools: Sequence[UObject],
    context: UObject,
    location: Optional[Tuple[float, float, float]] = None,
    velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    radius: int = 0,
) -> None:
    spawner = construct_object("Behavior_SpawnLootAroundPoint")
    if location is not None:
        spawner.CircularScatterRadius = radius
        spawner.CustomLocation = (location, None, "")
        spawner.SpawnVelocity = velocity
        spawner.SpawnVelocityRelativeTo = 1

    spawner.ItemPools = pools
    spawner.ApplyBehaviorToContext(context, (), None, None, None, ())


def spawn_item(
    pool: UObject, context: UObject, callback: Callable[[UObject], None]
) -> None:
    spawner = ConstructObject("Behavior_SpawnLootAroundPoint")
    spawner.ItemPools = (pool,)
    spawner.SpawnVelocityRelativeTo = 1
    spawner.CustomLocation = (
        (float("inf"), float("inf"), float("inf")),
        None,
        "",
    )

    def hook(caller: UObject, _f: UFunction, params: FStruct) -> bool:
        if caller is spawner:
            spawned_loot = tuple(params.SpawnedLoot)
            if len(spawned_loot):
                callback(spawned_loot[0].Inv)
            RemoveHook(
                "WillowGame.Behavior_SpawnLootAroundPoint.PlaceSpawnedItems",
                f"LootRandomizer.{id(spawner)}",
            )
        return True

    RunHook(
        "WillowGame.Behavior_SpawnLootAroundPoint.PlaceSpawnedItems",
        f"LootRandomizer.{id(spawner)}",
        hook,
    )

    spawner.ApplyBehaviorToContext(context, (), None, None, None, ())


def show_confirmation(
    title: str, message: str, on_confirm: Callable[[], None]
) -> None:
    dialog = get_pc().GFxUIManager.ShowDialog()
    dialog.SetText(title, message)
    dialog.bNoCancel = False
    dialog.AppendButton("Confirm", "Confirm", "")
    dialog.AppendButton("Cancel", "Cancel", "")
    dialog.SetDefaultButton("Cancel", True)
    dialog.ApplyLayout()

    def unhook(caller: UObject, function: UFunction, params: FStruct) -> bool:
        RemoveHook("WillowGame.WillowGFxDialogBox.Cancelled", "LootRandomizer")
        RemoveHook("WillowGame.WillowGFxDialogBox.Accepted", "LootRandomizer")
        return True

    def confirm(caller: UObject, function: UFunction, params: FStruct) -> bool:
        unhook(caller, function, params)
        if caller.CurrentSelection == 0:
            on_confirm()
        return True

    RunHook(
        "WillowGame.WillowGFxDialogBox.Cancelled", "LootRandomizer", unhook
    )
    RunHook(
        "WillowGame.WillowGFxDialogBox.Accepted", "LootRandomizer", confirm
    )


def construct_behaviorsequence_behavior(
    *path_components: str,
    sequence: str,
    enables: bool = True,
    outer: UObject,
):
    path_components = ("",) * (6 - len(path_components)) + path_components

    pathname_value = (
        "("
        + "".join(
            f"PathComponentNames[{index}]={path_component},"
            for index, path_component in enumerate(path_components)
        )
        + "IsSubobjectMask=16)"
    )

    behavior = construct_object(
        "Behavior_ChangeRemoteBehaviorSequenceState", outer
    )
    behavior.Action = 1 if enables else 2
    set_command(behavior, "SequenceName", sequence)
    set_command(behavior, "ProviderDefinitionPathName", pathname_value)
    return behavior


def show_dialog(title: str, message: str, duration: float = 0) -> None:
    get_pc().GFxUIManager.ShowTrainingDialog(
        message, title, duration, 0, False
    )


class BPD:
    uobject: UObject
    consumer: Optional[UObject]

    def __init__(
        self, uobject: UObject, consumer: Optional[UObject] = None
    ) -> None:
        self.consumer = consumer
        self.uobject = uobject

    @staticmethod
    def Path(path: str) -> BPD:
        uobject = FindObject("BehaviorProviderDefinition", path)
        if not uobject:
            raise Exception(f"Could not locate BPD {path}")
        return BPD(uobject)

    @staticmethod
    def Pawn(consumer: UObject) -> BPD:
        uobject = consumer.AIClass.BehaviorProviderDefinition
        if not uobject:
            raise Exception(
                f"Could not locate BPD for {consumer.AIClass.Name}"
            )
        return BPD(uobject, consumer)

    @staticmethod
    def PawnAI(consumer: UObject) -> BPD:
        try:
            uobject = consumer.AIClass.AIDef.BehaviorProviderDefinition
            assert uobject
        except:
            raise Exception(f"Could not locate BPD for {consumer.AIClass}")
        return BPD(uobject, consumer)

    @staticmethod
    def IO(consumer: UObject) -> BPD:
        return BPD(
            consumer.InteractiveObjectDefinition.BehaviorProviderDefinition,
            consumer,
        )

    def enable_sequence(self, sequence: str) -> None:
        if not self.consumer:
            raise Exception(
                f"No consumer for {UObject.PathName(self.uobject)}"
            )
        get_behaviorkernel().ChangeBehaviorSequenceActivationStatus(
            (self.consumer.ConsumerHandle.PID,), self.uobject, sequence, 1
        )

    def disable_sequence(self, sequence: str) -> None:
        if not self.consumer:
            raise Exception(
                f"No consumer for {UObject.PathName(self.uobject)}"
            )
        get_behaviorkernel().ChangeBehaviorSequenceActivationStatus(
            (self.consumer.ConsumerHandle.PID,), self.uobject, sequence, 2
        )

    def get_sequence(self, name: str) -> FStruct:
        for sequence in self.uobject.BehaviorSequences:
            if sequence.BehaviorSequenceName == name:
                return sequence
        raise Exception(
            f"Could not locate sequence '{name}' in BPD {UObject.PathName(self.uobject)}"
        )

    def construct_sequence_behavior(
        self,
        outer: UObject,
        sequence: str,
        enables: bool = True,
    ) -> UObject:
        behavior = construct_object(
            "Behavior_ChangeRemoteBehaviorSequenceState", outer
        )
        behavior.Action = 1 if enables else 2
        set_command(behavior, "SequenceName", sequence)

        path_components: List[str] = []
        for component in UObject.PathName(self.uobject).split("."):
            for component in component.split(":"):
                path_components.append(component)
        path_components = [""] * (6 - len(path_components)) + path_components

        set_command(
            behavior,
            "ProviderDefinitionPathName",
            (
                "("
                + "".join(
                    f"PathComponentNames[{index}]={path_component},"
                    for index, path_component in enumerate(path_components)
                )
                + "IsSubobjectMask=16)"
            ),
        )

        return behavior
