# Housing Market Dashboard

Flask dashboard for scraping, cleaning, storing, and visualizing Hanoi housing market listings.

## Features
- Data collection modules for supported real-estate sources
- Cleaning and transformation utilities
- SQLite storage for property records
- Dashboard, properties, analytics, database, data-collection, reports, and settings pages
- Automatic redirect from `/` to `/dashboard`; the landing page is no longer used

## Quick start
1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `python3 -m flask --app app run --host 127.0.0.1 --port 5001`
4. Open `http://127.0.0.1:5001`; it redirects to `/dashboard`.

The app initializes the database and opens the dashboard entry point.
