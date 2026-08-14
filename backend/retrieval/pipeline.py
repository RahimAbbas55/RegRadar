# Runs full retrieval pipeline: query rewriting, hybrid search, and optional reranking.
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from retrieval.query_rewriter import rewrite_query
from retrieval.hybrid_search import hybrid_search

def retrieve(
    query: str,
    top_k: int = 5,
    tag: str | None = None,
    source_file: str | None = None,
    use_query_rewriting: bool = True,
    use_reranker: bool = True,
) -> dict:
    timings = {}
    rewrite_start = time.perf_counter()
    if use_query_rewriting:
        search_query, rewrite_usage = rewrite_query(query)
    else:
        search_query, rewrite_usage = query, {"prompt_tokens": 0, "completion_tokens": 0}
    timings["rewrite_ms"] = round((time.perf_counter() - rewrite_start) * 1000, 1)
    search_start = time.perf_counter()
    results = hybrid_search(
        search_query,
        top_k=top_k,
        tag=tag,
        source_file=source_file,
        use_reranker=use_reranker,
    )
    timings["search_and_rerank_ms"] = round((time.perf_counter() - search_start) * 1000, 1)
    return {
        "original_query": query,
        "search_query": search_query,
        "results": results,
        "timings": timings,
        "token_usage": {"rewrite": rewrite_usage},
    }