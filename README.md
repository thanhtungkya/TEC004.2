# Hanoi Housing Market Dashboard

Python/Flask application for collecting, cleaning, storing, analyzing, and visualizing Hanoi real-estate listings.

## What it does

- Scrapes listing data from supported Vietnamese real-estate sites.
- Cleans prices, areas, districts, dates, and duplicate records.
- Stores records in SQLite.
- Serves dashboard, property list, analytics, database, data-collection, reports, and settings pages.
- Exports property and analytics data as CSV or JSON.
- Optionally predicts fair market prices through OpenAI when `OPENAI_API_KEY` is configured.

## Repository layout

```text
TEC004.2/
├── app.py                         # Root WSGI entrypoint for deployment
├── requirements.txt               # Python dependencies
├── render.yaml                    # Render deployment config
├── DEPLOYMENT.md                  # Full deployment guide
├── QUICK_DEPLOY.md                # Short deployment guide
└── housing-market-dashboard/
    ├── app.py                     # Main Flask app and HTTP routes
    ├── init_database.py           # Standalone SQLite initialization script
    ├── data/database/             # Local SQLite database location
    ├── templates/                 # Flask HTML templates
    ├── static/css, static/js      # Frontend assets
    ├── src/
    │   ├── analytics/             # Market and district analysis
    │   ├── database/              # SQLite connection, schema, repository
    │   ├── models/                # Property model classes
    │   ├── processing/            # Cleaning and transformation pipeline
    │   ├── scraper/               # Source-specific scrapers and manager
    │   ├── services/              # OpenAI integration
    │   └── utils/                 # Config and logging helpers
    └── tests/                     # Pytest tests
```

## Runtime architecture

1. `app.py` at the repository root loads `housing-market-dashboard/app.py` and exposes `app` for Gunicorn.
2. The Flask app calls `create_tables()` on import, so the SQLite schema is created automatically.
3. Pages and APIs read data through `PropertyRepository`.
4. Scraping runs through `src.scraper.scraper_manager.run_all_scrapers()` and writes normalized records to SQLite.
5. Dashboard and analytics routes transform records with `DataCleaner` and analysis helpers.
6. Optional AI prediction calls `src.services.openai_service.predict_prices()`.

## Requirements

- Python 3.11 or 3.12
- SQLite, included with Python
- Browser/scraper dependencies from `requirements.txt`
- Optional: `OPENAI_API_KEY` for AI price prediction

## Local setup

Windows PowerShell:

```powershell
cd C:\Users\Duy\Documents\GitHub\TEC004.2
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install
python housing-market-dashboard\init_database.py
python app.py
```

macOS/Linux:

```bash
cd TEC004.2
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install
python housing-market-dashboard/init_database.py
python app.py
```

Open:

```text
http://127.0.0.1:5001
```

Alternative Flask command:

```bash
flask --app app run --host 127.0.0.1 --port 5001
```

## Configuration

Environment variables:

| Variable | Required | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | No | Enables `/api/analyze-prices` AI prediction. |
| `FLASK_ENV` | No | Set to `production` in deployment. |
| `PORT` | Deployment | Used by Render/Gunicorn bind command. |

Local `.env` example:

```env
OPENAI_API_KEY=your_api_key_here
```

## Database

Default database path:

```text
housing-market-dashboard/data/database/housing_market.db
```

Main table:

```sql
properties (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT,
  district TEXT,
  address TEXT,
  price REAL,
  price_text TEXT,
  area REAL,
  area_text TEXT,
  property_type TEXT,
  listing_date TEXT,
  source TEXT,
  url TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  ai_predicted_price REAL
)
```

Initialize manually:

```bash
python housing-market-dashboard/init_database.py
```

## Main pages

| Route | Purpose |
| --- | --- |
| `/` | Redirects automatically to `/dashboard` |
| `/dashboard` | Summary metrics and charts |
| `/properties` | Searchable property records |
| `/analytics` | Market and district analysis |
| `/data-collection` | Scraper controls and status |
| `/database` | Database import/export tools |
| `/settings` | App settings page |

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/collect` | Start collection workflow |
| `POST` | `/api/run-scraper` | Run selected scrapers |
| `GET` | `/api/scraper-status` | Read scraper progress and logs |
| `POST` | `/api/stop-scraper` | Stop active scraping job |
| `POST` | `/api/clean-data` | Clean submitted records |
| `POST` | `/api/analyze-prices` | Generate AI price predictions |
| `GET` | `/api/summary` | Return summary metrics |
| `GET` | `/api/analysis` | Return market analysis |
| `GET` | `/api/district-stats` | Return district statistics |
| `GET` | `/properties/export.csv` | Export property list as CSV |
| `GET` | `/analytics/export.csv` | Export analytics as CSV |
| `GET` | `/database/export.csv` | Export database as CSV |
| `GET` | `/database/export.json` | Export database as JSON |
| `POST` | `/database/import.csv` | Import CSV records |
| `POST` | `/database/import.json` | Import JSON records |

## Supported scraper sources

Configured in `housing-market-dashboard/src/scraper/scraper_manager.py`:

- `alonhadat`
- `homedy`
- `nhadat24h`
- `batdongsan`
- `mogi`
- `nhatot`
- `sosanhnha`
- `bds123`
- `nhaongay`
- `meeyland`
- `123nhadatviet`

## Data-cleaning pipeline

`DataCleaner.clean()` runs these steps:

1. Convert input records to a Pandas DataFrame.
2. Parse price values into numeric `price` values.
3. Parse area values into numeric `area` values.
4. Fill missing numeric values with `0.0`.
5. Fill missing text fields with `Unknown`, except `url` with an empty string.
6. Remove duplicate listings by `title`, `district`, `price`, and `area`.
7. Flag price and area outliers using IQR.
8. Compute derived columns such as price per square meter, month, and year.

## Tests

Run the test suite:

```bash
pytest housing-market-dashboard/tests
```

## Deployment on Render

This repository includes `render.yaml`:

```yaml
startCommand: gunicorn --workers 2 --worker-class sync --timeout 30 --bind 0.0.0.0:$PORT app:app
buildCommand: pip install -r requirements.txt
```

Steps:

1. Push the repository to GitHub.
2. Create a Render web service from the repository.
3. Use the included `render.yaml` or set the same build/start commands manually.
4. Add `OPENAI_API_KEY` only if AI prediction is needed.

See `QUICK_DEPLOY.md` and `DEPLOYMENT.md` for deployment walkthroughs.

## Cloudflare Tunnel for local sharing

```bash
cloudflared tunnel --url http://127.0.0.1:5001
```

Share the generated `trycloudflare.com` URL.

## Notes

- Scrapers depend on external websites, so selectors and anti-bot behavior can break collection.
- SQLite is enough for local/demo use. Move to PostgreSQL when multiple users need concurrent writes or persistent cloud storage.
- `requirements.txt` currently includes both scraper stacks and dashboard dependencies; install time can be large.
