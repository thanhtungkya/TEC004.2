# Hanoi Housing Market Dashboard

A comprehensive Python project for scraping, cleaning, storing, and visualizing Hanoi housing market listings.

## 🌟 Features

- **Data Collection:** Automated web scrapers built with Playwright to collect housing data from various sources.
- **Data Processing:** Cleaning and transformation utilities to standardize the collected property records.
- **Storage:** SQLite database for lightweight, local storage of property records.
- **Analytics & Prediction:** Integrated with OpenAI for price predictions and providing market/district analysis.
- **Interactive Dashboard:** A web-based dashboard built with Flask and Streamlit to visualize the data.

## 🛠️ Project Structure

The main application code is located in the `housing-market-dashboard/` directory.

- `housing-market-dashboard/src/scraper/`: Web scraping modules.
- `housing-market-dashboard/src/processing/`: Data cleaning and transformation logic.
- `housing-market-dashboard/src/database/`: SQLite database initialization and repository patterns.
- `housing-market-dashboard/src/analytics/`: Market and district data analysis.
- `housing-market-dashboard/app.py`: The main Flask application.

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.12
- Playwright system dependencies

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/thanhtungkya/TEC004.2.git
   cd TEC004.2
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install Playwright browsers:
   ```bash
   playwright install
   ```

5. Run the application:
   ```bash
   flask run --host 127.0.0.1 --port 5001
   ```
   Or using Python:
   ```bash
   python app.py
   ```

The app will initialize the SQLite database and launch the dashboard.

## 🚇 Expose Localhost with Cloudflare Tunnel

If you want to share your local dashboard with others over the internet, you can use Cloudflare Tunnel (`cloudflared`).

1. **Install Cloudflare Tunnel:**
   - Download the executable for your OS from the [Cloudflare Tunnel downloads page](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/).
   - Alternatively, install via a package manager (e.g., `brew install cloudflared` on macOS, or use `winget install Cloudflare.cloudflared` on Windows).

2. **Run the tunnel** pointing to your local Flask port (default 5001):
   ```bash
   cloudflared tunnel --url http://127.0.0.1:5001
   ```

3. The command output will provide a temporary public URL (e.g., `https://random-words.trycloudflare.com`). Share this link to allow others to access your dashboard securely!

## 🌐 Deployment

This project is configured for easy deployment on [Render](https://render.com). 

See the detailed deployment guides for instructions:
- [Quick Deployment Guide (5 mins)](QUICK_DEPLOY.md)
- [Comprehensive Deployment Guide](DEPLOYMENT.md)

The deployment relies on the included `render.yaml` configuration and `requirements.txt` (which includes Gunicorn for production serving).
