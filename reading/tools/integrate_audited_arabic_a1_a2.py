#!/usr/bin/env python3
import copy
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "reading" / "audit"
A1_PATH = ROOT / "reading" / "arabic" / "a1" / "passages.jsonl"
A2_PATH = ROOT / "reading" / "arabic" / "a2" / "passages.jsonl"
REPORT_PATH = AUDIT_DIR / "arabic_a1_a2_integrated_repair_audit_2026-08-23.json"

EXPECTED_GIT_BLOBS = {
    "a1": "f1eef9fa9cf0afb0007d5a22d396e5c78b143f03",
    "a2": "e4d5470d100e22f58e75cc2386860be8960f14f0",
}

# Exact independently adjudicated unit-repair PRs.
UNIT_PRS = {
    "a1": {1: 14, 2: 18, 3: 20, 4: 21, 5: 22, 6: 23, 7: 25, 8: 26, 9: 27, 10: 28},
    "a2": {1: 29, 2: 31, 3: 32, 4: 33, 5: 34, 6: 35, 7: 37, 8: 38, 9: 39, 10: 42},
}

PATHS = {"a1": "reading/arabic/a1/passages.jsonl", "a2": "reading/arabic/a2/passages.jsonl"}
LOCAL_PATHS = {"a1": A1_PATH, "a2": A2_PATH}
WORD_BANDS = {"a1": (90, 140), "a2": (140, 220)}

BANNED_TYPES = {
    "grammar_category",
    "grammar_function",
    "person_form",
    "morphology_label",
    "syntax_label",
}
BANNED_PROMPT_PATTERNS = [
    re.compile(r"التصنيف\s+النحوي"),
    re.compile(r"التصنيف\s+الصرفي"),
    re.compile(r"نوع\s+الكلمة\s+نحوي"),
    re.compile(r"ما\s+وظيفة.+في\s+(?:الجملة|العبارة|هذا\s+الاستعمال|الاستعمال)"),
]
LATIN_RE = re.compile(r"[A-Za-z]")


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def git_blob(path: Path) -> str:
    return run("git", "hash-object", str(path))


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def parse_jsonl_text(text: str):
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def dump_jsonl(path: Path, rows):
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n", encoding="utf-8")


def structural_fingerprint(record):
    # Repairs are assessment-only. Any source-branch drift outside Q/A/review bookkeeping is rejected.
    x = copy.deepcopy(record)
    x.pop("questions", None)
    x.pop("answer_key", None)
    x.pop("quality", None)
    x.pop("revision", None)
    return x


def exact_expected_ids(level, unit):
    return [f"ar-{level}-u{unit:02d}-p{i:02d}" for i in range(1, 7)]


def fetch_pr_rows(pr_number: int, path: str):
    ref = f"refs/remotes/origin/pr-{pr_number}"
    subprocess.run(
        ["git", "fetch", "--no-tags", "origin", f"+refs/pull/{pr_number}/head:{ref}"],
        check=True,
    )
    return parse_jsonl_text(run("git", "show", f"{ref}:{path}"))


