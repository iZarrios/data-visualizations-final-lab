"""Cached loaders for dataset."""

from functools import lru_cache

import pandas as pd

from src.utils import DATA_DIR


@lru_cache(maxsize=1)
def load_races() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "races.csv", parse_dates=["date"])
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    return df


@lru_cache(maxsize=1)
def load_results() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "results.csv")


@lru_cache(maxsize=1)
def load_drivers() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "drivers.csv", parse_dates=["dob"])


@lru_cache(maxsize=1)
def load_constructors() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "constructors.csv")


@lru_cache(maxsize=1)
def load_circuits() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "circuits.csv")


@lru_cache(maxsize=1)
def load_pit_stops() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "pit_stops.csv")


@lru_cache(maxsize=1)
def race_results() -> pd.DataFrame:
    return load_results().merge(
        load_races()[["raceId", "year", "date", "name"]],
        on="raceId",
        how="left",
    )
