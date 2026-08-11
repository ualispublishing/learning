#!/usr/bin/env python3
"""Extract Al-Said 2023 Table 4 with PyMuPDF word coordinates.

This avoids Poppler's RTL glyph fragmentation. The published table has a stable rank
column, frequency/percentage columns, POS codes, and an Arabic word column. We recover
all 1000 rank anchors geometrically, then attach Arabic/POS rows to the nearest anchor.
The script fails closed unless all ranks are recovered and each rank resolves to one
undiacritized orthographic form (with any vocalized homographs preserved as variants).
"""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

BIDI = dict.fromkeys(map(ord, "\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069\ufeff"), None)
DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
AR = re.compile(r"[\u0621-\u063a\u0641-\u064a]")
POS_RE = re.compile(r"^(?:N\\[A-Z]+|V\\[A-Z]+|P\\[A-Z]+|ADV|ADJ|PRO|KH)$")
DEC_RE = re.compile(r"^\d+\.\d+$")
INT_RE = re.compile(r"^\d+$")


def clean(s: str) -> str:
    return unicodedata.normalize("NFC", (s or "").translate(BIDI)).strip()


def undiac(s: str) -> str:
    return DIAC.sub("", clean(s).replace("ـ", ""))


def key(s: str) -> str:
    return "".join(AR.findall(undiac(s)))


def cy(w):
    return (w[1] + w[3]) / 2


