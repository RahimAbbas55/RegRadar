# Builds a BM25 index over all chunks in the processed data directory, saving it to a pickle file for later retrieval.
import sys
import pickle
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from rank_bm25 import BM25Okapi
from ingestion.chunk_utils import load_all_chunks
INDEX_OUTPUT = Path(__file__).parent.parent.parent / "data" / "processed" / "bm25_index.pkl"
# Simple whitespace + lowercase tokenizer — BM25 doesn't need anything fancier than this to work well
TOKEN_PATTERN = re.compile(r"\w+")

def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())

def build_index():
    chunks = load_all_chunks()
    if not chunks:
        print("No chunks found — run chunk_semantic.py first.")
        return

    tokenized_corpus = [tokenize(c["text"]) for c in chunks]
    bm25 = BM25Okapi(tokenized_corpus)

    # Save both the index and the chunks list (in matching order) — BM25 returns scores by position,
    # so we need the original chunks alongside it to map scores back to actual content
    with open(INDEX_OUTPUT, "wb") as f:
        pickle.dump({"bm25": bm25, "chunks": chunks}, f)

    print(f"✅ Built BM25 index over {len(chunks)} chunks, saved to {INDEX_OUTPUT}")

if __name__ == "__main__":
    build_index()