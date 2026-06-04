import importlib.util
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent / "housing-market-dashboard"
APP_FILE = PROJECT_DIR / "app.py"

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

spec = importlib.util.spec_from_file_location("dashboard_app", APP_FILE)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load Flask app from {APP_FILE}")

module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

app = module.app

__all__ = ["app"]
