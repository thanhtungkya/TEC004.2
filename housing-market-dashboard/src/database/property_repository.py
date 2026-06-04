from src.database.db_connection import get_connection


class PropertyRepository:
    def insert_many(self, rows):
        conn = get_connection()
        try:
            conn.executemany(
                """
                INSERT INTO properties (title, district, price, area, source)
                VALUES (?, ?, ?, ?, ?)
                """,
                rows,
            )
            conn.commit()
        finally:
            conn.close()

    def fetch_all(self):
        conn = get_connection()
        try:
            return conn.execute("SELECT * FROM properties ORDER BY id DESC").fetchall()
        finally:
            conn.close()
