# %% [markdown]
# # CHAIMA'S WORKSPACE: CORE DATA LOADING & CLEANING PIPELINE
# Run this cell block first to load the datasets and map variables.

# %%
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

COLOR_PALETTE = {
    'text_dark': '#2C2C2C',
    'neutral_bg': '#F8F7F3',
    'grid_line': '#D3D3D3'
}

try:
    # Load raw tables using clean relative folder path indices
    df_circuits = pd.read_csv('data/circuits.csv')
    df_races = pd.read_csv('data/races.csv')
    
    # Force data types to uniform integers and explicit timestamps
    df_races['date'] = pd.to_datetime(df_races['date'], errors='coerce')
    df_races['year'] = pd.to_numeric(df_races['year'], errors='coerce').astype(int)
    
    print("🏁 [SUCCESS] Relational tables successfully parsed into active memory panels!")
    print(f"Loaded {len(df_races)} chronological races and {len(df_circuits)} track profiles.")

except FileNotFoundError as e:
    print(f"❌ [PATH CONFIGURATION ERROR] Could not locate files.\nDetails: {e}")

# %% [markdown]
# # VISUALIZATION 1: SEASONAL VOLUME SCALING & DENSITY COMPRESSION (Q1.3)
# FIXED: Re-architected with explicit Plotly Graph Objects to ensure dual-axis alignment.

# %%
# 1. Compute annual volume metrics (max round index per season)
volume_df = df_races.groupby('year')['round'].max().reset_index(name='total_rounds')

# 2. Compute density metrics (average interval space in days between consecutive rounds)
density_records = []
for year, group in df_races.dropna(subset=['date']).groupby('year'):
    sorted_group = group.sort_values('round')
    if len(sorted_group) > 1:
        # Calculate time deltas between successive events
        days_gaps = sorted_group['date'].diff().dt.days.dropna()
        average_gap = days_gaps.mean()
    else:
        average_gap = 0
    density_records.append({'year': year, 'avg_days_gap': average_gap})

df_density = pd.DataFrame(density_records)
df_q13 = pd.merge(volume_df, df_density, on='year')

# Generate Figure explicitly to support dual-axis scaling layers
fig_q13 = go.Figure()

# Add Volume Trace (Left Axis)
fig_q13.add_trace(go.Scatter(
    x=df_q13['year'], y=df_q13['total_rounds'],
    mode='lines+markers', name='Total Races (Volume)',
    line=dict(color='#1E90FF', width=3.5),
    yaxis='y1'
))

# Add Density Gap Trace filled as a background area (Right Axis)
fig_q13.add_trace(go.Scatter(
    x=df_q13['year'], y=df_q13['avg_days_gap'],
    mode='lines', name='Avg Days Gap (Density)',
    line=dict(color='#FF4500', width=1.5),
    fill='tozeroy', fillcolor='rgba(255, 69, 0, 0.2)',
    yaxis='y2'
))

# Configure the dual-axis structural properties to keep visual balance
fig_q13.update_layout(
    title=dict(text="Evolution of Seasonal Calendar Volume vs. Density Compression (1950-2024)", font=dict(color='#1E90FF', size=16)),
    template="plotly_dark",
    paper_bgcolor="#000000", plot_bgcolor="#0A0A0A",
    xaxis=dict(title=dict(text="Championship Season Year", font=dict(color="#FFFFFF", size=13)), gridcolor="#444444", tickfont=dict(color="#FFFFFF")),
    yaxis=dict(title=dict(text="Total Scheduled Rounds (Races)", font=dict(color="#1E90FF", size=12)), side="left", tickfont=dict(color="#FFFFFF")),
    yaxis2=dict(title=dict(text="Average Days Gap Between Events", font=dict(color="#FF4500", size=12)), side="right", overlaying="y", tickfont=dict(color="#FFFFFF"), range=[40, 0]),
    legend=dict(x=0.05, y=0.95, bgcolor="rgba(0, 0, 0, 0.9)", font=dict(color="#FFFFFF"))
)

# Save as interactive HTML
fig_q13.write_html("visualization_1_volume_density.html")
print("✅ Saved: visualization_1_volume_density.html")

# %% [markdown]
# # VISUALIZATION 2: CIRCUIT PRESENCE MATRIX HEATMAP
# Shows which classic circuits hosted races across different years
# Grouped alphabetically by Country (A-Z top-to-bottom), and then by Circuit Name

