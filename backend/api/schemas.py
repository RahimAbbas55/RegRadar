# Pydantic request/response schemas for the RegRadar API.
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, description="The user's compliance question")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of source chunks to retrieve")
    tag: str | None = Field(default=None, description="Filter by 'R' (Rule) or 'G' (Guidance)")

class Source(BaseModel):
    provision_id: str
    tag: str | None

class QueryResponse(BaseModel):
    query: str
    search_query: str
    answer: str
    sources: list[Source]