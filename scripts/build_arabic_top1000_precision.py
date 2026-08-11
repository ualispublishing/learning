#!/usr/bin/env python3
"""Build the precision-grade Arabic Top-1000 candidate.

The user's existing 1,000-item rank/order is immutable.
This script improves only the linguistic content of each ranked card.

Authority split:
- INVENTORY/RANK: existing audit/al_said_2023_msa1000.csv rank/order.
- MORPHOLOGY: CALIMA-MSA r13 via CAMeL Tools.

Precision principles:
- never reorder or substitute a ranked item merely because another item is more frequent;
- preserve hamza/alif/alif-maqsura distinctions;
- require lexical analyses to match the exact repaired Arabic spelling;
- prefer the source's published POS family;
- never invent a lexical root for closed-class/function words;
- omit uncertain claims rather than filling them with generated guesses.
"""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from collections import Counter
from pathlib import Path

DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
ARABIC_ONLY = re.compile(r"^[\u0621-\u064a]+$")
SENSE_SUFFIX = re.compile(r"_[0-9]+$")

# Clear extraction/OCR defects only. Rank is never changed.
SOURCE_REPAIRS = {
    42: "الآن",
    64: "خلال",
    73: "نحن",
    89: "أيضا",
    127: "مرحبا",
    136: "إلا",
    161: "كلا",
    236: "انظر",
    246: "مجموعة",
    249: "مختلف",
    281: "لأن",
    314: "أكبر",
    338: "إطلاقا",
    373: "خصوصا",
    395: "مالية",
    396: "علاقة",
    408: "اقتصادي",
    421: "موضوع",
    429: "اسمع",
    485: "معلومات",
    487: "نتيجة",
    533: "مستشفى",
    547: "ضرورة",
    555: "أشخاص",
    563: "إعلان",
    577: "علاقات",
    588: "إعلام",
    608: "شخصية",
    615: "أهمية",
    628: "أنتم",
    642: "جمهورية",
    672: "مباريات",
    686: "استمرار",
    694: "اجتماعي",
    697: "أجهزة",
    700: "لايزال",
    717: "ملابس",
    745: "تعامل",
    747: "إجراءات",
    757: "عسكرية",
    760: "اتصال",
    772: "أصحاب",
    774: "مسؤولية",
    777: "مسلمون",
    789: "يتصل",
    856: "مهرجان",
    865: "مؤخرا",
    867: "نظرة",
    876: "نجح",
    906: "ميلاد",
    927: "وفقا",
    932: "أولاد",
    963: "إصلاح",
    978: "مخدرات",
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
    "N": {"noun", "noun_num", "noun_quant", "adj_num", "pron_rel", "pron_interrog", "pron_dem"},
    "V": {"verb"},
    "ADJ": {"adj", "adj_comp"},
    "ADV": {"adv", "adv_interrog", "adv_rel", "noun"},
    "PRO": {"pron", "pron_dem", "pron_rel", "pron_interrog"},
    "P": {"prep", "conj", "conj_sub", "part", "part_neg", "part_verb", "part_interrog",
          "part_fut", "part_voc", "part_focus", "part_restrict", "pron_interrog", "adv"},
    "KH": {"adv", "part", "noun", "conj", "interj", "pron"},
}

FUNCTION_POS = {
    "prep", "conj", "conj_sub", "pron", "pron_dem", "pron_rel", "pron_interrog",
    "part", "part_neg", "part_verb", "part_interrog", "part_fut", "part_voc",
    "part_focus", "part_restrict", "adv_interrog", "adv_rel", "interj",
}
FORBIDDEN_ANALYZER_POS = {"abbrev", "foreign", "noun_prop", "verb_pseudo"}


def undiac(text: str) -> str:
    return DIAC.sub("", unicodedata.normalize("NFC", text or "").replace("ـ", ""))


def normalize_exact(text: str) -> str:
    return undiac(text).replace("+", "").replace("#", "").strip()


def clean_lemma(text: str) -> str:
    return normalize_exact(SENSE_SUFFIX.sub("", text or ""))


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


def exact_lexical_match(front: str, analysis: dict) -> bool:
    """Reject CALIMA analyses whose lexical lemma is a different Arabic spelling.

    This prevents bleed such as أن→إن/آن, على→علي, إلى→آلي, كان→كأن.
    For inflected verb forms, CALIMA's `diac` surface is also accepted when exact.
    """
    front_n = normalize_exact(front)
    lex_n = clean_lemma(str(analysis.get("lex", "")))
    diac_n = normalize_exact(str(analysis.get("diac", "")))
    return front_n == lex_n or front_n == diac_n


def select_senses(front: str, codes: list[str], analyzer, bw2ar) -> list[dict]:
    analyses = [a for a in analyzer.analyze(front) if exact_lexical_match(front, a)]
    senses: list[dict] = []
    seen = set()
    for code in codes:
        matches = [a for a in analyses if compatible(code, str(a.get("pos", "")))]
        matches.sort(key=score, reverse=True)
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
            # One best exact-spelling lexical reading per published POS category.
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
        f"- Existing Top-1000 inventory, rank {rank} — rank/order preserved exactly",
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
            problems.append(f"rank={rank}: invalid front after repair {raw_front!r} -> {front!r}")
            rows.append({"Front": front, "Back": ""}); fronts.append(front); continue
        senses = select_senses(front, codes, analyzer, bw2ar)
        if not senses:
            problems.append(f"rank={rank}: no exact-spelling CALIMA analysis compatible with published POS {codes!r}: {raw_front!r} -> {front!r}")
        rows.append({"Front": front, "Back": render_back(rank, front, raw_front, codes, senses) if senses else ""})
        fronts.append(front)

    counts = Counter(fronts)
    dupes = sorted(x for x, n in counts.items() if n > 1)
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
        "ranking_policy=preserve existing 1,000-item rank/order exactly; do not rerank",
        "morphology_authority=CALIMA-MSA r13 via CAMeL Tools",
        "orthography_policy=preserve distinct hamza/alif/alif-maqsura spellings; exact lexical spelling required",
        "root_policy=omit roots for closed-class/function words and unsafe analyses",
        *problems[:250],
    ]
    args.report.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(args.report.read_text(encoding="utf-8"))
    if problems:
        raise SystemExit("Precision candidate failed: review report")


if __name__ == "__main__":
    main()
