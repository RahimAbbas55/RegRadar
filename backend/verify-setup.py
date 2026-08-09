"""One-off script to verify all external dependencies are reachable before ingestion work begins."""
import sys
from config import settings


def check_qdrant() -> bool:
    from qdrant_client import QdrantClient
    try:
        client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        client.get_collections()  # simplest call that proves the API responds
        print("✅ Qdrant reachable")
        return True
    except Exception as e:
        print(f"❌ Qdrant check failed: {e}")
        return False


def check_openai() -> bool:
    from openai import OpenAI
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        # cheapest possible call that proves the key works
        client.models.list()
        print("✅ OpenAI API key valid")
        return True
    except Exception as e:
        print(f"❌ OpenAI check failed: {e}")
        return False


def check_anthropic() -> bool:
    from anthropic import Anthropic
    try:
        client = Anthropic(api_key=settings.anthropic_api_key)
        # minimal real call — Anthropic has no lightweight "list models" equivalent,
        # so a 1-token message is the standard way to confirm the key works
        client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1,
            messages=[{"role": "user", "content": "hi"}],
        )
        print("✅ Anthropic API key valid")
        return True
    except Exception as e:
        print(f"❌ Anthropic check failed: {e}")
        return False


if __name__ == "__main__":
    results = [check_qdrant(), check_openai(), check_anthropic()]
    if all(results):
        print("\nAll systems green. Ready for Stage 2 (chunking pipeline).")
        sys.exit(0)
    else:
        print("\nOne or more checks failed — fix before proceeding.")
        sys.exit(1)