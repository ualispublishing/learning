# Generation-First, Final-Audit Workflow

This file records the current production-order instruction for the graded-reading project and should be read together with `reading/AGENT_HANDOFF.md`, `reading/ROADMAP.md`, `reading/TASKS.md`, and `reading/STATUS.json`.

## Production priority

The primary deliverable is the passage corpus. Generate passages first, while writing them to a high standard from the beginning. Do not interrupt ordinary passage generation with repeated formal audits after every passage or unit.

Preserve the existing curriculum architecture while generating:

- 6 passages per unit: introduce -> reinforce -> interleave -> transfer -> integrate/checkpoint -> fluency;
- 10 questions and 10 linked answers per canonical passage unless a documented exception is pedagogically necessary;
- deliberate contextual vocabulary introduction and later recycling;
- grammar/discourse progression appropriate to the planned CEFR level;
- high-quality natural language on first draft;
- P6 fluency/checkpoint passages with zero or minimal deliberately new material;
- independent natural writing for Arabic, French, and Urdu rather than translations of one another;
- canonical JSONL as the source format.

## Audit timing

Formal validation and correctness audits are intentionally deferred until the designated final review phase for the generated corpus/batch. Generation-stage passage records may therefore remain `draft` with formal quality fields `pending` even when they were written carefully.

Do not spend generation turns repeatedly recalculating coverage, rebuilding audit infrastructure, or re-running whole-corpus semantic reviews unless a concrete generation blocker requires it.

## Final review standard

At the final review phase, use **at least 10 distinct passes/approaches** rather than one repeated generic proofread. The exact set may be refined, but it should include separate lenses such as:

1. native-language naturalness and idiomaticity;
2. grammar, morphology, agreement, punctuation, and script correctness;
3. lexical sense/register/homograph precision;
4. CEFR/difficulty calibration and new-word load;
5. contextual inferability of deliberate vocabulary targets;
6. question quality, ambiguity, distractors, and answer-key correctness;
7. passage-to-question evidence alignment and reference resolution;
8. repetition, spacing, interleaving, and exposure-ledger consistency;
9. fluency/checkpoint suitability, known-material control, and comprehension gating;
10. schema/ID/link/count/data-integrity validation;
11. cross-passage continuity, duplicate-content, and topic/genre balance;
12. adversarial/error-seeking pass that tries to falsify prior approvals.

Additional independent passes are encouraged where useful. A passage is not finally approved merely because an earlier pass approved it.

## Relationship to earlier handoff gates

Earlier handoff documents contain conservative calibration gates written when audits were being performed during generation. This policy changes the **order of operations**, not the underlying quality criteria: preserve the criteria, generate the corpus/batch first, then apply them comprehensively at the final audit stage.

If a severe defect is obvious during generation, fix it immediately rather than knowingly propagating it. Otherwise, keep momentum on passage production and defer formal audit bookkeeping to the final review phase.
