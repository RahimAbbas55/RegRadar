# Smoke test for the retrieval pipeline, demonstrating query rewriting, hybrid search, and reranking.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from retrieval.pipeline import retrieve

def print_result(response: dict):
    print(f"\nOriginal query: {response['original_query']!r}")
    print(f"Rewritten query: {response['search_query']!r}")
    print("-" * 60)
    for i, chunk in enumerate(response["results"], 1):
        print(f"[{i}] {chunk['provision_id']} ({chunk.get('tag', '?')})  score={chunk.get('rerank_score', 0):.4f}")
        print(f"    {chunk['text'][:150]}...")

if __name__ == "__main__":
    casual_queries = [
        "do i need to train my staff on money laundering stuff?",
        "who's in charge of making sure we follow the rules?",
        "what happens if my company outsources some work to another firm?",
    ]
    for query in casual_queries:
        response = retrieve(query)
        print_result(response)