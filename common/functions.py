from common.types import GameTeam, GamePlayers


def team_p_skill(team: GameTeam, p_norm: float) -> float:
    """
    Calculate the p-norm skill of a team. For p = ∞, this is the skill of the most skilled player in the team.
    :param team: The team of players (X).
    :param p_norm: The p-norm to use for calculation (p).
    :return: The calculated p-norm skill of the team (s_p(X)).
    """
    if p_norm == float('inf'):
        return float(max(x.skill for x in team))
    return sum(x.skill ** p_norm for x in team) ** (1 / p_norm)


def p_fairness(team_x: GameTeam, team_y: GameTeam, p_norm: float) -> float:
    """
    Calculate the p-fairness between two teams. For p = ∞, this is the absolute difference between the most skilled players in each team.
    :param team_x: The first team of players (X).
    :param team_y: The second team of players (Y).
    :param p_norm: The p-norm used for fairness calculation (p).
    :return: The calculated p-fairness between the two teams (d_p(X, Y)).
    """
    return abs(team_p_skill(team_x, p_norm) - team_p_skill(team_y, p_norm))


def mean_skill(game_players: GameTeam) -> float:
    """
    Calculate the mean skill of players in a game, across both teams.
    :param game_players: The set of players in the game (Z).
    :return: The mean skill of the players (μ_Z).
    """
    return sum(player.skill for player in game_players) / len(game_players)


def q_uniformity(game_players: GamePlayers, q_norm: float) -> float:
    """
    Calculate the q-uniformity of players in a game, across both teams. For q = ∞, this is the farthest player from the mean.
    :param game_players: The set of players in the game (Z).
    :param q_norm: The q-norm used for uniformity calculation (q).
    :return: The calculated q-uniformity of the players (v_q(Z)).
    """
    if q_norm == float('inf'):
        return float(max(abs(player.skill - mean_skill(game_players)) for player in game_players))
    return ((1 / (len(game_players))) * sum(
        abs(z.skill - mean_skill(game_players)) ** q_norm for z in game_players)) ** (1 / q_norm)


def imbalance(team_x: GameTeam, team_y: GameTeam, p_norm: float, q_norm: float, fairness_weight: float) -> float:
    """
    The core imbalance function from the paper, combining the fairness weight, p-fairness, and q-uniformity. components.
    :param team_x: The first team of players (X).
    :param team_y: The second team of players (Y).
    :param p_norm: The p-norm used for fairness calculation (q).
    :param q_norm: The q-norm used for uniformity calculation (p).
    :param fairness_weight: Weighting factor for fairness in imbalance calculation (α).
    :return: The calculated imbalance score (f(X, Y)).
    """
    return fairness_weight * p_fairness(team_x, team_y, p_norm) + q_uniformity(team_x | team_y, q_norm)


def priority(team_x: GameTeam, team_y: GameTeam, queue_weight: float, imbalance: float) -> float:
    """
    The priority function from the paper, combining the imbalance score with a queue weight and maximum wait time across both teams.
    :param team_x: The first team of players (X).
    :param team_y: The second team of players (Y).
    :param queue_weight: Weighting factor for queue time in priority calculation (β).
    :param imbalance: The imbalance score (f(X, Y)).
    :return: The calculated priority score (g(X, Y)).
    """
    return imbalance + (queue_weight * min(player.enqueue_time for player in team_x | team_y))
