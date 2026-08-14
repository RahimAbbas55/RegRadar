# Runs the complete eval suite and produces a single summary report.
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).parent.parent))
from eval.retrieval_metrics import score_all as score_retrieval
from eval.ragas_faithfulness import load_ragas_dataset as load_faithfulness_dataset
from eval.ragas_relevancy import load_ragas_dataset as load_relevancy_dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
REPORT_OUTPUT = Path(__file__).parent.parent.parent / "docs" / "eval_report.md"

def generate_report() -> str:
    retrieval_scores = score_retrieval()
    retrieval_only = [s for s in retrieval_scores if s["type"] == "retrieval"]
    out_of_scope = [s for s in retrieval_scores if s["type"] == "out_of_scope"]

    avg_precision = sum(s["precision"] for s in retrieval_only) / len(retrieval_only)
    avg_recall = sum(s["recall"] for s in retrieval_only) / len(retrieval_only)
    refusal_rate = sum(1 for s in out_of_scope if s["correctly_refused"]) / len(out_of_scope) if out_of_scope else None

    faith_dataset, _ = load_faithfulness_dataset()
    faith_result = evaluate(faith_dataset, metrics=[faithfulness]).to_pandas()
    avg_faithfulness = faith_result["faithfulness"].mean()

    rel_dataset, _ = load_relevancy_dataset()
    rel_result = evaluate(rel_dataset, metrics=[answer_relevancy]).to_pandas()
    avg_relevancy = rel_result["answer_relevancy"].mean()

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    report = f"""# RegRadar Evaluation Report

Generated: {timestamp}
Dataset: {len(retrieval_only)} in-scope questions, {len(out_of_scope)} out-of-scope questions

## Retrieval Quality
- Average precision: {avg_precision:.3f}
- Average recall: {avg_recall:.3f}

## Generation Quality (RAGAS)
- Average faithfulness: {avg_faithfulness:.3f}
- Average answer relevancy: {avg_relevancy:.3f}

## Refusal Behavior
- Correctly refused out-of-scope questions: {f"{refusal_rate:.0%}" if refusal_rate is not None else "N/A"}

## Known Limitations
- Query rewriting introduces run-to-run non-determinism, which can shift retrieval results between eval runs
  (see: gd_002, gd_005, gd_008 scored 0.0 precision/recall in an earlier run, then correctly matched on re-run
  with the same code, purely due to rewriter phrasing variance)
- RAGAS answer_relevancy forces a score of exactly 0.0 for any answer its internal classifier judges as
  "noncommittal" — this penalizes appropriately hedged compliance language (e.g. correctly distinguishing
  Guidance from binding Rules), not just genuinely evasive answers
- RAGAS faithfulness may score lower on structured/tabular answers (e.g. long chapter-number lists), possibly
  due to how atomic claims are extracted from list-like content
- Golden dataset currently covers 8 questions across 7 scraped SYSC sections — a starting point, not
  comprehensive coverage of the full FCA Handbook
"""
    return report

if __name__ == "__main__":
    report = generate_report()
    REPORT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUTPUT.write_text(report, encoding="utf-8")
    print(report)
    print(f"\n✅ Report saved to {REPORT_OUTPUT}")