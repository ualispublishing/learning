#!/usr/bin/env python3
"""Whole-file structural sanity gate for language workbook v1.0 companion CSVs.

This complements exact decision alignment. It detects corruption that can be faithfully
propagated from a bad historical source pair (for example, a sentence split across CSV
columns or a truncated English fragment) without pretending to be a native-speaker
linguistic certification.
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "completed" / "languages" / "workbooks" / "v1.0"
AUDIT = ROOT / "audit" / "language-workbooks" / "v1.0"
LANGUAGES = ("arabic", "french", "urdu")
SENTENCE_FIELDS = ("rank", "level", "target", "english", "attribution")
VOCAB_FIELDS = ("rank", "target", "english", "part_of_speech")
ARABIC_BLOCKS = ((0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF))
FRENCH_FUNCTION = re.compile(
    r"\b(?:je|tu|il|elle|nous|vous|ils|elles|s'il|plaît|est|suis|sont|peux|pouvez|pourriez|avec|dans|pour|pas|quoi|comment|où|quand|pourquoi)\b",
    re.IGNORECASE,
)


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").replace("ـ", "")
    value = re.sub(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]", "", value)
    return re.sub(r"\s+", " ", value).strip().casefold()


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        raise SystemExit(f"missing required CSV: {path}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def latin_ratio(text: str) -> float:
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return 0.0
    good = 0
    for ch in letters:
        name = unicodedata.name(ch, "")
        if "LATIN" in name:
            good += 1
    return good / len(letters)


def arabic_ratio(text: str) -> float:
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return 0.0
    good = 0
    for ch in letters:
        code = ord(ch)
        if any(lo <= code <= hi for lo, hi in ARABIC_BLOCKS):
            good += 1
    return good / len(letters)


def token_count(text: str) -> int:
    return len(re.findall(r"\b[^\W_]+(?:['’-][^\W_]+)*\b", text, flags=re.UNICODE))


def english_word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z]+(?:['’-][A-Za-z]+)*", text))


def quote_problems(value: str) -> list[str]:
    problems = []
    if value.count('"') % 2:
        problems.append("unbalanced_ascii_double_quote")
    if value.count("“") != value.count("”"):
        problems.append("unbalanced_curly_double_quote")
    if value.count("«") != value.count("»"):
        problems.append("unbalanced_guillemets")
    return problems


def forbidden_characters(value: str) -> list[str]:
    problems = []
    if "\ufffd" in value:
        problems.append("unicode_replacement_character")
    if any(unicodedata.category(ch) == "Cc" for ch in value):
        problems.append("control_character")
    return problems


def audit_language(language: str) -> dict:
    sentence_path = OUT / language / f"{language}_sentence_bank_1000.csv"
    vocab_path = OUT / language / f"{language}_vocabulary_1000.csv"
    sfields, sentences = load_csv(sentence_path)
    vfields, vocab = load_csv(vocab_path)

    failures: list[dict] = []
    warnings: list[dict] = []

    if sfields != list(SENTENCE_FIELDS):
        failures.append({"type": "sentence_schema", "observed": sfields, "expected": list(SENTENCE_FIELDS)})
    if vfields != list(VOCAB_FIELDS):
        failures.append({"type": "vocabulary_schema", "observed": vfields, "expected": list(VOCAB_FIELDS)})
    if len(sentences) != 1000:
        failures.append({"type": "sentence_row_count", "observed": len(sentences), "expected": 1000})
    if len(vocab) != 1000:
        failures.append({"type": "vocabulary_row_count", "observed": len(vocab), "expected": 1000})

    for kind, rows, fields in (("sentence", sentences, SENTENCE_FIELDS), ("vocabulary", vocab, VOCAB_FIELDS)):
        ranks = []
        for pos, row in enumerate(rows, start=1):
            try:
                rank = int(row.get("rank", ""))
            except ValueError:
                rank = -1
            ranks.append(rank)
            if rank != pos:
                failures.append({"type": f"{kind}_rank_drift", "position": pos, "observed": row.get("rank")})
            for field in fields:
                value = row.get(field)
                if value is None or not str(value).strip():
                    failures.append({"type": f"{kind}_blank_field", "rank": pos, "field": field})
                    continue
                for issue in forbidden_characters(str(value)):
                    failures.append({"type": issue, "kind": kind, "rank": pos, "field": field})
                if field in {"target", "english"}:
                    for issue in quote_problems(str(value)):
                        failures.append({"type": issue, "kind": kind, "rank": pos, "field": field, "value": value})

        if ranks != list(range(1, len(rows) + 1)):
            # Detailed drift entries above contain the actionable ranks.
            pass

    if len(sentences) == 1000:
        if len({norm(row["target"]) for row in sentences}) != 1000:
            failures.append({"type": "sentence_target_uniqueness"})
        if len({norm(row["english"]) for row in sentences}) != 1000:
            failures.append({"type": "sentence_english_uniqueness"})

    # Script plausibility is deliberately coarse and structural, not linguistic grading.
    for row in sentences:
        rank = int(row["rank"])
        target = row["target"]
        english = row["english"]
        target_ratio = latin_ratio(target) if language == "french" else arabic_ratio(target)
        if target_ratio < 0.65:
            failures.append({"type": "target_script_ratio", "rank": rank, "ratio": round(target_ratio, 3), "value": target})
        if latin_ratio(english) < 0.65:
            failures.append({"type": "english_script_ratio", "rank": rank, "ratio": round(latin_ratio(english), 3), "value": english})

        if language == "french":
            target_words = token_count(target)
            english_words = english_word_count(english)
            if (target_words >= 8 and english_words <= 3) or (english_words >= 8 and target_words <= 3):
                failures.append({
                    "type": "extreme_french_length_mismatch",
                    "rank": rank,
                    "target_words": target_words,
                    "english_words": english_words,
                    "target": target,
                    "english": english,
                })
            markers = FRENCH_FUNCTION.findall(english)
            if len(markers) >= 2:
                failures.append({
                    "type": "french_function_words_in_english_field",
                    "rank": rank,
                    "markers": markers,
                    "english": english,
                })

        if language in {"arabic", "urdu"}:
            # Typography-only findings are visible in the audit but do not fail semantic production.
            if re.search(r"\s+[،؟.]", target):
                warnings.append({"type": "space_before_target_punctuation", "rank": rank, "target": target})
            if "," in target and any("ARABIC" in unicodedata.name(ch, "") for ch in target if ch.isalpha()):
                warnings.append({"type": "ascii_comma_in_arabic_script_target", "rank": rank, "target": target})

    return {
        "gate": "PASS" if not failures else "FAIL",
        "sentence_rows": len(sentences),
        "vocabulary_rows": len(vocab),
        "hard_failure_count": len(failures),
        "warning_count": len(warnings),
        "hard_failures": failures,
        "warnings": warnings,
    }


def main() -> None:
    AUDIT.mkdir(parents=True, exist_ok=True)
    languages = {language: audit_language(language) for language in LANGUAGES}
    failures = sum(info["hard_failure_count"] for info in languages.values())
    result = {
        "release": "v1.0",
        "gate": "PASS" if failures == 0 else "FAIL",
        "scope": "whole-file structural/encoding/bilingual-column sanity; not native-speaker certification",
        "languages": languages,
        "hard_failure_count": failures,
        "warning_count": sum(info["warning_count"] for info in languages.values()),
    }
    path = AUDIT / "content_sanity.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(f"language workbook content sanity failed with {failures} hard failure(s)")


if __name__ == "__main__":
    main()
