"""Shared F1 cream theme for all Plotly figures."""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

COLORS = {
    "neutral_bg": "#F8F7F3",
    "text_dark": "#2C2C2C",
    "grid_line": "#D3D3D3",
    "primary_blue": "#1F77B4",
    "primary_red": "#D62728",
    "accent_purple": "#610376",
    "accent_orange": "#FF7F0E",
    "driver_cyan": "#17a6d4",
    "constructor_orange": "#d9531e",
    "hosted_blue": "#ADD8E6",
    "white": "#FFFFFF",
}

CATEGORICAL_PALETTE = [
    COLORS["primary_blue"],
    COLORS["primary_red"],
    COLORS["accent_orange"],
    COLORS["accent_purple"],
    COLORS["driver_cyan"],
    COLORS["constructor_orange"],
    "#2ca02c",
    "#9467bd",
    "#8c564b",
    "#e377c2",
]

REGION_COLORS = {
    "Western Europe": "#1F77B4",
    "North America": "#9467bd",
    "Latin America": "#FF7F0E",
    "Asia-Pacific": "#2ca02c",
    "Eastern Europe": "#e377c2",
    "Africa & Middle East": "#bcbd22",
    "Middle East": "#bcbd22",
    "Europe": "#1F77B4",
    "Americas": "#FF7F0E",
    "Other": "#7f7f7f",
}

SEQUENTIAL_RED = [
    [0.0, "#FEE5D9"],
    [0.25, "#FCAE91"],
    [0.5, "#FB6A4A"],
    [0.75, "#DE2D26"],
    [1.0, "#A50F15"],
]

SEQUENTIAL_BLUE = [
    [0.0, "#DEEBF7"],
    [0.25, "#9ECAE1"],
    [0.5, "#4292C6"],
    [0.75, "#2171B5"],
    [1.0, "#084594"],
]

FONT_FAMILY = "Arial, Helvetica, sans-serif"

F1_CREAM_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        font=dict(family=FONT_FAMILY, color=COLORS["text_dark"], size=12),
        paper_bgcolor=COLORS["neutral_bg"],
        plot_bgcolor=COLORS["neutral_bg"],
        colorway=CATEGORICAL_PALETTE,
        title=dict(
            font=dict(size=16, color=COLORS["text_dark"]),
            x=0.5,
            xanchor="center",
        ),
        xaxis=dict(
            gridcolor=COLORS["grid_line"],
            linecolor=COLORS["text_dark"],
            tickfont=dict(color=COLORS["text_dark"]),
        ),
        yaxis=dict(
            gridcolor=COLORS["grid_line"],
            linecolor=COLORS["text_dark"],
            tickfont=dict(color=COLORS["text_dark"]),
        ),
        legend=dict(
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor=COLORS["grid_line"],
            borderwidth=1,
            font=dict(color=COLORS["text_dark"]),
        ),
        margin=dict(l=70, r=40, t=80, b=70),
    )
)

pio.templates["f1_cream"] = F1_CREAM_TEMPLATE


def apply_theme(
    fig: go.Figure,
    *,
    title: str | None = None,
    height: int = 560,
    width: int | None = None,
    **layout_kwargs,
) -> go.Figure:
    """Apply the shared cream theme and return the figure."""
    layout = dict(
        template="f1_cream",
        paper_bgcolor=COLORS["neutral_bg"],
        plot_bgcolor=COLORS["neutral_bg"],
        height=height,
    )
    if width is not None:
        layout["width"] = width
    if title is not None:
        layout["title"] = dict(
            text=f"<b>{title}</b>",
            font=dict(color=COLORS["text_dark"], size=16, family=FONT_FAMILY),
            x=0.5,
            xanchor="center",
        )
    layout.update(layout_kwargs)
    fig.update_layout(**layout)
    return fig
