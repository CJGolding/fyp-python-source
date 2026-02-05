import streamlit as st
from graphviz import Digraph

from common.types import RecordedState, Number, NodeColours, Step
from frontend.components._helpers import Colours, render_player_node, render_horizontal_rank


def _get_team_colour(team_name: str) -> NodeColours:
    """
    Get the fill and font colours for a team based on its name.
    :param team_name: The name of the team ('X' or 'Y').
    :return: A tuple containing the fill colour and font colour.
    """
    return (Colours.TEAM_X, Colours.TEXT_LIGHT) if team_name == 'X' else (Colours.TEAM_Y, Colours.TEXT_DARK)


def _create_team_nodes(index: int, graph: Digraph, team: list[dict[str, Number]], is_time_sensitive: bool,
                       team_name: str) -> None:
    """
    Create all nodes for a team in the graph.
    :param index: The match index.
    :param graph: The graph to add nodes to.
    :param team: The list of player dictionaries in the team.
    :param is_time_sensitive: Whether to include time-sensitive information in the node labels.
    :param team_name: The name of the team ('X' or 'Y').
    """
    fill_colour, font_colour = _get_team_colour(team_name)
    for i, player in enumerate(team):
        node_id: str = f'm{index}_t{team_name}_{i}'
        render_player_node(graph, node_id, player, fill_colour, font_colour, is_time_sensitive)


def _render_match_graph(index: int, match: dict, is_time_sensitive: bool) -> Digraph:
    """
    Render a single match as a graphviz graph with two teams and metric player and anchor_player_id as a divider.
    :param index: The match index.
    :param match: The match data dictionary.
    :param is_time_sensitive: Whether to include time-sensitive information in the node labels.
    :return: The constructed Digraph object.
    """
    team_x: list[dict[str, Number]] = match.get("team_x")
    team_y: list[dict[str, Number]] = match.get("team_y")
    anchor_player_id: int = match.get('anchor_player_id')

    # Determine metric key and player
    metric_key: str = "g" if is_time_sensitive else "f"
    metric_val: float = match.get("priority") or match.get("imbalance", 0)

    graph: Digraph = Digraph(comment=f'Match {index + 1}')
    graph.attr(rankdir='TB', bgcolor='white', nodesep='0.08', ranksep='0.25')
    graph.attr('node', shape='box', style='filled,rounded', fontname='Arial', fontsize='9',
               fixedsize='true', width='0.7', height='0.5', penwidth='1', color='black')

    _create_team_nodes(index, graph, team_x, is_time_sensitive, 'X')

    metric_node_id: str = f'm{index}_metric'
    graph.node(metric_node_id, f'Match P{anchor_player_id}\n{metric_key}={metric_val:.1f}',
               shape='plaintext', fontname='Arial Bold', fontsize='10',
               fontcolor='#000000', fillcolor='#ffffff', fixedsize='false', width='0', height='0.4')

    _create_team_nodes(index, graph, team_y, is_time_sensitive, 'Y')

    all_nodes: list[str] = []
    for i in range(len(team_x)):
        all_nodes.append(f'm{index}_tX_{i}')
    all_nodes.append(metric_node_id)
    for i in range(len(team_y)):
        all_nodes.append(f'm{index}_tY_{i}')

    render_horizontal_rank(graph, all_nodes)

    return graph


def render(step: Step, is_time_sensitive: bool) -> None:
    """
    Render created matches as horizontal visualisations of player nodes.
    :param step: The current Step object containing created matches.
    :param is_time_sensitive: Whether to include time-sensitive information in the node labels.
    """
    matches_state: RecordedState = step.created_matches.state
    st.subheader(f"Created Matches ({len(matches_state)} matches)")

    if matches_state:
        for i, match in enumerate(matches_state):
            graph = _render_match_graph(i, match, is_time_sensitive)
            with st.container(border=True, horizontal_alignment='center'):
                st.graphviz_chart(graph)
    else:
        st.info("No matches created yet")
