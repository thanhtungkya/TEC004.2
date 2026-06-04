import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DB_DIR = DATA_DIR / "database"
DB_PATH = DB_DIR / "housing_market.db"


def ensure_directories() -> None:
    for path in (RAW_DIR, PROCESSED_DIR, DB_DIR):
        path.mkdir(parents=True, exist_ok=True)
