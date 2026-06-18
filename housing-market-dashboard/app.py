import csv
import json
import math
from datetime import datetime
from io import StringIO
import threading
import app

from flask import Flask, Response, jsonify, render_template, request

from src.analytics.district_analysis import DistrictAnalysis
from src.analytics.market_analysis import MarketAnalysis
from src.database.create_tables import create_tables
from src.database.property_repository import PropertyRepository
from src.processing.transform_data import DataCleaner, transform_records
from src.scraper.scraper_manager import run_all_scrapers
from src.services.openai_service import predict_prices
from src.database.db_connection import get_connection

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialise the database once at import-time (not on every request).
create_tables()

scraping_state = {
    "is_running": False,
    "abort_event": None,
    "progress": {},
    "records_saved": 0,
    "message": "",
    "logs": []
}


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
    repo = PropertyRepository()
    rows = [dict(row) for row in repo.fetch_all()][:10]
    return render_template("dashboard.html", properties=rows)


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


def _format_listing_date(value):
    """Display listing dates as DD/MM/YYYY while keeping DB values unchanged."""
    if not value:
        return ""
    text = str(value).strip()
    if not text or text.lower() in {"none", "nan", "null"}:
        return ""

    for date_format in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text[:10], date_format).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return text


def _load_property_rows():
    repo = PropertyRepository()
    records = [dict(row) for row in repo.fetch_all()]
    dataframe = transform_records(records)
    properties = dataframe.to_dict("records")
    for item in properties:
        item["url"] = _normalise_external_url(item.get("url"), item.get("source"))
        item["listing_date_display"] = _format_listing_date(item.get("listing_date"))
    return properties


def _filter_property_rows(rows, args):
    query = (args.get("q") or "").strip().lower()
    source = (args.get("source") or "all").strip().lower()
    district = (args.get("district") or "all").strip().lower()
    property_type = (args.get("property_type") or "all").strip().lower()

    filtered = []
    for item in rows:
        title = str(item.get("title") or "")
        address = str(item.get("address") or "")
        item_district = str(item.get("district") or "")
        item_source = str(item.get("source") or "").lower()
        item_type = str(item.get("property_type") or "").lower()

        haystack = " ".join([title, address, item_district, item_source]).lower()
        if query and query not in haystack:
            continue
        if source != "all" and item_source != source:
            continue
        if district != "all" and district not in item_district.lower() and district not in address.lower():
            continue
        if property_type != "all" and item_type != property_type:
            continue
        filtered.append(item)

    return filtered


def _property_filter_options(rows):
    sources = sorted({str(item.get("source") or "").lower() for item in rows if item.get("source")})
    districts = sorted({str(item.get("district") or "") for item in rows if item.get("district") and str(item.get("district")).lower() != "unknown"})
    property_types = sorted({str(item.get("property_type") or "") for item in rows if item.get("property_type")})
    return sources, districts, property_types


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

    sources, districts, property_types = _property_filter_options(all_rows)
    query_args = request.args.to_dict(flat=True)
    query_args.pop("page", None)

    return render_template(
        "properties.html",
        properties=page_rows,
        sources=sources,
        districts=districts,
        property_types=property_types,
        filters={
            "q": request.args.get("q", ""),
            "source": request.args.get("source", "all"),
            "district": request.args.get("district", "all"),
            "property_type": request.args.get("property_type", "all"),
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
    writer = csv.DictWriter(output, fieldnames=["title", "address", "district", "price", "price_text", "area", "area_text", "property_type", "listing_date", "source", "url"])
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
            "property_type": item.get("property_type") or "",
            "listing_date": item.get("listing_date_display") or _format_listing_date(item.get("listing_date")),
            "source": item.get("source") or "",
            "url": item.get("url") or "",
        })
    # Excel on Windows often guesses CSV files as ANSI unless a UTF-8 BOM is
    # present, which turns Vietnamese text into mojibake like "Phường".
    csv_bytes = output.getvalue().encode("utf-8-sig")
    return Response(
        csv_bytes,
        content_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": "attachment; filename=property_listings.csv"},
    )