# %%
# DATA PREPARATION FOR HEATMAP
df_merged = pd.merge(df_races, df_circuits, on='circuitId', how='inner')

# Identify classic circuits (debuted 1950-1960)
classic_cohort_ids = df_merged[df_merged['year'] <= 1960]['circuitId'].unique()

# Filter to classic circuits only
df_classic = df_merged[df_merged['circuitId'].isin(classic_cohort_ids)].copy()

# CREATE PRESENCE MATRIX: 1 = hosted that year, 0 = not hosted
matrix_pivot = df_classic.groupby(['name_y', 'year']).size().unstack(fill_value=0)
matrix_pivot = matrix_pivot.map(lambda x: 1 if x > 0 else 0)

# =========================================================================
# FIXED: VERTICAL ORDERING BY COUNTRY (A-Z TOP-TO-BOTTOM)
# Maps each circuit to its country, sorts descending so Plotly draws it A-Z
# =========================================================================
# Create a unique mapping dictionary of {circuit_name: country}
circuit_to_country = df_classic.set_index('name_y')['country'].to_dict()

# Sort descending (Z to A) so the bottom-up plot engine renders it A-Z top-to-bottom
ordered_circuits = (
    pd.Series(circuit_to_country)
    .sort_values(ascending=False)
    .index
)

# Reindex the matrix with the country-grouped circuit order
matrix_pivot = matrix_pivot.reindex(ordered_circuits)

# Update the Y-axis labels to explicitly show "Country - Circuit Name"
matrix_pivot.index = [f"{circuit_to_country[name]} - {name}" for name in matrix_pivot.index]
# =========================================================================

# RENDER HEATMAP WITH CUSTOM 2-COLOR SCALE
if not matrix_pivot.empty:
    # CUSTOM COLOR SCALE: 2 colors only
    # Value 0 (Not Hosted) = White (#FFFFFF)
    # Value 1 (Hosted) = Pastel Blue (#ADD8E6)
    custom_colors = [
        [0, '#FFFFFF'],      # White for NO (not hosted)
        [1, '#ADD8E6']       # Pastel Blue for YES (hosted)
    ]
    
    fig_heatmap = px.imshow(
        matrix_pivot,
        labels=dict(
            x="Season",
            y="Classic Circuit (by Country)",
            color="Hosted"
        ),
        x=matrix_pivot.columns,
        y=matrix_pivot.index,
        # CUSTOM 2-COLOR SCALE: White (No) to Pastel Blue (Yes)
        color_continuous_scale=custom_colors,
        title="Historical Circuit Presence Matrix: Classic Tracks (Cohort 1950-1960)",
        zmin=0,
        zmax=1
    )

    # PROFESSIONAL LIGHT THEME STYLING
    fig_heatmap.update_layout(
        title=dict(
            text="<b>Classic F1 Circuits: Historical Presence & Displacement Matrix</b>",
            font=dict(color=COLOR_PALETTE['text_dark'], size=16, family="Arial, sans-serif"),
            x=0.5,
            xanchor='center'
        ),
        template="plotly_white",
        paper_bgcolor=COLOR_PALETTE['neutral_bg'],
        plot_bgcolor=COLOR_PALETTE['neutral_bg'],
        
        # X-AXIS (Years/Seasons) - ANGLED AT 45 DEGREES
        xaxis=dict(
            title=dict(text="<b>Season</b>", font=dict(color=COLOR_PALETTE['text_dark'], size=12)),
            tickfont=dict(color=COLOR_PALETTE['text_dark'], size=10),
            gridcolor=COLOR_PALETTE['grid_line'],
            gridwidth=1,
            showgrid=True,
            dtick=2,
            tickangle=-45  # INCLINE YEARS AT 45 DEGREES
        ),
        
        # Y-AXIS (Circuits)
        yaxis=dict(
            title=dict(text="<b>Classic Circuit</b>", font=dict(color=COLOR_PALETTE['text_dark'], size=12)),
            tickfont=dict(color=COLOR_PALETTE['text_dark'], size=9),
            gridcolor=COLOR_PALETTE['grid_line'],
            gridwidth=1,
            showgrid=True
        ),
        
        # COLOR BAR - HIDE GRADIENT, ADD CUSTOM DISCRETE BOXES
        coloraxis=dict(
            showscale=False,  # HIDE GRADIENT SCALE (PROPERTY OF COLORAXIS)
            cmin=0,
            cmax=1
        ),
        
        # GENERAL LAYOUT - Expanded left margin for the country prefixes
        margin=dict(l=280, r=150, t=100, b=120),  
        height=700,
        width=1400,
        showlegend=False
    )
    
    # ADD SUBTLE BORDERS
    fig_heatmap.update_xaxes(showline=True, linewidth=1, linecolor=COLOR_PALETTE['text_dark'])
    fig_heatmap.update_yaxes(showline=True, linewidth=1, linecolor=COLOR_PALETTE['text_dark'])
    
    # ADD CUSTOM DISCRETE COLOR BOXES (LEGEND) - RIGHT SIDE
    # BOX 1: WHITE FOR "NOT HOSTED" (NO)
    fig_heatmap.add_annotation(
        x=1.06,
        y=0.57,
        xref="paper",
        yref="paper",
        text="<b>Not Hosted</b>",
        showarrow=False,
        font=dict(size=11, color=COLOR_PALETTE['text_dark']),
        xanchor='left',
        yanchor='middle'
    )
    fig_heatmap.add_shape(
        type="rect",
        x0=1.02, x1=1.045,
        y0=0.555, y1=0.585,
        xref="paper", yref="paper",
        fillcolor="#FFFFFF",
        line=dict(color=COLOR_PALETTE['text_dark'], width=1.5),
        layer="above"
    )
    
    # BOX 2: BLUE FOR "HOSTED" (YES)
    fig_heatmap.add_annotation(
        x=1.06,
        y=0.48,
        xref="paper",
        yref="paper",
        text="<b>Hosted</b>",
        showarrow=False,
        font=dict(size=11, color=COLOR_PALETTE['text_dark']),
        xanchor='left',
        yanchor='middle'
    )
    fig_heatmap.add_shape(
        type="rect",
        x0=1.02, x1=1.045,
        y0=0.465, y1=0.495,
        xref="paper", yref="paper",
        fillcolor="#ADD8E6",  # PASTEL BLUE
        line=dict(color=COLOR_PALETTE['text_dark'], width=1.5),
        layer="above"
    )

    # Save visualization 2
    fig_heatmap.write_html("visualization_2_presence_matrix.html")
    print("✅ Saved: visualization_2_presence_matrix.html")

