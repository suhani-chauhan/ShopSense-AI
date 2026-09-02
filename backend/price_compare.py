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

# Google Shopping's structured index doesn't honor "site:" query operators
# (those only apply to organic web search), so a single India-locale query
# is issued and platform listings are picked out of the results by seller
# name — this also halves SerpAPI usage per product vs. two filtered queries.
PLATFORM_SOURCE_MATCH = {
    "amazon": "amazon",
    "flipkart": "flipkart",
}


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
        "title": item.get("title"),
        "price": item.get("price"),
        "rating": item.get("rating"),
        "reviews": item.get("reviews"),
        "url": item.get("product_link") or item.get("link"),
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
        "gl": "in",  # India locale surfaces Amazon.in and Flipkart listings
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


def get_price_comparison(product_name: str) -> dict:
    """Look up the top Amazon.in and Flipkart listings for a product via SerpAPI.

    Never raises — network/quota/missing-key failures are logged and result
    in None for the affected platform(s) so the caller can degrade gracefully.
    """
    cache = _load_cache()
    cached = cache.get(product_name)
    if cached and (time.time() - cached.get("timestamp", 0)) < CACHE_TTL_SECONDS:
        logger.info("Price cache HIT for %r — skipping SerpAPI request.", product_name)
        return cached["result"]

    logger.info("Price cache MISS for %r — querying SerpAPI live.", product_name)
    shopping_results = _fetch_shopping_results(product_name)

    result = {"amazon": None, "flipkart": None}
    for platform, needle in PLATFORM_SOURCE_MATCH.items():
        for item in shopping_results:
            if needle in (item.get("source") or "").lower():
                result[platform] = _extract_listing(item)
                break

    cache[product_name] = {"timestamp": time.time(), "result": result}
    _save_cache(cache)

    return result
