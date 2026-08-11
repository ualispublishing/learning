#!/usr/bin/env python3
"""Build the precision-grade Arabic Top-1000 candidate.

Authority split:
- INVENTORY/RANK: Al-Said (2023), Table 4: 1,000 undiacritized MSA common words.
- MORPHOLOGY: CALIMA-MSA r13 via CAMeL Tools.

The script never substitutes a merely similar high-frequency word for the published item.
A small explicit repair table fixes only clear PDF-extraction/OCR artifacts. Every final
front must remain one Arabic-script word. Distinct spellings (including hamza/alif and
alif-maqsura distinctions) are NEVER collapsed.
"""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from pathlib import Path

DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
ARABIC_ONLY = re.compile(r"^[\u0621-\u064a]+$")
SENSE_SUFFIX = re.compile(r"_[0-9]+$")

# Clear extraction defects visible in the source table.  Keep this deliberately small:
# uncertain rows must fail validation rather than receive a guessed replacement.
SOURCE_REPAIRS = {
    42: "الآن",       # اآلن
    73: "نحن",        # حن
    89: "أيضا",       # أياض
    161: "كلا",       # source typography represents كَلّا / كِلا
    249: "مختلف",     # مختفل
    408: "اقتصادي",   # اقتصاد/ي
    429: "اسمع",      # اسعم
    694: "اجتماعي",   # اجتماع/ي
    697: "أجهزة",     # أجةزه
    717: "ملابس",     # مالبس
    789: "يتصل",      # يتلص
    865: "مؤخرا",     # مؤخار
    867: "نظرة",      # ظرة
    876: "نجح",       # جح
    927: "وفقا",      # وفقا/ل -> lexical head وفقًا; لِـ is a clitic/preposition
    963: "إصلاح",     # إصالح
}

PAPER_POS_LABELS = {
    "N\\CN": "noun", "N\\CNU": "numeral / quantifying noun",
    "N\\DE": "demonstrative", "N\\RP": "relative/interrogative pronoun",
    "V\\VP": "perfect/past verb", "V\\VI": "imperfect/present verb",
    "V\\VR": "imperative verb", "P\\PRE": "preposition",
    "P\\PO": "particle", "P\\CO": "conjunction", "P\\QU": "interrogative particle",
    "P\\EX": "exceptive/restrictive particle", "ADJ": "adjective",
    "ADV": "adverb", "PRO": "pronoun", "KH": "other function word",
}

CAMEL_ALLOWED = {
    "N": {"noun", "noun_num", "noun_quant", "adj_num", "pron_rel", "pron_interrog"},
    "V": {"verb"},
    "ADJ": {"adj", "adj_comp"},
    "ADV": {"adv", "adv_interrog", "adv_rel", "noun"},
    "PRO": {"pron", "pron_dem", "pron_rel", "pron_interrog"},
    "P": {"prep", "conj", "conj_sub", "part", "part_neg", "part_verb", "part_interrog",
          "part_fut", "part_voc", "part_focus", "part_restrict", "pron_interrog"},
    "KH": {"adv", "part", "noun", "conj", "interj"},
}

FUNCTION_POS = {
    "prep", "conj", "conj_sub", "pron", "pron_dem", "pron_rel", "pron_interrog",
    "part", "part_neg", "part_verb", "part_interrog", "part_fut", "part_voc",
    "part_focus", "part_restrict", "adv_interrog", "adv_rel", "interj",
}
FORBIDDEN_ANALYZER_POS = {"abbrev", "foreign", "noun_prop", "verb_pseudo"}


def undiac(text: str) -> str:
    return DIAC.sub("", unicodedata.normalize("NFC", text or "").replace("ـ", ""))


def clean_lemma(text: str) -> str:
    return undiac(SENSE_SUFFIX.sub("", (text or ""))).replace("+", "").replace("#", "").strip()


def paper_codes(text: str) -> list[str]:
    return [x.strip() for x in (text or "").split("|") if x.strip()]


def family(code: str) -> str:
    if code.startswith("N\\"): return "N"
    if code.startswith("V\\"): return "V"
    if code.startswith("P\\"): return "P"
    return code if code in {"ADJ", "ADV", "PRO", "KH"} else ""


def compatible(code: str, pos: str) -> bool:
    return pos not in FORBIDDEN_ANALYZER_POS and pos in CAMEL_ALLOWED.get(family(code), set())


def score(a: dict) -> tuple[float, float]:
    def num(value: object) -> float:
        try: return float(value)
        except (TypeError, ValueError): return -99.0
    return num(a.get("pos_lex_logprob")), num(a.get("lex_logprob"))


def clean_gloss(text: str) -> str:
    g = (text or "").replace("_", " ").strip()
    g = re.sub(r"\+\[[^\]]+\]", "", g)
    g = re.sub(r"\[[^\]]+\]", "", g)
    g = re.sub(r"<[^>]+>", "", g)
    g = re.sub(r"\bthe\+", "", g, flags=re.I)
    g = re.sub(r"\s+", " ", g).strip(" ;,+")
    return g


def root_to_arabic(raw: str, pos: str, bw2ar) -> str:
    if pos in FUNCTION_POS or not raw or raw in {"0", "na", "#", "-"}:
        return ""
    converted = bw2ar(raw)
    letters = re.findall(r"[\u0621-\u063a\u0641-\u064a]", undiac(converted))
    if len(letters) not in (3, 4):
        return ""
    return " ".join(letters)


