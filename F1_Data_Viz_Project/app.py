# %% [markdown]
# # CHAIMA'S F1 DATA VISUALIZATION PROJECT
# Professional F1 Racing Analytics Dashboard with Interactive Visualizations
# =========================================================================

# %%
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# PROFESSIONAL COLOR PALETTE
COLOR_PALETTE = {
    'primary_blue': '#1F77B4',      # Professional blue
    'primary_red': '#D62728',       # Professional red
    'neutral_bg': '#F8F7F3',        # Cream/beige background
    'text_dark': '#2C2C2C',         # Dark text
    'text_light': '#FFFFFF',        # White text
    'grid_line': '#D3D3D3',         # Light grid
    'accent_bronze': "#4A0685"      # Bronze accent
}

# %%
# DATA LOADING & PREPROCESSING
# =============================
try:
    df_circuits = pd.read_csv('data/circuits.csv')
    df_races = pd.read_csv('data/races.csv')
    
    # Data type conversion
    df_races['date'] = pd.to_datetime(df_races['date'], errors='coerce')
    df_races['year'] = pd.to_numeric(df_races['year'], errors='coerce').astype(int)
    
    print("🏁 [SUCCESS] Data loaded successfully!")
    print(f"📊 Loaded {len(df_races)} races across {len(df_circuits)} circuits")

except FileNotFoundError as e:
    print(f"❌ [ERROR] Could not locate data files.\nDetails: {e}")

# %% [markdown]
# # VISUALIZATION 1: SEASONAL CALENDAR VOLUME & DENSITY ANALYSIS
# Shows evolution of F1 championship volume (number of races) and scheduling density

# %%
# METRIC 1: Annual Volume (total races per year)
volume_df = df_races.groupby('year')['round'].max().reset_index(name='total_rounds')

# METRIC 2: Scheduling Density (average days between consecutive races)
density_records = []
for year, group in df_races.dropna(subset=['date']).groupby('year'):
    sorted_group = group.sort_values('round')
    if len(sorted_group) > 1:
        days_gaps = sorted_group['date'].diff().dt.days.dropna()
        average_gap = days_gaps.mean()
    else:
        average_gap = 0
    density_records.append({'year': year, 'avg_days_gap': average_gap})

df_density = pd.DataFrame(density_records)
df_q13 = pd.merge(volume_df, df_density, on='year')

# CREATE DUAL-AXIS FIGURE
fig_q13 = go.Figure()

# Axis 1 (Left): Total Races Volume - Blue line with markers
fig_q13.add_trace(go.Scatter(
    x=df_q13['year'], 
    y=df_q13['total_rounds'],
    mode='lines+markers', 
    name='Total Races (Volume)',
    line=dict(color='#1F77B4', width=3),
    marker=dict(size=6, color='#1F77B4'),
    yaxis='y1'
))

# Axis 2 (Right): Scheduling Density - Orange line with fill
fig_q13.add_trace(go.Scatter(
    x=df_q13['year'], 
    y=df_q13['avg_days_gap'],
    mode='lines', 
    name='Avg Days Between Races (Density)',
    line=dict(color='#FF7F0E', width=2),
    fill='tozeroy', 
    fillcolor='rgba(255, 127, 14, 0.15)',
    yaxis='y2'
))

# PROFESSIONAL LAYOUT STYLING
fig_q13.update_layout(
    title=dict(
        text="F1 Championship Evolution: Annual Volume & Scheduling Density (1950-2024)",
        font=dict(color=COLOR_PALETTE['text_dark'], size=18, family="Arial, sans-serif"),
        x=0.5,
        xanchor='center'
    ),
    template="plotly_white",
    paper_bgcolor=COLOR_PALETTE['neutral_bg'],
    plot_bgcolor=COLOR_PALETTE['neutral_bg'],
    hovermode="x unified",
    
    # LEFT Y-AXIS: Total Races
    yaxis=dict(
        title=dict(text="<b>Total Scheduled Races</b>", font=dict(color='#1F77B4', size=12)),
        side="left",
        tickfont=dict(color=COLOR_PALETTE['text_dark'], size=11),
        gridcolor=COLOR_PALETTE['grid_line'],
        zeroline=False
    ),
    
    # RIGHT Y-AXIS: Density Gap
    yaxis2=dict(
        title=dict(text="<b>Average Days Gap</b>", font=dict(color='#FF7F0E', size=12)),
        side="right",
        overlaying="y",
        tickfont=dict(color=COLOR_PALETTE['text_dark'], size=11),
        gridcolor="rgba(0,0,0,0)",
        zeroline=False
    ),
    
    # X-AXIS: Years
    xaxis=dict(
        title=dict(text="<b>Championship Year</b>", font=dict(color=COLOR_PALETTE['text_dark'], size=12)),
        tickfont=dict(color=COLOR_PALETTE['text_dark'], size=11),
        gridcolor=COLOR_PALETTE['grid_line'],
        dtick=10
    ),
    
    # LEGEND
    legend=dict(
        x=0.02,
        y=0.98,
        bgcolor="rgba(255, 255, 255, 0.9)",
        bordercolor=COLOR_PALETTE['grid_line'],
        borderwidth=1
    ),
    
    margin=dict(l=80, r=80, t=100, b=80),
    height=600,
    width=1200
)

