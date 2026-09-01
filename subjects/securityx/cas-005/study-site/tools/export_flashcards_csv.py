from __future__ import annotations

import csv
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "exports"
OUT.mkdir(parents=True, exist_ok=True)
CSV_PATH = OUT / "securityx-cas-005-comprehensive-flashcards.csv"
SUMMARY_PATH = OUT / "securityx-cas-005-comprehensive-flashcards-summary.json"

EXAM_VERSION = "CompTIA SecurityX CAS-005 Exam Objectives v3.0"
AUDIT_DATE = "2026-08-22"
OFFICIAL_OBJECTIVES_URL = (
    "https://comptiacdn.azureedge.net/webcontent/docs/default-source/exam-objectives/"
    "comptia-securityx-cas-005-exam-objectives-%283-0%291d9e61d00bce410d87e3bca2ce40fa8a.pdf"
    "?sfvrsn=aa502057_0"
)

DOMAIN_WEIGHTS = {
    "Governance, Risk, and Compliance": 20,
    "Security Architecture": 27,
    "Security Engineering": 31,
    "Security Operations": 22,
}

OBJECTIVE_STATEMENTS = {
    "1.1": "Given a set of organizational security requirements, implement the appropriate governance components.",
    "1.2": "Given a set of organizational security requirements, perform risk management activities.",
    "1.3": "Explain how compliance affects information security strategies.",
    "1.4": "Given a scenario, perform threat-modeling activities.",
    "1.5": "Summarize the information security challenges associated with artificial intelligence (AI) adoption.",
    "2.1": "Given a scenario, analyze requirements to design resilient systems.",
    "2.2": "Given a scenario, implement security in the early stages of the systems life cycle and throughout subsequent stages.",
    "2.3": "Given a scenario, integrate appropriate controls in the design of a secure architecture.",
    "2.4": "Given a scenario, apply security concepts to the design of access, authentication, and authorization systems.",
    "2.5": "Given a scenario, securely implement cloud capabilities in an enterprise environment.",
    "2.6": "Given a scenario, integrate Zero Trust concepts into system architecture design.",
    "3.1": "Given a scenario, troubleshoot common issues with identity and access management (IAM) components in an enterprise environment.",
    "3.2": "Given a scenario, analyze requirements to enhance the security of endpoints and servers.",
    "3.3": "Given a scenario, troubleshoot complex network infrastructure security issues.",
    "3.4": "Given a scenario, implement hardware security technologies and techniques.",
    "3.5": "Given a set of requirements, secure specialized and legacy systems against threats.",
    "3.6": "Given a scenario, use automation to secure the enterprise.",
    "3.7": "Explain the importance of advanced cryptographic concepts.",
    "3.8": "Given a scenario, apply the appropriate cryptographic use case and/or technique.",
    "4.1": "Given a scenario, analyze data to enable monitoring and response activities.",
    "4.2": "Given a scenario, analyze vulnerabilities and attacks, and recommend solutions to reduce the attack surface.",
    "4.3": "Given a scenario, apply threat-hunting and threat intelligence concepts.",
    "4.4": "Given a scenario, analyze data and artifacts in support of incident response activities.",
}


def clean_html(value: str) -> str:
    value = value or ""
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.I)
    value = re.sub(r"</p\s*>", "\n", value, flags=re.I)
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    value = value.replace("\u00a0", " ")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def joined(values) -> str:
    if not values:
        return ""
    return " | ".join(str(v) for v in values)


def load_cards() -> list[dict]:
    cards: list[dict] = []
    chunks = sorted(DATA.glob("cards-*.js"))
    if not chunks:
        raise SystemExit("No SecurityX card chunks found")
    for path in chunks:
        text = path.read_text(encoding="utf-8")
        start = text.find("[")
        end = text.rfind("]")
        if start < 0 or end <= start:
            raise SystemExit(f"Could not locate JSON array in {path}")
        cards.extend(json.loads(text[start : end + 1]))
    return cards


cards = load_cards()
blueprint = json.loads((DATA / "blueprint_index.json").read_text(encoding="utf-8"))
blueprint_entries = blueprint["entries"]

if len(cards) != 1156:
    raise SystemExit(f"Expected 1156 audited cards, got {len(cards)}")
if len(blueprint_entries) != 618:
    raise SystemExit(f"Expected 618 audited blueprint entries, got {len(blueprint_entries)}")
if any(len(card.get("pages", [])) != 8 for card in cards):
    raise SystemExit("Every exported card must have exactly eight study layers")
