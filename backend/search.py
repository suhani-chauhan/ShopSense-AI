"""Thin FAISS-only sanity check — exercises search_products() without
calling the Groq LLM, using the single source of truth in rag_pipeline.py."""

import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from backend.rag_pipeline import search_products

if __name__ == "__main__":
    queries = [
        "warm gloves for men",
        "wool cardigan for women",
        "leather handbag"
    ]

    for query in queries:
        print(f"\n🔍 Searching for: '{query}'")
        results = search_products(query, top_k=3)
        for rank, r in enumerate(results, start=1):
            print(f"  {rank}. {r['name']} — {r.get('brand')} — ${r.get('price')}")
