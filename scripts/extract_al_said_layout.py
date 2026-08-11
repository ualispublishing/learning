#!/usr/bin/env python3
"""Extract the ranked MSA inventory from Al-Said 2023 using layout-preserved text.

Poppler's -layout output keeps the table columns far more faithfully than its per-glyph
TSV for this RTL PDF. Rank rows are identified by their frequency metrics; each POS +
Arabic variant line is assigned to the nearest rank anchor. The article groups vocalized
homographs under a single undiacritized rank, so every variant assigned to one rank must
reduce to the same Arabic-letter key. The script fails closed on ambiguity.
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
POS_TOKEN = r"(?:N\\[A-Z]+|V\\[A-Z]+|P\\[A-Z]+|ADV|ADJ|PRO|KH)"
POS_RE = re.compile(rf"\b({POS_TOKEN})\b")
DEC_RE = re.compile(r"(?<!\d)\d+\.\d+(?!\d)")
INT_RE = re.compile(r"(?<!\d)(\d{1,7})(?!\d)")
RANK_END_RE = re.compile(r"(?<!\d)(\d{1,4})\s*$")


def clean(s: str) -> str:
    return unicodedata.normalize("NFC", (s or "").translate(BIDI)).strip("\n")


def undiac(s: str) -> str:
    return DIAC.sub("", clean(s).replace("ـ", ""))


def arabic_key(s: str) -> str:
    return "".join(AR.findall(undiac(s)))


def is_metric_rank_line(line: str):
    line = clean(line)
    m = RANK_END_RE.search(line)
    if not m:
        return None
    rank = int(m.group(1))
    if not 1 <= rank <= 1000:
        return None
    nums = [int(x) for x in INT_RE.findall(line)]
    has_frequency = any(n >= 10000 for n in nums)
    # Most rows contain two percentages; a few PDF rows split one percentage token.
    if not has_frequency or len(DEC_RE.findall(line)) < 1:
        return None
    return rank


def variant_from_line(line: str):
    line = clean(line)
    m = POS_RE.search(line)
    if not m:
        return None
    tail = line[m.end():]
    # Drop the rank if the Arabic variant shares the metric line.
    tail = RANK_END_RE.sub("", tail)
    key = arabic_key(tail)
    if not key:
        return None
    # Reconstruct a readable vocalized variant by retaining Arabic letters/marks only.
    # Spaces inserted inside Arabic words by PDF layout are removed; separate lexical
    # variants occur on separate POS lines rather than as whitespace-separated words.
    chars = []
    for ch in tail:
        o = ord(ch)
        if AR.fullmatch(ch) or (0x0610 <= o <= 0x061A) or (0x064B <= o <= 0x065F) or o == 0x0670 or (0x06D6 <= o <= 0x06ED):
            chars.append(ch)
    vocalized = unicodedata.normalize("NFC", "".join(chars))
    return m.group(1), key, vocalized


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=Path("audit/al_said_2023_msa1000.csv"))
    ap.add_argument("--debug", type=Path, default=Path("audit/al_said_2023_msa1000_debug.txt"))
    args = ap.parse_args()

    lines = args.text.read_text(encoding="utf-8", errors="replace").splitlines()
    anchors = {}
    duplicate_anchors = defaultdict(list)
    for i, line in enumerate(lines):
        rank = is_metric_rank_line(line)
        if rank is not None:
            duplicate_anchors[rank].append(i)

    # The table occupies a continuous sequence. For duplicate numeric hits, choose the
    # occurrence that yields a monotonic 1..1000 sequence. Greedy is safe because each
    # real rank appears once and page/footer numbers fail the metric test.
    prev = -1
    for rank in range(1, 1001):
        choices = [i for i in duplicate_anchors.get(rank, []) if i > prev]
        if not choices:
            raise SystemExit(f"Missing rank anchor {rank}; candidates={duplicate_anchors.get(rank, [])}")
        anchors[rank] = choices[0]
        prev = choices[0]

    anchor_items = [(rank, anchors[rank]) for rank in range(1, 1001)]
    variants_by_rank = defaultdict(list)
    pos_by_rank = defaultdict(list)

    # Assign every POS+Arabic line to the nearest rank anchor by line distance. Cap the
    # radius so prose outside the table cannot attach to a rank.
    anchor_indices = [idx for _, idx in anchor_items]
    for i, line in enumerate(lines):
        parsed = variant_from_line(line)
        if not parsed:
            continue
        pos, key, vocalized = parsed
        # Binary search would be overkill for 1k*~3k; linear neighboring anchors via
        # bisect is clear and deterministic.
        import bisect
        j = bisect.bisect_left(anchor_indices, i)
        candidates = []
        if j < len(anchor_indices):
            candidates.append((abs(anchor_indices[j] - i), j + 1))
        if j > 0:
            candidates.append((abs(anchor_indices[j - 1] - i), j))
        if not candidates:
            continue
        dist, rank = min(candidates, key=lambda x: (x[0], x[1]))
        if dist > 4:
            continue
        item = (pos, key, vocalized, i)
        if item not in variants_by_rank[rank]:
            variants_by_rank[rank].append(item)

    rows = []
    problems = []
    for rank in range(1, 1001):
        vals = variants_by_rank.get(rank, [])
        if not vals:
            problems.append(f"rank={rank} no POS+Arabic variant within 4 lines of anchor={anchors[rank]}")
            rows.append({"rank": rank, "front": "", "variants": "", "pos_codes": "", "source": "Al-Said 2023 Table 4"})
            continue
        groups = defaultdict(list)
        for pos, key, vocalized, i in vals:
            groups[key].append((pos, vocalized, i))

        # Correct group should dominate by proximity to anchor. If multiple spellings
        # remain, choose only when one is strictly closer; otherwise fail closed.
        scores = []
        for key, group in groups.items():
            mind = min(abs(i - anchors[rank]) for _, _, i in group)
            scores.append((mind, -len(group), key))
        scores.sort()
        best = scores[0]
        if len(scores) > 1 and scores[1][:2] == best[:2]:
            problems.append(f"rank={rank} ambiguous keys={dict((k, [(p,v,i) for p,v,i in g]) for k,g in groups.items())}")
            chosen_key = ""
            chosen = []
        else:
            chosen_key = best[2]
            chosen = groups[chosen_key]

        vocs = []
        poss = []
        for pos, vocalized, _ in sorted(chosen, key=lambda x: x[2]):
            if vocalized and vocalized not in vocs:
                vocs.append(vocalized)
            if pos not in poss:
                poss.append(pos)
        rows.append({
            "rank": rank,
            "front": chosen_key,
            "variants": " | ".join(vocs),
            "pos_codes": " | ".join(poss),
            "source": "Al-Said 2023 Table 4",
        })

    nonempty = sum(bool(r["front"]) for r in rows)
    unique = len({r["front"] for r in rows if r["front"]})
    duplicate_fronts = defaultdict(list)
    for r in rows:
        if r["front"]:
            duplicate_fronts[r["front"]].append(r["rank"])
    duplicate_fronts = {k: v for k, v in duplicate_fronts.items() if len(v) > 1}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(rows)

    debug_lines = [
        f"lines={len(lines)}", f"anchors=1000", f"nonempty={nonempty}",
        f"unique_orthographic_fronts={unique}", f"duplicate_front_groups={len(duplicate_fronts)}",
        f"problems={len(problems)}",
    ]
    if duplicate_fronts:
        debug_lines.append("duplicate_fronts=" + repr(duplicate_fronts))
    debug_lines.extend(problems)
    args.debug.write_text("\n".join(debug_lines) + "\n", encoding="utf-8")

    if nonempty != 1000 or problems:
        raise SystemExit(f"Layout extraction failed closed; see {args.debug}")
    print(args.debug.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