@app.post("/api/clean-data")
def clean_data():
    """Re-process all existing records in the DB using the latest extraction
    functions.  Fixes price_text (removes garbage text), price (numeric),
    area (removes false 70m² defaults), and area_text.  Returns JSON with
    the number of records cleaned."""
    from src.scraper.selenium_scraper import (
        normalise_price_text, extract_price, extract_area
    )

    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, title, price_text, area_text FROM properties"
        ).fetchall()

        cleaned = 0
        for row in rows:
            row_id = row["id"]
            title = row["title"] or ""
            old_price_text = row["price_text"] or ""
            old_area_text = row["area_text"] or ""

            # --- Re-clean price_text ---
            # If the old price_text looks like it contains garbage (more than
            # ~40 chars is a strong signal it's an entire card dump, not a
            # clean price), re-extract from scratch.
            new_price_text = old_price_text
            if len(old_price_text) > 40 or not old_price_text:
                new_price_text = normalise_price_text(old_price_text or title)
            else:
                # Even short strings may have issues; normalise anyway.
                new_price_text = normalise_price_text(old_price_text)

            new_price = extract_price(new_price_text) if new_price_text else 0.0

            # --- Re-clean area ---
            new_area = extract_area(old_area_text) if old_area_text else 0.0
            if new_area == 0.0 and title:
                new_area = extract_area(title)
            # Clear area_text if we couldn't find a valid area
            new_area_text = old_area_text
            if new_area == 0.0:
                new_area_text = ""

            conn.execute(
                """UPDATE properties
                   SET price_text = ?, price = ?,
                       area_text = ?, area = ?
                 WHERE id = ?""",
                (new_price_text, new_price, new_area_text, new_area, row_id),
            )
            cleaned += 1

        deleted_cursor = conn.execute(
            """DELETE FROM properties 
               WHERE title IS NULL OR TRIM(title) = '' OR TRIM(title) = 'Untitled listing'
                  OR address IS NULL OR TRIM(address) = '' OR TRIM(address) = 'Unknown'
                  OR price IS NULL OR price = 0
                  OR area IS NULL OR area = 0
                  OR property_type IS NULL OR TRIM(property_type) = '' OR TRIM(property_type) = 'Unknown'
                  OR source IS NULL OR TRIM(source) = '' OR TRIM(source) = 'unknown'"""
        )
        deleted = deleted_cursor.rowcount

        conn.commit()
    finally:
        conn.close()

    return jsonify({"status": "ok", "cleaned": cleaned, "deleted": deleted})


def _filter_analytics_rows(rows, args):
    district = (args.get("district") or "all").strip().lower()
    property_type = (args.get("property_type") or "all").strip().lower()

    filtered = []
    for item in rows:
        item_district = str(item.get("district") or "").lower()
        item_address = str(item.get("address") or "").lower()
        item_type = str(item.get("property_type") or "").lower()
        if district != "all" and district not in item_district and district not in item_address:
            continue
        if property_type != "all" and item_type != property_type:
            continue
        filtered.append(item)
    return filtered


def _format_price_millions(value):
    value = float(value or 0)
    if value >= 1000:
        return f"{value / 1000:.2f} tỷ"
    return f"{value:.0f} triệu"


