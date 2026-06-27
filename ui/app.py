import streamlit as st
import sys
import os
import tempfile
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from groq import Groq

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load only these at startup (NO BLIP here)
embedder = SentenceTransformer("all-MiniLM-L6-v2")
groq_client = Groq(api_key="your_groq_api_key_here")

# Load FAISS
index = faiss.read_index("backend/product_index.faiss")
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
    relevant_products = search_products(user_query, top_k=3)
    context = ""
    for p in relevant_products:
        context += f"Product: {p['name']}\n"
        context += f"Description: {p['description']}\n\n"
    
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful shopping assistant. Use the product information provided to answer the user's question. Be friendly and helpful."
            },
            {
                "role": "user",
                "content": f"Based on these products:\n\n{context}\n\nAnswer this question: {user_query}"
            }
        ]
    )
    return response.choices[0].message.content

# Page config
st.set_page_config(
    page_title="🛒 AI Shopping Assistant",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 AI Shopping Assistant")
st.write("Ask a question to find the perfect product!")

# Sidebar
with st.sidebar:
    st.header("⚙️ Options")
    st.markdown("---")
    st.header("📦 About")
    st.write("This assistant uses:")
    st.write("- 🗄️ FAISS for product search")
    st.write("- 💬 Groq LLM for answers")

# Main query section
st.header("❓ Ask a Question")
query = st.text_input(
    "What are you looking for?",
    placeholder="e.g. Show me red sneakers"
)

if st.button("🔍 Search", type="primary"):
    if query:
        with st.spinner("🔍 Searching products..."):
            answer = answer_query(query)
        st.header("💬 Answer")
        st.write(answer)
    else:
        st.warning("Please enter a question!")

# Example queries
st.markdown("---")
st.header("💡 Try These Examples")

example_queries = [
    "Show me red sneakers",
    "I need a laptop for coding",
    "What phones do you have?",
    "Show me products under $500"
]

cols = st.columns(4)
for i, example in enumerate(example_queries):
    with cols[i]:
        if st.button(example):
            with st.spinner("Searching..."):
                answer = answer_query(example)
            st.header("💬 Answer")
            st.write(answer)