"""F1 championship volume and scheduling density by season."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from src.data_loader import load_races
from src.theme import COLORS, apply_theme


def build_figure() -> go.Figure:
    df_races = load_races()

    volume_df = df_races.groupby("year")["round"].max().reset_index(name="total_rounds")

    density_records = []
    for year, group in df_races.dropna(subset=["date"]).groupby("year"):
        sorted_group = group.sort_values("round")
        if len(sorted_group) > 1:
            average_gap = sorted_group["date"].diff().dt.days.dropna().mean()
        else:
            average_gap = 0
        density_records.append({"year": year, "avg_days_gap": average_gap})

    df_q13 = pd.merge(volume_df, pd.DataFrame(density_records), on="year")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_q13["year"],
            y=df_q13["total_rounds"],
            mode="lines+markers",
            name="Total Races (Volume)",
            line=dict(color=COLORS["primary_blue"], width=3),
            marker=dict(size=6, color=COLORS["primary_blue"]),
            yaxis="y1",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_q13["year"],
            y=df_q13["avg_days_gap"],
            mode="lines",
            name="Avg Days Between Races (Density)",
            line=dict(color=COLORS["accent_orange"], width=2),
            fill="tozeroy",
            fillcolor="rgba(255, 127, 14, 0.15)",
            yaxis="y2",
        )
    )

    apply_theme(
        fig,
        title="F1 Championship Evolution: Annual Volume & Scheduling Density",
        height=600,
        hovermode="x unified",
        yaxis=dict(
            title=dict(text="<b>Total Scheduled Races</b>", font=dict(color=COLORS["primary_blue"])),
            side="left",
            gridcolor=COLORS["grid_line"],
            zeroline=False,
        ),
        yaxis2=dict(
            title=dict(text="<b>Average Days Gap</b>", font=dict(color=COLORS["accent_orange"])),
            side="right",
            overlaying="y",
            gridcolor="rgba(0,0,0,0)",
            zeroline=False,
        ),
        xaxis=dict(title="<b>Championship Year</b>", dtick=10, gridcolor=COLORS["grid_line"]),
        legend=dict(x=0.02, y=0.98),
        margin=dict(l=80, r=80, t=100, b=80),
    )
    return fig
