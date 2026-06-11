import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as graph_objects
from dash import Dash, Input, Output, dcc, html
from plotly.subplots import make_subplots

# ==========================================
# 1. SIMULATED DATA GENERATION
# (Replace this with your actual CSV loads)
# ==========================================
np.random.seed(42)
decades = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]

mock_circuits = []
# Europe dominant early on
for d in decades:
    n_circuits = np.random.randint(5, 15)
    for _ in range(n_circuits):
        if d <= 1970:
            # Heavily European biased
            lat = np.random.uniform(40, 55)
            lon = np.random.uniform(-5, 15)
            region = "Europe"
        else:
            # Gradually expanding to Middle East, Asia, Americas
            region = np.random.choice(
                ["Europe", "Americas", "Asia-Pacific", "Middle East"],
                p=[0.3, 0.3, 0.2, 0.2],
            )
            if region == "Europe":
                lat, lon = np.random.uniform(40, 55), np.random.uniform(-5, 15)
            elif region == "Americas":
                lat, lon = np.random.uniform(25, 45), np.random.uniform(
                    -120, -70
                )
            elif region == "Asia-Pacific":
                lat, lon = np.random.uniform(-35, 35), np.random.uniform(
                    100, 140
                )
            else:
                lat, lon = np.random.uniform(23, 26), np.random.uniform(45, 55)

        mock_circuits.append(
            {
                "circuit_id": len(mock_circuits),
                "decade": d,
                "lat": lat,
                "lon": lon,
                "region": region,
                "races_hosted": np.random.randint(1, 15),
            }
        )

df = pd.DataFrame(mock_circuits)

# ==========================================
# 2. TRUE SPHERICAL CENTER OF GRAVITY (CoG)
# Fixes the 2D Map Distortion Critique
# ==========================================


def calculate_spherical_cog(dataframe):
    cog_list = []
    for dec in sorted(dataframe["decade"].unique()):
        df_dec = dataframe[dataframe["decade"] == dec]

        # Convert Lat/Lon to Radians
        lat_rad = np.radians(df_dec["lat"])
        lon_rad = np.radians(df_dec["lon"])
        w = df_dec["races_hosted"]

        # Convert to 3D Cartesian coordinates
        x = np.cos(lat_rad) * np.cos(lon_rad) * w
        y = np.cos(lat_rad) * np.sin(lon_rad) * w
        z = np.sin(lat_rad) * w

        # Weighted average of 3D vectors
        x_avg = np.sum(x) / np.sum(w)
        y_avg = np.sum(y) / np.sum(w)
        z_avg = np.sum(z) / np.sum(w)

        # Convert back to Spherical Lat/Lon
        hyp = np.sqrt(x_avg**2 + y_avg**2)
        cog_lat = np.degrees(np.arctan2(z_avg, hyp))
        cog_lon = np.degrees(np.arctan2(y_avg, x_avg))

        cog_list.append(
            {"decade": dec, "cog_lat": cog_lat, "cog_lon": cog_lon}
        )

    return pd.DataFrame(cog_list)


df_cog = calculate_spherical_cog(df)

# ==========================================
# 3. DASH APPLICATION LAYOUT
# ==========================================
app = Dash(__name__)

