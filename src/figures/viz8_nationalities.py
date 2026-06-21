"""Q2.1 — Driver vs constructor nationality diversification by decade."""

import pandas as pd
import plotly.graph_objects as go

from src.data_loader import load_constructors, load_drivers, load_races, load_results
from src.theme import COLORS, apply_theme


def _preprocess() -> pd.DataFrame:
    races = load_races()[["raceId", "year"]]
    results = load_results()[["raceId", "driverId", "constructorId"]]
    drivers = load_drivers()[["driverId", "nationality"]].copy()
    constructors = load_constructors()[["constructorId", "nationality"]].copy()

    for frame in (drivers, constructors):
        frame["nationality"] = (
            frame["nationality"].astype("string").str.strip().str.title()
        )

    entries = (
        results.merge(races, on="raceId")
        .merge(drivers.rename(columns={"nationality": "driver_nat"}), on="driverId")
        .merge(
            constructors.rename(columns={"nationality": "constructor_nat"}),
            on="constructorId",
        )
    )
    entries["decade"] = (entries["year"] // 10) * 10

    grouped = (
        entries.groupby("decade")
        .agg(
            driver_nationalities=("driver_nat", "nunique"),
            constructor_nationalities=("constructor_nat", "nunique"),
        )
        .reset_index()
    )
    grouped["decade_label"] = grouped["decade"].astype(str) + "s"
    return grouped.sort_values("decade").reset_index(drop=True)


def build_figure() -> go.Figure:
    data = _preprocess()
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data["decade_label"],
            y=data["constructor_nationalities"],
            name="Constructor Nationalities",
            legendrank=2,
            mode="lines+markers",
            line=dict(color=COLORS["constructor_orange"], width=2),
            marker=dict(size=7, symbol="x"),
            fill="tozeroy",
            fillcolor="rgba(217, 83, 30, 0.15)",
            hovertemplate=(
                "<b>Constructor Nationalities</b><br>"
                "Decade: %{x}<br>Unique nationalities: %{y}<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data["decade_label"],
            y=data["driver_nationalities"],
            name="Driver Nationalities",
            legendrank=1,
            mode="lines+markers",
            line=dict(color=COLORS["driver_cyan"], width=2),
            marker=dict(size=7, symbol="x"),
            fill="tonexty",
            fillcolor="rgba(23, 166, 212, 0.12)",
            hovertemplate=(
                "<b>Driver Nationalities</b><br>"
                "Decade: %{x}<br>Unique nationalities: %{y}<extra></extra>"
            ),
        )
    )

    apply_theme(
        fig,
        title="Structural Global Diversification Over Time",
        height=520,
        hovermode="x unified",
        xaxis=dict(title="Decade", range=[-0.5, len(data) - 0.5]),
        yaxis=dict(title="Unique Nationalities"),
        legend=dict(yanchor="top", y=0.98, xanchor="right", x=0.99),
        margin=dict(t=90, r=40, b=50, l=60),
    )
    return fig
