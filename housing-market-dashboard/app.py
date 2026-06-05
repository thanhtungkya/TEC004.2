import csv
import math
from io import StringIO

from flask import Flask, Response, jsonify, render_template, request

from src.analytics.district_analysis import DistrictAnalysis
from src.analytics.market_analysis import MarketAnalysis
from src.database.create_tables import create_tables
from src.database.property_repository import PropertyRepository
from src.processing.transform_data import DataCleaner, transform_records
from src.scraper.scraper_manager import run_all_scrapers

app = Flask(__name__)

# Initialise the database once at import-time (not on every request).
create_tables()


@app.after_request
def add_response_headers(response):
    """Add CORS and cache headers so browser extensions cannot block API calls."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/dashboard")
def dashboard():
    return render_template("dashboard.html")


def _normalise_external_url(url, source=None):
    """Return a safe external detail URL, or None when the DB value is stale."""
    if not url:
        return None
    value = str(url).strip()
    if not value or value.lower() in {"none", "nan", "null"}:
        return None
    if source == "nhadat24h" and "/tim-kiem" in value:
        # Old rows were backfilled with search URLs, not detail URLs.
        return None
    if not value.startswith(("http://", "https://")):
        return None
    return value


def _load_property_rows():
    repo = PropertyRepository()
    records = [dict(row) for row in repo.fetch_all()]
    dataframe = transform_records(records)
    properties = dataframe.to_dict("records")
    for item in properties:
        item["url"] = _normalise_external_url(item.get("url"), item.get("source"))
    return properties


def _filter_property_rows(rows, args):
    query = (args.get("q") or "").strip().lower()
    source = (args.get("source") or "all").strip().lower()
    district = (args.get("district") or "all").strip().lower()

    filtered = []
    for item in rows:
        title = str(item.get("title") or "")
        address = str(item.get("address") or "")
        item_district = str(item.get("district") or "")
        item_source = str(item.get("source") or "").lower()

        haystack = " ".join([title, address, item_district, item_source]).lower()
        if query and query not in haystack:
            continue
        if source != "all" and item_source != source:
            continue
        if district != "all" and district not in item_district.lower() and district not in address.lower():
            continue
        filtered.append(item)

    return filtered


def _property_filter_options(rows):
    sources = sorted({str(item.get("source") or "").lower() for item in rows if item.get("source")})
    districts = sorted({str(item.get("district") or "") for item in rows if item.get("district") and str(item.get("district")).lower() != "unknown"})
    return sources, districts


@app.get("/properties")
def properties():
    all_rows = _load_property_rows()
    filtered_rows = _filter_property_rows(all_rows, request.args)

    per_page = 10
    page = request.args.get("page", 1, type=int)
    total = len(filtered_rows)
    total_pages = max(1, math.ceil(total / per_page))
    page = min(max(page, 1), total_pages)
    start = (page - 1) * per_page
    end = start + per_page
    page_rows = filtered_rows[start:end]

    sources, districts = _property_filter_options(all_rows)
    query_args = request.args.to_dict(flat=True)
    query_args.pop("page", None)

    return render_template(
        "properties.html",
        properties=page_rows,
        sources=sources,
        districts=districts,
        filters={
            "q": request.args.get("q", ""),
            "source": request.args.get("source", "all"),
            "district": request.args.get("district", "all"),
        },
        pagination={
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "start": start + 1 if total else 0,
            "end": min(end, total),
            "has_prev": page > 1,
            "has_next": page < total_pages,
            "prev_page": page - 1,
            "next_page": page + 1,
        },
        query_args=query_args,
    )


@app.get("/properties/export.csv")
def export_properties_csv():
    rows = _filter_property_rows(_load_property_rows(), request.args)
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=["title", "address", "district", "price", "price_text", "area", "area_text", "source", "url"])
    writer.writeheader()
    for item in rows:
        writer.writerow({
            "title": item.get("title") or "",
            "address": item.get("address") or item.get("district") or "",
            "district": item.get("district") or "",
            "price": item.get("price") or "",
            "price_text": item.get("price_text") or item.get("price") or "",
            "area": item.get("area") or "",
            "area_text": item.get("area_text") or item.get("area") or "",
            "source": item.get("source") or "",
            "url": item.get("url") or "",
        })
    # Excel on Windows often guesses CSV files as ANSI unless a UTF-8 BOM is
    # present, which turns Vietnamese text into mojibake like "PhÆ°á»ng".
    csv_bytes = output.getvalue().encode("utf-8-sig")
    return Response(
        csv_bytes,
        content_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": "attachment; filename=property_listings.csv"},
    )


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


@app.post("/api/run-scraper")
def api_run_scraper():
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
            address = str(item.get("address") or item_district or "Unknown").strip()
            price = item.get("price") or 0
            area = item.get("area") or 0
            url = str(item.get("url") or "").strip() or None
            record_key = (source, title, item_district, address, price, area, url)

            if record_key in seen:
                continue
            seen.add(record_key)

            collected.append({
                "title": title,
                "district": item_district,
                "address": address,
                "price": price,
                "price_text": item.get("price_text"),
                "area": area,
                "area_text": item.get("area_text"),
                "source": source,
                "url": url,
            })

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


@app.get("/api/analysis")
def api_analysis():
    """Full statistical analysis report (cleaning → analysis pipeline)."""
    repo = PropertyRepository()
    records = [dict(row) for row in repo.fetch_all()]
    dataframe = DataCleaner().clean(records)
    report = MarketAnalysis().full_report(dataframe)
    return jsonify(report)


@app.get("/api/district-stats")
def api_district_stats():
    """Per-district price and area statistics."""
    repo = PropertyRepository()
    records = [dict(row) for row in repo.fetch_all()]
    dataframe = DataCleaner().clean(records)
    analysis = DistrictAnalysis()
    return jsonify({
        'top_districts': analysis.top_districts(dataframe),
        'price_statistics': analysis.price_statistics(dataframe),
        'area_statistics': analysis.area_statistics(dataframe),
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
