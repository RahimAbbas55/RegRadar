# FastAPI app entrypoint for RegRadar.
import sys
from pathlib import Path
from contextlib import asynccontextmanager
sys.path.insert(0, str(Path(__file__).parent.parent))
from fastapi import FastAPI, HTTPException
from api.schemas import QueryRequest, QueryResponse, Source
from generation.generate import generate_answer
from retrieval.reranker import get_model as get_reranker_model
from qdrant_client.http.exceptions import UnexpectedResponse, ResponseHandlingException
from openai import APIError as OpenAIAPIError
from observability.logger import log_query
import httpx

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
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty or whitespace only.")

    if request.tag and request.tag not in ("R", "G"):
        raise HTTPException(status_code=400, detail="tag must be 'R' or 'G' if provided.")

    try:
        result = generate_answer(request.query, top_k=request.top_k, tag=request.tag)
    except ResponseHandlingException as e:
        # Qdrant unreachable entirely — server down, wrong host/port, network issue
        raise HTTPException(status_code=503, detail=f"Vector database unreachable: {e}")
    except UnexpectedResponse as e:
        # Qdrant reachable but returned an error response
        raise HTTPException(status_code=503, detail=f"Vector database error: {e}")
    except OpenAIAPIError as e:
        raise HTTPException(status_code=503, detail=f"LLM provider error: {e}")
    except Exception as e:
        print(f"Unexpected error in /query: {type(e).__module__}.{type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your query.")

    log_query(
        query=result["query"],
        search_query=result["search_query"],
        answer=result["answer"],
        sources=result["sources"],
        timings=result.get("timings", {}),
        cost_usd=result.get("cost_usd", 0),
    )

    return QueryResponse(
        query=result["query"],
        search_query=result["search_query"],
        answer=result["answer"],
        sources=[Source(**s) for s in result["sources"]],
    )