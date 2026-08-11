# Scrape FCA Handbook sections and save them as HTML files in the raw data directory.
import time
from pathlib import Path
import requests
TARGET_SECTIONS = [
    ("sysc1_application_purpose", "https://handbook.fca.org.uk/handbook/sysc1"),
    ("sysc3_1_systems_controls", "https://handbook.fca.org.uk/handbook/sysc3/sysc3s1"),
    ("sysc3_2_areas_covered", "https://handbook.fca.org.uk/handbook/sysc3/sysc3s2"),
    ("sysc4_general_org_requirements", "https://handbook.fca.org.uk/handbook/sysc4"),
    ("sysc6_compliance_internal_audit", "https://handbook.fca.org.uk/handbook/sysc6"),
    ("sysc10_conflicts_of_interest", "https://handbook.fca.org.uk/handbook/SYSC/10/"),
    ("sysc1_1a_application_table", "https://handbook.fca.org.uk/handbook/sysc1/sysc1s5"),
]

RAW_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"

# FCA's server expects a normal browser-like request; a missing user-agent can trigger blocks
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

def scrape_section(name: str, url: str) -> bool:
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        output_path = RAW_DATA_DIR / f"{name}.html"
        output_path.write_text(response.text, encoding="utf-8")
        print(f"✅ Saved {name} ({len(response.text)} chars)")
        return True
    except requests.RequestException as e:
        print(f"❌ Failed to fetch {name}: {e}")
        return False

if __name__ == "__main__":
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for name, url in TARGET_SECTIONS:
        results.append(scrape_section(name, url))
        time.sleep(1.5)  # delay to avoid overwhelming the server and triggering rate limits

    success_count = sum(results)
    print(f"\n{success_count}/{len(TARGET_SECTIONS)} sections scraped successfully.")