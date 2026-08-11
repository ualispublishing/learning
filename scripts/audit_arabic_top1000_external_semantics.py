#!/usr/bin/env python3
"""Independent semantic verification for the promoted Arabic Top-1000 deck.

Signals:
- Kaikki/Wiktextract English-Wiktionary senses
- Arabic WordNet (OMW `omw-arb:2.0`) translated through the shared English synsets
- wordfreq corpus attestation
- existing CALIMA morphology coverage

This audit does not rewrite cards. It uses function-word-aware sense comparison so
short meanings such as `in`, `from`, `and`, `to be`, etc. are not discarded as
English stopwords. Rows lacking direct independent semantic agreement remain
explicit-review rows rather than being guessed.
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

import wn
from wordfreq import zipf_frequency

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
TARGET = ROOT / "arabic_top1000.csv"
KAikki = AUDIT / "arabic_top1000_external_verification.csv"
CALIMA = AUDIT / "arabic_top1000_learner_safety_audit.csv"

AR_DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*", re.I)
SPLIT_RE = re.compile(r"\s*(?:;|/|\||,(?!\s*(?:which|who|that|when|where)))\s*")
CONTENT_STOP = {
    "a","an","the","to","of","in","on","at","for","from","by","with","and","or","as","is","are","was","were","be","been","being",
    "one","that","this","which","who","whom","something","someone","used","use","form","forms","person","thing","things","depending","context",
    "masculine","feminine","singular","plural","present","past","future","particle","pronoun","noun","verb","adjective","adverb","preposition","conjunction",
}


def norm_ar(s: str) -> str:
    return AR_DIAC.sub("", unicodedata.normalize("NFKC", s or "").replace("ـ", "")).strip()


def meaning(back: str) -> str:
    m = re.search(r"(?m)^Meaning:\s*(.+?)\s*$", back or "")
    return m.group(1).strip() if m else ""


def raw_tokens(text: str) -> list[str]:
    return [t.strip("'-").lower() for t in WORD_RE.findall(text or "") if t.strip("'-")]


def content_tokens(text: str) -> set[str]:
    out = set()
    for t in raw_tokens(text):
        if t in CONTENT_STOP:
            continue
        if len(t) > 5 and t.endswith("ies"):
            t = t[:-3] + "y"
        else:
            for suf in ("ingly", "ation", "ments", "ment", "ing", "ied", "ed", "es", "s"):
                if len(t) > len(suf) + 3 and t.endswith(suf):
                    t = t[:-len(suf)]
                    break
        if len(t) >= 2 and t not in CONTENT_STOP:
            out.add(t)
    return out


def canonical_senses(text: str) -> set[str]:
    senses = set()
    for part in SPLIT_RE.split(text or ""):
        toks = raw_tokens(part)
        if len(toks) > 1 and toks[0] in {"a", "an", "the"}:
            toks = toks[1:]
        if toks and toks[0] == "to" and len(toks) == 2:
            toks = toks[1:]
        if toks and len(toks) <= 5:
            senses.add(" ".join(toks))
    return senses


def agrees(a: str, b: str) -> tuple[bool, str]:
    overlap = sorted(content_tokens(a) & content_tokens(b))
    if overlap:
        return True, "|".join(overlap[:12])
    s = sorted(canonical_senses(a) & canonical_senses(b))
    if s:
        return True, "|".join(s[:12])
    # Permit exact single semantic atoms (including function words) only when they
    # are complete short senses, not incidental words inside long definitions.
    aa = {x for x in canonical_senses(a) if len(x.split()) == 1}
    bb = {x for x in canonical_senses(b) if len(x.split()) == 1}
    atom = sorted(aa & bb)
    return (bool(atom), "|".join(atom[:12]))


def load_kaikki_evidence() -> dict[str, str]:
    # The external verifier stores only overlap tokens, not raw glosses. Reconstructing
    # raw gloss evidence is handled directly from OMW here; Kaikki agreement from the
    # external verifier is retained as an independent boolean signal.
    if not KAikki.exists():
        return {}
    out = {}
    with KAikki.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            out[norm_ar(r.get("front", ""))] = r.get("semantic_overlap", "").strip().lower() == "true"
    return out


def load_calima() -> set[str]:
    if not CALIMA.exists():
        return set()
    out = set()
    with CALIMA.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            try:
                if int(r.get("camel_analysis_count", "0") or 0) > 0:
                    out.add(norm_ar(r.get("front", "")))
            except ValueError:
                pass
    return out


def omw_evidence(front: str, ar_wn, en_wn) -> str:
    values = []
    # Exact lemma first. OMW Arabic WordNet also exposes alternative forms in the
    # current release, so Wn may resolve some orthographic variants automatically.
    try:
        synsets = ar_wn.synsets(front)
    except Exception:
        synsets = []
    for ss in synsets:
        translated = []
        for lex_id in ("omw-en:2.0",):
            try:
                translated.extend(ss.translate(lexicon=lex_id))
            except Exception:
                pass
        for ens in translated:
            try:
                values.extend(ens.lemmas())
                d = ens.definition()
                if d:
                    values.append(d)
            except Exception:
                pass
    return "; ".join(dict.fromkeys(values))[:5000]


def main() -> None:
    with TARGET.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1000:
        raise SystemExit(f"Expected 1000 Arabic rows, found {len(rows)}")

    ar_wn = wn.Wordnet("omw-arb:2.0")
    en_wn = wn.Wordnet("omw-en:2.0")
    kaikki_agreement = load_kaikki_evidence()
    calima = load_calima()

    results = []
    for rank, row in enumerate(rows, 1):
        front = norm_ar(row.get("Front", ""))
        m = meaning(row.get("Back", ""))
        omw = omw_evidence(front, ar_wn, en_wn)
        omw_ok, terms = agrees(m, omw) if omw else (False, "")
        kaikki_ok = kaikki_agreement.get(front, False)
        corpus = zipf_frequency(front, "ar") > 0
        morph = front in calima

        semantic_sources = int(kaikki_ok) + int(omw_ok)
        if semantic_sources >= 2:
            status = "verified_strong"
        elif semantic_sources == 1 and (corpus or morph):
            status = "verified"
        else:
            status = "explicit_review_required"

        results.append({
            "rank": rank,
            "front": front,
            "meaning": m,
            "kaikki_semantic_agreement": kaikki_ok,
            "omw_semantic_agreement": omw_ok,
            "omw_overlap_terms": terms,
            "wordfreq_attested": corpus,
            "calima_analysis": morph,
            "status": status,
        })

    fields = list(results[0])
    with (AUDIT / "arabic_top1000_external_semantic_audit.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(results)
    review = [r for r in results if r["status"] == "explicit_review_required"]
    with (AUDIT / "arabic_top1000_external_semantic_review_queue.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(review)

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    summary = {
        "rows": len(results),
        "status_counts": counts,
        "kaikki_semantic_agreement": sum(r["kaikki_semantic_agreement"] for r in results),
        "omw_semantic_agreement": sum(r["omw_semantic_agreement"] for r in results),
        "wordfreq_attested": sum(r["wordfreq_attested"] for r in results),
        "calima_analysis": sum(r["calima_analysis"] for r in results),
        "explicit_review_rows": len(review),
        "policy": "Rows without independent semantic agreement remain explicit-review items; no guessed correction is made.",
    }
    (AUDIT / "arabic_top1000_external_semantic_audit_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
