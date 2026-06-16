"""Q3.1 — Driver vs constructor win dominance per decade."""

from __future__ import annotations

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data_loader import load_constructors, load_drivers, load_races, load_results
from src.theme import SEQUENTIAL_BLUE, SEQUENTIAL_RED, apply_theme


def build_figure() -> go.Figure:
    df = load_results().merge(load_races()[["raceId", "year"]], on="raceId")
    wins = df[df["positionOrder"] == 1].copy()
    wins["decade"] = (wins["year"] // 10) * 10

    driver_wins = wins.merge(load_drivers()[["driverId", "surname"]], on="driverId")
    driver_heat = driver_wins.groupby(["surname", "decade"]).size().reset_index(name="wins")
    driver_pivot = driver_heat.pivot(index="surname", columns="decade", values="wins").fillna(0)
    driver_pivot = driver_pivot.loc[driver_pivot.sum(axis=1).sort_values(ascending=False).index]

    constructor_wins = wins.merge(load_constructors()[["constructorId", "name"]], on="constructorId")
    constructor_heat = constructor_wins.groupby(["name", "decade"]).size().reset_index(name="wins")
    constructor_pivot = constructor_heat.pivot(index="name", columns="decade", values="wins").fillna(0)
    constructor_pivot = constructor_pivot.loc[constructor_pivot.sum(axis=1).sort_values(ascending=False).index]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Driver Dominance per Decade", "Constructor Dominance per Decade"),
        horizontal_spacing=0.22,
    )

    fig.add_trace(
        go.Heatmap(
            z=driver_pivot.values,
            x=driver_pivot.columns,
            y=driver_pivot.index,
            colorscale=SEQUENTIAL_RED,
            colorbar=dict(title="Wins", x=0.42),
            hovertemplate="<b>%{y}</b><br>Decade: %{x}s<br>Wins: %{z}<extra></extra>",
        ),
        row=1, col=1,
    )
    fig.add_trace(
        go.Heatmap(
            z=constructor_pivot.values,
            x=constructor_pivot.columns,
            y=constructor_pivot.index,
            colorscale=SEQUENTIAL_BLUE,
            colorbar=dict(title="Wins", x=1.02),
            hovertemplate="<b>%{y}</b><br>Decade: %{x}s<br>Wins: %{z}<extra></extra>",
        ),
        row=1, col=2,
    )

    fig.update_yaxes(autorange="reversed", row=1, col=1)
    fig.update_yaxes(autorange="reversed", row=1, col=2)

    apply_theme(
        fig,
        height=800,
        dragmode=False,
        margin=dict(l=80, r=100, t=60, b=60),
    )
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True, autorange="reversed")
    return fig
