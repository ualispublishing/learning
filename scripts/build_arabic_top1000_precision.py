#!/usr/bin/env python3
"""Build the precision-grade arabic_top1000.csv candidate.

Inputs:
- Al-Said 2023 Table 4 rank inventory, reconciled for PDF extraction noise.
- CALIMA-MSA r13 morphology through CAMeL Tools.

Design rules:
- Front is Arabic script only and exactly one reconciled source form.
- Ranking comes only from Al-Said's published MSA list.
- Meanings, lemmas and roots come only from CAMeL analyses compatible with the paper POS.
- Homographs are represented as separate sense blocks on the back, never blended.
- Closed-class/function-word senses never receive invented derivational roots.
- No guessed synonyms, examples, etymologies, French or Urdu translations are emitted.
  Those may be added later only from independently verified bilingual sources.
"""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
AR_FRONT = re.compile(r"^[\u0621-\u064a]+$")
AR_LETTER = re.compile(r"[\u0621-\u063a\u0641-\u064a]")
SENSE_SUFFIX = re.compile(r"_[0-9]+$")

PAPER_POS_LABELS = {
    "N\\CN": "noun",
    "N\\CNU": "numeral / quantifying noun",
    "N\\DE": "demonstrative",
    "N\\RP": "relative/interrogative pronoun",
    "V\\VP": "perfect/past verb",
    "V\\VI": "imperfect/present verb",
    "V\\VR": "imperative verb",
    "P\\PRE": "preposition",
    "P\\PO": "particle",
    "P\\CO": "conjunction",
    "P\\QU": "interrogative particle",
    "P\\EX": "exceptive/restrictive particle",
    "ADJ": "adjective",
    "ADV": "adverb",
    "PRO": "pronoun",
    "KH": "other function word",
}

CAMEL_ALLOWED = {
    "N": {"noun", "noun_num", "noun_quant", "adj_num"},
    "V": {"verb"},
    "ADJ": {"adj", "adj_comp"},
    "ADV": {"adv", "adv_interrog", "adv_rel"},
    "PRO": {"pron", "pron_dem", "pron_rel", "pron_interrog"},
    "P": {"prep", "conj", "conj_sub", "part", "part_neg", "part_verb", "part_interrog", "part_fut", "part_voc", "part_focus", "part_restrict", "pron_interrog"},
    "KH": {"adv", "part", "noun", "conj"},
}

FUNCTION_POS = {
    "prep", "conj", "conj_sub", "pron", "pron_dem", "pron_rel", "pron_interrog",
    "part", "part_neg", "part_verb", "part_interrog", "part_fut", "part_voc",
    "part_focus", "part_restrict", "adv_interrog", "adv_rel",
}


def undiac(s: str) -> str:
    return DIAC.sub("", unicodedata.normalize("NFC", s or "").replace("ـ", ""))


def clean_lemma(s: str) -> str:
    return SENSE_SUFFIX.sub("", (s or "")).replace("+", "").replace("#", "").strip()


def source_family(code: str) -> str:
    c = code.strip()
    if c.startswith("N\\"): return "N"
    if c.startswith("V\\"): return "V"
    if c.startswith("P\\"): return "P"
    if c in {"ADJ", "ADV", "PRO", "KH"}: return c
    return ""


def compatible(code: str, camel_pos: str) -> bool:
    fam = source_family(code)
    return bool(fam and camel_pos in CAMEL_ALLOWED.get(fam, set()))


def number(v, default=-99.0):
    try: return float(v)
    except (TypeError, ValueError): return default


def clean_gloss(gloss: str) -> str:
    g = (gloss or "").replace("_", " ").strip()
    # Remove analyzer inflection notes while preserving lexical glosses.
    g = re.sub(r"\+\[[^\]]+\]", "", g)
    g = re.sub(r"<[^>]+>", "", g)
    g = re.sub(r"\+(?:he|she|it|they|them|his|her|their|you|I|we)(?:;\w+)*", "", g, flags=re.I)
    g = re.sub(r"\bthe\+", "", g, flags=re.I)
    g = re.sub(r"\s+", " ", g).strip(" ;,+")
    return g


def normalize_root(value: str, camel_pos: str) -> str:
    if camel_pos in FUNCTION_POS:
        return ""
    letters = AR_LETTER.findall(undiac(value or ""))
    if len(letters) not in (3, 4):
        return ""
    return " ".join(letters)


def paper_codes(s: str) -> list[str]:
    out = []
    for x in (s or "").split("|"):
        x = x.strip()
        if x and x not in out:
            out.append(x)
    return out


def analysis_key(a: dict, code: str):
    pos = str(a.get("pos", ""))
    lemma = undiac(clean_lemma(str(a.get("lex", ""))))
    root = normalize_root(str(a.get("root", "")), pos)
    gloss = clean_gloss(str(a.get("gloss", "")))
    return code, pos, lemma, root, gloss


