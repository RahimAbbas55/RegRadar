# Re-writes user queries into a more precise and formal search query.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from openai import OpenAI
from config import settings
client = OpenAI(api_key=settings.openai_api_key)

REWRITE_PROMPT = """You are a query rewriting assistant for a UK financial regulation search system (FCA Handbook).
Rewrite the user's question into a clear, precise search query using formal regulatory terminology where appropriate.
Keep the rewritten query concise — one sentence. Do not answer the question, only rewrite it.
Return ONLY the rewritten query, nothing else — no preamble, no explanation.
User question: {query}
Rewritten query:"""

def rewrite_query(query: str) -> tuple[str, dict]:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=100,
        messages=[{"role": "user", "content": REWRITE_PROMPT.format(query=query)}],
    )
    rewritten = response.choices[0].message.content.strip()
    usage = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
    }
    return (rewritten if rewritten else query), usage# fallback to original if the model returns empty