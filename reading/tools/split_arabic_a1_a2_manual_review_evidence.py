#!/usr/bin/env python3
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "reading" / "audit" / "arabic_a1_a2_manual_review_evidence_2026-08-23.json"
OUTDIR = ROOT / "reading" / "audit" / "arabic_a1_a2_manual_review_units"
A1 = ROOT / "reading" / "arabic" / "a1" / "passages.jsonl"
A2 = ROOT / "reading" / "arabic" / "a2" / "passages.jsonl"
EXPECTED = {
    "a1": "4723cb4c9974a9a9c84b6c030d9c1a30c0820500",
    "a2": "d6a10dddde14628c8e4a7ddb4db7781604852210",
}


def blob(path):
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def compact_item(item):
    warning = item.get("warning", {})
    qe = item.get("question_evidence") or {}
    return {
        "review_id": item.get("review_id"),
        "classification": item.get("classification"),
        "warning_code": item.get("warning_code"),
        "passage_id": item.get("passage_id"),
        "sequence": item.get("sequence"),
        "title": item.get("title"),
        "target_id": item.get("target_id"),
        "target_form": item.get("target_form"),
        "target_metadata": item.get("target_metadata"),
        "introduction": item.get("introduction"),
        "warning": warning,
        "text": item.get("full_text"),
        "top_surface_candidates": (item.get("surface_candidate_tokens") or [])[:6],
        "candidate_sentence_hits": item.get("candidate_sentence_hits"),
        "question_evidence": None if not qe else {
            "question": qe.get("question"),
            "answer": qe.get("answer"),
            "target_id_is_locally_declared": qe.get("target_id_is_locally_declared"),
            "local_new_targets": qe.get("local_new_targets"),
            "local_review_targets": qe.get("local_review_targets"),
        },
    }


def main():
    actual = {"a1": blob(A1), "a2": blob(A2)}
    if actual != EXPECTED:
        raise SystemExit(f"Unexpected corpus blobs: {actual}")
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    if source.get("packet_count") != 107:
        raise SystemExit("Expected 107-item evidence packet")
    grouped = defaultdict(list)
    for item in source.get("items", []):
        pid = str(item.get("passage_id"))
        m = re.search(r"ar-(a1|a2)-u(\d{2})", pid)
        if not m:
            raise SystemExit(f"Cannot group {pid}")
        grouped[f"{m.group(1)}-u{m.group(2)}"].append(compact_item(item))
    OUTDIR.mkdir(parents=True, exist_ok=True)
    manifest = {"schema_version": 1, "date": "2026-08-23", "input_blobs": actual, "total_items": 0, "units": []}
    for key in sorted(grouped):
        items = grouped[key]
        path = OUTDIR / f"{key}.json"
        payload = {"unit_key": key, "count": len(items), "items": items}
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest["units"].append({"unit_key": key, "count": len(items), "path": str(path.relative_to(ROOT))})
        manifest["total_items"] += len(items)
    (OUTDIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
