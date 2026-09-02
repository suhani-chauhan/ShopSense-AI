import os

import requests
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

BACKEND_DOWN_MESSAGE = (
    "Backend not running — start it with: uvicorn backend.main:app --reload"
)


def call_chat_api(query):
    """POST query to the /chat endpoint. Returns (result, error_message)."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat", json={"query": query}, timeout=60
        )
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.ConnectionError:
        return None, BACKEND_DOWN_MESSAGE
    except requests.exceptions.HTTPError:
        detail = response.json().get("detail", response.text)
        return None, f"Backend error: {detail}"
    except requests.exceptions.RequestException as e:
        return None, f"Backend error: {e}"


def render_answer(query):
    with st.spinner("🔍 Searching products..."):
        result, error = call_chat_api(query)

    if error:
        st.error(error)
        return

    st.header("💬 Answer")
    st.write(result["answer"])
    if result.get("sources"):
        st.caption("Sources: " + ", ".join(result["sources"]))


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
        render_answer(query)
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
            render_answer(example)
