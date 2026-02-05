import streamlit as st
from graphviz import Digraph

from common import Colours
from common.types import LegendItem, ButtonType


def render_button(label: str, controls_disabled: bool = False, button_type: ButtonType = "secondary") -> bool:
    """
    Render a button with consistent styling and disabled state based on varying conditions.
    :param label: The label for the button.
    :param controls_disabled: Whether the button should be disabled.
    :param button_type: The type of the button (e.g. 'primary', 'secondary').
    :return: True if the button was clicked, False otherwise.
    """
    return st.button(label, disabled=controls_disabled, width='stretch', type=button_type)


def render_empty_graph(name: str, shape: str) -> None:
    """
    Create a graph with a single 'Empty' node.
    :param name: The name of the graph.
    :param shape: The shape of the node (e.g. 'box', 'circle').
    """
    graph: Digraph = Digraph(comment=name)
    graph.attr(rankdir='TB', bgcolor='white', nodesep='0.08', ranksep='0.25')
    graph.node('empty', 'Empty', shape=shape, style='filled,rounded', fillcolor='#f5f5f5',
               fontcolor='#999999', fontname='Arial', fontsize='9', fixedsize='true', width='0.7', height='0.5')
    st.graphviz_chart(graph)


def render_horizontal_rank(graph: Digraph, row_nodes: list[str]) -> None:
    """
    Render a horizontal rank of nodes in the graph.
    :param graph: The graph to render the rank in.
    :param row_nodes: The list of node IDs to include in the rank.
    """
    with graph.subgraph() as s:
        s.attr(rank='same')
        for j, node in enumerate(row_nodes):
            s.node(node)
            if j > 0:
                s.edge(row_nodes[j - 1], node, style='invis')


def render_player_node(graph: Digraph, node_id: str, player: dict, fill_colour: Colours,
                       font_colour: Colours, is_time_sensitive: bool) -> None:
    """
    Render a single player node.
    :param graph: The graph to render the node in.
    :param node_id: The ID of the node.
    :param player: The player data dictionary.
    :param fill_colour: The fill colour for the node.
    :param font_colour: The font colour for the node.
    :param is_time_sensitive: Whether to include time-sensitive information in the label.
    """
    label: str = f"P{player['id']}\ns={player['skill']}"
    if is_time_sensitive:
        label += f"\nt={player.get('enqueue_time', 0):.2f}"

    graph.node(node_id, label, fillcolor=fill_colour, fontcolor=font_colour)


def render_legend(items: list[LegendItem]) -> None:
    """
    Render a colour legend from a list of (label, background_colour, foreground_colour) tuples.
    :param items: List of tuples containing (label, background_colour, foreground_colour).
    """
    html: str = " ".join([
        f'<span style="background-color:{background};color:{foreground};'
        f'padding:2px 8px;border-radius:4px;font-size:11px;margin-right:4px;">{label}</span>'
        for label, background, foreground in items
    ])
    st.markdown(html, unsafe_allow_html=True)
