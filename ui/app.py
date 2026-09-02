import os

import requests
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

BACKEND_DOWN_MESSAGE = (
    "Backend not running — start it with: uvicorn backend.main:app --reload"
)


def _post(endpoint, **kwargs):
    """POST to the API and return (json_result, error_message)."""
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", timeout=60, **kwargs)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.ConnectionError:
        return None, BACKEND_DOWN_MESSAGE
    except requests.exceptions.HTTPError:
        detail = response.json().get("detail", response.text)
        return None, f"Backend error: {detail}"
    except requests.exceptions.RequestException as e:
        return None, f"Backend error: {e}"


def call_chat_api(query):
    return _post("/chat", json={"query": query})


def call_chat_image_api(uploaded_file):
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    return _post("/chat/image", files=files)


def call_compare_api(query):
    return _post("/chat/compare", json={"query": query})


def render_result(result):
    st.header("💬 Answer")
    if result.get("caption"):
        st.caption(f"I see: {result['caption']}")
    st.write(result["answer"])
    if result.get("sources"):
        st.caption("Sources: " + ", ".join(result["sources"]))


def render_comparison(result):
    st.subheader("💰 Price Comparison")

    comparison = result.get("comparison", {})
    col_amazon, col_flipkart = st.columns(2)
    for col, platform, label in (
        (col_amazon, "amazon", "🅰️ Amazon"),
        (col_flipkart, "flipkart", "🅵 Flipkart"),
    ):
        data = comparison.get(platform)
        with col:
            st.markdown(f"**{label}**")
            if data:
                st.write(data.get("title") or "—")
                st.write(f"💵 {data.get('price', 'N/A')}")
                rating = f"{data['rating']}★" if data.get("rating") is not None else "No rating"
                reviews = f"({data['reviews']} reviews)" if data.get("reviews") is not None else ""
                st.write(f"⭐ {rating} {reviews}".strip())
                if data.get("url"):
                    st.markdown(f"[View listing]({data['url']})")
            else:
                st.write("No result found")

    st.write(result.get("answer", ""))


def run_search(query):
    with st.spinner("🔍 Searching products..."):
        result, error = call_chat_api(query)
    st.session_state.last_query = query
    st.session_state.last_result = result
    st.session_state.last_error = error
    st.session_state.comparison_result = None
    st.session_state.comparison_error = None


def run_image_search(uploaded_file):
    with st.spinner("🖼️ Analyzing image..."):
        result, error = call_chat_image_api(uploaded_file)
    st.session_state.last_query = result.get("caption") if result else None
    st.session_state.last_result = result
    st.session_state.last_error = error
    st.session_state.comparison_result = None
    st.session_state.comparison_error = None


def run_price_comparison():
    with st.spinner("💰 Comparing prices..."):
        result, error = call_compare_api(st.session_state.last_query)
    st.session_state.comparison_result = result
    st.session_state.comparison_error = error


for key in ("last_query", "last_result", "last_error", "comparison_result", "comparison_error"):
    st.session_state.setdefault(key, None)


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
    st.write("- 🖼️ BLIP for image captioning")
    st.write("- 💬 Groq LLM for answers")
    st.write("- 💰 SerpAPI for live price comparison")

# Main query section
st.header("❓ Ask a Question")
query = st.text_input(
    "What are you looking for?",
    placeholder="e.g. warm gloves for men under $600"
)

if st.button("🔍 Search", type="primary"):
    if query:
        run_search(query)
    else:
        st.warning("Please enter a question!")

# Image search section
st.markdown("---")
st.header("📷 Or Search by Image")
uploaded_file = st.file_uploader("Upload a product photo", type=["jpg", "jpeg", "png"])

if st.button("🖼️ Search by Image", type="primary"):
    if uploaded_file is not None:
        run_image_search(uploaded_file)
    else:
        st.warning("Please upload an image first!")

# Result + price comparison (persisted across reruns via session_state)
if st.session_state.last_error:
    st.error(st.session_state.last_error)
elif st.session_state.last_result:
    render_result(st.session_state.last_result)

    if st.button("🔍 Compare prices"):
        run_price_comparison()

    if st.session_state.comparison_error:
        st.error(st.session_state.comparison_error)
    elif st.session_state.comparison_result:
        render_comparison(st.session_state.comparison_result)

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
            run_search(example)
