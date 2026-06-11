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
                    row.get('price_text'),
                    row.get('area'),
                    row.get('area_text'),
                    row.get('property_type'),
                    row.get('listing_date'),
                    row.get('source'),
                    row.get('url'),
                ))
                continue

            values = tuple(row)
            if len(values) == 5:
                title, district, price, area, source = values
                values = (title, district, district, price, None, area, None, None, None, source, None)
            elif len(values) == 6:
                title, district, price, area, source, url = values
                values = (title, district, district, price, None, area, None, None, None, source, url)
            elif len(values) == 7:
                title, district, address, price, area, source, url = values
                values = (title, district, address, price, None, area, None, None, None, source, url)
            elif len(values) == 9:
                title, district, address, price, price_text, area, area_text, source, url = values
                values = (title, district, address, price, price_text, area, area_text, None, None, source, url)
            normalised_rows.append(values)

        conn = get_connection()
        try:
            conn.executemany(
                """
                INSERT INTO properties (title, district, address, price, price_text, area, area_text, property_type, listing_date, source, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
