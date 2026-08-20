import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANON = ROOT / "reading" / "urdu" / "a1" / "passages.jsonl"
STAGING = ROOT / "reading" / "urdu" / "a1" / "staging" / "unit06"
OUT = ROOT / "reading" / "audit" / "urdu_a1_unit06_promotion_2026-08-20.json"
EXPECTED_CANON_GIT_BLOB = "4a267176ce4119c84c7886fc80e46c873f432119"
EXPECTED_STAGED_BLOBS = {
    "ur-a1-u06-p01.json": "5349f6c156b4d8d3e11ddbb2bb9cf43aedad5d88",
    "ur-a1-u06-p02.json": "5de47820796a0443435f42a957647d3309acc39b",
    "ur-a1-u06-p03.json": "6c7fd786262adbdb7d80ade96115d0199a05c211",
    "ur-a1-u06-p04.json": "4ebc5ef3076c3aab27a0d054fb3622497d900c7d",
    "ur-a1-u06-p05.json": "9888a917b4ca29f0bc36ad1c0c31a58b92910423",
    "ur-a1-u06-p06.json": "18c6c57918c665f26c43ca644e9da092d17a5bb7",
}
ROMAN_RE = re.compile(r"[A-Za-z]")


def git_blob(path):
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_record(p, seq):
    if p.get("sequence") != seq or p.get("unit") != 6 or p.get("id") != f"ur-a1-u06-p{seq-30:02d}":
        raise SystemExit(f"identity/sequence mismatch for staged sequence {seq}")
    if p.get("language") != "ur" or p.get("cefr") != "A1":
        raise SystemExit(f"language/CEFR mismatch for {p.get('id')}")
    wc = p.get("word_count")
    if not isinstance(wc, int) or not 90 <= wc <= 140:
        raise SystemExit(f"A1 word-band failure for {p['id']}: {wc}")
    qs, ans = p.get("questions", []), p.get("answer_key", [])
    if len(qs) != 10 or len(ans) != 10:
        raise SystemExit(f"10Q/10A failure for {p['id']}")
    qids = {q.get("id") for q in qs}
    if {a.get("question_id") for a in ans} != qids:
        raise SystemExit(f"answer linkage failure for {p['id']}")
    declared = {x.get("id") for x in p.get("new_lexical_targets", []) + p.get("review_lexical_targets", [])}
    for q in qs:
        unknown = set(q.get("target_ids", [])) - declared
        if unknown:
            raise SystemExit(f"undeclared question targets in {p['id']}: {sorted(unknown)}")
    text = p.get("text", "")
    for t in p.get("new_lexical_targets", []):
        form = t.get("form")
        if not form or form not in text:
            raise SystemExit(f"new target not visible in {p['id']}: {t.get('id')} {form}")
    for r in p.get("review_lexical_targets", []):
        if r.get("representation") == "running_text" and r.get("form") not in text:
            raise SystemExit(f"running-text review not visible in {p['id']}: {r.get('id')}")
    if seq == 36 and p.get("new_lexical_targets"):
        raise SystemExit("Unit 06 checkpoint P06 must have zero new lexical targets")
    learner = " ".join([p.get("title", ""), p.get("text", "")] + [q.get("prompt", "") for q in qs] + [a.get("answer", "") for a in ans])
    if ROMAN_RE.search(learner):
        raise SystemExit(f"Roman-script learner-facing leakage in {p['id']}")


def main():
    canon_blob = git_blob(CANON)
    if canon_blob != EXPECTED_CANON_GIT_BLOB:
        raise SystemExit(f"canonical frontier drift: expected blob {EXPECTED_CANON_GIT_BLOB}, got {canon_blob}")
    before_sha256 = sha256(CANON)
    rows = [json.loads(x) for x in CANON.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(rows) != 30 or [r.get("sequence") for r in rows] != list(range(1, 31)):
        raise SystemExit("live Urdu A1 is not the verified contiguous 1-30 frontier")

    existing_ids = {r.get("id") for r in rows}
    existing_target_ids = {t.get("id") for r in rows for t in r.get("new_lexical_targets", [])}
    staged = []
    staged_target_ids = set()
    staged_blob_evidence = {}
    for i, name in enumerate(EXPECTED_STAGED_BLOBS, start=31):
        path = STAGING / name
        actual_blob = git_blob(path)
        expected_blob = EXPECTED_STAGED_BLOBS[name]
        if actual_blob != expected_blob:
            raise SystemExit(f"staging drift for {name}: expected {expected_blob}, got {actual_blob}")
        staged_blob_evidence[name] = actual_blob
        p = json.loads(path.read_text(encoding="utf-8"))
        validate_record(p, i)
        if p.get("id") in existing_ids:
            raise SystemExit(f"passage ID collision: {p['id']}")
        new_ids = {t.get("id") for t in p.get("new_lexical_targets", [])}
        collision = new_ids & (existing_target_ids | staged_target_ids)
        if collision:
            raise SystemExit(f"new-target ID collision in {p['id']}: {sorted(collision)}")
        staged_target_ids |= new_ids
        staged.append(p)

    combined = rows + staged
    if len(combined) != 36 or [r.get("sequence") for r in combined] != list(range(1, 37)):
        raise SystemExit("post-promotion sequence continuity failed")
    if any(len(r.get("questions", [])) != 10 or len(r.get("answer_key", [])) != 10 for r in combined):
        raise SystemExit("post-promotion 10Q/10A regression")

    CANON.write_text("\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in combined) + "\n", encoding="utf-8")
    after_sha256 = sha256(CANON)
    out = {
        "schema_version": 1,
        "date": "2026-08-20",
        "language": "ur",
        "level": "A1",
        "unit": 6,
        "status": "GUARDED_PROMOTION_APPLIED_NEEDS_REVIEW",
        "before_git_blob": canon_blob,
        "before_sha256": before_sha256,
        "after_sha256": after_sha256,
        "staged_git_blobs": staged_blob_evidence,
        "canonical_passages_after": 36,
        "canonical_questions_after": 360,
        "canonical_answers_after": 360,
        "promoted_sequences": [31, 32, 33, 34, 35, 36],
        "promoted_passages": 6,
        "promoted_questions": 60,
        "promoted_answers": 60,
        "new_target_ids_added": sorted(staged_target_ids),
        "source_lexicon_mutated": False,
        "checks": {
            "frontier_blob_exact": True,
            "staging_blobs_exact": True,
            "sequences_contiguous": True,
            "a1_word_band_90_140": True,
            "ten_questions_and_answers": True,
            "answer_linkage": True,
            "question_targets_locally_declared": True,
            "new_targets_visible": True,
            "running_text_reviews_visible": True,
            "new_target_id_collisions": 0,
            "p06_zero_new_targets": True,
            "learner_facing_roman_script_zero": True,
        },
        "formal_final_audit": "deferred under generation-first policy",
        "next_generation_frontier": "Urdu A1 Unit 07 sequences 37-42, already staged but must be reverified against this promoted canonical hash before promotion.",
        "release_effect": "Generation progress only; Urdu remains non-release-ready."
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": out["status"], "canonical_passages_after": 36, "after_sha256": after_sha256}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
