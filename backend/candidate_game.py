from typing import Optional

from common.functions import imbalance, priority
from common.types import Player, GameTeam


class CandidateGame:
    def __init__(self, anchor_player: Player, team_x: GameTeam, team_y: GameTeam, p_norm: float, q_norm: float,
                 fairness_weight: float, queue_weight: Optional[float] = None) -> None:
        """
        Represents a candidate game with two teams, an anchor player, imbalance score, and optional priority score.
        :param anchor_player: The player anchoring the candidate game (p_i).
        :param team_x: Set of players in team X (X_i).
        :param team_y: Set of players in team Y (Y_i).
        :param p_norm: The p-norm used for fairness calculation (q).
        :param q_norm: The q-norm used for uniformity calculation (p).
        :param fairness_weight: Weighting factor for fairness in imbalance calculation (α).
        :param queue_weight: Optional weighting factor for queue time in priority calculation (β).
        """
        self.anchor_player: Player = anchor_player
        self.team_x: GameTeam = team_x
        self.team_y: GameTeam = team_y
        self.imbalance: float = imbalance(team_x, team_y, p_norm, q_norm, fairness_weight)
        self.priority: Optional[float] = priority(self.team_x, self.team_y, queue_weight,
                                                  self.imbalance) if queue_weight is not None else None

    def to_dict(self) -> dict:
        """Convert CandidateGame to dictionary representation for recording."""
        return {
            "anchor_player_id": self.anchor_player.id,
            "team_x": [player.to_dict() for player in self.team_x],
            "team_y": [player.to_dict() for player in self.team_y],
            "imbalance": self.imbalance,
            "priority": self.priority
        }

    def __lt__(self, other: "CandidateGame") -> bool:
        """Less-than comparison based on priority (g) if available, otherwise imbalance (f)."""
        if self.priority is not None and other.priority is not None:
            return self.priority < other.priority
        return self.imbalance < other.imbalance

    def __str__(self) -> str:
        priority_string: str = f", g: {self.priority})" if self.priority is not None else ""
        return f"CandidateGame(Player ID: {self.anchor_player.id} Team X: {[p.id for p in self.team_x]}, Team Y: {[p.id for p in self.team_y]}, f: {self.imbalance}{priority_string})"
