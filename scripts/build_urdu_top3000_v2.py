#!/usr/bin/env python3
"""Build Urdu ranks 1001-3000 from the CLE frequency list with safe semantics.

The CLE 5,000-word corpus list is the ranking/form authority. A continuation row
must also have at least one independent learner-semantic source (ReadUrdu or
Kaikki); CLE WordNet/closed-class membership and agreement between semantic
sources are preserved as audit signals rather than being required at build time.
No weak row is auto-promoted: the independent audit decides the review queue.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import build_french_urdu_core_candidates_v2 as fu
import refine_french_urdu_candidate_meanings_v4 as v4

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
TARGET = 2000


def clean(text: str) -> str:
    return " ".join((text or "").replace("_", " ").split()).strip(" ;.")


def good(text: str) -> bool:
    x = clean(text)
    return bool(x) and len(x) <= 320 and not any(ch in x for ch in "[]<>") and "+" not in x


def live_fronts() -> set[str]:
    with (ROOT / "urdu_top1000.csv").open(encoding="utf-8-sig", newline="") as f:
        return {fu.norm_ur((r.get("Front") or "").strip()) for r in csv.DictReader(f)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kaikki", required=True)
    ap.add_argument("--urdu-freq-text", required=True)
    ap.add_argument("--urdu-wordnet-text", required=True)
    ap.add_argument("--urdu-closed-text", required=True)
    ap.add_argument("--readurdu", required=True)
    args = ap.parse_args()

    excluded = live_fronts()
    freq_text = Path(args.urdu_freq_text).read_text(encoding="utf-8", errors="replace")
    wn_text = fu.norm_ur(Path(args.urdu_wordnet_text).read_text(encoding="utf-8", errors="replace"))
    closed_text = fu.norm_ur(Path(args.urdu_closed_text).read_text(encoding="utf-8", errors="replace"))
    ranked = fu.extract_urdu_freq(freq_text)
    readurdu = fu.read_readurdu(Path(args.readurdu))
    kaikki = fu.load_kaikki(Path(args.kaikki), fu.norm_ur)
    curated = v4.v3.v2.base.URDU_SAFE

    rows, rejected = [], []
    for word, freq in ranked:
        if word in excluded:
            continue
        in_wn = fu.inventory_contains(wn_text, word)
        in_closed = fu.inventory_contains(closed_text, word)
        has_read = word in readurdu
        has_k = word in kaikki
        if not (has_read or has_k):
            rejected.append({"front": word, "frequency": freq, "reason": "no_independent_semantic_source"})
            continue
        rmeaning = clean(readurdu.get(word, {}).get("meaning", "")) if has_read else ""
        kmeaning = fu.compact_meaning(kaikki.get(word, {}).get("all_glosses", [])) if has_k else ""
        meaning = clean(curated.get(word) or rmeaning or kmeaning)
        if not good(meaning):
            rejected.append({"front": word, "frequency": freq, "reason": "no_safe_learner_meaning"})
            continue
        rows.append({
            "rank": 1001 + len(rows),
            "front": word,
            "meaning": meaning,
            "pos": "|".join(sorted(kaikki.get(word, {}).get("poses", set()))) or ("closed-class" if in_closed else "content word"),
            "frequency": freq,
            "cle_wordnet": in_wn,
            "cle_closed_class": in_closed,
            "readurdu_entry": has_read,
            "readurdu_meaning": rmeaning,
            "kaikki_entry": has_k,
            "kaikki_meaning": kmeaning,
            "source": "CLE Urdu 5,000 corpus frequency list; ReadUrdu/Kaikki learner semantics; CLE lexical inventories as support signals",
        })
        if len(rows) >= TARGET:
            break

    ev = AUDIT / "urdu_top3000_continuation_evidence.csv"
    with ev.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["rank","front","meaning"])
        w.writeheader(); w.writerows(rows)

    cand = AUDIT / "urdu_top3000_candidate.csv"
    with cand.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Front", "Back"]); w.writeheader()
        for r in rows:
            back = "\n".join([
                f"Rank: {r['rank']}", "", f"Meaning: {r['meaning']}", "",
                f"Part of speech: {r['pos']}", "", f"Frequency evidence: {r['frequency']}", "", "Sources:",
                "- CLE Urdu 5,000 corpus frequency list — ranking/form authority",
                "- ReadUrdu and/or Kaikki/Wiktextract — learner-semantic evidence",
                "- CLE WordNet/closed-class lists — independent lexical-support signals where available",
                "- Continuation candidate; requires independent verification before promotion",
            ])
            w.writerow({"Front": r["front"], "Back": back})

    with (AUDIT / "urdu_top3000_rejections.csv").open("w", encoding="utf-8", newline="") as f:
        fields = list(rejected[0]) if rejected else ["front","frequency","reason"]
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rejected)

    summary = {
        "language": "urdu", "continuation_rows": len(rows), "expected_rows": TARGET,
        "start_rank": 1001, "end_rank": 3000, "distinct_fronts": len({r['front'] for r in rows}),
        "meaning_rows": sum(bool(r['meaning']) for r in rows), "rejected_rows": len(rejected),
        "rows_with_readurdu": sum(r['readurdu_entry'] for r in rows),
        "rows_with_kaikki": sum(r['kaikki_entry'] for r in rows),
        "rows_with_both_semantic_sources": sum(r['readurdu_entry'] and r['kaikki_entry'] for r in rows),
        "structural_gate": "PASS" if len(rows)==TARGET and len({r['front'] for r in rows})==TARGET else "FAIL",
        "status": "candidate_only_not_promoted",
    }
    (AUDIT / "urdu_top3000_candidate_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary["structural_gate"] != "PASS":
        raise SystemExit("Unable to build 2,000 supported Urdu continuation rows")


if __name__ == "__main__":
    main()
