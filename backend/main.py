import io
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend import database

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}
TITLE_LENGTH = 40


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import (and thereby load the FAISS index, metadata, embedding model,
    # and BLIP captioning model) once at startup rather than per-request.
    from backend.image_to_text import describe_image
    from backend.price_compare import get_shopping_comparison, resolve_direct_link
    from backend.rag_pipeline import (
        answer_comparison_query,
        answer_query,
        metadata,
        search_products,
        search_products_smart,
    )

    database.init_db()

    app.state.search_products = search_products
    app.state.search_products_smart = search_products_smart
    app.state.answer_query = answer_query
    app.state.answer_comparison_query = answer_comparison_query
    app.state.describe_image = describe_image
    app.state.get_shopping_comparison = get_shopping_comparison
    app.state.resolve_direct_link = resolve_direct_link
    app.state.products_loaded = len(metadata)

    yield


app = FastAPI(title="ShopSense AI API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=3, ge=1)


class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[int] = None
    # A narrow-down facet chosen from the previous turn's facet chips, e.g.
    # {"subcategory": "Knitwear"}. Only honoured when conversation_id is set.
    facet: Optional[dict] = None


class CompareRequest(BaseModel):
    query: str
    conversation_id: Optional[int] = None


class ResolveLinkRequest(BaseModel):
    page_token: str
    store: str


class SaveProductRequest(BaseModel):
    product_id: int
    name: str
    brand: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None


def _caption_from_upload(file: UploadFile, describe_image) -> str:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG and PNG images are supported.")

    contents = file.file.read()
    try:
        return describe_image(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not process image: {e}") from e


def _require_conversation(conversation_id: Optional[int]):
    if conversation_id is not None and not database.conversation_exists(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found.")


def _persist_exchange(conversation_id, user_content, assistant_content, title_seed, extra=None):
    database.add_message(conversation_id, "user", user_content)
    database.add_message(conversation_id, "assistant", assistant_content, extra=extra)
    database.set_title_if_default(conversation_id, title_seed[:TITLE_LENGTH].strip())


@app.get("/health")
def health(request: Request):
    return {"status": "ok", "products_loaded": request.app.state.products_loaded}


@app.post("/search/text")
def search_text(body: SearchRequest, request: Request):
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    return request.app.state.search_products(body.query, top_k=body.top_k)


def _effective_query(body: ChatRequest) -> tuple[str, bool]:
    """If the previous assistant turn asked a clarifying question, fold this
    turn's reply (e.g. "for women") into that original query so the follow-up
    search actually applies it, instead of searching on "for women" alone.
    Returns (query_to_search, force) — force=True skips asking again.
    """
    if body.conversation_id is None:
        return body.query, False

    last_two = database.get_last_two_messages(body.conversation_id)
    if len(last_two) == 2:
        prev_user, prev_assistant = last_two
        if (
            prev_assistant["role"] == "assistant"
            and prev_user["role"] == "user"
            and (prev_assistant["extra"] or {}).get("clarifying")
        ):
            return f"{prev_user['content']} {body.query}", True

    return body.query, False


@app.post("/chat")
def chat(body: ChatRequest, request: Request):
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    _require_conversation(body.conversation_id)

    query, force = _effective_query(body)

    # Feed the last few turns back into the model so follow-ups resolve.
    # Behaviour is unchanged when no conversation_id is supplied.
    history = (
        database.get_recent_messages(body.conversation_id, limit=6)
        if body.conversation_id is not None
        else None
    )

    try:
        result = request.app.state.answer_query(
            query, force=force, history=history, facet=body.facet
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq request failed: {e}") from e

    # The query that actually produced this answer — may be `body.query`
    # combined with an earlier turn (see _effective_query). Persisted and
    # returned so a later "Compare prices" click on this exact message
    # searches on what was actually answered, not just the previous message
    # in the thread (which, after a clarification exchange, can be a bare
    # one-word reply like "women").
    result["effective_query"] = query

    if body.conversation_id is not None:
        _persist_exchange(
            body.conversation_id,
            body.query,
            result["answer"],
            title_seed=body.query,
            extra={
                "sources": result.get("sources"),
                "products": result.get("products"),
                "clarifying": result.get("clarifying", False),
                "effective_query": query,
                "facets": result.get("facets"),
            },
        )

    return result


@app.post("/chat/compare")
def chat_compare(body: CompareRequest, request: Request):
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    _require_conversation(body.conversation_id)

    results = request.app.state.search_products_smart(body.query, top_k=1)["results"]
    if not results:
        raise HTTPException(status_code=404, detail="No matching product found.")

    top_product = results[0]
    listings = request.app.state.get_shopping_comparison(top_product["name"])

    try:
        answer = request.app.state.answer_comparison_query(top_product, listings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq request failed: {e}") from e

    if body.conversation_id is not None:
        _persist_exchange(
            body.conversation_id,
            f"[Compare prices] {body.query}",
            answer,
            title_seed=body.query,
            extra={"product": top_product, "listings": listings},
        )

    return {"product": top_product, "listings": listings, "answer": answer}


@app.post("/resolve-listing-link")
def resolve_listing_link(body: ResolveLinkRequest, request: Request):
    if not body.page_token.strip() or not body.store.strip():
        raise HTTPException(status_code=400, detail="page_token and store must not be empty.")

    url = request.app.state.resolve_direct_link(body.page_token, body.store)
    return {"url": url}


@app.post("/search/image")
def search_image(
    request: Request,
    file: UploadFile = File(...),
    top_k: int = Form(default=3, ge=1),
):
    caption = _caption_from_upload(file, request.app.state.describe_image)
    results = request.app.state.search_products(caption, top_k=top_k)
    return {"caption": caption, "results": results}


@app.post("/chat/image")
def chat_image(
    request: Request,
    file: UploadFile = File(...),
    conversation_id: Optional[int] = Form(default=None),
):
    _require_conversation(conversation_id)

    caption = _caption_from_upload(file, request.app.state.describe_image)

    history = (
        database.get_recent_messages(conversation_id, limit=6)
        if conversation_id is not None
        else None
    )

    try:
        result = request.app.state.answer_query(caption, history=history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq request failed: {e}") from e

    if conversation_id is not None:
        _persist_exchange(
            conversation_id,
            f"[Image search] {caption}",
            result["answer"],
            title_seed=caption,
            extra={
                "caption": caption,
                "sources": result.get("sources"),
                "products": result.get("products"),
                "clarifying": result.get("clarifying", False),
                "effective_query": caption,
                "facets": result.get("facets"),
            },
        )

    return {"caption": caption, "effective_query": caption, **result}


@app.post("/conversations")
def create_conversation():
    return database.create_conversation()


@app.get("/conversations")
def list_conversations():
    return database.list_conversations()


@app.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: int):
    conversation = database.get_conversation_messages(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conversation


@app.delete("/conversations/{conversation_id}")
def remove_conversation(conversation_id: int):
    if not database.delete_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"deleted": True}


@app.post("/saved-products")
def save_product(body: SaveProductRequest):
    return database.create_saved_product(
        body.product_id, body.name, body.brand, body.price, body.image_url, body.product_url
    )


@app.get("/saved-products")
def get_saved_products():
    return database.list_saved_products()


@app.delete("/saved-products/{saved_id}")
def remove_saved_product(saved_id: int):
    if not database.delete_saved_product(saved_id):
        raise HTTPException(status_code=404, detail="Saved product not found.")
    return {"deleted": True}
