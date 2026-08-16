# RegRadar Architecture

## Overview

RegRadar is a retrieval-augmented generation (RAG) system that answers compliance questions
against the UK FCA Handbook, with every claim traceable to a specific, citable provision.
The system is split into two pipelines — ingestion (run once, offline) and query (run per
request) — plus a frontend that consumes the query pipeline over HTTP.

## Ingestion pipeline

Run manually via the scripts in `backend/ingestion/`, in this order:

1. **Scrape** (`scrape_fca.py`) — fetches raw HTML for a curated list of FCA Handbook SYSC
   sections. Targets individual section pages (e.g. `/handbook/sysc3/sysc3s2`), not chapter
   overview pages, since overview pages require JavaScript rendering that a plain HTTP
   request can't execute.

2. **Clean** (`clean_documents.py`) — parses the real DOM structure (Angular-rendered but
   server-side-rendered into static HTML) to extract individual provisions. Each provision
   captures: provision ID (e.g. `SYSC 3.2.6A`), effective date, Rule/Guidance tag, section
   heading, body text, and any embedded tables (converted to markdown, kept separate from
   prose text so they aren't flattened and destroyed).

3. **Chunk** (`chunk_semantic.py`) — splits provision text into embedding-ready chunks using
   sentence-boundary-aware grouping (never cuts mid-sentence), targeting ~500 characters per
   chunk. Tables are kept as single atomic chunks, never split — a table row without its
   header row is meaningless.

4. **Deduplicate** (`chunk_utils.py`) — the FCA Handbook's parent chapter pages sometimes
   embed the same provisions shown on their dedicated subsection pages. Chunks are deduped
   by `(provision_id, text)` before embedding, to avoid the same content being indexed twice
   under different source files.

5. **Embed** (`generate_embeddings.py`) — generates dense vector embeddings for every chunk
   using OpenAI's `text-embedding-3-small` (1536 dimensions), batched for efficiency.

6. **Index** — two parallel indexes are built from the same deduplicated chunk set:
   - **Qdrant** (`upsert_to_qdrant.py`) — dense vector search, cosine similarity. Point IDs
     are deterministic UUIDs derived from `chunk_id`, so re-running ingestion overwrites
     rather than duplicates.
   - **BM25** (`bm25_index.py`) — sparse keyword index, for exact-term matching that dense
     embeddings can miss (e.g. specific regulation numbers).

## Query pipeline

Composed in `backend/retrieval/pipeline.py` and `backend/generation/generate.py`, run on
every incoming request:

1. **Query rewriting** (`query_rewriter.py`) — an LLM (`gpt-4o-mini`) rewrites casual or
   vague user questions into precise regulatory phrasing before retrieval. This is
   non-deterministic by default (temperature-based sampling), which is a known, documented
   tradeoff — see `docs/eval_report.md`.

2. **Hybrid search** (`hybrid_search.py`) — the rewritten query is run through both dense
   (Qdrant) and sparse (BM25) retrieval in parallel, pulling a wide candidate pool (default
   20) from each. Results are merged via **Reciprocal Rank Fusion (RRF)**, which scores by
   rank position rather than raw similarity scores, avoiding the scale-mismatch problem
   between cosine similarity and BM25 scores. Optional metadata filtering (by `tag` or
   `source_file`) is applied at this stage.

3. **Reranking** (`reranker.py`) — a cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`)
   re-scores the fused candidate pool directly against the query, narrowing to the final
   top-K (default 5). This is more accurate than embedding similarity alone, since the
   cross-encoder sees the query and each candidate together rather than as separately
   embedded vectors — but too slow to run over the full corpus, hence the two-stage
   retrieve-then-rerank design.

4. **Generation** (`generate.py`, `prompts.py`) — the top-K reranked chunks are inserted into
   a prompt that instructs the LLM (`gpt-4o`) to answer strictly from the provided context,
   cite every claim by provision ID, distinguish Rule from Guidance, and explicitly decline
   to answer if the context doesn't cover the question. This grounding is what allows the
   system to correctly refuse out-of-scope questions rather than hallucinate.

## Serving layer

`backend/api/main.py` — a FastAPI app exposing:
- `GET /health` — basic liveness check
- `POST /query` — runs the full query pipeline, returns `{query, search_query, answer, sources}`

The reranker model is loaded once at server startup (via FastAPI's `lifespan` handler), not
per-request, since model loading takes several seconds and would otherwise happen on every
cold request. CORS is configured to allow the frontend's dev origin.

Error handling distinguishes three failure modes with distinct HTTP status codes: client
input errors (400), downstream service failures — Qdrant or the LLM provider unreachable or
erroring (503), and genuinely unexpected errors (500, logged server-side but not exposed to
the caller in detail).

## Observability

`backend/observability/` — every request is logged as a structured JSON line
(`data/logs/queries.jsonl`), capturing the original query, rewritten query, full answer text,
cited sources, per-stage latency (rewrite / search+rerank / generation), and estimated
per-query cost based on token usage. A fallback tracker (`fallback_tracker.py`) analyzes
these logs to compute the rate at which the system correctly declines to answer out-of-scope
questions.

## Evaluation

`backend/eval/` — a golden dataset of hand-verified question → expected-provision pairs is
run through the full pipeline (`run_eval.py`), then scored on:
- **Retrieval precision/recall** — did we retrieve the provisions we expected?
- **RAGAS faithfulness** — are the generated claims actually supported by retrieved context?
- **RAGAS answer relevancy** — does the answer address the question asked?
- **Refusal accuracy** — does the system correctly decline out-of-scope questions?

Results and known metric limitations are written to `docs/eval_report.md` via
`eval_report.py`.

## Frontend

`frontend/` — React + TypeScript (Vite). A single-page chat interface
(`components/ChatLayout.tsx`) that calls `POST /query` and renders answers with citation
"stamps" (`components/CitationStamp.tsx`) — the product's signature visual element, showing
each cited provision's ID and Rule/Guidance status with distinct color coding. Covers empty,
loading, error, and populated states; responsive down to mobile; keyboard-accessible. See
`frontend/QA_CHECKLIST.md` for the verification checklist.

## Known limitations (see `docs/eval_report.md` for full detail)

- Query rewriting introduces run-to-run non-determinism affecting eval reproducibility
- RAGAS's `answer_relevancy` metric forces a score of 0 for answers its internal classifier
  judges "noncommittal," which can unfairly penalize correctly-hedged compliance language
- Corpus currently covers 7 SYSC sections (298 chunks) — a starting point, not the full
  Handbook
- No response streaming yet (Stage 13); no message persistence in the frontend