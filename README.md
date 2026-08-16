# RegRadar

A retrieval-augmented generation (RAG) system for querying UK financial regulation — FCA Handbook, AML/KYC guidance, and PSD2/PSR text — with grounded, cited answers.

## Status
🚧 In active development. Backend and frontend are both functional (Stages 1-12 of 16). Streaming, richer citations, deployment, and final docs remain.

## What it does
RegRadar answers compliance questions against the FCA Handbook (SYSC sourcebook) with:
- Hybrid retrieval (dense embeddings + BM25 keyword search, fused via Reciprocal Rank Fusion)
- Cross-encoder reranking for precision
- LLM query rewriting (casual questions → precise regulatory phrasing)
- Citation-grounded generation — every claim traces back to a specific provision ID
- Explicit Rule vs. Guidance distinction (binding vs. non-binding FCA text), visually encoded in the UI
- Refuses to answer questions outside its ingested scope, rather than guessing

## Stack
- **Backend**: FastAPI, Python 3.12
- **Vector DB**: Qdrant (hybrid dense + sparse search)
- **Embeddings**: OpenAI `text-embedding-3-small`
- **Reranking**: `cross-encoder/ms-marco-MiniLM-L-6-v2` (sentence-transformers)
- **Generation**: OpenAI `gpt-4o` (query rewriting via `gpt-4o-mini`)
- **Evaluation**: RAGAS (faithfulness, answer relevancy), custom retrieval precision/recall
- **Observability**: Structured JSON logging, per-stage latency tracking, per-query cost tracking
- **Frontend**: React + TypeScript, Vite
- **Deployment** (planned): Docker, AWS EC2, GitHub Actions CI/CD

## Architecture

See `docs/ARCHITECTURE.md` for the full system design, including the ingestion pipeline, query pipeline, and frontend structure.

See `docs/eval_report.md` for current evaluation metrics and known limitations.

## Current data coverage
7 FCA Handbook SYSC sections (governance, systems/controls, financial crime, AML), 298 deduplicated chunks — a starting corpus, not the full Handbook.

## Running locally

**Backend:**
```bash
# Start Qdrant
cd docker && docker compose up -d

# Install backend dependencies
cd ../backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Verify environment
python3 verify_setup.py

# Run ingestion (if starting fresh)
python3 ingestion/scrape_fca.py
python3 ingestion/clean_documents.py
python3 ingestion/chunk_semantic.py
python3 ingestion/generate_embeddings.py
python3 ingestion/upsert_to_qdrant.py
python3 retrieval/bm25_index.py

# Start the API
uvicorn api.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. The frontend expects the backend running at `http://localhost:8000` (configurable via `frontend/.env`, see `.env.example`).

Query the API directly:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "do i need to train my staff on money laundering?"}'
```

## Evaluation
```bash
cd backend
python3 eval/run_eval.py       # run golden dataset through the pipeline
python3 eval/eval_report.py    # generate metrics report -> docs/eval_report.md
```

## Frontend QA
See `frontend/QA_CHECKLIST.md` for the manual verification checklist covering all UI states (empty, loading, error, mobile, keyboard accessibility).

## Why
Built to demonstrate production-grade RAG architecture — hybrid retrieval, reranking, query rewriting, citation-grounded generation, and a formal evaluation harness — not just embed-and-stuff-into-prompt. Designed around UK fintech compliance use cases (Revolut, Monzo, Citi-style risk/regulatory tooling).