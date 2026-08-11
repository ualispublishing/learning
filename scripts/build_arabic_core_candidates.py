#!/usr/bin/env python3
"""Build a reproducible MSA lexical-core candidate list from CAMeL frequencies.

Inventory selection is separated from flashcard prose. Surface frequencies are mapped to
MSA lexical analyses using CAMeL's pretrained MLE disambiguator, then aggregated by
lemma + lexical POS. This prevents a frequent undiacritized form from being assigned to
an arbitrary morphology analysis (for example كل -> أكل rather than كُلّ).
"""

from __future__ import annotations

import argparse
import csv
import re
import unicodedata
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

AR_DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
AR_LETTER = re.compile(r"[\u0621-\u063a\u0641-\u064a]")
SENSE_SUFFIX = re.compile(r"_[0-9]+$")

EXCLUDED_POS = {"noun_prop", "foreign"}
NONROOT_POS_PREFIXES = (
    "prep", "conj", "pron", "part", "adv_interrog", "pron_interrog",
)


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s or "")


def undiac(s: str) -> str:
    return AR_DIAC.sub("", nfc(s).replace("ـ", ""))


def key(s: str) -> str:
    return undiac(s).translate(str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي"})).strip()


def clean_lemma(s: str) -> str:
    s = SENSE_SUFFIX.sub("", nfc(s or ""))
    s = s.replace("+", "").replace("#", "")
    return s.strip()


def valid_arabic_word(s: str) -> bool:
    plain = undiac(s)
    return bool(plain) and all(ch.isspace() or AR_LETTER.fullmatch(ch) for ch in plain)


def normalize_root(value: str | None, pos: str) -> str:
    if not value or pos.startswith(NONROOT_POS_PREFIXES):
        return ""
    letters = AR_LETTER.findall(undiac(value))
    if len(letters) not in (3, 4):
        return ""
    return " ".join(letters)


def iter_top_frequency_rows(zf: zipfile.ZipFile, member: str, per_file_limit: int):
    with zf.open(member) as raw:
        for i, line in enumerate(raw):
            if i >= per_file_limit:
                break
            text = line.decode("utf-8-sig", errors="replace").strip()
            if not text or "\t" not in text:
                continue
            word, freq_s = text.rsplit("\t", 1)
            try:
                freq = int(freq_s)
            except ValueError:
                continue
            yield word.strip(), freq


def chunks(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def analysis_from_disambiguated_word(dw) -> dict:
    if not getattr(dw, "analyses", None):
        return {}
    top = dw.analyses[0]
    analysis = getattr(top, "analysis", None)
    return analysis if isinstance(analysis, dict) else {}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frequency-zip", required=True, type=Path)
    ap.add_argument("--output", type=Path, default=Path("audit/arabic_msa_core_candidates.csv"))
    ap.add_argument("--summary", type=Path, default=Path("audit/arabic_msa_core_candidates_summary.txt"))
    ap.add_argument("--per-file-limit", type=int, default=50000)
    ap.add_argument("--candidate-count", type=int, default=1500)
    ap.add_argument("--batch-size", type=int, default=512)
    args = ap.parse_args()

    from camel_tools.disambig.mle import MLEDisambiguator

    mle = MLEDisambiguator.pretrained("calima-msa-r13", top=1, cache_size=100000)

    surface_freq: Counter[str] = Counter()
    with zipfile.ZipFile(args.frequency_zip) as zf:
        members = [
            n for n in zf.namelist()
            if n.lower().endswith((".tsv", ".txt")) and not n.startswith("__MACOSX/")
        ]
        if not members:
            raise SystemExit(f"No TSV/TXT members found; archive contains: {zf.namelist()}")
        for member in members:
            for surface, freq in iter_top_frequency_rows(zf, member, args.per_file_limit):
                if valid_arabic_word(surface):
                    surface_freq[surface] += freq

    surface_items = surface_freq.most_common()
    lemma_freq: Counter[tuple[str, str]] = Counter()
    records: dict[tuple[str, str], dict] = {}
    surfaces_by_lexeme: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    skipped = Counter()

    for batch in chunks(surface_items, args.batch_size):
        words = [undiac(surface) for surface, _ in batch]
        disambig = mle.disambiguate(words)
        if len(disambig) != len(batch):
            raise RuntimeError("MLE disambiguator returned an unexpected number of words")

        for (surface, freq), dw in zip(batch, disambig):
            a = analysis_from_disambiguated_word(dw)
            if not a:
                skipped["no_analysis"] += 1
                continue

            pos = str(a.get("pos", "")).strip()
            if pos in EXCLUDED_POS:
                skipped["excluded_pos"] += 1
                continue

            lemma = clean_lemma(str(a.get("lex", "")))
            if not lemma or not valid_arabic_word(lemma):
                skipped["bad_lemma"] += 1
                continue

            # POS remains part of the key so true homographic lexemes are not merged.
            # Presentation-layer deduplication can later decide whether a learner should
            # see separate sense cards or one carefully labeled multi-sense entry.
            lexeme_key = (key(lemma), pos)
            if not lexeme_key[0]:
                continue

            lemma_freq[lexeme_key] += freq
            surfaces_by_lexeme[lexeme_key][surface] += freq
            if lexeme_key not in records or freq > records[lexeme_key]["metadata_surface_freq"]:
                records[lexeme_key] = {
                    "front": lemma,
                    "lemma_undiac": undiac(lemma),
                    "pos": pos,
                    "root": normalize_root(str(a.get("root", "")), pos),
                    "english_gloss": str(a.get("gloss", "")).replace("_", " ").strip(),
                    "metadata_surface": surface,
                    "metadata_surface_freq": freq,
                }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    ranked = lemma_freq.most_common(args.candidate_count)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        fields = [
            "rank", "front", "lemma_undiac", "pos", "root", "english_gloss",
            "frequency", "surface_types", "top_surfaces",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for rank, (lexeme_key, freq) in enumerate(ranked, start=1):
            r = records[lexeme_key]
            tops = surfaces_by_lexeme[lexeme_key].most_common(6)
            w.writerow({
                "rank": rank,
                "front": r["front"],
                "lemma_undiac": r["lemma_undiac"],
                "pos": r["pos"],
                "root": r["root"],
                "english_gloss": r["english_gloss"],
                "frequency": freq,
                "surface_types": len(surfaces_by_lexeme[lexeme_key]),
                "top_surfaces": " | ".join(f"{s}:{n}" for s, n in tops),
            })

    args.summary.write_text(
        "\n".join([
            f"archive_members={members!r}",
            f"surface_types_loaded={len(surface_freq)}",
            f"unique_lemma_pos_lexemes={len(lemma_freq)}",
            f"candidates_written={len(ranked)}",
            f"skipped={dict(skipped)}",
            "source=https://github.com/CAMeL-Lab/Camel_Arabic_Frequency_Lists/releases/tag/v1.0",
            "method=CAMeL MSA frequency surfaces -> pretrained CALIMA-MSA MLE disambiguation -> aggregate by lemma+POS; exclude proper/foreign items",
            "root_policy=emit only 3/4-radical roots for lexical POS; omit roots for closed-class function words",
        ]) + "\n",
        encoding="utf-8",
    )
    print(args.summary.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
