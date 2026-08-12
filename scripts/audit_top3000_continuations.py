#!/usr/bin/env python3
"""Independent structural/semantic triage for rank 1001-3000 candidates.

Review rows are committed for explicit resolution; they do not silently pass or
silently rewrite cards. Structural defects are blocking failures.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

from wordfreq import zipf_frequency

import build_french_urdu_core_candidates_v2 as fu
import build_arabic_top1000_precision as arprec

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
MEANING_RE = re.compile(r"(?m)^Meaning:\s*(.+?)\s*$")
RANK_RE = re.compile(r"(?m)^Rank:\s*(\d+)\s*$")
WORD_RE = re.compile(r"[a-z]+(?:'[a-z]+)?", re.I)
PLACEHOLDER_RE = re.compile(r"^(?:arabic|french|urdu)_word_\d+$", re.I)
STOP = {"a","an","the","to","of","and","or","for","as","be","is","are","was","were","with","by","from","that","which","who","this","it","he","she","they","you","i","we","one"}
LANG_CODE = {"arabic": "ar", "french": "fr", "urdu": "ur"}


def toks(text: str) -> set[str]:
    out = {x.lower() for x in WORD_RE.findall(text or "") if x.lower() not in STOP}
    expanded = set(out)
    for x in list(out):
        if len(x) > 4 and x.endswith("ies"): expanded.add(x[:-3] + "y")
        if len(x) > 4 and x.endswith("es"): expanded.add(x[:-2])
        if len(x) > 3 and x.endswith("s"): expanded.add(x[:-1])
        if len(x) > 5 and x.endswith("ing"): expanded.add(x[:-3])
        if len(x) > 4 and x.endswith("ed"): expanded.add(x[:-2])
    return expanded


def sem_overlap(a: str, b: str) -> tuple[bool, str]:
    aa, bb = toks(a), toks(b)
    hits = sorted(aa & bb)
    return bool(hits), ",".join(hits[:10])


def read_candidate(language: str):
    p = AUDIT / f"{language}_top3000_candidate.csv"
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_evidence(language: str):
    p = AUDIT / f"{language}_top3000_continuation_evidence.csv"
    with p.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_top1000(language: str):
    p = ROOT / f"{language}_top1000.csv"
    normalizer = fu.norm_fr if language == "french" else fu.norm_ur if language == "urdu" else arprec.undiac
    with p.open(encoding="utf-8-sig", newline="") as f:
        return {normalizer((r.get("Front") or "").strip()) for r in csv.DictReader(f)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--language", choices=["arabic","french","urdu"], required=True)
    ap.add_argument("--kaikki", required=True)
    args = ap.parse_args()
    language = args.language
    rows = read_candidate(language)
    evidence = read_evidence(language)
    if len(rows) != len(evidence):
        raise SystemExit(f"{language}: candidate/evidence row mismatch {len(rows)} vs {len(evidence)}")

    normalizer = fu.norm_fr if language == "french" else fu.norm_ur if language == "urdu" else arprec.undiac
    kaikki = fu.load_kaikki(Path(args.kaikki), normalizer)
    top1000 = read_top1000(language)
    problems = []
    details = []
    counts = Counter()
    seen = set()

    for idx, (card, ev) in enumerate(zip(rows, evidence), start=1001):
        front_raw = (card.get("Front") or "").strip()
        front = normalizer(front_raw)
        back = card.get("Back") or ""
        rm = RANK_RE.search(back)
        mm = MEANING_RE.search(back)
        meaning = mm.group(1).strip() if mm else ""
        row_flags = []
        if not front: row_flags.append("blank_front")
        if PLACEHOLDER_RE.fullmatch(front_raw): row_flags.append("placeholder_front")
        if rm is None or int(rm.group(1)) != idx: row_flags.append("rank_mismatch")
        if not meaning: row_flags.append("missing_meaning")
        if front in top1000: row_flags.append("overlaps_live_top1000")
        if front in seen: row_flags.append("duplicate_continuation_front")
        seen.add(front)

        corpus = zipf_frequency(front_raw, LANG_CODE[language])
        corpus_ok = corpus > 0
        k = kaikki.get(front)
        kmeaning = fu.compact_meaning(k.get("all_glosses", [])) if k else ""
        ksem, khits = sem_overlap(meaning, kmeaning) if kmeaning else (False, "")

        if language == "french":
            # Lexique + Kaikki were required at construction; semantic overlap is an
            # independent post-build check on the final learner gloss.
            status = "verified_strong" if corpus_ok and ksem else "explicit_review_required"
        elif language == "urdu":
            rmeaning = ev.get("readurdu_meaning", "")
            rsem, rhits = sem_overlap(meaning, rmeaning) if rmeaning else (False, "")
            external_sem_sources = int(ksem) + int(rsem)
            lexical_support = ev.get("cle_wordnet") == "True" or ev.get("cle_closed_class") == "True"
            if corpus_ok and external_sem_sources >= 2:
                status = "verified_strong"
            elif corpus_ok and external_sem_sources == 1 and lexical_support:
                status = "verified"
            else:
                status = "explicit_review_required"
        else:
            exact_calima = int(ev.get("calima_exact_analyses") or 0) > 0
            if corpus_ok and exact_calima and ksem:
                status = "verified_strong"
            elif corpus_ok and exact_calima:
                status = "verified_morphology_review_semantics"
            else:
                status = "explicit_review_required"

        if row_flags:
            status = "blocking_structural_problem"
            problems.append(f"rank {idx} {front_raw}: {'|'.join(row_flags)}")
        counts[status] += 1
        details.append({
            "rank": idx, "front": front_raw, "meaning": meaning, "status": status,
            "wordfreq_zipf": f"{corpus:.3f}", "kaikki_entry": bool(k),
            "kaikki_semantic_support": ksem, "kaikki_overlap_terms": khits,
            "readurdu_entry": ev.get("readurdu_entry", ""),
            "readurdu_semantic_support": (sem_overlap(meaning, ev.get("readurdu_meaning", ""))[0] if language == "urdu" and ev.get("readurdu_meaning") else ""),
            "calima_exact_analyses": ev.get("calima_exact_analyses", ""),
            "flags": "|".join(row_flags),
        })

    if len(rows) != 2000: problems.append(f"row_count={len(rows)} expected=2000")
    if len(seen) != 2000: problems.append(f"distinct_fronts={len(seen)} expected=2000")
    if rows and ((RANK_RE.search(rows[0].get('Back','') or '') or [None, None])[1] != '1001'):
        problems.append("first_rank_not_1001")

    detail_path = AUDIT / f"{language}_top3000_audit.csv"
    with detail_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(details[0]) if details else ["rank","front","meaning","status"])
        w.writeheader(); w.writerows(details)
    review = [d for d in details if d["status"] in {"explicit_review_required","verified_morphology_review_semantics"}]
    review_path = AUDIT / f"{language}_top3000_review_queue.csv"
    with review_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(details[0]) if details else ["rank","front","meaning","status"])
        w.writeheader(); w.writerows(review)
    summary = {
        "language": language, "rows": len(rows), "rank_range": [1001,3000],
        "distinct_fronts": len(seen), "top1000_overlap_rows": sum("overlaps_live_top1000" in d["flags"] for d in details),
        "placeholder_rows": sum("placeholder_front" in d["flags"] for d in details),
        "status_counts": dict(sorted(counts.items())), "review_rows": len(review),
        "blocking_problems": len(problems), "problems": problems[:50],
        "promotion_gate": "PASS" if not problems and not review and len(rows) == 2000 else "REVIEW_REQUIRED",
        "policy": "Never auto-promote weak semantic rows; frequency/morphology attestation is not treated as semantic proof.",
    }
    (AUDIT / f"{language}_top3000_audit_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if problems:
        raise SystemExit(f"{language}: structural audit failed")


if __name__ == "__main__":
    main()
