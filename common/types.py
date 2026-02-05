"""Common type definitions used across the project."""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional, TypedDict, Literal

if TYPE_CHECKING:
    from backend.player import Player as _Player
    from backend.candidate_game import CandidateGame as _CandidateGame
    from backend.step import Step as _Step
    from backend.snapshots import (
        BaseSnapshot as _BaseSnapshot,
        HeapSnapshot as _HeapSnapshot,
        QueueSnapshot as _QueueSnapshot
    )
    from backend.min_heap import MinHeap as _MinHeap
    from backend.sorted_set import SortedSet as _SortedSet
    from backend.unrestricted_game_manager import UnrestrictedGameManager as _UnrestrictedGameManager
    from backend.time_sensitive_game_manager import TimeSensitiveGameManager as _TimeSensitiveGameManager
    from common.colours import Colours as _Colours
    from common.actions import (
        QueueActions as _QueueActions,
        HeapActions as _HeapActions
    )

# Primitive types
type Number = int | float

# Class type aliases
type Player = _Player
type CandidateGame = _CandidateGame
type CreatedMatch = _CandidateGame
type MinHeap = _MinHeap
type SortedSet = _SortedSet
type GameManager = _UnrestrictedGameManager | _TimeSensitiveGameManager
type Step = _Step
type HeapSnapshot = _HeapSnapshot
type QueueSnapshot = _QueueSnapshot
type CreatedMatchesSnapshot = _BaseSnapshot

# Recorder types
type RecordedWindow = set[int]
type RecordedPlayer = int
type RecordedTeam = set[int]
type RecordedGame = int
type RecordedState = list[dict[str, Number]]
type RecordedSnapshot = dict[str, RecordedState | RecordedWindow | RecordedPlayer | RecordedTeam | RecordedGame | str]
type RecordedStep = dict[str, RecordedSnapshot]
type RecordedStatistic = list[Number]
type RecordedParameters = dict[str, Number]

# Backend types
type GameTeam = set[Player]
type GamePlayers = set[Player]
type AffectedPlayers = set[Player]
type LambdaFunction = Callable[[Number], bool]
type BestCandidateResult = tuple[CandidateGame, float, int]
type PartitionFunction = Callable[[Player, GamePlayers], BestCandidateResult]

# Project-wide types
type AsynchronousFunction = Callable

# Frontend types
type LegendItem = tuple[str, _Colours, _Colours]
type NodeColours = tuple[_Colours, _Colours]
type InsertionInputField = tuple[str, int, int, int]
type StepLabelAction = _QueueActions | _HeapActions
type StepLabelValue = tuple[str, str]
type ButtonType = Literal['primary', 'secondary', 'tertiary']


class SessionState(TypedDict):
    game_manager: Optional[GameManager]
    initialised: bool
    current_step: int
    is_playing: bool
    is_time_sensitive: bool
    insertion_mode: int
    params: RecordedParameters
    stopped: bool
