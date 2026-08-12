# Shared chunk loading utility for ingestion and retrieval pipelines.
import json
from pathlib import Path
CHUNKS_DIR = Path(__file__).parent.parent.parent / "data" / "processed" / "chunks_semantic"

def load_all_chunks(dedupe: bool = True) -> list[dict]:
    all_chunks = []
    seen_keys = set()
    duplicate_count = 0

    for path in sorted(CHUNKS_DIR.glob("*.json")):
        chunks = json.loads(path.read_text(encoding="utf-8"))
        for chunk in chunks:
            key = (chunk["provision_id"], chunk["text"])
            if dedupe and key in seen_keys:
                duplicate_count += 1
                continue
            seen_keys.add(key)
            all_chunks.append(chunk)

    if dedupe and duplicate_count:
        print(f"Deduplicated {duplicate_count} chunk(s) with identical provision_id + text across source files.")

    return all_chunks