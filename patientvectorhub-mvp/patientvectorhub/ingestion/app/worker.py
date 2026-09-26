"""
Ingestion service entrypoint.

Exposes POST /ingest which api-gateway calls after storing an uploaded
file. Runs the pipeline synchronously in-request for the MVP (no Kafka
queue) - acceptable at MVP document volumes; Phase 2 should move this
behind a real queue once throughput requires it.
"""
import sys
import os
import uuid
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))  # allow `vector_store_pkg` import outside Docker too

from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.db import SessionLocal
from app import models
from app.parser import parse_document
from app.chunker import chunk_text
from app.embedder import embed_texts, embedding_dim

from vector_store_pkg.qdrant_client import QdrantStore
from vector_store_pkg.schema import VectorRecord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingestion")

app = FastAPI(title="PatientVectorHub Ingestion", version="0.1.0-mvp")

_store = QdrantStore(url=settings.qdrant_url, collection=settings.qdrant_collection)


class IngestRequest(BaseModel):
    document_id: str
    storage_path: str
    tenant_id: str


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


def _run_pipeline(document_id: str, storage_path: str, tenant_id: str):
    db: Session = SessionLocal()
    try:
        doc = db.query(models.Document).filter_by(id=document_id).first()
        if doc is None:
            logger.error("document %s not found", document_id)
            return

        doc.status = "parsing"
        db.commit()

        text = parse_document(storage_path)
        pieces = chunk_text(text)
        if not pieces:
            doc.status = "failed"
            doc.error_message = "No extractable text (empty or scanned/image-only document)"
            db.commit()
            return

        doc.status = "embedding"
        db.commit()

        vectors = embed_texts(pieces)
        _store.ensure_collection(dim=embedding_dim())

        records = []
        chunk_rows = []
        for idx, (piece, vector) in enumerate(zip(pieces, vectors)):
            point_id = str(uuid.uuid4())
            records.append(VectorRecord(
                id=point_id,
                vector=vector,
                payload={"document_id": document_id, "tenant_id": tenant_id, "chunk_index": idx, "text": piece},
            ))
            chunk_rows.append(models.Chunk(
                id=str(uuid.uuid4()),
                document_id=document_id,
                tenant_id=tenant_id,
                chunk_index=idx,
                text=piece,
                vector_point_id=point_id,
            ))

        _store.upsert(records)
        db.add_all(chunk_rows)
        doc.status = "ready"
        db.commit()
        logger.info("document %s ingested: %d chunks", document_id, len(chunk_rows))

    except Exception as exc:  # noqa: BLE001 - MVP: surface any failure onto the document row
        logger.exception("ingestion failed for %s", document_id)
        doc = db.query(models.Document).filter_by(id=document_id).first()
        if doc:
            doc.status = "failed"
            doc.error_message = str(exc)[:2000]
            db.commit()
    finally:
        db.close()


@app.post("/ingest")
def ingest(req: IngestRequest):
    # Synchronous for MVP simplicity. If this becomes a latency problem for
    # the upload request, move to BackgroundTasks or a real queue.
    _run_pipeline(req.document_id, req.storage_path, req.tenant_id)
    return {"document_id": req.document_id, "status": "submitted"}
