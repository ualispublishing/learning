import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
SRC = READING / "audit" / "french_coverage_evidence_2026-08-19.json"
FUNCTION_SUPPORT = READING / "planning" / "a1_function_support.json"
OUT = READING / "audit" / "french_coverage_methodology_correction_v2_2026-08-19.json"

# Additional fixed-linker lemmas are kept separate from the repository's explicit
# function-support list so this diagnostic does not pretend they were already
# policy-approved. They remain candidates for the full NLP v2 implementation.
LINKER_CANDIDATES = {"tandis", "afin"}


def main():
    x = json.loads(SRC.read_text(encoding="utf-8"))
    fs = json.loads(FUNCTION_SUPPORT.read_text(encoding="utf-8"))
    repo_function_forms = {str(v).casefold() for v in fs["french"]["function_forms"]}

    visible_policy_hits = {}
    visible_linker_hits = {}
    retained = []
    for label, count in x.get("top_uncontrolled_unknown_candidates", []):
        lemma = label.split(" | upos=", 1)[0].casefold()
        if lemma in repo_function_forms:
            visible_policy_hits[lemma] = visible_policy_hits.get(lemma, 0) + int(count)
        elif lemma in LINKER_CANDIDATES:
            visible_linker_hits[lemma] = visible_linker_hits.get(lemma, 0) + int(count)
            retained.append([label, count])
        else:
            retained.append([label, count])

    out = {
        "schema_version": 2,
        "date": "2026-08-19",
        "language": "fr",
        "status": "METHODOLOGY_CORRECTION_DO_NOT_AUTOPROMOTE",
        "source_artifact": "reading/audit/french_coverage_evidence_2026-08-19.json",
        "bound_canonical_hashes": x.get("bound_canonical_hashes"),
        "methodology_findings": [
            {
                "severity": "major",
                "kind": "v1_ignored_repository_function_support_inventory",
                "evidence": "v1 classifier used UD closed-class POS only and did not load reading/planning/a1_function_support.json; that repository file explicitly lists French forms such as ne, n, y, en, où, parce, donc and contractions as function support."
            },
            {
                "severity": "major",
                "kind": "pr11_surface_reconstruction_not_authoritative",
                "evidence": "PR #11 reconstructed occurrence candidates rather than preserving the v1 token-level category decision; its top queue includes forms such as vers/que/pour that can already be classified as grammar/function or ranked support in the source audit."
            },
            {
                "severity": "major",
                "kind": "known_coverage_not_derivable_from_static_support",
                "evidence": "LEXICAL_COVERAGE_POLICY distinguishes supported curriculum coverage from actual learner-known coverage; stored zero values must not be replaced by support percentages without telemetry/mastery evidence."
            }
        ],
        "repository_function_forms": sorted(repo_function_forms),
        "v1_uncontrolled_unknown_token_count": int(x.get("classification_counts", {}).get("uncontrolled_unknown_candidate", 0)),
        "policy_declared_function_hits_visible_in_v1_top150": sum(visible_policy_hits.values()),
        "policy_declared_function_hits_by_lemma_visible_in_v1_top150": dict(sorted(visible_policy_hits.items())),
        "additional_linker_candidates_visible_in_v1_top150_not_yet_auto_reclassified": dict(sorted(visible_linker_hits.items())),
        "top_remaining_v1_candidates_after_policy_declared_function_filter": retained[:50],
        "limitations": [
            "The v1 artifact only publishes the global top 150 unresolved types and per-passage top 25, so this compact correction cannot compute exact corrected coverage rates.",
            "A full Stanza rerun is required with repository function-support forms integrated at token classification time.",
            "No canonical passage or quality metadata is changed by this diagnostic."
        ],
        "required_v2_classifier_order": [
            "situational_proper_or_number",
            "repository_function_form_or_closed_class_POS",
            "controlled_new_target",
            "scheduled_review_target",
            "prior_curriculum_support_proxy",
            "verified_pedagogical_support",
            "ranked_backbone",
            "uncontrolled_unknown_candidate"
        ],
        "decision": {
            "v1_support_rates_release_authoritative": False,
            "pr11_reconstructed_unknown_queue_release_authoritative": False,
            "may_set_estimated_known_token_coverage": False,
            "may_set_quality_coverage_check_pass": False,
            "requires_full_v2_nlp_rerun": True
        }
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": out["status"],
        "visible_policy_function_hits": out["policy_declared_function_hits_visible_in_v1_top150"],
        "by_lemma": out["policy_declared_function_hits_by_lemma_visible_in_v1_top150"],
        "linker_candidates": out["additional_linker_candidates_visible_in_v1_top150_not_yet_auto_reclassified"],
        "decision": out["decision"]
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
