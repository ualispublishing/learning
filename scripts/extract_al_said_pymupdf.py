#!/usr/bin/env python3
"""Extract Al-Said 2023 Table 4 with PyMuPDF word coordinates.

Source: Almoataz B. Al-Said (2023), "A New List of Common Words in Modern
Standard Arabic", MEAH Sección Árabe-Islam 72, pp. 287-351, Table 4, CC BY 4.0.

The PDF is RTL and PyMuPDF can split one Arabic word into visual fragments. The
published table also intentionally groups some vocalized/shape variants under one
rank. This extractor therefore preserves the *rank* as the authoritative unit:

1. recover ranks 1..1000 from the stable rank column in strict visual order;
2. reconstruct each Arabic variant using PyMuPDF's page/block/line grouping and
   right-to-left fragment order;
3. attach each variant and POS code to its nearest rank baseline;
4. preserve distinct published orthographic variants on one Arabic-only front;
5. fail closed unless every rank has a front and the 1000 rank-front records are
   distinct as records.

This extracts inventory evidence only. It never invents translations, roots,
examples, or synonyms.
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
    dist, rank = min(opts, key=lambda x: (x[0], x[1]))
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
    for pno in range(18, 62):  # PDF pages 19..62, 1-based
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

    # Rank anchors: stable rightmost numeric column. Strict visual progression rejects
    # article page numbers that happen to equal a vocabulary rank.
    by_rank: dict[int, list[dict]] = defaultdict(list)
    for t in tokens:
        if not INT_RE.fullmatch(t["text"]):
            continue
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
    if any(b <= a for a, b in zip(anchor_gys, anchor_gys[1:])):
        raise SystemExit("Rank anchors are not strictly monotonic")

    # Arabic word-cell fragments. Widen the right boundary enough to include initial
    # letters such as ن in نَفَس / نَشَر / نَحْنُ, which extend beyond x=435 in this PDF.
    # Grouping by PyMuPDF page/block/line is more robust than y quantization: detached
    # suffix glyphs such as ة / ت / ية remain members of the same logical word line.
    fragments: list[dict] = []
    for t in tokens:
        if not AR.search(t["text"]):
            continue
        if not (345.0 <= t["x0"] <= 443.5 and 404.0 <= t["x1"] <= 446.5):
            continue
        if not (165.0 <= t["cy"] <= 665.0):
            continue
        fragments.append(t)

    line_groups: dict[tuple[int, int, int], list[dict]] = defaultdict(list)
    for t in fragments:
        line_groups[(t["page"], t["block"], t["line"])].append(t)

    reconstructed = []
    for group in line_groups.values():
        ordered = sorted(group, key=lambda t: (t["x0"], t["word"]), reverse=True)
        k = "".join(arabic_letters(t["text"]) for t in ordered)
        if not k:
            continue
        gy = sum(global_y(t) for t in group) / len(group)
        rank, dist = nearest_rank(anchor_gys, gy)
        if dist > 7.75:
            continue
        reconstructed.append({
            "rank": rank,
            "gy": gy,
            "key": k,
            "raw": " + ".join(t["text"] for t in ordered),
        })

    lines_by_rank: dict[int, list[dict]] = defaultdict(list)
    for line in reconstructed:
        lines_by_rank[line["rank"]].append(line)

    pos_by_rank: dict[int, list[str]] = defaultdict(list)
    for t in tokens:
        if not POS_RE.fullmatch(t["text"]):
            continue
        rank, dist = nearest_rank(anchor_gys, global_y(t))
        if dist <= 7.75 and t["text"] not in pos_by_rank[rank]:
            pos_by_rank[rank].append(t["text"])

    rows = []
    problems = []
    front_records = set()

    for rank in range(1, 1001):
        group = sorted(lines_by_rank.get(rank, []), key=lambda x: x["gy"])
        if not group:
            problems.append(f"rank={rank}: no Arabic word-cell variant")
            rows.append({"rank": rank, "front": "", "variants_raw": "", "pos_codes": "", "source": "Al-Said 2023 Table 4"})
            continue

        keys = []
        traces = []
        for line in group:
            if line["key"] not in keys:
                keys.append(line["key"])
            if line["raw"] not in traces:
                traces.append(line["raw"])

        # PDF extraction can occasionally produce a truncated duplicate variant (e.g.
        # فس beside نفس). If one form is a strict substring of another, discard only the
        # shorter extraction artifact. Genuine shape variants such as مؤكد / مؤكدا remain.
        cleaned_keys = []
        for k in keys:
            if any(k != other and k in other for other in keys):
                continue
            if k not in cleaned_keys:
                cleaned_keys.append(k)
        if not cleaned_keys:
            cleaned_keys = keys

        front = " / ".join(cleaned_keys)
        if not front:
            problems.append(f"rank={rank}: empty reconstructed front")

        # The rank is part of record identity because the paper may deliberately group or
        # repeat related surface spellings. We still surface exact duplicate front strings
        # later for manual lexical validation rather than rejecting source extraction.
        record_id = (rank, front)
        if record_id in front_records:
            problems.append(f"rank={rank}: duplicate record identity")
        front_records.add(record_id)

        rows.append({
            "rank": rank,
            "front": front,
            "variants_raw": " | ".join(traces),
            "pos_codes": " | ".join(pos_by_rank.get(rank, [])),
            "source": "Al-Said 2023 Table 4",
        })

    nonempty = sum(bool(r["front"]) for r in rows)
    duplicate_fronts: dict[str, list[int]] = defaultdict(list)
    for r in rows:
        if r["front"]:
            duplicate_fronts[r["front"]].append(int(r["rank"]))
    duplicate_fronts = {k: v for k, v in duplicate_fronts.items() if len(v) > 1}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)

    debug_lines = [
        f"tokens={len(tokens)}",
        "rank_anchors=1000",
        f"arabic_fragments={len(fragments)}",
        f"reconstructed_variant_lines={len(reconstructed)}",
        f"nonempty_rows={nonempty}",
        f"pos_rows={sum(bool(pos_by_rank.get(n)) for n in range(1,1001))}",
        f"duplicate_front_groups_for_review={len(duplicate_fronts)}",
        f"problems={len(problems)}",
    ]
    if duplicate_fronts:
        debug_lines.append("duplicate_fronts_for_review=" + repr(duplicate_fronts))
    debug_lines.extend(problems)
    args.debug.write_text("\n".join(debug_lines) + "\n", encoding="utf-8")

    if nonempty != 1000 or len(rows) != 1000 or problems:
        raise SystemExit(f"Published-list extraction failed closed; see {args.debug}")
    print(args.debug.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
