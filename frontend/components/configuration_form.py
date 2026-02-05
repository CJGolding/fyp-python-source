import streamlit as st

from backend import UnrestrictedGameManager, TimeSensitiveGameManager
from common.types import RecordedParameters
from frontend.components._helpers import render_button
from frontend.state import reset_animation, set_state, StateKeys, get_state


def render() -> None:
    """Render the configuration panel for initialising the game manager."""
    st.subheader("Configuration")
    mode: str = st.selectbox("Mode", ["Unrestricted", "Time-Sensitive"])
    is_time_sensitive: bool = mode == "Time-Sensitive"
    col1, col2 = st.columns(2)

    with col1:
        team_size: int = st.number_input("Team Size (k)", 1, 5, 2)
        q_norm: float = st.number_input("Uniformity Norm (q)", 1.0, None, 1.0, 1.0)
        matchmaking_approach: str = st.selectbox("Matchmaking Approach", ["Exact", "Approximate"])
        approximate_matchmaking: bool = matchmaking_approach == "Approximate"
    with col2:
        p_norm: float = st.number_input("Fairness Norm (p)", 1.0, 3.0, 1.0, 1.0)
        fairness_weight: float = st.number_input("Fairness Weight (α)", 0.1, None, 0.1, 0.1)
        if is_time_sensitive:
            queue_weight: float = st.number_input("Queue Weight (β)", 0.1, 1.0, 0.1, 0.1)

    if render_button("Initialise", button_type="primary"):
        set_state(StateKeys.IS_TIME_SENSITIVE, is_time_sensitive)
        if is_time_sensitive:
            set_state(StateKeys.GAME_MANAGER,
                      TimeSensitiveGameManager(team_size, p_norm, q_norm, fairness_weight, queue_weight, True,
                                               approximate_matchmaking))
        else:
            set_state(StateKeys.GAME_MANAGER,
                      UnrestrictedGameManager(team_size, p_norm, q_norm, fairness_weight, True,
                                              approximate_matchmaking))
        params: RecordedParameters = get_state(StateKeys.GAME_MANAGER).get_parameters()
        set_state(StateKeys.PARAMS, params)
        set_state(StateKeys.INITIALISED, True)
        reset_animation()
        st.rerun()
