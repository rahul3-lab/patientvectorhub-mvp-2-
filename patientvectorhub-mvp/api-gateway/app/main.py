import os
from contextlib import asynccontextmanager
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

INGESTION_URL = os.getenv("INGESTION_URL", "http://localhost:8001")
RAG_ENGINE_URL = os.getenv("RAG_ENGINE_URL", "http://localhost:8002")


class DocumentRequest(BaseModel):
    patient_id: str = Field(min_length=1, max_length=128)
    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=2_000_000)
    metadata: dict[str, str] = Field(default_factory=dict)


class QueryRequest(BaseModel):
    patient_id: str = Field(min_length=1, max_length=128)
    question: str = Field(min_length=3, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)


def tenant_id(x_tenant_id: Annotated[str | None, Header()] = None) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header is required")
    return x_tenant_id


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient(timeout=30)
    yield
    await app.state.http.aclose()


app = FastAPI(title="PatientVectorHub API Gateway", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "api-gateway"}


@app.get("/ready")
async def ready(request: Request):
    results = {}
    for name, base_url in {"ingestion": INGESTION_URL, "rag_engine": RAG_ENGINE_URL}.items():
        try:
            response = await request.app.state.http.get(f"{base_url}/health")
            results[name] = response.status_code == 200
        except httpx.HTTPError:
            results[name] = False
    if not all(results.values()):
        raise HTTPException(status_code=503, detail=results)
    return {"status": "ready", "dependencies": results}


@app.post("/v1/documents", status_code=202)
async def ingest(payload: DocumentRequest, request: Request, tenant: str = Depends(tenant_id)):
    response = await request.app.state.http.post(f"{INGESTION_URL}/v1/ingest", json=payload.model_dump(), headers={"X-Tenant-ID": tenant})
    if response.is_error:
        raise HTTPException(response.status_code, response.text)
    return response.json()


@app.post("/v1/query")
async def query(payload: QueryRequest, request: Request, tenant: str = Depends(tenant_id)):
    response = await request.app.state.http.post(f"{RAG_ENGINE_URL}/v1/query", json=payload.model_dump(), headers={"X-Tenant-ID": tenant})
    if response.is_error:
        raise HTTPException(response.status_code, response.text)
    return response.json()
