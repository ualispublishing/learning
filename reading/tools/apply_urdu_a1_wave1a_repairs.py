import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading" / "urdu" / "a1" / "passages.jsonl"
REPORT = ROOT / "reading" / "audit" / "urdu_a1_wave1a_reconstructed_clozes_2026-08-23.json"
EXPECTED_GIT_BLOB = "16507c293ae39cd44f7f5136dd00c9ef029646a7"
DATE = "2026-08-23"


def git_blob_sha(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def split_key(answer: str):
    return [part.strip() for part in answer.split("؛")]


def reconstruct(prompt: str, answer: str) -> str:
    parts = split_key(answer)
    out = prompt
    for part in parts:
        if "_____" not in out:
            raise AssertionError(f"Too many keyed parts for prompt: {prompt!r} / {answer!r}")
        out = out.replace("_____", part, 1)
    if "_____" in out:
        raise AssertionError(f"Too few keyed parts for prompt: {prompt!r} / {answer!r}")
    return out


actual_blob = git_blob_sha(PATH)
if actual_blob != EXPECTED_GIT_BLOB:
    raise SystemExit(f"Refusing repair: expected canonical blob {EXPECTED_GIT_BLOB}, found {actual_blob}")

raw_lines = PATH.read_text(encoding="utf-8").splitlines()
if len(raw_lines) != 60:
    raise SystemExit(f"Refusing repair: expected 60 passages, found {len(raw_lines)}")
rows = [json.loads(line) for line in raw_lines]
by_id = {row["id"]: row for row in rows}
if len(by_id) != 60 or sorted(row["sequence"] for row in rows) != list(range(1, 61)):
    raise SystemExit("Refusing repair: passage IDs/sequences are not the expected 60-record A1 frontier")

changed = set()
repair_log = []


def question(row_id, qid):
    row = by_id[row_id]
    return next(q for q in row["questions"] if q["id"] == qid)


def answer(row_id, aid):
    row = by_id[row_id]
    return next(a for a in row["answer_key"] if a["id"] == aid)


def set_question(row_id, qid, *, old_prompt, new_prompt, new_type=None):
    q = question(row_id, qid)
    if q["prompt"] != old_prompt:
        raise AssertionError(f"{row_id}/{qid} prompt drift: {q['prompt']!r}")
    before = dict(q)
    q["prompt"] = new_prompt
    if new_type is not None:
        q["type"] = new_type
    changed.add(row_id)
    repair_log.append({"passage_id": row_id, "item": qid, "kind": "question", "before": before, "after": dict(q)})


def set_answer(row_id, aid, *, old_answer, new_answer):
    a = answer(row_id, aid)
    if a["answer"] != old_answer:
        raise AssertionError(f"{row_id}/{aid} answer drift: {a['answer']!r}")
    before = dict(a)
    a["answer"] = new_answer
    changed.add(row_id)
    repair_log.append({"passage_id": row_id, "item": aid, "kind": "answer", "before": before, "after": dict(a)})


# U1 P04: restore the real/future conditional used by the source and correct the semantic scope of اگر.
set_question("ur-a1-u01-p04", "q1", old_prompt="اگر بارش شروع ہوتی تو عائشہ اور خالہ کیا کرتیں؟", new_prompt="اگر بارش شروع ہو تو عائشہ اور خالہ کیا کریں گی؟")
set_answer("ur-a1-u01-p04", "a1", old_answer="وہ گھر میں رہتیں۔", new_answer="وہ گھر میں رہیں گی۔")
set_question("ur-a1-u01-p04", "q3", old_prompt="«اگر» کیا بتاتا ہے؟ الف) ایک شرط اور نتیجہ ب) صرف ایک جگہ ج) صرف ایک شخص", new_prompt="«اگر» جملے کے کس حصے کو شروع کرتا ہے؟ الف) شرط ب) جگہ ج) شخص", new_type="vocabulary_in_context")
set_answer("ur-a1-u01-p04", "a3", old_answer="الف) ایک شرط اور نتیجہ۔", new_answer="الف) شرط۔")

# U4 checkpoint: keep both exact review targets while making the keyed completion grammatical.
set_question("ur-a1-u04-p06", "q9", old_prompt="خالی جگہیں پُر کریں: یہ _____ _____ ہے۔", new_prompt="خالی جگہیں پُر کریں: یہ _____ _____ کے کمرے ہیں۔")

# U5 P01: make Q/A relation literal rather than an unanswerable why-frame.
set_question("ur-a1-u05-p01", "q5", old_prompt="مختصر اور واضح جواب کیوں اچھا سمجھا جاتا ہے؟", new_prompt="استاد اچھے جواب کے بارے میں کیا کہتے ہیں؟", new_type="literal_detail")
set_answer("ur-a1-u05-p01", "a5", old_answer="کیونکہ استاد کہتے ہیں کہ اچھا جواب مختصر اور واضح ہوتا ہے۔", new_answer="وہ کہتے ہیں کہ اچھا جواب مختصر اور واضح ہوتا ہے۔")

# U6 checkpoint: repair prompt/answer alignment and multi-blank answer order.
set_question("ur-a1-u06-p06", "q3", old_prompt="صبح اور شام عائشہ کی واپسی کی ترتیب کیا ہے؟", new_prompt="صبح اور شام عائشہ کی روز کی ترتیب کیا ہے؟")
set_question("ur-a1-u06-p06", "q8", old_prompt="خالی جگہیں پُر کریں: یہ میرا _____ بس کا _____ ہے۔", new_prompt="خالی جگہیں پُر کریں: یہ بس میں میرا _____ _____ ہے۔")
set_answer("ur-a1-u06-p06", "a8", old_answer="سفر؛ پہلا", new_answer="پہلا؛ سفر")
set_question("ur-a1-u06-p06", "q9", old_prompt="خالی جگہیں پُر کریں: _____ نکلتے وقت _____ واپسی کا وقت بتاؤ؛ ضرورت ہو تو _____ کرو اور دوسرا _____ دیکھو۔", new_prompt="خالی جگہیں پُر کریں: _____ گھر سے نکلتے وقت بتاؤ کہ _____ کو کب واپس آؤ گے؛ ضرورت ہو تو _____ کرو اور دوسرا _____ دیکھو۔")
set_answer("ur-a1-u06-p06", "a10", old_answer="صحیح؛ اجازت", new_answer="اجازت؛ صحیح")

# U7: remove invalid/forced adverb frames while preserving exact targets.
set_question("ur-a1-u07-p04", "q9", old_prompt="خالی جگہ پُر کریں: _____ میں یہ کام پہلے کروں گا۔", new_prompt="خالی جگہ پُر کریں: _____ یہ کام پہلے کروں گا۔")
set_question("ur-a1-u07-p06", "q10", old_prompt="خالی جگہیں پُر کریں: سوال _____ پڑھو اور _____ وقت لکھو۔", new_prompt="خالی جگہیں پُر کریں: سوال _____ پڑھو اور لکھو کہ اسے حل کرنے میں _____ کتنا وقت لگے گا۔")

# U8: preserve target forms while fixing gender and Q/A grounding.
set_question("ur-a1-u08-p05", "q9", old_prompt="خالی جگہ پُر کریں: میں نے _____ کتاب پڑھ لی۔", new_prompt="خالی جگہ پُر کریں: میں نے _____ سبق پڑھ لیا۔")
set_question("ur-a1-u08-p06", "q5", old_prompt="جواب لکھتے وقت عائشہ کو دوسرے قلم کی ضرورت کیوں یاد آتی ہے؟", new_prompt="جواب لکھتے وقت عائشہ کو کیا کرنا پڑا؟", new_type="literal_detail")
set_question("ur-a1-u08-p06", "q10", old_prompt="خالی جگہیں پُر کریں: _____ گئی تو ہر _____ سنبھالی؛ میز کا _____ کام ہوا مگر کچھ _____ تھا۔", new_prompt="خالی جگہیں پُر کریں: _____ گئی تو ہم نے ہر _____ کو سنبھالا؛ _____ ہفتہ گھر کے کام ہوتے رہے اور کچھ کاغذ _____ تھے۔")

# U9: repair clozes whose keyed target form cannot grammatically fit the old frame.
set_question("ur-a1-u09-p01", "q10", old_prompt="خالی جگہ پُر کریں: مجھے یہ کتاب مریم کو _____ ہے۔", new_prompt="خالی جگہ پُر کریں: میں یہ کتاب مریم کو _____ چاہتی ہوں۔")
set_question("ur-a1-u09-p05", "q10", old_prompt="خالی جگہ پُر کریں: روز چلنے کا ایک _____ صحت ہے۔", new_prompt="خالی جگہ پُر کریں: روز چلنے کا ایک _____ یہ ہے کہ صحت بہتر رہتی ہے۔")

# Invalidate only gates touched by Q/A repairs; do not promote any gate.
for row_id in sorted(changed):
    row = by_id[row_id]
    row["revision"] = int(row.get("revision", 0)) + 1
    ql = row.setdefault("quality", {})
    for key in ("answer_key_check", "linguistic_review", "pedagogical_review", "schema_check"):
        ql[key] = "pending"
    ql["status"] = "draft"
    note = "Wave 1A bounded Q/A repair applied 2026-08-23; gate revalidation pending."
    notes = ql.setdefault("notes", [])
    if note not in notes:
        notes.append(note)

# Global structural validation and deterministic cloze reconstruction report.
reconstructions = []
for row in rows:
    qids = [q["id"] for q in row["questions"]]
    aids = [a["id"] for a in row["answer_key"]]
    if len(qids) != len(set(qids)) or len(aids) != len(set(aids)):
        raise AssertionError(f"Duplicate Q/A IDs in {row['id']}")
    answer_by_q = {a["question_id"]: a for a in row["answer_key"]}
    for q in row["questions"]:
        if q["answer_id"] not in aids:
            raise AssertionError(f"Missing answer_id {q['answer_id']} in {row['id']}/{q['id']}")
        a = answer_by_q.get(q["id"])
        if not a or a["id"] != q["answer_id"]:
            raise AssertionError(f"Q/A linkage failure in {row['id']}/{q['id']}")
        if q.get("type") == "cloze_transfer":
            reconstructed = reconstruct(q["prompt"], a["answer"])
            reconstructions.append({
                "passage_id": row["id"],
                "sequence": row["sequence"],
                "question_id": q["id"],
                "prompt": q["prompt"],
                "answer": a["answer"],
                "reconstructed": reconstructed,
            })

if not reconstructions:
    raise AssertionError("No cloze questions found")

# Preserve untouched JSONL lines exactly; only changed passage lines are reserialized.
out_lines = []
for original, row in zip(raw_lines, rows):
    if row["id"] in changed:
        out_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
    else:
        out_lines.append(original)
PATH.write_text("\n".join(out_lines) + "\n", encoding="utf-8")

REPORT.write_text(json.dumps({
    "schema_version": 1,
    "date": DATE,
    "language": "urdu",
    "level": "A1",
    "input_git_blob_sha": EXPECTED_GIT_BLOB,
    "changed_passage_ids": sorted(changed),
    "changed_passage_count": len(changed),
    "repair_operations": repair_log,
    "cloze_question_count": len(reconstructions),
    "structural_validation": "pass",
    "reconstructions": reconstructions,
    "quality_promotion": False,
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"changed": sorted(changed), "cloze_count": len(reconstructions), "report": str(REPORT.relative_to(ROOT))}, ensure_ascii=False))
