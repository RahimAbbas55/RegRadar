# Run the golden dataset evaluation pipeline and save results to a JSON file.
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from eval.golden_dataset import GOLDEN_DATASET
from generation.generate import generate_answer
RESULTS_OUTPUT = Path(__file__).parent.parent.parent / "data" / "processed" / "eval_results.json"

def run_all() -> list[dict]:
    results = []
    for item in GOLDEN_DATASET:
        print(f"Running {item['id']}: {item['question']!r}")
        pipeline_result = generate_answer(item["question"])

        retrieved_provision_ids = [s["provision_id"] for s in pipeline_result["sources"]]

        results.append({
            "id": item["id"],
            "question": item["question"],
            "expected_provision_ids": item["expected_provision_ids"],
            "retrieved_provision_ids": retrieved_provision_ids,
            "answer": pipeline_result["answer"],
            "difficulty": item["difficulty"],
        })
    return results

if __name__ == "__main__":
    results = run_all()
    RESULTS_OUTPUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n✅ Saved {len(results)} eval results to {RESULTS_OUTPUT}")