"""F1 Data Visualization — unified Dash dashboard.

Premium Racing Theme with Tailwind CSS
Team 3 | Course: Data Visualization Lab
"""

from __future__ import annotations

import os

from dash import Dash, Input, Output, callback_context, dcc, html

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

# Section IDs for navigation
SECTIONS = [
    {"id": "calendar", "title": "Calendar & Circuits", "desc": "How the championship schedule grew in volume, density, and geographic breadth."},
    {"id": "geographic", "title": "Geographic Evolution", "desc": "Race hosting by region and the spherical center of gravity path through time."},
    {"id": "nationality", "title": "Nationality & Talent", "desc": "Structural diversification and regional waves of drivers on the grid."},
    {"id": "competition", "title": "Competition Dynamics", "desc": "Team driver utilization and win dominance across eras."},
    {"id": "performance", "title": "Performance & Demographics", "desc": "Pit-lane pace evolution and shifting driver age profiles."},
]

decades = get_decades()


def _graph(figure, *, config: dict | None = None):
    return html.Div(
        className="bg-white rounded-lg p-3 mb-6 shadow-sm card-hover interactive",
        children=[dcc.Graph(figure=figure, config=config or GRAPH_CONFIG)],
    )


def _section(section_id: str, section_badge: str, title: str, blurb: str, children: list):
    return html.Div(
        id=section_id,
        className="py-12 border-t border-gray-300 fade-in-section",
        children=[
            html.Span(section_badge, className="section-badge"),
            html.H2(title, className="text-3xl font-bold text-gray-800 mb-3"),
            html.P(blurb, className="text-gray-600 mb-6 max-w-4xl"),
            *children,
        ],
    )


app = Dash(__name__)
server = app.server

# Add custom CSS and Tailwind CDN
custom_css_path = '/static/css/styles.css'

app.index_string = f'''
<!DOCTYPE html>
<html>
<head>
    {{%metas%}}
    <title>F1 Historical Analytics — Team 3</title>
    {{%favicon%}}
    {{%css%}}
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Custom styles -->
    <link rel="stylesheet" href="{custom_css_path}">
    <!-- Tailwind config for brand colors -->
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        'f1-red': '#D62728',
                        'f1-blue': '#1F77B4',
                        'f1-orange': '#FF7F0E',
                        'f1-cream': '#F8F7F3',
                        'f1-dark': '#2C2C2C',
                    }}
                }}
            }}
        }}
    </script>
</head>
<body class="bg-f1-cream text-f1-dark min-h-screen">
    {{%app_entry%}}
    <footer>
        {{%config%}}
        {{%scripts%}}
        {{%renderer%}}
    </footer>
</body>
</html>
'''

