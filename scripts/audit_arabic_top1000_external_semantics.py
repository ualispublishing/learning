#!/usr/bin/env python3
"""Independent semantic verification for the promoted Arabic Top-1000 deck.

Signals:
- Kaikki/Wiktextract English-Wiktionary senses
- Arabic WordNet (OMW `omw-arb:2.0`) translated through shared English synsets
- wordfreq corpus attestation
- existing CALIMA morphology coverage

This audit never rewrites cards. It uses function-word-aware sense comparison so
short meanings such as `in`, `from`, `and`, `to be`, etc. are not discarded as
English stopwords. Rows without direct semantic agreement stay explicit-review
items rather than receiving guessed corrections.
"""
from __future__ import annotations

import argparse
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


def learner_meaning(back: str) -> str:
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
    exact = sorted(canonical_senses(a) & canonical_senses(b))
    if exact:
        return True, "|".join(exact[:12])
    aa = {x for x in canonical_senses(a) if len(x.split()) == 1}
    bb = {x for x in canonical_senses(b) if len(x.split()) == 1}
    atoms = sorted(aa & bb)
    return bool(atoms), "|".join(atoms[:12])


def load_kaikki(path: Path, targets: set[str]) -> dict[str, str]:
    values: dict[str, list[str]] = {t: [] for t in targets}
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except Exception:
                continue
            word = norm_ar(str(obj.get("word", "")))
            if word not in targets:
                continue
            for sense in obj.get("senses") or []:
                for gloss in sense.get("glosses") or []:
                    g = re.sub(r"\s+", " ", str(gloss or "")).strip()
                    if g and g not in values[word]:
                        values[word].append(g)
    return {w: "; ".join(gs)[:7000] for w, gs in values.items() if gs}


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


def omw_evidence(front: str, ar_wn) -> str:
    values = []
    try:
        synsets = ar_wn.synsets(front)
    except Exception:
        synsets = []
    for ss in synsets:
        try:
            translated = ss.translate(lexicon="omw-en:2.0")
        except Exception:
            translated = []
        for ens in translated:
            try:
                values.extend(ens.lemmas())
                definition = ens.definition()
                if definition:
                    values.append(definition)
            except Exception:
                pass
    return "; ".join(dict.fromkeys(values))[:7000]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kaikki-jsonl", required=True)
    args = ap.parse_args()

    with TARGET.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1000:
        raise SystemExit(f"Expected 1000 Arabic rows, found {len(rows)}")

    fronts = [norm_ar(r.get("Front", "")) for r in rows]
    kaikki = load_kaikki(Path(args.kaikki_jsonl), set(fronts))
    calima = load_calima()
    ar_wn = wn.Wordnet("omw-arb:2.0")

    results = []
    for rank, row in enumerate(rows, 1):
        front = fronts[rank - 1]
        meaning = learner_meaning(row.get("Back", ""))
        kg = kaikki.get(front, "")
        ow = omw_evidence(front, ar_wn)
        kaikki_ok, kterms = agrees(meaning, kg) if kg else (False, "")
        omw_ok, oterms = agrees(meaning, ow) if ow else (False, "")
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
            "meaning": meaning,
            "kaikki_entry": bool(kg),
            "kaikki_semantic_agreement": kaikki_ok,
            "kaikki_overlap_terms": kterms,
            "omw_entry": bool(ow),
            "omw_semantic_agreement": omw_ok,
            "omw_overlap_terms": oterms,
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
        "kaikki_entry_coverage": sum(r["kaikki_entry"] for r in results),
        "kaikki_semantic_agreement": sum(r["kaikki_semantic_agreement"] for r in results),
        "omw_entry_coverage": sum(r["omw_entry"] for r in results),
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
