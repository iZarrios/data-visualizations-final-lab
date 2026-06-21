"""Shared path constants and small pandas helpers used across visualizations."""

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def decade_label(year: pd.Series) -> pd.Series:
    """Map calendar years to decade start (e.g. 1987 → 1980)."""
    return (year // 10) * 10
