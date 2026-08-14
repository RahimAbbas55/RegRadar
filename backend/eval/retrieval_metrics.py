# Computes the precision and recall of retrieval results
import json
from pathlib import Path
RESULTS_PATH = Path(__file__).parent.parent.parent / "data" / "processed" / "eval_results.json"
REFUSAL_PHRASES = ["does not contain", "cannot answer", "no relevant provisions", "does not cover"]

def compute_precision_recall(expected: list[str], retrieved: list[str]) -> dict:
    if not expected:
        return None  # handled separately for out-of-scope questions

    expected_set = set(expected)
    retrieved_set = set(retrieved)

    true_positives = len(expected_set & retrieved_set)
    recall = true_positives / len(expected_set) if expected_set else 0.0
    precision = true_positives / len(retrieved_set) if retrieved_set else 0.0

    return {"precision": round(precision, 3), "recall": round(recall, 3)}

def check_out_of_scope_refusal(answer: str) -> bool:
    answer_lower = answer.lower()
    return any(phrase in answer_lower for phrase in REFUSAL_PHRASES)

def score_all() -> list[dict]:
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    scored = []

    for r in results:
        if not r["expected_provision_ids"]:
            scored.append({
                "id": r["id"],
                "type": "out_of_scope",
                "correctly_refused": check_out_of_scope_refusal(r["answer"]),
            })
        else:
            metrics = compute_precision_recall(r["expected_provision_ids"], r["retrieved_provision_ids"])
            scored.append({"id": r["id"], "type": "retrieval", **metrics})
    return scored

if __name__ == "__main__":
    scored = score_all()
    for s in scored:
        print(s)