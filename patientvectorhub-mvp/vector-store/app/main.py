from math import sqrt
from threading import Lock

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="PatientVectorHub Vector Store", version="0.1.0")
records: list[dict] = []
lock = Lock()


class VectorRecord(BaseModel):
    id: str
    tenant_id: str
    patient_id: str
    document_id: str
    text: str
    vector: list[float]
    metadata: dict[str, str] = Field(default_factory=dict)


class InsertRequest(BaseModel):
    records: list[VectorRecord]


class SearchRequest(BaseModel):
    tenant_id: str
    patient_id: str
    vector: list[float]
    top_k: int = Field(default=5, ge=1, le=20)


def cosine(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    magnitude = sqrt(sum(a * a for a in left)) * sqrt(sum(b * b for b in right))
    return dot / magnitude if magnitude else 0.0


@app.get("/health")
async def health():
    return {"status": "ok", "service": "vector-store", "backend": "memory"}


@app.post("/v1/vectors", status_code=201)
async def insert(payload: InsertRequest):
    with lock:
        records.extend(record.model_dump() for record in payload.records)
    return {"inserted": len(payload.records)}


@app.post("/v1/search")
async def search(payload: SearchRequest):
    with lock:
        candidates = [r for r in records if r["tenant_id"] == payload.tenant_id and r["patient_id"] == payload.patient_id]
    ranked = sorted(candidates, key=lambda r: cosine(payload.vector, r["vector"]), reverse=True)[:payload.top_k]
    return {"matches": [{"id": r["id"], "document_id": r["document_id"], "text": r["text"], "metadata": r["metadata"], "score": round(cosine(payload.vector, r["vector"]), 4)} for r in ranked]}
