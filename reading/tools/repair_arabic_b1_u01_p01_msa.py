import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading" / "arabic" / "b1" / "passages.jsonl"
OUT = ROOT / "reading" / "audit" / "arabic_b1_u01_p01_msa_repair_2026-08-20.json"
EXPECTED_GIT_BLOB = "53f114cd16a15f5da144b5a86a240ab131271ec1"
PID = "ar-b1-u01-p01"
QID = "q7"
OLD_PROMPT = "ما دلالة «حتى إن» في «حتى إن كانت الإجابة لا الآن»؟"
OLD_ANSWER = "تفيد أن وضوح القرار يظل مهمًا حتى في الحالة التي تكون فيها النتيجة عدم التسجيل الآن."
NEW_PROMPT = "ما دلالة «حتى إن» في الجملة: «يظل وضوح القرار مهمًا حتى إن كانت الإجابة هي «لا، ليس الآن»»؟"
NEW_ANSWER = "تفيد أن وضوح القرار يظل مهمًا حتى في الحالة التي تكون فيها الإجابة «لا، ليس الآن»."
NEW_EXPLANATION = "«حتى إن» تضيف معنى التنازل هنا: تبقى الفكرة صحيحة في هذه الحالة أيضًا."


def git_blob(path):
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = git_blob(PATH)
    if blob != EXPECTED_GIT_BLOB:
        raise SystemExit(f"B1 canonical drift: expected {EXPECTED_GIT_BLOB}, got {blob}")
    before = sha256(PATH)
    rows = [json.loads(x) for x in PATH.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(rows) != 60 or [r.get("sequence") for r in rows] != list(range(1, 61)):
        raise SystemExit("B1 structural precondition failed")

    applied = 0
    q8_snapshot = None
    for p in rows:
        if p.get("id") != PID:
            continue
        answers = {a.get("question_id"): a for a in p.get("answer_key", [])}
        qmap = {q.get("id"): q for q in p.get("questions", [])}
        q = qmap.get(QID)
        a = answers.get(QID)
        if not q or not a or q.get("prompt") != OLD_PROMPT or a.get("answer") != OLD_ANSWER or q.get("type") != "grammar_in_context":
            raise SystemExit("q7 repair precondition mismatch")
        q["prompt"] = NEW_PROMPT
        a["answer"] = NEW_ANSWER
        a["explanation"] = NEW_EXPLANATION
        p["revision"] = int(p.get("revision", 0)) + 1
        applied += 1
        q8 = qmap.get("q8")
        a8 = answers.get("q8")
        q8_snapshot = {
            "prompt": q8.get("prompt") if q8 else None,
            "type": q8.get("type") if q8 else None,
            "answer": a8.get("answer") if a8 else None,
            "status": "NEEDS_EDUCATOR_ADJUDICATION_UNCHANGED",
        }

    if applied != 1:
        raise SystemExit(f"expected exactly one q7 repair, got {applied}")
    for p in rows:
        if len(p.get("questions", [])) != 10 or len(p.get("answer_key", [])) != 10:
            raise SystemExit(f"10Q/10A regression in {p['id']}")
        if {q.get("id") for q in p.get("questions", [])} != {a.get("question_id") for a in p.get("answer_key", [])}:
            raise SystemExit(f"Q/A linkage regression in {p['id']}")

    PATH.write_text("\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n", encoding="utf-8")
    after = sha256(PATH)
    out = {
        "schema_version": 1,
        "date": "2026-08-20",
        "language": "ar",
        "level": "B1",
        "passage_id": PID,
        "status": "CONFIRMED_MSA_DEFECT_REPAIRED_NEEDS_INDEPENDENT_REVIEW",
        "before_git_blob": blob,
        "before_sha256": before,
        "after_sha256": after,
        "repair": {
            "question_id": QID,
            "old_prompt": OLD_PROMPT,
            "new_prompt": NEW_PROMPT,
            "old_answer": OLD_ANSWER,
            "new_answer": NEW_ANSWER,
            "new_explanation": NEW_EXPLANATION,
            "passage_text_changed": False,
        },
        "separate_unresolved_item": {"question_id": "q8", **(q8_snapshot or {})},
        "release_effect": "Arabic remains educator-blocked; this repair resolves only the confirmed malformed-MSA q7 defect and does not adjudicate q8 or any corpus-wide class."
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": out["status"], "after_sha256": after}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
