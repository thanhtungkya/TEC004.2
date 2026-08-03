import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import unittest
from src.services.cma_valuation_service import CMAValuationEngine

class TestCMAValuationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = CMAValuationEngine()
        self.sample_records = [
            {"id": 1, "title": "Căn hộ A", "district": "Cầu Giấy", "property_type": "Căn hộ", "price": 4500, "area": 75, "source": "alonhadat"},
            {"id": 2, "title": "Căn hộ B", "district": "Cầu Giấy", "property_type": "Căn hộ", "price": 4800, "area": 80, "source": "homedy"},
            {"id": 3, "title": "Căn hộ C", "district": "Cầu Giấy", "property_type": "Căn hộ", "price": 4200, "area": 70, "source": "nhadat24h"},
            {"id": 4, "title": "Căn hộ D (Virtual Outlier)", "district": "Cầu Giấy", "property_type": "Căn hộ", "price": 25000, "area": 30, "source": "batdongsan"},
            {"id": 5, "title": "Nhà riêng E", "district": "Nam Từ Liêm", "property_type": "Nhà riêng", "price": 8500, "area": 60, "source": "mogi"},
        ]

    def test_prepare_market_dataset(self):
        df = self.engine.prepare_market_dataset(self.sample_records)
        self.assertFalse(df.empty)
        self.assertIn("price_per_m2", df.columns)
        self.assertIn("segment_outlier", df.columns)
        
        # Check that high price/m2 outlier (ID 4: 25000/30 = 833.3) was flagged
        outlier_rows = df[df["id"] == 4]
        if not outlier_rows.empty:
            self.assertTrue(outlier_rows.iloc[0]["segment_outlier"])

    def test_find_comparable_properties(self):
        df = self.engine.prepare_market_dataset(self.sample_records)
        target = {"id": 1, "district": "Cầu Giấy", "property_type": "Căn hộ", "area": 75, "price": 4500}
        comps = self.engine.find_comparable_properties(target, df, top_n=3)
        self.assertTrue(len(comps) > 0)
        self.assertEqual(comps[0]["district"], "Cầu Giấy")
        self.assertNotEqual(comps[0]["id"], 1)  # Target excluded

    def test_calculate_district_index(self):
        df = self.engine.prepare_market_dataset(self.sample_records)
        index_data = self.engine.calculate_district_index(df, "Cầu Giấy", "Căn hộ")
        self.assertEqual(index_data["district"], "Cầu Giấy")
        self.assertGreater(index_data["median_price_per_m2"], 0)
        self.assertIn("market_temperature", index_data)

    def test_analyze_property_valuation(self):
        df = self.engine.prepare_market_dataset(self.sample_records)
        target = {"id": 1, "title": "Căn hộ A", "district": "Cầu Giấy", "property_type": "Căn hộ", "price": 4500, "area": 75}
        report = self.engine.analyze_property_valuation(target, df)
        
        self.assertIn("valuation", report)
        self.assertIn("fair_price_billion", report["valuation"])
        self.assertIn("price_position", report["valuation"])
        self.assertIn("comparables", report)
        self.assertIn("district_index", report)
        self.assertIn("recommendations", report)

if __name__ == "__main__":
    unittest.main()
