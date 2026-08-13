# Reranker module for re-scoring retrieved chunks against a query using a cross-encoder model.
from sentence_transformers import CrossEncoder
MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
_model = None

def get_model() -> CrossEncoder:
    global _model
    if _model is None:
        print(f"Loading reranker model ({MODEL_NAME})... this may take a moment on first run.")
        _model = CrossEncoder(MODEL_NAME)
    return _model

def rerank(query: str, chunks: list[dict], top_k: int = 5) -> list[dict]:
    """Re-scores chunks against the query directly, returns the top_k most relevant."""
    if not chunks:
        return []

    model = get_model()
    pairs = [(query, chunk["text"]) for chunk in chunks]
    scores = model.predict(pairs)

    scored_chunks = [{**chunk, "rerank_score": float(score)} for chunk, score in zip(chunks, scores)]
    scored_chunks.sort(key=lambda c: c["rerank_score"], reverse=True)

    return scored_chunks[:top_k]