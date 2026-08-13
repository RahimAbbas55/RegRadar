# Compares the order of results returned by hybrid search with and without reranking for a few test queries.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from retrieval.hybrid_search import hybrid_search

def print_comparison(query: str, top_k: int = 5):
    print(f"\nQuery: {query!r}")
    print("=" * 70)
    fused_only = hybrid_search(query, top_k=top_k, use_reranker=False)
    reranked = hybrid_search(query, top_k=top_k, use_reranker=True)
    fused_order = [c["provision_id"] for c in fused_only]
    reranked_order = [c["provision_id"] for c in reranked]
    print(f"RRF-only order:   {fused_order}")
    print(f"Reranked order:   {reranked_order}")
    print(f"Order changed:    {fused_order != reranked_order}")

if __name__ == "__main__":
    test_queries = [
        "What are a firm's obligations around financial crime systems and controls?",
        "Which chapters of SYSC apply to insurers?",
        "What is a firm's compliance function responsible for?",
    ]
    for query in test_queries:
        print_comparison(query)