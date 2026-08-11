#!/usr/bin/env python3
"""Reconcile PDF-extracted Al-Said 2023 MSA-1000 fronts with a CAMeL validation lexicon.

The paper remains the ranking authority. CAMeL is used only to repair extraction noise and
validate lexical plausibility. Repairs are conservative:
- exact published-source overrides for rows whose PDF text is independently readable;
- concatenate split fragments when the concatenation is attested;
- otherwise fuzzy-repair only malformed/non-attested fronts when a same-POS candidate is
  uniquely better within a small Damerau-Levenshtein radius;
- preserve valid source homographs and surface forms instead of lemmatizing the list.

Outputs an audit CSV plus an unresolved list. The final deck builder must fail if any row
remains unresolved.
"""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
AR_ONLY = re.compile(r"^[\u0621-\u064a]+$")

# Source-backed corrections for PDF text-extraction artifacts. These ranks are legible in
# the official paper text (Table 4) and are not inferred from CAMeL.
SOURCE_OVERRIDES = {
    42: "الآن",
    45: "نعم",
    73: "نحن",
    347: "بينما",
    550: "نتائج",
    615: "أهمية",
    628: "أنتم",
    660: "نجاح",
    785: "نفط",
    789: "يتصل",
    793: "أسفل",
    798: "نوم",
}

POS_MAP = {
    "N": {"noun", "noun_num", "noun_prop", "noun_quant"},
    "V": {"verb"},
    "ADJ": {"adj", "adj_comp"},
    "ADV": {"adv", "adv_interrog", "adv_rel"},
    "PRO": {"pron", "pron_dem", "pron_rel", "pron_interrog"},
    "P": {"prep", "conj", "conj_sub", "part", "part_neg", "part_verb", "part_interrog", "part_fut", "part_voc", "part_focus", "part_restrict", "pron_interrog"},
    "KH": {"adv", "part", "noun"},
}


def undiac(s: str) -> str:
    return DIAC.sub("", unicodedata.normalize("NFC", s or "").replace("ـ", ""))


def norm(s: str) -> str:
    return undiac(s).strip().replace(" ", "")


def pos_families(source_codes: str) -> set[str]:
    fam = set()
    for code in (source_codes or "").split("|"):
        c = code.strip()
        if not c:
            continue
        if c.startswith("N\\"):
            fam |= POS_MAP["N"]
        elif c.startswith("V\\"):
            fam |= POS_MAP["V"]
        elif c.startswith("P\\"):
            fam |= POS_MAP["P"]
        elif c == "ADJ":
            fam |= POS_MAP["ADJ"]
        elif c == "ADV":
            fam |= POS_MAP["ADV"]
        elif c == "PRO":
            fam |= POS_MAP["PRO"]
        elif c == "KH":
            fam |= POS_MAP["KH"]
    return fam


def damerau(a: str, b: str) -> int:
    """Optimal-string-alignment Damerau-Levenshtein distance."""
    a, b = norm(a), norm(b)
    da = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1): da[i][0] = i
    for j in range(len(b) + 1): da[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i-1] == b[j-1] else 1
            da[i][j] = min(da[i-1][j] + 1, da[i][j-1] + 1, da[i-1][j-1] + cost)
            if i > 1 and j > 1 and a[i-1] == b[j-2] and a[i-2] == b[j-1]:
                da[i][j] = min(da[i][j], da[i-2][j-2] + cost)
    return da[-1][-1]


