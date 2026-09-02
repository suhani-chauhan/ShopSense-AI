# API Latency Benchmark

15 queries per endpoint, against `http://127.0.0.1:8000`.

| Endpoint | N | Min (s) | Max (s) | Avg (s) |
|---|---|---|---|---|
| POST /search/text | 15 | 0.014 | 0.076 | 0.031 |
| POST /chat | 15 | 0.513 | 2.100 | 0.954 |

**RAG answer-generation overhead over raw retrieval (avg /chat - avg /search/text): 0.923s**
