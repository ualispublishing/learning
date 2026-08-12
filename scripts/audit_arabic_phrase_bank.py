#!/usr/bin/env python3
"""Deep learner-safety audit for arabic_phrase_bank.csv.

Checks all 1,405 cards for schema completeness, normalized duplicate fronts,
mixed-script/overlong phrase fronts, parseable EN/FR/UR translations, examples,
English example translations, machine artifacts, likely dialect-only main fronts,
and token-level CALIMA-MSA morphology coverage for both the front and example.
The audit never rewrites the phrase bank; suspicious rows are emitted to an
explicit review queue.
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "arabic_phrase_bank.csv"
AUDIT = ROOT / "audit"
AUDIT.mkdir(exist_ok=True)

DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
AR_WORD = re.compile(r"[\u0621-\u064a]+")
LATIN = re.compile(r"[A-Za-z]")
ARABIC = re.compile(r"[\u0600-\u06FF]")
EN_RE = re.compile(r"(?m)^EN:\s*(.+?)\s*$")
FR_RE = re.compile(r"(?m)^FR:\s*(.+?)\s*$")
UR_RE = re.compile(r"(?m)^UR:\s*(.+?)\s*$")
DEF_RE = re.compile(r"(?ms)^Definition:\s*\n\(EN\)\s*(.+?)(?=\n\n(?:Example:|Translation:|Root:|Related / near-equivalents:)|\Z)")
EXAMPLE_RE = re.compile(r"(?m)^Example:\s*(.+?)\s*$")
EXTRANS_RE = re.compile(r"(?m)^Translation:\s*(.+?)\s*$")
ROOT_RE = re.compile(r"(?m)^Root:\s*(.+?)\s*$")
RELATED_RE = re.compile(r"(?m)^Related / near-equivalents:\s*(.+?)\s*$")
MACHINE = re.compile(r"(?:TODO|TBD|placeholder|arabic[_ -]?phrase[_ -]?\d+|\[def\.|\[indef\.|<verb>|\+he;it|it;they;she\+)", re.I)
DIALECT_MAIN = re.compile(r"(?:^|\s)(?:عايز|عاوز|إزاي|ازاي|شو|مو|ليش|معليش|معلش|شلون|وين|إيش|ايش|لسه|لسا)(?:\s|$)")
PUNCT_STRIP = re.compile(r"[^\u0621-\u064a\s]")


def undiac(text: str) -> str:
    return DIAC.sub("", unicodedata.normalize("NFKC", text or "").replace("ـ", "")).strip()


def norm_front(text: str) -> str:
    x = undiac(text)
    x = PUNCT_STRIP.sub(" ", x)
    return re.sub(r"\s+", " ", x).strip()


def extract(regex, text: str) -> str:
    m = regex.search(text or "")
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def arabic_words(text: str) -> list[str]:
    return AR_WORD.findall(undiac(text))


def morphology(words: list[str], analyzer) -> tuple[int, list[str]]:
    bad = []
    for w in words:
        if not analyzer.analyze(w):
            bad.append(w)
    return len(words) - len(bad), bad


def main() -> None:
    from camel_tools.morphology.analyzer import Analyzer
    from camel_tools.morphology.database import MorphologyDB

    analyzer = Analyzer(MorphologyDB.builtin_db("calima-msa-r13", flags="a"), backoff="NONE", cache_size=30000)
    with TARGET.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    normalized_groups = defaultdict(list)
    for i, row in enumerate(rows, 1):
        normalized_groups[norm_front(row.get("Front", ""))].append(i)
    duplicate_norm = {k: v for k, v in normalized_groups.items() if k and len(v) > 1}

    details = []
    counts = Counter()
    for rank, row in enumerate(rows, 1):
        front = (row.get("Front") or "").strip()
        back = row.get("Back") or ""
        en = extract(EN_RE, back)
        fr = extract(FR_RE, back)
        ur = extract(UR_RE, back)
        definition = extract(DEF_RE, back)
        example = extract(EXAMPLE_RE, back)
        example_en = extract(EXTRANS_RE, back)
        root = extract(ROOT_RE, back)
        related = extract(RELATED_RE, back)
        norm = norm_front(front)
        flags = []

        if not front: flags.append("blank_front")
        if not back.strip(): flags.append("blank_back")
        if "\n" in front or "\r" in front: flags.append("multiline_front")
        if len(front) > 180: flags.append("overlong_front")
        if len(arabic_words(front)) > 18: flags.append("too_many_front_tokens")
        if LATIN.search(front): flags.append("latin_in_front")
        if not ARABIC.search(front): flags.append("no_arabic_in_front")
        if norm in duplicate_norm: flags.append("normalized_duplicate_front")
        if DIALECT_MAIN.search(undiac(front)): flags.append("likely_dialect_main_front")
        if MACHINE.search(front) or MACHINE.search(back): flags.append("machine_artifact")

        if not en: flags.append("missing_en")
        if not fr: flags.append("missing_fr")
        if not ur: flags.append("missing_ur")
        if not definition: flags.append("missing_definition_en")
        if not example: flags.append("missing_example_ar")
        if not example_en: flags.append("missing_example_en")
        if not root: flags.append("missing_root_field")
        if not related: flags.append("missing_related")
        if en and not LATIN.search(en): flags.append("en_not_latin")
        if fr and not LATIN.search(fr): flags.append("fr_not_latin")
        if ur and not ARABIC.search(ur): flags.append("ur_not_arabic_script")
        if example and not ARABIC.search(example): flags.append("example_not_arabic")
        if example_en and not LATIN.search(example_en): flags.append("example_translation_not_latin")
        if len(back) > 7000: flags.append("overlong_back")

        fw = arabic_words(front)
        ew = arabic_words(example)
        front_ok, front_bad = morphology(fw, analyzer)
        example_ok, example_bad = morphology(ew, analyzer)
        front_ratio = front_ok / len(fw) if fw else 0.0
        example_ratio = example_ok / len(ew) if ew else 0.0
        if fw and front_ratio < 0.80: flags.append("low_calima_front_coverage")
        if ew and example_ratio < 0.75: flags.append("low_calima_example_coverage")

        # Severity: missing core learner fields, malformed/mixed front, duplicate
        # normalized phrase, dialect-only front, or poor MSA morphology requires review.
        review_flags = {
            "blank_front","blank_back","multiline_front","overlong_front","too_many_front_tokens",
            "latin_in_front","no_arabic_in_front","normalized_duplicate_front","likely_dialect_main_front",
            "machine_artifact","missing_en","missing_fr","missing_ur","missing_definition_en",
            "missing_example_ar","missing_example_en","en_not_latin","fr_not_latin","ur_not_arabic_script",
            "example_not_arabic","example_translation_not_latin","low_calima_front_coverage","low_calima_example_coverage",
        }
        status = "explicit_review_required" if any(x in review_flags for x in flags) else "structurally_verified"
        counts[status] += 1
        details.append({
            "rank": rank,
            "front": front,
            "normalized_front": norm,
            "en": en,
            "fr": fr,
            "ur": ur,
            "definition_en": definition,
            "example_ar": example,
            "example_en": example_en,
            "root": root,
            "related": related,
            "front_token_count": len(fw),
            "front_calima_coverage": f"{front_ratio:.3f}",
            "front_unanalyzed_tokens": "|".join(dict.fromkeys(front_bad)),
            "example_token_count": len(ew),
            "example_calima_coverage": f"{example_ratio:.3f}",
            "example_unanalyzed_tokens": "|".join(dict.fromkeys(example_bad)),
            "flags": "|".join(flags),
            "status": status,
        })

    fields = list(details[0]) if details else ["rank","front","status"]
    with (AUDIT / "arabic_phrase_bank_audit.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(details)
    review = [d for d in details if d["status"] == "explicit_review_required"]
    with (AUDIT / "arabic_phrase_bank_review_queue.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(review)

    flag_counts = Counter()
    for d in details:
        for fl in filter(None, d["flags"].split("|")):
            flag_counts[fl] += 1
    summary = {
        "file": "arabic_phrase_bank.csv",
        "rows": len(rows),
        "distinct_exact_fronts": len({(r.get('Front') or '').strip() for r in rows}),
        "distinct_normalized_fronts": len(normalized_groups),
        "normalized_duplicate_groups": len(duplicate_norm),
        "status_counts": dict(sorted(counts.items())),
        "review_rows": len(review),
        "flag_counts": dict(sorted(flag_counts.items())),
        "front_tokens_total": sum(d["front_token_count"] for d in details),
        "front_tokens_calima_analyzed": sum(round(float(d["front_calima_coverage"])*d["front_token_count"]) for d in details),
        "example_tokens_total": sum(d["example_token_count"] for d in details),
        "example_tokens_calima_analyzed": sum(round(float(d["example_calima_coverage"])*d["example_token_count"]) for d in details),
        "promotion_gate": "PASS" if not review and len(rows) == 1405 else "REVIEW_REQUIRED",
        "policy": "Structural and MSA morphology checks are triage signals; they do not by themselves prove translation or phrase-level semantics.",
    }
    (AUDIT / "arabic_phrase_bank_audit_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
