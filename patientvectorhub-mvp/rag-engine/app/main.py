import hashlib
import os
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

VECTOR_STORE_URL = os.getenv("VECTOR_STORE_URL", "http://localhost:8003")
app = FastAPI(title="PatientVectorHub RAG Engine", version="0.1.0")


class QueryRequest(BaseModel):
    patient_id: str
    question: str = Field(min_length=3)
    top_k: int = Field(default=5, ge=1, le=20)


def tenant_id(x_tenant_id: Annotated[str | None, Header()] = None) -> str:
    if not x_tenant_id:
        raise HTTPException(400, "X-Tenant-ID header is required")
    return x_tenant_id


def embed(text: str, dimensions: int = 128) -> list[float]:
    digest = hashlib.sha512(text.lower().encode()).digest()
    return [((digest[i % len(digest)] / 255) * 2) - 1 for i in range(dimensions)]


@app.get("/health")
async def health():
    return {"status": "ok", "service": "rag-engine"}


@app.post("/v1/query")
async def query(payload: QueryRequest, tenant: str = Depends(tenant_id)):
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(f"{VECTOR_STORE_URL}/v1/search", json={"tenant_id": tenant, "patient_id": payload.patient_id, "vector": embed(payload.question), "top_k": payload.top_k})
        response.raise_for_status()
    matches = response.json()["matches"]
    if not matches:
        answer = "No indexed patient-document context was found for this question."
    else:
        excerpts = " ".join(match["text"] for match in matches[:2])
        answer = f"Based on the indexed document context: {excerpts[:1200]}"
    return {"answer": answer, "citations": [{"document_id": m["document_id"], "filename": m["metadata"].get("filename", "unknown"), "score": m["score"], "excerpt": m["text"][:240]} for m in matches], "disclaimer": "For workflow support only; not medical advice. Verify against the source record."}