def page_y(w):
    return w["page"] * 1000.0 + w["cy"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=Path("audit/al_said_2023_msa1000.csv"))
    ap.add_argument("--debug", type=Path, default=Path("audit/al_said_2023_msa1000_debug.txt"))
    args = ap.parse_args()

    import fitz

    doc = fitz.open(args.pdf)
    tokens = []
    # Article list occupies PDF pages 19..62 inclusive => zero-based 18..61.
    for pno in range(18, 62):
        page = doc[pno]
        for x0, y0, x1, y1, text, block, line, wordno in page.get_text("words", sort=False):
            text = clean(text)
            if not text:
                continue
            tokens.append({
                "page": pno + 1, "x0": float(x0), "y0": float(y0), "x1": float(x1),
                "y1": float(y1), "cy": (float(y0) + float(y1)) / 2, "text": text,
                "block": int(block), "line": int(line), "word": int(wordno),
            })

    # Group tokens into visual lines per page by block+line, then derive metric evidence.
    visual_lines = defaultdict(list)
    for t in tokens:
        visual_lines[(t["page"], t["block"], t["line"])].append(t)

    candidates = []
    for t in tokens:
        if not INT_RE.match(t["text"]):
            continue
        n = int(t["text"])
        if not 1 <= n <= 1000 or not (70 <= t["cy"] <= 790):
            continue
        line = visual_lines[(t["page"], t["block"], t["line"])]
        decimals = sum(bool(DEC_RE.match(x["text"])) for x in line)
        bigfreq = sum(bool(INT_RE.match(x["text"])) and int(x["text"]) >= 10000 for x in line)
        # Some PDF rows split percentage tokens across adjacent text lines; rank geometry
        # plus the frequency integer is enough if at least one percentage remains.
        if decimals >= 1 and bigfreq >= 1:
            candidates.append((n, t))

    bins = defaultdict(set)
    for n, t in candidates:
        bins[int(t["x0"] // 10)].add(n)
    if not bins:
        raise SystemExit("No table rank column found")
    best_bin = max(bins, key=lambda b: (len(bins[b]), b))
    rank_x0 = best_bin * 10
    by_rank = defaultdict(list)
    for n, t in candidates:
        if abs(t["x0"] - rank_x0) <= 22:
            by_rank[n].append(t)

    anchors = {}
    prev_g = -1.0
    for n in range(1, 1001):
        opts = sorted(by_rank.get(n, []), key=lambda t: page_y(t))
        viable = [t for t in opts if page_y(t) > prev_g]
        if not viable:
            raise SystemExit(f"Missing/invalid rank {n}; candidates={opts}")
        anchors[n] = viable[0]
        prev_g = page_y(viable[0])

    rank_x = sum(t["x0"] for t in anchors.values()) / 1000.0

    # Arabic word-cell tokens are immediately left of the rank column. PyMuPDF generally
    # returns whole Arabic words, so no manual reversal is performed.
    arabic_tokens = []
    for t in tokens:
        if not AR.search(t["text"]):
            continue
        if t["x1"] < rank_x - 180 or t["x1"] > rank_x - 2:
            continue
        k = key(t["text"])
        if not k:
            continue
        arabic_tokens.append({**t, "key": k})

    pos_tokens = [t for t in tokens if POS_RE.match(t["text"])]
    anchor_positions = [(n, page_y(anchors[n])) for n in range(1, 1001)]

    rows = []
    problems = []
    duplicate_keys = defaultdict(list)
    for n in range(1, 1001):
        g = page_y(anchors[n])
        prev_g = page_y(anchors[n - 1]) if n > 1 else g - 80
        next_g = page_y(anchors[n + 1]) if n < 1000 else g + 80
        lo = (prev_g + g) / 2
        hi = (g + next_g) / 2

        nearby = [t for t in arabic_tokens if lo <= page_y(t) < hi]
        if not nearby:
            # Homograph variants can straddle the metric baseline more broadly than the
            # midpoint window. Expand only within the neighboring rank anchors.
            nearby = [t for t in arabic_tokens if prev_g + 1 <= page_y(t) <= next_g - 1]
        if not nearby:
            problems.append(f"rank={n} no Arabic token")
            rows.append({"rank": n, "front": "", "variants": "", "pos_codes": "", "source": "Al-Said 2023 Table 4"})
            continue

        groups = defaultdict(list)
        for t in nearby:
            groups[t["key"]].append(t)
        scored = []
        for k, group in groups.items():
            d = min(abs(page_y(t) - g) for t in group)
            # Prefer entries whose Arabic token lies closest to the rank baseline, then
            # entries supported by multiple vocalized variants.
            scored.append((d, -len(group), k, group))
        scored.sort(key=lambda x: (x[0], x[1], x[2]))
        d, negc, chosen_key, chosen = scored[0]
        if len(scored) > 1 and abs(scored[1][0] - d) < 0.75 and scored[1][1] == negc:
            problems.append(f"rank={n} ambiguous keys={[(x[2], round(x[0],2)) for x in scored[:4]]}")
            chosen_key = ""
            chosen = []

        variants = []
        for t in sorted(chosen, key=page_y):
            v = t["text"]
            if v not in variants:
                variants.append(v)

        poss = []
        for pt in pos_tokens:
            if lo <= page_y(pt) < hi and pt["text"] not in poss:
                poss.append(pt["text"])

        rows.append({
            "rank": n, "front": chosen_key, "variants": " | ".join(variants),
            "pos_codes": " | ".join(poss), "source": "Al-Said 2023 Table 4",
        })
        if chosen_key:
            duplicate_keys[chosen_key].append(n)

    duplicates = {k: v for k, v in duplicate_keys.items() if len(v) > 1}
    nonempty = sum(bool(r["front"]) for r in rows)
    unique = len({r["front"] for r in rows if r["front"]})

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(rows)

    debug = [
        f"tokens={len(tokens)}", f"rank_column_x={rank_x:.2f}", "anchors=1000",
        f"nonempty={nonempty}", f"unique_orthographic_fronts={unique}",
        f"duplicate_front_groups={len(duplicates)}", f"problems={len(problems)}",
    ]
    if duplicates:
        debug.append("duplicate_fronts=" + repr(duplicates))
    debug.extend(problems)
    args.debug.write_text("\n".join(debug) + "\n", encoding="utf-8")

    if nonempty != 1000 or problems:
        raise SystemExit(f"Extraction failed closed; see {args.debug}")
    print(args.debug.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