def parse_surface_field(field: str):
    for item in (field or "").split("|"):
        item = item.strip()
        if not item:
            continue
        if ":" in item:
            surface, count = item.rsplit(":", 1)
            try: freq = int(count)
            except ValueError: freq = 0
        else:
            surface, freq = item, 0
        surface = norm(surface)
        if surface and AR_ONLY.fullmatch(surface):
            yield surface, freq


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=Path("audit/al_said_2023_msa1000.csv"))
    ap.add_argument("--lexicon", type=Path, default=Path("audit/arabic_msa_core_candidates.csv"))
    ap.add_argument("--output", type=Path, default=Path("audit/arabic_msa1000_reconciled.csv"))
    ap.add_argument("--summary", type=Path, default=Path("audit/arabic_msa1000_reconciliation_summary.txt"))
    args = ap.parse_args()

    with args.source.open(encoding="utf-8", newline="") as f:
        source_rows = list(csv.DictReader(f))
    with args.lexicon.open(encoding="utf-8", newline="") as f:
        lex_rows = list(csv.DictReader(f))

    # Surface lexicon: exact surface -> candidate metadata list. Include both lemma spelling
    # and the frequent observed surface forms retained by the CAMeL frequency builder.
    lex = defaultdict(list)
    for r in lex_rows:
        pos = r.get("pos", "")
        freq = int(r.get("frequency") or 0)
        lemma = norm(r.get("lemma_undiac") or r.get("front") or "")
        forms = [(lemma, freq)] if lemma and AR_ONLY.fullmatch(lemma) else []
        forms.extend(parse_surface_field(r.get("top_surfaces", "")))
        seen = set()
        for form, surface_freq in forms:
            if form in seen: continue
            seen.add(form)
            lex[form].append({
                "form": form, "pos": pos, "root": r.get("root", ""),
                "gloss": r.get("english_gloss", ""),
                "lexeme_frequency": freq, "surface_frequency": surface_freq,
                "lemma": lemma,
            })

    all_forms = list(lex)
    output = []
    counts = defaultdict(int)
    unresolved = []

    for row in source_rows:
        rank = int(row["rank"])
        raw_front = norm(row.get("front", ""))
        pos_codes = row.get("pos_codes", "")
        allowed = pos_families(pos_codes)
        method = "exact"
        confidence = "high"
        final = raw_front
        note = ""

        if rank in SOURCE_OVERRIDES:
            final = SOURCE_OVERRIDES[rank]
            method = "source_override"
            note = "Official Table 4 text resolves PDF extraction artifact."
        else:
            # Slash-separated PDF pieces may be either a split single word or genuinely
            # distinct source shapes. First test simple concatenation as one lexical form.
            slash_parts = [norm(x) for x in row.get("front", "").split("/") if norm(x)]
            concat = "".join(slash_parts) if len(slash_parts) > 1 else ""
            if concat in lex:
                final = concat
                method = "concatenated_attested_fragments"
                note = "PDF fragments concatenate to an attested MSA form."

        matches = lex.get(final, [])
        pos_matches = [m for m in matches if not allowed or m["pos"] in allowed]
        if pos_matches:
            matches = pos_matches
        elif matches:
            note = (note + " " if note else "") + "Exact form attested; CAMeL POS differs from paper POS family."
            confidence = "medium"

        # Fuzzy correction only if the current form is unattested, clearly malformed, or
        # still contains a slash artifact. Never fuzzy-replace an attested source word.
        if not matches:
            q = final
            maxdist = 1 if len(q) <= 5 else 2
            candidates = []
            for form in all_forms:
                if abs(len(form) - len(q)) > maxdist:
                    continue
                # Cheap character overlap gate makes the O(1000*lexicon) pass practical.
                if len(set(q) & set(form)) < max(1, min(len(set(q)), len(set(form))) - 2):
                    continue
                meta = lex[form]
                compatible = [m for m in meta if not allowed or m["pos"] in allowed]
                if not compatible:
                    continue
                d = damerau(q, form)
                if d <= maxdist:
                    best_meta = max(compatible, key=lambda m: (m["surface_frequency"], m["lexeme_frequency"]))
                    candidates.append((d, -best_meta["surface_frequency"], -best_meta["lexeme_frequency"], form, best_meta))
            candidates.sort()
            if candidates:
                best = candidates[0]
                # Require distance superiority, or if tied, a very strong frequency lead.
                tied = [c for c in candidates if c[0] == best[0]]
                unique_best = len(tied) == 1
                if not unique_best and len(tied) >= 2:
                    f1 = -tied[0][1] or -tied[0][2]
                    f2 = -tied[1][1] or -tied[1][2]
                    unique_best = f1 >= max(10, f2 * 4)
                if unique_best:
                    final = best[3]
                    matches = lex[final]
                    method = "fuzzy_repair"
                    confidence = "high" if best[0] == 1 else "medium"
                    note = f"Repaired unattested PDF form by unique same-POS MSA candidate (distance {best[0]})."
                else:
                    confidence = "unresolved"
                    note = "Multiple equally plausible MSA repairs."
            else:
                confidence = "unresolved"
                note = "No sufficiently close same-POS MSA validation candidate."

        # Choose metadata without pretending ambiguous analyses are one sense. Store a
        # compact union for later final-card construction.
        final_matches = lex.get(final, [])
        compatible = [m for m in final_matches if not allowed or m["pos"] in allowed] or final_matches
        roots = sorted({m["root"].strip() for m in compatible if m["root"].strip()})
        glosses = []
        camel_pos = []
        for m in sorted(compatible, key=lambda x: (-x["surface_frequency"], -x["lexeme_frequency"])):
            if m["pos"] and m["pos"] not in camel_pos: camel_pos.append(m["pos"])
            g = m["gloss"].strip()
            if g and g not in glosses: glosses.append(g)

        if confidence == "unresolved":
            unresolved.append((rank, raw_front, pos_codes, note))
        counts[method] += 1
        counts[f"confidence_{confidence}"] += 1
        output.append({
            "rank": rank,
            "source_front": row.get("front", ""),
            "front": final,
            "paper_pos": pos_codes,
            "camel_pos": " | ".join(camel_pos),
            "camel_roots": " | ".join(roots),
            "camel_glosses": " | ".join(glosses[:6]),
            "repair_method": method,
            "confidence": confidence,
            "note": note,
        })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(output[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(output)

    summary = [
        f"rows={len(output)}",
        f"unique_fronts={len({r['front'] for r in output})}",
        *[f"{k}={counts[k]}" for k in sorted(counts)],
        f"unresolved={len(unresolved)}",
    ]
    for item in unresolved[:100]:
        summary.append("UNRESOLVED rank=%s source=%r pos=%r note=%s" % item)
    args.summary.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(args.summary.read_text(encoding="utf-8"))

    if len(output) != 1000 or unresolved:
        raise SystemExit(f"Reconciliation is not precision-safe: {len(unresolved)} unresolved rows")


if __name__ == "__main__":
    main()
