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


def render_result(result):
    st.header("💬 Answer")
    if result.get("caption"):
        st.caption(f"I see: {result['caption']}")
    st.write(result["answer"])
    if result.get("sources"):
        st.caption("Sources: " + ", ".join(result["sources"]))


def render_answer(query):
    with st.spinner("🔍 Searching products..."):
        result, error = call_chat_api(query)
    if error:
        st.error(error)
        return
    render_result(result)


def render_image_answer(uploaded_file):
    with st.spinner("🖼️ Analyzing image..."):
        result, error = call_chat_image_api(uploaded_file)
    if error:
        st.error(error)
        return
    render_result(result)


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

# Image search section
st.markdown("---")
st.header("📷 Or Search by Image")
uploaded_file = st.file_uploader("Upload a product photo", type=["jpg", "jpeg", "png"])

if st.button("🖼️ Search by Image", type="primary"):
    if uploaded_file is not None:
        render_image_answer(uploaded_file)
    else:
        st.warning("Please upload an image first!")

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