app.layout = html.Div([
    # Store for tracking active section
    dcc.Store(id='active-section', data='calendar'),
    
    # Fixed Navbar
    html.Nav(
        className="fixed top-0 left-0 right-0 bg-white/95 navbar-blur shadow-md z-50 border-b border-gray-200",
        children=[
            html.Div(
                className="max-w-7xl mx-auto px-6 py-4",
                children=[
                    html.Div(
                        className="flex items-center justify-between",
                        children=[
                            # Logo/Brand area
                            html.A(
                                href="#calendar",
                                className="flex items-center gap-3 group",
                                children=[
                                    html.Div(
                                        className="w-10 h-10 bg-gradient-to-br from-f1-red to-f1-blue rounded-lg flex items-center justify-center text-white font-bold text-lg shadow-md group-hover:shadow-lg transition-shadow interactive",
                                        children="🏁"
                                    ),
                                    html.Span(
                                        "F1 Analytics",
                                        className="text-xl font-bold text-gray-800 group-hover:text-f1-red transition-colors"
                                    ),
                                ],
                            ),
                            # Navigation Links
                            html.Div(
                                className="hidden md:flex items-center gap-1",
                                children=[
                                    html.A(
                                        href=f"#{section['id']}",
                                        className=f"nav-link px-4 py-2 text-sm font-medium text-gray-600 hover:text-f1-red rounded-lg interactive {('active' if i == 0 else '')}",
                                        children=section['title'],
                                        key=f"nav-{section['id']}"
                                    )
                                    for i, section in enumerate(SECTIONS)
                                ],
                            ),
                            # CTA / Back to top
                            html.A(
                                href="#calendar",
                                className="hidden md:inline-flex items-center px-4 py-2 bg-gradient-to-r from-f1-red to-f1-blue text-white text-sm font-semibold rounded-lg shadow-md hover:shadow-lg interactive transform hover:-translate-y-0.5",
                                children=[
                                    html.Span("📊 Dashboard"),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    ),
    
    # Main Content (with top padding for fixed navbar)
    html.Div(
        className="pt-28 pb-16",
        children=[
            # Hero Section
            html.Section(
                className="relative overflow-hidden mb-16",
                children=[
                    # Subtle background pattern
                    html.Div(
                        className="absolute inset-0 bg-gradient-to-br from-f1-red/5 via-transparent to-f1-blue/5",
                    ),
                    html.Div(
                        className="max-w-7xl mx-auto px-6 relative z-10",
                        children=[
                            # Hero content
                            html.Div(
                                className="text-center py-8 fade-in-section",
                                children=[
                                    html.H1(
                                        "Formula 1 Historical Analytics",
                                        className="text-5xl md:text-6xl font-extrabold mb-4 hero-glow gradient-text",
                                    ),
                                    html.P(
                                        "Interactive exploration of championship calendars, global talent flows, team dynamics, and performance trends across seven decades of F1 racing.",
                                        className="text-xl text-gray-600 max-w-3xl mx-auto mb-8 leading-relaxed",
                                    ),
                                    # Quick stats badges
                                    html.Div(
                                        className="flex flex-wrap justify-center gap-4 mt-6",
                                        children=[
                                            html.Div(
                                                className="px-6 py-3 bg-white rounded-xl shadow-sm border border-gray-200",
                                                children=[
                                                    html.Span(className="text-2xl font-bold text-f1-red"), "🏎️ 7+ Decades"
                                                ]
                                            ),
                                            html.Div(
                                                className="px-6 py-3 bg-white rounded-xl shadow-sm border border-gray-200",
                                                children=[
                                                    html.Span(className="text-2xl font-bold text-f1-blue"), "📈 10+ Visualizations"
                                                ]
                                            ),
                                            html.Div(
                                                className="px-6 py-3 bg-white rounded-xl shadow-sm border border-gray-200",
                                                children=[
                                                    html.Span(className="text-2xl font-bold text-f1-orange"), "🌍 Global Data"
                                                ]
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            
            # Sections Container
            html.Div(
                className="max-w-7xl mx-auto px-6",
                children=[
                    _section(
                        "calendar",
                        "📅",
                        "Calendar & Circuits",
                        "How the championship schedule grew in volume, density, and geographic breadth.",
                        [
                            _graph(build_calendar_volume(), config=STATIC_GRAPH_CONFIG),
                            _graph(build_circuit_presence(), config=STATIC_GRAPH_CONFIG),
                            _graph(build_venue_share(), config=STATIC_GRAPH_CONFIG),
                        ],
                    ),
                    _section(
                        "geographic",
                        "🌍",
                        "Geographic Evolution",
                        "Race hosting by region and the spherical center of gravity path through time.",
                        [
                            html.Div(
                                className="flex gap-4 flex-wrap",
                                children=[
                                    html.Div(
                                        className="flex-1 min-w-[45%] bg-white rounded-lg p-3 shadow-sm card-hover interactive",
                                        children=[dcc.Graph(id="cog-timeline", config=STATIC_GRAPH_CONFIG)],
                                    ),
                                    html.Div(
                                        className="flex-1 min-w-[45%] bg-white rounded-lg p-3 shadow-sm card-hover interactive",
                                        children=[dcc.Graph(id="cog-globe", config=GRAPH_CONFIG)],
                                    ),
                                ],
                            ),
                            html.Div(
                                className="mt-6 px-4 py-3 bg-white rounded-lg shadow-sm",
                                children=[
                                    html.Label(
                                        "Show data up to decade:",
                                        className="font-semibold text-gray-700 block mb-4",
                                    ),
                                    dcc.Slider(
                                        id="decade-slider",
                                        min=min(decades),
                                        max=max(decades),
                                        value=max(decades),
                                        marks={str(d): f"{d}s" for d in decades},
                                        step=None,
                                        className="custom-slider",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    _section(
                        "nationality",
                        "👥",
                        "Nationality & Talent",
                        "Structural diversification and regional waves of drivers on the grid.",
                        [
                            _graph(build_viz8()),
                            _graph(build_viz9()),
                        ],
                    ),
                    _section(
                        "competition",
                        "🏆",
                        "Competition Dynamics",
                        "Team driver utilization and win dominance across eras.",
                        [
                            _graph(build_q24()),
                            _graph(build_q31(), config=STATIC_GRAPH_CONFIG),
                        ],
                    ),
                    _section(
                        "performance",
                        "⚡",
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
    ),
    
    # Footer
    html.Footer(
        className="bg-gradient-to-r from-gray-900 to-gray-800 text-white py-12 mt-20",
        children=[
            html.Div(
                className="max-w-7xl mx-auto px-6",
                children=[
                    html.Div(
                        className="grid md:grid-cols-3 gap-8 mb-8",
                        children=[
                            # Brand column
                            html.Div(
                                children=[
                                    html.Div(
                                        className="flex items-center gap-3 mb-4",
                                        children=[
                                            html.Div(
                                                className="w-10 h-10 bg-gradient-to-br from-f1-red to-f1-blue rounded-lg flex items-center justify-center text-white font-bold",
                                                children="🏁"
                                            ),
                                            html.Span("F1 Analytics", className="text-xl font-bold"),
                                        ],
                                    ),
                                    html.P(
                                        "Data-driven insights into Formula 1 racing history.",
                                        className="text-gray-400",
                                    ),
                                ],
                            ),
                            # Quick links
                            html.Div(
                                children=[
                                    html.H3("Quick Navigation", className="font-semibold mb-4 text-white"),
                                    html.Ul(
                                        className="space-y-2",
                                        children=[
                                            html.Li(
                                                html.A(
                                                    href=f"#{section['id']}",
                                                    className="text-gray-400 hover:text-f1-red transition-colors text-sm interactive",
                                                    children=section['title'],
                                                ),
                                                key=f"footer-{section['id']}"
                                            )
                                            for section in SECTIONS
                                        ],
                                    ),
                                ],
                            ),
                            # Tech stack
                            html.Div(
                                children=[
                                    html.H3("Tech Stack", className="font-semibold mb-4 text-white"),
                                    html.Div(
                                        className="flex flex-wrap gap-2",
                                        children=[
                                            html.Span("Python", className="px-3 py-1 bg-gray-700 rounded-full text-xs"),
                                            html.Span("Dash", className="px-3 py-1 bg-gray-700 rounded-full text-xs"),
                                            html.Span("Plotly", className="px-3 py-1 bg-gray-700 rounded-full text-xs"),
                                            html.Span("Tailwind", className="px-3 py-1 bg-gray-700 rounded-full text-xs"),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Bottom bar
                    html.Div(
                        className="border-t border-gray-700 pt-8 flex flex-col md:flex-row justify-between items-center gap-4",
                        children=[
                            html.P(
                                "© 2026 F1 Data Visualization | Team 3 | Data Visualization Lab",
                                className="text-gray-400 text-sm",
                            ),
                            html.A(
                                href="#calendar",
                                className="inline-flex items-center gap-2 px-4 py-2 bg-f1-red hover:bg-red-700 rounded-lg text-sm font-medium transition-colors interactive",
                                children=[
                                    "↑ Back to Top"
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    ),

    # Callback for active section tracking
    html.Script('''
        // Smooth scroll handling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener("click", function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute("href"));
                if (target) {
                    target.scrollIntoView({ behavior: "smooth", block: "start" });
                }
            });
        });
    '''),
])


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
