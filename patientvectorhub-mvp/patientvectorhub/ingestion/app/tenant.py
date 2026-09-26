"""Tenant lookup helper - keeps ingestion from needing the full Tenant model."""
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_tenant_name(db: Session, tenant_id: str) -> str | None:
    row = db.execute(text("SELECT name FROM tenants WHERE id = :id"), {"id": tenant_id}).first()
    return row[0] if row else None
