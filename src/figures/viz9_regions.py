"""Q2.2 — Geopolitical waves of talent influx by region."""

import pandas as pd
import plotly.graph_objects as go

from src.data_loader import load_drivers, load_races, load_results
from src.theme import COLORS, apply_theme

NATIONALITY_TO_REGION = {
    "British": "Western Europe",
    "Italian": "Western Europe",
    "French": "Western Europe",
    "German": "Western Europe",
    "Belgian": "Western Europe",
    "Dutch": "Western Europe",
    "Spanish": "Western Europe",
    "Swiss": "Western Europe",
    "Austrian": "Western Europe",
    "Swedish": "Western Europe",
    "Finnish": "Western Europe",
    "Danish": "Western Europe",
    "Irish": "Western Europe",
    "Portuguese": "Western Europe",
    "Monegasque": "Western Europe",
    "Liechtensteiner": "Western Europe",
    "American": "North America",
    "American-Italian": "North America",
    "Canadian": "North America",
    "Brazilian": "Latin America",
    "Argentine": "Latin America",
    "Argentinian": "Latin America",
    "Argentine-Italian": "Latin America",
    "Mexican": "Latin America",
    "Venezuelan": "Latin America",
    "Colombian": "Latin America",
    "Chilean": "Latin America",
    "Uruguayan": "Latin America",
    "Australian": "Asia-Pacific",
    "New Zealander": "Asia-Pacific",
    "Japanese": "Asia-Pacific",
    "Thai": "Asia-Pacific",
    "Malaysian": "Asia-Pacific",
    "Indonesian": "Asia-Pacific",
    "Indian": "Asia-Pacific",
    "Chinese": "Asia-Pacific",
    "Russian": "Eastern Europe",
    "Polish": "Eastern Europe",
    "Czech": "Eastern Europe",
    "Hungarian": "Eastern Europe",
    "East German": "Eastern Europe",
    "South African": "Africa & Middle East",
    "Rhodesian": "Africa & Middle East",
}

REGION_ORDER = [
    ("Western Europe", "#1F77B4"),
    ("North America", "#9467bd"),
    ("Latin America", "#FF7F0E"),
    ("Asia-Pacific", "#2ca02c"),
    ("Eastern Europe", "#e377c2"),
    ("Africa & Middle East", "#bcbd22"),
    ("Other", "#7f7f7f"),
]

ERAS = [
    ("Pioneer Era", 1950, 1960),
    ("Turbo & Senna Era", 1977, 1994),
    ("Japanese & Global Boom", 1995, 2012),
]


def _preprocess() -> pd.DataFrame:
    races = load_races()[["raceId", "year"]]
    results = load_results()[["raceId", "driverId"]]
    drivers = load_drivers()[["driverId", "nationality"]].copy()
    drivers["nationality"] = (
        drivers["nationality"].astype("string").str.strip().str.title()
    )
    drivers["region"] = (
        drivers["nationality"].map(NATIONALITY_TO_REGION).fillna("Other")
    )

    entries = results.merge(races, on="raceId").merge(
        drivers[["driverId", "region"]], on="driverId"
    )
    counts = (
        entries.groupby(["year", "region"])["driverId"]
        .nunique()
        .reset_index(name="drivers")
    )
    regions = [name for name, _ in REGION_ORDER]
    return (
        counts.pivot(index="year", columns="region", values="drivers")
        .reindex(columns=regions)
        .fillna(0)
        .astype(int)
        .sort_index()
    )


def build_figure() -> go.Figure:
    data = _preprocess()
    years = data.index.tolist()
    fig = go.Figure()

    for region, color in REGION_ORDER:
        fig.add_trace(
            go.Scatter(
                x=years,
                y=data[region],
                name=region,
                mode="lines",
                stackgroup="grid",
                line=dict(width=0.5, color=color),
                fillcolor=color,
                hovertemplate=f"<b>{region}</b><br>Year: %{{x}}<br>Drivers: %{{y}}<extra></extra>",
            )
        )

    y_top = data.sum(axis=1).max()
    for label, start, end in ERAS:
        fig.add_vrect(
            x0=start,
            x1=end,
            line_width=0,
            fillcolor=COLORS["text_dark"],
            opacity=0.04,
            layer="below",
        )
        fig.add_annotation(
            x=(start + end) / 2,
            y=y_top * 1.04,
            text=f"<i>{label}</i>",
            showarrow=False,
            font=dict(size=10, color="#666666"),
            yanchor="bottom",
        )

    apply_theme(
        fig,
        title="Geopolitical Waves of Talent Influx",
        height=520,
        hovermode="x unified",
        xaxis=dict(title="Season", range=[min(years), max(years)]),
        yaxis=dict(title="Number of Drivers on Grid", rangemode="tozero"),
        legend=dict(
            title="Region",
            traceorder="reversed",
            yanchor="top",
            y=1.0,
            xanchor="left",
            x=1.01,
        ),
        margin=dict(t=90, r=120, b=50, l=70),
    )
    return fig
