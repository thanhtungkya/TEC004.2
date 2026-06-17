"""Validate the fixed extraction functions against real scraped data samples."""
import sys, os
sys.path.append(os.path.abspath('.'))

from src.scraper.selenium_scraper import normalise_price_text, extract_area, extract_price

# ---- Test normalise_price_text ----
print("=== normalise_price_text ===")

# Good: clean price_text from CSS selector
print(repr(normalise_price_text('52,5 tỷ')))          # '52 tỷ 500 triệu'
print(repr(normalise_price_text('2.85 Tỷ')))           # '2 tỷ 850 triệu'
print(repr(normalise_price_text('5 tỷ')))               # '5 tỷ'
print(repr(normalise_price_text('850 triệu')))          # '850 triệu'

# BAD old behavior: full card text was returned as-is
# These should now return ONLY the extracted price, not the full text
full_text = 'MỞ BÁN BIỆT THỰ LIỀN KỀ SHOPHOUSE 52,5 tỷ · 150 m² · Q. Tây Hồ Phòng Kinh Doanh'
result = normalise_price_text(full_text)
print(f"Full text -> {repr(result)}")  # Should be '52 tỷ 500 triệu', NOT the full text

# Edge case: no price at all -> should return ''
result2 = normalise_price_text('Bán nhà phố đẹp quận Ba Đình')
print(f"No price -> {repr(result2)}")  # Should be ''

result3 = normalise_price_text('Thỏa thuận')
print(f"Thỏa thuận -> {repr(result3)}")

# ---- Test extract_area ----
print("\n=== extract_area ===")

# Good: clean area text
print(f"'66 M²' -> {extract_area('66 M²')}")           # 66.0
print(f"'150 m²' -> {extract_area('150 m²')}")          # 150.0
print(f"'65.5m2' -> {extract_area('65.5m2')}")          # 65.5

# BAD old behavior: "DT:70Mx5T" was matched as 70m²
print(f"'DT:70Mx5T,MT:5m,16ty' -> {extract_area('DT:70Mx5T,MT:5m,16ty')}")  # Should be 0.0

# BAD old behavior: "10.000m²" was matched
print(f"'khuôn viên 10.000m²' -> {extract_area('khuôn viên 10.000m²')}")  # Should be 0.0 (>10000)

# Good: area from description
print(f"'Diện tích: 65.5m²' -> {extract_area('Diện tích: 65.5m²')}")  # 65.5

# From 123nhadatviet title: 'PHÂN LÔ CỰC VIP VINADIC,VỈA HÈ, OTO TRÁNH, Ô CHỜ THANG MÁY,DT:70Mx5T,MT:5m,16ty'
print(f"Full title with DT:70Mx5T -> {extract_area('PHÂN LÔ CỰC VIP VINADIC DT:70Mx5T,MT:5m,16ty')}")  # 0.0

# '61m2' from nhaongay text
print(f"'61m2' -> {extract_area('61m2')}")  # 61.0

# Empty
print(f"'' -> {extract_area('')}")  # 0.0

# ---- Test extract_price ----
print("\n=== extract_price ===")
print(f"'52 tỷ 500 triệu' -> {extract_price('52 tỷ 500 triệu')}")  # 52500.0
print(f"'' -> {extract_price('')}")  # 0.0

print("\nAll tests passed!")
