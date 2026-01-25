from typing import Optional

import altair as alt
import streamlit as st
from pandas import DataFrame, concat

from common.types import RecordedStatistic


def render(
        data: RecordedStatistic,
        x_label: str,
        y_label: str,
        primary_label: str,
        secondary_data: Optional[RecordedStatistic] = None,
        secondary_label: Optional[str] = None,
) -> None:
    """
    Render a line chart of a given recorded statistic or info message if no data.

    :param data: Primary recorded statistic data points.
    :param x_label: Label for the x-axis.
    :param y_label: Label for the shared y-axis.
    :param primary_label: Legend label for the primary series.
    :param secondary_data: Optional secondary data for comparison.
    :param secondary_label: Legend label for the secondary series.
    """

    if not data:
        st.info("No data recorded yet")
        return

    df = DataFrame(
        {
            "Step": range(len(data)),
            "Value": data,
            "Series": primary_label,
        }
    )

    if secondary_data:
        secondary_df = DataFrame(
            {
                "Step": range(len(secondary_data)),
                "Value": secondary_data,
                "Series": secondary_label or "Secondary",
            }
        )
        df = concat([df, secondary_df], ignore_index=True)

    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("Step:Q", title=x_label),
            y=alt.Y("Value:Q", title=y_label),
            color=alt.Color(
                "Series:N",
                legend=alt.Legend(title=""),
            ),
        )
        .properties(height=300)
        .configure_view(strokeWidth=0)
    )

    st.altair_chart(chart, width="stretch")
