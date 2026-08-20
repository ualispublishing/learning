import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "reading" / "audit" / "french_coverage_evidence_2026-08-19.json"
OUT = ROOT / "reading" / "audit" / "french_coverage_evidence_v2_2026-08-19.json"

# Narrow, policy-backed correction layer over the original Stanza audit.
# These lemmas are grammatical/function forms that French NLP may tag ADV rather
# than one of the UD closed-class POS tags used by the v1 classifier.
# Do not expand this set to ordinary content adverbs merely to improve coverage.
POLICY_FUNCTION_LEMMAS = {
    "ne",      # negation particle; explicitly named by LEXICAL_COVERAGE_POLICY
    "où",      # interrogative/relative grammatical form; explicitly named by policy
    "parce",   # only occurs as the fixed linker parce que in this corpus audit; adjudicate occurrences
    "tandis",  # linker in tandis que; adjudicate occurrences
    "afin",    # linker in afin de / afin que; adjudicate occurrences
}


def parse_candidate(s):
    # v1 stores passage candidates as: surface | lemma=LEMMA | upos=POS
    parts = [p.strip() for p in s.split("|")]
    out = {"surface": parts[0] if parts else ""}
    for p in parts[1:]:
        if "=" in p:
            k, v = p.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def main():
    x = json.loads(SRC.read_text(encoding="utf-8"))
    old_global = x.get("classification_counts", {})
    moved = 0
    moved_by_lemma = {}
    unresolved_total_v1 = int(old_global.get("uncontrolled_unknown_candidate", 0))

    passages = []
    for p in x.get("passages", []):
        p = dict(p)
        top = p.get("top_uncontrolled_unknown_candidates", [])
        moved_here = 0
        retained = []
        for row in top:
            label, count = row
            d = parse_candidate(label)
            lemma = (d.get("lemma") or d.get("surface") or "").casefold()
            if lemma in POLICY_FUNCTION_LEMMAS:
                moved_here += count
                moved += count
                moved_by_lemma[lemma] = moved_by_lemma.get(lemma, 0) + count
            else:
                retained.append(row)
        # IMPORTANT: v1 keeps only top-25 unresolved types per passage. Therefore
        # this postprocessor is an adjudication diagnostic, not a replacement for
        # a full NLP rerun. Coverage is not recomputed from these truncated rows.
        p["policy_function_reclassification_hits_in_top25"] = moved_here
        p["top_uncontrolled_unknown_candidates_after_policy_filter"] = retained
        passages.append(p)

    top_global = []
    for label, count in x.get("top_uncontrolled_unknown_candidates", []):
        lemma = label.split(" | upos=", 1)[0].casefold()
        if lemma not in POLICY_FUNCTION_LEMMAS:
            top_global.append([label, count])

    out = {
        "schema_version": 2,
        "date": "2026-08-19",
        "language": "fr",
        "status": "ADJUDICATION_DIAGNOSTIC_DO_NOT_AUTOPROMOTE",
        "source_artifact": "reading/audit/french_coverage_evidence_2026-08-19.json",
        "bound_canonical_hashes": x.get("bound_canonical_hashes"),
        "method": {
            "purpose": "Correct known v1 false-positive grammar/function candidates before full v2 NLP rerun.",
            "policy_basis": "LEXICAL_COVERAGE_POLICY: French common grammatical forms such as ne, à, y, où must be grammar/function support when ranked inventory misses them.",
            "narrow_additional_function_lemmas": sorted(POLICY_FUNCTION_LEMMAS),
            "important_limitation": "The source artifact stores only the top 25 unresolved candidate types per passage; this artifact therefore does not recompute supported coverage. A full NLP rerun is required for authoritative v2 rates.",
            "known_coverage_field_population_decision": "BLOCKED; supported coverage is not learner mastery."
        },
        "v1_uncontrolled_unknown_token_count": unresolved_total_v1,
        "policy_function_hits_visible_in_v1_top25": moved,
        "policy_function_hits_by_lemma_visible_in_v1_top25": moved_by_lemma,
        "top_uncontrolled_candidates_after_policy_filter": top_global[:150],
        "passages": passages,
        "decision": {
            "may_set_estimated_known_token_coverage": False,
            "may_set_quality_coverage_check_pass": False,
            "requires_full_v2_nlp_rerun": True,
            "pr11_reconstructed_surface_queue_authoritative": False
        }
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ["status","v1_uncontrolled_unknown_token_count","policy_function_hits_visible_in_v1_top25","policy_function_hits_by_lemma_visible_in_v1_top25","decision"]}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
