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

# Approximate OpenAI pricing per 1M tokens
PRICING = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
}

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

    generation_usage = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
    }
    rewrite_usage = retrieval_result["token_usage"]["rewrite"]

    total_cost = (
        calculate_cost("gpt-4o-mini", rewrite_usage["prompt_tokens"], rewrite_usage["completion_tokens"])
        + calculate_cost(GENERATION_MODEL, generation_usage["prompt_tokens"], generation_usage["completion_tokens"])
    )

    answer = response.choices[0].message.content

    return {
        "query": query,
        "search_query": retrieval_result["search_query"],
        "answer": answer,
        "sources": [{"provision_id": c["provision_id"], "tag": c.get("tag"), "text": c["text"]} for c in chunks],
        "timings": timings,
        "cost_usd": round(total_cost, 6),
    }

def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    rates = PRICING.get(model, {"input": 0, "output": 0})
    return (prompt_tokens / 1_000_000 * rates["input"]) + (completion_tokens / 1_000_000 * rates["output"])