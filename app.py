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


def _viz_card(title: str, description: str, figure_component, insights: list[str]):
    """Create a visualization card with title, description, graph, and insights."""
    return html.Div(
        className="bg-white rounded-lg p-6 mb-8 shadow-md card-hover border-l-4 border-f1-red",
        children=[
            html.H4(className="text-xl font-bold text-gray-800 mb-3", children=title),
            html.P(
                className="text-gray-600 mb-4 leading-relaxed",
                children=description,
            ),
            figure_component,
            html.Div(
                className="mt-6 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-5 border border-gray-200",
                children=[
                    html.H5(
                        className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2",
                        children=[html.Span("💡"), html.Span("Key Insights")],
                    ),
                    html.Ul(
                        className="space-y-2 text-gray-700",
                        children=[html.Li(children=insight, className="pl-4 border-l-2 border-f1-blue") for insight in insights],
                    ),
                ],
            ),
        ],
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
    <title>F1 Historical Analytics - Team 3</title>
    {{%favicon%}}
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='50' fill='%23D62728'/><rect y='50' width='100' height='50' fill='%231F77B4'/><text x='50' y='65' font-size='50' text-anchor='middle' fill='white' font-family='Arial'>🏎️</text></svg>"/>
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
                                        className="w-12 h-12 bg-gradient-to-br from-f1-red via-white to-f1-blue rounded-lg flex items-center justify-center shadow-md group-hover:shadow-lg transition-shadow interactive border-2 border-gray-800",
                                        children="🏁"
                                    ),
                                    html.Div(
                                        className="flex flex-col",
                                        children=[
                                            html.Span(
                                                "F1 Analytics",
                                                className="text-lg font-extrabold text-gray-800 group-hover:text-f1-red transition-colors leading-tight"
                                            ),
                                            html.Span(
                                                "Historical Data Lab",
                                                className="text-xs text-gray-500 font-medium -mt-1"
                                            ),
                                        ]
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
                    # Subtle background pattern with racing theme
                    html.Div(
                        className="absolute inset-0 bg-gradient-to-br from-f1-red/10 via-transparent to-f1-blue/10",
                    ),
                    # Decorative racing elements
                    html.Div(
                        className="absolute top-20 left-10 w-32 h-32 bg-f1-red/5 rounded-full blur-3xl",
                    ),
                    html.Div(
                        className="absolute bottom-10 right-10 w-48 h-48 bg-f1-blue/5 rounded-full blur-3xl",
                    ),
                    html.Div(
                        className="max-w-7xl mx-auto px-6 relative z-10",
                        children=[
                            # Hero content
                            html.Div(
                                className="text-center py-12 fade-in-section",
                                children=[
                                    html.Div(
                                        className="inline-block px-4 py-2 bg-gradient-to-r from-f1-red/10 to-f1-blue/10 rounded-full border border-gray-300 mb-6",
                                        children=[
                                            html.Span(className="text-sm font-semibold text-gray-700"),
                                            "🏁 Explore 74 Years of F1 History"
                                        ],
                                    ),
                                    html.H1(
                                        ["Beyond the Checkered Flag: ", html.Br(), "F1 Data Decoded"],
                                        className="text-5xl md:text-6xl lg:text-7xl font-extrabold mb-6 hero-glow text-f1-red",
                                    ),
                                    html.P(
                                        [
                                            "Discover the hidden stories behind Formula 1's greatest legends, dominant teams, and paradigm shifts. ",
                                            "From ", html.Span(className="font-bold text-f1-red"), "Schumacher's Ferrari dynasty", html.Span(className="font-normal"),
                                            " to ", html.Span(className="font-bold text-f1-blue"), "Hamilton's record-breaking reign", html.Span(className="font-normal"),
                                            ", explore how the sport transformed from a ",
                                            html.Span(className="font-bold text-f1-orange"), "49% European driver field in 1950", html.Span(className="font-normal"),
                                            " to today's global talent showcase. Uncover surprises:",
                                        ],
                                        className="text-xl text-gray-700 max-w-4xl mx-auto mb-8 leading-relaxed",
                                    ),
                                    # Curiosity hooks
                                    html.Div(
                                        className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-5xl mx-auto mb-10",
                                        children=[
                                            html.Div(
                                                className="bg-white rounded-xl shadow-md p-6 border-l-4 border-f1-red hover:shadow-lg transition-shadow interactive",
                                                children=[
                                                    html.H3(className="text-3xl font-bold text-f1-red mb-2"), "🏆",
                                                    html.P(
                                                        "Which driver won the MOST races in a single decade? (Hint: Not who you think)",
                                                        className="text-sm text-gray-700 font-medium leading-relaxed",
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                className="bg-white rounded-xl shadow-md p-6 border-l-4 border-f1-blue hover:shadow-lg transition-shadow interactive",
                                                children=[
                                                    html.H3(className="text-3xl font-bold text-f1-blue mb-2"), "🎂",
                                                    html.P(
                                                        "Drivers are 8 YEARS younger now than in the 1950s — what changed?",
                                                        className="text-sm text-gray-700 font-medium leading-relaxed",
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                className="bg-white rounded-xl shadow-md p-6 border-l-4 border-f1-orange hover:shadow-lg transition-shadow interactive",
                                                children=[
                                                    html.H3(className="text-3xl font-bold text-f1-orange mb-2"), "🌍",
                                                    html.P(
                                                        "North America had 43% of F1 drivers in the 1950s... now it's under 2%. Why?",
                                                        className="text-sm text-gray-700 font-medium leading-relaxed",
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                className="bg-white rounded-xl shadow-md p-6 border-l-4 border-green-500 hover:shadow-lg transition-shadow interactive",
                                                children=[
                                                    html.H3(className="text-3xl font-bold text-green-500 mb-2"), "⚡",
                                                    html.P(
                                                        "Pit stops haven't gotten faster since 2012 — here's why teams plateaued",
                                                        className="text-sm text-gray-700 font-medium leading-relaxed",
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    # Quick stats badges with actual numbers
                                    html.Div(
                                        className="flex flex-wrap justify-center gap-4 mt-6",
                                        children=[
                                            html.Div(
                                                className="px-6 py-4 bg-white rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition-shadow interactive group",
                                                children=[
                                                    html.Span(className="text-3xl font-extrabold text-f1-red block"), "74",
                                                    html.Small(className="text-gray-600 font-medium"), "Years of Data (1950-2024)",
                                                ],
                                            ),
                                            html.Div(
                                                className="px-6 py-4 bg-white rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition-shadow interactive group",
                                                children=[
                                                    html.Span(className="text-3xl font-extrabold text-f1-blue block"), "1,118",
                                                    html.Small(className="text-gray-600 font-medium"), "Races Analyzed",
                                                ],
                                            ),
                                            html.Div(
                                                className="px-6 py-4 bg-white rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition-shadow interactive group",
                                                children=[
                                                    html.Span(className="text-3xl font-extrabold text-f1-orange block"), "76+",
                                                    html.Small(className="text-gray-600 font-medium"), "Countries Represented",
                                                ],
                                            ),
                                            html.Div(
                                                className="px-6 py-4 bg-white rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition-shadow interactive group",
                                                children=[
                                                    html.Span(className="text-3xl font-extrabold text-green-500 block"), "10+",
                                                    html.Small(className="text-gray-600 font-medium"), "Interactive Visualizations",
                                                ],
                                            ),
                                        ],
                                    ),
                                    # Call to action
                                    html.Div(
                                        className="mt-10",
                                        children=[
                                            html.A(
                                                href="#calendar",
                                                className="inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-f1-red to-red-700 text-white rounded-lg font-bold text-lg shadow-lg hover:shadow-xl hover:scale-105 transition-all interactive",
                                                children=[
                                                    "Start Exploring",
                                                    html.Span(className="text-xl"), "↓",
                                                ],
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
                        "The Evolution of F1: From 7 Races to a Global Marathon",
                        "Discover how F1 transformed from a European championship with just 7 races into today's grueling 24-race global spectacle. Learn which tracks have stood the test of time and which vanished into history.",
                        [
                            _viz_card(
                                "F1 Championship Evolution: Annual Volume & Scheduling Density",
                                "This dual-axis visualization tracks how Formula 1 has evolved from a modest championship with fewer races to today's global marathon. The blue line shows the growing number of races per season (volume), while the orange area reveals scheduling density. The data shows dramatic expansion: from an average of 8.4 races per season in the 1950s to 21.4 races in the 2020s - more than doubling the calendar size over seven decades.",
                                _graph(build_calendar_volume(), config=STATIC_GRAPH_CONFIG),
                                [
                                    "F1 grew from 7 races in 1950 (first season) to a record 24 races in 2024",
                                    "Average calendar size: 8.4 races/season (1950s) → 21.4 races/season (2020s) - nearly triple the volume",
                                    "Exponential growth accelerated in the 2000s and continues through today with constant new market additions",
                                    "The expanded calendar creates logistical challenges as teams race on 5 continents within single seasons",
                                ],
                            ),
                            _viz_card(
                                "Classic F1 Circuits: Historical Presence & Displacement Matrix",
                                "This heatmap reveals the heritage tracks that defined Formula 1's early years (1950-1960). Each row represents a classic circuit, and blue squares indicate when that track hosted a race. The matrix shows how legendary circuits like Monaco (70 races), Monza (74 races), and Silverstone (59 races) have appeared most frequently throughout history, though with intermittent gaps. Many early venues were one-off races or hosted only occasionally during F1's formative era.",
                                _graph(build_circuit_presence(), config=STATIC_GRAPH_CONFIG),
                                [
                                    "Monaco, Monza, and Silverstone are the most persistent classic circuits but all have hosting gaps over the decades",
                                    "20 different circuits hosted races during the 1950-1960 golden era, but many disappeared quickly",
                                    "European circuits dominated early F1 before global expansion brought racing to other continents",
                                    "Tracks that survived longer (Monaco since 1950, Monza since 1950) became institutional pillars of the sport",
                                ],
                            ),
                            _viz_card(
                                "F1 Calendar Evolution: Classic vs Modern Venue Share by Decade",
                                "This stacked bar chart compares how F1's venue composition has changed over seven decades. Purple bars represent races at classic tracks (those existing in 1950-1960), while blue bars show modern and new venues. The dramatic shift from purple to blue tells the story of F1's transformation: from 100% classic tracks in the 1950s to just 21-23% by the 2010s-2020s, reflecting a fundamental restructuring of the championship.",
                                _graph(build_venue_share(), config=STATIC_GRAPH_CONFIG),
                                [
                                    "The 1950s calendar was 100% classic tracks (84 races total across all venues)",
                                    "Modern venues took majority dominance by the 1970s (66.7%), not the 1990s as commonly assumed",
                                    "Classic track share declined steadily: 66% (1960s) → 33% (1970s) → ~25% (1980s-2000s) → ~22% (2010s-2020s)",
                                    "The total calendar has grown from 84 races in the 1950s to nearly 200 per decade in recent years",
                                ],
                            ),
                        ],
                    ),
                    _viz_card(
                        "Geographic Evolution: Regional Race Distribution & Center of Gravity",
                        "This dual visualization explores how F1 has transformed from a European-centric championship into a truly global sport. The stacked bar chart shows race distribution across world regions by decade, revealing the emergence of new markets. The interactive globe displays actual circuit locations (dots sized by races hosted) and traces the spherical center of gravity - a weighted average position that literally tracks how F1's geographic focus has shifted over time as the dashed line moves across the map.",
                        html.Div([
                            html.Div(
                                className="flex gap-4 flex-wrap mb-6",
                                children=[
                                    html.Div(
                                        className="flex-1 min-w-[45%] bg-gray-50 rounded-lg p-3 shadow-sm border border-gray-200",
                                        children=[dcc.Graph(id="cog-timeline", config=STATIC_GRAPH_CONFIG)],
                                    ),
                                    html.Div(
                                        className="flex-1 min-w-[45%] bg-gray-50 rounded-lg p-3 shadow-sm border border-gray-200",
                                        children=[dcc.Graph(id="cog-globe", config=GRAPH_CONFIG)],
                                    ),
                                ],
                            ),
                            html.Div(
                                className="px-4 py-3 bg-white rounded-lg shadow-sm border border-gray-200",
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
                        ]),
                        [
                            "Europe's dominance has gradually declined as Middle East, Asia-Pacific, and Americas regions expanded",
                            "The center of gravity path visually demonstrates F1's expansion eastward and southward over decades",
                            "Middle Eastern races (Bahrain, Abu Dhabi, Saudi Arabia) represent the newest wave of growth since 2000s",
                            "Interactive slider lets you see how the geographic center shifted with each era of expansion",
                        ],
                    ),

                    html.Div(className="my-8 border-t-2 border-dashed border-gray-300"),

                    _section(
                        "geographic",
                        "🌍",
                        "Geographic Evolution (Detailed View)",
                        "Interactive exploration of race hosting patterns and center of gravity evolution.",
                        [
                            html.Div(
                                className="bg-white rounded-lg p-6 border-l-4 border-f1-blue",
                                children=[
                                    html.H5("🗺️ What You're Seeing", className="text-lg font-semibold mb-3"),
                                    html.P(
                                        "The timeline chart above stacks races by region, showing how the championship balanced its global presence. The globe visualization uses 3D orthographic projection with circuit markers sized by frequency of hosting. The dashed line traces the mathematical center of gravity - calculated using spherical coordinates weighted by race count - which physically moves as new circuits are added in different parts of the world.",
                                        className="text-gray-600 mb-4",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    _section(
                        "nationality",
                        "👥",
                        "The Globalization of Genius: How F1 Became Truly International",
                        "From 49% European drivers in the 1950s to today's worldwide talent pool — trace the seismic shifts in where F1 champions come from. Uncover why North America went from 43% dominance to near extinction.",
                        [
                            _viz_card(
                                "Structural Global Diversification: Driver & Constructor Nationalities Over Time",
                                "This line chart tracks F1's globalization by counting unique nationalities among drivers (cyan area) and constructors/team origins (orange area) each decade. Unlike expected steady growth, the data reveals surprisingly stable driver nationality counts from 1950s-2020s (hovering around 21-26), while constructor nationalities peaked in 1970s at 14 then declined. The gap shows global talent distributed among European-based teams.",
                                _graph(build_viz8()),
                                [
                                    "Driver nationalities remained remarkably stable: 21 (1950s) to 26 (2010s peak), not the dramatic increase expected",
                                    "Constructor diversity peaked at 14 unique nationalities in the 1970s, then declined to 7-11 in recent decades",
                                    "British constructors dominate overwhelmingly (12,239 entries) vs Italian (5,732), French (2,414), others much less",
                                    "The gap between driver and constructor diversity reflects F1's structure: global talent pool but team headquarters concentrated in Europe (Motorhome Valley UK)",
                                ],
                            ),
                            _viz_card(
                                "Geopolitical Waves of Talent Influx by Region",
                                "This area chart shows the composition of drivers on the grid by their geographic region of origin through history. Each colored band represents a region with thickness indicating driver appearances per season. Contrary to intuition, Western Europe did NOT consistently dominate early decades - North America represented 42.6% of drivers in the 1950s! Latin America's prominence peaked in the 2000s (16.9%), while Western Europe's dominance grew over time to reach ~70% by the 1990s.",
                                _graph(build_viz9()),
                                [
                                    "1950s was most diverse era: Western Europe only 49.3%, North America 42.6% - completely different from today's grid!",
                                    "Western Europe's share grew steadily: 49% (1950s) → 78% (1980s-1990s) → ~65% (2020s)",
                                    "Latin America peaked in the 2000s at 16.9% of all driver appearances, down from 11-13% in 1980s-2010s",
                                    "North America's presence dramatically declined: 43% (1950s) → under 2% (2010s-2020s), explaining US market struggles",
                                ],
                            ),
                        ],
                    ),
                    _section(
                        "competition",
                        "🏆",
                        "Dynasties & Dominance: Who REALLY Ruled F1 History?",
                        "Compare legendary rivalries, measure absolute domination, and discover which decades were truly competitive vs. controlled by a single driver or team.",
                        [
                            _viz_card(
                                "Driver Retention & Team Stability: Average Races per Driver per Decade",
                                "This box plot reveals how driver tenure with teams has evolved across F1 history. The data shows a dramatic shift in stability: from 1.9 average races per driver per team in the 1950s to 38 races in the 2010s-2020s. This twenty-fold increase reflects both longer driver careers and expanded seasons. Ferrari and Mercedes have shown exceptional retention, with drivers completing 58-99 races per team in recent decades.",
                                _graph(build_q24()),
                                [
                                    "Average races per driver increased 20x: 1.9 (1950s) → 38.0 (2010s) - a fundamental shift in team stability",
                                    "Ferrari dominated retention historically: 7.5 races/driver (1950s), 28.6 (1970s), 58.0 (2000s)",
                                    "Modern extremes show Mercedes and Red Bull at 71.3 races/driver (2020s) vs. minimum of 11.3 - huge variation",
                                    "1970s-1980s marked the turning point when seasons expanded and driver contracts became longer-term",
                                ],
                            ),
                            _viz_card(
                                "Driver vs Constructor Win Dominance: A Heatmap Comparison by Decade",
                                "This dual heat map reveals the concentration of race wins among top performers. The data shows remarkable patterns: Schumacher's 62 wins in the 2000s (Ferrari), Hamilton's 73 wins in the 2010s, and Verstappen's 55 wins in the 2020s represent extreme driver dominance. Constructor-wise, Ferrari's historical supremacy (249 total wins) and Mercedes' 93 wins in the 2010s show how organizational excellence can define entire eras.",
                                _graph(build_q31(), config=STATIC_GRAPH_CONFIG),
                                [
                                    "Schumacher-Ferrari 2000s: 62 driver wins + 85 constructor wins = most dominant single-decade combination in F1 history",
                                    "Hamilton-Mercedes 2010s: 73 driver wins (all-time decade record) paired with Mercedes' 93 constructor wins",
                                    "Ferrari is the only team to win in every decade from 1950s-2020s - unmatched consistency across 70+ years",
                                    "1980s was actually dominated by Prost (39 wins) and McLaren (56 wins), not as competitive as traditionally remembered",
                                ],
                            ),
                        ],
                    ),
                    _section(
                        "performance",
                        "⚡",
                        "Speed, Age & Strategy: The Science of F1 Performance",
                        "Why are modern F1 drivers 8 years younger on average? Why haven't pit stops gotten faster since 2012? Explore the data behind speed and success.",
                        [
                            _viz_card(
                                "Pit-Lane Excellence: Team Strategy & Pace Evolution (2011+)",
                                "This line chart tracks the evolution of pit-stop performance since 2011, when detailed pit data became consistently available. The dark line represents the field median pit time each season. Contrary to expected continuous improvement, median pit times have remained remarkably stable around 23-24 seconds from 2011-2024, starting at 22.37s (2011) and ending at 23.29s (2024). This plateau suggests teams have reached optimal efficiency limits or that regulation changes balance any gains.",
                                _graph(build_q33()),
                                [
                                    "Median pit times plateaued around 23-24 seconds since 2011, not continuously improving as expected",
                                    "2014-2015 saw the slowest median times (24.22s, 24.25s) possibly due to fuel flow or safety regulation changes",
                                    "Best year was 2012 at 22.26s - surprisingly, recent years have not surpassed this performance",
                                    "Consistent field of 600-1100 pit stops per year shows data reliability for meaningful trend analysis",
                                ],
                            ),
                            _viz_card(
                                "Driver Age Evolution: How the Grid's Demographics Have Shifted Across Decades",
                                "This violin plot shows the age distribution of drivers competing in each decade. The data reveals a clear trend: F1 drivers are getting significantly younger. The median age has dropped from 34.7 years in the 1950s to just 26.7 years in the 2020s - an 8-year decrease! Youngest-ever race entries appeared in 2015 (Max Verstappen at 17.5 years), marking a new era of teenage prodigies entering F1.",
                                _graph(build_q41(), config=STATIC_GRAPH_CONFIG),
                                [
                                    "Median driver age declined dramatically: 34.7y (1950s) → 26.7y (2020s) - the grid is nearly a decade younger!",
                                    "1950s drivers were oldest: median 34.7 years, minimum 20.2 years - very different from today's teenage debuts",
                                    "Youngest race entry: Max Verstappen at 17.5 years old (2015) - first driver under 18 in modern era",
                                    "Age range has expanded: modern F1 sees drivers from 17.5 to 43+ years, reflecting both younger debuts and longer careers",
                                ],
                            ),
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
                                                className="w-12 h-12 bg-gradient-to-br from-f1-red via-white to-f1-blue rounded-lg flex items-center justify-center shadow-md border-2 border-gray-700",
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
                                "INF8808E (E2026) - Data visualization | Team 3",
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
