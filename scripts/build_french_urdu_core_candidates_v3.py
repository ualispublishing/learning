#!/usr/bin/env python3
"""Precision candidate builder with CLE-specific Urdu Unicode normalization.

CLE's legacy PDF font/text encoding uses Arabic HEH (ه) in positions that
represent Urdu DO-CHASHMI HE (ھ), e.g. source `بهی`, `تها`, `کچه`, `پهر`,
`گهر` correspond to standard Urdu `بھی`, `تھا`, `کچھ`, `پھر`, `گھر`.
Dictionary sources are normalized separately and must NOT apply this rule.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import build_french_urdu_core_candidates_v2 as v2

ROOT = v2.ROOT
AUDIT = v2.AUDIT


def norm_ur_cle(s: str) -> str:
    s = v2.nfkc(s).replace("ـ", "").replace("\u200c", "").replace("\u200d", "")
    s = v2.URDU_DIAC.sub("", s)
    # CLE PDF legacy encoding: Arabic yeh/kaf normalization plus Arabic HEH as
    # do-chashmi he. True Urdu heh-goal is already encoded distinctly as ہ.
    return (
        s.replace("ي", "ی")
         .replace("ى", "ی")
         .replace("ك", "ک")
         .replace("ه", "ھ")
         .strip()
    )


def extract_urdu_freq_cle(text: str) -> list[tuple[str, int]]:
    pairs: list[tuple[str, int]] = []
    seen = set()
    for raw in text.splitlines():
        line = v2.nfkc(raw)
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            continue
        m = re.match(r"^(\d{2,})\s+(.+)$", line)
        if m:
            freq, word = int(m.group(1)), m.group(2)
        else:
            m = re.match(r"^(.+?)\s+(\d{2,})$", line)
            if not m:
                continue
            word, freq = m.group(1), int(m.group(2))
        word = norm_ur_cle(word)
        if not word or not v2.URDUISH.fullmatch(word) or len(word) > 45:
            continue
        if word in seen:
            continue
        seen.add(word)
        pairs.append((word, freq))
    pairs.sort(key=lambda x: -x[1])
    return pairs


def build_urdu(args) -> None:
    freq_text = Path(args.urdu_freq_text).read_text(encoding="utf-8", errors="replace")
    wn_text = norm_ur_cle(Path(args.urdu_wordnet_text).read_text(encoding="utf-8", errors="replace"))
    closed_text = norm_ur_cle(Path(args.urdu_closed_text).read_text(encoding="utf-8", errors="replace"))
    ranked = extract_urdu_freq_cle(freq_text)

    # Dictionary resources use ordinary Urdu Unicode normalization, not CLE legacy encoding.
    readurdu = v2.read_readurdu(Path(args.readurdu))
    kaikki = v2.load_kaikki(Path(args.kaikki), v2.norm_ur)

    selected = []
    rejected = []
    for word, freq in ranked:
        in_wn = v2.inventory_contains(wn_text, word)
        in_closed = v2.inventory_contains(closed_text, word)
        alternate_double = word in readurdu and word in kaikki
        if not (in_wn or in_closed or alternate_double):
            rejected.append({"front": word, "frequency": freq, "reason": "insufficient_lexical_support"})
            continue

        meaning = ""
        semantic_source = ""
        if word in readurdu:
            meaning = readurdu[word]["meaning"]
            semantic_source = "ReadUrdu composite dictionary"
        if not meaning and word in kaikki:
            meaning = v2.compact_meaning(kaikki[word]["all_glosses"])
            semantic_source = "Kaikki/Wiktextract"
        if not meaning:
            rejected.append({"front": word, "frequency": freq, "reason": "no_clean_dictionary_meaning"})
            continue

        kposes = sorted(kaikki.get(word, {}).get("poses", set()))
        selected.append({
            "rank": len(selected) + 1,
            "front": word,
            "meaning": meaning,
            "pos": "|".join(kposes) or ("closed-class" if in_closed else "content word"),
            "frequency": freq,
            "cle_wordnet": in_wn,
            "cle_closed_class": in_closed,
            "readurdu_entry": word in readurdu,
            "kaikki_entry": word in kaikki,
            "semantic_source": semantic_source,
            "source": "CLE Urdu 5,000 corpus frequency list (legacy Unicode normalized) + CLE lexical inventories; ReadUrdu/Kaikki semantics",
        })
        if len(selected) == 1000:
            break

    v2.write_candidate("urdu", selected, rejected, extra_summary={
        "parsed_frequency_rows": len(ranked),
        "cle_unicode_normalization": "Arabic HEH (ه) -> Urdu do-chashmi HE (ھ) for CLE PDF extraction only",
        "source_tripwires": {
            "بھی": 140157,
            "تھا": 61762,
            "تھے": 43418,
            "کچھ": 21568,
            "پھر": 17870,
            "گھر": 11973,
        },
        "tripwires_present": {
            "بھی": any(r["front"] == "بھی" and r["frequency"] == 140157 for r in selected),
            "malformed_بہی_absent": all(r["front"] != "بہی" for r in selected),
        },
    })


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--language", choices=["french", "urdu"], required=True)
    ap.add_argument("--lexique")
    ap.add_argument("--kaikki", required=True)
    ap.add_argument("--legacy-french")
    ap.add_argument("--urdu-freq-text")
    ap.add_argument("--urdu-wordnet-text")
    ap.add_argument("--urdu-closed-text")
    ap.add_argument("--readurdu")
    args = ap.parse_args()
    if args.language == "french":
        if not args.lexique:
            raise SystemExit("--lexique required for French")
        v2.build_french(args)
    else:
        required = [args.urdu_freq_text, args.urdu_wordnet_text, args.urdu_closed_text, args.readurdu]
        if not all(required):
            raise SystemExit("Urdu requires frequency/WordNet/closed-class text and ReadUrdu dictionary")
        build_urdu(args)


if __name__ == "__main__":
    main()