# %% [markdown]
# # VISUALIZATION 3: NORMALLY DISTRIBUTED BAR STACKS OF CALENDAR SHARE (Q1.4)
# Visualizes the contraction of classic track real estate by decade.

# %%
# Step 1: Label each race entry as either a Classic Circuit or a New/Modern Venue
df_merged['venue_classification'] = np.where(
    df_merged['circuitId'].isin(classic_cohort_ids), 
    'Classic Tracks Cohort (1950-1960)', 
    'Modern & New Venues'
)

# Step 2: Group into decadal time blocks
df_merged['decade'] = (df_merged['year'] // 10 * 10).astype(str) + "s"

# Calculate total race counts within each category per decade
decade_share = df_merged.groupby(['decade', 'venue_classification']).size().reset_index(name='race_count')

# Render the 100% Stacked Proportional Bar Chart
fig_share = px.bar(
    decade_share, x="decade", y="race_count", color="venue_classification",
    title="Decadal Contraction of Classic Calendar Real Estate Share (1950-2020s)",
    labels={"decade": "Championship Decade Generation", "race_count": "Total Scheduled Grand Prix Slots", "venue_classification": "Circuit Profile"},
    color_discrete_map={'Classic Tracks Cohort (1950-1960)': '#00CED1', 'Modern & New Venues': '#FF6347'},
    category_orders={"decade": ["1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]}
)

fig_share.update_layout(
    template="plotly_dark",
    paper_bgcolor="#000000", plot_bgcolor="#0A0A0A",
    title_font_color="#1E90FF",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#FFFFFF"), bgcolor="rgba(0, 0, 0, 0.9)"),
    yaxis=dict(tickformat="%.0%", tickfont=dict(color="#FFFFFF"), gridcolor="#333333"),
    xaxis=dict(tickfont=dict(color="#FFFFFF"), title=dict(text="Championship Decade Era", font=dict(color="#FFFFFF", size=12))),
)

fig_share.update_traces(marker=dict(), textposition="inside")
fig_share.update_xaxes(categoryorder="array", categoryarray=["1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"])

# Save as interactive HTML
fig_share.write_html("visualization_3_calendar_share.html")
print("✅ Saved: visualization_3_calendar_share.html")

print("\n✅ All visualizations have been created and saved!")
