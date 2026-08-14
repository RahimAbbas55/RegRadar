# Generates citated answers to user queries based on retrieved chunks from the FCA Handbook.
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from openai import OpenAI
from config import settings
from generation.prompts import SYSTEM_PROMPT, build_user_prompt
from retrieval.pipeline import retrieve
client = OpenAI(api_key=settings.openai_api_key)
GENERATION_MODEL = "gpt-4o"

def generate_answer(query: str, top_k: int = 5, **retrieve_kwargs) -> dict:
    """Runs full retrieval, then generates a cited answer grounded in the retrieved chunks."""
    retrieval_result = retrieve(query, top_k=top_k, **retrieve_kwargs)
    chunks = retrieval_result["results"]
    timings = retrieval_result["timings"]

    if not chunks:
        return {
            "query": query,
            "answer": "No relevant provisions were found in the FCA Handbook for this question.",
            "sources": [],
            "timings": timings,
        }

    user_prompt = build_user_prompt(retrieval_result["search_query"], chunks)

    generation_start = time.perf_counter()
    response = client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    timings["generation_ms"] = round((time.perf_counter() - generation_start) * 1000, 1)
    timings["total_ms"] = sum(v for k, v in timings.items() if k != "total_ms")

    answer = response.choices[0].message.content

    return {
        "query": query,
        "search_query": retrieval_result["search_query"],
        "answer": answer,
        "sources": [{"provision_id": c["provision_id"], "tag": c.get("tag"), "text": c["text"]} for c in chunks],
        "timings": timings,
    }