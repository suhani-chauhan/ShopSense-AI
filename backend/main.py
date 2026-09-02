import io
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import (and thereby load the FAISS index, metadata, embedding model,
    # and BLIP captioning model) once at startup rather than per-request.
    from backend.image_to_text import describe_image
    from backend.rag_pipeline import answer_query, metadata, search_products

    app.state.search_products = search_products
    app.state.answer_query = answer_query
    app.state.describe_image = describe_image
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


def _caption_from_upload(file: UploadFile, describe_image) -> str:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG and PNG images are supported.")

    contents = file.file.read()
    try:
        return describe_image(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not process image: {e}") from e


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
def chat_image(request: Request, file: UploadFile = File(...)):
    caption = _caption_from_upload(file, request.app.state.describe_image)

    try:
        result = request.app.state.answer_query(caption)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq request failed: {e}") from e

    return {"caption": caption, **result}
