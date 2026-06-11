"""F1 Data Visualization — unified Dash dashboard."""

from __future__ import annotations

import os

from dash import Dash, Input, Output, dcc, html

from src.figures.calendar_volume import build_figure as build_calendar_volume
from src.figures.circuit_presence import build_figure as build_circuit_presence
from src.figures.geographic_cog import (
    build_globe_figure,
    build_timeline_figure,
    get_decades,
)
from src.figures.q24_team_races import build_figure as build_q24
from src.figures.q31_dominance import build_figure as build_q31
from src.figures.q33_pit_stops import build_figure as build_q33
from src.figures.q41_driver_age import build_figure as build_q41
from src.figures.venue_share import build_figure as build_venue_share
from src.figures.viz8_nationalities import build_figure as build_viz8
from src.figures.viz9_regions import build_figure as build_viz9
from src.theme import COLORS

GRAPH_CONFIG = {"displayModeBar": True, "scrollZoom": True}

STATIC_GRAPH_CONFIG = {
    **GRAPH_CONFIG,
    "scrollZoom": False,
    "doubleClick": False,
    "modeBarButtonsToRemove": ["zoom", "zoomIn", "zoomOut", "autoScale", "resetScale", "pan2d", "lasso2d", "select2d"],
}

PAGE_STYLE = {
    "fontFamily": "Arial, Helvetica, sans-serif",
    "backgroundColor": COLORS["neutral_bg"],
    "color": COLORS["text_dark"],
    "minHeight": "100vh",
    "padding": "0 0 60px 0",
}

CONTAINER_STYLE = {
    "maxWidth": "1200px",
    "margin": "0 auto",
    "padding": "0 24px",
}

SECTION_STYLE = {
    "marginTop": "48px",
    "paddingTop": "32px",
    "borderTop": f"1px solid {COLORS['grid_line']}",
}

CARD_STYLE = {
    "backgroundColor": COLORS["white"],
    "borderRadius": "8px",
    "padding": "8px",
    "marginBottom": "24px",
    "boxShadow": "0 2px 8px rgba(0,0,0,0.06)",
}

decades = get_decades()


def _graph(figure, *, config: dict | None = None):
    return html.Div(
        style=CARD_STYLE,
        children=[dcc.Graph(figure=figure, config=config or GRAPH_CONFIG)],
    )


def _section(title: str, blurb: str, children: list):
    return html.Div(
        style=SECTION_STYLE,
        children=[
            html.H2(title, style={"marginBottom": "8px"}),
            html.P(blurb, style={"color": "#555", "marginBottom": "24px"}),
            *children,
        ],
    )


app = Dash(__name__)
server = app.server

app.layout = html.Div(
    style=PAGE_STYLE,
    children=[
        html.Div(
            style={**CONTAINER_STYLE, "paddingTop": "40px"},
            children=[
                html.H1(
                    "Formula 1 Historical Analytics",
                    style={"textAlign": "center", "marginBottom": "8px", "fontWeight": "700"},
                ),
                html.P(
                    "Interactive exploration of championship calendars, global talent flows, "
                    "team dynamics, and performance trends across seven decades of F1.",
                    style={"textAlign": "center", "color": "#555", "marginBottom": "40px"},
                ),
            ],
        ),
        html.Div(
            style=CONTAINER_STYLE,
            children=[
                _section(
                    "Calendar & Circuits",
                    "How the championship schedule grew in volume, density, and geographic breadth.",
                    [
                        _graph(build_calendar_volume()),
                        _graph(build_circuit_presence()),
                        _graph(build_venue_share()),
                    ],
                ),
                _section(
                    "Geographic Evolution",
                    "Race hosting by region and the spherical center of gravity path through time.",
                    [
                        html.Div(
                            style={"display": "flex", "gap": "16px", "flexWrap": "wrap"},
                            children=[
                                html.Div(
                                    style={**CARD_STYLE, "flex": "1 1 45%"},
                                    children=[dcc.Graph(id="cog-timeline", config=GRAPH_CONFIG)],
                                ),
                                html.Div(
                                    style={**CARD_STYLE, "flex": "1 1 45%"},
                                    children=[dcc.Graph(id="cog-globe", config=GRAPH_CONFIG)],
                                ),
                            ],
                        ),
                        html.Div(
                            style={"padding": "12px 8px 24px"},
                            children=[
                                html.Label(
                                    "Show data up to decade:",
                                    style={
                                        "fontWeight": "bold",
                                        "display": "block",
                                        "marginBottom": "16px",
                                    },
                                ),
                                dcc.Slider(
                                    id="decade-slider",
                                    min=min(decades),
                                    max=max(decades),
                                    value=max(decades),
                                    marks={str(d): f"{d}s" for d in decades},
                                    step=None,
                                ),
                            ],
                        ),
                    ],
                ),
                _section(
                    "Nationality & Talent",
                    "Structural diversification and regional waves of drivers on the grid.",
                    [
                        _graph(build_viz8()),
                        _graph(build_viz9()),
                    ],
                ),
                _section(
                    "Competition Dynamics",
                    "Team driver utilization and win dominance across eras.",
                    [
                        _graph(build_q24()),
                        _graph(build_q31(), config=STATIC_GRAPH_CONFIG),
                    ],
                ),
                _section(
                    "Performance & Demographics",
                    "Pit-lane pace evolution and shifting driver age profiles.",
                    [
                        _graph(build_q33()),
                        _graph(build_q41(), config=STATIC_GRAPH_CONFIG),
                    ],
                ),
            ],
        ),
    ],
)


@app.callback(
    Output("cog-timeline", "figure"),
    Output("cog-globe", "figure"),
    Input("decade-slider", "value"),
)
def update_cog(selected_decade):
    return build_timeline_figure(selected_decade), build_globe_figure(selected_decade)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=True)
