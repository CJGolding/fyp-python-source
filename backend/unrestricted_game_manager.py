import logging
import math
import random
import time
from itertools import combinations, count
from threading import Thread
from typing import Optional

from backend._clock import reset as reset_clock
from backend.candidate_game import CandidateGame
from backend.min_heap import MinHeap
from backend.player import Player
from backend.recorder import Recorder
from backend.sorted_set import SortedSet
from common.actions import QueueActions, HeapActions
from common.functions import p_fairness
from common.types import (Number, RecordedParameters, LambdaFunction, AsynchronousFunction, CreatedMatch,
                          AffectedPlayers, GamePlayers, PartitionFunction, BestCandidateResult)

LOG: logging.Logger = logging.getLogger(__name__)

_EXECUTION_TIMEOUT_SECONDS: int = 5


class UnrestrictedGameManager:
    def __init__(self, team_size: int = 2, p_norm: float = 1.0, q_norm: float = 1.0, fairness_weight: float = 0.1,
                 is_recording: bool = False, approximate=False) -> None:
        """
        The UnrestrictedGameManager class manages a matchmaking process for creating balanced games.
        It supports inserting players, creating matches, and recording the matchmaking process.
        :param team_size: Number of players per team (k), between 1 and 5.
        :param p_norm: The p-norm used for fairness calculation (p), greater than or equal to 1.
        :param q_norm: The q-norm used for uniformity calculation (q), greater than or equal to 1.
        :param fairness_weight: Weighting factor for fairness in imbalance calculation (α), greater than 0.
        :param is_recording: Flag to enable or disable recording of the matchmaking process.
        :param approximate: Flag to enable or disable greedy approximation in matchmaking.
        """
        reset_clock()
        self.team_size: int = self.validate_config(team_size, lambda x: 1 <= x <= 5, "team_size", "between 1 and 5")
        self.p_norm: float = self.validate_config(p_norm, lambda x: x >= 1, "p_norm", "greater than or equal to 1.0")
        self.q_norm: float = self.validate_config(q_norm, lambda x: x >= 1, "q_norm", "greater than or equal to 1.0")
        self.fairness_weight: float = self.validate_config(fairness_weight, lambda x: x > 0, "fairness_weight",
                                                           "greater than 0.0")
        self.skill_window: int = math.ceil(4 * (1 + fairness_weight) * team_size ** (1 + (1 / q_norm)))
        self.required_players: int = (2 * self.team_size) - 1
        self.players: SortedSet = SortedSet()
        self.candidate_games: MinHeap = MinHeap()
        self.created_matches: list[CreatedMatch] = []
        self._current_player_id: count[int] = count()
        self._match_quality_metric: str = "imbalance"
        self._partition_solver: PartitionFunction = self._greedy_balanced_partition if approximate else self._brute_force_partition
        self.recorder: Optional[Recorder] = Recorder() if is_recording else None
        self._current_thread: Optional[Thread] = None
        self._record()
        LOG.info(f"Created {self.__class__.__name__}: {self}")

    def __repr__(self) -> str:
        return f"Team Size: {self.team_size}, P: {self.p_norm}, Q: {self.q_norm}, α: {self.fairness_weight}, Window: {self.skill_window}"

    def get_parameters(self) -> RecordedParameters:
        """Get the configuration parameters of the UnrestrictedGameManager for frontend state management."""
        return {
            "team_size": self.team_size,
            "p_norm": self.p_norm,
            "q_norm": self.q_norm,
            "fairness_weight": self.fairness_weight,
            "skill_window": self.skill_window
        }

    @staticmethod
    def validate_config(value: Number, criteria: LambdaFunction, name: str, requirements: str) -> Number:
        """Validate configuration parameters based on provided criteria as a lambda function."""
        if not criteria(value):
            raise ValueError(f"Invalid player for {name}: {value}. Must be {requirements}.")
        return value

    def _record(self, **kwargs) -> None:
        """Record the current state of the matchmaking process if recording is enabled."""
        if self.recorder:
            self.recorder.record_step(**kwargs,
                                      queue_state=self.players,
                                      heap_state=self.candidate_games,
                                      created_matches=self.created_matches
                                      )

    def _create_candidate_game(self, player: Player, team_x: set[Player], team_y: set[Player]) -> CandidateGame:
        """
        Create a CandidateGame instance given two teams and an anchor player.
        :param player: The anchor player for the candidate game (p_i).
        :param team_x: Set of players in team X (X_i).
        :param team_y: Set of players in team Y (Y_i).
        :return: A CandidateGame instance representing the candidate game (X_i, Y_i).
        """
        return CandidateGame(player, team_x, team_y, self.p_norm, self.q_norm, self.fairness_weight)

    def _calculate_best_game_including_player(self, player: Player) -> Optional[
        CandidateGame]:
        """
        Calculate the best candidate game that includes the specified player.
        It involves generating all possible combinations of players within a skill window and evaluating them.
        This guarantees that the game with the lowest imbalance (or priority) is found.
        Time Complexity: k^O(k) where k is the team size.
        :param player: The Player instance to include in the candidate game (p_i).
        :return: The best CandidateGame instance including the player (X_i, Y_i), or None if no valid game exists.
        """
        if player not in self.players:
            return None

        player_index: int = self.players.index(player)
        window_start_index: int = player_index + 1
        window_end_index: int = min(len(self.players), window_start_index + self.skill_window)
        visible_players: SortedSet = self.players[window_start_index: window_end_index]
        self._record(target_player=player_index, queue_action=QueueActions.ANCHOR,
                     window=set(range(window_start_index, window_end_index)))

        if len(visible_players) < self.required_players:
            return None

        best_game: Optional[CandidateGame] = None
        min_game_val: float = float('inf')
        total_num_enumerations: int = 0
        start = time.perf_counter()

        for remaining_players in combinations(visible_players, self.required_players):
            elapsed = time.perf_counter() - start
            if elapsed > _EXECUTION_TIMEOUT_SECONDS:
                LOG.warning(
                    f"Timeout reached, prematurely ending search for best game for Player {player.id}.")
                break
            if min_game_val == 0:
                LOG.info(f"Perfect game found for Player {player.id} with imbalance 0, breaking early.")
                break
            game, curr_game_val, num_enumerations = self._partition_solver(player, set(remaining_players))
            total_num_enumerations += num_enumerations
            if curr_game_val < min_game_val:
                min_game_val = curr_game_val
                best_game = game

        LOG.info(f"Checked {total_num_enumerations} candidate games for Player {player.id}.")

        return best_game

    def _brute_force_partition(self, anchor_player: Player, remaining_players: GamePlayers) -> BestCandidateResult:
        """
        Find the best candidate game including the anchor player using brute-force enumeration of all team combinations.
        Time Complexity: 2^O(k) where k is the team size.
        :param anchor_player: The anchor Player instance to include in the candidate game (p_i).
        :param remaining_players: Set of remaining Player instances to partition into teams.
        :return: A tuple containing the CandidateGame instance (X_i, Y_i), its imbalance (f) or priority (g) player, and the number of enumerations.
        """
        best_game: Optional[CandidateGame] = None
        min_game_val: float = float('inf')
        num_enumerated: int = 0

        for team_x_others in combinations(remaining_players, self.team_size - 1):
            num_enumerated += 1
            team_x_players: set[Player] = set(team_x_others) | {anchor_player}
            team_y_players: set[Player] = remaining_players - team_x_players
            game: CandidateGame = self._create_candidate_game(anchor_player, team_x_players, team_y_players)
            curr_game_val: float = getattr(game, self._match_quality_metric)
            if curr_game_val < min_game_val:
                min_game_val = curr_game_val
                best_game = game
            if min_game_val == 0:
                break
        return best_game, min_game_val, num_enumerated

    def _greedy_balanced_partition(self, anchor_player: Player, remaining_players: GamePlayers) -> BestCandidateResult:
        """
        Approximate the best candidate game including the anchor player using a greedy balanced partitioning algorithm.
        Time Complexity: O(k log k) where k is the team size.
        :param anchor_player: The anchor Player instance to include in the candidate game (p_i).
        :param remaining_players: Set of remaining Player instances to partition into teams.
        :return: A tuple containing the CandidateGame instance (X_i, Y_i), its imbalance (f) or priority (g) player, and the number of enumerations (1).
        """
        game_players: SortedSet = SortedSet({anchor_player} | remaining_players)
        sorted_game_players: list[Player] = sorted(game_players, reverse=True)
        team_x: GamePlayers = set()
        team_y: GamePlayers = set()

        for player in sorted_game_players:
            if len(team_x) < self.team_size and len(team_y) < self.team_size:
                if p_fairness(team_x | {player}, team_y, self.p_norm) <= p_fairness(team_x, team_y | {player},
                                                                                    self.p_norm):
                    team_x.add(player)
                else:
                    team_y.add(player)
            elif len(team_x) < self.team_size:
                team_x.add(player)
            else:
                team_y.add(player)

        game: CandidateGame = self._create_candidate_game(anchor_player, team_x, team_y)
        return game, getattr(game, self._match_quality_metric), 1

    def _insert_player(self, player: Player, bulk: bool = False) -> AffectedPlayers:
        """
        Insert a new player into the matchmaking queue and update candidate games accordingly.
        Time Complexity: k^O(k) log n where k is the team size and n is the number of players in the queue.
        :param player: The Player instance to insert into the queue (p_i).
        :bulk: Flag indicating if this insertion is part of a bulk operation (to avoid redundant heap updates).
        :return: Set of affected Player instances whose candidate games were updated.
        """
        self.players.add(player)
        player_index: int = self.players.index(player)
        self._record(target_player=player_index, queue_action=QueueActions.INSERT)
        affected_players: AffectedPlayers = set(self.players[max(0, player_index - self.skill_window): player_index])

        if not bulk:
            best_game: Optional[CandidateGame] = self._calculate_best_game_including_player(player)
            if best_game:
                self._record(queue_action=QueueActions.GAME_FOUND,
                             team_x={self.players.index(p) for p in best_game.team_x},
                             team_y={self.players.index(p) for p in best_game.team_y})
                self.candidate_games.push(best_game)
                self._record(preserve_queue=True, target_game=self.candidate_games.index(player.id),
                             heap_action=HeapActions.INSERT)
            else:
                self._record(queue_action=QueueActions.GAME_NOT_FOUND)
            self._update_candidate_games_for_list(affected_players)

        return affected_players

    def _insert_players(self, affected_players: AffectedPlayers) -> None:
        """
        Inserts multiple players into the matchmaking queue, deferring candidate game updates until all insertions are complete.
        :param affected_players: Set of Player instances to insert into the queue.
        """
        for player in affected_players:
            LOG.info(f"Adding player {player.id} to the queue.")
            affected_players = affected_players | self._insert_player(player, True)
            LOG.info(f"Total affected players after inserting player {player.id}: {len(affected_players)}")
        self._update_candidate_games_for_list(affected_players)

    def _remove_player(self, player: Player, bulk: bool = False) -> AffectedPlayers:
        """
        Removes a player from the matchmaking queue and update candidate games accordingly.
        Time Complexity: k^O(k) log n where k is the team size and n is the number of players in the queue.
        :param player: The Player instance to remove from the queue (p_i).
        :bulk: Flag indicating if this removal is part of a bulk operation (to avoid redundant heap updates).
        :return: Set of affected Player instances whose candidate games were updated.
        """
        player_index: int = self.players.index(player)
        affected_players = set(self.players[max(0, player_index - self.skill_window): player_index])
        self._record(target_player=player_index, queue_action=QueueActions.REMOVE)
        self.players.remove(player)

        if not bulk:
            if player.id in self.candidate_games:
                self._record(target_game=self.candidate_games.index(player.id), heap_action=HeapActions.REMOVE)
                self.candidate_games.remove(player.id)
            else:
                self._record()
            self._update_candidate_games_for_list(affected_players)
        return affected_players

    def _remove_players(self, affected_players: AffectedPlayers) -> None:
        """
        Removes multiple players from the matchmaking queue, deferring candidate game updates until all removals are complete.
        :param affected_players: Set of Player instances to remove from the queue.
        """
        for player in affected_players:
            LOG.info(f"Removing player {player.id} from the queue.")
            affected_players = affected_players | self._remove_player(player, True)
            LOG.info(f"Total affected players after removing player {player.id}: {len(affected_players)}")
        self._update_candidate_games_for_list(affected_players)

    def _update_candidate_games_for_list(self, affected_players: AffectedPlayers) -> None:
        """
        Internal method to update candidate games for a list of affected players after an insertion or removal.
        :param affected_players: SortedSet of Player instances whose candidate games need to be updated.
        """
        for player in SortedSet(affected_players):
            best_game: Optional[CandidateGame] = self._calculate_best_game_including_player(player)
            if best_game:
                self._record(queue_action=QueueActions.GAME_FOUND,
                             team_x=[self.players.index(p) for p in best_game.team_x],
                             team_y=[self.players.index(p) for p in best_game.team_y]
                             )
                self.candidate_games.push(best_game)
                self._record(target_game=self.candidate_games.index(player.id), heap_action=HeapActions.INSERT)
            else:
                if player.id in self.candidate_games:
                    self._record(queue_action=QueueActions.GAME_NOT_FOUND,
                                 target_game=self.candidate_games.index(player.id),
                                 heap_action=HeapActions.REMOVE
                                 )
                    self.candidate_games.remove(player.id)

    def _query_best_game(self) -> Optional[CandidateGame]:
        """
        Query the best candidate game from the heap.
        :return: The best CandidateGame instance (X, Y) or None if the heap is empty.
        """
        return self.candidate_games.peek()

    def create_match(self) -> None:
        """
        Create a match from the best candidate game and remove involved players from the queue.
        The game is implicitly removed from the candidate games heap as players are removed and their games are updated.
        """
        self._record(clear=True)
        game: CandidateGame = self._query_best_game()
        if game is None:
            self._record(queue_action=QueueActions.GAME_NOT_FOUND)
            LOG.warning("No valid candidate games available to create a match.")
            self._record()
            return

        self._record(target_game=0, heap_action=HeapActions.CREATE)
        self.created_matches.append(game)
        LOG.info(f"Created Match: {game}")

        players_in_game: GamePlayers = game.team_x | game.team_y
        self._remove_players(players_in_game)
        self._record()
        LOG.info(f"Heap Size after match creation: {len(self.candidate_games)}")

    def insert_player_manually(self, player_skill: int) -> None:
        """
        Insert a single player with the specified skill level into the matchmaking queue.
        :param player_skill: Skill level of the player to insert (non-negative integer).
        """
        self._record(clear=True)
        player: Player = Player(next(self._current_player_id), player_skill)
        self._insert_player(player)

    def insert_players_automatically(self, num_players: int = 10, mean: int = 1500, std_dev: int = 200) -> None:
        """
        Insert multiple players with skill levels generated from a Normal distribution into the matchmaking queue.
        :param num_players: Number of players to insert (positive integer).
        :param mean: Mean skill level for the Normal distribution.
        :param std_dev: Standard deviation for the Normal distribution.
        """
        self._record(clear=True)
        players: AffectedPlayers = {Player(next(self._current_player_id), abs(int(round(random.gauss(mean, std_dev)))))
                                    for _
                                    in range(num_players)}
        self._insert_players(players)

    @property
    def is_executing_async(self) -> bool:
        """Check if an async operation is currently in progress."""
        return self._current_thread is not None and self._current_thread.is_alive()

    def _run_async(self, target: AsynchronousFunction, *args) -> Thread:
        """
        Run a target function asynchronously. Returns the thread for monitoring.
        :param target: The target function to run asynchronously.
        :param args: Arguments to pass to the target function.
        :return: The Thread instance running the target function.
        """
        thread: Thread = Thread(
            target=target,
            args=args,
            daemon=True
        )
        self._current_thread = thread
        thread.start()
        return thread

    def insert_player_manually_async(self, player_skill: int = 1500) -> Thread:
        """
        Asynchronously insert a single player with the specified skill level into the matchmaking queue.
        :param player_skill: Skill level of the player to insert (non-negative integer).
        :return: The Thread instance running the insertion operation.
        """
        return self._run_async(self.insert_player_manually, player_skill)

    def insert_players_automatically_async(self, num_players: int = 10, mean: int = 1500, std_dev: int = 200) -> Thread:
        """
        Asynchronously insert multiple players with skill levels generated from a Normal distribution.
        :param num_players: Number of players to insert (positive integer).
        :param mean: Mean skill level for the Normal distribution.
        :param std_dev: Standard deviation for the Normal distribution.
        :return: The Thread instance running the bulk insertion operation.
        """
        return self._run_async(self.insert_players_automatically, num_players, mean, std_dev)

    def create_match_async(self) -> Thread:
        """
        Asynchronously create a match from the best candidate game.
        :return: The Thread instance running the match creation operation.
        """
        return self._run_async(self.create_match)