def normalize_prompt(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def count_words(text):
    return len(re.findall(r"\S+", str(text)))


def count_sentences(text):
    return sum(str(text).count(p) for p in (".", "؟", "!", "۔"))


def learner_strings(record):
    out = [record.get("text", ""), record.get("title", "")]
    for q in record.get("questions", []):
        out.append(q.get("prompt", ""))
        out.extend(q.get("options", []) or [])
    for a in record.get("answer_key", []):
        out.append(a.get("answer", ""))
        out.append(a.get("explanation", ""))
    return out


def add_error(errors, code, **detail):
    errors.append({"code": code, **detail})


def validate_level(level, rows):
    errors = []
    warnings = []
    q_count = 0
    a_count = 0
    cloze_count = 0
    qtypes = Counter()
    new_ids = []

    if len(rows) != 60:
        add_error(errors, "passage_count", level=level, expected=60, actual=len(rows))
        return errors, warnings, {}

    for idx, r in enumerate(rows, start=1):
        rid = r.get("id")
        expected_unit = (idx - 1) // 6 + 1
        expected_p = (idx - 1) % 6 + 1
        expected_id = f"ar-{level}-u{expected_unit:02d}-p{expected_p:02d}"
        if r.get("sequence") != idx:
            add_error(errors, "sequence", passage_id=rid, expected=idx, actual=r.get("sequence"))
        if r.get("unit") != expected_unit:
            add_error(errors, "unit", passage_id=rid, expected=expected_unit, actual=r.get("unit"))
        if rid != expected_id:
            add_error(errors, "id", passage_id=rid, expected=expected_id)
        if r.get("language") != "ar":
            add_error(errors, "language", passage_id=rid, actual=r.get("language"))
        if str(r.get("cefr", "")).lower() != level:
            add_error(errors, "cefr", passage_id=rid, expected=level.upper(), actual=r.get("cefr"))

        text = r.get("text", "")
        wc = count_words(text)
        lo, hi = WORD_BANDS[level]
        if not (lo <= wc <= hi):
            add_error(errors, "word_band", passage_id=rid, count=wc, band=[lo, hi])
        if r.get("word_count") != wc:
            add_error(errors, "word_count_metadata", passage_id=rid, metadata=r.get("word_count"), calculated=wc)
        sc = count_sentences(text)
        if r.get("sentence_count") != sc:
            add_error(errors, "sentence_count_metadata", passage_id=rid, metadata=r.get("sentence_count"), calculated=sc)

        qs = r.get("questions", [])
        ans = r.get("answer_key", [])
        q_count += len(qs)
        a_count += len(ans)
        if len(qs) != 10:
            add_error(errors, "question_count", passage_id=rid, actual=len(qs))
        if len(ans) != 10:
            add_error(errors, "answer_count", passage_id=rid, actual=len(ans))
        if [q.get("id") for q in qs] != [f"q{i}" for i in range(1, 11)]:
            add_error(errors, "question_ids", passage_id=rid)
        if [a.get("id") for a in ans] != [f"a{i}" for i in range(1, 11)]:
            add_error(errors, "answer_ids", passage_id=rid)

        prompts = [normalize_prompt(q.get("prompt")) for q in qs]
        dups = [p for p, n in Counter(prompts).items() if n > 1]
        if dups:
            add_error(errors, "duplicate_prompts_within_passage", passage_id=rid, prompts=dups)

        by_qid = {a.get("question_id"): a for a in ans}
        local_targets = {t.get("id") for t in r.get("new_lexical_targets", [])} | {t.get("id") for t in r.get("review_lexical_targets", [])}
        for q in qs:
            qid = q.get("id")
            qtype = q.get("type")
            qtypes[qtype] += 1
            a = by_qid.get(qid)
            if not a:
                add_error(errors, "missing_answer", passage_id=rid, question_id=qid)
                continue
            if q.get("answer_id") != a.get("id"):
                add_error(errors, "qa_link", passage_id=rid, question_id=qid, expected=q.get("answer_id"), actual=a.get("id"))
            if qtype in BANNED_TYPES:
                add_error(errors, "formal_metalinguistic_type", passage_id=rid, question_id=qid, type=qtype, prompt=q.get("prompt"))
            for pat in BANNED_PROMPT_PATTERNS:
                if pat.search(q.get("prompt", "")):
                    add_error(errors, "formal_metalinguistic_prompt", passage_id=rid, question_id=qid, prompt=q.get("prompt"))
                    break
            tids = q.get("target_ids", []) or []
            if not isinstance(tids, list):
                add_error(errors, "target_ids_not_list", passage_id=rid, question_id=qid)
            else:
                for tid in tids:
                    if tid not in local_targets:
                        add_error(errors, "question_target_not_local", passage_id=rid, question_id=qid, target_id=tid)
            if qtype == "cloze_transfer":
                cloze_count += 1
                blanks = str(q.get("prompt", "")).count("_____")
                parts = [p.strip() for p in re.split(r"[؛;]", str(a.get("answer", ""))) if p.strip()]
                if blanks != len(parts):
                    add_error(errors, "cloze_blank_answer_mismatch", passage_id=rid, question_id=qid, blanks=blanks, answer_parts=len(parts), answer=a.get("answer"))
                recon = q.get("prompt", "")
                for p in parts:
                    recon = recon.replace("_____", p.rstrip(".؟!۔"), 1)
                if "_____" in recon:
                    add_error(errors, "cloze_unfilled", passage_id=rid, question_id=qid, reconstructed=recon)

        for t in r.get("new_lexical_targets", []):
            tid = t.get("id")
            new_ids.append(tid)
            form = str(t.get("form", ""))
            actual = text.count(form) if form else 0
            if actual != t.get("exposures_in_text"):
                add_error(errors, "new_target_exposure", passage_id=rid, target_id=tid, form=form, metadata=t.get("exposures_in_text"), calculated=actual)
            if actual < 1:
                add_error(errors, "new_target_missing", passage_id=rid, target_id=tid, form=form)
            if not str(t.get("intended_sense", "")).strip():
                add_error(errors, "empty_intended_sense", passage_id=rid, target_id=tid)

        for t in r.get("review_lexical_targets", []):
            if t.get("representation") == "running_text" and str(t.get("form", "")) not in text:
                add_error(errors, "running_text_review_target_missing", passage_id=rid, target_id=t.get("id"), form=t.get("form"))

        for s in learner_strings(r):
            if LATIN_RE.search(str(s)):
                add_error(errors, "latin_script_in_learner_facing_arabic", passage_id=rid, sample=str(s)[:180])
                break

        quality = r.get("quality", {})
        if quality.get("status") != "draft":
            add_error(errors, "quality_status_not_draft", passage_id=rid, status=quality.get("status"))
        for gate in ("answer_key_check", "coverage_check", "linguistic_review", "pedagogical_review", "schema_check"):
            if quality.get(gate) != "pending":
                add_error(errors, "quality_gate_not_pending", passage_id=rid, gate=gate, value=quality.get(gate))

    dup_new = [tid for tid, n in Counter(new_ids).items() if n > 1]
    if dup_new:
        add_error(errors, "duplicate_new_target_ids", level=level, ids=dup_new)
    if q_count != 600:
        add_error(errors, "total_questions", level=level, expected=600, actual=q_count)
    if a_count != 600:
        add_error(errors, "total_answers", level=level, expected=600, actual=a_count)

    return errors, warnings, {
        "passages": len(rows),
        "questions": q_count,
        "answers": a_count,
        "clozes": cloze_count,
        "question_type_counts": dict(qtypes),
        "new_target_count": len(new_ids),
    }


def main():
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": 1,
        "date": "2026-08-23",
        "scope": "Arabic A1+A2 integrated assessment repair",
        "expected_input_git_blobs": EXPECTED_GIT_BLOBS,
        "source_prs": UNIT_PRS,
        "integration": {},
        "validation": {},
        "hard_errors": [],
        "warnings": [],
        "quality_promotion": False,
    }

    main_rows = {}
    for level, path in LOCAL_PATHS.items():
        actual_blob = git_blob(path)
        report.setdefault("actual_input_git_blobs", {})[level] = actual_blob
        if actual_blob != EXPECTED_GIT_BLOBS[level]:
            add_error(report["hard_errors"], "unexpected_input_blob", level=level, expected=EXPECTED_GIT_BLOBS[level], actual=actual_blob)
        main_rows[level] = load_jsonl(path)

    if report["hard_errors"]:
        REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise SystemExit(1)

    integrated = {level: copy.deepcopy(rows) for level, rows in main_rows.items()}
    by_id = {level: {r["id"]: r for r in rows} for level, rows in integrated.items()}

    for level, unit_map in UNIT_PRS.items():
        report["integration"][level] = []
        for unit, pr in unit_map.items():
            source_rows = fetch_pr_rows(pr, PATHS[level])
            source_unit = [r for r in source_rows if r.get("unit") == unit]
            ids = [r.get("id") for r in source_unit]
            expected_ids = exact_expected_ids(level, unit)
            if ids != expected_ids:
                add_error(report["hard_errors"], "source_unit_ids", level=level, unit=unit, pr=pr, expected=expected_ids, actual=ids)
                continue
            for src in source_unit:
                cur = by_id[level].get(src["id"])
                if cur is None:
                    add_error(report["hard_errors"], "missing_current_record", passage_id=src["id"], pr=pr)
                    continue
                if structural_fingerprint(src) != structural_fingerprint(cur):
                    add_error(report["hard_errors"], "stale_source_nonassessment_drift", passage_id=src["id"], pr=pr)
                    continue
                cur["questions"] = copy.deepcopy(src["questions"])
                cur["answer_key"] = copy.deepcopy(src["answer_key"])
                cur["revision"] = max(int(cur.get("revision") or 0), int(src.get("revision") or 0)) + 1
                q = cur.setdefault("quality", {})
                for gate in ("answer_key_check", "coverage_check", "linguistic_review", "pedagogical_review", "schema_check"):
                    q[gate] = "pending"
                q["status"] = "draft"
                notes = q.setdefault("notes", [])
                note = f"Integrated independently adjudicated operational-assessment repair from PR #{pr} on 2026-08-23; final integrated semantic/integrity review pending."
                if note not in notes:
                    notes.append(note)
            report["integration"][level].append({"unit": unit, "source_pr": pr, "passage_ids": ids})

    if report["hard_errors"]:
        REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise SystemExit(1)

    for level in ("a1", "a2"):
        dump_jsonl(LOCAL_PATHS[level], integrated[level])
        report.setdefault("output_git_blobs", {})[level] = git_blob(LOCAL_PATHS[level])
        errors, warnings, stats = validate_level(level, integrated[level])
        report["hard_errors"].extend(errors)
        report["warnings"].extend(warnings)
        report["validation"][level] = stats

    report["hard_error_count"] = len(report["hard_errors"])
    report["warning_count"] = len(report["warnings"])
    report["status"] = "PASS_DETERMINISTIC_INTEGRATED_NEEDS_SEMANTIC_REVIEW" if not report["hard_errors"] else "FAIL"
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": report["status"],
        "hard_errors": report["hard_error_count"],
        "warnings": report["warning_count"],
        "a1": report["validation"].get("a1"),
        "a2": report["validation"].get("a2"),
        "outputs": report.get("output_git_blobs", {}),
    }, ensure_ascii=False))
    if report["hard_errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
