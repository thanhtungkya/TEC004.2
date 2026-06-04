def remove_duplicates(records):
    seen = set()
    unique = []
    for record in records:
        key = (record.get('title'), record.get('district'), record.get('price'), record.get('area'))
        if key not in seen:
            seen.add(key)
            unique.append(record)
    return unique
