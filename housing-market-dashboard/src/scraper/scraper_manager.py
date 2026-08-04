"""
scraper_manager.py
Orchestrates parallel concurrent execution of all multi-source real estate web scrapers.

Features:
    - Parallel multi-threaded execution across all selected scraper modules
    - Thread-safe tracking of existing URLs and progress log callbacks
    - Graceful cancellation support via threading.Event

Dependencies:
    - concurrent.futures.ThreadPoolExecutor: Concurrency manager
    - src.database.property_repository: URL deduplication fetcher

Exports:
    - run_all_scrapers(): Main orchestrator for parallel scraping
"""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.database.property_repository import PropertyRepository
from src.scraper.selenium_scraper import SCRAPE_LINK_LIMIT, normalize_listing_url
from src.scraper.alonhadat_scraper import scrape_alonhadat
from src.scraper.homedy_scraper import scrape_homedy
from src.scraper.nhadat24h_scraper import scrape_nhadat24h
from src.scraper.batdongsan_scraper import scrape_batdongsan
from src.scraper.mogi_scraper import scrape_mogi
from src.scraper.nhatot_scraper import scrape_nhatot
from src.scraper.sosanhnha_scraper import scrape_sosanhnha
from src.scraper.bds123_scraper import scrape_bds123
from src.scraper.nhaongay_scraper import scrape_nhaongay
from src.scraper.meeyland_scraper import scrape_meeyland

logger = logging.getLogger(__name__)


def run_all_scrapers(sources=None, progress_cb=None, log_cb=None, abort_event=None, link_limit=SCRAPE_LINK_LIMIT):
    """Runs all selected web scrapers in parallel simultaneously.

    Args:
        sources: List of scraper names to run (defaults to all available).
        progress_cb: Thread-safe callback for progress updates.
        log_cb: Thread-safe callback for status log messages.
        abort_event: Event flag to signal premature cancellation.
        link_limit: Maximum items to collect per source.

    Returns:
        Dict[str, List[Dict]]: Dictionary mapping scraper names to collected property rows.
    """
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
    selected = [item.lower() for item in (sources or list(scrapers.keys())) if item.lower() in scrapers]

    if not selected:
        return {}

    results = {}
    lock = threading.Lock()

    def _scrape_single_source(name):
        if abort_event and abort_event.is_set():
            if log_cb:
                log_cb(name, "Fail", "Aborted by user.")
            return name, []

        func = scrapers[name]
        if log_cb:
            log_cb(name, "Info", f"Started parallel scraping. Active deduplication links: {len(existing_urls)}.")

        try:
            records = func(
                progress_cb=progress_cb,
                log_cb=log_cb,
                abort_event=abort_event,
                existing_urls=existing_urls,
                link_limit=link_limit,
            )
            with lock:
                existing_urls.update(normalize_listing_url(row.get('url')) for row in (records or []) if row.get('url'))
            
            if log_cb:
                log_cb(name, "Success", f"Finished parallel scraping. Got {len(records or [])} new records.")
            return name, records or []
        except Exception as exc:
            logger.error("Scraper '%s' failed: %s", name, exc)
            if log_cb:
                error_msg = f"[{type(exc).__name__}] {exc}"
                log_cb(name, "Fail", f"Error: {error_msg}")
            return name, []

    max_workers = min(len(selected), 10)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_scrape_single_source, name) for name in selected]
        for future in as_completed(futures):
            try:
                name, records = future.result()
                results[name] = records
            except Exception as exc:
                logger.error("Error retrieving scraper task result: %s", exc)

    return results

