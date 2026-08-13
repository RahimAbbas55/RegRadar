# FastAPI app entrypoint for RegRadar.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI

app = FastAPI(
    title="RegRadar API",
    description="AI compliance assistant for UK financial regulation (FCA Handbook)",
    version="0.1.0",
)

@app.get("/health")
def health_check():
    return {"status": "ok"}