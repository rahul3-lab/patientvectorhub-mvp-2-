"""
Retrieval: embed the question with the same embedding backend used at
ingest time, then search Qdrant scoped to the caller's tenant.

MVP does not cache in Redis (spec lists Redis as a rag-engine dependency
for future query/response caching) - added when latency/cost actually
warrants it.
"""
from functools import lru_cache

from app.config import settings
from vector_store_pkg.qdrant_client import QdrantStore
from vector_store_pkg.schema import ScoredRecord

_store = QdrantStore(url=settings.qdrant_url, collection=settings.qdrant_collection)


@lru_cache(maxsize=1)
def _local_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(settings.embedding_model)


def _embed_query(question: str) -> list[float]:
    if settings.embedding_provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        resp = client.embeddings.create(model=settings.openai_embedding_model, input=[question])
        return resp.data[0].embedding

    model = _local_model()
    return model.encode([question], normalize_embeddings=True)[0].tolist()


def retrieve(question: str, tenant_id: str, top_k: int) -> list[ScoredRecord]:
    vector = _embed_query(question)
    return _store.search(vector=vector, top_k=top_k, tenant_id=tenant_id)
