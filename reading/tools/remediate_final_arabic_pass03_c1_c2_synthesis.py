#!/usr/bin/env python3
"""Guarded Pass 03 remediation for C1/C2 synthesis distribution.

Each current C1/C2 passage has exactly one explicit synthesis item and a Q1 gist
item whose keyed answer already states the central issue/claim in a compact
sentence. The Ten-Question Standard expects two synthesis/reformulation/critical-
interpretation tasks at C levels. This remediation converts only Q1 from a gist
prompt into an explicit one-sentence summary task; the keyed answer is preserved
byte-for-byte.

Fail closed on any corpus/schema drift. Passage prose, lexical targets, grammar
metadata, all answers, IDs, and Q2-Q10 are invariant.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEVELS = ("c1", "c2")
SYNTHESIS_TYPES = {"paraphrase", "summary", "synthesis", "cross_text_synthesis"}
ARABIC_WORD = re.compile(r"[\u0621-\u064A]+")
PROMPTS = {
    "c1": "لخّص في جملة واحدة القضية المركزية التي يعالجها النص.",
    "c2": "لخّص في جملة واحدة القضية أو الإشكال المركزي الذي ينظم النص حوله تحليله أو تأويله.",
}


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def dump(path: Path, data: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in data), encoding="utf-8")


def answer_for(row: dict, qid: str) -> dict:
    hits = [a for a in row.get("answer_key", []) if isinstance(a, dict) and a.get("question_id") == qid]
    if len(hits) != 1:
        raise AssertionError(f"{row.get('id')}: expected exactly one answer for {qid}, got {len(hits)}")
    return hits[0]


def invariant_projection(row: dict) -> dict:
    """Everything except the deliberately changed Q1 prompt/type and quality notes."""
    x = copy.deepcopy(row)
    qs = x.get("questions", [])
    if qs:
        qs[0] = {k: v for k, v in qs[0].items() if k not in {"prompt", "type"}}
    quality = x.get("quality")
    if isinstance(quality, dict):
        quality.pop("notes", None)
    return x


def main() -> None:
    total_changed = 0
    for level in LEVELS:
        path = ROOT / f"reading/arabic/{level}/passages.jsonl"
        data = rows(path)
        if len(data) != 60:
            raise AssertionError(f"{level}: expected 60 passages, got {len(data)}")
        before = copy.deepcopy(data)

        for row in data:
            pid = row.get("id")
            qs = row.get("questions", [])
            if len(qs) != 10:
                raise AssertionError(f"{pid}: expected 10 questions, got {len(qs)}")
            q1 = qs[0]
            if q1.get("id") != "q1" or q1.get("type") != "gist":
                raise AssertionError(f"{pid}: Q1 contract drift: {q1.get('id')}/{q1.get('type')}")
            if any(q.get("type") == "summary" for q in qs):
                raise AssertionError(f"{pid}: already has summary; refuse ambiguous conversion")
            synthesis_before = sum(q.get("type") in SYNTHESIS_TYPES for q in qs)
            if synthesis_before != 1:
                raise AssertionError(f"{pid}: expected exactly one synthesis-role item before remediation, got {synthesis_before}")

            a1 = answer_for(row, "q1")
            answer_text = str(a1.get("answer", "")).strip()
            if len(ARABIC_WORD.findall(answer_text)) < 3:
                raise AssertionError(f"{pid}: Q1 answer too short to serve as a one-sentence summary: {answer_text!r}")

            q1["type"] = "summary"
            q1["prompt"] = PROMPTS[level]
            if answer_for(row, "q1") != a1:
                raise AssertionError(f"{pid}: answer changed unexpectedly")
            synthesis_after = sum(q.get("type") in SYNTHESIS_TYPES for q in qs)
            if synthesis_after != 2:
                raise AssertionError(f"{pid}: expected two synthesis-role items after remediation, got {synthesis_after}")

            quality = row.setdefault("quality", {})
            notes = quality.setdefault("notes", [])
            note = "Final Pass 03 remediation: converted the existing central-gist Q1 into an explicit one-sentence summary task; keyed answer and all passage/lexical content preserved."
            if note not in notes:
                notes.append(note)
            total_changed += 1

        for old, new in zip(before, data):
            if old.get("id") != new.get("id"):
                raise AssertionError("row order/id drift")
            if invariant_projection(old) != invariant_projection(new):
                raise AssertionError(f"{old.get('id')}: field outside Q1 prompt/type or quality.notes changed")
            old_answers = old.get("answer_key", [])
            new_answers = new.get("answer_key", [])
            if old_answers != new_answers:
                raise AssertionError(f"{old.get('id')}: answer_key drift")
            if old.get("text") != new.get("text"):
                raise AssertionError(f"{old.get('id')}: passage text drift")
            if old.get("new_lexical_targets") != new.get("new_lexical_targets"):
                raise AssertionError(f"{old.get('id')}: lexical target drift")
            if old.get("review_lexical_targets") != new.get("review_lexical_targets"):
                raise AssertionError(f"{old.get('id')}: review target drift")

        dump(path, data)

    if total_changed != 120:
        raise AssertionError(f"expected 120 passages changed, got {total_changed}")
    print(f"remediated_c_level_synthesis_passages={total_changed}")


if __name__ == "__main__":
    main()
