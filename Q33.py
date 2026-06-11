# Q3.3 — Pit-stop pace evolution and team strategy edges (2011+)


races = read_csv("races.csv", parse_dates=["date"])
results = read_csv("results.csv")
drivers = read_csv("drivers.csv", parse_dates=["dob"])
constructors = read_csv("constructors.csv")
circuits = read_csv("circuits.csv")
status = read_csv("status.csv")
driver_standings = read_csv("driver_standings.csv")
constructor_standings = read_csv("constructor_standings.csv")
qualifying = read_csv("qualifying.csv")
pit_stops = read_csv("pit_stops.csv")
lap_times = read_csv("lap_times.csv")
sprint_results = read_csv("sprint_results.csv")
seasons = read_csv("seasons.csv")

pit_team = (
    pit_stops
    .merge(races[["raceId", "year", "name"]], on="raceId", how="left")
    .rename(columns={"name": "race_name"})
    .merge(
        results[["raceId", "driverId", "constructorId"]].drop_duplicates(),
        on=["raceId", "driverId"],
        how="left",
    )
    .merge(constructors[["constructorId", "name"]], on="constructorId", how="left")
    .rename(columns={"name": "constructor_name"})
)
pit_team["pit_lane_seconds"] = pit_team["milliseconds"] / 1000
pit_normal = pit_team.query("10 <= pit_lane_seconds <= 60").copy()

fleet_by_year = (
    pit_normal.groupby("year", as_index=False)
    .agg(
        median_pit=("pit_lane_seconds", "median"),
        stops=("pit_lane_seconds", "count"),
    )
)

TOP_PIT_TEAMS = 8
top_pit_teams = (
    pit_normal.groupby("constructor_name", as_index=False)["pit_lane_seconds"]
    .count()
    .sort_values("pit_lane_seconds", ascending=False)
    .head(TOP_PIT_TEAMS)["constructor_name"]
)

team_year_pit = (
    pit_normal[pit_normal["constructor_name"].isin(top_pit_teams)]
    .groupby(["year", "constructor_name"], as_index=False)
    .agg(median_pit=("pit_lane_seconds", "median"), stops=("pit_lane_seconds", "count"))
    .query("stops >= 15")
)
year_median_lookup = fleet_by_year.set_index("year")["median_pit"]
team_year_pit["edge_vs_field"] = (
    team_year_pit["median_pit"] - team_year_pit["year"].map(year_median_lookup)
).round(2)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=fleet_by_year["year"],
        y=fleet_by_year["median_pit"],
        mode="lines+markers",
        name="Field median",
        line={"color": MODERN_TEXT, "width": 3},
        marker={"size": 7},
        customdata=fleet_by_year[["stops"]],
        hovertemplate=(
            "Season %{x}<br>Median: %{y:.2f} s<br>Stops in sample: %{customdata[0]}<extra></extra>"
        ),
    )
)

for i, team in enumerate(top_pit_teams):
    team_line = team_year_pit[team_year_pit["constructor_name"] == team].sort_values("year")
    fig.add_trace(
        go.Scatter(
            x=team_line["year"],
            y=team_line["median_pit"],
            mode="lines+markers",
            name=team,
            line={"color": MODERN_PALETTE[i % len(MODERN_PALETTE)], "width": 1.5},
            marker={"size": 5},
            customdata=np.stack([team_line["edge_vs_field"], team_line["stops"]], axis=-1),
            hovertemplate=(
                f"{team}<br>"
                "Season %{x}<br>"
                "Median: %{y:.2f} s<br>"
                "Vs field: %{customdata[0]:+.2f} s<br>"
                "Stops: %{customdata[1]}<extra></extra>"
            ),
        )
    )

fig.update_layout(
    title="Fleet and team median pit-lane times by season (toggle teams in legend)",
    template="f1_modern",
    height=520,
    width=980,
    margin={"t": 90, "b": 75, "l": 78, "r": 30},
    legend={
        "orientation": "h",
        "yanchor": "bottom",
        "y": -0.28,
        "xanchor": "center",
        "x": 0.5,
        "font": {"size": 10},
        "itemsizing": "constant",
        "tracegroupgap": 8,
    },
    xaxis_title="Season",
    yaxis_title="Median pit-lane time (s)",
)
fig.show()

