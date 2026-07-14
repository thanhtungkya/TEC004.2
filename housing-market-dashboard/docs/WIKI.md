# Hanoi Housing Market Dashboard Wiki

## 1. Project Overview

Hanoi Housing Market Dashboard is a Flask web application for collecting, cleaning, storing, analyzing, and visualizing Hanoi real-estate listings.

The current app entry point is `/`, which redirects to `/dashboard`.

Core capabilities:

- Scrape public housing listing sources.
- Normalize price, area, district, address, property type, source, and URL.
- Store listings in SQLite.
- Display dashboard charts with Chart.js.
- Search/filter property listings.
- Import/export database records as CSV or JSON.
- Run market analytics and export insight CSV.
- Optional OpenAI-powered price prediction.
- Persist light/dark UI theme in the browser.

## 2. Tech Stack

| Layer | Technology |
|---|---|
| Web framework | Flask |
| Templates | Jinja HTML |
| Styling | Custom CSS tokens, light/dark theme |
| Charts | Chart.js |
| Scraping | SeleniumBase, site-specific scraper modules |
| Data processing | pandas, NumPy |
| Storage | SQLite |
| AI service | OpenAI API via `src/services/openai_service.py` |
| Tests | pytest |

## 3. Runtime Entry Points

Main file:

```text
app.py
```

Important routes:

| Method | Route | Purpose |
|---|---|---|
| GET | `/` | Redirects to `/dashboard` |
| GET | `/dashboard` | Main analytics dashboard |
| GET | `/properties` | Search/filter listings table |
| GET | `/properties/export.csv` | Export filtered properties |
| GET | `/data-collection` | Scraping control UI |
| POST | `/api/run-scraper` | Start async scraper thread |
| GET | `/api/scraper-status` | Poll scraper progress/logs |
| POST | `/api/stop-scraper` | Signal scraper abort |
| GET | `/database` | DB stats, preview, import/export UI |
| POST | `/database/import.csv` | Import records from CSV |
| POST | `/database/import.json` | Import records from JSON |
| GET | `/database/export.csv` | Export DB as CSV |
| GET | `/database/export.json` | Export DB as JSON |
| GET | `/analytics` | Advanced analytics page |
| GET | `/analytics/export.csv` | Export analytics summary |
| GET | `/settings` | Appearance / theme settings |
| POST | `/api/analyze-prices` | Run OpenAI price predictions |
| GET | `/api/summary` | Dashboard summary JSON |
| GET | `/api/analysis` | Full analysis JSON |
| GET | `/api/district-stats` | District stats JSON |

## 4. Directory Map

```text
housing-market-dashboard/
├─ app.py                         # Flask routes and app orchestration
├─ requirements.txt               # Python dependencies
├─ data/database/housing_market.db # SQLite database
├─ templates/                     # Jinja pages
│  ├─ dashboard.html
│  ├─ properties.html
│  ├─ data_collection.html
│  ├─ database.html
│  ├─ analytics.html
│  └─ settings.html
├─ static/
│  ├─ css/style.css               # UI tokens, layout, brand, charts
│  └─ js/
│     ├─ collection.js            # Scraper UI polling/actions
│     └─ theme.js                 # Light/dark theme persistence
├─ src/
│  ├─ scraper/                    # SeleniumBase scraping modules
│  ├─ database/                   # SQLite connection/schema/repository
│  ├─ processing/                 # cleaning + transform pipeline
│  ├─ analytics/                  # market and district analytics
│  ├─ services/                   # OpenAI price prediction
│  ├─ models/                     # property model classes
│  └─ utils/                      # config/logger
└─ tests/                         # pytest coverage
```

## 5. Data Model

SQLite table: `properties`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | Primary key |
| `title` | TEXT | Listing title |
| `district` | TEXT | Hanoi district |
| `address` | TEXT | Address/location text |
| `price` | REAL | Numeric price, normalized by processing |
| `price_text` | TEXT | Original display price |
| `area` | REAL | Numeric area |
| `area_text` | TEXT | Original display area |
| `property_type` | TEXT | Apartment, land, villa, etc. |
| `listing_date` | TEXT | Legacy column; new scraping does not collect it |
| `source` | TEXT | Source site |
| `url` | TEXT | External detail URL |
| `created_at` | TEXT | SQLite timestamp |
| `ai_predicted_price` | REAL | Optional AI prediction |

Current product rule:

