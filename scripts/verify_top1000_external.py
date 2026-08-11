#!/usr/bin/env python3
"""Cross-check learner Top-1000 decks against independent lexical resources.

This verifier is deliberately conservative. It does NOT rewrite learner cards.
It records whether the published form and learner-facing English meaning receive
support from external resources, and emits a review queue where support is weak
or semantic wording does not overlap the independent dictionary glosses.

Sources:
- WiktAPI (structured English-Wiktionary / target-Wiktionary data)
- wordfreq (multi-corpus attestation only; not a semantic authority)
- Arabic WordNet 4.0 lexical coverage when --arabic-wordnet is supplied
- Existing CALIMA learner-safety audit coverage for Arabic when present
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    from wordfreq import zipf_frequency
except Exception:  # pragma: no cover
    zipf_frequency = None

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
AUDIT.mkdir(exist_ok=True)

LANGS = {
    "arabic": {"code": "ar", "edition": "ar"},
    "french": {"code": "fr", "edition": "fr"},
    "urdu": {"code": "ur", "edition": "ur"},
}

STOP = {
    "a","an","the","to","of","in","on","at","for","from","by","with","and","or","as","is","are","was","were","be","been","being",
    "used","use","word","term","one","that","this","which","who","whom","something","someone","often","usually","especially","indicating",
    "expressing","referring","form","forms","particle","pronoun","noun","verb","adjective","adverb","preposition","conjunction","marker",
    "masculine","feminine","singular","plural","present","past","future","case","person","thing","things","meaning","means"
}
TOKEN_RE = re.compile(r"[a-z][a-z'-]*", re.I)


def norm_unicode(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").replace("ـ", "")
    return s.strip()


def english_evidence(back: str) -> str:
    m = re.search(r"(?m)^Meaning:\s*(.+?)\s*$", back or "")
    if m:
        return m.group(1).strip()
    parts = []
    m = re.search(r"(?m)^EN:\s*(.+?)\s*$", back or "")
    if m:
        parts.append(m.group(1).strip())
    m = re.search(r"(?s)Definition:\s*\n\(EN\)\s*(.+?)(?:\n\n|$)", back or "")
    if m:
        parts.append(m.group(1).strip())
    return "; ".join(parts)


def token_set(text: str) -> set[str]:
    out = set()
    for t in TOKEN_RE.findall((text or "").lower()):
        t = t.strip("'-")
        if not t or t in STOP or len(t) < 2:
            continue
        # light English normalization solely for overlap detection
        for suffix in ("ing", "ed", "es", "s"):
            if len(t) > len(suffix) + 3 and t.endswith(suffix):
                t = t[:-len(suffix)]
                break
        out.add(t)
    return out


def wikt_fetch(word: str, code: str, edition: str = "en", retries: int = 2) -> dict:
    url = f"https://api.wiktapi.dev/v1/{edition}/word/{urllib.parse.quote(word, safe='')}?lang={code}"
    req = urllib.request.Request(url, headers={"User-Agent": "ualispublishing-learning-verifier/1.0"})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):
                return {"entries": [], "_http": e.code}
            if e.code == 429 and attempt < retries:
                time.sleep(1.5 * (attempt + 1)); continue
            return {"entries": [], "_http": e.code, "_error": str(e)}
        except Exception as e:
            if attempt < retries:
                time.sleep(0.7 * (attempt + 1)); continue
            return {"entries": [], "_error": str(e)}
    return {"entries": []}


def summarize_wikt(payload: dict) -> tuple[bool, set[str], set[str]]:
    entries = payload.get("entries") or []
    gloss_tokens: set[str] = set()
    poses: set[str] = set()
    for ent in entries:
        if ent.get("pos"):
            poses.add(str(ent["pos"]).lower())
        for sense in ent.get("senses") or []:
            for gloss in sense.get("glosses") or []:
                gloss_tokens |= token_set(str(gloss))
    return bool(entries), gloss_tokens, poses


def load_arabic_wordnet(path: Path | None) -> set[str]:
    if not path or not path.exists():
        return set()
    opener = gzip.open if path.suffix == ".gz" else open
    lemmas: set[str] = set()
    with opener(path, "rb") as f:
        for _, elem in ET.iterparse(f, events=("end",)):
            if elem.tag.rsplit("}", 1)[-1] == "Lemma":
                wf = elem.attrib.get("writtenForm") or elem.attrib.get("lemma")
                if wf:
                    lemmas.add(norm_unicode(wf))
            elem.clear()
    return lemmas


def load_camel_support() -> set[str]:
    path = AUDIT / "arabic_top1000_learner_safety_audit.csv"
    if not path.exists():
        return set()
    out = set()
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            try:
                if int(row.get("camel_analysis_count", "0") or 0) > 0:
                    out.add(norm_unicode(row.get("front", "")))
            except ValueError:
                pass
    return out


def verify_one(rank: int, front: str, expected: str, code: str, edition: str, awn: set[str], camel: set[str]) -> dict:
    en = wikt_fetch(front, code, "en")
    target = wikt_fetch(front, code, edition) if edition != "en" else en
    en_exists, gloss_tokens, en_pos = summarize_wikt(en)
    target_exists, _, target_pos = summarize_wikt(target)
    expected_tokens = token_set(expected)
    overlap = sorted(expected_tokens & gloss_tokens)
    semantic = bool(overlap)
    # For very short function-word meanings, exact substring is a useful additional signal.
    if not semantic and expected and en_exists:
        compact = expected.lower().strip()
        for tok in expected_tokens:
            if tok in gloss_tokens:
                semantic = True; break
    freq_present = False
    if zipf_frequency is not None:
        try:
            freq_present = zipf_frequency(front, code) > 0.0
        except Exception:
            freq_present = False
    awn_present = front in awn if awn else False
    camel_present = front in camel if camel else False

    support_count = sum([en_exists, target_exists, freq_present, awn_present, camel_present])
    if semantic and support_count >= 2:
        confidence = "strong"
    elif semantic:
        confidence = "moderate"
    elif en_exists and gloss_tokens:
        confidence = "semantic_review"
    elif support_count >= 2:
        confidence = "form_only"
    else:
        confidence = "weak"

    return {
        "rank": rank,
        "front": front,
        "expected_english": expected,
        "wikt_en_entry": en_exists,
        "wikt_target_entry": target_exists,
        "wordfreq_attested": freq_present,
        "arabic_wordnet_entry": awn_present,
        "camel_analysis": camel_present,
        "semantic_overlap": semantic,
        "semantic_overlap_terms": "|".join(overlap[:12]),
        "wikt_pos": "|".join(sorted(en_pos)),
        "target_wikt_pos": "|".join(sorted(target_pos)),
        "support_count": support_count,
        "confidence": confidence,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--language", choices=sorted(LANGS), required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--arabic-wordnet")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()

    cfg = LANGS[args.language]
    input_path = ROOT / args.input
    with input_path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1000 or not rows or list(rows[0]) != ["Front", "Back"]:
        raise SystemExit(f"{args.input}: expected exactly 1000 Front,Back rows")

    awn = load_arabic_wordnet(Path(args.arabic_wordnet)) if args.language == "arabic" and args.arabic_wordnet else set()
    camel = load_camel_support() if args.language == "arabic" else set()

    tasks = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for rank, row in enumerate(rows, 1):
            front = norm_unicode(row["Front"])
            expected = english_evidence(row["Back"])
            tasks.append(pool.submit(verify_one, rank, front, expected, cfg["code"], cfg["edition"], awn, camel))
        results = [f.result() for f in as_completed(tasks)]
    results.sort(key=lambda r: r["rank"])

    out_csv = AUDIT / f"{args.language}_top1000_external_verification.csv"
    fields = list(results[0])
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(results)

    review = [r for r in results if r["confidence"] in {"semantic_review", "form_only", "weak"}]
    review_csv = AUDIT / f"{args.language}_top1000_external_review_queue.csv"
    with review_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(review)

    counts = {}
    for r in results:
        counts[r["confidence"]] = counts.get(r["confidence"], 0) + 1
    summary = {
        "language": args.language,
        "input": args.input,
        "rows": len(results),
        "confidence_counts": counts,
        "wikt_en_coverage": sum(r["wikt_en_entry"] for r in results),
        "target_wiktionary_coverage": sum(r["wikt_target_entry"] for r in results),
        "wordfreq_attested": sum(r["wordfreq_attested"] for r in results),
        "arabic_wordnet_coverage": sum(r["arabic_wordnet_entry"] for r in results),
        "camel_analysis_coverage": sum(r["camel_analysis"] for r in results),
        "semantic_overlap_rows": sum(r["semantic_overlap"] for r in results),
        "review_queue_rows": len(review),
        "policy": [
            "No external source silently rewrites learner cards.",
            "Wiktionary semantic overlap is a verification signal, not an oracle.",
            "wordfreq is used only as independent corpus attestation, not for meaning.",
            "Missing coverage is not treated as proof that a learner entry is wrong.",
            "Rows with weak or non-overlapping semantic support are queued for explicit review."
        ]
    }
    (AUDIT / f"{args.language}_top1000_external_verification_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
