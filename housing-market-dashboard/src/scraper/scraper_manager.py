import logging

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
