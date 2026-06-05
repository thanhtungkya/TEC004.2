from src.database.db_connection import get_connection


def create_tables() -> None:
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

        conn.commit()
    finally:
        conn.close()
