# Structured JSON logging for RegRadar requests — one log line per query, machine-parseable.
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
LOG_DIR = Path(__file__).parent.parent.parent / "data" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "queries.jsonl"  

class JSONLFileHandler(logging.Handler):
    def emit(self, record):
        log_entry = record.__dict__.get("structured_data", {})
        log_entry["timestamp"] = datetime.now(timezone.utc).isoformat()
        log_entry["level"] = record.levelname
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

logger = logging.getLogger("regradar")
logger.setLevel(logging.INFO)
logger.addHandler(JSONLFileHandler())
logger.addHandler(logging.StreamHandler(sys.stdout))

def log_query(query: str, search_query: str, answer: str, sources: list[dict], **extra_fields):
    logger.info("query_processed", extra={"structured_data": {
        "event": "query_processed",
        "query": query,
        "search_query": search_query,
        "answer": answer, 
        "answer_length": len(answer),
        "source_count": len(sources),
        "source_provision_ids": [s.get("provision_id") for s in sources],
        **extra_fields,
    }})