app.layout = html.Div(
    style={
        "fontFamily": "Segoe UI, sans-serif",
        "backgroundColor": "#f8f9fa",
        "padding": "20px",
    },
    children=[
        html.H1(
            "Formula 1 Geographic Evolution Dashboard",
            style={"textAlign": "center", "color": "#1a202c"},
        ),
        html.P(
            "Addressing temporal distortions and map projection limitations in spatial data.",
            style={"textAlign": "center", "color": "#718096", "margin": "10px"},
        ),
        html.Div(
            style={
                "display": "flex",
                "justifyContent": "center",
                "gap": "20px",
                "margin": "20px 0",
            },
            children=[
                html.Div(
                    style={
                        "width": "48%",
                        "backgroundColor": "white",
                        "padding": "15px",
                        "borderRadius": "8px",
                        "boxShadow": "0 4px 6px rgba(0,0,0,0.05)",
                    },
                    children=[
                        html.H3(
                            "Perspective 1: Pure Temporal Shift (No Map Distortion)",
                            style={"color": "#2d3748"},
                        ),
                        dcc.Graph(id="temporal-evolution-plot"),
                    ],
                ),
                html.Div(
                    style={
                        "width": "48%",
                        "backgroundColor": "white",
                        "padding": "15px",
                        "borderRadius": "8px",
                        "boxShadow": "0 4px 6px rgba(0,0,0,0.05)",
                    },
                    children=[
                        html.H3(
                            "Perspective 2: True Spherical Center of Gravity",
                            style={"color": "#2d3748"},
                        ),
                        dcc.Graph(id="spherical-cog-globe"),
                    ],
                ),
            ],
        ),
        html.Div(
            style={
                "width": "80%",
                "margin": "auto",
                "textAlign": "center",
                "padding": "20px",
            },
            children=[
                html.Label(
                    "Highlight Circuit Status Up To Decade:",
                    style={"fontWeight": "bold", "color": "#4a5568"},
                ),
                dcc.Slider(
                    id="decade-slider",
                    min=min(decades),
                    max=max(decades),
                    value=max(decades),
                    marks={str(d): str(d) for d in decades},
                    step=None,
                ),
            ],
        ),
    ],
)


# ==========================================
# 4. CALLBACKS FOR INTERACTIVITY
# ==========================================
@app.callback(
    [
        Output("temporal-evolution-plot", "figure"),
        Output("spherical-cog-globe", "figure"),
    ],
    [Input("decade-slider", "value")],
)
def update_graphs(selected_decade):
    # Filter dataset based on slider
    filtered_df = df[df["decade"] <= selected_decade]

    # --- 1. FIG: TEMPORAL EVOLUTION (Clean Timeline Breakdown) ---
    # We aggregate races by region per decade to show expansion without messy map dots
    timeline_data = (
        filtered_df.groupby(["decade", "region"])["races_hosted"]
        .sum()
        .reset_index()
    )

    fig_timeline = px.bar(
        timeline_data,
        x="decade",
        y="races_hosted",
        color="region",
        title="Distribution of Races Hosted by Global Region",
        labels={"races_hosted": "Total Races Held", "decade": "Decade"},
        color_discrete_sequence=px.colors.qualitative.Safe,
        barmode="stack",
    )
    fig_timeline.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )

    # --- 2. FIG: SPHERICAL GLOBE WITH CORRECTED CoG ---
    # Using an Orthographic projection (Globe) solves the 2D projection critique.
    fig_globe = graph_objects.Figure()

    # Add active circuits
    fig_globe.add_trace(
        graph_objects.Scattergeo(
            lon=filtered_df["lon"],
            lat=filtered_df["lat"],
            text=filtered_df["region"],
            mode="markers",
            marker=dict(
                size=filtered_df["races_hosted"] * 1.5 + 4,
                color="#e53e3e",
                opacity=0.6,
            ),
            name="Active Circuits",
        )
    )

    # Filter CoG trace up to selected decade
    current_cog = df_cog[df_cog["decade"] <= selected_decade]

    # Add corrected CoG Path line
    fig_globe.add_trace(
        graph_objects.Scattergeo(
            lon=current_cog["cog_lon"],
            lat=current_cog["cog_lat"],
            mode="lines+markers",
            line=dict(color="#3182ce", width=3, dash="dash"),
            marker=dict(size=10, color="#2b6cb0", symbol="diamond"),
            name="True Spherical CoG Path",
            text=current_cog["decade"].apply(lambda x: f"{x}s CoG"),
        )
    )

    fig_globe.update_layout(
        title="True 3D Spherical Center of Gravity Path",
        geo=dict(
            projection_type="orthographic",  # Renders as a 3D Earth Globe
            showland=True,
            landcolor="#edf2f7",
            showocean=True,
            oceancolor="#ebf8ff",
            showcountries=True,
            countrycolor="#cbd5e0",
            center=dict(lat=30, lon=20),  # Centered near the movement path
        ),
        margin=dict(l=0, r=0, t=40, b=0),
    )

    return fig_timeline, fig_globe


if __name__ == "__main__":
    app.run(debug=True)
