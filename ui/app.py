import os
import sys

import streamlit as st

# Ensure the repo root is on sys.path so `backend` can be imported as a
# package regardless of the working directory `streamlit run` is invoked from.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from backend.rag_pipeline import answer_query

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
    placeholder="e.g. warm gloves for men under $600"
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
    "warm gloves for men under $600",
    "elegant wool cardigan for women",
    "affordable accessories",
    "leather handbag under $1000"
]

cols = st.columns(4)
for i, example in enumerate(example_queries):
    with cols[i]:
        if st.button(example):
            with st.spinner("Searching..."):
                answer = answer_query(example)
            st.header("💬 Answer")
            st.write(answer)
