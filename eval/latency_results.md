# API Latency Benchmark

15 queries per endpoint, against `http://127.0.0.1:8000`.

| Endpoint | N | Min (s) | Max (s) | Avg (s) |
|---|---|---|---|---|
| POST /search/text | 15 | 0.014 | 0.087 | 0.029 |
| POST /chat | 15 | 0.347 | 1.287 | 0.770 |

**RAG answer-generation overhead over raw retrieval (avg /chat - avg /search/text): 0.741s**
