import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading" / "arabic" / "a1" / "passages.jsonl"
REPORT = ROOT / "reading" / "audit" / "arabic_a1_u01_metalinguistic_refinement_2026-08-20.json"
EXPECTED_BEFORE_SHA256 = "6cb78aa291c9e4e19c26fcb165b50edb9c2346ace90635b099fda9a7535409b0"
PID = "ar-a1-u01-p02"
QID = "q7"
OLD = "إذا كانت المدرسة لاحقًا، أي جملة صحيحة: «نذهب إلى المدرسة بعد قليل» أم «نذهب إلى المدرسة قبل قليل»؟"
NEW = "ستذهب ليلى إلى المدرسة بعد دقائق. أي جملة أنسب: «نذهب إلى المدرسة بعد قليل» أم «نذهب إلى المدرسة قبل قليل»؟"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    before = sha256(PATH)
    if before != EXPECTED_BEFORE_SHA256:
        raise SystemExit(f"refinement hash drift: expected {EXPECTED_BEFORE_SHA256}, got {before}")
    rows = [json.loads(x) for x in PATH.read_text(encoding="utf-8").splitlines() if x.strip()]
    matches = 0
    for p in rows:
        if p.get("id") != PID:
            continue
        for q in p.get("questions", []):
            if q.get("id") == QID:
                if q.get("prompt") != OLD or q.get("type") != "grammar_choice":
                    raise SystemExit("refinement precondition mismatch")
                q["prompt"] = NEW
                p["revision"] = int(p.get("revision", 0)) + 1
                matches += 1
    if matches != 1:
        raise SystemExit(f"expected one refinement, got {matches}")
    for p in rows:
        if len(p.get("questions", [])) != 10 or len(p.get("answer_key", [])) != 10:
            raise SystemExit(f"10Q/10A regression: {p['id']}")
    PATH.write_text("\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n", encoding="utf-8")
    after = sha256(PATH)
    out = {
        "schema_version": 1,
        "date": "2026-08-20",
        "language": "ar",
        "level": "A1",
        "unit": 1,
        "status": "SELF_REVIEW_REFINEMENT_APPLIED_NEEDS_INDEPENDENT_REVIEW",
        "before_sha256": before,
        "after_sha256": after,
        "passage_id": PID,
        "question_id": QID,
        "old_prompt": OLD,
        "new_prompt": NEW,
        "reason": "Removed awkward semantics in the first bounded repair while preserving the operational temporal-use assessment and answer.",
        "release_effect": "No release effect; Arabic remains educator-blocked."
    }
    REPORT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"refined": matches, "after": after}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
