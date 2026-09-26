"""
Prompt assembly for the RAG answer step. Deliberately simple string
templating for the MVP - no prompt-management framework.
"""
from vector_store_pkg.schema import ScoredRecord

SYSTEM_PROMPT = (
    "You are a clinical document assistant. Answer the user's question using "
    "ONLY the provided context excerpts from the patient's documents. If the "
    "context does not contain the answer, say you don't have enough "
    "information - do not guess or fabricate clinical details. Be concise."
)


def build_prompt(question: str, contexts: list[ScoredRecord]) -> str:
    context_block = "\n\n".join(
        f"[Excerpt {i+1}] {c.payload.get('text', '')}" for i, c in enumerate(contexts)
    )
    return (
        f"Context excerpts:\n{context_block}\n\n"
        f"Question: {question}\n\n"
        f"Answer using only the context above:"
    )
