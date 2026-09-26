# PatientVectorHub — MVP

A working, local-only slice of the full PatientVectorHub design: upload a
document → it gets parsed, chunked, embedded, and indexed → ask a question
→ get an answer grounded in retrieved excerpts.

This MVP was scoped for **one developer, 2–4 weeks, local/self-hosted
infra only** (no cloud spend required). It intentionally cuts several
pieces from the full architecture — see **"What's cut and why"** below
before you go looking for Keycloak or Kafka.

## Architecture (as built)

```
dashboard (React/Vite)
      │
      ▼
api-gateway (FastAPI)  ──► ingestion (FastAPI worker)  ──► Qdrant + Postgres
      │                                                        ▲
      ▼                                                        │
rag-engine (FastAPI)  ───────────────────────────────────────┘
      │
      ▼
  Ollama (local LLM) or OpenAI
```

- **api-gateway/** — upload/status/query routes, shared-secret auth, Alembic migrations (source of truth for the DB schema)
- **ingestion/** — parse (PDF/txt/md) → chunk → embed (local Bio_ClinicalBERT by default) → store
- **rag-engine/** — embed query → retrieve from Qdrant (tenant-scoped) → prompt → LLM → answer + sources
- **vector-store/** — `VectorStore` abstraction; only `QdrantStore` is implemented
- **dashboard/** — minimal upload + ask UI

## Quickstart (Windows/macOS/Linux, Docker required)

```bash
cp .env.example .env
docker-compose up -d postgres qdrant

# run migrations once (from api-gateway/, in a venv or via docker exec)
cd api-gateway
pip install -r requirements.txt
alembic upgrade head
cd ..

python infra/scripts/seed_db.py     # creates "demo-tenant"

docker-compose up --build
```

Then open the dashboard at `http://localhost:5173`.

**LLM setup:** by default `LLM_PROVIDER=ollama`. Install [Ollama](https://ollama.com)
on the host and run `ollama pull llama3.1:8b` before asking questions — or
set `LLM_PROVIDER=openai` and `OPENAI_API_KEY` in `.env` if you'd rather
pay per call than run a local model.

**First run note:** the embedding model (`Bio_ClinicalBERT`, ~400MB)
downloads from Hugging Face on first use and is cached after that.

## What's cut and why

The full service map (see original spec) calls for Keycloak, Vault,
Kafka, and a dual Weaviate/Qdrant abstraction. None of that fits in
"solo developer, 2–4 weeks, local-only" without either blowing the
timeline or shipping something that doesn't actually run end-to-end.
Cut for MVP:

| Full design | MVP replacement | Why |
|---|---|---|
| Keycloak (OIDC/identity) | Shared-secret bearer token + `X-Tenant-Id` header | Real auth is a multi-day integration on its own; a shared secret gets you tenant-scoped requests today |
| Vault (secrets mgmt) | `.env` file | No ops overhead for a single local deployment |
| Kafka (async messaging) | Direct synchronous HTTP call gateway → ingestion | At MVP document volumes, a queue adds infra without adding capability yet |
| Weaviate + Qdrant abstraction | Qdrant only, behind a `VectorStore` ABC | One less service to run locally; the ABC keeps Weaviate addable later without touching call sites |
| Redis (query caching) | None | No caching yet — add when latency/cost actually requires it |

**Everything above is still architected for**: `vector-store/app/schema.py`
defines the interface so a `WeaviateStore` can be dropped in later, and
`app/auth.py` isolates the auth mechanism so Keycloak can replace it
without touching route logic.

## Known gaps / Phase 2 backlog

- No OCR — scanned/image-only PDFs will fail ingestion with "no extractable text"
- No retry mechanism if ingestion is down when a doc is uploaded (it just stays `pending`)
- No per-user auth, only per-tenant shared secret
- No integration/unit tests included yet
- Chunking is word-count based, not a real tokenizer
- Multi-tenant isolation is a `tenant_id` filter, not DB-level row security

## Repo layout

```
api-gateway/      FastAPI entrypoint, auth, Alembic migrations
ingestion/         parse → chunk → embed → store pipeline
rag-engine/        retrieve → prompt → LLM → answer
vector-store/      shared VectorStore abstraction (Qdrant impl)
dashboard/          React/Vite upload + query UI
infra/scripts/      seed_db.py, init_qdrant.py
docker-compose.yml  Postgres + Qdrant + all 4 services + dashboard
```
