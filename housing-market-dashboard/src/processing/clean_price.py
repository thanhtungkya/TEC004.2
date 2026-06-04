def clean_price(value):
    try:
        return float(str(value).replace('.', '').replace(',', '.').replace(' triệu', '').replace(' tỷ', '000'))
    except ValueError:
        return 0.0
