# F1 Data Visualization — Final Lab

Unified interactive dashboard combining course visualizations over the [Ergast Formula 1 dataset](https://ergast.com/mrd/).

## Setup

```bash
pip install -r requirements.txt
```

## Run locally

```bash
python app.py
```

Open http://localhost:8050

## Deploy (Render)

1. Push this repo to GitHub.
2. Create a new **Web Service** on [Render](https://render.com) connected to the repo.
3. Render picks up `render.yaml` automatically, or set:
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `gunicorn app:server --bind 0.0.0.0:$PORT`

## Project structure

```
data/              Canonical CSV dataset
src/
  theme.py         Shared cream Plotly theme
  data_loader.py   Cached data loaders
  figures/         One module per visualization
app.py             Dash entry point
```

## Visualizations

- Calendar volume & scheduling density
- Classic circuit presence matrix
- Classic vs modern venue share
- Geographic evolution (interactive decade slider)
- Nationality diversification (Q2.1)
- Regional talent influx (Q2.2)
- Avg races per driver per team (Q2.4)
- Win dominance heatmaps (Q3.1)
- Pit-stop pace evolution (Q3.3)
- Driver age by decade (Q4.1)
