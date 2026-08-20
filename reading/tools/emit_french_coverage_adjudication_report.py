import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "reading" / "audit"
SRC = AUDIT / "french_coverage_adjudication_candidates_2026-08-19.json"
OUT = AUDIT / "french_coverage_adjudication_report_2026-08-19.md"


def intro_label(i):
    if not i:
        return "none"
    return f"{i.get('passage_id')} ({i.get('level')}, {i.get('form')!r}, rank {i.get('source_rank')})"


def main():
    x = json.loads(SRC.read_text(encoding="utf-8"))
    s = x["summary"]
    lines = [
        "# French coverage adjudication report — 2026-08-19",
        "",
        "> Candidate adjudication report. Nothing listed here is automatically a corpus defect.",
        "",
        "## Counts",
        f"- Chronology flags: {s['chronology_findings_total']} ({x['summary'].get('chronology_by_kind')})",
        f"- Duplicate introduction target IDs: {s['duplicate_target_ids_reconstructed']}",
        f"- Review-before-introduction cases: {s['review_before_intro_cases']}",
        f"- Question-before-introduction target IDs: {s['question_before_intro_target_ids']}",
        f"- Review-regression target IDs: {s['review_regression_target_ids']}",
        f"- Reconstructed unknown token instances: {s['unknown_candidate_token_instances_reconstructed']} across {s['unknown_candidate_types_reconstructed']} candidate types",
        f"- Passages over diagnostic unknown threshold: {s['over_threshold_passages']}",
        "",
        "## All duplicate first introductions",
    ]
    for d in x["duplicate_first_introductions"]:
        lines.append(f"- `{d['target_id']}`: " + " -> ".join(intro_label(i) for i in d["introductions"]))

    lines += ["", "## All review-before-introduction cases"]
    for r in x["review_before_introduction"]:
        f = r["finding"]
        lines.append(f"- `{f.get('target_id')}` reviewed at `{f.get('passage_id')}` stage `{f.get('review_stage')}`; introductions: " + ", ".join(intro_label(i) for i in r.get("introductions", [])))

    qgroups = x["question_before_introduction_groups"]
    introduced_later = [g for g in qgroups if g.get("ever_introduced")]
    never = [g for g in qgroups if not g.get("ever_introduced")]
    lines += [
        "", "## Question-target ordering",
        f"- Target IDs questioned before first declaration: {len(qgroups)}",
        f"- Introduced later: {len(introduced_later)}",
        f"- Never declared as new lexical target: {len(never)}",
        "- Top 20 by flag count:",
    ]
    for g in qgroups[:20]:
        ex = (g.get("question_occurrences_before_first_intro") or [{}])[0]
        lines.append(f"  - `{g['target_id']}` count={g['finding_count']}; eventual={intro_label(g.get('eventual_introduction'))}; first={ex.get('passage_id')} {ex.get('question_id')} [{ex.get('question_type')}]: {ex.get('prompt')}")

    lines += ["", "## Review-stage transition frequencies"]
    for transition, count in x["review_stage_transition_counts_all_targets"].items():
        lines.append(f"- `{transition}`: {count}")

    lines += ["", "## Top 15 target IDs with reported stage regressions"]
    for g in x["review_stage_regression_groups"][:15]:
        seq = " -> ".join((r.get("stage") or "?") for r in g.get("review_history", []))
        pids = ", ".join(r.get("passage_id", "?") for r in g.get("review_history", [])[:12])
        if len(g.get("review_history", [])) > 12:
            pids += ", ..."
        lines.append(f"- `{g['target_id']}` regressions={g['regression_count']}; stages={seq}; passages={pids}")

    lines += ["", "## All passages over unknown-token diagnostic threshold"]
    for p in x["over_threshold_passages"]:
        cand = "; ".join(f"{a} ×{b}" for a,b in p.get("unknown_candidates", [])[:12])
        lines.append(f"- `{p['passage_id']}` {p['level']} {p['passage_type']}: rate={p['unknown_rate']:.4f}, threshold={p['threshold']:.4f}; {cand}")

    lines += ["", "## Top 30 uncontrolled-unknown candidates"]
    for u in x["unknown_candidates_ranked"][:30]:
        refs = ", ".join(f"{p['passage_id']}×{p['count']}" for p in u.get("passages", [])[:8])
        lines.append(f"- `{u['candidate']}` ×{u['count']}: {refs}")

    lines += [
        "", "## Required adjudication order",
        "1. Decide whether duplicate introductions are true duplicate R0s, intentional level resets, or metadata errors.",
        "2. Decide the single review-before-introduction case from its actual passage context.",
        "3. Separate question-target flags caused by non-lexical/support IDs from genuine future-target leakage.",
        "4. Compare review-stage transitions to the repository's spaced-reinforcement contract; do not assume global monotonicity if the standard does not require it.",
        "5. Adjudicate all threshold-failing passages and the high-frequency unknown candidates before any coverage PASS.",
        "6. Do not populate `estimated_known_token_coverage` from support coverage or planned contacts alone.",
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
