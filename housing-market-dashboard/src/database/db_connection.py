"""
db_connection.py
SQLite database connection factory and row factory setup.

Features:
    - Creates and configures SQLite database connection
    - Sets sqlite3.Row factory for dictionary-like column access

Dependencies:
    - sqlite3: Embedded SQLite database driver
    - src.utils.config.DB_PATH: Database file path location

Exports:
    - get_connection(): Returns configured sqlite3.Connection object
"""

import sqlite3

from src.utils.config import DB_PATH



def get_connection() -> sqlite3.Connection:
    """Establishes and configures SQLite database connection.

    Ensures target parent directory exists, connects to housing_market.db,
    and sets row_factory to sqlite3.Row for dict-like column access.

    Returns:
        sqlite3.Connection: Active database connection handle.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

