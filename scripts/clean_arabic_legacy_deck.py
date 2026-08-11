#!/usr/bin/env python3
"""Preserve the uploaded Arabic deck and split its phrase material safely.

The uploaded file mixes lexical items and multiword expressions. This script never destroys
that source: it archives it verbatim, then emits a de-duplicated phrase bank with claims
that are invalid at phrase level removed or relabeled.
"""

from __future__ import annotations

import csv
import re
import shutil
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "arabic_top1000.csv"
ARCHIVE = ROOT / "archive" / "wordlists" / "arabic_top1000_uploaded_2026-08-11.csv"
PHRASES = ROOT / "arabic_phrase_bank.csv"
LEGACY_WORDS = ROOT / "audit" / "arabic_legacy_single_words_cleaned.csv"

DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
ROOT_LINE = re.compile(r"(?m)^Root Word:\s*.*$")
SYN_LINE = re.compile(r"(?m)^Synonyms:\s*(.*)$")
ARABIC_WORD_RE = re.compile(r"[\u0621-\u064a]+")

CLOSED_CLASS = {
    "في", "من", "على", "أن", "إن", "إلى", "هذا", "هذه", "هؤلاء", "ذلك", "تلك", "لم", "لن", "لا",
    "ما", "ماذا", "يا", "هو", "هي", "هم", "هن", "هما", "نحن", "أنا", "أنت", "أنتم", "أنتن", "أنتما",
    "الذي", "التي", "الذين", "اللاتي", "اللواتي", "أو", "أم", "و", "ف", "ثم", "بل", "لكن", "لعل",
    "ليت", "كأن", "قد", "سوف", "حيث", "إذا", "إذ", "لو", "كي", "حتى", "عن", "مع", "هل", "أي",
    "أين", "متى", "كيف", "كم", "لماذا", "هنا", "هناك", "كما", "إما", "إلا",
}


def undiac(s: str) -> str:
    return DIAC.sub("", unicodedata.normalize("NFC", s or "").replace("ـ", ""))


def key(s: str) -> str:
    return re.sub(r"\s+", " ", undiac(s).strip()).translate(str.maketrans({"أ":"ا", "إ":"ا", "آ":"ا", "ٱ":"ا", "ى":"ي"}))


def token_count(front: str) -> int:
    return len([x for x in re.split(r"\s+", undiac(front).strip()) if x])


def clean_back(front: str, back: str, phrase: bool) -> str:
    back = unicodedata.normalize("NFC", back or "")
    back = back.replace("\nAR: (self)", "")

    if phrase:
        if ROOT_LINE.search(back):
            back = ROOT_LINE.sub("Root: — (multiword expression; no single lexical root)", back)
        # Existing 'synonyms' in generated phrase cards are often paraphrases/near-equivalents,
        # not substitution-equivalent synonyms. Relabel rather than overclaim.
        back = SYN_LINE.sub(lambda m: f"Related / near-equivalents: {m.group(1)}", back)
    else:
        if key(front) in {key(x) for x in CLOSED_CLASS} and ROOT_LINE.search(back):
            back = ROOT_LINE.sub("Root: — (function word; no productive lexical root)", back)

    # High-confidence correction found by manual audit.
    if key(front) == key("مِنَ الصَّعْبِ تَصْدِيقُهُ"):
        back = back.replace(
            "هَذِهِ القِصَّةُ مِنَ الصَّعْبِ تَصْدِيقُهُ.",
            "مِنَ الصَّعْبِ تَصْدِيقُ هَذِهِ القِصَّةِ.",
        ).replace(
            "هَذِهِ القِصَّةُ مِنَ الصَّعْبِ تَصَدِّيقُهُ.",
            "مِنَ الصَّعْبِ تَصْدِيقُ هَذِهِ القِصَّةِ.",
        )
    return back


def main() -> None:
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    PHRASES.parent.mkdir(parents=True, exist_ok=True)
    LEGACY_WORDS.parent.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE.exists():
        shutil.copyfile(SOURCE, ARCHIVE)

    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Earliest occurrence wins: the uploaded deck is ordered, so this preserves the
    # primary/highest-ranked sense while the verbatim archive retains every alternative.
    phrase_rows = []
    word_rows = []
    seen_phrase = set()
    seen_word = set()
    for row in rows:
        front = row["Front"].strip()
        is_phrase = token_count(front) > 1
        k = key(front)
        if is_phrase:
            if k in seen_phrase:
                continue
            seen_phrase.add(k)
            phrase_rows.append({"Front": front, "Back": clean_back(front, row["Back"], True)})
        else:
            if k in seen_word:
                continue
            seen_word.add(k)
            word_rows.append({"Front": front, "Back": clean_back(front, row["Back"], False)})

    for path, out_rows in ((PHRASES, phrase_rows), (LEGACY_WORDS, word_rows)):
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["Front", "Back"], lineterminator="\n")
            w.writeheader()
            w.writerows(out_rows)

    print(f"archived={ARCHIVE}")
    print(f"phrase_bank_rows={len(phrase_rows)}")
    print(f"legacy_unique_single_word_rows={len(word_rows)}")


if __name__ == "__main__":
    main()
