"""
clean_price.py
Data processing utility for parsing Vietnamese real estate price expressions into million VND values.

Features:
    - Parses Vietnamese price terms: "tỷ" (billions) and "triệu" (millions)
    - Supports composite strings (e.g. "5 tỷ 200 triệu" -> 5200.0)
    - Returns float('nan') for negotiation listings ("thỏa thuận", "liên hệ")

Dependencies:
    - re, math: Regular expressions and numeric validation

Exports:
    - clean_price(value): Converts raw price string/number to normalized million VND float
"""

import re
import math



def clean_price(value):
    """
    Parse Vietnamese real-estate price strings into a numeric value
    expressed in **triệu VND** (millions of VND).

    Supported formats
    -----------------
    - "5 tỷ 200 triệu"  → 5200.0
    - "5 tỷ"             → 5000.0
    - "200 triệu"        → 200.0
    - "5.2 tỷ"           → 5200.0
    - "3,500"            → 3500.0   (plain number with comma thousands)
    - 4200               → 4200.0   (already numeric)

    Returns ``float('nan')`` for values that cannot be parsed so that
    Pandas missing-value handling (e.g. ``fillna``, ``dropna``) works
    naturally downstream.
    """
    # Already a number
    if isinstance(value, (int, float)):
        if math.isnan(value) if isinstance(value, float) else False:
            return float('nan')
        return float(value)

    text = str(value).strip().lower()
    if not text or text in ('none', 'nan', 'n/a', 'thỏa thuận', 'liên hệ'):
        return float('nan')

    total = 0.0
    matched = False

    # Pattern: X tỷ (with optional decimal)
    ty_match = re.search(r'([\d]+[.,]?\d*)\s*tỷ', text)
    if ty_match:
        ty_str = ty_match.group(1).replace(',', '.')
        total += float(ty_str) * 1000  # 1 tỷ = 1000 triệu
        matched = True

    # Pattern: X triệu
    trieu_match = re.search(r'([\d]+[.,]?\d*)\s*triệu', text)
    if trieu_match:
        trieu_str = trieu_match.group(1).replace(',', '.')
        total += float(trieu_str)
        matched = True

    if matched:
        return total

    # Fallback: try to extract a plain number
    # Remove dots used as thousand separators, keep comma as decimal
    cleaned = text.replace('.', '').replace(',', '.')
    # Remove any remaining non-numeric characters except dot and minus
    cleaned = re.sub(r'[^\d.\-]', '', cleaned)

    try:
        result = float(cleaned)
        return result if result > 0 else float('nan')
    except (ValueError, TypeError):
        return float('nan')
