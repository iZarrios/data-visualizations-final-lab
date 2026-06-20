# F1 Data Visualization — Final Lab

Interactive Dash dashboard of Formula 1 analytics built with Plotly, using the [Ergast F1 dataset](https://ergast.com/mrd/) (`data/`).

## Requirements

- Python **3.13+**
- Dependencies: `pandas`, `plotly`, `dash`, `gunicorn` (see `requirements.txt`)

## Run locally

### Option A — uv (recommended)

```bash
cd data-visualizations-final-lab
uv sync
uv run python app.py
```

### Option B — pip

```bash
cd data-viz-final-lab
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open **http://localhost:8050** in your browser.

Press `Ctrl+C` in the terminal to stop the server.

## Deploy (Render)

1. Push this repo to GitHub.
2. Create a **Web Service** on [Render](https://render.com) linked to the repo.
3. Render uses `render.yaml` automatically. Manual settings:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:server --bind 0.0.0.0:$PORT`

## Project structure

```
data/              Ergast CSV files
src/
  theme.py         Shared cream Plotly theme
  data_loader.py   Cached data loaders
  figures/         One module per visualization
app.py             Dash entry point
requirements.txt
render.yaml        Render deployment config
```

## Dashboard contents

- Calendar volume & scheduling density
- Classic circuit presence matrix
- Classic vs modern venue share
- Geographic evolution (decade slider)
- Nationality diversification (Q2.1)
- Regional talent influx (Q2.2)
- Avg races per driver per team (Q2.4)
- Win dominance heatmaps (Q3.1)
- Pit-stop pace evolution (Q3.3)
- Driver age by decade (Q4.1)
