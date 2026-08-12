# Runs test for the hybrid search function, printing the results for a few sample queries.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from retrieval.hybrid_search import hybrid_search

def print_results(query: str, results: list[dict]):
    print(f"\nQuery: {query!r}")
    print("=" * 60)
    for i, chunk in enumerate(results, 1):
        print(f"\n[{i}] rrf_score={chunk['rrf_score']:.4f}  {chunk['provision_id']}  ({chunk.get('tag', '?')})")
        print(f"    heading: {chunk.get('heading')}")
        text = chunk["text"]
        print(f"    text: {text[:200]}{'...' if len(text) > 200 else ''}")

if __name__ == "__main__":
    test_queries = [
        "What are a firm's obligations around financial crime systems and controls?",
        "Which chapters of SYSC apply to insurers?",
        "What is a firm's compliance function responsible for?",
    ]

    for query in test_queries:
        results = hybrid_search(query)
        print_results(query, results)