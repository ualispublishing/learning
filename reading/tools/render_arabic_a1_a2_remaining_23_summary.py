#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "reading" / "audit" / "arabic_a1_a2_remaining_23_2026-08-23.json"
OUT = ROOT / "reading" / "audit" / "arabic_a1_a2_remaining_23_summary_2026-08-23.md"

def esc(s):
    return str(s or "").replace("|", "\\|").replace("\n", " ")

def extract_forms(item):
    sb = item.get("source_blocker", {})
    hits = sb.get("hits", []) or []
    c = Counter(h.get("token") for h in hits if h.get("token"))
    if not c:
        return "—"
    return ", ".join(f"{k}×{v}" for k, v in c.most_common())

def qtypes(item):
    qs = item.get("questions_assessing_target", []) or []
    return ", ".join(q.get("question", {}).get("type", "?") for q in qs) or "—"

def main():
    data = json.loads(SRC.read_text(encoding="utf-8"))
    if data.get("count") != 23:
        raise SystemExit(f"Expected 23 blockers, got {data.get('count')}")
    lines = [
        "# Arabic A1/A2 remaining 23 — decision sheet",
        "",
        f"Input A1 blob: `{data['input_blobs']['a1']}`  ",
        f"Input A2 blob: `{data['input_blobs']['a2']}`  ",
        f"Total: **{data['count']}** — new-target realization: **{data['new_target_realization_count']}**; exposure-count contract: **{data['exposure_count_contract_count']}**.",
        "",
        "| # | Kind | Passage | Target | Lemma / POS | Declared | Supported | Actual supported forms | Qs assessing target |",
        "|---:|---|---|---|---|---:|---:|---|---|",
    ]
    for item in data["items"]:
        tr = item.get("target_record", {})
        sb = item.get("source_blocker", {})
        lines.append(
            f"| {esc(item['blocker_id'])} | {esc(item['kind'])} | {esc(item['passage_id'])} | **{esc(tr.get('form'))}** | {esc(tr.get('lemma'))} / {esc(tr.get('part_of_speech'))} | {esc(sb.get('declared'))} | {esc(sb.get('supported_count'))} | {esc(extract_forms(item))} | {esc(qtypes(item))} |"
        )
    lines += ["", "## Per-case evidence", ""]
    for item in data["items"]:
        tr = item.get("target_record", {})
        sb = item.get("source_blocker", {})
        lines += [
            f"### {item['blocker_id']} — {item['passage_id']} — {tr.get('form')}",
            f"- Kind: `{item['kind']}`; intended sense: {tr.get('intended_sense')}",
            f"- Lemma/POS: `{tr.get('lemma')}` / `{tr.get('part_of_speech')}`",
            f"- Declared exposures: **{sb.get('declared')}**; supported realizations: **{sb.get('supported_count')}**; forms: {extract_forms(item)}",
            f"- Passage: {item.get('text')}",
        ]
        for qa in item.get("questions_assessing_target", []) or []:
            q = qa.get("question", {})
            a = qa.get("answer", {})
            lines.append(f"- {q.get('id')} `{q.get('type')}`: {q.get('prompt')} → **{a.get('answer')}**")
        lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} with {len(data['items'])} cases")

if __name__ == "__main__":
    main()
