import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import unittest
from unittest.mock import patch
import json
from app import app

class TestAppRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_ai_settings_get(self):
        response = self.client.get("/api/settings/ai")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "ok")
        self.assertIn("config", data)

    @patch("app.save_ai_config")
    @patch("app.get_ai_config")
    def test_ai_settings_post(self, mock_get, mock_save):
        mock_save.return_value = True
        mock_get.return_value = {
            "provider": "gemini",
            "api_key": "AIzaSy...",
            "model": "gemini-1.5-flash",
            "custom_endpoint": "",
            "has_key": True
        }
        payload = {
            "provider": "gemini",
            "api_key": "AIzaSyTest123",
            "model": "gemini-1.5-flash",
            "custom_endpoint": ""
        }
        response = self.client.post("/api/settings/ai", json=payload)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["config"]["provider"], "gemini")

if __name__ == "__main__":
    unittest.main()
