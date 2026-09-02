"""Latency benchmark for the running API — no labeling required.

Runs all eval queries through POST /search/text (raw FAISS retrieval) and
POST /chat (retrieval + Groq answer generation) and reports min/max/average
response time per endpoint, plus the RAG generation overhead over raw
retrieval. Requires the API to already be running (see README.md).
"""

import os
import statistics
import time

import requests

from eval.queries import QUERIES

API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")
_EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(_EVAL_DIR, "latency_results.md")


def benchmark_endpoint(endpoint, build_payload):
    timings = []
    for item in QUERIES:
        payload = build_payload(item["query"])
        start = time.perf_counter()
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=payload, timeout=60)
        elapsed = time.perf_counter() - start
        response.raise_for_status()
        timings.append(elapsed)
    return timings


def summarize(timings):
    return {
        "n": len(timings),
        "min": min(timings),
        "max": max(timings),
        "avg": statistics.mean(timings),
    }


def main():
    print(f"Benchmarking against {API_BASE_URL} ({len(QUERIES)} queries per endpoint)...")

    search_timings = benchmark_endpoint("/search/text", lambda q: {"query": q, "top_k": 10})
    search_stats = summarize(search_timings)
    print(
        f"\nPOST /search/text: min={search_stats['min']:.3f}s "
        f"max={search_stats['max']:.3f}s avg={search_stats['avg']:.3f}s"
    )

    chat_timings = benchmark_endpoint("/chat", lambda q: {"query": q})
    chat_stats = summarize(chat_timings)
    print(
        f"POST /chat:        min={chat_stats['min']:.3f}s "
        f"max={chat_stats['max']:.3f}s avg={chat_stats['avg']:.3f}s"
    )

    overhead = chat_stats["avg"] - search_stats["avg"]
    print(f"\nRAG answer-generation overhead over raw retrieval (avg): {overhead:.3f}s")

    lines = [
        "# API Latency Benchmark",
        "",
        f"{len(QUERIES)} queries per endpoint, against `{API_BASE_URL}`.",
        "",
        "| Endpoint | N | Min (s) | Max (s) | Avg (s) |",
        "|---|---|---|---|---|",
        f"| POST /search/text | {search_stats['n']} | {search_stats['min']:.3f} | "
        f"{search_stats['max']:.3f} | {search_stats['avg']:.3f} |",
        f"| POST /chat | {chat_stats['n']} | {chat_stats['min']:.3f} | "
        f"{chat_stats['max']:.3f} | {chat_stats['avg']:.3f} |",
        "",
        f"**RAG answer-generation overhead over raw retrieval (avg /chat - avg "
        f"/search/text): {overhead:.3f}s**",
    ]
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nWrote results -> {RESULTS_PATH}")


if __name__ == "__main__":
    main()
