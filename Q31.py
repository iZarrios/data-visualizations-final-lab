import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

results = pd.read_csv("results.csv")
races = pd.read_csv("races.csv")
drivers = pd.read_csv("drivers.csv")
constructors = pd.read_csv("constructors.csv")

df = results.merge(races[["raceId", "year"]], on="raceId")

wins = df[df["positionOrder"] == 1].copy()

wins["decade"] = (wins["year"] // 10) * 10

driver_wins = wins.merge(drivers[["driverId", "surname"]], on="driverId")

driver_heat = (
    driver_wins.groupby(["surname", "decade"])
    .size()
    .reset_index(name="wins")
)

driver_pivot = driver_heat.pivot(index="surname", columns="decade", values="wins").fillna(0)

driver_pivot = driver_pivot.loc[
    driver_pivot.sum(axis=1).sort_values(ascending=False).index
]

constructor_wins = wins.merge(constructors[["constructorId", "name"]], on="constructorId")

constructor_heat = (
    constructor_wins.groupby(["name", "decade"])
    .size()
    .reset_index(name="wins")
)

constructor_pivot = constructor_heat.pivot(index="name", columns="decade", values="wins").fillna(0)

constructor_pivot = constructor_pivot.loc[
    constructor_pivot.sum(axis=1).sort_values(ascending=False).index
]

fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=("Driver Dominance per Decade", "Constructor Dominance per Decade"),
    horizontal_spacing=0.15
)

fig.add_trace(
    go.Heatmap(
        z=driver_pivot.values,
        x=driver_pivot.columns,
        y=driver_pivot.index,
        colorscale="Reds",
        colorbar=dict(title="Wins", x=0.46)
    ),
    row=1, col=1
)

fig.add_trace(
    go.Heatmap(
        z=constructor_pivot.values,
        x=constructor_pivot.columns,
        y=constructor_pivot.index,
        colorscale="Blues",
        colorbar=dict(title="Wins", x=1.02)
    ),
    row=1, col=2
)

fig.update_yaxes(autorange="reversed", row=1, col=1)
fig.update_yaxes(autorange="reversed", row=1, col=2)

fig.update_layout(
    title="Driver vs Constructor Dominance per Decade",
    height=800,
)

fig.show()
