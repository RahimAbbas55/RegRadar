# End-to-end smoke test: real questions through the full pipeline, including a deliberate out-of-scope question.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from generation.generate import generate_answer

def print_result(query: str):
    result = generate_answer(query)
    print(f"\nQuery: {query!r}")
    print("=" * 70)
    print(f"Answer:\n{result['answer']}")
    print(f"\nSources: {[s['provision_id'] for s in result['sources']]}")

if __name__ == "__main__":
    test_queries = [
        "do i need to train my staff on money laundering stuff?",
        "who is responsible for outsourcing decisions at a firm?",
        # Deliberately out-of-scope: not covered by our scraped SYSC sections at all
        "what is the maximum penalty for insider trading under UK law?",
    ]
    for query in test_queries:
        print_result(query)