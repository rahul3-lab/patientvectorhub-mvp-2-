# PatientVectorHub

PatientVectorHub is a Windows-friendly, cloud-ready RAG platform starter for patient document workflows. It provides four isolated Python services, a React dashboard, and Docker Compose infrastructure that can be run locally or used as a foundation for cloud deployment.

## Quick start (Windows PowerShell)

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Open `http://localhost:8000/docs` for the gateway API and `http://localhost:5173` for the dashboard. The default development mode uses an in-memory vector backend; switch `VECTOR_BACKEND=qdrant` or `weaviate` once the corresponding service is healthy.

## Services

| Service | Port | Responsibility |
|---|---:|---|
| API Gateway | 8000 | CORS, health/readiness, tenant-aware proxy surface |
| Ingestion | 8001 | Parse, chunk, embed, and persist patient documents |
| RAG Engine | 8002 | Retrieve relevant chunks and orchestrate grounded answers |
| Vector Store | 8003 | Backend-neutral vector collection and similarity-search contract |
| Dashboard | 5173 | Upload documents and ask patient-context questions |

## API flow

1. `POST /v1/documents` at the gateway sends a document to ingestion.
2. Ingestion chunks the text, makes deterministic development embeddings (or OpenAI embeddings when configured), and writes chunks to Vector Store.
3. `POST /v1/query` retrieves scoped chunks and returns a grounded response with citations.

Every document and query requires an `X-Tenant-ID` header. Development values are accepted locally; production should set `AUTH_MODE=keycloak` and validate JWTs at the gateway.

## Development commands

```powershell
docker compose up --build
docker compose down
docker compose logs -f api-gateway
```

See `docs/architecture.md` for boundaries, security guidance, and cloud deployment notes.
