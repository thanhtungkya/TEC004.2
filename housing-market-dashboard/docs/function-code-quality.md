# 4. Function and Code Quality

## 4.1. Application Architecture & Module Organization

The TEC004.2 project follows a **Layered Architecture**. Each layer has a clear responsibility, which makes the code easier to maintain, test, and extend.

The main application is located in:

```text
housing-market-dashboard/
```

Current project structure:

```text
housing-market-dashboard/
├─ app.py                         # Flask routes, API endpoints, app orchestration
├─ data/database/housing_market.db # SQLite database
├─ templates/                     # Jinja HTML pages
│  ├─ dashboard.html              # Main dashboard UI
│  ├─ properties.html             # Property listing table
│  ├─ data_collection.html        # Scraper control UI
│  ├─ database.html               # Import/export and database preview
│  ├─ analytics.html              # Analytics dashboard
│  └─ settings.html               # Appearance settings
├─ static/
│  ├─ css/style.css               # Global UI styling and theme tokens
│  └─ js/
│     ├─ collection.js            # Scraper progress polling and UI control
│     └─ theme.js                 # Dark/light theme persistence
├─ src/
│  ├─ scraper/                    # Web scraping layer
│  ├─ database/                   # Database connection, schema, repository
│  ├─ processing/                 # Data cleaning and transformation
│  ├─ analytics/                  # Market and district analytics
│  ├─ services/                   # External service integration, e.g. OpenAI
│  ├─ models/                     # Domain model classes
│  └─ utils/                      # Configuration and logging helpers
└─ tests/                         # Automated tests
```

### Layer responsibilities

| Layer | Responsibility | Example files |
|---|---|---|
| Presentation Layer | HTML templates, CSS, frontend JavaScript | `templates/`, `static/` |
| Application Layer | Flask routes, API orchestration | `app.py` |
| Scraping Layer | Collect data from external real-estate websites | `src/scraper/` |
| Processing Layer | Clean price, area, duplicates, and outliers | `src/processing/` |
| Data Access Layer | SQLite connection and repository methods | `src/database/` |
| Analytics Layer | Market summaries and district analysis | `src/analytics/` |
| Service Layer | Optional AI price prediction | `src/services/openai_service.py` |
| Testing Layer | Regression and feature tests | `tests/` |

This modular organization separates business logic from web routes and database operations. For example, data cleaning is handled by `DataCleaner`, database access is handled by `PropertyRepository`, and scraping orchestration is handled by `run_all_scrapers()`.

## 4.2. Coding Standards

The project mainly uses **Python**, with HTML/Jinja, CSS, and JavaScript for the dashboard interface.

### Python coding standards

The team should follow **PEP 8** conventions:

- Use `snake_case` for variables and functions.
- Use `PascalCase` for classes.
- Use uppercase constants for global configuration values.
- Keep functions focused on one responsibility.
- Use clear module names based on feature or responsibility.
- Use explicit imports instead of wildcard imports.
- Use docstrings for public classes and important functions.

Examples from the project:

```python
class PropertyRepository:
    def insert_many(self, rows):
        ...
```

```python
SCRAPE_LINK_LIMIT = 1000
```

```python
def normalize_listing_url(url: str) -> str:
    ...
```

### Naming conventions

| Code element | Convention | Example |
|---|---|---|
| Class | `PascalCase` | `PropertyRepository`, `DataCleaner` |
| Function | `snake_case` | `run_all_scrapers`, `fetch_urls` |
| Variable | `snake_case` | `existing_urls`, `normalised_rows` |
| Constant | `UPPER_SNAKE_CASE` | `SCRAPE_LINK_LIMIT`, `HANOI_DISTRICTS` |
| Template file | Descriptive lowercase | `data_collection.html` |
| Test file | `test_*.py` | `test_collection_api.py` |

### JavaScript coding standards

The frontend JavaScript follows simple browser-native conventions:

- Use `const` and `let`.
- Use descriptive DOM variable names.
- Keep event handlers small.
- Use `async/await` for API calls.
- Avoid unnecessary frontend dependencies.

Example:

```javascript
const sourceOptions = document.getElementById('sourceOptions');
const startBtn = document.getElementById('startScrape');

function selectedSources() {
  if (!sourceOptions) return [];
  return Array.from(sourceOptions.querySelectorAll('input:checked')).map((box) => box.value);
}
```