if set(OBJECTIVE_STATEMENTS) != {card["objective"] for card in cards}:
    missing = set(OBJECTIVE_STATEMENTS) - {card["objective"] for card in cards}
    extra = {card["objective"] for card in cards} - set(OBJECTIVE_STATEMENTS)
    raise SystemExit(f"Objective coverage mismatch missing={sorted(missing)} extra={sorted(extra)}")

card_ids = {card["id"] for card in cards}
missing_bp_cards = [e for e in blueprint_entries if e["card_id"] not in card_ids]
if missing_bp_cards:
    raise SystemExit(f"Blueprint entries reference missing cards: {missing_bp_cards[:5]}")

fronts = [card["front"] for card in cards]
directs = [clean_html(card["pages"][0]["content"]) for card in cards]
if len(fronts) != len(set(fronts)):
    raise SystemExit("Duplicate card fronts detected")
if len(directs) != len(set(directs)):
    raise SystemExit("Duplicate direct answers detected")

bp_by_card: dict[str, list[dict]] = defaultdict(list)
for entry in blueprint_entries:
    bp_by_card[entry["card_id"]].append(entry)

# Safely inherit published-blueprint coverage to sibling cards that share the same
# concept and objective. This adds hierarchy labels without inventing new semantic claims.
concept_bp: dict[tuple[str, str], list[dict]] = defaultdict(list)
for card in cards:
    key = (card.get("concept_id", ""), card.get("objective", ""))
    for entry in bp_by_card.get(card["id"], []):
        if entry not in concept_bp[key]:
            concept_bp[key].append(entry)

fieldnames = [
    "Front",
    "Back",
    "ID",
    "Concept_ID",
    "Deck",
    "Exam_Version",
    "Audit_Date",
    "Domain",
    "Domain_Weight_Percent",
    "Objective",
    "Objective_Statement",
    "Subdomain",
    "Topic",
    "Card_Type",
    "Difficulty",
    "Stage",
    "Estimated_Seconds",
    "Layer_1_Direct_Answer",
    "Layer_2_Concept_Expansion",
    "Layer_3_Worked_SecurityX_Scenario",
    "Layer_4_Boundaries_and_Misconceptions",
    "Layer_5_Connections_and_Memory",
    "Layer_6_Transfer_Prompt",
    "Layer_7_Mastery_Evidence",
    "Layer_8_Sources",
    "Full_Layered_Back",
    "Prerequisites",
    "Source_IDs",
    "Tags",
    "Modalities",
    "Answer_Rubric",
    "Blueprint_Topic_IDs",
    "Blueprint_Topics",
    "Blueprint_Coverage_Type",
    "Label_Domain",
    "Label_Objective",
    "Label_Subdomain",
    "Label_Topic",
    "Label_Card_Type",
    "Label_Difficulty",
    "Label_Stage",
    "Label_Blueprint_Topics",
    "Label_Sources",
    "Label_Tags",
    "Label_Modalities",
    "All_Labels",
    "Official_Objectives_URL",
]

