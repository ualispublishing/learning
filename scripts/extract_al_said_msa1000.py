#!/usr/bin/env python3
"""Extract Al-Said's ranked 1,000 MSA word inventory from pdftotext TSV.

Source: Almoataz B. Al-Said (2023), "A New List of Common Words in Modern
Standard Arabic", MEAH Sección Árabe-Islam 72, pp. 287-351, CC BY 4.0.

The article's table is laid out right-to-left. We use word coordinates rather than
plain-text order, locate the rank column geometrically, then assign Arabic word-cell
content to the nearest rank row. The script fails closed unless ranks 1..1000 are all
present exactly once and every row yields one normalized orthographic front.
"""
from __future__ import annotations

import argparse
import csv
import math
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

BIDI = dict.fromkeys(map(ord, "\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069\ufeff"), None)
DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
AR = re.compile(r"[\u0621-\u063a\u0641-\u064a]")
POS_RE = re.compile(r"^(?:N|V|P|ADV|ADJ|PRO|KH)(?:\\[A-Z]+)?$")


def clean(s: str) -> str:
    return unicodedata.normalize("NFC", (s or "").translate(BIDI)).strip()


def undiac(s: str) -> str:
    return DIAC.sub("", clean(s).replace("ـ", ""))


def arabic_only_key(s: str) -> str:
    # Keep Arabic letters only. Parenthetical clitic notation in the paper, e.g. لـ(ه),
    # is presentation metadata; the lexical orthographic front is the Arabic-letter form.
    return "".join(AR.findall(undiac(s)))


def is_int(s: str) -> bool:
    return bool(re.fullmatch(r"\d+", clean(s)))


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
                    "page": int(x["page_num"]),
                    "block": int(x["block_num"]),
                    "par": int(x["par_num"]),
                    "line": int(x["line_num"]),
                    "word": int(x["word_num"]),
                    "left": float(x["left"]),
                    "top": float(x["top"]),
                    "width": float(x["width"]),
                    "height": float(x["height"]),
                    "text": text,
                })
            except (KeyError, TypeError, ValueError):
                continue
    return rows