def select_senses(front: str, codes: list[str], analyzer, bw2ar) -> list[dict]:
    analyses = analyzer.analyze(front)
    senses: list[dict] = []
    seen = set()
    for code in codes:
        matches = [a for a in analyses if compatible(code, str(a.get("pos", "")))]
        matches.sort(key=score, reverse=True)
        # Keep distinct lexical interpretations for the POS supplied by the paper.
        for a in matches:
            pos = str(a.get("pos", ""))
            gloss = clean_gloss(str(a.get("gloss", "")))
            if not gloss:
                continue
            lemma = clean_lemma(str(a.get("lex", "")))
            root = root_to_arabic(str(a.get("root", "")), pos, bw2ar)
            key = (code, pos, lemma, root, gloss.casefold())
            if key in seen:
                continue
            seen.add(key)
            senses.append({
                "paper_code": code,
                "paper_label": PAPER_POS_LABELS.get(code, code),
                "pos": pos,
                "lemma": lemma,
                "root": root,
                "gloss": gloss,
            })
            # At most two lexical readings for a single published POS category.
            if sum(1 for x in senses if x["paper_code"] == code) >= 2:
                break
    return senses


def render_back(rank: int, front: str, raw_front: str, codes: list[str], senses: list[dict]) -> str:
    lines = [f"Rank: {rank}", "", "Meaning / grammatical senses:"]
    for i, s in enumerate(senses, 1):
        lines.append(f"{i}. {s['paper_label']}: {s['gloss']}")
        if s["lemma"] and s["lemma"] != front:
            lines.append(f"   Lemma: {s['lemma']}")
        if s["pos"] in FUNCTION_POS:
            lines.append("   Root: — (closed-class/function word; no productive lexical root asserted)")
        elif s["root"]:
            lines.append(f"   Root: {s['root']}")
        else:
            lines.append("   Root: — (not safely established from CALIMA-MSA)")
    lines += ["", "Published POS: " + " / ".join(PAPER_POS_LABELS.get(c, c) for c in codes)]
    if raw_front.strip() != front:
        lines.append(f"Source extraction repaired: {raw_front.strip()} → {front}")
    lines += [
        "", "Sources:",
        f"- Al-Said (2023), Table 4, rank {rank} — learner-oriented MSA common-word inventory",
        "- CALIMA-MSA r13 via CAMeL Tools — morphology, POS, lexical sense and root validation",
        "", "Precision note: no synonym, example, French, or Urdu claim is included unless independently verified.",
    ]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("audit/al_said_2023_msa1000.csv"))
    ap.add_argument("--output", type=Path, default=Path("audit/arabic_top1000_precision_candidate.csv"))
    ap.add_argument("--report", type=Path, default=Path("audit/arabic_top1000_precision_report.txt"))
    args = ap.parse_args()

    from camel_tools.morphology.analyzer import Analyzer
    from camel_tools.morphology.database import MorphologyDB
    from camel_tools.utils.charmap import CharMapper

    db = MorphologyDB.builtin_db("calima-msa-r13", flags="a")
    analyzer = Analyzer(db, backoff="NONE", cache_size=10000)
    bw2ar = CharMapper.builtin_mapper("bw2ar")

    with args.input.open(encoding="utf-8", newline="") as f:
        src = list(csv.DictReader(f))

    rows = []
    problems = []
    fronts = []
    for r in src:
        rank = int(r["rank"])
        raw_front = r["front"]
        front = SOURCE_REPAIRS.get(rank, undiac(raw_front).strip())
        codes = paper_codes(r["pos_codes"])
        if rank != len(rows) + 1:
            problems.append(f"rank sequence mismatch at source rank {rank}")
        if not ARABIC_ONLY.fullmatch(front):
            problems.append(f"rank={rank}: non-single-word/non-Arabic front {raw_front!r} -> {front!r}")
            rows.append({"Front": front, "Back": ""}); fronts.append(front); continue
        senses = select_senses(front, codes, analyzer, bw2ar)
        if not senses:
            problems.append(f"rank={rank}: no CALIMA analysis compatible with published POS {codes!r}: {raw_front!r} -> {front!r}")
        rows.append({"Front": front, "Back": render_back(rank, front, raw_front, codes, senses) if senses else ""})
        fronts.append(front)

    dupes = sorted({x for x in fronts if fronts.count(x) > 1})
    if dupes:
        problems.append("duplicate exact fronts: " + repr(dupes))
    if len(src) != 1000:
        problems.append(f"source row count is {len(src)}, expected 1000")
    if len(rows) != 1000:
        problems.append(f"output row count is {len(rows)}, expected 1000")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Front", "Back"], lineterminator="\n")
        w.writeheader(); w.writerows(rows)

    report = [
        f"source_rows={len(src)}",
        f"output_rows={len(rows)}",
        f"unique_exact_fronts={len(set(fronts))}",
        f"explicit_source_repairs={sum(1 for r in src if int(r['rank']) in SOURCE_REPAIRS)}",
        f"problems={len(problems)}",
        "ranking_authority=Al-Said 2023 Table 4; rank is never inferred from morphology",
        "morphology_authority=CALIMA-MSA r13 via CAMeL Tools",
        "orthography_policy=preserve distinct hamza/alif/alif-maqsura spellings; only remove diacritics/tatweel",
        "root_policy=convert CALIMA Buckwalter roots to Arabic; omit roots for closed-class/function words or unsafe analyses",
        *problems[:250],
    ]
    args.report.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(args.report.read_text(encoding="utf-8"))
    if problems:
        raise SystemExit("Precision candidate failed: review report")


if __name__ == "__main__":
    main()
