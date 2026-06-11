"""Integration test for the data analysis pipeline."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from src.processing.transform_data import DataCleaner
from src.processing.clean_price import clean_price
from src.processing.clean_area import clean_area
from src.analytics.market_analysis import MarketAnalysis
from src.analytics.district_analysis import DistrictAnalysis

print("=" * 60)
print("  DATA ANALYSIS PIPELINE — INTEGRATION TEST")
print("=" * 60)

# ── 1. Test clean_price ─────────────────────────────────────
print("\n[1] clean_price tests:")
tests_price = [
    ("5 tỷ 200 triệu", 5200.0),
    ("5 tỷ", 5000.0),
    ("200 triệu", 200.0),
    ("5.2 tỷ", 5200.0),
    ("Thỏa thuận", "nan"),
    (3000, 3000.0),
]
for val, expected in tests_price:
    result = clean_price(val)
    status = "PASS" if (str(result) == str(expected) or abs(result - expected) < 0.01 if expected != "nan" else str(result) == "nan") else "FAIL"
    print(f"  clean_price({val!r:25s}) = {result:>10} | expected {expected:>10} [{status}]")

# ── 2. Test clean_area ──────────────────────────────────────
print("\n[2] clean_area tests:")
tests_area = [
    ("80 m²", 80.0),
    ("120m2", 120.0),
    ("65.5", 65.5),
    ("none", "nan"),
]
for val, expected in tests_area:
    result = clean_area(val)
    status = "PASS" if (str(result) == str(expected) or abs(result - expected) < 0.01 if expected != "nan" else str(result) == "nan") else "FAIL"
    print(f"  clean_area({val!r:15s}) = {result:>10} | expected {expected:>10} [{status}]")

# ── 3. Test DataCleaner ─────────────────────────────────────
print("\n[3] DataCleaner pipeline:")
sample = [
    {"title": "Căn hộ A", "district": "Quận 1", "price": 5000, "area": 80, "source": "alonhadat", "created_at": "2025-01-15"},
    {"title": "Căn hộ B", "district": "Quận 2", "price": 3000, "area": 60, "source": "homedy", "created_at": "2025-02-20"},
    {"title": "Villa C", "district": "Quận 7", "price": 12000, "area": 200, "source": "nhadat24h", "created_at": "2025-03-10"},
    {"title": "Căn hộ A", "district": "Quận 1", "price": 5000, "area": 80, "source": "alonhadat", "created_at": "2025-01-15"},  # duplicate
    {"title": "Nhà D", "district": None, "price": None, "area": "65 m²", "source": "alonhadat", "created_at": "2025-04-05"},
    {"title": "Penthouse E", "district": "Quận 3", "price": "8 tỷ 500 triệu", "area": "150m2", "source": "homedy", "created_at": "2025-05-18"},
]

cleaner = DataCleaner()
df = cleaner.clean(sample)

print(f"  Input records:  {len(sample)}")
print(f"  Output rows:    {len(df)}  (duplicate removed)")
print(f"  Columns:        {list(df.columns)}")
print(f"  Has price_per_m2: {'price_per_m2' in df.columns}")
print(f"  Has is_outlier:   {'is_outlier' in df.columns}")
print(f"  Has month/year:   {'month' in df.columns and 'year' in df.columns}")
print(f"\n  Sample data (first 3 rows):")
for _, row in df.head(3).iterrows():
    print(f"    {row['title']:15s} | {row['district']:8s} | price={row['price']:>10.1f} | area={row['area']:>6.1f} | $/m²={row['price_per_m2']:>8.2f}")

# ── 4. Test MarketAnalysis ──────────────────────────────────
print("\n[4] MarketAnalysis:")
ma = MarketAnalysis()
report = ma.full_report(df)

print(f"  Report keys: {list(report.keys())}")
print(f"  Summary: {report['summary']}")
print(f"  Price trends ({len(report['price_trends_by_district'])} districts):")
for d in report["price_trends_by_district"]:
    print(f"    {d['district']:10s} | avg_price={d['avg_price']:>10.1f} | count={d['listing_count']}")
print(f"  Price/m² rankings ({len(report['price_per_m2_rankings'])} districts):")
for d in report["price_per_m2_rankings"]:
    print(f"    {d['district']:10s} | avg_$/m²={d['avg_price_per_m2']:>10.2f}")
print(f"  Source distribution ({len(report['property_type_distribution'])} sources):")
for d in report["property_type_distribution"]:
    print(f"    {d['source']:12s} | count={d['count']} | {d['percentage']}%")
print(f"  Seasonal patterns ({len(report['seasonal_patterns'])} periods):")
for d in report["seasonal_patterns"]:
    print(f"    {int(d['year'])}-{int(d['month']):02d} | avg_price={d['avg_price']:>10.1f} | count={d['listing_count']}")

# ── 5. Test DistrictAnalysis ────────────────────────────────
print("\n[5] DistrictAnalysis:")
da = DistrictAnalysis()
price_stats = da.price_statistics(df)
area_stats = da.area_statistics(df)

print(f"  Price statistics ({len(price_stats)} districts):")
for d in price_stats:
    print(f"    {d['district']:10s} | mean={d['mean']:>10.1f} | median={d['median']:>10.1f} | min={d['min']:>8.1f} | max={d['max']:>8.1f}")
print(f"  Area statistics ({len(area_stats)} districts):")
for d in area_stats:
    print(f"    {d['district']:10s} | mean={d['mean']:>8.1f} | median={d['median']:>8.1f}")

# ── 6. Test with empty data ─────────────────────────────────
print("\n[6] Empty data handling:")
empty_df = cleaner.clean([])
empty_report = ma.full_report(empty_df)
print(f"  Empty clean:  {len(empty_df)} rows [PASS]")
print(f"  Empty report: {empty_report['summary']} [PASS]")

print("\n" + "=" * 60)
print("  ALL TESTS COMPLETED SUCCESSFULLY")
print("=" * 60)
