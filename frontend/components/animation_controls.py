import streamlit as st

from frontend.components._helpers import render_button
from frontend.state import StateKeys, set_state


def render(current_index: int, max_index: int, is_playing: bool, is_executing_async: bool, is_on_final_step: bool,
           has_stopped: bool) -> None:
    """
    Render animation control buttons for playback and manipulation of steps.
    :param current_index: The current step index.
    :param max_index: The maximum step index.
    :param is_playing: Whether the animation is currently playing.
    :param is_executing_async: Whether the system is currently executing asynchronously.
    :param is_on_final_step: Whether the current step is the final step.
    :param has_stopped: Whether the animation has been stopped.
    """
    st.header("Animation Controls")

    play_label: str = "Pause" if is_playing else "Play"
    if render_button(play_label, is_on_final_step or has_stopped):
        set_state(StateKeys.IS_PLAYING, not is_playing)
        st.rerun()

    c1, c2 = st.columns(2)
    with c1:
        if render_button("Step Backward", current_index <= 0 or has_stopped):
            set_state(StateKeys.IS_PLAYING, False)
            set_state(StateKeys.CURRENT_STEP, current_index - 1)
            st.rerun()
        if render_button("Skip Backward", current_index <= 0 or has_stopped):
            set_state(StateKeys.IS_PLAYING, False)
            set_state(StateKeys.CURRENT_STEP, 0)
            st.rerun()

    with c2:
        if render_button("Step Forward", is_on_final_step or has_stopped):
            set_state(StateKeys.IS_PLAYING, False)
            set_state(StateKeys.CURRENT_STEP, current_index + 1)
            st.rerun()
        if render_button("Skip Forward", is_on_final_step or is_executing_async or has_stopped):
            set_state(StateKeys.IS_PLAYING, False)
            set_state(StateKeys.CURRENT_STEP, max_index)
            st.rerun()

    st.divider()
