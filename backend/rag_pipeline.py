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
    for idx in indices[0]:
        if idx != -1:
            results.append(metadata[idx])
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

    return response.choices[0].message.content


if __name__ == "__main__":
    # Test queries against the real fashion catalog
    queries = [
        "warm gloves for men under $600",
        "elegant wool cardigan for women",
        "affordable accessories"
    ]

    for query in queries:
        print(f"\n❓ Query: {query}")
        print(f"💬 Answer: {answer_query(query)}")
        print("-" * 50)
