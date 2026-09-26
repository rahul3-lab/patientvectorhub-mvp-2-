# Architecture

## Data boundaries

`API Gateway -> Ingestion -> Vector Store` handles writes. `API Gateway -> RAG Engine -> Vector Store` handles reads. Tenant ID is mandatory at each public boundary and becomes part of each vector record; searches always filter by tenant.

## Production guardrails

- Use Keycloak JWT validation (`AUTH_MODE=keycloak`) and map the tenant to a verified claim; never trust a client-supplied tenant header in production.
- Encrypt transport, volumes, backups, and provider credentials. Store secrets in Vault or the deployment platform's secret manager.
- Add PostgreSQL metadata/audit persistence, Kafka retries/dead-letter topics, malware scanning, and document retention controls before handling PHI.
- Replace the template answer provider with an approved clinical LLM and require human review. This project is not a medical device and does not provide medical advice.

## Backend adapters

The in-memory adapter is intentionally the default so the demo is immediately runnable. The `VectorRepository` contract isolates persistence; production adapters should implement the same insert/search methods for Qdrant or Weaviate and run schema setup from `vector-store/scripts/setup_vector_schema.ps1`.
