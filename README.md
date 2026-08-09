# RegRadar

A retrieval-augmented generation (RAG) system for querying UK financial regulation — FCA Handbook, AML/KYC guidance, and PSD2/PSR text — with grounded, cited answers.

## Status
🚧 In active development. See `docs/ARCHITECTURE.md` for design details.

## Stack
- Backend: FastAPI, Python
- Vector DB: Qdrant (hybrid dense + sparse search)
- Frontend: React + TypeScript
- Deployment: Docker, AWS EC2, GitHub Actions CI/CD

## Why
Built to demonstrate production-grade RAG architecture: hybrid retrieval, reranking, 
query rewriting, citation-grounded generation, and a formal evaluation harness — 
not just embed-and-stuff-into-prompt.# RegRadar
