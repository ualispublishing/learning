#!/usr/bin/env python3
"""Build a reproducible MSA lexical-core candidate list from CAMeL frequencies.

This script does not generate study-card prose. It establishes the *inventory* first:
frequency evidence -> MSA morphological analysis -> lemma/POS/root/gloss -> ranked unique
lexemes. Keeping inventory selection separate from card writing makes the final deck auditable.
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

# Proper names, foreign items, digits and punctuation are not appropriate for a general
# lexical core. Everything else is retained, including high-frequency function words.
EXCLUDED_POS = {"noun_prop", "foreign"}

# Closed classes do not receive a pedagogical root even if a morphology DB has a
# historical/placeholder root feature.
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
    # Arabic lexical roots are overwhelmingly 3 or 4 radicals; anything else is not
    # safe enough to teach automatically.
    if len(letters) not in (3, 4):
        return ""
    return " ".join(letters)


def best_analysis(analyses: list[dict]) -> dict:
    if not analyses:
        return {}

    def num(x, default=-99.0):
        try:
            return float(x)
        except (TypeError, ValueError):
            return default

    # Prefer ordinary MSA lexemes with strong lexical probability. The analyzer's
    # probability features are used only for ranking analyses of the same surface form.
    def score(a: dict):
        pos = str(a.get("pos", ""))
        excluded = 1 if pos in EXCLUDED_POS else 0
        return (-excluded, num(a.get("pos_lex_logprob")), num(a.get("lex_logprob")))

    return max(analyses, key=score)


def iter_top_frequency_rows(zf: zipfile.ZipFile, member: str, per_file_limit: int):
    with zf.open(member) as raw:
        prev = None
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
            # Frequency files are expected to be sorted. We do not abort on a rare
            # local inversion, but track it through the returned data if needed.
            prev = freq if prev is None else prev
            yield word.strip(), freq
            prev = freq


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frequency-zip", required=True, type=Path)
    ap.add_argument("--output", type=Path, default=Path("audit/arabic_msa_core_candidates.csv"))
    ap.add_argument("--summary", type=Path, default=Path("audit/arabic_msa_core_candidates_summary.txt"))
    ap.add_argument("--per-file-limit", type=int, default=50000)
    ap.add_argument("--candidate-count", type=int, default=1500)
    args = ap.parse_args()

    from camel_tools.morphology.analyzer import Analyzer
    from camel_tools.morphology.database import MorphologyDB

    db = MorphologyDB.builtin_db("calima-msa-r13", flags="a")
    analyzer = Analyzer(db, backoff="NONE", cache_size=50000)

    surface_freq: Counter[str] = Counter()
    with zipfile.ZipFile(args.frequency_zip) as zf:
        members = [n for n in zf.namelist() if n.lower().endswith((".tsv", ".txt"))]
        if not members:
            raise SystemExit(f"No TSV/TXT members found; archive contains: {zf.namelist()}")
        for member in members:
            for surface, freq in iter_top_frequency_rows(zf, member, args.per_file_limit):
                if valid_arabic_word(surface):
                    surface_freq[surface] += freq

    lemma_freq: Counter[str] = Counter()
    records: dict[str, dict] = {}
    surfaces_by_lemma: dict[str, Counter[str]] = defaultdict(Counter)
    skipped = Counter()

    # Analyzing the most frequent surface types is enough to produce a stable 1k core,
    # while avoiding millions of negligible tail forms.
    for surface, freq in surface_freq.most_common():
        analyses = analyzer.analyze(undiac(surface))
        if not analyses:
            skipped["no_analysis"] += 1
            continue
        a = best_analysis(analyses)
        pos = str(a.get("pos", ""))
        if pos in EXCLUDED_POS:
            skipped["excluded_pos"] += 1
            continue
        lemma = clean_lemma(str(a.get("lex", "")))
        if not lemma or not valid_arabic_word(lemma):
            skipped["bad_lemma"] += 1
            continue
        k = key(lemma)
        if not k:
            continue
        lemma_freq[k] += freq
        surfaces_by_lemma[k][surface] += freq
        # Save metadata from the strongest surface contribution. It will be replaced if
        # a later surface contributes more frequency to the same lemma.
        if k not in records or freq > records[k]["metadata_surface_freq"]:
            records[k] = {
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
        fields = ["rank", "front", "lemma_undiac", "pos", "root", "english_gloss", "frequency", "surface_types", "top_surfaces"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for rank, (k, freq) in enumerate(ranked, start=1):
            r = records[k]
            tops = surfaces_by_lemma[k].most_common(6)
            w.writerow({
                "rank": rank,
                "front": r["front"],
                "lemma_undiac": r["lemma_undiac"],
                "pos": r["pos"],
                "root": r["root"],
                "english_gloss": r["english_gloss"],
                "frequency": freq,
                "surface_types": len(surfaces_by_lemma[k]),
                "top_surfaces": " | ".join(f"{s}:{n}" for s, n in tops),
            })

    args.summary.write_text(
        "\n".join([
            f"archive_members={members!r}",
            f"surface_types_loaded={len(surface_freq)}",
            f"unique_lemmas={len(lemma_freq)}",
            f"candidates_written={len(ranked)}",
            f"skipped={dict(skipped)}",
            "source=https://github.com/CAMeL-Lab/Camel_Arabic_Frequency_Lists/releases/tag/v1.0",
            "method=aggregate high-frequency MSA surface forms by strongest CALIMA-MSA lexical analysis; exclude proper/foreign items",
        ]) + "\n",
        encoding="utf-8",
    )

    print(args.summary.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
