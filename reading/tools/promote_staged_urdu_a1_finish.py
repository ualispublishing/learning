#!/usr/bin/env python3
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "reading/urdu/a1/passages.jsonl"
EVIDENCE = ROOT / "reading/audit/urdu_a1_units09_10_promotion_2026-08-22.json"
SOURCE_SHA256 = "89fbbbaf5f7b376a274accb1dc0cbe6cae82eba496f24d4bfff57cf3e2977e63"
UNITS = {
    9: {
        "files": [f"reading/urdu/a1/staging/unit09/ur-a1-u09-p0{i}.json" for i in range(1, 7)],
        "blob_shas": [
            "64b3ae387cc77a4d5d3c26a4a7c8e473cfd83fc6",
            "da46ecf6fbce474eedccc468a4349208db483b50",
            "c00b469a970b04ae3e313e248410bddabf66b31a",
            "0b2b5dee8052eb3ae7563e7c8b2ce0ddb2234da4",
            "c9abe90f1b7c8f285379043af8a3f59327087499",
            "34fdf32249eae63bbfdfc3a8992a73f32d889f3c",
        ],
        "sequences": list(range(49, 55)),
    },
    10: {
        "files": [f"reading/urdu/a1/staging/unit10/ur-a1-u10-p0{i}.json" for i in range(1, 7)],
        "blob_shas": [
            "40845d5ab0436107a25aefd162b7680abd2f1b6c",
            "92b391574bb1fe32fab6ed04b103a080d68665fc",
            "74f4b32937a30dc03555f740fe3c16246c83cb9c",
            "3ebb10f745bc929d42771dd12cdd0d7d80929681",
            "ea5563df91642a8eabe1ca74c74324f6e68ad579",
            "eac507c7f57621f5f6eed360289a53712eb263ef",
        ],
        "sequences": list(range(55, 61)),
    },
}
ASCII = re.compile(r"[A-Za-z]")
WORD_RE = re.compile(r"\w+", re.UNICODE)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def read_jsonl(data: bytes):
    return [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]


def has_surface(text: str, form: str) -> bool:
    form = (form or "").strip()
    if not form:
        return True
    if any(ch.isspace() for ch in form):
        return re.search(r"(?<!\w)" + re.escape(form) + r"(?!\w)", text, re.UNICODE) is not None
    return form in WORD_RE.findall(text or "")


def learner_strings(record):
    yield record.get("text", "")
    for q in record.get("questions", []):
        yield q.get("prompt", "")
    for a in record.get("answer_key", []):
        yield a.get("answer", "")
        yield a.get("explanation", "")


def validate_record(record, expected_seq, expected_unit, introduced_ids):
    problems = []
    if record.get("language") != "ur": problems.append("language")
    if str(record.get("cefr", "")).upper() != "A1": problems.append("cefr")
    if record.get("sequence") != expected_seq: problems.append("sequence")
    if record.get("unit") != expected_unit: problems.append("unit")
    wc = record.get("word_count")
    if not isinstance(wc, int) or not 90 <= wc <= 140: problems.append("word_count")

    qs = record.get("questions", [])
    ans = record.get("answer_key", [])
    if len(qs) != 10: problems.append("questions_count")
    if len(ans) != 10: problems.append("answers_count")
    qids = [q.get("id") for q in qs]
    aids = [a.get("id") for a in ans]
    if len(set(qids)) != len(qids): problems.append("duplicate_question_ids")
    if len(set(aids)) != len(aids): problems.append("duplicate_answer_ids")
    amap = {a.get("id"): a for a in ans}
    for q in qs:
        aid = q.get("answer_id")
        if aid not in amap or amap[aid].get("question_id") != q.get("id"):
            problems.append(f"answer_link:{q.get('id')}")

    new_targets = record.get("new_lexical_targets", [])
    reviews = record.get("review_lexical_targets", [])
    local_ids = {t.get("id") for t in new_targets + reviews if t.get("id")}
    for q in qs:
        for tid in q.get("target_ids", []) or []:
            if tid not in local_ids:
                problems.append(f"nonlocal_question_target:{tid}")

    text = record.get("text", "")
    for t in new_targets:
        tid, form = t.get("id"), t.get("form")
        if not tid or tid in introduced_ids:
            problems.append(f"new_target_collision:{tid}")
        if form and not has_surface(text, form):
            problems.append(f"new_target_not_visible:{tid}")
    for t in reviews:
        if t.get("representation") == "running_text" and t.get("form") and not has_surface(text, t.get("form")):
            problems.append(f"running_review_not_visible:{t.get('id')}")

    if expected_seq % 6 == 0 and new_targets:
        problems.append("p06_has_new_targets")
    for s in learner_strings(record):
        if ASCII.search(s or ""):
            problems.append("learner_facing_roman_script")
            break
    return problems


