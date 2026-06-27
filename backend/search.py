import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

# Load embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index
index = faiss.read_index("backend/product_index.faiss")

# Load metadata
with open("backend/product_metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

def search_products(query, top_k=3):
    # Convert query to numbers
    query_embedding = embedder.encode([query])
    query_embedding = np.array(query_embedding, dtype="float32")

    # Search FAISS
    distances, indices = index.search(query_embedding, top_k)

    # Return results
    results = []
    for i, idx in enumerate(indices[0]):
        if idx != -1:
            results.append({
                "rank": i + 1,
                "product": metadata[idx]["name"],
                "description": metadata[idx]["description"],
                "distance": round(float(distances[0][i]), 4)
            })
    return results

if __name__ == "__main__":
    # Test with different queries
    queries = [
        "red running shoes",
        "laptop for coding",
        "smartphone with big screen"
    ]
    
    for query in queries:
        print(f"\n🔍 Searching for: '{query}'")
        results = search_products(query, top_k=1)
        for r in results:
            print(f"✅ Best match: {r['product']}")
            print(f"   Description: {r['description']}")
            print(f"   Distance: {r['distance']}")