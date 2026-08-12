# Embedding a real query to test the retrieval pipeline.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from openai import OpenAI
from qdrant_client import QdrantClient
from config import settings
EMBEDDING_MODEL = "text-embedding-3-small"
TOP_K = 5
openai_client = OpenAI(api_key=settings.openai_api_key)
qdrant_client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

def embed_query(query: str) -> list[float]:
    response = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
    return response.data[0].embedding

def search(query: str, top_k: int = TOP_K):
    query_vector = embed_query(query)
    results = qdrant_client.search(
        collection_name=settings.qdrant_collection_name,
        query_vector=query_vector,
        limit=top_k,
    )
    return results

def print_results(query: str, results):
    print(f"\nQuery: {query!r}")
    print("=" * 60)
    for i, hit in enumerate(results, 1):
        payload = hit.payload
        print(f"\n[{i}] score={hit.score:.4f}  {payload['provision_id']}  ({payload.get('tag', '?')})")
        print(f"    heading: {payload.get('heading')}")
        print(f"    text: {payload['text'][:200]}{'...' if len(payload['text']) > 200 else ''}")

if __name__ == "__main__":
    test_queries = [
        "What are a firm's obligations around financial crime systems and controls?",
        "Which chapters of SYSC apply to insurers?",
        "What is a firm's compliance function responsible for?",
    ]

    for query in test_queries:
        results = search(query)
        print_results(query, results)