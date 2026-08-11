#!/usr/bin/env python3
"""Extract Al-Said 2023 Table 4 with PyMuPDF word coordinates.

Source: Almoataz B. Al-Said (2023), "A New List of Common Words in Modern
Standard Arabic", MEAH Sección Árabe-Islam 72, pp. 287-351, Table 4, CC BY 4.0.

The PDF is RTL and PyMuPDF sometimes splits one Arabic word into several visual
fragments. The table geometry is stable: the rank column is at x≈453-460 and the
Arabic word cell sits immediately to its left. We therefore:

1. recover ranks 1..1000 from the rank column in strict visual order;
2. reconstruct each Arabic visual line by joining its fragments right-to-left;
3. attach each reconstructed line to the nearest rank baseline;
4. require all vocalized variants under one rank to share one undiacritized form;
5. fail closed unless the published inventory is exactly 1000 unique forms.

This script extracts inventory evidence only. It does not invent translations,
roots, examples, or synonyms.
"""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from bisect import bisect_left
from collections import defaultdict
from pathlib import Path

BIDI = dict.fromkeys(map(ord, "\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069\ufeff"), None)
DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
AR = re.compile(r"[\u0621-\u063a\u0641-\u064a]")
INT_RE = re.compile(r"^\d+$")
# Paper POS codes include values such as N\CN, V\PERF, P\PRE, ADV, ADJ, PRO.
POS_RE = re.compile(r"^(?:N|V|P)(?:\\[A-Z]+)+$|^(?:ADV|ADJ|PRO|KH)$")


def clean(s: str) -> str:
    return unicodedata.normalize("NFC", (s or "").translate(BIDI)).strip()


def undiac(s: str) -> str:
    return DIAC.sub("", clean(s).replace("ـ", ""))


def arabic_letters(s: str) -> str:
    return "".join(AR.findall(undiac(s)))


def global_y(t: dict) -> float:
    return t["page"] * 1000.0 + t["cy"]


