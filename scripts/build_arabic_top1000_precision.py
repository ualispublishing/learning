#!/usr/bin/env python3
"""Build a precision-grade Arabic top-1000 flashcard candidate.

The published deck is derived directly from CAMeL's machine-readable MSA frequency
inventory after CALIMA-MSA disambiguation. The broad candidate builder has already
aggregated surface-token frequencies by lemma + POS; this presentation step then:

- ranks by validated aggregate frequency;
- merges genuine homographs and harmless orthographic variants into one learner front;
- keeps extending the ranked candidate stream until there are 1,000 UNIQUE canonical fronts;
- emits roots only when CALIMA-MSA supplied a defensible lexical root;
- never invents a root for closed-class/function words;
- does not emit generated synonyms, examples, etymologies, French, or Urdu glosses.

Those omitted enrichment fields can be added later only from independently verified
bilingual/example sources. Precision is preferred to plausible-looking fabrication.
"""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from collections import OrderedDict
from pathlib import Path

DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
ARABIC_ONLY = re.compile(r"^[\u0621-\u064a]+$")
CANON_TRANS = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي"})

POS_LABELS = {
    "noun": "noun", "noun_num": "numeral noun", "noun_quant": "quantifying noun",
    "adj_num": "numeral adjective", "adj": "adjective", "adj_comp": "comparative adjective",
    "verb": "verb", "adv": "adverb", "adv_interrog": "interrogative adverb",
    "adv_rel": "relative adverb", "prep": "preposition", "conj": "conjunction",
    "conj_sub": "subordinating conjunction", "pron": "pronoun",
    "pron_dem": "demonstrative pronoun", "pron_rel": "relative pronoun",
    "pron_interrog": "interrogative pronoun", "part": "particle",
    "part_neg": "negative particle", "part_verb": "verbal particle",
    "part_interrog": "interrogative particle", "part_fut": "future particle",
    "part_voc": "vocative particle", "part_focus": "focus particle",
    "part_restrict": "restrictive particle",
}

FUNCTION_POS = {
    "prep", "conj", "conj_sub", "pron", "pron_dem", "pron_rel", "pron_interrog",
    "part", "part_neg", "part_verb", "part_interrog", "part_fut", "part_voc",
    "part_focus", "part_restrict", "adv_interrog", "adv_rel",
}


def undiac(text: str) -> str:
    return DIAC.sub("", unicodedata.normalize("NFC", text or "").replace("ـ", ""))


def normalize_front(text: str) -> str:
    return undiac(text).strip()


def canonical_key(text: str) -> str:
    return normalize_front(text).translate(CANON_TRANS)


def clean_gloss(text: str) -> str:
    g = (text or "").replace("_", " ").strip()
    g = re.sub(r"\+\[[^\]]+\]", "", g)
    g = re.sub(r"<[^>]+>", "", g)
    g = re.sub(r"\bthe\+", "", g, flags=re.I)
    g = re.sub(r"\+(?:he|she|it|they|them|his|her|their|you|I|we)(?:;\w+)*", "", g, flags=re.I)
    g = re.sub(r"\s*;\s*", "; ", g)
    g = re.sub(r"\s+", " ", g).strip(" ;,+")
    return g


def clean_root(text: str, pos: str) -> str:
    if pos in FUNCTION_POS:
        return ""
    letters = re.findall(r"[\u0621-\u063a\u0641-\u064a]", undiac(text or ""))
    if len(letters) not in (3, 4):
        return ""
    return " ".join(letters)


def sense_key(s: dict) -> tuple[str, str, str]:
    return s["pos"], s["gloss"].casefold(), s["root"]


