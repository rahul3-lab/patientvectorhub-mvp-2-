"""
Embedding backends.

- huggingface (default): runs emilyalsentzer/Bio_ClinicalBERT locally via
  sentence-transformers. Zero API cost, first run downloads the model
  (~400MB) from Hugging Face Hub, then it's cached.
- openai: hosted, costs money, used if EMBEDDING_PROVIDER=openai and
  OPENAI_API_KEY is set. Kept as an interchangeable option per the spec's
  "OpenAI or Hugging Face-hosted clinical-bert" requirement.
"""
from functools import lru_cache

from app.config import settings


@lru_cache(maxsize=1)
def _local_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    if settings.embedding_provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        resp = client.embeddings.create(model=settings.openai_embedding_model, input=texts)
        return [d.embedding for d in resp.data]

    model = _local_model()
    vectors = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return vectors.tolist()


def embedding_dim() -> int:
    if settings.embedding_provider == "openai":
        # text-embedding-3-small = 1536 dims
        return 1536
    return _local_model().get_sentence_embedding_dimension()
