# Runs full retrieval pipeline: query rewriting, hybrid search, and optional reranking.
import sys
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
    search_query = rewrite_query(query) if use_query_rewriting else query
    results = hybrid_search(
        search_query,
        top_k=top_k,
        tag=tag,
        source_file=source_file,
        use_reranker=use_reranker,
    )
    return {
        "original_query": query,
        "search_query": search_query,
        "results": results,
    }