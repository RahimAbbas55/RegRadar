# Sends real HTTP requests to the running RegRadar API, covering the cases verified manually during development.
import httpx
BASE_URL = "http://localhost:8000"

def check(description: str, condition: bool):
    status = "✅" if condition else "❌"
    print(f"{status} {description}")
    return condition

def test_health():
    response = httpx.get(f"{BASE_URL}/health")
    return check("Health check returns 200", response.status_code == 200)

def test_valid_query():
    response = httpx.post(
        f"{BASE_URL}/query",
        json={"query": "do i need to train my staff on money laundering stuff?"},
        timeout=30.0,
    )
    ok = check("Valid query returns 200", response.status_code == 200)
    data = response.json()
    ok &= check("Response has non-empty answer", bool(data.get("answer")))
    ok &= check("Response has sources", len(data.get("sources", [])) > 0)
    return ok

def test_empty_query_rejected():
    response = httpx.post(f"{BASE_URL}/query", json={"query": "   "})
    return check("Empty query returns 400", response.status_code == 400)

def test_bad_tag_rejected():
    response = httpx.post(f"{BASE_URL}/query", json={"query": "outsourcing rules", "tag": "X"})
    return check("Invalid tag returns 400", response.status_code == 400)

def test_tag_filtered_query():
    response = httpx.post(
        f"{BASE_URL}/query",
        json={"query": "compliance function responsibilities", "tag": "R"},
        timeout=30.0,
    )
    ok = check("Tag-filtered query returns 200", response.status_code == 200)
    data = response.json()
    all_rules = all(s["tag"] == "R" for s in data.get("sources", []))
    ok &= check("All sources correctly tagged 'R'", all_rules)
    return ok

if __name__ == "__main__":
    print("Running RegRadar API smoke test (server must be running on localhost:8000)...\n")

    results = [
        test_health(),
        test_valid_query(),
        test_empty_query_rejected(),
        test_bad_tag_rejected(),
        test_tag_filtered_query(),
    ]
    print(f"\n{sum(results)}/{len(results)} checks passed.")