#!/usr/bin/env python3
"""Extract Al-Said's ranked 1,000 MSA word inventory from pdftotext TSV.

Source: Almoataz B. Al-Said (2023), "A New List of Common Words in Modern
Standard Arabic", MEAH Sección Árabe-Islam 72, pp. 287-351, CC BY 4.0.

The PDF table is RTL and some rank rows contain several vocalized homographs.
We therefore anchor each rank on its numeric frequency row, reconstruct Arabic
word-cell lines geometrically, and retain only variants sharing the anchor row's
undiacritized orthography. The extractor fails closed unless ranks 1..1000 are
all recovered.
"""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

BIDI = dict.fromkeys(map(ord, "\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069\ufeff"), None)
DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
AR = re.compile(r"[\u0621-\u063a\u0641-\u064a]")
POS_RE = re.compile(r"^(?:N|V|P|ADV|ADJ|PRO|KH)(?:\\[A-Z]+)?$")
DEC_RE = re.compile(r"^\d+\.\d+$")


def clean(s: str) -> str:
    return unicodedata.normalize("NFC", (s or "").translate(BIDI)).strip()


def undiac(s: str) -> str:
    return DIAC.sub("", clean(s).replace("ـ", ""))


def arabic_only_key(s: str) -> str:
    return "".join(AR.findall(undiac(s)))


def is_int(s: str) -> bool:
    return bool(re.fullmatch(r"\d+", clean(s)))


def center_y(w: dict) -> float:
    return w["top"] + w["height"] / 2


def global_y(w: dict) -> float:
    return w["page"] * 1000.0 + center_y(w)


def parse_tsv(path: Path):
    rows = []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        for x in r:
            if x.get("level") != "5":
                continue
            text = clean(x.get("text", ""))
            if not text:
                continue
            try:
                rows.append({
                    "page": int(x["page_num"]), "block": int(x["block_num"]),
                    "par": int(x["par_num"]), "line": int(x["line_num"]),
                    "word": int(x["word_num"]), "left": float(x["left"]),
                    "top": float(x["top"]), "width": float(x["width"]),
                    "height": float(x["height"]), "text": text,
                })
            except (KeyError, TypeError, ValueError):
                continue
    return rows


def has_metrics(w: dict, words: list[dict]) -> bool:
    """True only for a table rank token sitting on a frequency/percentage row."""
    cy = center_y(w)
    same = [x for x in words if x["page"] == w["page"] and abs(center_y(x) - cy) <= 5.5]
    decimals = sum(1 for x in same if DEC_RE.match(x["text"]))
    bigints = sum(1 for x in same if is_int(x["text"]) and int(x["text"]) >= 10000)
    return decimals >= 2 and bigints >= 1


