# F1 Data Visualization — Final Lab

Interactive Dash dashboard exploring 74 years of Formula 1 history (1950–2024), built with Plotly and the [Formula 1 World Championship dataset on Kaggle](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020) (`data/`).

**Course:** INF8808E (E2026) — Data Visualization Lab · **Team 3**

## Requirements

- Python **3.13+**
- [uv](https://docs.astral.sh/uv/) for dependency management (`pyproject.toml` / `uv.lock`)

## Run locally

```bash
cd data-viz-final-lab
uv sync
uv run python app.py
```

Open **http://localhost:8050** in your browser. Press `Ctrl+C` to stop the server.

## Production

```bash
uv run gunicorn app:server --bind 0.0.0.0:$PORT
```

Set `PORT` to the port your host expects (e.g. `8050`). The WSGI entry point is `server` in `app.py`.

## Data

CSV files in `data/` come from the [Formula 1 World Championship (1950–2020) Kaggle dataset](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020) by Rohan Rao. The files are derived from the Ergast API and include races, results, drivers, constructors, circuits, and pit stops.

## Project structure

```
data/                 F1 championship CSV files (Kaggle dataset)
src/
  theme.py            Shared cream Plotly theme and color palette
  data_loader.py      Cached CSV loaders
  utils.py            Shared helpers (paths, decade bucketing)
  figures/            One module per visualization
    calendar_volume.py
    circuit_presence.py
    geographic_cog.py
    venue_share.py
    viz8_nationalities.py
    viz9_regions.py
    q24_team_races.py
    q31_dominance.py
    q33_pit_stops.py
    q41_driver_age.py
static/css/styles.css Custom dashboard styling
app.py                Dash entry point
pyproject.toml        Dependencies and project metadata
uv.lock               Locked dependency versions
```

## Dashboard sections

| Section | Visualizations |
|---------|----------------|
| **Calendar & Circuits** | Championship volume & scheduling density · Classic circuit presence matrix · Classic vs modern venue share |
| **Geographic Evolution** | Regional race distribution · Spherical center of gravity (interactive decade slider) |
| **Nationality & Talent** | Driver vs constructor nationality diversification (Q2.1) · Regional talent influx (Q2.2) |
| **Competition Dynamics** | Avg races per driver per team (Q2.4) · Win dominance heatmaps (Q3.1) |
| **Performance & Demographics** | Pit-stop pace evolution (Q3.3) · Driver age by decade (Q4.1) |
