# Analyzes logged queries to compute the rate at which the system declines to answer (fallback/refusal rate).
import json
from pathlib import Path
LOG_FILE = Path(__file__).parent.parent.parent / "data" / "logs" / "queries.jsonl"
REFUSAL_PHRASES = ["does not contain", "cannot answer", "no relevant provisions", "does not cover", "does not explicitly state"]

def load_logged_queries() -> list[dict]:
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def is_refusal(log_entry: dict) -> bool:
    answer = log_entry.get("answer", "").lower()
    return any(phrase in answer for phrase in REFUSAL_PHRASES)

def compute_fallback_rate() -> dict:
    entries = [e for e in load_logged_queries() if e.get("event") == "query_processed"]
    if not entries:
        return {"total_queries": 0, "fallback_rate": None}
    refusals = sum(1 for e in entries if is_refusal(e))
    return {
        "total_queries": len(entries),
        "refusals": refusals,
        "fallback_rate": round(refusals / len(entries), 3),
    }

if __name__ == "__main__":
    stats = compute_fallback_rate()
    print(stats)