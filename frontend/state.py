from enum import StrEnum
from typing import Any

import streamlit as st

from common.types import SessionState


class StateKeys(StrEnum):
    """Constants for session state keys to avoid magic strings."""
    GAME_MANAGER = "game_manager"
    INITIALISED = "initialised"
    CURRENT_STEP = "current_step"
    IS_PLAYING = "is_playing"
    IS_TIME_SENSITIVE = "is_time_sensitive"
    INSERTION_MODE = "insertion_mode"
    PARAMS = "params"
    STOPPED = "stopped"
    CURRENT_THREAD = "current_thread"


_DEFAULT_STATE: SessionState = {
    "game_manager": None,
    "initialised": False,
    "current_step": 0,
    "is_playing": False,
    "is_time_sensitive": False,
    "insertion_mode": 0,
    "params": {},
    "stopped": False
}


def get_state(key: str) -> Any:
    """
    Get a player from session state with validation.
    :param key: The key to retrieve from session state.
    :return: The player associated with the key.
    """
    if key not in _DEFAULT_STATE:
        raise KeyError(f"Unknown state key: {key}")
    return st.session_state.get(key)


def set_state(key: str, value: Any) -> None:
    """
    Set a player in session state with validation.
    :param key: The key to set in session state.
    :param value: The player to set for the key.
    """
    if key not in _DEFAULT_STATE:
        raise KeyError(f"Unknown state key: {key}")
    st.session_state[key] = value


def init_session_state() -> None:
    """Initialise all session states with defaults."""
    for key, default in _DEFAULT_STATE.items():
        st.session_state.setdefault(key, default)


def reset_animation() -> None:
    """Reset animation state."""
    set_state(StateKeys.CURRENT_STEP, 0)
    set_state(StateKeys.IS_PLAYING, False)
    set_state(StateKeys.STOPPED, False)


def stop_execution() -> None:
    """Stop playback and signal game manager to stop, including async operations."""
    set_state(StateKeys.IS_PLAYING, False)
    set_state(StateKeys.STOPPED, True)


def reset_all() -> None:
    """Full reset to initial state."""
    set_state(StateKeys.GAME_MANAGER, None)
    set_state(StateKeys.INITIALISED, False)
    reset_animation()


def start_playback() -> None:
    """Start animation playback."""
    set_state(StateKeys.CURRENT_STEP, 0)
    set_state(StateKeys.IS_PLAYING, True)
    set_state(StateKeys.STOPPED, False)
