"""Q2.4 — Average races per driver per team per decade."""

import plotly.express as px
import plotly.graph_objects as go

from src.data_loader import load_constructors, load_races, load_results
from src.theme import apply_theme


def build_figure() -> go.Figure:
    """avg_races_per_driver = total_entries / num_drivers per team-decade."""
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
        hover_data={
            "decade": True,
            "avg_races_per_driver": ":.1f",
            "total_entries": True,
            "num_drivers": True,
        },
        labels={
            "decade": "Decade",
            "avg_races_per_driver": "Average Races per Driver",
            "total_entries": "Total Entries",
            "num_drivers": "Number of Drivers",
        },
    )

    apply_theme(
        fig,
        height=560,
        xaxis_title="Decade",
        yaxis_title="Average Races per Driver",
    )
    return fig
