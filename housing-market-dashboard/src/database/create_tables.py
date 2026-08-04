"""
create_tables.py
SQLite database table schema definition and incremental migration runner.

Features:
    - Creates properties table with fields for titles, prices, areas, source URLs, and AI reports
    - Performs safe backward-compatible schema migrations for existing databases

Dependencies:
    - src.database.db_connection.get_connection: Database connection provider

Exports:
    - create_tables(): Initializes and migrates properties table schema
"""

from src.database.db_connection import get_connection



def create_tables() -> None:
    """Initializes SQLite database schema and executes incremental migrations.

    Executes CREATE TABLE IF NOT EXISTS for properties table and checks table PRAGMA
    info to alter and add any missing columns for existing local databases.
    """
    conn = get_connection()

    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                district TEXT,
                address TEXT,
                price REAL,
                price_text TEXT,
                area REAL,
                area_text TEXT,
                property_type TEXT,
                listing_date TEXT,
                source TEXT,
                url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # Keep older local databases working after the schema grows.
        columns = {row[1] for row in conn.execute("PRAGMA table_info(properties)")}
        if "address" not in columns:
            conn.execute("ALTER TABLE properties ADD COLUMN address TEXT")
        if "url" not in columns:
            conn.execute("ALTER TABLE properties ADD COLUMN url TEXT")
        if "price_text" not in columns:
            conn.execute("ALTER TABLE properties ADD COLUMN price_text TEXT")
        if "area_text" not in columns:
            conn.execute("ALTER TABLE properties ADD COLUMN area_text TEXT")
        if "property_type" not in columns:
            conn.execute("ALTER TABLE properties ADD COLUMN property_type TEXT")
        if "listing_date" not in columns:
            conn.execute("ALTER TABLE properties ADD COLUMN listing_date TEXT")
        if "ai_predicted_price" not in columns:
            conn.execute("ALTER TABLE properties ADD COLUMN ai_predicted_price REAL")
        if "ai_valuation_report" not in columns:
            conn.execute("ALTER TABLE properties ADD COLUMN ai_valuation_report TEXT")

        conn.commit()
    finally:
        conn.close()

