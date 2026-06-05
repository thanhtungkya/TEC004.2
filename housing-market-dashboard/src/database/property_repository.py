from src.database.db_connection import get_connection


class PropertyRepository:
    def insert_many(self, rows):
        normalised_rows = []
        for row in rows:
            if isinstance(row, dict):
                normalised_rows.append((
                    row.get('title'),
                    row.get('district'),
                    row.get('address'),
                    row.get('price'),
                    row.get('area'),
                    row.get('source'),
                    row.get('url'),
                ))
                continue

            values = tuple(row)
            if len(values) == 5:
                title, district, price, area, source = values
                values = (title, district, district, price, area, source, None)
            elif len(values) == 6:
                title, district, price, area, source, url = values
                values = (title, district, district, price, area, source, url)
            normalised_rows.append(values)

        conn = get_connection()
        try:
            conn.executemany(
                """
                INSERT INTO properties (title, district, address, price, area, source, url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                normalised_rows,
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
