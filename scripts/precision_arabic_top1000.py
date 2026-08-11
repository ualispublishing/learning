#!/usr/bin/env python3
"""Audit and precision-clean arabic_top1000.csv.

The first phase is intentionally conservative: it produces a complete, machine-readable
morphology/structure audit without changing study content. A later --apply pass uses
reviewed rules/overrides so uncertain linguistic claims are never silently invented.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "arabic_top1000.csv"
AUDIT_DIR = ROOT / "audit"
AUDIT_CSV = AUDIT_DIR / "arabic_top1000_morphology_audit.csv"
AUDIT_JSON = AUDIT_DIR / "arabic_top1000_audit_summary.json"

ARABIC_DIACRITICS = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
ARABIC_LETTER = re.compile(r"[\u0621-\u063a\u0641-\u064a]")
ROOT_LINE = re.compile(r"(?m)^Root Word:\s*(.*)$")
FIELD_LINE = {
    "en": re.compile(r"(?m)^EN:\s*(.*)$"),
    "fr": re.compile(r"(?m)^FR:\s*(.*)$"),
    "ur": re.compile(r"(?m)^UR:\s*(.*)$"),
    "definition": re.compile(r"(?ms)^Definition:\s*\n\(EN\)\s*(.*?)(?:\n\nExample:|\Z)"),
    "example": re.compile(r"(?m)^Example:\s*(.*)$"),
    "translation": re.compile(r"(?m)^Translation:\s*(.*)$"),
    "synonyms": re.compile(r"(?m)^Synonyms:\s*(.*)$"),
}

# Closed-class and solid-stem items that should not be forced into the productive
# root-and-pattern model. CAMeL morphology is the main authority; this set is a
# conservative backstop for diacritized spellings/coverage gaps.
NON_DERIVED_OR_CLOSED_CLASS = {
    "في", "من", "على", "أن", "إن", "إلى", "هذا", "هذه", "هؤلاء", "ذلك", "تلك",
    "لم", "لن", "لا", "ما", "ماذا", "يا", "هو", "هي", "هم", "هن", "هما", "نحن",
    "أنا", "أنت", "أنتم", "أنتن", "أنتما", "الذي", "التي", "الذين", "اللاتي", "اللواتي",
    "أو", "أم", "و", "ف", "ثم", "بل", "لكن", "لعل", "ليت", "كأن", "قد", "سوف",
    "حيث", "إذا", "إذ", "لو", "كي", "حتى", "عن", "مع", "هل", "أي", "أين", "متى",
    "كيف", "كم", "لماذا", "هنا", "هناك", "كلما", "كما", "إما", "إلا", "غير",
}

POS_WITHOUT_PRODUCTIVE_ROOT = {
    "prep", "conj", "pron", "pron_dem", "pron_rel", "adv_interrog", "pron_interrog",
    "part", "part_neg", "part_verb", "part_focus", "part_interrog", "part_voc",
    "part_fut", "part_restrict", "part_exhort", "part_det", "part_rc", "part_verb_like",
}


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text or "")


def undiac(text: str) -> str:
    text = nfc(text).replace("ـ", "")
    return ARABIC_DIACRITICS.sub("", text)


def canonical_key(text: str) -> str:
    text = undiac(text).strip()
    text = re.sub(r"[\s\u00a0]+", " ", text)
    # Normalize presentation-level alif variants for duplicate detection only.
    return text.translate(str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي"}))


def extract(pattern: re.Pattern[str], back: str) -> str:
    m = pattern.search(back or "")
    return m.group(1).strip() if m else ""


def current_root_arabic(back: str) -> str:
    value = extract(ROOT_LINE, back)
    if not value:
        return ""
    # Prefer Arabic text in parentheses, else Arabic letters anywhere in value.
    parens = re.findall(r"\(([^()]*)\)", value)
    candidate = parens[-1] if parens else value
    letters = ARABIC_LETTER.findall(undiac(candidate))
    return ".".join(letters)


def normalize_camel_root(value: str | None) -> str:
    if not value or value in {"0", "na", "#", "-"}:
        return ""
    value = undiac(value).replace("_", ".").replace("-", ".")
    letters = ARABIC_LETTER.findall(value)
    return ".".join(letters)


def english_terms(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z]+", (text or "").lower())
    stop = {"a", "an", "the", "to", "of", "and", "or", "in", "on", "at", "is", "be", "that", "which", "for", "with"}
    return {w for w in words if len(w) > 1 and w not in stop}


def choose_analysis(analyses: list[dict], en: str, definition: str) -> dict:
    if not analyses:
        return {}
    target = english_terms(en) | english_terms(definition)

    def score(a: dict) -> tuple[float, float, float]:
        gloss = english_terms(str(a.get("gloss", "")).replace(";", " ").replace("_", " "))
        overlap = len(target & gloss)
        poslex = float(a.get("pos_lex_logprob") or -99.0)
        lexprob = float(a.get("lex_logprob") or -99.0)
        # Semantic overlap dominates; probabilities break ties.
        return (overlap, poslex, lexprob)

    return max(analyses, key=score)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-only", action="store_true", help="Generate audit files only")
    args = parser.parse_args()

    try:
        from camel_tools.morphology.analyzer import Analyzer
        from camel_tools.morphology.database import MorphologyDB
    except ImportError as exc:
        raise SystemExit("camel-tools is required for the precision audit") from exc

    db = MorphologyDB.builtin_db("calima-msa-r13", flags="a")
    analyzer = Analyzer(db, backoff="NONE", cache_size=5000)

    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ["Front", "Back"]:
            raise SystemExit(f"Unexpected CSV schema: {reader.fieldnames!r}")
        rows = list(reader)

    key_to_indices: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(rows, start=1):
        key_to_indices[canonical_key(row["Front"])].append(i)

    audit_rows: list[dict[str, str | int]] = []
    flag_counts: Counter[str] = Counter()
    analyzed_count = 0
    no_analysis_count = 0

    for idx, row in enumerate(rows, start=1):
        front = nfc(row.get("Front", "")).strip()
        back = nfc(row.get("Back", ""))
        en = extract(FIELD_LINE["en"], back)
        fr = extract(FIELD_LINE["fr"], back)
        ur = extract(FIELD_LINE["ur"], back)
        definition = extract(FIELD_LINE["definition"], back)
        example = extract(FIELD_LINE["example"], back)
        translation = extract(FIELD_LINE["translation"], back)
        synonyms = extract(FIELD_LINE["synonyms"], back)
        root_raw = extract(ROOT_LINE, back)
        root_now = current_root_arabic(back)

        key = canonical_key(front)
        tokens = [t for t in re.split(r"\s+", undiac(front)) if t]
        multiword = len(tokens) != 1
        flags: list[str] = []

        for name, value in (("EN", en), ("FR", fr), ("UR", ur), ("definition", definition),
                            ("example", example), ("translation", translation)):
            if not value:
                flags.append(f"missing_{name.lower()}")

        if len(key_to_indices[key]) > 1:
            flags.append("duplicate_front")
        if "AR: (self)" in back:
            flags.append("self_translation_artifact")
        if synonyms and canonical_key(front) in {canonical_key(x.strip()) for x in re.split(r"[,،]", synonyms)}:
            flags.append("self_listed_as_synonym")

        camel_pos = camel_lex = camel_root = camel_gloss = ""
        if multiword:
            flags.append("multiword_no_single_root")
            if root_raw and root_now:
                flags.append("phrase_has_single_root_claim")
        else:
            surface = undiac(front)
            analyses = analyzer.analyze(surface)
            if analyses:
                analyzed_count += 1
                best = choose_analysis(analyses, en, definition)
                camel_pos = str(best.get("pos", ""))
                camel_lex = str(best.get("lex", "")).replace("_1", "").replace("_2", "")
                camel_root = normalize_camel_root(best.get("root"))
                camel_gloss = str(best.get("gloss", ""))
            else:
                no_analysis_count += 1
                flags.append("camel_no_analysis")

            if surface in NON_DERIVED_OR_CLOSED_CLASS:
                flags.append("closed_class_no_productive_root")
            if camel_pos in POS_WITHOUT_PRODUCTIVE_ROOT and not camel_root:
                flags.append("camel_nonroot_function_word")

            if root_now and not camel_root and (surface in NON_DERIVED_OR_CLOSED_CLASS or camel_pos in POS_WITHOUT_PRODUCTIVE_ROOT):
                flags.append("invented_root_on_function_word")
            elif root_now and camel_root and root_now != camel_root:
                flags.append("root_disagrees_with_camel")
            elif not root_now and camel_root:
                flags.append("missing_valid_root")

        # Known high-confidence grammar problem discovered in manual review.
        if front == "مِنَ الصَّعْبِ تَصَدِّيقُهُ" or front == "مِنَ الصَّعْبِ تَصْدِيقُهُ":
            if "هَذِهِ القِصَّةُ" in example and ("تَصْدِيقُهُ" in example or "تَصَدِّيقُهُ" in example):
                flags.append("example_pronoun_gender_mismatch")

        for flag in flags:
            flag_counts[flag] += 1

        audit_rows.append({
            "index": idx,
            "front": front,
            "english": en,
            "current_root_raw": root_raw,
            "current_root_ar": root_now,
            "camel_pos": camel_pos,
            "camel_lemma": camel_lex,
            "camel_root": camel_root,
            "camel_gloss": camel_gloss,
            "token_count": len(tokens),
            "flags": "|".join(flags),
        })

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    with AUDIT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(audit_rows[0].keys()))
        writer.writeheader()
        writer.writerows(audit_rows)

    summary = {
        "source": str(SOURCE.relative_to(ROOT)),
        "row_count": len(rows),
        "schema": ["Front", "Back"],
        "unique_normalized_fronts": len(key_to_indices),
        "duplicate_front_groups": sum(1 for v in key_to_indices.values() if len(v) > 1),
        "camel_single_word_analyzed": analyzed_count,
        "camel_single_word_no_analysis": no_analysis_count,
        "flag_counts": dict(sorted(flag_counts.items())),
        "principles": {
            "root_policy": "Use a lexical root only when supported by MSA morphology; do not invent roots for non-root function words.",
            "phrase_policy": "A multiword expression has no single lexical root; analyze constituent content words separately if needed.",
            "ambiguity_policy": "Automated morphology is evidence, not authority; disagreements are flagged for review rather than silently overwritten.",
        },
    }
    AUDIT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if not args.audit_only:
        raise SystemExit("Apply mode is intentionally disabled until audit discrepancies are reviewed.")


if __name__ == "__main__":
    main()
