"""Generates embeddings for all chunks and saves them locally, before any Qdrant interaction."""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from openai import OpenAI
from config import settings

CHUNKS_DIR = Path(__file__).parent.parent.parent / "data" / "processed" / "chunks_semantic"
EMBEDDINGS_OUTPUT = Path(__file__).parent.parent.parent / "data" / "processed" / "embeddings.json"
EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 50
client = OpenAI(api_key=settings.openai_api_key)

def load_all_chunks() -> list[dict]:
    all_chunks = []
    for path in sorted(CHUNKS_DIR.glob("*.json")):
        chunks = json.loads(path.read_text(encoding="utf-8"))
        all_chunks.extend(chunks)
    return all_chunks

def embed_batch(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return [item.embedding for item in response.data]

def generate_all_embeddings(chunks: list[dict]) -> list[dict]:
    embedded_chunks = []
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        texts = [c["text"] for c in batch]
        vectors = embed_batch(texts)

        for chunk, vector in zip(batch, vectors):
            embedded_chunks.append({**chunk, "embedding": vector})

        print(f"✅ Embedded {min(i + BATCH_SIZE, len(chunks))}/{len(chunks)} chunks")

    return embedded_chunks

if __name__ == "__main__":
    chunks = load_all_chunks()
    if not chunks:
        print("No chunks found — run chunk_semantic.py first.")
        exit(1)

    print(f"Embedding {len(chunks)} chunks using {EMBEDDING_MODEL}...")
    embedded_chunks = generate_all_embeddings(chunks)

    EMBEDDINGS_OUTPUT.write_text(json.dumps(embedded_chunks), encoding="utf-8")
    print(f"\nSaved {len(embedded_chunks)} embedded chunks to {EMBEDDINGS_OUTPUT}")
    print(f"Embedding dimension: {len(embedded_chunks[0]['embedding'])}")