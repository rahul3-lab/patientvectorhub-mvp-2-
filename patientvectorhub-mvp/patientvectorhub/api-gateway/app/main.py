from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import health, documents, query

app = FastAPI(
    title="PatientVectorHub API Gateway",
    version="0.1.0-mvp",
    description="Entry point for document upload/status and RAG queries. "
                 "MVP auth = shared secret (see app/auth.py); Keycloak is Phase 2.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(documents.router)
app.include_router(query.router)
