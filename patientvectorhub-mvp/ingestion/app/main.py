import hashlib
import os
import re
import uuid
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

VECTOR_STORE_URL = os.getenv("VECTOR_STORE_URL", "http://localhost:8003")
app = FastAPI(title="PatientVectorHub Ingestion", version="0.1.0")


class IngestRequest(BaseModel):
    patient_id: str
    filename: str
    content: str = Field(min_length=1)
    metadata: dict[str, str] = Field(default_factory=dict)


def tenant_id(x_tenant_id: Annotated[str | None, Header()] = None) -> str:
    if not x_tenant_id:
        raise HTTPException(400, "X-Tenant-ID header is required")
    return x_tenant_id


def chunk_text(text: str, size: int = 900, overlap: int = 150) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []
    return [normalized[i:i + size] for i in range(0, len(normalized), size - overlap)]


def embed(text: str, dimensions: int = 128) -> list[float]:
    # Stable local fallback; replace with OpenAI/Hugging Face embedding client in production.
    digest = hashlib.sha512(text.lower().encode()).digest()
    return [((digest[i % len(digest)] / 255) * 2) - 1 for i in range(dimensions)]


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ingestion"}


@app.post("/v1/ingest", status_code=202)
async def ingest(payload: IngestRequest, tenant: str = Depends(tenant_id)):
    document_id = str(uuid.uuid4())
    chunks = chunk_text(payload.content)
    records = [{"id": str(uuid.uuid4()), "tenant_id": tenant, "patient_id": payload.patient_id,
                "document_id": document_id, "text": chunk, "vector": embed(chunk),
                "metadata": {**payload.metadata, "filename": payload.filename, "chunk_index": str(index)}}
               for index, chunk in enumerate(chunks)]
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(f"{VECTOR_STORE_URL}/v1/vectors", json={"records": records})
        response.raise_for_status()
    return {"document_id": document_id, "chunks_indexed": len(records), "status": "accepted"}
