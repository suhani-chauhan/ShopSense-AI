import os
import pickle
import re

import faiss
import numpy as np
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not set. Copy .env.example to .env and set "
        "GROQ_API_KEY=your_key_here."
    )

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(_BACKEND_DIR, "product_index.faiss")
METADATA_PATH = os.path.join(_BACKEND_DIR, "product_metadata.pkl")

# Load models
embedder = SentenceTransformer("all-MiniLM-L6-v2")
groq_client = Groq(api_key=GROQ_API_KEY)

# Load FAISS index
index = faiss.read_index(INDEX_PATH)

# Load metadata
with open(METADATA_PATH, "rb") as f:
    metadata = pickle.load(f)


def search_products(query, top_k=3):
    query_embedding = embedder.encode([query])
    query_embedding = np.array(query_embedding, dtype="float32")
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        if idx != -1:
            results.append({**metadata[idx], "distance": float(distances[0][i])})
    return results


# ---- Query understanding + hybrid (filter + boost) retrieval --------------
# Pure dense-vector search ranks generic lexical overlap (e.g. every dress
# being "close" to the word "dress") above real gender/style relevance, and
# never uses the gender/category metadata already sitting on every record.
# The fixes below are layered on top of search_products() rather than
# replacing it: search_products() stays available as-is for callers that
# want raw semantic search (/search/text, /search/image).

_GENDER_WORD_PATTERNS = {
    "Woman": r"\b(woman|women|female|ladies|lady|girlfriend|wife)\b",
    "Man": r"\b(man|men|male|gents|gentleman|boyfriend|husband)\b",
}
_KIDS_PATTERN = r"\b(kid|kids|child|children|toddler)\b"
_SUBGROUP_PATTERNS = {
    "Baby": r"\b(baby|babies|infant|newborn)\b",
    "Girls": r"\b(girl|girls)\b",
    "Boys": r"\b(boy|boys)\b",
}
_STOPWORDS = {
    "a", "an", "the", "for", "of", "in", "on", "with", "and", "or", "to", "me", "my",
    "some", "any", "please", "show", "find", "want", "need", "looking", "search",
    "give", "under", "above", "below", "is", "are", "this", "that", "it",
}
_KEYWORD_STOPWORDS = _STOPWORDS | {
    w
    for pattern in list(_GENDER_WORD_PATTERNS.values()) + [_KIDS_PATTERN] + list(_SUBGROUP_PATTERNS.values())
    for w in re.findall(r"[a-z]+", pattern)
}

_OVERSAMPLE = 6
_BOOST_PER_HIT = 0.15
_LOW_CONFIDENCE_DISTANCE = 1.1

# ---- Facets (real narrow-down chips) -------------------------------------
# `subcategory` is the closest thing this catalog has to an article type
# (Knitwear, Boots, Trench Coats…). It falls back to the coarse `category`
# when a record's subcategory is missing or a non-descriptive placeholder.
_FACET_JUNK = {"", "n.a.", "na", "view all", "view all fragrance", "view all make-up",
               "new", "latest", "burberry loves"}
_MAX_FACETS = 5
_MIN_FACET_COUNT = 2

SYSTEM_PROMPT = (
    "You are a helpful, friendly shopping assistant. Answer the user's "
    "question using ONLY the product information in the latest message — "
    "never invent products, brands, categories, or prices. Earlier messages "
    "are the conversation so far; use them to resolve follow-ups like 'show "
    "me more of those' or 'the third one'. "
    "If the latest message says the results span multiple categories, finish "
    "your reply with one short sentence inviting the user to narrow to one of "
    "those exact categories. If it doesn't say that, don't add such a line."
)

_MAX_HISTORY_CHARS = 1200


def _facet_key(product):
    sub = (product.get("subcategory") or "").strip()
    if sub.lower() not in _FACET_JUNK:
        return sub, "subcategory"
    cat = (product.get("category") or "").strip()
    if cat.lower() not in _FACET_JUNK:
        return cat, "category"
    return None, None


