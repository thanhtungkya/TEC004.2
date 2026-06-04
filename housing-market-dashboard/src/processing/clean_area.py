def clean_area(value):
    try:
        return float(str(value).replace('m2', '').strip())
    except ValueError:
        return 0.0
