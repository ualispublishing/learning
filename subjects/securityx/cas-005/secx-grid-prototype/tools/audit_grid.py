from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT.parent / "study-site" / "data"

EXPECTED_OBJECTIVES = {
    "1.1", "1.2", "1.3", "1.4", "1.5",
    "2.1", "2.2", "2.3", "2.4", "2.5", "2.6",
    "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8",
    "4.1", "4.2", "4.3", "4.4",
}
EXPECTED_DOMAINS = {
    "Governance, Risk, and Compliance",
    "Security Architecture",
    "Security Engineering",
    "Security Operations",
}


def load_cards() -> list[dict]:
    cards: list[dict] = []
    chunks = sorted(DATA.glob("cards-*.js"))
    assert len(chunks) == 29, f"expected 29 chunks, got {len(chunks)}"
    for path in chunks:
        text = path.read_text(encoding="utf-8")
        start, end = text.find("["), text.rfind("]")
        assert start >= 0 and end > start, f"JSON array not found in {path.name}"
        cards.extend(json.loads(text[start : end + 1]))
    return cards


cards = load_cards()
blueprint = json.loads((DATA / "blueprint_index.json").read_text(encoding="utf-8"))["entries"]
index = (ROOT / "index.html").read_text(encoding="utf-8")
app = (ROOT / "app-v2.js").read_text(encoding="utf-8")
css = (ROOT / "styles.css").read_text(encoding="utf-8")

assert len(cards) == 1156, len(cards)
assert len(blueprint) == 618, len(blueprint)
assert all(len(card.get("pages", [])) == 8 for card in cards), "all cards must retain 8 layers"
assert len({card["id"] for card in cards}) == len(cards), "duplicate card IDs"
assert len({card["front"] for card in cards}) == len(cards), "duplicate card fronts"

numbered = [card for card in cards if card.get("objective") != "Acronyms"]
acronyms = [card for card in cards if card.get("objective") == "Acronyms"]
assert len(acronyms) == 191, len(acronyms)
assert {card["objective"] for card in numbered} == EXPECTED_OBJECTIVES
assert {card["domain"] for card in numbered} == EXPECTED_DOMAINS

for card in numbered:
    for field in ("id", "domain", "objective", "subdomain", "topic", "front", "concept_id"):
        assert card.get(field), f"{card.get('id')} missing {field}"
    assert card.get("source_ids"), f"{card['id']} missing source_ids"

# Every numbered card must be addressable by the exact grid path.
paths = [
    (card["domain"], card["objective"], card["subdomain"], card["topic"], card["id"])
    for card in numbered
]
assert len(paths) == len(set(paths)), "duplicate hierarchy-addressable card path"

card_ids = {card["id"] for card in cards}
assert all(entry["card_id"] in card_ids for entry in blueprint), "blueprint references missing card"

# UI contract: alternate site must use v2 and retain requested keyboard semantics.
assert '<script src="app-v2.js"></script>' in index
for token in ("ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Enter", "Escape", "Home", "openRelated", "cycleProgress", "localStorage"):
    assert token in app, f"missing UI contract token {token}"
for key_label in ("mastery", "related", "deeper", "shallower"):
    assert key_label in index.lower(), f"missing control label {key_label}"
for css_token in ("progress-1", "progress-2", "progress-3", "progress-4", "related-hint"):
    assert css_token in css, f"missing CSS state {css_token}"

# No invented semantic relationship classes: related edges must stay tied to exact existing metadata.
for required_relation in ("PREREQUISITE", "SAME CONCEPT", "SAME BLUEPRINT", "SAME TOPIC"):
    assert required_relation in app

objective_counts = Counter(card["objective"] for card in numbered)
domain_counts = Counter(card["domain"] for card in numbered)
print("PASS SecX alternate-grid deterministic audit")
print(f"PASS cards={len(cards)} numbered={len(numbered)} acronyms={len(acronyms)} blueprint={len(blueprint)} objectives={len(objective_counts)}")
print("PASS domains=" + ", ".join(f"{name}:{domain_counts[name]}" for name in sorted(domain_counts)))
print("PASS all 1,156 cards retain eight layers and all numbered cards are hierarchy-addressable")
