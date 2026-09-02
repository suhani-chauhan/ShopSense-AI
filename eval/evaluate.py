"""Compute precision@5, precision@10, recall@10, and MRR from a hand-labeled
eval/candidates.json (each candidate needs a "relevant": true/false field),
and write a readable table to eval/results.md.
"""

import json
import os

_EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
CANDIDATES_PATH = os.path.join(_EVAL_DIR, "candidates.json")
RESULTS_PATH = os.path.join(_EVAL_DIR, "results.md")

P5_K = 5
P10_K = 10


def load_candidates():
    with open(CANDIDATES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_query(entry):
    candidates = entry["candidates"]
    relevance = [bool(c.get("relevant")) for c in candidates]

    top5 = relevance[:P5_K]
    top10 = relevance[:P10_K]

    precision_at_5 = sum(top5) / len(top5) if top5 else 0.0
    precision_at_10 = sum(top10) / len(top10) if top10 else 0.0

    total_relevant = sum(relevance)
    recall_at_10 = (sum(top10) / total_relevant) if total_relevant > 0 else None

    mrr = 0.0
    for rank, is_relevant in enumerate(relevance, start=1):
        if is_relevant:
            mrr = 1.0 / rank
            break

    return {
        "id": entry["id"],
        "query": entry["query"],
        "precision_at_5": precision_at_5,
        "precision_at_10": precision_at_10,
        "recall_at_10": recall_at_10,
        "mrr": mrr,
        "total_relevant": total_relevant,
    }


def average(per_query, key, skip_none=False):
    values = [q[key] for q in per_query if not (skip_none and q[key] is None)]
    return sum(values) / len(values) if values else 0.0


def main():
    data = load_candidates()

    unlabeled_queries = [
        e["query"] for e in data if any(c.get("relevant") is None for c in e["candidates"])
    ]
    if unlabeled_queries:
        print("WARNING: these queries have unlabeled candidates (treated as not relevant):")
        for q in unlabeled_queries:
            print(f"  - {q}")
        print()

    per_query = [evaluate_query(e) for e in data]

    overall = {
        "precision_at_5": average(per_query, "precision_at_5"),
        "precision_at_10": average(per_query, "precision_at_10"),
        "recall_at_10": average(per_query, "recall_at_10", skip_none=True),
        "mrr": average(per_query, "mrr"),
    }

    lines = [
        "# FAISS Retrieval Evaluation Results",
        "",
        "> **Note on recall@10:** relevance is only judged within each query's "
        "labeled top-10 candidate pool (judging all 3,038 catalog products per "
        "query isn't feasible by hand), so recall@10 reads 1.0 whenever at "
        "least one relevant item was retrieved. Its main signal is flagging "
        "queries where **zero** retrieved candidates were relevant "
        "(recall shown as N/A).",
        "",
        "| ID | Query | P@5 | P@10 | Recall@10 | MRR | #Relevant |",
        "|---|---|---|---|---|---|---|",
    ]
    for q in per_query:
        recall_str = f"{q['recall_at_10']:.2f}" if q["recall_at_10"] is not None else "N/A"
        lines.append(
            f"| {q['id']} | {q['query']} | {q['precision_at_5']:.2f} | "
            f"{q['precision_at_10']:.2f} | {recall_str} | {q['mrr']:.2f} | "
            f"{q['total_relevant']} |"
        )

    lines += [
        "",
        "## Overall (macro-averaged across queries)",
        "",
        f"- **Precision@5**: {overall['precision_at_5']:.3f}",
        f"- **Precision@10**: {overall['precision_at_10']:.3f}",
        f"- **Recall@10**: {overall['recall_at_10']:.3f}",
        f"- **MRR**: {overall['mrr']:.3f}",
    ]

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote results -> {RESULTS_PATH}")


if __name__ == "__main__":
    main()
