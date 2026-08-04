"""
remove_duplicates.py
Record deduplication module for raw scraped housing dataset.

Features:
    - Deduplicates listing records based on title, district, price, and area key tuples
    - Preserves insertion order while eliminating duplicate scraper output entries

Dependencies:
    - None (standard Python library types)

Exports:
    - remove_duplicates(records): Returns list of unique property dictionaries
"""

def remove_duplicates(records):
    """Deduplicates property records while preserving original order.

    Args:
        records: Iterable of record dictionaries.

    Returns:
        List of unique property dictionaries.
    """
    seen = set()
    unique = []
    for record in records:
        key = (record.get('title'), record.get('district'), record.get('price'), record.get('area'))
        if key not in seen:
            seen.add(key)
            unique.append(record)
    return unique

