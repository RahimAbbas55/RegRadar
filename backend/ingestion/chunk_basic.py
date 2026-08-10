#Basic fixed-size chunking with overlap, as a baseline to compare smarter chunking against later.
import json
from pathlib import Path
PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
CHUNKS_DIR = PROCESSED_DIR / "chunks_basic"
CHUNK_SIZE = 500      # target characters per chunk
CHUNK_OVERLAP = 75    # characters shared between consecutive chunks from the same provision

def fixed_size_split(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if len(text) <= size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap  # step back by the overlap amount so context isn't lost at the boundary
    return chunks

def chunk_document(doc: dict) -> list[dict]:
    chunks = []
    for provision in doc["provisions"]:
        pieces = fixed_size_split(provision["text"])
        for i, piece in enumerate(pieces):
            chunks.append({
                "chunk_id": f"{provision['provision_id']}_{i}",
                "provision_id": provision["provision_id"],
                "heading": provision["heading"],
                "date": provision["date"],
                "tag": provision["tag"],
                "text": piece,
                "source_file": doc["source_file"],
            })
    return chunks

if __name__ == "__main__":
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    processed_files = list(PROCESSED_DIR.glob("*.json"))

    total_chunks = 0
    for path in processed_files:
        doc = json.loads(path.read_text(encoding="utf-8"))
        chunks = chunk_document(doc)
        output_path = CHUNKS_DIR / path.name
        output_path.write_text(json.dumps(chunks, indent=2), encoding="utf-8")
        print(f"✅ {path.name} → {len(chunks)} chunks")
        total_chunks += len(chunks)

    print(f"\nTotal: {total_chunks} chunks across {len(processed_files)} documents.")