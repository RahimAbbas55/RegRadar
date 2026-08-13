# FastAPI app entrypoint for RegRadar.
import sys
from pathlib import Path
from contextlib import asynccontextmanager
sys.path.insert(0, str(Path(__file__).parent.parent))
from fastapi import FastAPI, HTTPException
from api.schemas import QueryRequest, QueryResponse, Source
from generation.generate import generate_answer
from retrieval.reranker import get_model as get_reranker_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up the reranker model at startup, not on the first user request
    print("Warming up reranker model...")
    get_reranker_model()
    print("Reranker ready.")
    yield

app = FastAPI(
    title="RegRadar API",
    description="AI compliance assistant for UK financial regulation (FCA Handbook)",
    version="0.1.0",
    lifespan=lifespan,
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    try:
        result = generate_answer(request.query, top_k=request.top_k, tag=request.tag)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return QueryResponse(
        query=result["query"],
        search_query=result["search_query"],
        answer=result["answer"],
        sources=[Source(**s) for s in result["sources"]],
    )