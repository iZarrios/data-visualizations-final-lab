"""Q2.4 — Average races per driver per team per decade."""

from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go

from src.data_loader import load_constructors, load_races, load_results
from src.theme import apply_theme


def build_figure() -> go.Figure:
    df = load_results().merge(load_races()[["raceId", "year"]], on="raceId")
    df = df.merge(load_constructors()[["constructorId", "name"]], on="constructorId")
    df["decade"] = (df["year"] // 10) * 10

    agg = (
        df.groupby(["decade", "name"])
        .agg(total_entries=("resultId", "count"), num_drivers=("driverId", "nunique"))
        .reset_index()
    )
    agg["avg_races_per_driver"] = agg["total_entries"] / agg["num_drivers"]

    fig = px.box(
        agg,
        x="decade",
        y="avg_races_per_driver",
        points="all",
        hover_name="name",
        hover_data=["total_entries", "num_drivers"],
        labels={"decade": "Decade", "avg_races_per_driver": "Average Races per Driver"},
    )

    apply_theme(
        fig,
        title="Average Races per Driver per Team per Decade",
        height=560,
        xaxis_title="Decade",
        yaxis_title="Average Races per Driver",
    )
    return fig
