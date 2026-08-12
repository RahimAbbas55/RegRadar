# Create a Qdrant collection and upsert all of the chunks in it``
import sys
import json
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from config import settings
EMBEDDINGS_PATH = Path(__file__).parent.parent.parent / "data" / "processed" / "embeddings.json"
VECTOR_SIZE = 1536  # must match text-embedding-3-small's output dimension
client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

def ensure_collection_exists():
    existing = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection_name in existing:
        print(f"Collection '{settings.qdrant_collection_name}' already exists — will upsert into it.")
        return

    client.create_collection(
        collection_name=settings.qdrant_collection_name,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    print(f"✅ Created collection '{settings.qdrant_collection_name}'")


def chunk_id_to_point_id(chunk_id: str) -> str:
    """Deterministic UUID from our readable chunk_id, so re-running ingestion overwrites rather than duplicates."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))

def build_points(embedded_chunks: list[dict]) -> list[PointStruct]:
    points = []
    for chunk in embedded_chunks:
        point_id = chunk_id_to_point_id(chunk["chunk_id"])
        payload = {k: v for k, v in chunk.items() if k != "embedding"}  # everything except the vector itself
        points.append(PointStruct(id=point_id, vector=chunk["embedding"], payload=payload))
    return points

if __name__ == "__main__":
    if not EMBEDDINGS_PATH.exists():
        print("No embeddings.json found — run generate_embeddings.py first.")
        exit(1)

    embedded_chunks = json.loads(EMBEDDINGS_PATH.read_text(encoding="utf-8"))
    print(f"Loaded {len(embedded_chunks)} embedded chunks.")

    ensure_collection_exists()

    points = build_points(embedded_chunks)
    client.upsert(collection_name=settings.qdrant_collection_name, points=points)
    print(f"✅ Upserted {len(points)} points into '{settings.qdrant_collection_name}'")

    count = client.count(collection_name=settings.qdrant_collection_name).count
    print(f"Collection now contains {count} points total.")