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
STAGES = ["R0", "R1", "R2", "R3", "R4", "R5", "long_term"]


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


def apply_arabic_a1_exposure(ledger):
    passage_path = ROOT / "reading" / "arabic" / "a1" / "passages.jsonl"
    passages = [json.loads(x) for x in passage_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    state = {}

    def touch(tid, pid, count=1, stage=None, introduced=False):
        if not re.fullmatch(r"ar-r\d+", tid or ""):
            return
        rank = int(tid[4:])
        item = state.setdefault(tid, {
            "rank": rank,
            "introduced_in": None,
            "meaningful_contacts": 0,
            "last_contact_passage": None,
            "highest_review_stage": "R0",
        })
        if introduced and item["introduced_in"] is None:
            item["introduced_in"] = pid
        item["meaningful_contacts"] += count
        item["last_contact_passage"] = pid
        if stage and STAGES.index(stage) > STAGES.index(item["highest_review_stage"]):
            item["highest_review_stage"] = stage

    for passage in sorted(passages, key=lambda x: x["sequence"]):
        pid = passage["id"]
        for target in passage.get("new_lexical_targets", []):
            touch(target.get("id"), pid, max(1, int(target.get("exposures_in_text", 1))), introduced=True)
        for review in passage.get("review_lexical_targets", []):
            touch(review.get("id"), pid, 1, stage=review.get("review_stage"))
        for question in passage.get("questions", []):
            for tid in question.get("target_ids", []):
                touch(tid, pid, 1)

    by_id = {row["id"]: row for row in ledger}
    summary = []
    for tid, item in sorted(state.items(), key=lambda kv: kv[1]["rank"]):
        ledger_id = f"ar-rank-{item['rank']:04d}"
        if ledger_id not in by_id:
            raise SystemExit(f"missing Arabic ledger row {ledger_id}")
        row = by_id[ledger_id]
        row["introduced_in"] = item["introduced_in"]
        row["meaningful_contacts"] = item["meaningful_contacts"]
        row["last_contact_passage"] = item["last_contact_passage"]
        hi = item["highest_review_stage"]
        row["next_reinforcement_stage"] = "R1" if hi == "R0" else STAGES[min(STAGES.index(hi) + 1, len(STAGES) - 1)]
        summary.append({
            "target_id": tid,
            "rank": item["rank"],
            "introduced_in": row["introduced_in"],
            "meaningful_contacts": row["meaningful_contacts"],
            "last_contact_passage": row["last_contact_passage"],
            "next_reinforcement_stage": row["next_reinforcement_stage"],
        })
    if len(summary) != 10:
        raise SystemExit(f"expected 10 Arabic A1 Unit-01 targets, found {len(summary)}")
    return {"unit": "ar-a1-u01", "target_count": len(summary), "learner_success_assumed": False, "targets": summary}


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
        exposure = apply_arabic_a1_exposure(ledger) if lang == "arabic" else None
        write_jsonl(OUT / f"{lang}_lexical_exposure.jsonl", ledger)
        summary["languages"][lang] = {
            "rows": len(rows),
            "rank_min": min(ranks),
            "rank_max": max(ranks),
            "distinct_ranks": len(set(ranks)),
            "assumed_mastered_true": sum(x["assumed_mastered"] for x in ledger),
            "gate": "PASS",
        }
        if exposure:
            summary["languages"][lang]["curriculum_exposure"] = exposure
    (OUT / "build_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
