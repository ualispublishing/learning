#!/usr/bin/env python3
"""Regression checks for external-verifier source-header compatibility."""
from __future__ import annotations

import verify_top1000_external as verifier


def main() -> None:
    headers = [
        "1_Mot",
        "2_Phono",
        "3_Phono_IPA",
        "4_Lemme",
        "5_Cgram",
        "6_CgramOrtho",
        "10_FreqMot",
        "11_FreqOrtho",
        "12_FreqLemme",
    ]

    assert verifier.find_column(
        headers,
        ("mot", "ortho", "orthography", "word", "forme", "form", "graphie"),
    ) == "1_Mot"
    assert verifier.find_column(headers, ("lemme", "lemma")) == "4_Lemme"
    assert verifier.find_column(
        headers,
        ("cgram", "grammatical_category", "pos", "categorie", "catgram"),
    ) == "5_Cgram"

    # Preserve compatibility with unnumbered/legacy header names too.
    legacy = ["ortho", "lemme", "cgram"]
    assert verifier.find_column(legacy, ("mot", "ortho", "word")) == "ortho"
    assert verifier.find_column(legacy, ("lemme", "lemma")) == "lemme"
    assert verifier.find_column(legacy, ("cgram", "pos")) == "cgram"

    verifier.check_lexique4_header_compatibility()
    print("PASS: Lexique4 numbered and legacy headers resolve correctly")


if __name__ == "__main__":
    main()