def _build_analytics_context(args):
    all_rows = _load_property_rows()
    rows = _filter_analytics_rows(all_rows, args)
    dataframe = transform_records(rows)

    valid_price_rows = [item for item in rows if float(item.get("price") or 0) > 0]
    valid_area_rows = [item for item in rows if float(item.get("price") or 0) > 0 and float(item.get("area") or 0) > 0]
    total_listings = len(rows)
    avg_price = sum(float(item.get("price") or 0) for item in valid_price_rows) / len(valid_price_rows) if valid_price_rows else 0
    avg_price_per_m2 = sum(float(item.get("price") or 0) / float(item.get("area") or 1) for item in valid_area_rows) / len(valid_area_rows) if valid_area_rows else 0
    districts = sorted({str(item.get("district") or "") for item in all_rows if item.get("district") and str(item.get("district")).lower() != "unknown"})
    property_types = sorted({str(item.get("property_type") or "") for item in all_rows if item.get("property_type")})

    district_groups = {}
    for item in valid_price_rows:
        district_name = item.get("district") or "Unknown"
        district_groups.setdefault(district_name, []).append(float(item.get("price") or 0))
    district_comparison = [
        {"district": name, "avg_price": round(sum(values) / len(values), 2), "count": len(values)}
        for name, values in district_groups.items()
    ]
    district_comparison.sort(key=lambda item: item["avg_price"], reverse=True)
    district_comparison = district_comparison[:10]

    type_counts = {}
    for item in rows:
        type_name = item.get("property_type") or "Unknown"
        type_counts[type_name] = type_counts.get(type_name, 0) + 1
    property_type_distribution = [{"property_type": name, "count": count} for name, count in sorted(type_counts.items())]

    most_expensive = sorted(valid_price_rows, key=lambda item: float(item.get("price") or 0), reverse=True)[:10]
    most_expensive = [{
        "title": item.get("title") or "Untitled listing",
        "district": item.get("district") or "Unknown",
        "price": item.get("price_text") or _format_price_millions(item.get("price")),
    } for item in most_expensive]

    best_value = sorted(valid_area_rows, key=lambda item: float(item.get("price") or 0) / float(item.get("area") or 1))[:10]
    best_value = [{
        "title": item.get("title") or "Untitled listing",
        "district": item.get("district") or "Unknown",
        "price_per_m2": _format_price_millions(float(item.get("price") or 0) / float(item.get("area") or 1)),
    } for item in best_value]

    latest_dates = [item.get("listing_date") for item in rows if item.get("listing_date") and str(item.get("listing_date")).lower() != "unknown"]
    latest_date = max(latest_dates) if latest_dates else ""

    return {
        "summary": {
            "total_listings": total_listings,
            "avg_price": round(avg_price, 2),
            "avg_price_per_m2": round(avg_price_per_m2, 2),
            "district_coverage": len({item.get("district") for item in rows if item.get("district") and str(item.get("district")).lower() != "unknown"}),
        },
        "districts": districts,
        "property_types": property_types,
        "filters": {
            "district": args.get("district", "all"),
            "property_type": args.get("property_type", "all"),
            "period": args.get("period", "all"),
        },
        "updated_label": _format_listing_date(latest_date) if latest_date else "—",
        "district_comparison": district_comparison,
        "property_type_distribution": property_type_distribution,
        "most_expensive": most_expensive,
        "best_value": best_value,
        "chart_data": {
            "district_labels": [item["district"] for item in district_comparison],
            "district_prices": [item["avg_price"] for item in district_comparison],
            "type_labels": [item["property_type"] for item in property_type_distribution],
            "type_counts": [item["count"] for item in property_type_distribution],
        },
    }


@app.get("/analytics")
def analytics():
    context = _build_analytics_context(request.args)
    context["chart_data_json"] = json.dumps(context["chart_data"], ensure_ascii=False)
    return render_template("analytics.html", **context)


