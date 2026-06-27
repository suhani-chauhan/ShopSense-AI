import faiss
import numpy as np
from transformers import BlipProcessor, BlipForConditionalGeneration
from sentence_transformers import SentenceTransformer
from PIL import Image

# Load BLIP for image captioning
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# Load SentenceTransformer for embeddings
embedder = SentenceTransformer("all-MiniLM-L6-v2")  # lightweight, fast

def describe_image(image_path):
    """Generate a text caption from an image."""
    img = Image.open(image_path).convert("RGB")
    inputs = processor(img, return_tensors="pt")
    out = model.generate(**inputs, max_new_tokens=30)
    return processor.decode(out[0], skip_special_tokens=True)

def embed_text(text):
    """Convert text into semantic embedding vector."""
    emb = embedder.encode([text])
    return np.array(emb, dtype="float32")

if __name__ == "__main__":
    # Step 1: Caption the sneaker image
    desc = describe_image("backend/sample_sneaker.png")
    print("Description:", desc)

    # Step 2: Create FAISS index
    dim = embed_text(desc).shape[1]  # embedding dimension
    index = faiss.IndexFlatL2(dim)

    # Step 3: Store description in FAISS
    vec = embed_text(desc)
    index.add(vec)
    print("Stored description in FAISS index")

    # Step 4: Query FAISS
    query = "red sneakers"
    qvec = embed_text(query)
    D, I = index.search(qvec, k=1)
    print("Closest product index:", I[0][0])
