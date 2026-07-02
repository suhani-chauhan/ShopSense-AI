import pandas as pd
import os

# ── Load raw data ────────────────────────────────────────────────
df = pd.read_csv("data/metadata/products_raw.csv")
print("Raw shape:", df.shape)

# ── Select only useful columns ───────────────────────────────────
df = df[[
    "title",         # product name
    "brand",         # brand name
    "category1_code",# gender (MAN/WOMAN)
    "category2_code",# main category (CLOTHES, ACCESSORIES etc)
    "category3_code",# subcategory (KNITWEAR, HATS etc)
    "price",         # price in USD
    "imageurl",      # product image URL
    "itemurl"        # product page URL
]].copy()

# ── Rename to clean names ────────────────────────────────────────
df.rename(columns={
    "title"         : "name",
    "category1_code": "gender",
    "category2_code": "category",
    "category3_code": "subcategory",
    "imageurl"      : "image_url",
    "itemurl"       : "product_url"
}, inplace=True)

# ── Drop rows missing critical fields ────────────────────────────
df.dropna(subset=["name", "price"], inplace=True)

# ── Clean each column ────────────────────────────────────────────
df["name"]        = df["name"].str.strip().str.title()
df["gender"]      = df["gender"].str.strip().str.title().fillna("Unisex")
df["category"]    = df["category"].str.strip().str.title().fillna("General")
df["subcategory"] = df["subcategory"].str.strip().str.title().fillna("General")
df["brand"]       = df["brand"].str.strip().str.title().fillna("Burberry")

# ── Clean price ──────────────────────────────────────────────────
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df.dropna(subset=["price"], inplace=True)
df["price"] = df["price"].round(2)

# ── Add price range bucket ───────────────────────────────────────
def price_bucket(p):
    if p < 300:   return "budget"
    elif p < 700: return "mid-range"
    else:         return "premium"

df["price_range"] = df["price"].apply(price_bucket)

# ── Build description ────────────────────────────────────────────
# This is the most important column — it gets embedded into FAISS
# The richer and cleaner this is, the better the search results
df["description"] = (
    df["name"] + ". " +
    "Brand: " + df["brand"] + ". " +
    "Gender: " + df["gender"] + ". " +
    "Category: " + df["category"] + " - " + df["subcategory"] + ". " +
    "Price: $" + df["price"].astype(str) + " (" + df["price_range"] + " range)."
)

# ── Add unique ID ────────────────────────────────────────────────
df.reset_index(drop=True, inplace=True)
df.insert(0, "id", df.index + 1)

# ── Final column order ───────────────────────────────────────────
df = df[[
    "id", "name", "brand", "gender",
    "category", "subcategory",
    "price", "price_range",
    "description", "image_url", "product_url"
]]

# ── Save ─────────────────────────────────────────────────────────
os.makedirs("data/metadata", exist_ok=True)
df.to_csv("data/metadata/products_clean.csv", index=False)

print(f"\n✅ Cleaned products : {len(df)}")
print(f"\nPrice range breakdown:")
print(df["price_range"].value_counts())
print(f"\nGender breakdown:")
print(df["gender"].value_counts())
print(f"\nSample description:")
print(df["description"].iloc[0])
print(f"\nSaved → data/metadata/products_clean.csv")