# Chunking provisions into semantically meaningful chunks based on sentence boundaries and target chunk sizes.
import json
import re
from pathlib import Path
PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
CHUNKS_DIR = PROCESSED_DIR / "chunks_semantic"
TARGET_CHUNK_SIZE = 500   
MIN_CHUNK_SIZE = 100      
SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+(?=[A-Z(])")

def split_into_sentences(text: str) -> list[str]:
    sentences = SENTENCE_SPLIT_PATTERN.split(text)
    return [s.strip() for s in sentences if s.strip()]

def group_sentences(sentences: list[str], target_size: int = TARGET_CHUNK_SIZE) -> list[str]:
    chunks = []
    current = ""

    for sentence in sentences:
        if current and len(current) + len(sentence) + 1 > target_size:
            chunks.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()

    if current:
        if chunks and len(current) < MIN_CHUNK_SIZE:
            chunks[-1] = f"{chunks[-1]} {current}"
        else:
            chunks.append(current)

    return chunks

def chunk_document(doc: dict) -> list[dict]:
    chunks = []
    for provision in doc["provisions"]:
        base_meta = {
            "provision_id": provision["provision_id"],
            "heading": provision["heading"],
            "date": provision["date"],
            "tag": provision["tag"],
            "source_file": doc["source_file"],
        }

        # Prose text gets sentence-grouped as before
        sentences = split_into_sentences(provision["text"])
        pieces = group_sentences(sentences) if sentences else ([provision["text"]] if provision["text"] else [])

        for i, piece in enumerate(pieces):
            source_stem = doc["source_file"].replace(".html", "").replace(".json", "")
            chunks.append({**base_meta, "chunk_id": f"{source_stem}::{provision['provision_id']}_{i}",
                            "text": piece, "contains_table": False})

        # Each table becomes its own atomic chunk — never split, never merged with prose
        for t_idx, table_md in enumerate(provision.get("tables", [])):
            source_stem = doc["source_file"].replace(".html", "").replace(".json", "")
            chunks.append({**base_meta, "chunk_id": f"{source_stem}::{provision['provision_id']}_table_{t_idx}",
                            "text": table_md, "contains_table": True})
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