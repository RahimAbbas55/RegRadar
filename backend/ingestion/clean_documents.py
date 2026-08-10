# Cleaning raw FCA handbook HTML files into structured JSON with provision IDs, dates, tags, headings, and body text.
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup

RAW_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
PROVISION_PATTERN = re.compile(r"^SYSC\s+\d+(\.\d+)+[A-Z]?$")

def find_heading_for(label_tag):
    """Walks backward through preceding siblings/ancestors to find the nearest heading text."""
    for heading_tag in label_tag.find_all_previous(["h2", "h3", "h4"]):
        text = heading_tag.get_text(strip=True)
        if text:
            return text
    return None

def parse_provisions_from_soup(soup: BeautifulSoup) -> list[dict]:
    provisions = []

    for label in soup.find_all("label"):
        span = label.find("span")
        if not span:
            continue
        provision_id = span.get_text(strip=True)
        if not PROVISION_PATTERN.match(provision_id):
            continue

        header_container = label.parent

        # Date and G/R tag are sibling <span> elements within the same header container
        bold_spans = header_container.find_all("span", class_="font-bold")
        date_text = bold_spans[0].get_text(strip=True) if len(bold_spans) > 0 else None
        # The G/R tag span has an extra "provison-type" class (FCA's own typo, matched as-is)
        tag_span = header_container.find("span", class_="provison-type")
        tag_text = tag_span.get_text(strip=True) if tag_span else None

        # Body text lives in a sibling <div class="provision-meta">
        meta_div = header_container.find_next_sibling("div", class_="provision-meta")
        body_text = meta_div.get_text(separator=" ", strip=True) if meta_div else ""

        provisions.append({
            "provision_id": provision_id,
            "date": date_text,
            "tag": tag_text,  # "G" = Guidance, "R" = Rule
            "heading": find_heading_for(label),
            "text": body_text,
        })

    return provisions

def clean_file(raw_path: Path) -> dict:
    html = raw_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    provisions = parse_provisions_from_soup(soup)

    return {
        "source_file": raw_path.name,
        "provision_count": len(provisions),
        "provisions": provisions,
    }

if __name__ == "__main__":
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    raw_files = list(RAW_DIR.glob("*.html"))

    if not raw_files:
        print("No raw HTML files found in data/raw/ — run scrape_fca.py first.")
    else:
        for raw_path in raw_files:
            result = clean_file(raw_path)
            output_path = PROCESSED_DIR / f"{raw_path.stem}.json"
            output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(f"✅ {raw_path.name} → {result['provision_count']} provisions extracted")