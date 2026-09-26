"""
RAG Engine service entrypoint. POST /answer runs retrieve -> prompt -> LLM
and returns the answer plus the source excerpts, so the dashboard can show
citations.
"""
from fastapi import FastAPI
from pydantic import BaseModel

from app.config import settings
from app.retriever import retrieve
from app.prompt import build_prompt, SYSTEM_PROMPT
from app.llm import generate_answer

app = FastAPI(title="PatientVectorHub RAG Engine", version="0.1.0-mvp")


class AnswerRequest(BaseModel):
    question: str
    tenant_id: str
    top_k: int | None = None


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/answer")
def answer(req: AnswerRequest):
    top_k = req.top_k or settings.default_top_k
    contexts = retrieve(req.question, req.tenant_id, top_k)

    if not contexts:
        return {
            "answer": "I don't have any ingested documents to answer this from yet for this tenant.",
            "sources": [],
        }

    prompt = build_prompt(req.question, contexts)
    answer_text = generate_answer(SYSTEM_PROMPT, prompt)

    return {
        "answer": answer_text,
        "sources": [
            {
                "document_id": c.payload.get("document_id"),
                "chunk_index": c.payload.get("chunk_index"),
                "score": c.score,
                "excerpt": c.payload.get("text", "")[:300],
            }
            for c in contexts
        ],
    }
