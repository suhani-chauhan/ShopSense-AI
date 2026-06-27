import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from groq import Groq

# Load models
embedder = SentenceTransformer("all-MiniLM-L6-v2")
groq_client = Groq(api_key="***REMOVED-GROQ-API-KEY***")

# Load FAISS index
index = faiss.read_index("backend/product_index.faiss")

# Load metadata
with open("backend/product_metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

def search_products(query, top_k=3):
    query_embedding = embedder.encode([query])
    query_embedding = np.array(query_embedding, dtype="float32")
    distances, indices = index.search(query_embedding, top_k)
    
    results = []
    for i, idx in enumerate(indices[0]):
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
        context += f"Description: {p['description']}\n\n"
    
    # Step 3: Send to Groq LLM for a proper answer
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
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
    # Test queries
    queries = [
        "Show me red sneakers",
        "I need a laptop for coding",
        "What phones do you have?"
    ]
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        print(f"💬 Answer: {answer_query(query)}")
        print("-" * 50)