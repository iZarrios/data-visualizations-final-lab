"""Geographic evolution — regional race distribution and spherical center of gravity."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.data_loader import load_circuits, load_races
from src.theme import COLORS, REGION_COLORS, apply_theme

COUNTRY_TO_REGION = {
    "UK": "Europe", "Italy": "Europe", "France": "Europe", "Germany": "Europe",
    "Belgium": "Europe", "Netherlands": "Europe", "Spain": "Europe", "Switzerland": "Europe",
    "Austria": "Europe", "Sweden": "Europe", "Monaco": "Europe", "Portugal": "Europe",
    "Hungary": "Europe", "Turkey": "Europe", "Russia": "Europe",
    "USA": "Americas", "United States": "Americas", "Brazil": "Americas",
    "Argentina": "Americas", "Mexico": "Americas", "Canada": "Americas",
    "Japan": "Asia-Pacific", "China": "Asia-Pacific", "Australia": "Asia-Pacific",
    "Malaysia": "Asia-Pacific", "Singapore": "Asia-Pacific", "Korea": "Asia-Pacific",
    "India": "Asia-Pacific",
    "UAE": "Middle East", "Bahrain": "Middle East", "Qatar": "Middle East",
    "Saudi Arabia": "Middle East", "Azerbaijan": "Middle East",
    "South Africa": "Africa", "Morocco": "Africa",
}


def load_circuit_decade_data() -> pd.DataFrame:
    circuits = load_circuits().rename(columns={"name": "circuit_name"})
    merged = load_races().merge(circuits, on="circuitId", how="inner")
    merged["decade"] = (merged["year"] // 10) * 10
    merged["region"] = merged["country"].map(COUNTRY_TO_REGION).fillna("Other")
    merged = merged.rename(columns={"lat": "latitude", "lng": "longitude"})

    grouped = (
        merged.groupby(
            ["circuitId", "circuit_name", "decade", "latitude", "longitude", "region"],
            as_index=False,
        )
        .size()
        .rename(columns={"size": "races_hosted"})
    )
    return grouped


def calculate_spherical_cog(dataframe: pd.DataFrame) -> pd.DataFrame:
    cog_list = []
    for dec in sorted(dataframe["decade"].unique()):
        df_dec = dataframe[dataframe["decade"] == dec]
        lat_rad = np.radians(df_dec["latitude"])
        lon_rad = np.radians(df_dec["longitude"])
        w = df_dec["races_hosted"]

        x = np.cos(lat_rad) * np.cos(lon_rad) * w
        y = np.cos(lat_rad) * np.sin(lon_rad) * w
        z = np.sin(lat_rad) * w

        x_avg = np.sum(x) / np.sum(w)
        y_avg = np.sum(y) / np.sum(w)
        z_avg = np.sum(z) / np.sum(w)

        hyp = np.sqrt(x_avg**2 + y_avg**2)
        cog_list.append({
            "decade": dec,
            "cog_lat": np.degrees(np.arctan2(z_avg, hyp)),
            "cog_lon": np.degrees(np.arctan2(y_avg, x_avg)),
        })
    return pd.DataFrame(cog_list)


def get_decades() -> list[int]:
    df = load_circuit_decade_data()
    return sorted(df["decade"].unique().tolist())


def build_timeline_figure(selected_decade: int) -> go.Figure:
    df = load_circuit_decade_data()
    filtered = df[df["decade"] <= selected_decade]
    timeline_data = filtered.groupby(["decade", "region"])["races_hosted"].sum().reset_index()

    color_map = {r: REGION_COLORS.get(r, "#7f7f7f") for r in timeline_data["region"].unique()}
    fig = px.bar(
        timeline_data,
        x="decade",
        y="races_hosted",
        color="region",
        labels={"races_hosted": "Total Races Held", "decade": "Decade", "region": "Region"},
        color_discrete_map=color_map,
        barmode="stack",
    )
    apply_theme(
        fig,
        title="Distribution of Races Hosted by Global Region",
        height=480,
        xaxis_title="Decade",
        yaxis_title="Total Races Held",
        legend=dict(title="Region"),
        dragmode=False,
        margin=dict(t=80, b=60, l=70, r=30),
    )
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def build_globe_figure(selected_decade: int) -> go.Figure:
    df = load_circuit_decade_data()
    df_cog = calculate_spherical_cog(df)
    filtered = df[df["decade"] <= selected_decade]
    current_cog = df_cog[df_cog["decade"] <= selected_decade]

    fig = go.Figure()
    fig.add_trace(
        go.Scattergeo(
            lon=filtered["longitude"],
            lat=filtered["latitude"],
            text=filtered["circuit_name"] + " (" + filtered["region"] + ")",
            mode="markers",
            marker=dict(
                size=filtered["races_hosted"] * 1.2 + 4,
                color=COLORS["primary_red"],
                opacity=0.65,
            ),
            name="Circuits",
            hovertemplate="%{text}<br>Races: %{marker.size}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scattergeo(
            lon=current_cog["cog_lon"],
            lat=current_cog["cog_lat"],
            mode="lines+markers",
            line=dict(color=COLORS["primary_blue"], width=3, dash="dash"),
            marker=dict(size=10, color=COLORS["primary_blue"], symbol="diamond"),
            name="Spherical CoG Path",
            text=current_cog["decade"].apply(lambda x: f"{x}s CoG"),
            hovertemplate="%{text}<extra></extra>",
        )
    )

    apply_theme(
        fig,
        title="True Spherical Center of Gravity Path",
        height=480,
        geo=dict(
            projection_type="orthographic",
            projection_scale=2.2,  # Prevent zooming out too far (higher = more zoomed in)
            showland=True,
            landcolor="#EDE8DF",
            showocean=True,
            oceancolor="#E8F4FC",
            showcountries=True,
            countrycolor=COLORS["grid_line"],
            center=dict(lat=30, lon=20),
        ),
        margin=dict(l=0, r=0, t=60, b=0),
        showlegend=True,
        legend=dict(x=0.01, y=0.99),
    )
    return fig