def locate_rank_tokens(words: list[dict]):
    candidates = []
    for w in words:
        if w["top"] < 75 or w["top"] > 790 or not is_int(w["text"]):
            continue
        n = int(w["text"])
        if 1 <= n <= 1000 and has_metrics(w, words):
            candidates.append((n, w))

    bins: dict[int, set[int]] = defaultdict(set)
    for n, w in candidates:
        bins[int(w["left"] // 12)].add(n)
    if not bins:
        raise SystemExit("Could not locate the table rank column")
    best_bin = max(bins, key=lambda b: (len(bins[b]), b))
    x0 = best_bin * 12

    by_rank: dict[int, list[dict]] = defaultdict(list)
    for n, w in candidates:
        if abs(w["left"] - x0) <= 22:
            by_rank[n].append(w)

    selected = {}
    for n in range(1, 1001):
        opts = by_rank.get(n, [])
        if len(opts) == 1:
            selected[n] = opts[0]
        elif opts:
            # Actual table ranks progress monotonically through the extracted pages.
            # Prefer the option closest to the expected local neighborhood.
            selected[n] = sorted(opts, key=lambda w: (w["page"], w["top"]))[-1 if n < 50 else 0]

    missing = [n for n in range(1, 1001) if n not in selected]
    if missing:
        raise SystemExit(
            f"Rank extraction missing {len(missing)} ranks; first={missing[:25]}; "
            f"rank_bin={best_bin}; recovered={len(selected)}"
        )

    # Enforce strict monotonic visual order; this catches any accidental prose/header token.
    order = [global_y(selected[n]) for n in range(1, 1001)]
    bad_order = [n for n in range(2, 1001) if order[n - 1] <= order[n - 2]]
    if bad_order:
        raise SystemExit(f"Non-monotonic rank positions at {bad_order[:20]}")
    return selected


def line_records(words: list[dict], rank_x: float):
    """Reconstruct Arabic strings and POS labels for lines in the table's word/POS area."""
    # Arabic words are right-aligned immediately left of the rank column. Long words may
    # start far left, so filter on their right edge rather than only their left edge.
    grouped: dict[tuple[int, int, int, int], list[dict]] = defaultdict(list)
    for w in words:
        if w["top"] < 75 or w["top"] > 790:
            continue
        right = w["left"] + w["width"]
        if AR.search(w["text"]) and (rank_x - 135) <= right <= (rank_x - 3) and w["left"] >= rank_x - 210:
            grouped[(w["page"], w["block"], w["par"], w["line"])].append(w)

    lines = []
    for _, toks in grouped.items():
        # pdftotext already emits Arabic fragments in logical direction; visual x-order
        # must be assembled left-to-right here (the previous extractor reversed fragments).
        toks = sorted(toks, key=lambda x: x["left"])
        text = "".join(t["text"] for t in toks)
        k = arabic_only_key(text)
        if not k:
            continue
        lines.append({
            "page": toks[0]["page"],
            "gy": sum(global_y(t) for t in toks) / len(toks),
            "text": clean(text),
            "key": k,
        })
    return sorted(lines, key=lambda x: x["gy"])


def pos_near(words: list[dict], gy_lo: float, gy_hi: float) -> list[str]:
    out = []
    for w in words:
        gy = global_y(w)
        if gy_lo <= gy <= gy_hi:
            t = clean(w["text"])
            if POS_RE.match(t) and t not in out:
                out.append(t)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tsv", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=Path("audit/al_said_2023_msa1000.csv"))
    ap.add_argument("--debug", type=Path, default=Path("audit/al_said_2023_msa1000_debug.txt"))
    args = ap.parse_args()

    words = parse_tsv(args.tsv)
    ranks = locate_rank_tokens(words)
    rank_x = sum(w["left"] for w in ranks.values()) / 1000.0
    lines = line_records(words, rank_x)
    rank_gy = {n: global_y(w) for n, w in ranks.items()}

    out = []
    debug = []
    for rank in range(1, 1001):
        gy = rank_gy[rank]
        prev_gy = rank_gy[rank - 1] if rank > 1 else gy - 70
        next_gy = rank_gy[rank + 1] if rank < 1000 else gy + 70

        # A multi-variant row can have one variant before the numeric baseline and another
        # after it. Search the full interval bounded by adjacent numeric rows, with a small
        # overlap; later we keep only one orthographic key, which prevents row bleed.
        lo = prev_gy + 1
        hi = next_gy - 1
        nearby = [ln for ln in lines if lo <= ln["gy"] <= hi]
        if not nearby:
            debug.append(f"rank={rank} ERROR no Arabic line candidates gy={gy:.1f}")
            out.append({"rank": rank, "front": "", "variants": "", "pos_codes": "", "source": "Al-Said 2023 Table 4"})
            continue

        # Anchor = closest Arabic word-cell line to the rank's metric baseline. This works
        # both when the first variant sits on the metric line and when the metric line itself
        # has an empty word cell between two same-spelling vocalized variants.
        anchor = min(nearby, key=lambda ln: abs(ln["gy"] - gy))
        anchor_key = anchor["key"]
        same = [ln for ln in nearby if ln["key"] == anchor_key]
        variants = []
        for ln in sorted(same, key=lambda x: x["gy"]):
            if ln["text"] not in variants:
                variants.append(ln["text"])

        # If the closest line was a split fragment, prefer an orthographic key represented
        # by two or more nearby lines when that key is nearly as close to the metric row.
        key_groups: dict[str, list[dict]] = defaultdict(list)
        for ln in nearby:
            key_groups[ln["key"]].append(ln)
        repeated = []
        for k, group in key_groups.items():
            if len(group) >= 2:
                d = min(abs(x["gy"] - gy) for x in group)
                repeated.append((d, -len(group), k, group))
        if repeated:
            repeated.sort()
            d, _, k, group = repeated[0]
            if d <= abs(anchor["gy"] - gy) + 8:
                anchor_key = k
                variants = []
                for ln in sorted(group, key=lambda x: x["gy"]):
                    if ln["text"] not in variants:
                        variants.append(ln["text"])

        pos = pos_near(words, lo, hi)
        if len({arabic_only_key(v) for v in variants}) != 1:
            debug.append(f"rank={rank} ERROR nonuniform variants={variants!r}")

        out.append({
            "rank": rank,
            "front": anchor_key,
            "variants": " | ".join(variants),
            "pos_codes": " | ".join(pos),
            "source": "Al-Said 2023 Table 4",
        })

    bad = [r for r in out if not r["front"]]
    unique_fronts = len({r["front"] for r in out if r["front"]})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(out)

    args.debug.write_text("\n".join([
        f"rank_x={rank_x:.2f}", f"rows={len(out)}", f"nonempty={len(out)-len(bad)}",
        f"unique_orthographic_fronts={unique_fronts}", f"debug_issue_count={len(debug)}",
        *debug,
    ]) + "\n", encoding="utf-8")

    if bad or any("ERROR" in x for x in debug):
        raise SystemExit(f"Extraction failed closed; see {args.debug}")
    print(args.debug.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
