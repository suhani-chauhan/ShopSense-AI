import html
import os
import textwrap

import requests
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")

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


def _shopping_card_html(listing):
    title = html.escape(listing.get("title") or "")
    store = html.escape(listing.get("store") or "Unknown store")
    price = html.escape(str(listing.get("price") or "N/A"))
    image_url = html.escape(listing.get("image_url") or "")
    url = html.escape(listing.get("url") or "#")

    old_price = listing.get("old_price")
    old_price_html = (
        f'<span class="sc-old-price">{html.escape(str(old_price))}</span>' if old_price else ""
    )

    delivery = listing.get("delivery")
    delivery_html = f'<div class="sc-delivery">{html.escape(delivery)}</div>' if delivery else ""

    image_html = f'<img class="sc-image" src="{image_url}" alt="{title}" />' if image_url else ""

    # Built as a single line, with no embedded newlines — a blank-looking
    # line here (e.g. from an empty image_html/delivery_html slot) would be
    # read by Streamlit's markdown parser as ending the raw-HTML block and
    # mangle everything that follows.
    return (
        f'<a class="sc-card" href="{url}" target="_blank" rel="noopener noreferrer">'
        f"{image_html}"
        f'<div class="sc-title">{title}</div>'
        f'<div class="sc-price-row"><span class="sc-price">{price}</span>{old_price_html}</div>'
        f'<div class="sc-store">{store}</div>'
        f"{delivery_html}"
        f"</a>"
    )


def render_comparison(result):
    st.subheader("💰 Price Comparison")

    listings = result.get("listings") or []
    if not listings:
        st.write(result.get("answer", ""))
        return

    cards = "".join(_shopping_card_html(listing) for listing in listings)

    carousel_html = textwrap.dedent(
        f"""
        <style>
        .sc-carousel {{
            display: flex;
            overflow-x: auto;
            gap: 12px;
            padding: 4px 4px 16px 4px;
        }}
        .sc-card {{
            flex: 0 0 200px;
            width: 200px;
            display: flex;
            flex-direction: column;
            background: var(--secondary-background-color);
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 10px;
            padding: 10px;
            text-decoration: none !important;
            color: inherit !important;
            transition: border-color 0.15s ease;
        }}
        .sc-card:hover {{
            border-color: rgba(128, 128, 128, 0.6);
        }}
        .sc-image {{
            width: 100%;
            aspect-ratio: 1 / 1;
            object-fit: cover;
            border-radius: 6px;
            margin-bottom: 8px;
            background: rgba(128, 128, 128, 0.08);
        }}
        .sc-title {{
            font-size: 0.85rem;
            line-height: 1.3em;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            min-height: 2.6em;
            margin-bottom: 6px;
            color: var(--text-color) !important;
            text-decoration: none !important;
        }}
        .sc-price-row {{
            margin-bottom: 4px;
        }}
        .sc-price {{
            font-weight: 700;
            font-size: 1rem;
            color: var(--text-color) !important;
        }}
        .sc-old-price {{
            text-decoration: line-through !important;
            opacity: 0.6;
            font-size: 0.78rem;
            margin-left: 6px;
            color: var(--text-color) !important;
        }}
        .sc-store {{
            font-size: 0.75rem;
            opacity: 0.65;
            color: var(--text-color) !important;
            text-decoration: none !important;
        }}
        .sc-delivery {{
            font-size: 0.72rem;
            opacity: 0.55;
            margin-top: 2px;
            color: var(--text-color) !important;
            text-decoration: none !important;
        }}
        </style>
        <div class="sc-carousel">{cards}</div>
        """
    ).strip()

    st.markdown(carousel_html, unsafe_allow_html=True)

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
