# Runs a series of checks on the semantic chunks produced by chunk_semantic.py to identify potential issues.
import json
from pathlib import Path
from collections import Counter
from collections import Counter
from chunk_utils import load_all_chunks
MIN_REASONABLE_CHUNK_LEN = 20    # chunks shorter than this are likely extraction failures
MAX_REASONABLE_CHUNK_LEN = 2500   # chunks longer than this likely failed to split properly

chunks = load_all_chunks()

def check_empty_or_tiny(chunks: list[dict]) -> list[dict]:
    return [c for c in chunks if len(c["text"].strip()) < MIN_REASONABLE_CHUNK_LEN]

def check_oversized(chunks: list[dict]) -> list[dict]:
    return [c for c in chunks if len(c["text"]) > MAX_REASONABLE_CHUNK_LEN]

def check_malformed_tables(chunks: list[dict]) -> list[dict]:
    return [c for c in chunks if c.get("contains_table") and "|" not in c["text"]]

def check_duplicate_ids(chunks: list[dict]) -> list[str]:
    id_counts = Counter(c["chunk_id"] for c in chunks)
    return [chunk_id for chunk_id, count in id_counts.items() if count > 1]

def print_summary(chunks: list[dict]) -> None:
    by_source = Counter(c["source_file"] for c in chunks)
    table_count = sum(1 for c in chunks if c.get("contains_table"))
    sizes = [len(c["text"]) for c in chunks]

    print("=== Chunk Summary ===")
    for source, count in sorted(by_source.items()):
        print(f"  {source}: {count} chunks")
    print(f"\nTotal chunks: {len(chunks)}")
    print(f"Table chunks: {table_count}")
    print(f"Avg chunk length: {sum(sizes) / len(sizes):.0f} chars")
    print(f"Min / Max chunk length: {min(sizes)} / {max(sizes)} chars")

if __name__ == "__main__":
    chunks = load_all_chunks()

    if not chunks:
        print("No chunks found — run chunk_semantic.py first.")
        exit(1)

    print_summary(chunks)

    print("\n=== Issue Checks ===")
    tiny = check_empty_or_tiny(chunks)
    oversized = check_oversized(chunks)
    malformed_tables = check_malformed_tables(chunks)
    dupes = check_duplicate_ids(chunks)

    print(f"Tiny/empty chunks (<{MIN_REASONABLE_CHUNK_LEN} chars): {len(tiny)}")
    for c in tiny[:5]:
        print(f"  - {c['chunk_id']}: {c['text']!r}")

    print(f"Oversized chunks (>{MAX_REASONABLE_CHUNK_LEN} chars): {len(oversized)}")
    for c in oversized[:5]:
        print(f"  - {c['chunk_id']}: {len(c['text'])} chars")

    print(f"Malformed table chunks: {len(malformed_tables)}")
    for c in malformed_tables[:5]:
        print(f"  - {c['chunk_id']}")

    print(f"Duplicate chunk_ids: {len(dupes)}")
    for chunk_id in dupes[:5]:
        print(f"  - {chunk_id}")

    total_issues = len(tiny) + len(oversized) + len(malformed_tables) + len(dupes)
    if total_issues == 0:
        print("\n✅ All checks passed. Chunks are ready for embedding (Stage 3).")
    else:
        print(f"\n⚠️  {total_issues} issue(s) found — review before proceeding to Stage 3.")