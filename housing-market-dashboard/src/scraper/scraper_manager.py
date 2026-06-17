import logging

from src.scraper.alonhadat_scraper import scrape_alonhadat
from src.scraper.homedy_scraper import scrape_homedy
from src.scraper.nhadat24h_scraper import scrape_nhadat24h

logger = logging.getLogger(__name__)


def run_all_scrapers(sources=None, progress_cb=None, abort_event=None):
    scrapers = {
        'alonhadat': scrape_alonhadat,
        'homedy': scrape_homedy,
        'nhadat24h': scrape_nhadat24h,
    }

    selected = [item.lower() for item in (sources or list(scrapers.keys()))]
    results = {}
    for name in selected:
        if abort_event and abort_event.is_set():
            break
        if name not in scrapers:
            continue
        try:
            results[name] = scrapers[name](progress_cb=progress_cb, abort_event=abort_event)
        except Exception as exc:
            logger.error("Scraper '%s' failed: %s", name, exc)
            results[name] = []
    return results
