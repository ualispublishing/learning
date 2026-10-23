import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "reading" / "audit"
SRC = AUDIT / "french_coverage_adjudication_candidates_2026-08-19.json"
OUT = AUDIT / "french_coverage_adjudication_brief_2026-08-19.json"


def main():
    x = json.loads(SRC.read_text(encoding="utf-8"))
    qgroups = x["question_before_introduction_groups"]
    rgroups = x["review_stage_regression_groups"]
    q_status = Counter("introduced_later" if g.get("ever_introduced") else "never_declared_new_target" for g in qgroups)
    q_level = Counter()
    for g in qgroups:
        for q in g.get("question_occurrences_before_first_intro", []):
            q_level[q.get("level")] += 1
    r_level = Counter()
    for g in rgroups:
        for f in g.get("reported_regressions", []):
            pid = f.get("passage_id", "")
            if pid.startswith("fr-"):
                r_level[pid.split("-")[1].upper()] += 1

    brief = {
        "schema_version": 1,
        "date": "2026-08-19",
        "language": "fr",
        "warning": "Semantic-adjudication candidates; not automatically defects.",
        "summary": x["summary"],
        "duplicate_first_introductions_all": x["duplicate_first_introductions"],
        "review_before_introduction_all": x["review_before_introduction"],
        "question_before_introduction_aggregate": {
            "target_group_status": dict(q_status),
            "question_occurrence_levels": dict(q_level),
            "top30_target_groups": [
                {
                    "target_id": g["target_id"], "finding_count": g["finding_count"],
                    "ever_introduced": g["ever_introduced"], "eventual_introduction": g.get("eventual_introduction"),
                    "question_type_counts": g.get("question_type_counts", {}),
                    "first_examples": g.get("question_occurrences_before_first_intro", [])[:2],
                }
                for g in qgroups[:30]
            ],
        },
        "review_stage_regression_aggregate": {
            "target_ids": len(rgroups),
            "regression_occurrence_levels": dict(r_level),
            "all_stage_transition_counts": x["review_stage_transition_counts_all_targets"],
            "top30_target_groups": [
                {
                    "target_id": g["target_id"], "regression_count": g["regression_count"],
                    "introductions": g.get("introductions", []),
                    "stage_sequence": [r.get("stage") for r in g.get("review_history", [])],
                    "stage_passages": [r.get("passage_id") for r in g.get("review_history", [])],
                }
                for g in rgroups[:30]
            ],
        },
        "over_threshold_passages_all": x["over_threshold_passages"],
        "unknown_candidates_top50": x["unknown_candidates_ranked"][:50],
    }
    OUT.write_text(json.dumps(brief, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(brief, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