fig_q13.show()

# SAVE VISUALIZATION 1
fig_q13.write_html("visualization_1_volume_density.html")
print("✅ Saved: visualization_1_volume_density.html")

# %% [markdown]
# # VISUALIZATION 2: CIRCUIT PRESENCE MATRIX HEATMAP
# Shows which classic circuits hosted races across different years
# Pastel Blue = Hosted (YES) | White = Not Hosted (NO)

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
            y="Classic Circuit",
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
        
        # GENERAL LAYOUT
        margin=dict(l=200, r=150, t=100, b=120),  # INCREASED BOTTOM MARGIN FOR ANGLED LABELS
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

    fig_heatmap.show()
    
    # SAVE VISUALIZATION 2
    fig_heatmap.write_html("visualization_2_presence_matrix.html")
    print("✅ Saved: visualization_2_presence_matrix.html")

# %% [markdown]
# # VISUALIZATION 3: DECADAL CALENDAR SHARE ANALYSIS
# Shows the proportion of classic vs modern venues hosting races by decade
# Stacked bar chart showing market share evolution

# %%
# CLASSIFY VENUES
df_merged['venue_type'] = np.where(
    df_merged['circuitId'].isin(classic_cohort_ids),
    'Classic Tracks (1950-1960)',
    'Modern & New Venues'
)

# GROUP BY DECADE
df_merged['decade'] = (df_merged['year'] // 10 * 10).astype(str) + "s"

# AGGREGATE RACE COUNTS
decade_share = df_merged.groupby(['decade', 'venue_type']).size().reset_index(name='race_count')

# CREATE STACKED BAR CHART
fig_share = px.bar(
    decade_share,
    x="decade",
    y="race_count",
    color="venue_type",
    title="Decadal Evolution: Classic vs Modern Circuit Market Share",
    labels={
        "decade": "Decade",
        "race_count": "Number of Races",
        "venue_type": "Circuit Type"
    },
    # PROFESSIONAL COLOR MAPPING
    color_discrete_map={
        'Classic Tracks (1950-1960)': "#610376",     # Bronze for classic
        'Modern & New Venues': '#1F77B4'             # Blue for modern
    },
    category_orders={
        "decade": ["1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]
    }
)

# PROFESSIONAL STYLING
fig_share.update_layout(
    title=dict(
        text="<b>F1 Calendar Evolution: Classic vs Modern Venue Share by Decade</b>",
        font=dict(color=COLOR_PALETTE['text_dark'], size=16, family="Arial, sans-serif"),
        x=0.5,
        xanchor='center'
    ),
    template="plotly_white",
    paper_bgcolor=COLOR_PALETTE['neutral_bg'],
    plot_bgcolor=COLOR_PALETTE['neutral_bg'],
    
    # X-AXIS
    xaxis=dict(
        title=dict(text="<b>Championship Decade</b>", font=dict(color=COLOR_PALETTE['text_dark'], size=12)),
        tickfont=dict(color=COLOR_PALETTE['text_dark'], size=11),
        gridcolor=COLOR_PALETTE['grid_line']
    ),
    
    # Y-AXIS
    yaxis=dict(
        title=dict(text="<b>Number of Races</b>", font=dict(color=COLOR_PALETTE['text_dark'], size=12)),
        tickfont=dict(color=COLOR_PALETTE['text_dark'], size=11),
        gridcolor=COLOR_PALETTE['grid_line'],
        zeroline=False
    ),
    
    # LEGEND
    legend=dict(
        title=dict(text="<b>Circuit Type</b>", font=dict(color=COLOR_PALETTE['text_dark'], size=11)),
        x=0.02,
        y=0.98,
        bgcolor="rgba(255, 255, 255, 0.9)",
        bordercolor=COLOR_PALETTE['grid_line'],
        borderwidth=1,
        font=dict(color=COLOR_PALETTE['text_dark'], size=10)
    ),
    
    # GENERAL LAYOUT
    margin=dict(l=100, r=100, t=120, b=80),
    height=600,
    width=1200,
    barmode="group"  # Side-by-side bars instead of stacked
)

# ENHANCE BAR APPEARANCE
fig_share.update_traces(
    marker=dict(
        line=dict(color=COLOR_PALETTE['text_dark'], width=0.5)
    )
)

fig_share.show()

# SAVE VISUALIZATION 3
fig_share.write_html("visualization_3_calendar_share.html")
print("✅ Saved: visualization_3_calendar_share.html")

# %% 
# COMPLETION MESSAGE
print("\n" + "="*70)
print("✅ ALL VISUALIZATIONS COMPLETE & SAVED")
print("="*70)
print(f"📁 Saved Files:")
print(f"   1. visualization_1_volume_density.html")
print(f"   2. visualization_2_presence_matrix.html")
print(f"   3. visualization_3_calendar_share.html")
print(f"\n💾 Theme: Professional Light Theme with Cream Background")
print(f"🎨 Color Palette: Professional Blue, Red, Bronze, and Earth Tones")
print("="*70)