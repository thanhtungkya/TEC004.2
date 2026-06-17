import re

tests = [
    "58m", # unsafe
    "Bán Nhà Chính Chủ Mặt Phố Tạ Hiện Hoàn Kiếm 58m Ô Tô Kinh Doanh", # Wait, no prefix! How to catch this?
    "DT:70Mx5T",
    "50m2",
    "35m2",
    "Bán nhà Xuân Thủy – Cầu Giấy 53m2 – MT5m – 5 Tầng",
    "Bán nhà Nguyễn Chính Hoàng Mai, 50m2, 5T, MT 3.9m",
    "150 m²",
    "Diện tích 65.5m",
    "Cách ô tô 50m"
]

def extract(text):
    def _parse(s):
        s = s.strip().replace(',', '.')
        parts = s.split('.')
        if len(parts) == 2 and len(parts[1]) == 3: return float(parts[0]+parts[1])
        return float(s)
        
    # 1. Standard m2 or m²
    m1 = re.search(r'(?<!\d)(\d{1,5}(?:[.,]\d{1,2})?)\s*(?:m2|m²)(?!\w)', text, flags=re.I)
    if m1: return _parse(m1.group(1))
    
    # 2. Prefix DT, Diện tích, S
    m2 = re.search(r'(?:diện tích|dtich|dt|s)\s*:?\s*(\d{1,5}(?:[.,]\d{1,2})?)\s*m?(?!\w)', text, flags=re.I)
    if m2: return _parse(m2.group(1))
    
    # 3. Multiplier like 70Mx5T
    m3 = re.search(r'(?<!\d)(\d{1,5}(?:[.,]\d{1,2})?)\s*m\s*[x\*]\s*\d+\s*(?:T|tầng)', text, flags=re.I)
    if m3: return _parse(m3.group(1))
    
    # 4. Dangerous fallback: catch isolated \d+m if it's reasonably large (>= 20) and not preceded by 'cách', 'mặt tiền', 'mt', 'đường', 'ngõ'
    m4 = re.search(r'(?<!\d)(\d{2,5}(?:[.,]\d{1,2})?)\s*m\b', text, flags=re.I)
    if m4:
        val = _parse(m4.group(1))
        idx = m4.start()
        context_before = text[max(0, idx-15):idx].lower()
        if not any(w in context_before for w in ['mt', 'tiền', 'ngõ', 'đường', 'cách', 'rộng', 'sâu']):
            if 15 <= val <= 10000:
                return val

    return 0.0

with open('scratch_area_out.txt', 'w', encoding='utf-8') as f:
    for t in tests:
        f.write(f"{t[:40]:<40} -> {extract(t)}\n")
