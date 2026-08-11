#!/usr/bin/env python3
"""Extract Al-Said 2023 Table 4 with PyMuPDF word coordinates.

Source: Almoataz B. Al-Said (2023), "A New List of Common Words in Modern
Standard Arabic", MEAH Sección Árabe-Islam 72, pp. 287-351, Table 4, CC BY 4.0.

PyMuPDF can split RTL Arabic words into several text objects and can assign a final
letter to another internal line even though it is on the same visual baseline. This
extractor therefore trusts table geometry, not PDF line labels:

1. recover ranks 1..1000 from the stable rank column;
2. collect every Arabic fragment in the word-cell horizontal band;
3. attach fragments to the nearest rank baseline;
4. cluster same-rank fragments by visual y baseline (2.25pt tolerance), then join
   each cluster right-to-left;
5. preserve distinct published shape/vocalization variants on one Arabic-only front;
6. fail closed unless all 1000 rank records are nonempty.

This is source extraction only. It never invents meanings, roots, examples or synonyms.
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
    j = bisect_left(anchor_gys, gy)
    opts = []
    if j < len(anchor_gys):
        opts.append((abs(anchor_gys[j] - gy), j + 1))
    if j > 0:
        opts.append((abs(anchor_gys[j - 1] - gy), j))
    if not opts:
        raise RuntimeError("No rank anchors")
    return min(opts, key=lambda x: (x[0], x[1]))[1], min(opts, key=lambda x: (x[0], x[1]))[0]


def cluster_by_y(items: list[dict], tolerance: float = 2.25) -> list[list[dict]]:
    """Cluster tokens that occupy the same visual Arabic variant baseline."""
    if not items:
        return []
    ordered = sorted(items, key=lambda t: t["cy"])
    clusters: list[list[dict]] = [[ordered[0]]]
    for t in ordered[1:]:
        current = clusters[-1]
        mean_y = sum(x["cy"] for x in current) / len(current)
        if abs(t["cy"] - mean_y) <= tolerance:
            current.append(t)
        else:
            clusters.append([t])
    return clusters


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=Path("audit/al_said_2023_msa1000.csv"))
    ap.add_argument("--debug", type=Path, default=Path("audit/al_said_2023_msa1000_debug.txt"))
    args = ap.parse_args()

    import pymupdf

    doc = pymupdf.open(args.pdf)
    tokens: list[dict] = []
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

    # Stable far-right rank column. Strict 1..1000 visual progression excludes page numbers.
    by_rank: dict[int, list[dict]] = defaultdict(list)
    for t in tokens:
        if INT_RE.fullmatch(t["text"]):
            n = int(t["text"])
            if 1 <= n <= 1000 and 445.0 <= t["x0"] <= 466.5 and 165.0 <= t["cy"] <= 665.0:
                by_rank[n].append(t)

    anchors: dict[int, dict] = {}
    prev_gy = -1.0
    for n in range(1, 1001):
        viable = [t for t in sorted(by_rank.get(n, []), key=global_y) if global_y(t) > prev_gy]
        if not viable:
            args.debug.parent.mkdir(parents=True, exist_ok=True)
            args.debug.write_text(f"missing_rank_anchor={n}\n", encoding="utf-8")
            raise SystemExit(f"Missing rank anchor {n}; see {args.debug}")
        anchors[n] = viable[0]
        prev_gy = global_y(viable[0])

    anchor_gys = [global_y(anchors[n]) for n in range(1, 1001)]

    # Word-cell band contains no other Arabic data columns. Long words can extend well left,
    # so allow x0 down to 300 and do not impose a lower bound on x1. The nearest-rank y gate
    # excludes running prose and headers.
    fragments_by_rank: dict[int, list[dict]] = defaultdict(list)
    fragment_count = 0
    for t in tokens:
        if not AR.search(t["text"]):
            continue
        if not (300.0 <= t["x0"] <= 444.5 and t["x1"] <= 447.5):
            continue
        if not (165.0 <= t["cy"] <= 665.0):
            continue
        rank, dist = nearest_rank(anchor_gys, global_y(t))
        if dist <= 7.75:
            fragments_by_rank[rank].append(t)
            fragment_count += 1

    variants_by_rank: dict[int, list[dict]] = defaultdict(list)
    for rank in range(1, 1001):
        # Pages never mix inside one rank; cluster in page-local y coordinates.
        for cluster in cluster_by_y(fragments_by_rank.get(rank, []), tolerance=2.25):
            ordered = sorted(cluster, key=lambda t: (t["x0"], t["word"]), reverse=True)
            k = "".join(arabic_letters(t["text"]) for t in ordered)
            if not k:
                continue
            variants_by_rank[rank].append({
                "key": k,
                "cy": sum(t["cy"] for t in cluster) / len(cluster),
                "raw": " + ".join(t["text"] for t in ordered),
            })

    pos_by_rank: dict[int, list[str]] = defaultdict(list)
    for t in tokens:
        if POS_RE.fullmatch(t["text"]):
            rank, dist = nearest_rank(anchor_gys, global_y(t))
            if dist <= 7.75 and t["text"] not in pos_by_rank[rank]:
                pos_by_rank[rank].append(t["text"])

    rows = []
    problems = []
    duplicate_fronts: dict[str, list[int]] = defaultdict(list)

    for rank in range(1, 1001):
        variants = sorted(variants_by_rank.get(rank, []), key=lambda x: x["cy"])
        if not variants:
            problems.append(f"rank={rank}: no Arabic word-cell variant")
            rows.append({"rank": rank, "front": "", "variants_raw": "", "pos_codes": "", "source": "Al-Said 2023 Table 4"})
            continue

        keys = []
        traces = []
        for v in variants:
            if v["key"] not in keys:
                keys.append(v["key"])
            if v["raw"] not in traces:
                traces.append(v["raw"])

        # Drop only obvious extraction truncations when an extracted key is wholly contained
        # in another variant from the same rank. Preserve genuine source shape variants.
        cleaned = [k for k in keys if not any(k != other and k in other for other in keys)]
        cleaned = cleaned or keys
        front = " / ".join(dict.fromkeys(cleaned))
        duplicate_fronts[front].append(rank)

        rows.append({
            "rank": rank,
            "front": front,
            "variants_raw": " | ".join(traces),
            "pos_codes": " | ".join(pos_by_rank.get(rank, [])),
            "source": "Al-Said 2023 Table 4",
        })

    duplicate_fronts = {k: v for k, v in duplicate_fronts.items() if k and len(v) > 1}
    nonempty = sum(bool(r["front"]) for r in rows)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(rows)

    debug = [
        f"tokens={len(tokens)}", "rank_anchors=1000", f"assigned_arabic_fragments={fragment_count}",
        f"reconstructed_variant_lines={sum(len(v) for v in variants_by_rank.values())}",
        f"nonempty_rows={nonempty}", f"pos_rows={sum(bool(pos_by_rank.get(n)) for n in range(1,1001))}",
        f"duplicate_front_groups_for_review={len(duplicate_fronts)}", f"problems={len(problems)}",
    ]
    if duplicate_fronts:
        debug.append("duplicate_fronts_for_review=" + repr(duplicate_fronts))
    debug.extend(problems)
    args.debug.write_text("\n".join(debug) + "\n", encoding="utf-8")

    if len(rows) != 1000 or nonempty != 1000 or problems:
        raise SystemExit(f"Published-list extraction failed closed; see {args.debug}")
    print(args.debug.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
