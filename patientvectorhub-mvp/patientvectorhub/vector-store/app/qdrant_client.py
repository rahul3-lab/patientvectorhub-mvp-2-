"""
Qdrant implementation of the VectorStore contract.

This is the only backend wired up for the MVP. A `WeaviateStore` can be
added later implementing the same `VectorStore` ABC from schema.py without
touching ingestion or rag-engine call sites.
"""
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.schema import VectorStore, VectorRecord, ScoredRecord


class QdrantStore(VectorStore):
    def __init__(self, url: str, collection: str):
        self.client = QdrantClient(url=url)
        self.collection = collection

    def ensure_collection(self, dim: int) -> None:
        existing = [c.name for c in self.client.get_collections().collections]
        if self.collection not in existing:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=qmodels.VectorParams(size=dim, distance=qmodels.Distance.COSINE),
            )

    def upsert(self, records: list[VectorRecord]) -> None:
        points = [
            qmodels.PointStruct(id=r.id, vector=r.vector, payload=r.payload)
            for r in records
        ]
        self.client.upsert(collection_name=self.collection, points=points)

    def search(self, vector: list[float], top_k: int, tenant_id: str | None = None) -> list[ScoredRecord]:
        query_filter = None
        if tenant_id:
            query_filter = qmodels.Filter(
                must=[qmodels.FieldCondition(key="tenant_id", match=qmodels.MatchValue(value=tenant_id))]
            )
        results = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=top_k,
            query_filter=query_filter,
        )
        return [ScoredRecord(id=str(r.id), score=r.score, payload=r.payload or {}) for r in results]

    def delete_by_document(self, document_id: str) -> None:
        self.client.delete(
            collection_name=self.collection,
            points_selector=qmodels.FilterSelector(
                filter=qmodels.Filter(
                    must=[qmodels.FieldCondition(key="document_id", match=qmodels.MatchValue(value=document_id))]
                )
            ),
        )
