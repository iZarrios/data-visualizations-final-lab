# Q4.1 — Driver age at race by decade
age_frame = (
    race_results.merge(drivers[["driverId", "dob"]], on="driverId", how="left")
    .merge(races[["raceId", "date"]], on="raceId", how="left", suffixes=("", "_race"))
)
age_frame["age_years"] = (age_frame["date"] - age_frame["dob"]).dt.days / 365.25
age_frame = age_frame.dropna(subset=["age_years"]).query("15 <= age_years <= 55")
age_frame["decade"] = decade_label(age_frame["year"])
age_frame["decade_label"] = age_frame["decade"].astype(str) + "s"

decade_order = (
    age_frame[["decade", "decade_label"]]
    .drop_duplicates()
    .sort_values("decade")["decade_label"]
    .tolist()
)

age_stats = (
    age_frame.groupby("decade_label", as_index=False)["age_years"]
    .agg(min_age="min", median_age="median", max_age="max")
)

# ~27k race entries with points="all" draws one SVG marker each → slow hover/pan.
# Violin uses all data for the shape; a capped sample supplies fast interactive dots.
MAX_HOVER_POINTS_PER_DECADE = 400

fig = go.Figure()
for label in decade_order:
    values = age_frame.loc[age_frame["decade_label"] == label, "age_years"]
    row = age_stats.loc[age_stats["decade_label"] == label].iloc[0]
    color = MODERN_PALETTE[0]
    n_sample = min(MAX_HOVER_POINTS_PER_DECADE, len(values))
    sample_y = values.sample(n=n_sample, random_state=42)

    fig.add_trace(
        go.Violin(
            x=[label] * len(values),
            y=values,
            name=label,
            legendgroup=label,
            scalegroup=label,
            line_color=color,
            fillcolor=color,
            opacity=0.75,
            box_visible=False,
            points=False,
            meanline_visible=True,
            hoverinfo="skip",
        )
    )

    fig.add_trace(
        go.Scattergl(
            x=[label] * n_sample,
            y=sample_y,
            mode="markers",
            name=f"{label} entries",
            legendgroup=label,
            showlegend=False,
            marker={"size": 4, "opacity": 0.4, "color": color},
            hovertemplate=(
                f"<b>{label}</b><br>"
                "Age: %{y:.1f} years<br>"
                f"Min: {row['min_age']:.1f} · Median: {row['median_age']:.1f} · Max: {row['max_age']:.1f}<br>"
                "<extra></extra>"
            ),
        )
    )

fig.update_layout(
    title="Driver age distributions shift across decades",
    template="f1_modern",
    xaxis_title="Decade",
    yaxis_title="Driver age at race (years)",
    hovermode="closest",
    showlegend=False,
    height=520,
    width=950,
)
fig.update_xaxes(categoryorder="array", categoryarray=decade_order)
fig.show()
