from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db

router = APIRouter(tags=["health"])


@router.get("/healthz")
def liveness():
    """Liveness: process is up. No dependency checks."""
    return {"status": "ok"}


@router.get("/readyz")
def readiness(db: Session = Depends(get_db)):
    """Readiness: can we actually reach Postgres."""
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return {"status": "ok" if db_ok else "degraded", "database": db_ok}