def select_senses(analyses: list[dict], codes: list[str]):
    senses = []
    for code in codes:
        compatible_analyses = [a for a in analyses if compatible(code, str(a.get("pos", "")))]
        if not compatible_analyses:
            continue
        compatible_analyses.sort(key=lambda a: (number(a.get("pos_lex_logprob")), number(a.get("lex_logprob"))), reverse=True)

        # Distinct lexical analyses, not case/inflection duplicates. Keep at most three
        # meanings for one published POS code, which is enough for the common homographs
        # without turning the back into an analyzer dump.
        seen = set()
        chosen = []
        for a in compatible_analyses:
            k = analysis_key(a, code)
            if not k[-1]:
                continue
            lexical = k[1:]  # pos, lemma, root, gloss
            if lexical in seen:
                continue
            seen.add(lexical)
            chosen.append(a)
            if len(chosen) >= 3:
                break
        for a in chosen:
            pos = str(a.get("pos", ""))
            lemma = undiac(clean_lemma(str(a.get("lex", ""))))
            root = normalize_root(str(a.get("root", "")), pos)
            gloss = clean_gloss(str(a.get("gloss", "")))
            senses.append({
                "paper_code": code,
                "paper_label": PAPER_POS_LABELS.get(code, code),
                "camel_pos": pos,
                "lemma": lemma,
                "root": root,
                "gloss": gloss,
            })
    return senses


def render_back(rank: int, front: str, codes: list[str], senses: list[dict]) -> str:
    lines = [f"Rank: {rank}", "", "Meaning / grammatical senses:"]
    for i, s in enumerate(senses, start=1):
        lines.append(f"{i}. {s['paper_label']}: {s['gloss']}")
        if s["lemma"] and s["lemma"] != front:
            lines.append(f"   Lemma: {s['lemma']}")
        if s["camel_pos"] in FUNCTION_POS:
            lines.append("   Root: — (function word; no productive lexical root)")
        elif s["root"]:
            lines.append(f"   Root: {s['root']}")
        else:
            lines.append("   Root: — (not safely established)")
    lines += [
        "",
        "Published POS: " + " / ".join(PAPER_POS_LABELS.get(c, c) for c in codes),
        "",
        "Sources:",
        f"- Al-Said (2023), Table 4, rank {rank} — MSA frequency inventory",
        "- CALIMA-MSA r13 morphology via CAMeL Tools — sense/POS/root validation",
    ]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("audit/arabic_msa1000_reconciled.csv"))
    ap.add_argument("--output", type=Path, default=Path("audit/arabic_top1000_precision_candidate.csv"))
    ap.add_argument("--report", type=Path, default=Path("audit/arabic_top1000_precision_report.txt"))
    args = ap.parse_args()

    from camel_tools.morphology.analyzer import Analyzer
    from camel_tools.morphology.database import MorphologyDB

    db = MorphologyDB.builtin_db("calima-msa-r13", flags="a")
    analyzer = Analyzer(db, backoff="NONE", cache_size=10000)

    with args.input.open(encoding="utf-8", newline="") as f:
        src = list(csv.DictReader(f))

    rows = []
    problems = []
    seen_fronts = set()
    sense_counts = []
    for r in src:
        rank = int(r["rank"])
        front = undiac(r["front"]).strip()
        codes = paper_codes(r["paper_pos"])

        if r.get("confidence") == "unresolved":
            problems.append(f"rank={rank}: reconciliation unresolved")
        if not AR_FRONT.fullmatch(front):
            problems.append(f"rank={rank}: front is not Arabic-script-only: {front!r}")
        if front in seen_fronts:
            problems.append(f"rank={rank}: duplicate front {front!r}")
        seen_fronts.add(front)

        analyses = analyzer.analyze(front)
        senses = select_senses(analyses, codes)
        if not senses:
            problems.append(f"rank={rank}: no CAMeL analysis compatible with paper POS {codes!r} for {front!r}")
            continue
        sense_counts.append(len(senses))
        back = render_back(rank, front, codes, senses)
        rows.append({"Front": front, "Back": back})

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Front", "Back"], lineterminator="\n")
        w.writeheader(); w.writerows(rows)

    report = [
        f"input_rows={len(src)}",
        f"output_rows={len(rows)}",
        f"unique_fronts={len({r['Front'] for r in rows})}",
        f"min_senses={min(sense_counts) if sense_counts else 0}",
        f"max_senses={max(sense_counts) if sense_counts else 0}",
        f"problems={len(problems)}",
        *problems[:200],
    ]
    args.report.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(args.report.read_text(encoding="utf-8"))

    if len(src) != 1000 or len(rows) != 1000 or len(seen_fronts) != 1000 or problems:
        raise SystemExit("Precision candidate failed validation; see report")


if __name__ == "__main__":
    main()