def compute_facets(products):
    """Real category distribution of a result set, as narrow-down chips.

    Counts are exact counts of the retrieved products — never invented.
    Returns at most _MAX_FACETS facets, each backed by >= _MIN_FACET_COUNT
    products, and only when the set genuinely spans 2+ categories (a narrow
    query whose results are all one type gets no facets).
    """
    counts, fields = {}, {}
    for p in products:
        label, field = _facet_key(p)
        if label is None:
            continue
        counts[label] = counts.get(label, 0) + 1
        fields[label] = field

    qualifying = [(label, n) for label, n in counts.items() if n >= _MIN_FACET_COUNT]
    if len(qualifying) < 2:
        return []

    qualifying.sort(key=lambda kv: (-kv[1], kv[0]))
    return [
        {"label": label, "count": n, "filter": {fields[label]: label}}
        for label, n in qualifying[:_MAX_FACETS]
    ]


def _matches_facet(product, facet):
    return all(
        str(product.get(k, "")).strip().lower() == str(v).strip().lower()
        for k, v in facet.items()
    )


def _shown_products_note(extra):
    products = (extra or {}).get("products") or []
    if not products:
        return ""
    listed = "; ".join(
        f"{i}. {p.get('name', '?')}" + (f" ({p['brand']})" if p.get("brand") else "")
        for i, p in enumerate(products[:8], 1)
    )
    return f"\n\n[Products shown, in order: {listed}]"


def _history_messages(history):
    """Prior turns as Groq chat messages. Assistant turns are truncated and
    annotated with the ordered product list they displayed so ordinal
    references ('the third one') resolve.
    """
    out = []
    for turn in history or []:
        role = turn.get("role")
        content = (turn.get("content") or "").strip()
        if role not in ("user", "assistant") or not content:
            continue
        if role == "assistant":
            content = content[:_MAX_HISTORY_CHARS] + _shown_products_note(turn.get("extra"))
        out.append({"role": role, "content": content})
    return out


def _rewrite_followup(user_query, history):
    """Rewrite a context-dependent follow-up ('more like the third one',
    'the cheaper ones') into a standalone search query so retrieval — not
    just the answer — benefits from history. Returns user_query unchanged if
    it's already standalone or the rewrite looks unusable.
    """
    convo = "\n".join(
        f"{t['role']}: {(t.get('content') or '')[:400]}"
        for t in history
        if t.get("role") in ("user", "assistant") and (t.get("content") or "").strip()
    )
    if not convo:
        return user_query
    try:
        resp = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You rewrite a shopper's latest message into a single "
                        "standalone product-search query, resolving references "
                        "like 'those', 'the third one', 'more like it' using the "
                        "conversation. If the message is already standalone, "
                        "return it unchanged. Reply with ONLY the query text."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Conversation so far:\n{convo}\n\n"
                        f"Latest message: {user_query}\n\nStandalone search query:"
                    ),
                },
            ],
        )
        rewritten = (resp.choices[0].message.content or "").strip().strip('"').strip()
        if rewritten and len(rewritten) <= 200:
            return rewritten
    except Exception:
        pass
    return user_query


def extract_query_intent(query):
    """Rule-based gender/age-group extraction, matched against the catalog's
    actual gender values (Man/Woman/Kids) and Kids' subcategory values
    (Baby/Girls/Boys). Deterministic and free — no extra LLM round-trip just
    to pull a slot out of a short query.
    """
    lower = query.lower()

    # Checked before generic girl/boy so "for my girlfriend" resolves to
    # Woman, not Kids.
    for gender, pattern in _GENDER_WORD_PATTERNS.items():
        if re.search(pattern, lower):
            return {"gender": gender, "kids_subgroup": None}

    if re.search(_KIDS_PATTERN, lower):
        for subgroup, pattern in _SUBGROUP_PATTERNS.items():
            if re.search(pattern, lower):
                return {"gender": "Kids", "kids_subgroup": subgroup}
        return {"gender": "Kids", "kids_subgroup": None}

    for subgroup, pattern in _SUBGROUP_PATTERNS.items():
        if re.search(pattern, lower):
            return {"gender": "Kids", "kids_subgroup": subgroup}

    return {"gender": None, "kids_subgroup": None}


