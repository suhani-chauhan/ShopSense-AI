"""Representative test queries for the FAISS retrieval evaluation harness.

Mix of specific, broad, price-constrained, and gender/category-specific
queries against the 3,038-product Burberry catalog.
"""

QUERIES = [
    # Specific
    {"id": 1, "query": "black leather ankle boots"},
    {"id": 2, "query": "cashmere wool scarf"},
    {"id": 3, "query": "men's denim sneakers"},
    {"id": 4, "query": "gold hoop earrings"},
    # Broad
    {"id": 5, "query": "gift for my mom"},
    {"id": 6, "query": "something stylish for winter"},
    {"id": 7, "query": "everyday accessory"},
    {"id": 8, "query": "elegant outfit for a wedding"},
    # Price-constrained
    {"id": 9, "query": "winter coat under $500"},
    {"id": 10, "query": "affordable wallet under $300"},
    {"id": 11, "query": "luxury handbag over $2000"},
    {"id": 12, "query": "budget-friendly sunglasses under $200"},
    # Gender / category-specific
    {"id": 13, "query": "women's knitwear"},
    {"id": 14, "query": "men's hats and gloves"},
    {"id": 15, "query": "kids shoes"},
]