def render_back(rank: int, group: dict) -> str:
    lines = [
        f"Rank: {rank}",
        f"Validated frequency: {group['frequency']}",
        "",
        "Meaning / grammatical senses:",
    ]
    for i, s in enumerate(group["senses"], start=1):
        label = POS_LABELS.get(s["pos"], s["pos"] or "lexical item")
        lines.append(f"{i}. {label}: {s['gloss']}")
        if s["pos"] in FUNCTION_POS:
            lines.append("   Root: — (closed-class/function word; no productive lexical root asserted)")
        elif s["root"]:
            lines.append(f"   Root: {s['root']}")
        else:
            lines.append("   Root: — (not safely established from CALIMA-MSA)")

    if len(group["spellings"]) > 1:
        alternatives = [x for x in group["spellings"] if x != group["front"]]
        if alternatives:
            lines += ["", "Orthographic variants encountered in source data: " + "، ".join(alternatives)]

    lines += [
        "",
        "Sources:",
        "- CAMeL Arabic Frequency Lists v1.0 — MSA frequency inventory",
        "- CALIMA-MSA r13 via CAMeL Tools — lemma, POS, sense and root validation",
        "",
        "Precision note: generated synonyms/examples/FR/UR translations are intentionally omitted unless independently verified.",
    ]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("audit/arabic_msa_core_candidates.csv"))
    ap.add_argument("--output", type=Path, default=Path("audit/arabic_top1000_precision_candidate.csv"))
    ap.add_argument("--report", type=Path, default=Path("audit/arabic_top1000_precision_report.txt"))
    ap.add_argument("--target", type=int, default=1000)
    args = ap.parse_args()

    with args.input.open(encoding="utf-8", newline="") as f:
        candidates = list(csv.DictReader(f))
    if len(candidates) < args.target:
        raise SystemExit(f"Need at least {args.target} validated candidates; got {len(candidates)}")

    # Group with exactly the same normalization used by the independent audit.
    # The display spelling remains the highest-frequency validated lemma spelling.
    groups: OrderedDict[str, dict] = OrderedDict()
    bad = []
    for row in candidates:
        front = normalize_front(row.get("lemma_undiac") or row.get("front") or "")
        if not front or not ARABIC_ONLY.fullmatch(front):
            bad.append((row.get("rank", "?"), front))
            continue
        try:
            frequency = int(row.get("frequency") or 0)
        except ValueError:
            frequency = 0
        pos = (row.get("pos") or "").strip()
        gloss = clean_gloss(row.get("english_gloss") or "")
        if not gloss:
            continue
        root = clean_root(row.get("root") or "", pos)
        key = canonical_key(front)

        if key not in groups:
            groups[key] = {"front": front, "frequency": 0, "senses": [], "spellings": []}
        g = groups[key]
        g["frequency"] += frequency
        if front not in g["spellings"]:
            g["spellings"].append(front)
        sense = {"pos": pos, "gloss": gloss, "root": root}
        existing = {sense_key(x) for x in g["senses"]}
        if sense_key(sense) not in existing:
            g["senses"].append(sense)

    ranked = list(groups.values())
    ranked = sorted(enumerate(ranked), key=lambda p: (-p[1]["frequency"], p[0]))
    selected = [g for _, g in ranked[: args.target]]

    problems = []
    keys = [canonical_key(g["front"]) for g in selected]
    if len(selected) != args.target:
        problems.append(f"expected {args.target} unique fronts; got {len(selected)}")
    if len(set(keys)) != len(selected):
        problems.append("duplicate canonical learner-facing fronts remain")
    for i, g in enumerate(selected, start=1):
        if not g["senses"]:
            problems.append(f"rank {i} {g['front']!r}: no validated sense")
        for s in g["senses"]:
            if s["pos"] in FUNCTION_POS and s["root"]:
                problems.append(f"rank {i} {g['front']!r}: function word retained a root")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Front", "Back"], lineterminator="\n")
        w.writeheader()
        for rank, group in enumerate(selected, start=1):
            w.writerow({"Front": group["front"], "Back": render_back(rank, group)})

    report_lines = [
        f"validated_candidates_read={len(candidates)}",
        f"unique_canonical_validated_fronts={len(groups)}",
        f"output_rows={len(selected)}",
        f"output_unique_canonical_fronts={len(set(keys))}",
        f"source_rows_skipped_bad_front={len(bad)}",
        f"validation_problems={len(problems)}",
        "ranking=aggregate CAMeL MSA frequency after CALIMA-MSA disambiguation; homographs/orthographic variants merged by canonical learner-facing front",
        "root_policy=closed-class/function words have no asserted productive root; lexical roots only when CALIMA-MSA supplies a valid 3/4-radical root",
        "enrichment_policy=no generated synonyms/examples/FR/UR translations in the precision core",
    ]
    if bad:
        report_lines.append("bad_front_samples=" + repr(bad[:20]))
    report_lines.extend(problems[:100])
    args.report.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(args.report.read_text(encoding="utf-8"))

    if problems:
        raise SystemExit("Precision candidate failed validation; see report")


if __name__ == "__main__":
    main()
