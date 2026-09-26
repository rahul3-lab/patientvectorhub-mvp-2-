"""
Shared retrieval-storage contract.

MVP note: only Qdrant is implemented. The `VectorStore` interface below is
the abstraction point for adding Weaviate later (Phase 2) - ingestion and
rag-engine should only ever import VectorStore, never QdrantStore directly.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class VectorRecord:
    id: str
    vector: list[float]
    payload: dict = field(default_factory=dict)


@dataclass
class ScoredRecord:
    id: str
    score: float
    payload: dict


class VectorStore(ABC):
    @abstractmethod
    def ensure_collection(self, dim: int) -> None:
        ...

    @abstractmethod
    def upsert(self, records: list[VectorRecord]) -> None:
        ...

    @abstractmethod
    def search(self, vector: list[float], top_k: int, tenant_id: str | None = None) -> list[ScoredRecord]:
        ...

    @abstractmethod
    def delete_by_document(self, document_id: str) -> None:
        ...
