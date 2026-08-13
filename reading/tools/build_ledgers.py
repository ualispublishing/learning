import csv
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reading" / "ledgers"
LEX = ROOT / "reading" / "lexicons"
OUT.mkdir(parents=True, exist_ok=True)
LEX.mkdir(parents=True, exist_ok=True)

SPECS = {
    "arabic": ("ar", "arabic_top1000.csv", "arabic_top3000.csv"),
    "french": ("fr", "french_top1000.csv", "french_top3000.csv"),
    "urdu": ("ur", "urdu_top1000.csv", "urdu_top3000.csv"),
}

FIELD = re.compile(r"(?m)^([^:\n]+):\s*(.+)$")
AR_DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")


def fields(back):
    return {m.group(1).strip(): m.group(2).strip() for m in FIELD.finditer(back)}


def norm(text, lang):
    text = unicodedata.normalize("NFC", text.strip()).replace("ـ", "")
    text = re.sub(r"\s+", " ", text)
    if lang in ("arabic", "urdu"):
        return AR_DIAC.sub("", text)
    return text.replace("’", "'").casefold()


def band(rank):
    if rank <= 500:
        return "A1_core_candidate"
    if rank <= 1000:
        return "A2_core_candidate"
    if rank <= 2000:
        return "B1_core_candidate"
    return "B2_core_candidate"


def read_file(lang, code, filename):
    result = []
    with (ROOT / filename).open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            meta = fields(row["Back"])
            rank = int(meta["Rank"])
            result.append({
                "id": f"{code}-rank-{rank:04d}",
                "language": code,
                "form": row["Front"].strip(),
                "match_form": norm(row["Front"], lang),
                "rank": rank,
                "meaning_en_source": meta.get("Meaning"),
                "part_of_speech_source": meta.get("Part of speech"),
                "source_file": filename,
                "planning_band": band(rank),
                "cefr_claim": False,
            })
    return result


def write_jsonl(path, rows):
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main():
    summary = {"languages": {}, "overall_gate": "PASS"}
    for lang, (code, top1, cont) in SPECS.items():
        rows = read_file(lang, code, top1) + read_file(lang, code, cont)
        ranks = [r["rank"] for r in rows]
        if len(rows) != 3000 or sorted(ranks) != list(range(1, 3001)):
            raise SystemExit(f"{lang}: invalid rank sequence")
        write_jsonl(LEX / f"{lang}.jsonl", rows)
        ledger = [{
            "id": r["id"],
            "language": code,
            "form": r["form"],
            "match_form": r["match_form"],
            "rank": r["rank"],
            "planning_band": r["planning_band"],
            "available_to_curriculum": True,
            "assumed_mastered": False,
            "introduced_in": None,
            "meaningful_contacts": 0,
            "successful_retrievals": 0,
            "failed_retrievals": 0,
            "next_reinforcement_stage": "R0",
            "last_contact_passage": None,
        } for r in rows]
        write_jsonl(OUT / f"{lang}_lexical_exposure.jsonl", ledger)
        summary["languages"][lang] = {
            "rows": len(rows),
            "rank_min": min(ranks),
            "rank_max": max(ranks),
            "distinct_ranks": len(set(ranks)),
            "assumed_mastered_true": sum(x["assumed_mastered"] for x in ledger),
            "gate": "PASS",
        }
    (OUT / "build_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