def validate_staged(staged):
    problems = []
    introduced = set()
    source_records = read_jsonl(CORPUS.read_bytes())
    for r in source_records:
        for t in r.get("new_lexical_targets", []):
            if t.get("id"): introduced.add(t["id"])

    unit_targets = {}
    for unit in (9, 10):
        unit_targets[unit] = set()
        for rec in staged[unit]:
            problems.extend(f"u{unit}:{rec.get('id')}:{p}" for p in validate_record(rec, rec["sequence"], unit, introduced))
            for t in rec.get("new_lexical_targets", []):
                tid = t.get("id")
                if tid:
                    introduced.add(tid)
                    unit_targets[unit].add(tid)
        p06 = staged[unit][-1]
        review_ids = {t.get("id") for t in p06.get("review_lexical_targets", []) if t.get("id")}
        if not unit_targets[unit].issubset(review_ids):
            problems.append(f"u{unit}:p06_missing_unit_reviews")

    for unit in (9, 10):
        intro = {}
        for rec in staged[unit]:
            for t in rec.get("new_lexical_targets", []):
                if t.get("form"):
                    intro[t["form"]] = rec["sequence"]
        for rec in staged[unit]:
            text = rec.get("text", "")
            for form, seq in intro.items():
                if seq > rec["sequence"] and has_surface(text, form):
                    problems.append(f"u{unit}:{rec.get('id')}:premature_target:{form}")
    return problems


def main():
    current = CORPUS.read_bytes()
    current_sha = sha256(current)
    if EVIDENCE.exists():
        ev = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        if ev.get("after_sha256") == current_sha and len(read_jsonl(current)) == 60:
            print("Already promoted and hash-bound; verify-only resume PASS")
            return
    if current_sha != SOURCE_SHA256:
        raise SystemExit(f"FAIL source drift: {current_sha} != {SOURCE_SHA256}")
    source_records = read_jsonl(current)
    if len(source_records) != 48 or [r.get("sequence") for r in source_records] != list(range(1, 49)):
        raise SystemExit("FAIL source frontier is not exact 1..48")

    staged = {}
    raw_by_unit = {}
    for unit, spec in UNITS.items():
        staged[unit], raw_by_unit[unit] = [], []
        for rel, expected_blob, expected_seq in zip(spec["files"], spec["blob_shas"], spec["sequences"]):
            data = (ROOT / rel).read_bytes()
            actual_blob = git_blob_sha(data)
            if actual_blob != expected_blob:
                raise SystemExit(f"FAIL staged blob drift {rel}: {actual_blob} != {expected_blob}")
            rec = json.loads(data.decode("utf-8"))
            if rec.get("sequence") != expected_seq:
                raise SystemExit(f"FAIL staged sequence {rel}")
            staged[unit].append(rec)
            raw_by_unit[unit].append(data.strip(b"\n"))

    problems = validate_staged(staged)
    if problems:
        raise SystemExit("FAIL validation:\n" + "\n".join(problems))

    base = current.rstrip(b"\n") + b"\n"
    after09 = base + b"\n".join(raw_by_unit[9]) + b"\n"
    final = after09 + b"\n".join(raw_by_unit[10]) + b"\n"
    final_records = read_jsonl(final)
    if len(final_records) != 60 or [r.get("sequence") for r in final_records] != list(range(1, 61)):
        raise SystemExit("FAIL final sequence/cardinality")
    qcount = sum(len(r.get("questions", [])) for r in final_records)
    acount = sum(len(r.get("answer_key", [])) for r in final_records)
    if (qcount, acount) != (600, 600):
        raise SystemExit(f"FAIL final Q/A cardinality {(qcount, acount)}")

    CORPUS.write_bytes(final)
    evidence = {
        "schema_version": 1,
        "date": "2026-08-22",
        "language": "ur",
        "level": "A1",
        "status": "PASS_DETERMINISTIC_BATCH_PROMOTION_NEEDS_FINAL_REVIEW",
        "promotion_order": [9, 10],
        "before_sha256": SOURCE_SHA256,
        "after_unit09_sha256": sha256(after09),
        "after_sha256": sha256(final),
        "canonical_passages_after": 60,
        "canonical_questions_after": 600,
        "canonical_answers_after": 600,
        "promoted_sequences": list(range(49, 61)),
        "staging_git_blobs": {str(u): dict(zip(UNITS[u]["files"], UNITS[u]["blob_shas"])) for u in (9, 10)},
        "checks": {
            "source_frontier_sha256_exact": True,
            "staging_git_blobs_exact": True,
            "promotion_order_unit09_then_unit10": True,
            "sequences_contiguous_1_60": True,
            "a1_word_band_90_140": True,
            "ten_questions_and_answers_each": True,
            "answer_linkage": True,
            "question_targets_locally_declared": True,
            "new_target_id_collisions_zero": True,
            "new_targets_visible_exact_token": True,
            "running_text_reviews_visible_exact_token": True,
            "p06_zero_new_and_reviews_unit_targets": True,
            "premature_future_target_exposure_zero_exact_token": True,
            "learner_facing_roman_script_zero": True
        },
        "formal_final_audit": "deferred under generation-first policy",
        "independent_semantic_naturalness_pedagogical_review": "PENDING",
        "educator_release_review": "PENDING",
        "release_effect": "Generation/canonicalization complete for Urdu A1 through sequence 60; Urdu remains non-release-ready pending final multi-pass review and educator release approval."
    }
    EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "after_unit09_sha256": evidence["after_unit09_sha256"], "after_sha256": evidence["after_sha256"]}, ensure_ascii=False))

if __name__ == "__main__":
    main()