with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as fh:
    writer = csv.DictWriter(fh, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for card in cards:
        pages = [clean_html(p.get("content", "")) for p in card["pages"]]
        direct_bp = bp_by_card.get(card["id"], [])
        inherited_bp = concept_bp.get((card.get("concept_id", ""), card["objective"]), [])
        effective_bp = direct_bp or inherited_bp
        if direct_bp:
            coverage_type = "direct-published-blueprint-map"
        elif inherited_bp:
            coverage_type = "concept-inherited-published-blueprint-map"
        else:
            coverage_type = "supporting-knowledge"

        bp_ids = [e["id"] for e in effective_bp]
        bp_topics = [e["topic"] for e in effective_bp]
        source_ids = card.get("source_ids", [])
        tags = card.get("tags", [])
        modalities = card.get("modalities", [])

        labels = [
            f"domain:{card['domain']}",
            f"objective:{card['objective']}",
            f"subdomain:{card.get('subdomain', '')}",
            f"topic:{card.get('topic', '')}",
            f"card_type:{card.get('card_type', '')}",
            f"difficulty:{card.get('difficulty', '')}",
            f"stage:{card.get('stage', '')}",
            f"coverage:{coverage_type}",
            f"exam:{EXAM_VERSION}",
        ]
        labels.extend(f"blueprint:{x}" for x in bp_topics)
        labels.extend(f"source:{x}" for x in source_ids)
        labels.extend(f"tag:{x}" for x in tags)
        labels.extend(f"modality:{x}" for x in modalities)
        labels = [x for x in labels if not x.endswith(":")]

        full_back = "\n\n".join(
            f"{card['pages'][i]['title']}\n{pages[i]}" for i in range(8)
        )
        writer.writerow(
            {
                "Front": card["front"],
                "Back": pages[0],
                "ID": card["id"],
                "Concept_ID": card.get("concept_id", ""),
                "Deck": card.get("deck", ""),
                "Exam_Version": EXAM_VERSION,
                "Audit_Date": AUDIT_DATE,
                "Domain": card["domain"],
                "Domain_Weight_Percent": DOMAIN_WEIGHTS[card["domain"]],
                "Objective": card["objective"],
                "Objective_Statement": OBJECTIVE_STATEMENTS[card["objective"]],
                "Subdomain": card.get("subdomain", ""),
                "Topic": card.get("topic", ""),
                "Card_Type": card.get("card_type", ""),
                "Difficulty": card.get("difficulty", ""),
                "Stage": card.get("stage", ""),
                "Estimated_Seconds": card.get("estimated_seconds", ""),
                "Layer_1_Direct_Answer": pages[0],
                "Layer_2_Concept_Expansion": pages[1],
                "Layer_3_Worked_SecurityX_Scenario": pages[2],
                "Layer_4_Boundaries_and_Misconceptions": pages[3],
                "Layer_5_Connections_and_Memory": pages[4],
                "Layer_6_Transfer_Prompt": pages[5],
                "Layer_7_Mastery_Evidence": pages[6],
                "Layer_8_Sources": pages[7],
                "Full_Layered_Back": full_back,
                "Prerequisites": joined(card.get("prerequisites", [])),
                "Source_IDs": joined(source_ids),
                "Tags": joined(tags),
                "Modalities": joined(modalities),
                "Answer_Rubric": clean_html(card.get("answer_rubric", "")),
                "Blueprint_Topic_IDs": joined(bp_ids),
                "Blueprint_Topics": joined(bp_topics),
                "Blueprint_Coverage_Type": coverage_type,
                "Label_Domain": card["domain"],
                "Label_Objective": card["objective"],
                "Label_Subdomain": card.get("subdomain", ""),
                "Label_Topic": card.get("topic", ""),
                "Label_Card_Type": card.get("card_type", ""),
                "Label_Difficulty": str(card.get("difficulty", "")),
                "Label_Stage": card.get("stage", ""),
                "Label_Blueprint_Topics": joined(bp_topics),
                "Label_Sources": joined(source_ids),
                "Label_Tags": joined(tags),
                "Label_Modalities": joined(modalities),
                "All_Labels": joined(labels),
                "Official_Objectives_URL": OFFICIAL_OBJECTIVES_URL,
            }
        )

domain_counts = Counter(card["domain"] for card in cards)
objective_counts = Counter(card["objective"] for card in cards)
card_type_counts = Counter(card.get("card_type", "") for card in cards)
coverage_counts = Counter()
for card in cards:
    direct_bp = bp_by_card.get(card["id"], [])
    inherited_bp = concept_bp.get((card.get("concept_id", ""), card["objective"]), [])
    coverage_counts[
        "direct-published-blueprint-map"
        if direct_bp
        else "concept-inherited-published-blueprint-map"
        if inherited_bp
        else "supporting-knowledge"
    ] += 1

summary = {
    "exam": EXAM_VERSION,
    "official_objectives_url": OFFICIAL_OBJECTIVES_URL,
    "audit_date": AUDIT_DATE,
    "cards_exported": len(cards),
    "eight_layers_per_card": all(len(c.get("pages", [])) == 8 for c in cards),
    "objective_sections": len(objective_counts),
    "published_blueprint_topics": len(blueprint_entries),
    "published_blueprint_topics_with_existing_card": len(blueprint_entries) - len(missing_bp_cards),
    "duplicate_fronts": len(fronts) - len(set(fronts)),
    "duplicate_direct_answers": len(directs) - len(set(directs)),
    "domain_weights_percent": DOMAIN_WEIGHTS,
    "domain_card_counts": dict(sorted(domain_counts.items())),
    "objective_card_counts": dict(sorted(objective_counts.items())),
    "card_type_counts": dict(sorted(card_type_counts.items())),
    "coverage_label_counts": dict(sorted(coverage_counts.items())),
    "csv_columns": fieldnames,
    "limitations": [
        "CompTIA states published objective examples are non-exhaustive; this export covers the audited public CAS-005 v3.0 blueprint and supporting knowledge, not protected live exam items.",
        "Application skill still requires unseen scenario and PBQ practice; memorizing a CSV cannot guarantee a pass.",
    ],
}
SUMMARY_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print(f"PASS cards={len(cards)} objectives={len(objective_counts)} blueprint_topics={len(blueprint_entries)}")
print(f"PASS output={CSV_PATH}")
print(f"PASS summary={SUMMARY_PATH}")
