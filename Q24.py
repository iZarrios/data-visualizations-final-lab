import pandas as pd
import plotly.express as px

results = pd.read_csv("results.csv")
races = pd.read_csv("races.csv")
constructors = pd.read_csv("constructors.csv")

df = results.merge(races[["raceId", "year"]], on="raceId")

df = df.merge(constructors[["constructorId", "name"]], on="constructorId")

df["decade"] = (df["year"] // 10) * 10

agg = (
    df.groupby(["decade", "name"])
    .agg(
        total_entries=("resultId", "count"),
        num_drivers=("driverId", "nunique")
    )
    .reset_index()
)

agg["avg_races_per_driver"] = agg["total_entries"] / agg["num_drivers"]

fig = px.box(
    agg,
    x="decade",
    y="avg_races_per_driver",
    points="all",
    hover_name="name",
    hover_data=["total_entries", "num_drivers"],
    title="Average Races per Driver per Team per Decade",
    labels={
        "decade": "Decade",
        "avg_races_per_driver": "Average Races per Driver"
    }
)

fig.show()
