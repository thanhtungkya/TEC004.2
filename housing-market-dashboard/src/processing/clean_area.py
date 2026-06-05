import re
import math


def clean_area(value):
    """
    Parse an area string into a float representing square metres.

    Handles common suffixes: ``m2``, ``m²``, ``m 2``, as well as plain
    numbers. Returns ``float('nan')`` for values that cannot be parsed.
    """
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return float('nan')
        return float(value) if value > 0 else float('nan')

    text = str(value).strip().lower()
    if not text or text in ('none', 'nan', 'n/a'):
        return float('nan')

    # Remove area suffixes
    text = re.sub(r'\s*m[²2]\s*', '', text)
    text = text.replace(',', '.')

    # Extract the first number found
    match = re.search(r'[\d]+\.?\d*', text)
    if match:
        try:
            result = float(match.group())
            return result if result > 0 else float('nan')
        except ValueError:
            return float('nan')

    return float('nan')
