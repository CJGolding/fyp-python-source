from typing import Optional

from backend.snapshots import QueueSnapshot, HeapSnapshot, BaseSnapshot
from common.actions import QueueActions, HeapActions
from common.types import (RecordedStep, RecordedWindow, Player, RecordedTeam, RecordedGame, MinHeap, CreatedMatch,
                          SortedSet)


class Step:
    def __init__(self, created_matches: list[CreatedMatch], queue_state: SortedSet = None, heap_state: MinHeap = None,
                 queue_snapshot: Optional[QueueSnapshot] = None, heap_snapshot: Optional[HeapSnapshot] = None,
                 window: Optional[RecordedWindow] = None, target_player: Optional[Player] = None,
                 team_x: Optional[RecordedTeam] = None, team_y: Optional[RecordedTeam] = None,
                 queue_action: QueueActions = QueueActions.IDLE, target_game: Optional[RecordedGame] = None,
                 heap_action: HeapActions = HeapActions.IDLE) -> None:
        """
        Represents a single step in the matchmaking process, capturing snapshots of the queue, heap, and created matches.
        :param queue_state: Current state of the matchmaking queue as a SortedSet of Players.
        :param heap_state: Current state of the candidate game heap as a MinHeap of CandidateGames.
        :param created_matches: List of matches created up to this step.
        :param queue_snapshot: Optional pre-existing QueueSnapshot to use.
        :param heap_snapshot: Optional pre-existing HeapSnapshot to use.
        :param window: Optional skill window used in the queue snapshot as a range of indices.
        :param target_player: Optional target player involved in the queue action.
        :param team_x: Optional list of player IDs in team X for the queue snapshot.
        :param team_y: Optional list of player IDs in team Y for the queue snapshot.
        :param queue_action: Action taken on the queue during this step.
        :param target_game: Optional target game index involved in the heap action.
        :param heap_action: Action taken on the heap during this step.
        """
        self.queue_snapshot: QueueSnapshot = queue_snapshot or QueueSnapshot(
            state=[player.to_dict() for player in queue_state],
            window=window,
            target_player=target_player,
            team_x=team_x,
            team_y=team_y,
            action=queue_action
        )
        self.heap_snapshot: HeapSnapshot = heap_snapshot or HeapSnapshot(
            state=[game.to_dict() for game in heap_state],
            target_game=target_game,
            action=heap_action
        )
        self.created_matches: BaseSnapshot = BaseSnapshot(
            state=[match.to_dict() for match in created_matches]
        )

    def to_dict(self) -> RecordedStep:
        """Convert the Step instance to a dictionary for object immutability."""
        return {
            "queue_snapshot": self.queue_snapshot.to_dict(),
            "heap_snapshot": self.heap_snapshot.to_dict(),
            "created_matches": self.created_matches.to_dict()
        }
