#!/usr/bin/env python3
"""Finalize the existing Arabic Top-1000 deck without changing its rank/order.

This is the human-resolution layer over build_arabic_top1000_precision.py.
The 1,000 source rows and their ranks are immutable. We only repair clear source
extraction defects and supply conservative manual analyses where CALIMA-MSA cannot
reliably express the intended high-frequency MSA item/POS.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

import build_arabic_top1000_precision as base

# Repairs are source-text/OCR/RTL extraction corrections only. Rank is unchanged.
FINAL_REPAIRS = {
    **base.SOURCE_REPAIRS,
    45: "نعم",
    267: "نحو",
    270: "نوع",
    361: "اذهب",
    368: "انتخابات",
    381: "بلاد",
    500: "كلام",
    550: "نتائج",
    660: "نجاح",
    673: "لاحق",
    696: "أسهم",
    760: "اتصالات",
    770: "أسرع",
    785: "نفط",
    793: "أسفل",
    798: "نوم",
    852: "علاج",
    873: "أوسط",
}

# Same unvocalized spelling appears at two intentional ranks with different functions.
ALLOWED_DUPLICATES = {"ما": {10, 347}}


def sense(label: str, pos: str, gloss: str, root: str = "", lemma: str = "") -> dict:
    return {
        "paper_label": label,
        "pos": pos,
        "gloss": gloss,
        "root": root,
        "lemma": lemma,
    }


# Human-resolved rows. These are intentionally conservative: no speculative synonyms,
# translations, etymologies or examples are added. Roots are omitted where uncertain or
# where the entry functions as a closed-class item/expression.
MANUAL_SENSES = {
    15: [sense("adverb / preposition", "prep", "with; together with")],
    45: [sense("particle", "part", "yes; indeed")],
    50: [sense("noun", "noun", "master; gentleman; Mr.", "س و د")],
    62: [sense("particle", "part", "yes; indeed; certainly")],
    64: [sense("adverb", "adv", "during; throughout; through", "خ ل ل")],
    72: [sense("interrogative particle", "adv_interrog", "how")],
    74: [sense("numeral / quantifying noun", "adj_num", "first; foremost", "أ و ل")],
    81: [sense("noun / comparative", "adj_comp", "more; most", "ك ث ر")],
    88: [sense("adjective", "adj", "many; much; numerous", "ك ث ر")],
    102: [sense("adverb / conjunction", "adv_rel", "where; whereupon; in which")],
    104: [sense("adverb / preposition", "prep", "since; for (a period); ago")],
    106: [sense("interrogative particle", "adv_interrog", "where")],
    109: [sense("other function word", "interj", "come on; let's go")],
    116: [sense("noun / comparative", "adj_comp", "better; best; preferable", "ف ض ل")],
    127: [sense("noun / greeting expression", "noun", "hello; welcome", "ر ح ب")],
    161: [
        sense("particle", "part", "no; indeed not (كَلَّا)"),
        sense("quantifier", "noun_quant", "both, masculine form (كِلَا)"),
    ],
    172: [sense("adjective", "adj", "small; little; young", "ص غ ر")],
    204: [sense("proper noun", "noun_prop", "Allah; God")],
    209: [sense("noun", "noun", "women; plural of نِسْوَة")],
    219: [sense("adjective", "adj", "beautiful; nice; fine", "ج م ل")],
    236: [sense("imperative verb", "verb", "look!; see!", "ن ظ ر")],
    249: [sense("adjective / noun", "adj", "different; various; differing", "خ ل ف")],
    267: [sense("adverb / preposition", "adv", "toward; about; approximately", "ن ح و")],
    269: [sense("fixed expression", "part", "necessarily; must; inevitably (standard phrase: لا بُدَّ)")],
    270: [sense("noun", "noun", "type; kind; sort", "ن و ع")],
    292: [sense("particle", "part", "attention/emphasis particle; also unvocalized form of أَلَّا 'that not'")],
    299: [sense("relative expression", "pron_rel", "from/of what; from/of which (مِن + ما)")],
    314: [sense("noun / comparative", "adj_comp", "bigger; greater; biggest; greatest", "ك ب ر")],
    326: [sense("demonstrative expression", "pron_dem", "like this; thus; in this way")],
    346: [sense("noun / comparative", "adj_comp", "higher; highest; upper", "ع ل و")],
    347: [sense("adverb / exclamative particle", "part", "how ...!; what a ...! in exclamation")],
    353: [sense("demonstrative", "pron_dem", "these")],
    361: [sense("imperative verb", "verb", "go!", "ذ ه ب")],
    381: [sense("noun", "noun", "lands; countries", "ب ل د")],
    389: [sense("adjective", "adj", "Islamic", "س ل م")],
    429: [sense("imperative verb", "verb", "listen!; hear!", "س م ع")],
    459: [sense("noun / quantifier", "noun_quant", "many; numerous; a number of", "ع د د")],
    460: [sense("particle", "part", "as if; as though")],
    500: [sense("noun", "noun", "speech; talk; words", "ك ل م")],
    503: [sense("adverb", "adv", "throughout; during; all through", "ط و ل")],
    550: [sense("noun", "noun", "results; outcomes", "ن ت ج")],
    568: [sense("adjective", "adj", "honest; trustworthy; faithful; reliable", "أ م ن")],
    604: [sense("adjective", "adj", "bad; poor; evil", "س و أ")],
    626: [sense("adverb", "adv", "together")],
    634: [sense("exceptive/restrictive particle", "part_restrict", "except; other than; apart from")],
    648: [sense("adjective", "adj", "sure; certain; confident", "أ ك د")],
    660: [sense("noun", "noun", "success", "ن ج ح")],
    673: [
        sense("adjective", "adj", "subsequent; later; following", "ل ح ق"),
        sense("perfect/past verb", "verb", "pursued; followed; caught up with", "ل ح ق"),
    ],
    696: [
        sense("noun", "noun", "shares; stocks", "س ه م"),
        sense("perfect/past verb", "verb", "contributed; participated", "س ه م"),
    ],
    710: [sense("adverb / conjunction", "conj", "when; since; as; because, according to context")],
    770: [
        sense("comparative", "adj_comp", "faster; fastest", "س ر ع"),
        sense("perfect/past verb", "verb", "hurried; sped up", "س ر ع"),
    ],
    785: [sense("noun", "noun", "oil; petroleum", "ن ف ط")],
    793: [sense("noun / adverb", "noun", "bottom; lower part; below", "س ف ل")],
    798: [sense("noun", "noun", "sleep", "ن و م")],
    852: [sense("noun", "noun", "treatment; therapy; remedy", "ع ل ج")],
    873: [sense("noun / comparative", "adj_comp", "middle; central; intermediate", "و س ط")],
    878: [sense("adjective", "adj", "bad; evil; poor, feminine singular", "س و أ")],
    898: [sense("adjective", "adj", "dead", "م و ت")],
    907: [sense("particle", "part_restrict", "only; merely; nothing but")],
    924: [sense("imperative verb", "verb", "do!", "ف ع ل")],
    927: [sense("noun used adverbially", "noun", "according to; in accordance with (commonly وَفْقًا لِـ)", "و ف ق")],
}

# Additional rows where the published POS is coarse or CALIMA's exact analysis is known
# to miss the ordinary learner sense. These prevent tool limitations from becoming blank
# or misleading cards.
MANUAL_SENSES.update({
    269: MANUAL_SENSES[269],
    700: [sense("imperfect/present verb expression", "verb", "still is; continues to be (standard spacing: لا يزال)", "ز و ل")],
})


def render_manual_back(rank: int, front: str, raw_front: str, codes: list[str], senses: list[dict]) -> str:
    lines = [f"Rank: {rank}", "", "Meaning / grammatical senses:"]
    for i, s in enumerate(senses, 1):
        lines.append(f"{i}. {s['paper_label']}: {s['gloss']}")
        if s.get("lemma") and s["lemma"] != front:
            lines.append(f"   Lemma: {s['lemma']}")
        if s["pos"] in base.FUNCTION_POS or not s.get("root"):
            lines.append("   Root: — (closed-class/function word or no safe productive lexical root asserted)")
        else:
            lines.append(f"   Root: {s['root']}")
    lines += ["", "Published POS: " + " / ".join(base.PAPER_POS_LABELS.get(c, c) for c in codes)]
    if raw_front.strip() != front:
        lines.append(f"Source extraction repaired: {raw_front.strip()} → {front}")
    lines += [
        "", "Sources:",
        f"- Existing Top-1000 inventory, rank {rank} — rank/order preserved exactly",
        "- CALIMA-MSA r13 via CAMeL Tools — automated morphology cross-check",
        "- Human precision review — ordinary MSA lexical/POS resolution for analyzer or extraction exceptions",
        "", "Precision note: uncertain generated synonyms, examples and cross-language translations are not asserted.",
    ]
    return "\n".join(lines)


def allowed_duplicate_groups(fronts: list[str]) -> tuple[bool, list[str]]:
    counts = Counter(fronts)
    unexpected = []
    for word, n in counts.items():
        if n <= 1:
            continue
        ranks = {i for i, f in enumerate(fronts, 1) if f == word}
        if ALLOWED_DUPLICATES.get(word) != ranks:
            unexpected.append(f"{word}:{sorted(ranks)}")
    return not unexpected, unexpected


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

    rows: list[dict] = []
    problems: list[str] = []
    fronts: list[str] = []
    automatic = 0
    manual = 0

    for r in src:
        rank = int(r["rank"])
        raw_front = r["front"]
        front = FINAL_REPAIRS.get(rank, base.undiac(raw_front).strip())
        codes = base.paper_codes(r["pos_codes"])

        if rank != len(rows) + 1:
            problems.append(f"rank sequence mismatch at source rank {rank}")
        if not base.ARABIC_ONLY.fullmatch(front):
            problems.append(f"rank={rank}: invalid Arabic front after repair {raw_front!r} -> {front!r}")
            rows.append({"Front": front, "Back": ""})
            fronts.append(front)
            continue

        if rank in MANUAL_SENSES:
            senses = MANUAL_SENSES[rank]
            back = render_manual_back(rank, front, raw_front, codes, senses)
            manual += 1
        else:
            senses = base.select_senses(front, codes, analyzer, bw2ar)
            if not senses:
                problems.append(
                    f"rank={rank}: unresolved after exact CALIMA + human exception pass: "
                    f"{raw_front!r} -> {front!r}, POS={codes!r}"
                )
                back = ""
            else:
                back = base.render_back(rank, front, raw_front, codes, senses)
                automatic += 1

        rows.append({"Front": front, "Back": back})
        fronts.append(front)

    ok_dupes, bad_dupes = allowed_duplicate_groups(fronts)
    if not ok_dupes:
        problems.extend("unexpected duplicate front " + x for x in bad_dupes)
    if len(src) != 1000 or len(rows) != 1000:
        problems.append(f"row count source={len(src)} output={len(rows)}; expected 1000/1000")
    if any(not r["Back"].strip() for r in rows):
        problems.append("one or more rows have an empty learner-facing Back")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Front", "Back"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    report = [
        f"source_rows={len(src)}",
        f"output_rows={len(rows)}",
        f"automatic_exact_rows={automatic}",
        f"human_resolved_rows={manual}",
        f"source_repairs={sum(1 for r in src if int(r['rank']) in FINAL_REPAIRS)}",
        f"distinct_front_spellings={len(set(fronts))}",
        "intentional_duplicate=ما at ranks 10 and 347 (different grammatical functions)",
        f"problems={len(problems)}",
        "ranking_policy=preserve the existing 1,000 ranks exactly; no reranking",
        "precision_policy=exact CALIMA-MSA analysis where reliable; explicit human resolution for extraction/analyzer exceptions",
        *problems,
    ]
    args.report.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(args.report.read_text(encoding="utf-8"))
    if problems:
        raise SystemExit("Arabic Top-1000 finalization still has unresolved precision problems")


if __name__ == "__main__":
    main()
