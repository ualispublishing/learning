import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading" / "urdu" / "a1" / "passages.jsonl"
REPORT = ROOT / "reading" / "audit" / "urdu_a1_wave1b_cloze_key_normalization_2026-08-23.json"
EXPECTED_GIT_BLOB = "71274b00bf4ba7cf149804132f1b4eae21478d40"
TERMINAL = re.compile(r"[۔.!?؟]+$")


def git_blob_sha(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def key_parts(answer: str):
    return [part.strip() for part in answer.split("؛")]


def normalized_answer(answer: str):
    return "؛ ".join(TERMINAL.sub("", part).strip() for part in key_parts(answer))


def reconstruct(prompt: str, answer: str):
    out = prompt
    for part in key_parts(answer):
        if "_____" not in out:
            raise AssertionError(f"Too many keyed parts: {prompt!r} / {answer!r}")
        out = out.replace("_____", part, 1)
    if "_____" in out:
        raise AssertionError(f"Too few keyed parts: {prompt!r} / {answer!r}")
    return out


actual = git_blob_sha(PATH)
if actual != EXPECTED_GIT_BLOB:
    raise SystemExit(f"Refusing normalization: expected {EXPECTED_GIT_BLOB}, found {actual}")

raw_lines = PATH.read_text(encoding="utf-8").splitlines()
rows = [json.loads(x) for x in raw_lines if x]
if len(rows) != 60 or [r["sequence"] for r in rows] != list(range(1, 61)):
    raise SystemExit("Unexpected Urdu A1 frontier")

changed_rows = set()
changes = []
cloze_count = 0
reconstructed_changed = []

for row in rows:
    answers_by_q = {a["question_id"]: a for a in row["answer_key"]}
    for q in row["questions"]:
        if q.get("type") != "cloze_transfer":
            continue
        cloze_count += 1
        a = answers_by_q[q["id"]]
        old = a["answer"]
        new = normalized_answer(old)
        if new != old:
            a["answer"] = new
            changed_rows.add(row["id"])
            changes.append({
                "passage_id": row["id"],
                "sequence": row["sequence"],
                "question_id": q["id"],
                "answer_id": a["id"],
                "old_answer": old,
                "new_answer": new,
            })
        for part in key_parts(a["answer"]):
            if TERMINAL.search(part):
                raise AssertionError(f"Terminal punctuation remains in {row['id']}/{q['id']}: {part!r}")
        rec = reconstruct(q["prompt"], a["answer"])
        if row["id"] in changed_rows and any(c["question_id"] == q["id"] for c in changes if c["passage_id"] == row["id"]):
            reconstructed_changed.append({
                "passage_id": row["id"],
                "question_id": q["id"],
                "prompt": q["prompt"],
                "answer": a["answer"],
                "reconstructed": rec,
            })

if cloze_count != 130:
    raise AssertionError(f"Expected 130 cloze questions after Wave 1A, found {cloze_count}")
if not changes:
    raise AssertionError("Expected at least one legacy cloze key with terminal punctuation")

for row in rows:
    if row["id"] not in changed_rows:
        continue
    row["revision"] = int(row.get("revision", 0)) + 1
    ql = row.setdefault("quality", {})
    ql["answer_key_check"] = "pending"
    ql["schema_check"] = "pending"
    ql["status"] = "draft"
    note = "Wave 1B cloze-key punctuation normalization applied 2026-08-23; answer/schema revalidation pending."
    notes = ql.setdefault("notes", [])
    if note not in notes:
        notes.append(note)

out_lines = []
for original, row in zip(raw_lines, rows):
    if row["id"] in changed_rows:
        out_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
    else:
        out_lines.append(original)
PATH.write_text("\n".join(out_lines) + "\n", encoding="utf-8")

REPORT.write_text(json.dumps({
    "schema_version": 1,
    "date": "2026-08-23",
    "language": "urdu",
    "level": "A1",
    "input_git_blob_sha": EXPECTED_GIT_BLOB,
    "cloze_question_count": cloze_count,
    "normalized_key_count": len(changes),
    "changed_passage_ids": sorted(changed_rows),
    "changes": changes,
    "reconstructed_changed_items": reconstructed_changed,
    "validation": {
        "all_cloze_blank_counts_match_key_part_counts": True,
        "no_cloze_key_part_has_terminal_sentence_punctuation": True,
        "quality_promotion": False
    }
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"cloze_count": cloze_count, "normalized": len(changes), "passages": sorted(changed_rows)}, ensure_ascii=False))
