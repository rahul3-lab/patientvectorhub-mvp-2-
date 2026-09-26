"""
Document upload + status routes.

The gateway does NOT parse/embed documents itself - it stores the file,
writes a `pending` row, and forwards the job to the ingestion service.
This keeps the gateway thin and matches the service-map split in the spec.
"""
import os
import shutil
import uuid

import httpx
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.auth import verify_shared_secret, get_current_tenant
from app.config import settings
from app.db import get_db
from app import models

router = APIRouter(prefix="/documents", tags=["documents"], dependencies=[Depends(verify_shared_secret)])

UPLOAD_DIR = "/data/uploads"


def _get_or_create_tenant(db: Session, tenant_name: str) -> models.Tenant:
    tenant = db.query(models.Tenant).filter_by(name=tenant_name).first()
    if tenant is None:
        tenant = models.Tenant(name=tenant_name)
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    return tenant


@router.post("")
async def upload_document(
    file: UploadFile = File(...),
    tenant_name: str = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    tenant = _get_or_create_tenant(db, tenant_name)

    ext = os.path.splitext(file.filename or "")[1]
    stored_name = f"{uuid.uuid4()}{ext}"
    stored_path = os.path.join(UPLOAD_DIR, stored_name)

    with open(stored_path, "wb") as out:
        shutil.copyfileobj(file.file, out)

    doc = models.Document(
        tenant_id=tenant.id,
        filename=file.filename or stored_name,
        storage_path=stored_path,
        status="pending",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Hand off to ingestion service. Fire-and-forget-ish: MVP has no Kafka,
    # so this is a direct HTTP call. If ingestion is down, the doc just
    # stays "pending" and a retry script (Phase 2) or manual re-POST here
    # would pick it up.
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                f"{settings.ingestion_url}/ingest",
                json={"document_id": doc.id, "storage_path": doc.storage_path, "tenant_id": tenant.id},
            )
    except httpx.HTTPError:
        # Don't fail the upload if ingestion is briefly unavailable.
        pass

    return {"document_id": doc.id, "status": doc.status}


@router.get("/{document_id}")
def get_document(
    document_id: str,
    tenant_name: str = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    doc = db.query(models.Document).filter_by(id=document_id).first()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "status": doc.status,
        "error_message": doc.error_message,
        "chunk_count": len(doc.chunks),
    }


@router.get("")
def list_documents(
    tenant_name: str = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    tenant = db.query(models.Tenant).filter_by(name=tenant_name).first()
    if tenant is None:
        return []
    return [
        {"document_id": d.id, "filename": d.filename, "status": d.status}
        for d in tenant.documents
    ]
