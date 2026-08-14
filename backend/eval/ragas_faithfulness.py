# Scores answer faithfulness using RAGAS 
import sys
import os
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings
os.environ["OPENAI_API_KEY"] = settings.openai_api_key  
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness
RESULTS_PATH = Path(__file__).parent.parent.parent / "data" / "processed" / "eval_results.json"

def load_ragas_dataset() -> Dataset:
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    in_scope = [r for r in results if r["expected_provision_ids"]]
    return Dataset.from_dict({
        "question": [r["question"] for r in in_scope],
        "answer": [r["answer"] for r in in_scope],
        "contexts": [r["retrieved_texts"] for r in in_scope],
    }), [r["id"] for r in in_scope]

if __name__ == "__main__":
    dataset, ids = load_ragas_dataset()
    print(f"Scoring faithfulness for {len(dataset)} in-scope questions...")

    result = evaluate(dataset, metrics=[faithfulness])
    scores_df = result.to_pandas()

    for id_, score in zip(ids, scores_df["faithfulness"]):
        print(f"{id_}: {score:.3f}")

    print(f"\nAverage faithfulness: {scores_df['faithfulness'].mean():.3f}")