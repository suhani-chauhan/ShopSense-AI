import json
import logging
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    logger.addHandler(_handler)

SERPAPI_URL = "https://serpapi.com/search"
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(_BACKEND_DIR, "price_cache.json")
CACHE_TTL_SECONDS = 24 * 60 * 60  # 1 day


def _load_cache():
    if not os.path.exists(CACHE_PATH):
        return {}
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Could not read price cache, starting fresh: %s", e)
        return {}


def _save_cache(cache):
    try:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except OSError as e:
        logger.warning("Could not write price cache: %s", e)


def _extract_listing(item):
    return {
        "store": item.get("source"),
        "title": item.get("title"),
        "price": item.get("price"),
        "old_price": item.get("old_price"),
        "rating": item.get("rating"),
        "review_count": item.get("reviews"),
        "url": item.get("product_link") or item.get("link"),
        "image_url": item.get("thumbnail"),
        "delivery": item.get("delivery"),
    }


def _fetch_shopping_results(product_name):
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        logger.error(
            "SERPAPI_KEY is not set. Copy .env.example to .env and set "
            "SERPAPI_KEY=your_key_here to enable price comparison."
        )
        return []

    params = {
        "engine": "google_shopping",
        "q": product_name,
        "gl": "in",  # India locale surfaces a broad mix of Indian sellers
        "hl": "en",
        "api_key": api_key,
    }

    try:
        response = requests.get(SERPAPI_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error("SerpAPI request failed for %r: %s", product_name, e)
        return []

    if data.get("error"):
        logger.error("SerpAPI returned an error for %r: %s", product_name, data["error"])
        return []

    return data.get("shopping_results") or []


def _get_raw_shopping_results(product_name):
    """Cached raw SerpAPI shopping_results for a product — the full response,
    not a deduplicated/truncated view, so changing num_results later doesn't
    require a fresh API call. A cache entry from the old {"amazon":...,
    "flipkart":...} shape is treated as a miss and gets overwritten.
    """
    cache = _load_cache()
    cached = cache.get(product_name)
    if (
        cached
        and "shopping_results" in cached
        and (time.time() - cached.get("timestamp", 0)) < CACHE_TTL_SECONDS
    ):
        logger.info("Price cache HIT for %r — skipping SerpAPI request.", product_name)
        return cached["shopping_results"]

    logger.info("Price cache MISS for %r — querying SerpAPI live.", product_name)
    shopping_results = _fetch_shopping_results(product_name)

    cache[product_name] = {"timestamp": time.time(), "shopping_results": shopping_results}
    _save_cache(cache)

    return shopping_results


def get_shopping_comparison(product_name: str, num_results: int = 5) -> list:
    """Return up to num_results shopping listings for a product, one per
    distinct store, in SerpAPI's original ranking order — a general shopping
    grid rather than a fixed Amazon/Flipkart lookup.

    Never raises — a missing key, network failure, or empty results all
    result in an empty list (logged), same graceful-degradation contract
    as before.
    """
    shopping_results = _get_raw_shopping_results(product_name)

    listings = []
    seen_stores = set()
    for item in shopping_results:
        store = item.get("source")
        if not store or store in seen_stores:
            continue
        seen_stores.add(store)
        listings.append(_extract_listing(item))
        if len(listings) >= num_results:
            break

    return listings
