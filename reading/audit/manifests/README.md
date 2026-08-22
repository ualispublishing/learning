# Bounded language repair manifests

This directory is the queue for exact, review-gated language assessment repairs.

## Workflow

1. Create one `repair/**` branch from the intended base.
2. Add one JSON manifest in this directory for each corpus file being changed.
3. The registered workflow runs a fail-closed preflight, applies only the exact manifest repairs, validates the bounded unit, verifies the generated output/evidence, and commits only the corpus and evidence paths named by the manifest.
4. Open a draft PR and keep the independent semantic/native/educator review gate. Deterministic PASS is not release approval.

Multiple manifests in one push may target different corpus files. A push containing multiple manifests for the same corpus file is rejected to prevent order-dependent repairs.

## Required manifest fields

```json
{
  "schema_version": 1,
  "date": "YYYY-MM-DD",
  "language": "ar",
  "level": "A2",
  "unit": 10,
  "input_file": "reading/arabic/a2/passages.jsonl",
  "expected_before_sha256": "...",
  "expected_scope": {"records": 6, "questions": 60, "answers": 60},
  "repair_evidence_file": "reading/audit/example_repair.json",
  "post_evidence_file": "reading/audit/example_postrepair.json",
  "pass_status": "PASS_DETERMINISTIC_A2_UNIT10",
  "repairs": [
    {
      "passage_id": "ar-a2-u10-p01",
      "question_id": "q10",
      "before": {"prompt": "exact old prompt", "type": "grammar_function", "answer": "exact old answer"},
      "after": {"prompt": "exact new prompt", "type": "contrast", "answer": "exact new answer", "explanation": "brief evidence-based explanation"}
    }
  ],
  "false_positives": [
    {
      "passage_id": "ar-a2-u10-p06",
      "question_id": "q9",
      "prompt": "exact unchanged prompt",
      "type": "grammar_function",
      "answer": "exact unchanged answer",
      "reason": "Why the flagged item is a legitimate discourse/comprehension task."
    }
  ],
  "notable_sense_corrections": [],
  "release_effect": "Arabic remains educator-blocked; independent semantic/native/educator review required."
}
```

For languages whose formal-question markers differ from the Arabic defaults, set `formal_types` and/or `formal_prompt_markers` explicitly in the manifest.

## Fail-closed guarantees

The preflight rejects unsafe paths, stale corpus hashes, wrong unit scope, broken question/answer linkage, unknown IDs, duplicate repair/false-positive keys, and overlap between repairs and false positives. The repair engine additionally requires exact old prompt/type/answer triples, preserves passage prose and target linkage, checks the full bounded scope, rejects unexpected residual formal-metalinguistic findings and duplicate prompts, writes SHA-bound evidence, and verifies that evidence against the resulting corpus before any generated files are committed.
