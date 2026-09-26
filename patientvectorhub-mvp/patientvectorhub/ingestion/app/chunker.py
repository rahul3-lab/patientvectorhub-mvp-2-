"""
Simple fixed-size word-count chunker with overlap. Not token-exact (a real
tokenizer would be more precise) but avoids pulling in a heavyweight
tokenizer dependency just for chunk boundaries - fine for MVP quality bar.
"""
from app.config import settings


def chunk_text(text: str) -> list[str]:
    words = text.split()
    if not words:
        return []

    size = settings.chunk_size_tokens
    overlap = settings.chunk_overlap_tokens
    step = max(size - overlap, 1)

    chunks = []
    for start in range(0, len(words), step):
        piece = words[start:start + size]
        if not piece:
            break
        chunks.append(" ".join(piece))
        if start + size >= len(words):
            break
    return chunks