@app.get("/analytics/export.csv")
def export_analytics_csv():
    context = _build_analytics_context(request.args)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["metric", "value"])
    for key, value in context["summary"].items():
        writer.writerow([key, value])
    writer.writerow([])
    writer.writerow(["top_10_most_expensive"])
    writer.writerow(["listing", "district", "price"])
    for item in context["most_expensive"]:
        writer.writerow([item["title"], item["district"], item["price"]])
    writer.writerow([])
    writer.writerow(["top_10_best_value"])
    writer.writerow(["listing", "district", "price_per_m2"])
    for item in context["best_value"]:
        writer.writerow([item["title"], item["district"], item["price_per_m2"]])
    csv_bytes = output.getvalue().encode("utf-8-sig")
    return Response(
        csv_bytes,
        content_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": "attachment; filename=analytics_insights.csv"},
    )


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
    global scraping_state
    if scraping_state.get("is_running"):
        return jsonify({"status": "error", "message": "Scraping is already in progress."}), 400

    create_tables()

    selected = request.get_json(silent=True) or {}
    requested_sources = [item.lower() for item in (selected.get("sources") or [
        "alonhadat", "homedy", "nhadat24h", "batdongsan", "mogi", "nhatot", 
        "sosanhnha", "bds123", "nhaongay", "meeyland", "123nhadatviet"
    ])]
    keyword = (selected.get("keyword") or "").strip()
    district = (selected.get("district") or "").strip()
    allowed_sources = (
        "alonhadat", "homedy", "nhadat24h", "batdongsan", "mogi", "nhatot", 
        "sosanhnha", "bds123", "nhaongay", "meeyland", "123nhadatviet"
    )
    sources = [source for source in requested_sources if source in allowed_sources]

    if not sources:
        return jsonify({"status": "error", "message": "No valid sources were selected."}), 400

    scraping_state = {
        "is_running": True,
        "abort_event": threading.Event(),
        "progress": {s: 0 for s in sources},
        "records_saved": 0,
        "message": "Starting...",
        "keyword": keyword,
        "district": district,
        "sources": sources,
        "logs": []
    }

    def _scrape_worker():
        global scraping_state
        def _progress_cb(source_name):
            scraping_state["progress"][source_name] += 1
            
        def _log_cb(source_name, status, message):
            import datetime
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            scraping_state["logs"].append({
                "time": ts,
                "source": source_name.capitalize(),
                "status": status,
                "message": message
            })
            
        try:
            results = run_all_scrapers(sources, progress_cb=_progress_cb, log_cb=_log_cb, abort_event=scraping_state["abort_event"])
        except Exception as exc:
            scraping_state["is_running"] = False
            scraping_state["message"] = f"Scraping failed: {exc}"
            return

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
                    "property_type": item.get("property_type"),
                    "listing_date": item.get("listing_date"),
                    "source": source,
                    "url": url,
                })

        if collected:
            try:
                PropertyRepository().insert_many(collected)
                scraping_state["records_saved"] = len(collected)
                scraping_state["message"] = f"Collected {len(collected)} listings from {', '.join(sources)}."
            except Exception as exc:
                scraping_state["message"] = f"Database update failed: {exc}"
        else:
            scraping_state["message"] = f"Collected 0 listings from {', '.join(sources)}."
            
        scraping_state["is_running"] = False

    thread = threading.Thread(target=_scrape_worker)
    thread.daemon = True
    thread.start()

    return jsonify({"status": "ok", "message": "Scraping started."})


@app.get("/api/scraper-status")
def api_scraper_status():
    global scraping_state
    return jsonify({
        "is_running": scraping_state.get("is_running", False),
        "progress": scraping_state.get("progress", {}),
        "records_saved": scraping_state.get("records_saved", 0),
        "message": scraping_state.get("message", ""),
        "logs": scraping_state.get("logs", [])
    })


@app.post("/api/stop-scraper")
def api_stop_scraper():
    global scraping_state
    if scraping_state.get("is_running") and scraping_state.get("abort_event"):
        scraping_state["abort_event"].set()
        return jsonify({"status": "ok", "message": "Stop signal sent."})
    return jsonify({"status": "error", "message": "Not running."}), 400


@app.post("/api/analyze-prices")
def api_analyze_prices():
    repo = PropertyRepository()
    all_rows = [dict(row) for row in repo.fetch_all()]
    rows_to_analyze = [row for row in all_rows if row.get('price') and row.get('area') and not row.get('ai_predicted_price')]
    rows_to_analyze = rows_to_analyze[:10]
    
    if not rows_to_analyze:
        return jsonify({"status": "ok", "message": "No new properties to analyze."})

    predictions = predict_prices(rows_to_analyze)
    
    if not predictions:
        return jsonify({"status": "error", "message": "Failed to get predictions."})

    conn = get_connection()
    try:
        for pid, price in predictions.items():
            conn.execute("UPDATE properties SET ai_predicted_price = ? WHERE id = ?", (price, pid))
        conn.commit()
    finally:
        conn.close()

    return jsonify({"status": "ok", "message": f"Analyzed {len(predictions)} properties."})


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
