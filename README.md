# multimodal-rag-assistant
AI shopping assistant using multimodal RAG.

## Running the app

The app is split into two processes: a FastAPI backend (search + RAG) and a
Streamlit UI that talks to it over HTTP. Start both, in two terminals, from
the repo root.

1. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and set your `GROQ_API_KEY`.

3. Terminal 1 — start the API:

   ```
   uvicorn backend.main:app --reload --port 8000
   ```

4. Terminal 2 — start the UI:

   ```
   streamlit run ui/app.py
   ```

The UI expects the API at `http://127.0.0.1:8000` by default; override with
the `API_BASE_URL` environment variable if the API runs elsewhere.

> **Why `127.0.0.1` and not `localhost`?** On Windows, `localhost` can
> resolve to the IPv6 loopback address first; since the API here only binds
> to IPv4, that adds a multi-second connection stall per request. Using
> `127.0.0.1` directly avoids it — when testing with `curl` or a browser,
> prefer `http://127.0.0.1:8000` over `http://localhost:8000` too.