### Git source control rules

The project currently uses Git with the `main` branch.

Recommended Git workflow:

```text
main
└─ feature/<short-feature-name>
└─ fix/<short-bug-name>
└─ docs/<documentation-change>
```

Recommended commit message format:

```text
type(scope): short description
```

Examples:

```text
feat(scraper): skip existing listing urls during collection
fix(ui): prevent dashboard chart height overflow
docs(readme): add wiki and architecture diagram links
test(scraper): cover source link deduplication
```

Suggested commit types:

| Type | Purpose |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation change |
| `test` | Test change |
| `refactor` | Internal code cleanup |
| `style` | Formatting or UI-only styling |
| `chore` | Tooling/config updates |

## 4.3. Implemented Functionalities

The current system has several working features that have been tested successfully.

### Implemented and tested features

| Feature | Status |
|---|---|
| Dashboard page with summary metrics and charts | Implemented |
| Property listing page with searchable table | Implemented |
| Data collection UI for scraper execution | Implemented |
| Multi-source web scraping architecture | Implemented |
| Skip already-scraped listing URLs | Implemented |
| Move to another category when current category is exhausted | Implemented |
| Scraping limit of 1000 links per real-estate source | Implemented |
| SQLite storage for property records | Implemented |
| Database import from CSV/JSON | Implemented |
| Database export to CSV/JSON | Implemented |
| Analytics page with market insights | Implemented |
| CSV export for property and analytics data | Implemented |
| Dark/light appearance setting | Implemented |
| Optional AI price prediction through OpenAI | Partially implemented; requires `OPENAI_API_KEY` |
| Automated tests with pytest | Implemented |

Recent verification result:

```text
pytest: 7 passed
```

### Important code snippet 1: Scraper orchestration and duplicate URL skipping

This code shows good modular design because the scraper manager does not contain site-specific scraping logic. It coordinates source scrapers, loads existing URLs from the repository, normalizes them, and prevents duplicate scraping.

```python
def run_all_scrapers(sources=None, progress_cb=None, log_cb=None, abort_event=None, link_limit=SCRAPE_LINK_LIMIT):
    scrapers = {
        'alonhadat': scrape_alonhadat,
        'homedy': scrape_homedy,
        'nhadat24h': scrape_nhadat24h,
        'batdongsan': scrape_batdongsan,
        'mogi': scrape_mogi,
        'nhatot': scrape_nhatot,
        'sosanhnha': scrape_sosanhnha,
        'bds123': scrape_bds123,
        'nhaongay': scrape_nhaongay,
        'meeyland': scrape_meeyland,
    }

    existing_urls = {normalize_listing_url(url) for url in PropertyRepository().fetch_urls()}
    selected = [item.lower() for item in (sources or list(scrapers.keys()))]
    results = {}

    for name in selected:
        if abort_event and abort_event.is_set():
            if log_cb:
                log_cb(name, "Fail", "Aborted by user.")
            break

        if name not in scrapers:
            continue

        try:
            if log_cb:
                log_cb(name, "Info", f"Started scraping. Skipping {len(existing_urls)} already-saved links.")

            records = scrapers[name](
                progress_cb=progress_cb,
                log_cb=log_cb,
                abort_event=abort_event,
                existing_urls=existing_urls,
                link_limit=link_limit,
            )

            results[name] = records
            existing_urls.update(normalize_listing_url(row.get('url')) for row in records if row.get('url'))

            if log_cb:
                log_cb(name, "Success", f"Finished scraping. Got {len(records)} new records.")

        except Exception as exc:
            logger.error("Scraper '%s' failed: %s", name, exc)
            if log_cb:
                error_msg = f"[{type(exc).__name__}] {exc}"
                log_cb(name, "Fail", f"Error: {error_msg}")
            results[name] = []

    return results
```

Why this is good:

- Source scrapers are registered in one dictionary.
- Existing URLs are fetched once before scraping.
- URL deduplication is centralized.
- Errors are handled per source, so one failing scraper does not crash the entire scraping process.
- `abort_event` allows safe cancellation.

### Important code snippet 2: Multi-category scraping with link limit

