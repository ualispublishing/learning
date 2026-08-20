import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
AUDIT = READING / "audit"
LEVELS = ["a1", "a2", "b1", "b2", "c1", "c2"]


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    source_path = AUDIT / "french_coverage_evidence_2026-08-19.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))

    corpus = []
    by_id = {}
    intro_occurrences = defaultdict(list)
    review_occurrences = defaultdict(list)
    question_occurrences = defaultdict(list)
    global_index = 0
    for level in LEVELS:
        rows = load_jsonl(READING / "french" / level / "passages.jsonl")
        for p in rows:
            global_index += 1
            entry = {"level": level.upper(), "global_index": global_index, "passage": p}
            corpus.append(entry)
            by_id[p["id"]] = entry
            for t in p.get("new_lexical_targets", []):
                intro_occurrences[t["id"]].append({
                    "passage_id": p["id"], "level": level.upper(), "global_index": global_index,
                    "form": t.get("form"), "lemma": t.get("lemma"), "source_rank": t.get("source_rank"),
                })
            for r in p.get("review_lexical_targets", []):
                review_occurrences[r["id"]].append({
                    "passage_id": p["id"], "level": level.upper(), "global_index": global_index,
                    "form": r.get("form"), "stage": r.get("review_stage"), "representation": r.get("representation"),
                })
            for q in p.get("questions", []):
                for tid in q.get("target_ids", []):
                    question_occurrences[tid].append({
                        "passage_id": p["id"], "level": level.upper(), "global_index": global_index,
                        "question_id": q.get("id"), "question_type": q.get("type"), "prompt": q.get("prompt"),
                    })

    chronology = source.get("chronology_findings", [])
    by_kind = defaultdict(list)
    for f in chronology:
        by_kind[f.get("kind", "UNKNOWN")].append(f)

    duplicates = []
    for tid, occs in intro_occurrences.items():
        if len(occs) > 1:
            duplicates.append({"target_id": tid, "introduction_count": len(occs), "introductions": occs})
    duplicates.sort(key=lambda x: x["target_id"])

    review_before = []
    for f in by_kind.get("review_before_declared_introduction", []):
        tid = f.get("target_id")
        review_before.append({
            "finding": f,
            "introductions": intro_occurrences.get(tid, []),
            "all_reviews": review_occurrences.get(tid, []),
            "question_uses": question_occurrences.get(tid, [])[:20],
        })

    q_before_groups = []
    q_before = by_kind.get("question_target_before_declared_introduction", [])
    q_by_tid = defaultdict(list)
    for f in q_before:
        q_by_tid[f.get("target_id")].append(f)
    for tid, fs in q_by_tid.items():
        intros = intro_occurrences.get(tid, [])
        first_intro_index = intros[0]["global_index"] if intros else None
        q_rows = question_occurrences.get(tid, [])
        before_rows = [q for q in q_rows if first_intro_index is None or q["global_index"] < first_intro_index]
        q_before_groups.append({
            "target_id": tid,
            "finding_count": len(fs),
            "eventual_introduction": intros[0] if intros else None,
            "ever_introduced": bool(intros),
            "review_occurrences_before_first_intro": [r for r in review_occurrences.get(tid, []) if first_intro_index is None or r["global_index"] < first_intro_index],
            "question_occurrences_before_first_intro": before_rows[:50],
            "question_type_counts": dict(Counter(q.get("question_type") for q in before_rows)),
        })
    q_before_groups.sort(key=lambda x: (-x["finding_count"], x["target_id"] or ""))

    stage_regression_groups = []
    regressions = by_kind.get("review_stage_regression", [])
    reg_by_tid = defaultdict(list)
    for f in regressions:
        reg_by_tid[f.get("target_id")].append(f)
    for tid, fs in reg_by_tid.items():
        stage_regression_groups.append({
            "target_id": tid,
            "regression_count": len(fs),
            "introductions": intro_occurrences.get(tid, []),
            "review_history": review_occurrences.get(tid, []),
            "reported_regressions": fs,
        })
    stage_regression_groups.sort(key=lambda x: (-x["regression_count"], x["target_id"] or ""))

    # Reconstruct unknown-candidate occurrences from each passage's saved top candidates.
    unknown_by_key = defaultdict(lambda: {"count": 0, "passages": []})
    over_threshold = []
    for p in source.get("passages", []):
        candidates = p.get("top_uncontrolled_unknown_candidates", [])
        for pair in candidates:
            if not isinstance(pair, list) or len(pair) != 2:
                continue
            key, count = pair
            unknown_by_key[key]["count"] += count
            unknown_by_key[key]["passages"].append({"passage_id": p["id"], "level": p["level"], "count": count})
        if p.get("support_gate") != "PASS":
            live = by_id.get(p["id"], {})
            text = live.get("passage", {}).get("text")
            over_threshold.append({
                "passage_id": p["id"], "level": p["level"], "sequence": p.get("sequence"),
                "passage_type": p.get("passage_type"),
                "unknown_rate": p.get("uncontrolled_unknown_candidate_rate"),
                "threshold": p.get("uncontrolled_unknown_candidate_threshold"),
                "unknown_candidates": candidates,
                "text": text,
            })
    unknown_ranked = [
        {"candidate": k, "count": v["count"], "passages": v["passages"]}
        for k, v in unknown_by_key.items()
    ]
    unknown_ranked.sort(key=lambda x: (-x["count"], x["candidate"]))

    # Stage-pattern summary helps determine whether regressions reflect policy or bad labels.
    stage_transition_counts = Counter()
    for tid, reviews in review_occurrences.items():
        for prev, cur in zip(reviews, reviews[1:]):
            stage_transition_counts[f"{prev.get('stage')}->{cur.get('stage')}"] += 1

    result = {
        "schema_version": 1,
        "date": "2026-08-19",
        "language": "fr",
        "source_audit": str(source_path.relative_to(ROOT)),
        "source_status": source.get("status"),
        "purpose": "Compact semantic-adjudication input. Counts are candidates, not automatically corpus defects.",
        "summary": {
            "chronology_findings_total": len(chronology),
            "chronology_by_kind": {k: len(v) for k, v in sorted(by_kind.items())},
            "duplicate_target_ids_reconstructed": len(duplicates),
            "review_before_intro_cases": len(review_before),
            "question_before_intro_target_ids": len(q_before_groups),
            "review_regression_target_ids": len(stage_regression_groups),
            "unknown_candidate_types_reconstructed": len(unknown_ranked),
            "unknown_candidate_token_instances_reconstructed": sum(x["count"] for x in unknown_ranked),
            "over_threshold_passages": len(over_threshold),
        },
        "duplicate_first_introductions": duplicates,
        "review_before_introduction": review_before,
        "question_before_introduction_groups": q_before_groups,
        "review_stage_regression_groups": stage_regression_groups,
        "review_stage_transition_counts_all_targets": dict(stage_transition_counts.most_common()),
        "over_threshold_passages": over_threshold,
        "unknown_candidates_ranked": unknown_ranked,
    }
    out = AUDIT / "french_coverage_adjudication_candidates_2026-08-19.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": result["summary"], "top_unknown": unknown_ranked[:25], "over_threshold": over_threshold}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
