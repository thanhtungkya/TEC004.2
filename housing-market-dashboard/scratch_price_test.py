import re

texts = [
    "2,59 tỷ 70 triệu/m² 37 m²",
    "Giá: 257 triệu/m2",
    "70 triệu / m2",
    "8 tỷ 250 triệu",
    "52 tỷ 500 triệu",
]

for text in texts:
    match = re.search(r'(\d+(?:[\s.,]\d+)*)\s*(tỷ|ty|triệu|tr)\b(?!\s*(?:/|trên)?\s*m)', text, flags=re.I)
    if match:
        print(f"'{text}' -> {match.group(0)}")
    else:
        print(f"'{text}' -> NO MATCH")
