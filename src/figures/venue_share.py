"""Classic vs modern venue share by decade."""

from __future__ import annotations

import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.data_loader import load_circuits, load_races
from src.theme import COLORS, apply_theme


def build_figure() -> go.Figure:
    df_merged = load_races().merge(load_circuits(), on="circuitId", how="inner")
    classic_cohort_ids = df_merged[df_merged["year"] <= 1960]["circuitId"].unique()

    df_merged = df_merged.copy()
    df_merged["venue_type"] = np.where(
        df_merged["circuitId"].isin(classic_cohort_ids),
        "Classic Tracks (1950-1960)",
        "Modern & New Venues",
    )
    df_merged["decade"] = (df_merged["year"] // 10 * 10).astype(str) + "s"

    decade_share = df_merged.groupby(["decade", "venue_type"]).size().reset_index(name="race_count")

    fig = px.bar(
        decade_share,
        x="decade",
        y="race_count",
        color="venue_type",
        labels={"decade": "Decade", "race_count": "Number of Races", "venue_type": "Circuit Type"},
        color_discrete_map={
            "Classic Tracks (1950-1960)": COLORS["accent_purple"],
            "Modern & New Venues": COLORS["primary_blue"],
        },
        category_orders={
            "decade": ["1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"],
        },
    )

    apply_theme(
        fig,
        title="F1 Calendar Evolution: Classic vs Modern Venue Share by Decade",
        height=600,
        barmode="group",
        xaxis=dict(title="<b>Championship Decade</b>"),
        yaxis=dict(title="<b>Number of Races</b>", zeroline=False),
        legend=dict(
            title=dict(text="<b>Circuit Type</b>"),
            x=0.02, y=0.98,
        ),
        margin=dict(l=100, r=100, t=120, b=80),
    )
    fig.update_traces(marker=dict(line=dict(color=COLORS["text_dark"], width=0.5)))
    return fig
