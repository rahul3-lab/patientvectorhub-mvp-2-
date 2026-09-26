"""
Query route: forwards to the rag-engine service, scoped to the caller's
tenant. The gateway itself holds no retrieval/LLM logic - that lives in
rag-engine per the service map.
"""
import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.auth import verify_shared_secret, get_current_tenant
from app.config import settings

router = APIRouter(prefix="/query", tags=["query"], dependencies=[Depends(verify_shared_secret)])


@router.post("")
async def query(
    payload: dict,
    tenant_name: str = Depends(get_current_tenant),
):
    question = payload.get("question")
    if not question:
        raise HTTPException(status_code=400, detail="'question' is required")

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(
                f"{settings.rag_engine_url}/answer",
                json={"question": question, "tenant_id": tenant_name, "top_k": payload.get("top_k", 5)},
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"rag-engine error: {exc}") from exc

    return resp.json()
