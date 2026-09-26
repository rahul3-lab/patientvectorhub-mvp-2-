"""
Manually (re)create the Qdrant collection. Usually not needed - the
ingestion service calls ensure_collection() on first upload - but useful
for resetting during development:

    python infra/scripts/init_qdrant.py --dim 768 --reset
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "vector-store"))
from app.qdrant_client import QdrantStore  # noqa: E402

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.environ.get("QDRANT_COLLECTION", "patient_documents")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dim", type=int, default=768, help="Embedding dimension (Bio_ClinicalBERT=768, OpenAI small=1536)")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate the collection")
    args = parser.parse_args()

    store = QdrantStore(url=QDRANT_URL, collection=COLLECTION)
    if args.reset:
        try:
            store.client.delete_collection(COLLECTION)
            print(f"dropped collection {COLLECTION}")
        except Exception as e:
            print(f"(nothing to drop, or error: {e})")

    store.ensure_collection(dim=args.dim)
    print(f"collection {COLLECTION} ready with dim={args.dim}")


if __name__ == "__main__":
    main()
