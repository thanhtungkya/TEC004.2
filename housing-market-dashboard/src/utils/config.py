"""
config.py
Centralized directory paths and database file configuration.

Features:
    - Defines base paths for raw data, processed datasets, and SQLite DB
    - Ensures automatic creation of necessary system data directories

Dependencies:
    - pathlib.Path: System path resolution

Exports:
    - BASE_DIR, DATA_DIR, RAW_DIR, PROCESSED_DIR, DB_DIR, DB_PATH
    - ensure_directories(): Creates missing data directories
"""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DB_DIR = DATA_DIR / "database"
DB_PATH = DB_DIR / "housing_market.db"


def ensure_directories() -> None:
    """Ensures all required system directories exist on the filesystem.

    Creates RAW_DIR, PROCESSED_DIR, and DB_DIR if they do not exist.
    """
    for path in (RAW_DIR, PROCESSED_DIR, DB_DIR):
        path.mkdir(parents=True, exist_ok=True)

