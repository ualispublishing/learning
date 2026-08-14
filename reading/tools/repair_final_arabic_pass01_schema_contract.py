#!/usr/bin/env python3
"""Repair schema drift exposed by final Arabic Pass 01.

This changes only the schema contract. It deliberately does NOT loosen the four
CEFR-style broad domains and does NOT add R0 as a review stage.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "reading/schema/passage.schema.json"
LEVELS = ("a1", "a2", "b1", "b2", "c1", "c2")

# Existing basic strategies plus reviewed advanced descriptive strategies that
# are already used systematically by the B1-C2 curriculum.
APPROVED_ADVANCED = {
    "argument_reconstruction", "audience_register", "category_reflection",
    "causal_comparison", "causal_explanation", "close_reading",
    "communication_scope", "comparative_reading", "competing_interpretations",
    "complex_system", "conceptual_distinction", "conditional_assumption",
    "counterargument", "counterexample", "counterfactual", "counterreading",
    "cultural_interpretation", "decision_tradeoff", "design_tradeoff",
    "distributional_effect", "epistemic_distinction", "ethical_tradeoff",
    "evidence_interpretation", "evidence_qualification", "evidence_strength",
    "exception_case", "fairness_comparison", "feedback_loop",
    "fictional_archive", "fictional_charter", "fictional_legal_system",
    "fictional_science", "form_function", "formal_evidence", "future_scenario",
    "historical_narrative", "historiographical_reconstruction",
    "identity_interpretation", "implementation_gap", "implementation_tradeoff",
    "inference_chain", "inference_risk", "institutional_case",
    "institutional_incentive", "interpretive_contrast", "interpretive_evidence",
    "language_variation", "metric_response", "model_limit", "perspective_shift",
    "policy_tradeoff", "privacy_boundary", "procedural_reasoning",
    "professional_judgment", "recommendation_scope", "research_method",
    "rhetorical_effect", "rights_interpretation", "risk_distribution",
    "rule_adaptation", "scenario_comparison", "scenario_forecast",
    "source_comparison", "source_criticism", "source_critique", "source_selection",
    "stock_flow", "structural_relation", "style_analysis", "tradeoff",
    "translation_choice", "uncertainty", "uncertainty_analysis",
    "uncertainty_calibration", "user_perspective", "value_conflict",
}


def corpus_context_strategies() -> set[str]:
    values: set[str] = set()
    for level in LEVELS:
        path = ROOT / f"reading/arabic/{level}/passages.jsonl"
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            for target in row.get("new_lexical_targets", []):
                if isinstance(target, dict):
                    values.update(str(v) for v in target.get("context_strategy", []) if v)
    return values


def main() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    props = schema["properties"]
    defs = schema["$defs"]

    domains = props["domains"]["items"]["enum"]
    assert domains == ["personal", "public", "educational", "professional"], domains

    passage_types = props["passage_type"]["enum"]
    if "integration" not in passage_types:
        passage_types.append("integration")

    review_stages = defs["reviewLexicalTarget"]["properties"]["review_stage"]["enum"]
    assert "R0" not in review_stages, review_stages

    strategy_enum = defs["newLexicalTarget"]["properties"]["context_strategy"]["items"]["enum"]
    basic = set(strategy_enum)
    observed = corpus_context_strategies()
    unknown = observed - basic - APPROVED_ADVANCED
    if unknown:
        raise RuntimeError("Unreviewed context_strategy values remain: " + json.dumps(sorted(unknown), ensure_ascii=False))
    strategy_enum[:] = sorted(basic | APPROVED_ADVANCED)

    # Guard the two intended schema changes and the two intentionally retained restrictions.
    assert "integration" in props["passage_type"]["enum"]
    assert observed <= set(strategy_enum)
    assert props["domains"]["items"]["enum"] == ["personal", "public", "educational", "professional"]
    assert "R0" not in defs["reviewLexicalTarget"]["properties"]["review_stage"]["enum"]

    SCHEMA.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "passage_type_added": "integration",
        "observed_context_strategies": len(observed),
        "schema_context_strategies": len(strategy_enum),
        "domains_unchanged": domains,
        "R0_allowed": False,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
