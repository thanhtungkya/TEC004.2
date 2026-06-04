from flask import Flask, jsonify, render_template, request

from src.analytics.market_analysis import MarketAnalysis
from src.database.create_tables import create_tables
from src.database.property_repository import PropertyRepository
from src.processing.transform_data import transform_records
from src.scraper.scraper_manager import run_all_scrapers

app = Flask(__name__)


@app.before_request
def initialize_database():
    create_tables()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.get("/properties")
def properties():
    repo = PropertyRepository()
    records = [dict(row) for row in repo.fetch_all()]
    dataframe = transform_records(records)
    return render_template("properties.html", properties=dataframe.to_dict("records"))


@app.get("/analytics")
def analytics():
    repo = PropertyRepository()
    records = [dict(row) for row in repo.fetch_all()]
    dataframe = transform_records(records)
    summary = MarketAnalysis().summarize(dataframe)
    return render_template("analytics.html", summary=summary)


@app.get("/data-collection")
def data_collection():
    return render_template("data_collection.html")


@app.get("/database")
def database():
    return render_template("database.html")


@app.get("/reports")
def reports():
    return render_template("reports.html")


@app.get("/settings")
def settings():
    return render_template("settings.html")


@app.post("/api/collect")
def api_collect():
    create_tables()

    selected = request.get_json(silent=True) or {}
    requested_sources = [item.lower() for item in (selected.get("sources") or ["alonhadat", "homedy", "nhadat24h"])]
    keyword = (selected.get("keyword") or "").strip()
    district = (selected.get("district") or "").strip()
    allowed_sources = ("alonhadat", "homedy", "nhadat24h")
    sources = [source for source in requested_sources if source in allowed_sources]

    if not sources:
        return jsonify({"status": "error", "message": "No valid sources were selected."}), 400

    try:
        results = run_all_scrapers(sources)
    except Exception as exc:
        return jsonify({"status": "error", "message": f"Scraping failed: {exc}"}), 500

    seen = set()
    collected = []

    for source, rows in results.items():
        for item in rows or []:
            title = str(item.get("title") or "Untitled listing").strip()[:120]
            item_district = str(item.get("district") or district or "Unknown").strip()
            price = item.get("price") or 0
            area = item.get("area") or 0
            record_key = (source, title, item_district, price, area)

            if record_key in seen:
                continue
            seen.add(record_key)

            collected.append((title, item_district, price, area, source))

    if collected:
        try:
            PropertyRepository().insert_many(collected)
        except Exception as exc:
            return jsonify({"status": "error", "message": f"Database update failed: {exc}"}), 500

    return jsonify({
        "status": "ok",
        "keyword": keyword,
        "district": district,
        "sources": sources,
        "records_saved": len(collected),
        "message": f"Collected {len(collected)} listings from {', '.join(sources)}.",
    })


@app.get("/api/summary")
def api_summary():
    repo = PropertyRepository()
    records = [dict(row) for row in repo.fetch_all()]
    dataframe = transform_records(records)
    return jsonify(MarketAnalysis().summarize(dataframe))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
