"""Classic circuit presence matrix heatmap."""

import plotly.express as px
import plotly.graph_objects as go

from src.data_loader import load_circuits, load_races
from src.theme import COLORS, apply_theme


def build_figure() -> go.Figure:
    """Classic circuits = any venue that hosted a race during 1950–1960."""
    df_merged = load_races().merge(load_circuits(), on="circuitId", how="inner")
    classic_cohort_ids = df_merged[df_merged["year"] <= 1960]["circuitId"].unique()
    df_classic = df_merged[df_merged["circuitId"].isin(classic_cohort_ids)].copy()

    matrix_pivot = df_classic.groupby(["name_y", "year"]).size().unstack(fill_value=0)
    matrix_pivot = matrix_pivot.map(lambda x: 1 if x > 0 else 0)

    if matrix_pivot.empty:
        fig = go.Figure()
        apply_theme(
            fig, title="Classic F1 Circuits: Historical Presence Matrix", height=600
        )
        return fig

    custom_colors = [[0, COLORS["white"]], [1, COLORS["hosted_blue"]]]

    fig = px.imshow(
        matrix_pivot,
        labels=dict(x="Season", y="Classic Circuit", color="Hosted"),
        x=matrix_pivot.columns,
        y=matrix_pivot.index,
        color_continuous_scale=custom_colors,
        zmin=0,
        zmax=1,
    )

    apply_theme(
        fig,
        title="Classic F1 Circuits: Historical Presence & Displacement Matrix",
        height=700,
        showlegend=False,
        xaxis=dict(
            title="<b>Season</b>", tickangle=-45, dtick=2, gridcolor=COLORS["grid_line"]
        ),
        yaxis=dict(title="<b>Classic Circuit</b>", gridcolor=COLORS["grid_line"]),
        coloraxis=dict(showscale=False, cmin=0, cmax=1),
        margin=dict(l=200, r=150, t=100, b=120),
    )

    fig.update_xaxes(showline=True, linewidth=1, linecolor=COLORS["text_dark"])
    fig.update_yaxes(showline=True, linewidth=1, linecolor=COLORS["text_dark"])

    fig.add_annotation(
        x=1.06,
        y=0.57,
        xref="paper",
        yref="paper",
        text="<b>Not Hosted</b>",
        showarrow=False,
        font=dict(size=11, color=COLORS["text_dark"]),
        xanchor="left",
        yanchor="middle",
    )
    fig.add_shape(
        type="rect",
        x0=1.02,
        x1=1.045,
        y0=0.555,
        y1=0.585,
        xref="paper",
        yref="paper",
        fillcolor=COLORS["white"],
        line=dict(color=COLORS["text_dark"], width=1.5),
        layer="above",
    )
    fig.add_annotation(
        x=1.06,
        y=0.48,
        xref="paper",
        yref="paper",
        text="<b>Hosted</b>",
        showarrow=False,
        font=dict(size=11, color=COLORS["text_dark"]),
        xanchor="left",
        yanchor="middle",
    )
    fig.add_shape(
        type="rect",
        x0=1.02,
        x1=1.045,
        y0=0.465,
        y1=0.495,
        xref="paper",
        yref="paper",
        fillcolor=COLORS["hosted_blue"],
        line=dict(color=COLORS["text_dark"], width=1.5),
        layer="above",
    )
    return fig
