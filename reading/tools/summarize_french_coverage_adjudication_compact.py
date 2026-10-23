import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "reading" / "audit"
SRC = AUDIT / "french_coverage_adjudication_candidates_2026-08-19.json"
OUT = AUDIT / "french_coverage_adjudication_digest_2026-08-19.json"


def main():
    x = json.loads(SRC.read_text(encoding="utf-8"))
    qgroups = []
    for g in x["question_before_introduction_groups"]:
        rows = g.get("question_occurrences_before_first_intro", [])
        qgroups.append({
            "target_id": g["target_id"],
            "finding_count": g["finding_count"],
            "ever_introduced": g["ever_introduced"],
            "eventual_introduction": g.get("eventual_introduction"),
            "review_occurrences_before_first_intro": g.get("review_occurrences_before_first_intro", [])[:5],
            "question_type_counts": g.get("question_type_counts", {}),
            "first_examples": rows[:3],
            "last_examples": rows[-2:] if len(rows) > 3 else [],
        })
    rgroups = []
    for g in x["review_stage_regression_groups"]:
        hist = g.get("review_history", [])
        rgroups.append({
            "target_id": g["target_id"],
            "regression_count": g["regression_count"],
            "introductions": g.get("introductions", []),
            "stage_sequence": [{"passage_id": r["passage_id"], "level": r["level"], "stage": r.get("stage")} for r in hist],
            "reported_regressions": g.get("reported_regressions", []),
        })
    digest = {
        "schema_version": 1,
        "date": "2026-08-19",
        "language": "fr",
        "source": str(SRC.relative_to(ROOT)),
        "warning": "Candidate digest for semantic adjudication; entries are not automatically defects.",
        "summary": x["summary"],
        "duplicate_first_introductions": x["duplicate_first_introductions"],
        "review_before_introduction": x["review_before_introduction"],
        "question_before_introduction_groups": qgroups,
        "review_stage_regression_groups": rgroups,
        "review_stage_transition_counts_all_targets": x["review_stage_transition_counts_all_targets"],
        "over_threshold_passages": x["over_threshold_passages"],
        "unknown_candidates_top100": x["unknown_candidates_ranked"][:100],
    }
    OUT.write_text(json.dumps(digest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "summary": digest["summary"],
        "duplicate_first_introductions": digest["duplicate_first_introductions"],
        "review_before_introduction": digest["review_before_introduction"],
        "top_question_before_groups": qgroups[:20],
        "top_stage_regression_groups": rgroups[:20],
        "stage_transitions": digest["review_stage_transition_counts_all_targets"],
        "over_threshold_passages": digest["over_threshold_passages"],
        "unknown_top25": digest["unknown_candidates_top100"][:25],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
