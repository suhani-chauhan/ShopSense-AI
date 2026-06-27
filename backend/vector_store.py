import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

# Load embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Instead of loading BLIP here, we use pre-written descriptions
# (We already know BLIP works from image_to_text.py)
products = [
    {
        "id": 1,
        "name": "Nike Sneaker",
        "description": "a pair of red and white sneakers on a white background"
    },
    {
        "id": 2,
        "name": "Dell Laptop",
        "description": "a silver dell laptop with black keyboard and screen"
    },
    {
        "id": 3,
        "name": "Apple iPhone",
        "description": "a black apple iphone with large screen"
    }
]

def build_vector_store():
    descriptions = []
    metadata = []

    for product in products:
        print(f"Processing: {product['name']}")
        print(f"Description: {product['description']}")
        
        descriptions.append(product["description"])
        metadata.append(product)

    # Convert to embeddings
    embeddings = embedder.encode(descriptions)
    embeddings = np.array(embeddings, dtype="float32")

    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save FAISS index
    faiss.write_index(index, "backend/product_index.faiss")

    # Save metadata
    with open("backend/product_metadata.pkl", "wb") as f:
        pickle.dump(metadata, f)

    print("\n✅ Vector store built and saved!")
    print(f"Total products stored: {index.ntotal}")

if __name__ == "__main__":
    build_vector_store()