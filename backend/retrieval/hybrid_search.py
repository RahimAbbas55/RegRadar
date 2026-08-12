#Combines dense (Qdrant) and sparse (BM25) retrieval using Reciprocal Rank Fusion.
import sys
import pickle
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).parent.parent))
from openai import OpenAI
from qdrant_client import QdrantClient
from config import settings
from retrieval.bm25_index import tokenize
from qdrant_client.models import Filter, FieldCondition, MatchValue
EMBEDDING_MODEL = "text-embedding-3-small"
BM25_INDEX_PATH = Path(__file__).parent.parent.parent / "data" / "processed" / "bm25_index.pkl"
RRF_K = 60  # standard damping constant for reciprocal rank fusion
openai_client = OpenAI(api_key=settings.openai_api_key)
qdrant_client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

with open(BM25_INDEX_PATH, "rb") as f:
    _bm25_data = pickle.load(f)
    bm25_index = _bm25_data["bm25"]
    bm25_chunks = _bm25_data["chunks"]  # same order the index was built with

def embed_query(query: str) -> list[float]:
    response = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
    return response.data[0].embedding

def build_qdrant_filter(tag: str | None, source_file: str | None) -> Filter | None:
    conditions = []
    if tag:
        conditions.append(FieldCondition(key="tag", match=MatchValue(value=tag)))
    if source_file:
        conditions.append(FieldCondition(key="source_file", match=MatchValue(value=source_file)))
    return Filter(must=conditions) if conditions else None

def dense_search(query: str, top_k: int = 20, tag: str | None = None, source_file: str | None = None) -> list[dict]:
    query_vector = embed_query(query)
    qdrant_filter = build_qdrant_filter(tag, source_file)
    results = qdrant_client.search(
        collection_name=settings.qdrant_collection_name,
        query_vector=query_vector,
        query_filter=qdrant_filter,
        limit=top_k,
    )
    return [hit.payload for hit in results]

def sparse_search(query: str, top_k: int = 20, tag: str | None = None, source_file: str | None = None) -> list[dict]:
    tokenized_query = tokenize(query)
    scores = bm25_index.get_scores(tokenized_query)
    # Filter candidate indices by metadata before ranking, since BM25 itself has no filtering concept
    eligible_indices = [
        i for i, chunk in enumerate(bm25_chunks)
        if (tag is None or chunk.get("tag") == tag)
        and (source_file is None or chunk.get("source_file") == source_file)
    ]
    ranked_indices = sorted(eligible_indices, key=lambda i: scores[i], reverse=True)[:top_k]
    return [bm25_chunks[i] for i in ranked_indices]

def reciprocal_rank_fusion(result_lists: list[list[dict]], k: int = RRF_K) -> list[dict]:
    """Merges multiple ranked lists into one, scoring by rank position rather than raw scores."""
    rrf_scores = defaultdict(float)
    chunk_lookup = {}

    for result_list in result_lists:
        for rank, chunk in enumerate(result_list):
            key = chunk["chunk_id"]
            rrf_scores[key] += 1 / (k + rank + 1)  # +1 since rank starts at 0
            chunk_lookup[key] = chunk

    ranked_ids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)
    return [{**chunk_lookup[cid], "rrf_score": rrf_scores[cid]} for cid in ranked_ids]

def hybrid_search(
        query: str,
        top_k: int = 5,
        candidate_pool: int = 20,
        tag: str | None = None,
        source_file: str | None = None,
    ) -> list[dict]:
    dense_results = dense_search(query, top_k=candidate_pool, tag=tag, source_file=source_file)
    sparse_results = sparse_search(query, top_k=candidate_pool, tag=tag, source_file=source_file)
    fused = reciprocal_rank_fusion([dense_results, sparse_results])
    return fused[:top_k]