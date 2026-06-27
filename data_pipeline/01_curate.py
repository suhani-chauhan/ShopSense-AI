from datasets import load_dataset
import pandas as pd
import os

print("Downloading dataset...")
dataset = load_dataset("DBQ/Burberry.Product.prices.United.States", split="train")

df = pd.DataFrame(dataset)

print("Total products:", len(df))
print("\nColumns:", df.columns.tolist())
print("\nSample rows:")
print(df.head(3))

os.makedirs("data/metadata", exist_ok=True)
df.to_csv("data/metadata/products_raw.csv", index=False)
print("\nSaved to data/metadata/products_raw.csv")