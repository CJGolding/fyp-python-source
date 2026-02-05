import streamlit as st

from common.types import RecordedParameters

_PARAM_LABELS: dict[str, str] = {
    "mode": "Mode",
    "team_size": "GameTeam Size (k)",
    "p_norm": "Fairness Norm (p)",
    "q_norm": "Uniformity Norm (q)",
    "fairness_weight": "Fairness Weight (α)",
    "queue_weight": "Queue Weight (β)",
    "skill_window": "Skill Window Size"
}


def render(params: RecordedParameters) -> None:
    """
    Render parameter key-player pairs for reference.
    :param params: The parameters to render.
    """
    st.subheader("Parameters")
    for key, value in params.items():
        label: str = _PARAM_LABELS.get(key, key)
        col1, col2 = st.columns([3, 2])
        col1.markdown(f"**{label}**")
        col2.text(value)
