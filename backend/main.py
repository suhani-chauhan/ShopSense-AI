from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import (and thereby load the FAISS index, metadata, and embedding
    # model) once at startup rather than per-request.
    from backend.rag_pipeline import answer_query, metadata, search_products

    app.state.search_products = search_products
    app.state.answer_query = answer_query
    app.state.products_loaded = len(metadata)

    yield


app = FastAPI(title="ShopSense AI API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=3, ge=1)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health(request: Request):
    return {"status": "ok", "products_loaded": request.app.state.products_loaded}


@app.post("/search/text")
def search_text(body: SearchRequest, request: Request):
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    return request.app.state.search_products(body.query, top_k=body.top_k)


@app.post("/chat")
def chat(body: ChatRequest, request: Request):
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    try:
        return request.app.state.answer_query(body.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq request failed: {e}") from e
