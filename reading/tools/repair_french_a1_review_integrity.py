import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading" / "french" / "a1" / "passages.jsonl"
REPORT = ROOT / "reading" / "audit" / "french_a1_review_integrity_repair_2026-08-20.json"

# Lemma-aware + question-aware audit confirmed these declarations are phantom:
# the target is absent from learner-facing passage text and absent from a targeted task.
REMOVE = {
    ("fr-a1-u01-p02", "fr-rank-0048"),
    ("fr-a1-u01-p02", "fr-rank-0047"),
    ("fr-a1-u01-p03", "fr-rank-0048"),
    ("fr-a1-u01-p03", "fr-rank-0047"),
    ("fr-a1-u01-p03", "fr-rank-0061"),
    ("fr-a1-u01-p03", "fr-rank-0063"),
    ("fr-a1-u01-p04", "fr-rank-0023"),
    ("fr-a1-u01-p05", "fr-rank-0048"),
    ("fr-a1-u01-p05", "fr-rank-0047"),
    ("fr-a1-u01-p05", "fr-rank-0061"),
    ("fr-a1-u01-p05", "fr-rank-0063"),
    ("fr-a1-u01-p05", "fr-rank-0023"),
    ("fr-a1-u01-p05", "fr-rank-0035"),
    ("fr-a1-u01-p05", "fr-rank-0021"),
    ("fr-a1-u01-p06", "fr-rank-0063"),
    ("fr-a1-u03-p01", "fr-rank-0013"),
    ("fr-a1-u03-p04", "fr-rank-0038"),
    ("fr-a1-u05-p02", "fr-rank-0091"),
}

# Proven stage-label defects under docs/SPACED_REINFORCEMENT_STANDARD.md.
# These entries are real learner-facing reviews, so preserve them and normalize stage only.
RELABEL = {
    ("fr-a1-u01-p06", "fr-rank-0047"): ("R3", "R2"),
    ("fr-a1-u01-p06", "fr-rank-0061"): ("R3", "R2"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    before_hash = sha256(PATH)
    rows = [json.loads(x) for x in PATH.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(rows) != 60 or [r.get("sequence") for r in rows] != list(range(1, 61)):
        raise SystemExit("A1 structural precondition failed")

    removed = []
    relabeled = []
    seen_remove = set()
    seen_relabel = set()

    for p in rows:
        pid = p["id"]
        new_reviews = []
        for r in p.get("review_lexical_targets", []):
            key = (pid, r.get("id"))
            if key in REMOVE:
                removed.append({"passage_id": pid, "target_id": r.get("id"), "form": r.get("form"), "review_stage": r.get("review_stage"), "representation": r.get("representation")})
                seen_remove.add(key)
                continue
            if key in RELABEL:
                old, new = RELABEL[key]
                if r.get("review_stage") != old:
                    raise SystemExit(f"stage precondition failed for {key}: expected {old}, got {r.get('review_stage')}")
                nr = dict(r)
                nr["review_stage"] = new
                new_reviews.append(nr)
                relabeled.append({"passage_id": pid, "target_id": r.get("id"), "form": r.get("form"), "from": old, "to": new, "representation": r.get("representation")})
                seen_relabel.add(key)
                continue
            new_reviews.append(r)
        p["review_lexical_targets"] = new_reviews

    missing_remove = sorted(REMOVE - seen_remove)
    missing_relabel = sorted(set(RELABEL) - seen_relabel)
    if missing_remove or missing_relabel:
        raise SystemExit(f"repair precondition mismatch: missing_remove={missing_remove}, missing_relabel={missing_relabel}")
    if len(removed) != 18 or len(relabeled) != 2:
        raise SystemExit(f"unexpected repair counts removed={len(removed)} relabeled={len(relabeled)}")

    # Preserve learner-facing text/questions/answers exactly; only review metadata changes.
    PATH.write_text("\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n", encoding="utf-8")
    after_hash = sha256(PATH)

    # Deterministic postconditions.
    check = [json.loads(x) for x in PATH.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(check) != 60 or [r["sequence"] for r in check] != list(range(1, 61)):
        raise SystemExit("A1 structural postcondition failed")
    if any(len(r.get("questions", [])) != 10 or len(r.get("answer_key", [])) != 10 for r in check):
        raise SystemExit("question/answer cardinality drift")
    if any((p["id"], r.get("id")) in REMOVE for p in check for r in p.get("review_lexical_targets", [])):
        raise SystemExit("phantom review survived repair")

    report = {
        "schema_version": 1,
        "date": "2026-08-20",
        "language": "fr",
        "level": "A1",
        "status": "BOUNDED_REPAIR_APPLIED_NEEDS_POSTREPAIR_AUDIT",
        "before_sha256": before_hash,
        "after_sha256": after_hash,
        "canonical_records": len(check),
        "learner_facing_text_changed": False,
        "questions_changed": False,
        "answers_changed": False,
        "review_declarations_removed": len(removed),
        "review_stage_labels_corrected": len(relabeled),
        "removed": removed,
        "relabeled": relabeled,
        "known_unresolved_after_this_repair": [
            {
                "target_id": "fr-rank-0047",
                "lemma": "venir",
                "kind": "missing_later_R3_opportunity",
                "severity": "major",
                "note": "No natural learner-facing venir review was found in the intended +10-to-14 passage window. This repair does not fabricate one."
            }
        ],
        "release_effect": "French remains REOPEN_REQUIRED pending postrepair visibility/chronology/exposure audits and all other release gates."
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"before": before_hash, "after": after_hash, "removed": len(removed), "relabeled": len(relabeled)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