def locate_rank_tokens(words):
    candidates = []
    for w in words:
        if w["top"] < 85 or w["top"] > 780 or not is_int(w["text"]):
            continue
        n = int(w["text"])
        if 1 <= n <= 1000:
            candidates.append((n, w))

    # Rank values form the dominant far-right numeric column. Score 15-point x bins by
    # number of distinct ranks and prefer farther-right bins on ties.
    bins: dict[int, set[int]] = defaultdict(set)
    for n, w in candidates:
        bins[int(w["left"] // 15)].add(n)
    if not bins:
        raise SystemExit("Could not locate any rank candidates in TSV")
    best_bin = max(bins, key=lambda b: (len(bins[b]), b))
    center = best_bin * 15 + 7.5

    near = [(n, w) for n, w in candidates if abs((w["left"] + w["width"] / 2) - center) <= 30 or abs(w["left"] - best_bin * 15) <= 25]
    by_rank: dict[int, list[dict]] = defaultdict(list)
    for n, w in near:
        by_rank[n].append(w)

    # If geometry selected duplicate page-number/header tokens, choose the occurrence in
    # the table body that best follows the monotonic page progression of neighboring ranks.
    selected = {}
    prev_page = None
    for n in range(1, 1001):
        opts = by_rank.get(n, [])
        if not opts:
            continue
        opts.sort(key=lambda w: (w["page"], w["top"]))
        if prev_page is None:
            choice = opts[0]
        else:
            viable = [w for w in opts if w["page"] >= prev_page]
            choice = (viable or opts)[0]
        selected[n] = choice
        prev_page = choice["page"]

    missing = [n for n in range(1, 1001) if n not in selected]
    if missing:
        raise SystemExit(f"Rank-column extraction missing {len(missing)} ranks; first missing: {missing[:30]}; best_bin={best_bin}; bin_count={len(bins[best_bin])}")
    return selected


def row_windows(rank_tokens):
    by_page: dict[int, list[tuple[int, dict]]] = defaultdict(list)
    for rank, tok in rank_tokens.items():
        by_page[tok["page"]].append((rank, tok))
    windows = {}
    for page, items in by_page.items():
        items.sort(key=lambda it: it[1]["top"])
        for i, (rank, tok) in enumerate(items):
            y = tok["top"] + tok["height"] / 2
            if i == 0:
                lo = max(85.0, y - 22.0)
            else:
                p = items[i - 1][1]
                py = p["top"] + p["height"] / 2
                lo = (py + y) / 2
            if i == len(items) - 1:
                hi = min(780.0, y + 22.0)
            else:
                q = items[i + 1][1]
                qy = q["top"] + q["height"] / 2
                hi = (y + qy) / 2
            windows[rank] = (page, lo, hi)
    return windows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tsv", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=Path("audit/al_said_2023_msa1000.csv"))
    ap.add_argument("--debug", type=Path, default=Path("audit/al_said_2023_msa1000_debug.txt"))
    args = ap.parse_args()

    words = parse_tsv(args.tsv)
    rank_tokens = locate_rank_tokens(words)
    windows = row_windows(rank_tokens)

    # Estimate the word column from Arabic tokens nearest the rank column on rank-bearing
    # lines. Then use a deliberately broad band around that estimate for multi-line variants.
    rank_x = sum(t["left"] for t in rank_tokens.values()) / 1000
    word_x_samples = []
    for rank, rt in rank_tokens.items():
        cy = rt["top"] + rt["height"] / 2
        nearby = [
            w for w in words if w["page"] == rt["page"] and AR.search(w["text"])
            and w["left"] < rank_x - 5 and abs((w["top"] + w["height"] / 2) - cy) < 16
        ]
        if nearby:
            nearest = max(nearby, key=lambda w: w["left"])
            word_x_samples.append(nearest["left"])
    if not word_x_samples:
        raise SystemExit("Could not estimate Arabic word column")
    word_x = sorted(word_x_samples)[len(word_x_samples) // 2]
    word_lo = word_x - 105
    word_hi = rank_x - 8

    out = []
    debug = []
    for rank in range(1, 1001):
        page, lo, hi = windows[rank]
        cell = [
            w for w in words
            if w["page"] == page and lo <= (w["top"] + w["height"] / 2) < hi
            and word_lo <= w["left"] <= word_hi and AR.search(w["text"])
        ]
        # Group by visual line; within Arabic lines reconstruct right-to-left.
        by_line = defaultdict(list)
        for w in cell:
            by_line[(w["block"], w["par"], w["line"])].append(w)
        variants = []
        for _, line_words in sorted(by_line.items(), key=lambda kv: min(x["top"] for x in kv[1])):
            text = "".join(x["text"] for x in sorted(line_words, key=lambda x: x["left"], reverse=True))
            text = clean(text)
            k = arabic_only_key(text)
            if k and text not in variants:
                variants.append(text)

        # Fallback: capture any Arabic tokens in a slightly wider nearest-rank band.
        if not variants:
            fallback = [
                w for w in words if w["page"] == page and lo <= (w["top"] + w["height"] / 2) < hi
                and w["left"] < rank_x and AR.search(w["text"])
            ]
            fallback.sort(key=lambda w: (abs(rank_x - w["left"]), w["top"]))
            if fallback:
                variants = [fallback[0]["text"]]

        keys = [arabic_only_key(v) for v in variants if arabic_only_key(v)]
        # Collapse orthographically identical vocalized senses, but preserve all distinct
        # vocalizations in the variants field.
        key_counts = Counter(keys)
        if not key_counts:
            debug.append(f"rank={rank} page={page} ERROR no Arabic front; window={lo:.1f}-{hi:.1f}")
            front = ""
        else:
            front = key_counts.most_common(1)[0][0]
            if len(key_counts) > 1:
                debug.append(f"rank={rank} page={page} orthographic_keys={dict(key_counts)} variants={variants!r}")

        # POS codes in the same vertical window, just left of the word column.
        pos = []
        for w in words:
            if w["page"] != page or not (lo <= (w["top"] + w["height"] / 2) < hi):
                continue
            t = clean(w["text"])
            if POS_RE.match(t) and t not in pos:
                pos.append(t)

        out.append({
            "rank": rank,
            "front": front,
            "variants": " | ".join(variants),
            "pos_codes": " | ".join(pos),
            "source": "Al-Said 2023 Table 4",
        })

    bad = [r for r in out if not r["front"]]
    unique_fronts = len({r["front"] for r in out if r["front"]})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    args.debug.write_text(
        "\n".join([
            f"rank_x={rank_x:.2f}", f"word_x={word_x:.2f}", f"word_band={word_lo:.2f}..{word_hi:.2f}",
            f"rows={len(out)}", f"nonempty={len(out)-len(bad)}", f"unique_fronts={unique_fronts}",
            *debug,
        ]) + "\n",
        encoding="utf-8",
    )
    if bad:
        raise SystemExit(f"Extraction produced {len(bad)} empty fronts; see {args.debug}")
    print(args.debug.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
