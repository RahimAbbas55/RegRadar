# Sends a batch of varied queries to the live API and verifies logging, timing, cost, and fallback tracking all work together.
import httpx
from fallback_tracker import compute_fallback_rate, load_logged_queries
BASE_URL = "http://localhost:8000"
TEST_QUERIES = [
    "do i need to train my staff on money laundering stuff?",
    "who is responsible for outsourcing decisions?",
    "what is the maximum penalty for insider trading?", 
]

def check(description: str, condition: bool):
    status = "✅" if condition else "❌"
    print(f"{status} {description}")
    return condition

if __name__ == "__main__":
    print("Sending test queries to live API...\n")
    before_count = len(load_logged_queries())
    for q in TEST_QUERIES:
        response = httpx.post(f"{BASE_URL}/query", json={"query": q}, timeout=30.0)
        print(f"  {response.status_code} - {q!r}")
    after_entries = load_logged_queries()
    after_count = len(after_entries)
    print("\n=== Observability Checks ===")
    check("Log count increased by exactly 3", after_count - before_count == 3)
    recent_entries = after_entries[-3:]
    check("All recent entries have timings", all("timings" in e for e in recent_entries))
    check("All recent entries have cost_usd", all("cost_usd" in e for e in recent_entries))
    check("All recent entries have full answer text logged", all(len(e.get("answer", "")) > 0 for e in recent_entries))
    fallback_stats = compute_fallback_rate()
    print(f"\nCurrent fallback stats: {fallback_stats}")
    check("At least one refusal detected across all logs", fallback_stats["refusals"] >= 1)