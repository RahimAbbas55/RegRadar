# RegRadar Evaluation Report

Generated: 2026-08-14 11:24 UTC
Dataset: 7 in-scope questions, 1 out-of-scope questions

## Retrieval Quality
- Average precision: 0.286
- Average recall: 1.000

## Generation Quality (RAGAS)
- Average faithfulness: 0.821
- Average answer relevancy: 0.812

## Refusal Behavior
- Correctly refused out-of-scope questions: 100%

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