This code allows each website to have multiple categories. If one category has only old links, the scraper continues to the next category until it reaches the limit or runs out of sources.

```python
SCRAPE_LINK_LIMIT = 1000


def normalize_listing_url(url: str) -> str:
    value = str(url or '').strip()
    if not value:
        return ''
    value = value.split('#', 1)[0].split('?', 1)[0]
    return value.rstrip('/')


def collect_cards_from_sources(
    source_name: str,
    source_urls,
    selector: str,
    card_selector: Optional[str] = None,
    existing_urls=None,
    limit: int = SCRAPE_LINK_LIMIT,
    log_cb=None,
    abort_event=None,
):
    existing = {normalize_listing_url(url) for url in (existing_urls or set()) if url}
    seen = set()
    cards = []

    for source_url in source_urls:
        if abort_event and abort_event.is_set():
            break

        page_cards = render_listing_cards(source_url, selector, card_selector)
        added = 0

        for item in page_cards:
            url_key = normalize_listing_url(item.get('url'))

            if not url_key or url_key in existing or url_key in seen:
                continue

            seen.add(url_key)
            cards.append(item)
            added += 1

            if len(cards) >= limit:
                if log_cb:
                    log_cb(source_name, 'Info', f'Reached {limit} new links limit.')
                return cards

        if log_cb:
            log_cb(source_name, 'Info', f'{source_url}: {added} new links, {len(page_cards) - added} skipped.')

    return cards
```

Why this is good:

- Prevents duplicate scraping across database records and current runtime.
- Supports multiple categories per website.
- Enforces a strict `1000`-link limit.
- Keeps URL normalization reusable.
- Provides logging for skipped and collected links.

### Important code snippet 3: Data cleaning pipeline

The `DataCleaner` class demonstrates modular, step-by-step data processing.

```python
class DataCleaner:
    DUPLICATE_SUBSET = ['title', 'district', 'price', 'area']
    IQR_MULTIPLIER = 1.5

    def clean(self, records) -> pd.DataFrame:
        """Run the full cleaning pipeline and return a tidy DataFrame."""
        df = self._to_dataframe(records)
        if df.empty:
            return df

        df = self._clean_price_column(df)
        df = self._clean_area_column(df)
        df = self._handle_missing_values(df)
        df = self._remove_duplicates(df)
        df = self._detect_outliers(df)
        df = self._normalize_prices(df)
        df = self._compute_derived_columns(df)
        return df
```

Why this is good:

- The pipeline is readable and ordered.
- Each transformation step has a separate method.
- The class can be tested independently.
- It avoids mixing data cleaning logic with Flask route logic.

### Important code snippet 4: Repository pattern for database access

The project uses a repository class to isolate database operations from business logic.

```python
class PropertyRepository:
    def fetch_all(self):
        conn = get_connection()
        try:
            return conn.execute("SELECT * FROM properties ORDER BY id DESC").fetchall()
        finally:
            conn.close()

    def fetch_urls(self):
        conn = get_connection()
        try:
            return [
                row[0]
                for row in conn.execute(
                    "SELECT url FROM properties WHERE url IS NOT NULL AND TRIM(url) != ''"
                ).fetchall()
            ]
        finally:
            conn.close()
```

Why this is good:

- Database access is centralized.
- Connections are closed safely in `finally`.
- The scraper layer can request existing URLs without knowing SQL details.
- The code is easier to test and refactor later.

## 4.4. GitHub Repository Link

GitHub repository:

```text
https://github.com/thanhtungkya/TEC004.2
```

The repository includes a `README.md` file with:

- Project overview
- Repository layout
- Local setup instructions for Windows and macOS/Linux
- Database setup
- Main routes
- API endpoint list
- Supported scraper sources
- Testing instructions
- Deployment notes
- Links to:
  - `housing-market-dashboard/docs/WIKI.md`
  - `housing-market-dashboard/docs/architecture-diagrams.html`

Current README wiki links:

```md
## Documentation

- [Project wiki](housing-market-dashboard/docs/WIKI.md)
- [Architecture diagrams](housing-market-dashboard/docs/architecture-diagrams.html)
```

Note: The local working tree currently contains uncommitted changes, so the GitHub repository may need a final commit and push before it fully reflects the latest scraper updates and documentation.
