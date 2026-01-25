import streamlit as st

from common.types import GameManager
from frontend.components import line_chart


def render(game_manager: GameManager, is_time_sensitive: bool) -> None:
    """
    Render the statistics panel showing various metrics over time.
    :param game_manager: The game manager instance containing recorded statistics.
    :param is_time_sensitive: Whether to include time-sensitive statistics.
    """
    st.subheader("Statistics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Queue Size Over Time**")
        line_chart.render(game_manager.recorder.queue_size, "Step", "Queue Size", "Players")
        if is_time_sensitive:
            st.markdown("**Max Player Wait Time**")
            line_chart.render(game_manager.recorder.max_wait_time, "Step", "Max Wait Time", "Wait Time")

    with col2:
        st.markdown("**Heap Size Over Time**")
        line_chart.render(game_manager.recorder.heap_size, "Step", "Heap Size", "Candidate Games")
        if is_time_sensitive:
            st.markdown("**Priority vs Imbalance**")
            line_chart.render(game_manager.recorder.min_priority, "Step", "Priority vs Imbalance", "Priority",
                              game_manager.recorder.min_imbalance, "Imbalance")

    st.divider()
