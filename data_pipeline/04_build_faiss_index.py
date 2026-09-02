import os
import pickle

import faiss
import numpy as np
import pandas as pd

_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMBEDDINGS_PATH = os.path.join(_ROOT_DIR, "data", "embeddings", "product_embeddings.npy")
METADATA_CSV_PATH = os.path.join(_ROOT_DIR, "data", "embeddings", "product_metadata.csv")
INDEX_OUT_PATH = os.path.join(_ROOT_DIR, "backend", "product_index.faiss")
METADATA_OUT_PATH = os.path.join(_ROOT_DIR, "backend", "product_metadata.pkl")

# ── Load real product embeddings + metadata ─────────────────────
print("Loading embeddings...")
embeddings = np.load(EMBEDDINGS_PATH).astype("float32")
print(f"Embeddings shape: {embeddings.shape}")

print("\nLoading metadata...")
df = pd.read_csv(METADATA_CSV_PATH)
print(f"Metadata rows: {len(df)}")

# ── Build FAISS index ─────────────────────────────────────────────
print("\nBuilding FAISS index (IndexFlatL2)...")
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# ── Save FAISS index ──────────────────────────────────────────────
os.makedirs(os.path.dirname(INDEX_OUT_PATH), exist_ok=True)
faiss.write_index(index, INDEX_OUT_PATH)
print(f"Saved FAISS index -> {INDEX_OUT_PATH}")

# ── Save metadata (same row order as embeddings) ──────────────────
metadata = df.to_dict(orient="records")
with open(METADATA_OUT_PATH, "wb") as f:
    pickle.dump(metadata, f)
print(f"Saved metadata -> {METADATA_OUT_PATH}")

# ── Sanity check ────────────────────────────────────────────────
print("\n-- Sanity Check --")
print(f"index.ntotal  : {index.ntotal}")
print(f"len(metadata) : {len(metadata)}")
assert index.ntotal == 3038, f"Expected 3038 vectors, got {index.ntotal}"
assert len(metadata) == 3038, f"Expected 3038 metadata rows, got {len(metadata)}"
print("index.ntotal == 3038 and len(metadata) == 3038 -- OK")