- `listing_date` remains in schema for compatibility.
- New scraping/import flow should not collect or rely on listing dates.

## 6. Scraping Flow

1. User opens `/data-collection`.
2. User selects sources, keyword, and district.
3. Browser calls `POST /api/run-scraper`.
4. Flask starts a background `threading.Thread`.
5. `run_all_scrapers()` dispatches selected source modules.
6. Each scraper uses SeleniumBase helper functions in `selenium_scraper.py`.
7. Records are normalized and deduplicated in `app.py`.
8. `PropertyRepository.insert_many()` writes records to SQLite.
9. UI polls `/api/scraper-status` every second.
10. Progress bars, saved record count, and logs update live.

Supported source modules:

```text
alonhadat_scraper.py
homedy_scraper.py
nhadat24h_scraper.py
batdongsan_scraper.py
mogi_scraper.py
nhatot_scraper.py
sosanhnha_scraper.py
bds123_scraper.py
nhaongay_scraper.py
meeyland_scraper.py
```

## 7. Processing Pipeline

Primary module:

```text
src/processing/transform_data.py
```

Pipeline:

1. Convert rows to pandas DataFrame.
2. Clean numeric price.
3. Clean numeric area.
4. Fill missing values.
5. Drop duplicate listings by title/district/price/area.
6. Flag price and area outliers.
7. Normalize price values.
8. Compute derived metrics such as `price_per_m2`, `month`, and `year`.

## 8. Analytics and Dashboard

Dashboard data is built in `_build_dashboard_context()` in `app.py`.

Dashboard charts:

- Source coverage / collection health.
- Average price by district.
- Property type distribution.
- Price vs area scatter.
- Market trend line chart.
- Price bands.

Analytics page uses `_build_analytics_context()` and renders:

- District comparison.
- Property type analysis.
- Source coverage.
- Budget bands.
- Top 10 most expensive listings.
- Top 10 best-value listings.

## 9. Database Import/Export

Database page routes:

```text
GET  /database
POST /database/import.csv
POST /database/import.json
GET  /database/export.csv
GET  /database/export.json
```

Import behavior:

- CSV rows are read with `csv.DictReader`.
- JSON accepts either a list of objects or a wrapper object with `records`/`data`.
- Imported rows are normalized through `_normalise_import_row()`.
- New imports do not set `listing_date`.

Export behavior:

- CSV and JSON export the canonical database fields.
- Export excludes internal UI-only values.

## 10. AI Price Prediction

Module:

```text
src/services/openai_service.py
```

Flow:

1. User clicks `Analyze Prices (AI)` on Dashboard.
2. Browser calls `POST /api/analyze-prices`.
3. App selects up to 10 rows with price and area but no `ai_predicted_price`.
4. `predict_prices()` calls OpenAI using `OPENAI_API_KEY`.
5. Predictions are saved back to SQLite.

If `OPENAI_API_KEY` is missing, prediction returns `{}` and logs an error.

## 11. UI System

Main CSS:

```text
static/css/style.css
```

Theme script:

```text
static/js/theme.js
```

Design principles:

- Sidebar-first dashboard layout.
- Custom semantic CSS variables.
- Light/dark mode via `localStorage` key `tec004-theme`.
- Chart.js canvas containers use fixed heights to avoid runaway page height.
- Sidebar brand text is minimized to `Hanoi Housing Market Intelligence`.

## 12. Testing

Run the core tests:

```bash
python -m pytest tests/test_dashboard.py tests/test_processing.py tests/test_collection_api.py -q
```

Smoke-test routes manually:

```bash
python - <<'PY'
from app import app
client = app.test_client()
for path in ['/dashboard','/properties','/data-collection','/database','/analytics','/settings']:
    r = client.get(path)
    print(path, r.status_code)
PY
```

## 13. Known Design Decisions

- `/` redirects directly to `/dashboard`; landing page is no longer used.
- Reports tab was removed from navigation and route handling.
- Listing date collection was disabled by product request.
- Database schema keeps legacy `listing_date` to avoid destructive migrations.
- Scraper imports are lazy-loaded so the web UI can still boot if scraper-only dependencies are missing.

## 14. Codebase Size Snapshot

Generated with `pygount` excluding caches/build/dependencies:

```text
Python: 59 files, 2257 code lines
HTML/Jinja: 8 files, 755 code lines
CSS: 1 file, 266 code lines
JavaScript: 3 files, 159 code lines
Total: 77 files, 4333 code lines
```