def nearest_rank(anchor_gys: list[float], gy: float) -> tuple[int, float]:
    """Return 1-based rank and distance to nearest rank baseline."""
    j = bisect_left(anchor_gys, gy)
    options = []
    if j < len(anchor_gys):
        options.append((abs(anchor_gys[j] - gy), j + 1))
    if j > 0:
        options.append((abs(anchor_gys[j - 1] - gy), j))
    if not options:
        raise RuntimeError("No rank anchors")
    dist, rank = min(options, key=lambda x: (x[0], x[1]))
    return rank, dist


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=Path("audit/al_said_2023_msa1000.csv"))
    ap.add_argument("--debug", type=Path, default=Path("audit/al_said_2023_msa1000_debug.txt"))
    args = ap.parse_args()

    import pymupdf

    doc = pymupdf.open(args.pdf)
    tokens: list[dict] = []
    # Table 4 starts on PDF page 19 and ends on PDF page 62 (1-based).
    for pno in range(18, 62):
        page = doc[pno]
        for x0, y0, x1, y1, text, block, line, wordno in page.get_text("words", sort=False):
            text = clean(text)
            if not text:
                continue
            tokens.append({
                "page": pno + 1,
                "x0": float(x0), "y0": float(y0), "x1": float(x1), "y1": float(y1),
                "cy": (float(y0) + float(y1)) / 2.0,
                "text": text, "block": int(block), "line": int(line), "word": int(wordno),
            })

    # --- Rank anchors -------------------------------------------------------
    # Rank numbers are right-aligned in the stable far-right table column. Article page
    # numbers may share a similar x coordinate, but strict 1..1000 monotonic selection
    # naturally excludes them once the preceding rank has been selected.
    by_rank: dict[int, list[dict]] = defaultdict(list)
    for t in tokens:
        if not INT_RE.fullmatch(t["text"]):
            continue
        n = int(t["text"])
        if not (1 <= n <= 1000):
            continue
        if not (445.0 <= t["x0"] <= 466.5):
            continue
        # Table rows stay inside the body; page headers/footers are excluded.
        if not (165.0 <= t["cy"] <= 665.0):
            continue
        by_rank[n].append(t)

    anchors: dict[int, dict] = {}
    prev_gy = -1.0
    rank_debug = []
    for n in range(1, 1001):
        opts = sorted(by_rank.get(n, []), key=global_y)
        viable = [t for t in opts if global_y(t) > prev_gy]
        if not viable:
            rank_debug.append(f"rank={n} candidates={[(x['page'], round(x['x0'],1), round(x['cy'],1)) for x in opts]}")
            args.debug.parent.mkdir(parents=True, exist_ok=True)
            args.debug.write_text("Missing rank anchor\n" + "\n".join(rank_debug) + "\n", encoding="utf-8")
            raise SystemExit(f"Missing rank anchor {n}; see {args.debug}")
        # When an article page number happens to equal a rank, the true rank is the first
        # viable token after the previous rank in visual order.
        anchors[n] = viable[0]
        prev_gy = global_y(viable[0])

    anchor_gys = [global_y(anchors[n]) for n in range(1, 1001)]
    if any(b <= a for a, b in zip(anchor_gys, anchor_gys[1:])):
        raise SystemExit("Rank anchors are not strictly monotonic")

    # --- Arabic visual lines -----------------------------------------------
    # Word fragments lie in x≈405..432. Long words extend farther left, so test the
    # fragment's right edge and allow x0 down to 350. Group by page + visual baseline.
    arabic_fragments: list[dict] = []
    for t in tokens:
        if not AR.search(t["text"]):
            continue
        if not (350.0 <= t["x0"] <= 434.5 and 407.0 <= t["x1"] <= 435.5):
            continue
        # Keep only text in the vertical span of table rows, excluding prose/header text.
        if not (165.0 <= t["cy"] <= 665.0):
            continue
        arabic_fragments.append(t)

    # PyMuPDF fragments belonging to the same visual variant share almost exactly the
    # same y baseline. Quantize at 0.75pt to absorb tiny floating-point differences.
    line_groups: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for t in arabic_fragments:
        ybucket = int(round(t["cy"] / 0.75))
        line_groups[(t["page"], ybucket)].append(t)

    reconstructed_lines = []
    for (page, _), group in line_groups.items():
        # Arabic reads right-to-left: highest x fragment comes first. Extract only Arabic
        # letters for the canonical undiacritized key; keep raw fragments for traceability.
        ordered = sorted(group, key=lambda t: t["x0"], reverse=True)
        k = "".join(arabic_letters(t["text"]) for t in ordered)
        if not k:
            continue
        gy = sum(global_y(t) for t in group) / len(group)
        rank, dist = nearest_rank(anchor_gys, gy)
        # Multi-vocalization rows sit about ±6pt around a rank baseline. A 7.5pt cap
        # captures them while excluding neighboring prose or adjacent rank content.
        if dist > 7.5:
            continue
        reconstructed_lines.append({
            "rank": rank,
            "gy": gy,
            "key": k,
            "raw": " + ".join(t["text"] for t in ordered),
            "fragment_count": len(group),
        })

    lines_by_rank: dict[int, list[dict]] = defaultdict(list)
    for line in reconstructed_lines:
        lines_by_rank[line["rank"]].append(line)

    # POS tokens are separate text objects. Attach them to the nearest rank baseline using
    # the same conservative distance cap. These are evidence only; missing POS is allowed
    # because CAMeL provides an independent later validation layer.
    pos_by_rank: dict[int, list[str]] = defaultdict(list)
    for t in tokens:
        if not POS_RE.fullmatch(t["text"]):
            continue
        rank, dist = nearest_rank(anchor_gys, global_y(t))
        if dist <= 7.5 and t["text"] not in pos_by_rank[rank]:
            pos_by_rank[rank].append(t["text"])

    rows = []
    problems = []
    fronts: dict[str, list[int]] = defaultdict(list)

    for rank in range(1, 1001):
        group = sorted(lines_by_rank.get(rank, []), key=lambda x: x["gy"])
        if not group:
            problems.append(f"rank={rank}: no Arabic word-cell line")
            rows.append({
                "rank": rank, "front": "", "variants_raw": "", "pos_codes": "",
                "source": "Al-Said 2023 Table 4",
            })
            continue

        # Deduplicate repeated extraction lines. Every genuine vocalized homograph variant
        # under a rank must reduce to the same undiacritized spelling by the paper's design.
        keys = []
        variants_raw = []
        for line in group:
            if line["key"] not in keys:
                keys.append(line["key"])
            trace = line["raw"]
            if trace not in variants_raw:
                variants_raw.append(trace)

        if len(keys) != 1:
            problems.append(
                f"rank={rank}: conflicting orthographic forms {keys!r}; "
                f"raw={variants_raw!r}"
            )
            front = ""
        else:
            front = keys[0]
            fronts[front].append(rank)

        rows.append({
            "rank": rank,
            "front": front,
            "variants_raw": " | ".join(variants_raw),
            "pos_codes": " | ".join(pos_by_rank.get(rank, [])),
            "source": "Al-Said 2023 Table 4",
        })

    duplicate_fronts = {k: v for k, v in fronts.items() if len(v) > 1}
    nonempty = sum(bool(r["front"]) for r in rows)
    unique = len(fronts)
    if duplicate_fronts:
        problems.append(f"duplicate published fronts: {duplicate_fronts!r}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    debug_lines = [
        f"tokens={len(tokens)}",
        "rank_anchors=1000",
        f"arabic_fragments={len(arabic_fragments)}",
        f"reconstructed_word_lines={len(reconstructed_lines)}",
        f"nonempty_rows={nonempty}",
        f"unique_fronts={unique}",
        f"pos_rows={sum(bool(pos_by_rank.get(n)) for n in range(1,1001))}",
        f"problems={len(problems)}",
        *problems,
    ]
    args.debug.write_text("\n".join(debug_lines) + "\n", encoding="utf-8")

    if nonempty != 1000 or unique != 1000 or problems:
        raise SystemExit(f"Published-list extraction failed closed; see {args.debug}")

    print(args.debug.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