def _content_words(query):
    words = re.findall(r"[a-z]+", query.lower())
    return [w for w in words if w not in _KEYWORD_STOPWORDS and len(w) > 2]


def search_products_smart(query, top_k=8, facet=None):
    """Hybrid retrieval: oversampled FAISS search, then a hard gender filter
    (when the query names one) and a lexical keyword boost, so an explicit
    gender and a rare style word ('floral') both actually constrain ranking
    instead of losing to generic embedding-distance overlap.

    Returns a dict: results (<=top_k products), intent (from
    extract_query_intent), ambiguous (True if no gender was named and the
    catalog itself has no dominant gender for this query — a real "who is
    this for?" case, not just a query that happens to omit the word),
    low_confidence (True if even the best match is a weak one, e.g. thin
    style coverage in this single-brand catalog).
    """
    candidates = search_products(query, top_k=top_k * _OVERSAMPLE)

    # A facet click is a hard narrow-down: keep only candidates in that
    # category (unless nothing in the pool matches, then degrade gracefully).
    if facet:
        in_facet = [p for p in candidates if _matches_facet(p, facet)]
        if in_facet:
            candidates = in_facet

    intent = extract_query_intent(query)
    words = _content_words(query)

    for p in candidates:
        text = f"{p['name']} {p.get('description', '')}".lower()
        hits = sum(1 for w in words if w in text)
        p["_boosted_distance"] = p["distance"] - (_BOOST_PER_HIT * hits)

    gender = intent["gender"]
    matched_count = None
    if gender:
        matching = sorted((p for p in candidates if p["gender"] == gender), key=lambda p: p["_boosted_distance"])
        rest = sorted((p for p in candidates if p["gender"] != gender), key=lambda p: p["_boosted_distance"])
        matched_count = len(matching)
        ranked = matching + rest
        ambiguous = False
    else:
        ranked = sorted(candidates, key=lambda p: p["_boosted_distance"])
        top10 = ranked[:10]
        genders_seen = [p["gender"] for p in top10]
        if top10 and genders_seen:
            top_share = max(genders_seen.count(g) for g in set(genders_seen)) / len(genders_seen)
            ambiguous = len(set(genders_seen)) >= 2 and top_share <= 0.7
        else:
            ambiguous = False

    results = ranked[:top_k]
    for p in results:
        p.pop("_boosted_distance", None)

    low_confidence = bool(results) and (
        results[0]["distance"] > _LOW_CONFIDENCE_DISTANCE
        or (gender is not None and matched_count is not None and matched_count < max(1, top_k // 2))
    )

    return {
        "results": results,
        "intent": intent,
        "ambiguous": ambiguous,
        "low_confidence": low_confidence,
    }


def answer_query(user_query, top_k=8, force=False, history=None, facet=None):
    # Step 0: If this is a follow-up in an ongoing thread, rewrite it into a
    # standalone query so retrieval (not just the answer) uses the history —
    # this also carries an earlier-established gender through a facet click
    # ("Show me the knitwear" -> "women's knitwear"). Skipped only when a
    # clarifying reply was already folded in (force).
    search_query = user_query
    if history and not force:
        search_query = _rewrite_followup(user_query, history)

    # Deterministically carry a gender/age-group established earlier in the
    # thread when the follow-up (e.g. a facet click like "Show me the
    # knitwear") doesn't name one itself. The LLM rewrite alone is not
    # reliable enough for this.
    if history and not extract_query_intent(search_query)["gender"]:
        for turn in reversed(history):
            if turn.get("role") != "user":
                continue
            prior_gender = extract_query_intent(turn.get("content") or "")["gender"]
            if prior_gender:
                search_query = f"{prior_gender} {search_query}"
                break

    # Step 1: Find relevant products via hybrid (filtered + boosted) search
    search = search_products_smart(search_query, top_k=top_k, facet=facet)

    # If the query doesn't name a gender/age group and this catalog genuinely
    # has no dominant one for it, ask instead of guessing — unless this is
    # already the follow-up turn after asking (force=True) or a facet click
    # (the user is narrowing by type, gender was settled earlier). Facets are
    # still returned so the UI can offer type chips alongside the question.
    if search["ambiguous"] and not force and not facet:
        return {
            "answer": (
                "Just to make sure I show you the right products — is this for "
                "men, women, or kids? (If it's for kids, let me know the age "
                "group too — baby, girls, or boys.)"
            ),
            "sources": [],
            "products": [],
            "clarifying": True,
            "facets": compute_facets(search["results"]),
        }

    relevant_products = search["results"]
    facets = compute_facets(relevant_products)

    # Step 2: Build context from retrieved products
    context = ""
    for p in relevant_products:
        context += f"Product: {p['name']}\n"
        context += f"Brand: {p.get('brand', 'N/A')}\n"
        context += f"Price: ${p.get('price', 'N/A')}\n"
        context += f"Description: {p['description']}\n\n"

    if search["low_confidence"]:
        context += (
            "Note: catalog coverage for this specific style/gender combination "
            "is thin — be upfront about that in your answer rather than "
            "overstating variety.\n\n"
        )

    if facets:
        labels = ", ".join(f"{f['label']} ({f['count']})" for f in facets)
        context += (
            f"These results span multiple categories: {labels}. After answering, "
            "add one short sentence inviting the user to narrow to one of these "
            "exact categories.\n\n"
        )

    # Step 3: Send to Groq LLM for a proper answer, with prior turns as context
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(_history_messages(history))
    messages.append(
        {
            "role": "user",
            "content": f"""Based on these products:

{context}

Answer this question: {user_query}""",
        }
    )

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": [p["name"] for p in relevant_products],
        "products": relevant_products,
        "clarifying": False,
        "facets": facets,
    }


def _format_listing(listing):
    rating = f"{listing.get('rating')}★" if listing.get("rating") is not None else "no rating"
    reviews = (
        f"{listing['review_count']} reviews"
        if listing.get("review_count") is not None
        else "no review count"
    )
    store = listing.get("store") or "Unknown store"
    return f"{store}: {listing.get('title')} — {listing.get('price')}, {rating}, {reviews}"


def answer_comparison_query(product, listings):
    """Ask the LLM to summarize live shopping listings for a product.

    `product` is a metadata dict from search_products(); `listings` is the
    list of 0..N dicts returned by price_compare.get_shopping_comparison().
    """
    lines = [
        f"Product: {product['name']}",
        f"Brand: {product.get('brand', 'N/A')}",
        f"Our catalog price: ${product.get('price', 'N/A')}",
        "",
    ]

    if listings:
        lines.append("Live marketplace listings:")
        for listing in listings:
            lines.append(f"- {_format_listing(listing)}")
    else:
        lines.append("No live marketplace data is currently available for this product.")

    context = "\n".join(lines)

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful shopping assistant comparing prices across "
                    "marketplaces. Summarize the price and review tradeoffs across "
                    "whichever stores are listed in the data — only ever refer to "
                    "stores that actually appear there, never invent ones that "
                    "aren't present. Style example: 'Found on Amazon for ₹1,299 "
                    "(4.2★, 340 reviews) and Flipkart for ₹999 (3.8★, 45 reviews). "
                    "Amazon is pricier but significantly better reviewed.' If no "
                    "live data is available, say so plainly instead of making up "
                    "numbers."
                ),
            },
            {"role": "user", "content": context},
        ],
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    # Test queries against the real fashion catalog
    queries = [
        "warm gloves for men under $600",
        "elegant wool cardigan for women",
        "affordable accessories"
    ]

    for query in queries:
        result = answer_query(query)
        print(f"\n❓ Query: {query}")
        print(f"💬 Answer: {result['answer']}")
        print(f"📎 Sources: {', '.join(result['sources'])}")
        print("-" * 50)
