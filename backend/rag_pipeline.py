import os
import pickle

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


def answer_query(user_query):
    # Step 1: Find relevant products from FAISS
    relevant_products = search_products(user_query, top_k=3)

    # Step 2: Build context from retrieved products
    context = ""
    for p in relevant_products:
        context += f"Product: {p['name']}\n"
        context += f"Brand: {p.get('brand', 'N/A')}\n"
        context += f"Price: ${p.get('price', 'N/A')}\n"
        context += f"Description: {p['description']}\n\n"

    # Step 3: Send to Groq LLM for a proper answer
    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful shopping assistant. Use the product information provided to answer the user's question. Be friendly and helpful."
            },
            {
                "role": "user",
                "content": f"""Based on these products:

{context}

Answer this question: {user_query}"""
            }
        ]
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": [p["name"] for p in relevant_products],
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
