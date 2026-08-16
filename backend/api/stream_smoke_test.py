# Verifies the /query/stream SSE endpoint produces a well-formed event sequence: sources -> tokens -> done.
import json
import httpx
BASE_URL = "http://localhost:8000"

def check(description: str, condition: bool):
    status = "✅" if condition else "❌"
    print(f"{status} {description}")
    return condition

def parse_sse_events(response_text: str) -> list[dict]:
    events = []
    for line in response_text.strip().split("\n"):
        if line.startswith("data: "):
            events.append(json.loads(line[len("data: "):]))
    return events

if __name__ == "__main__":
    print("Sending streaming request...\n")

    with httpx.stream(
        "POST",
        f"{BASE_URL}/query/stream",
        json={"query": "do i need to train my staff on money laundering stuff?"},
        timeout=30.0,
    ) as response:
        full_text = ""
        for chunk in response.iter_text():
            full_text += chunk

    events = parse_sse_events(full_text)

    print(f"Received {len(events)} events\n")

    check("At least 3 events received", len(events) >= 3)
    check("First event is 'sources'", events[0]["type"] == "sources" if events else False)
    check("Sources list is non-empty", len(events[0].get("sources", [])) > 0 if events else False)

    token_events = [e for e in events if e["type"] == "token"]
    check("At least one 'token' event", len(token_events) > 0)

    reconstructed_answer = "".join(e["text"] for e in token_events)
    check("Reconstructed answer is non-empty", len(reconstructed_answer) > 0)

    check("Last event is 'done'", events[-1]["type"] == "done" if events else False)
    check("No 'error' events present", not any(e["type"] == "error" for e in events))

    print(f"\nReconstructed answer preview: {reconstructed_answer[:150]}...")