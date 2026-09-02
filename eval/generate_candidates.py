"""Run the eval query set through the real search_products() and write
eval/candidates.json — the top-10 results per query, ready for hand-labeling
(add "relevant": true/false to each candidate) before running evaluate.py.
"""

import json
import os
import sys

_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from backend.rag_pipeline import search_products
from eval.queries import QUERIES

_EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(_EVAL_DIR, "candidates.json")

TOP_K = 10


def generate_candidates(top_k=TOP_K):
    output = []
    for item in QUERIES:
        results = search_products(item["query"], top_k=top_k)
        candidates = [
            {
                "id": r.get("id"),
                "name": r.get("name"),
                "price": r.get("price"),
                "distance": r.get("distance"),
                "relevant": None,  # fill in by hand: true / false
            }
            for r in results
        ]
        output.append(
            {
                "id": item["id"],
                "query": item["query"],
                "candidates": candidates,
            }
        )
    return output


if __name__ == "__main__":
    data = generate_candidates()
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(data)} queries x top-{TOP_K} candidates -> {OUTPUT_PATH}")
