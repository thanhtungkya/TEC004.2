import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import unittest
import os
import json
from src.utils.env_utils import save_ai_config, get_ai_config, ENV_FILE
from src.services.openai_service import _build_prompt

class TestAISettings(unittest.TestCase):
    def test_save_and_get_ai_config(self):
        # Save custom provider config
        success = save_ai_config("custom", "sk-test12345678", "llama3", "https://api.custom.com/v1")
        self.assertTrue(success)

        # Retrieve config
        cfg = get_ai_config()
        self.assertEqual(cfg["provider"], "custom")
        self.assertEqual(cfg["model"], "llama3")
        self.assertEqual(cfg["custom_endpoint"], "https://api.custom.com/v1")
        self.assertTrue(cfg["has_key"])

    def test_build_prompt(self):
        sample_props = [
            {"id": 1, "district": "Quận 1", "area": 50, "property_type": "Căn hộ", "price": 3500}
        ]
        prompt = _build_prompt(sample_props)
        self.assertIn("Quận 1", prompt)
        self.assertIn("3500", prompt)

if __name__ == "__main__":
    unittest.main()
