import pandas as pd
import numpy as np
import os
from sentence_transformers import SentenceTransformer

# ── Load cleaned data ────────────────────────────────────────────
df = pd.read_csv("data/metadata/products_clean.csv")
print(f"Products to embed: {len(df)}")

# ── Load embedding model ─────────────────────────────────────────
# This model converts text → 384 numbers that capture meaning
print("\nLoading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded!")

# ── Generate embeddings ──────────────────────────────────────────
print("\nGenerating embeddings... (this takes 1-2 minutes)")
descriptions = df["description"].tolist()
embeddings = model.encode(
    descriptions,
    batch_size=64,
    show_progress_bar=True
)

print(f"\nEmbedding shape: {embeddings.shape}")
# Should print (3038, 384) — 3038 products, 384 numbers each

# ── Save embeddings ──────────────────────────────────────────────
os.makedirs("data/embeddings", exist_ok=True)
np.save("data/embeddings/product_embeddings.npy", embeddings)
print("Saved → data/embeddings/product_embeddings.npy")

# ── Save matching metadata ───────────────────────────────────────
# IMPORTANT: same order as embeddings so row 0 = product 0
df.to_csv("data/embeddings/product_metadata.csv", index=False)
print("Saved → data/embeddings/product_metadata.csv")

# ── Quick sanity check ───────────────────────────────────────────
print("\n── Sanity Check ──")
print(f"Products : {len(df)}")
print(f"Embeddings: {embeddings.shape[0]}")
print(f"Match    : {len(df) == embeddings.shape[0]}")
print(f"\nFirst product : {df['name'].iloc[0]}")
print(f"Its embedding : {embeddings[0][:5]}...") # first 5 numbers