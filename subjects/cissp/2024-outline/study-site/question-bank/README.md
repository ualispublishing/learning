# CISSP Atlas Question Bank

This directory governs the original CISSP Atlas practice bank from candidate authoring through immutable release batches.

## Current state

- Released: **80 records** = 79 standard MCQs + 1 Bellringer.
- Released difficulty: **F41 / E34 / S4 / B1**.
- Batch 001: released in v1.3 through `RELEASED_BATCHES.json`.
- Batch 002: **candidate-only**, 16 MCQs = E12/S4, pending automated repository gate.
- Long-term target: 800 records at F15% / E60% / S20% / B5%.

## Author → review → gate → release

1. Read `QUESTION_BANK_EXPANSION_PLAN.md`.
2. Author candidates to `CANDIDATE_SCHEMA.json` as JSONL records.
3. Put semantically reviewed candidates under `question-bank/candidates/` with `review_status` and originality provenance.
4. Run:

```bash
python question-bank/quality_gate.py
```

The default gate automatically excludes file paths already listed in `RELEASED_BATCHES.json` from the candidate set, while still using all released batches as duplicate-comparison corpus.

5. Resolve every `FAIL`; manually inspect and resolve every `WARN`.
6. Promote an approved batch by adding its immutable file paths/counts/difficulty distribution to `RELEASED_BATCHES.json` and updating release metadata/audits.
7. Run:

```bash
python audit.py
python question-bank/quality_gate.py
```

8. Only then is the batch eligible for the live site/Pages deployment.

## Non-negotiable originality rule

Questions are authored from the public CISSP scope, registered primary/supporting standards, and audited CISSP Atlas knowledge—not from live-exam recollections, exam dumps, leaked items, or commercial practice-question wording/templates.

Changing names, vendors, numbers, or synonyms does **not** make a question original if the underlying scenario, decision rule, evidence, and misconception path are materially the same.

The gate checks exact normalized text, near-text sequence similarity, token-shingle similarity, structural fingerprints, valid objective/subtopic/source mappings, semantic-review state, difficulty calibration, and required option rationales.

## Difficulty tiers

- `F`: **Foundation+** — slightly easier than expected exam level; foundation repair.
- `E`: **Exam-calibrated** — intended center of gravity; plausible distractors and resolvable managerial/technical judgment.
- `S`: **Stretch** — somewhat harder through additional constraints and reasoning steps, not obscure trivia.
- `B`: **Bellringer** — explicitly non-exam-representative, multi-domain integrative constructed-response case.

Difficulty scores are internal authoring/calibration metadata, not ISC2 psychometric scores.

## Released-batch rule

`RELEASED_BATCHES.json` is authoritative. A JSONL file physically residing under `candidates/` can still be an immutable released input if the release manifest lists it. The directory name alone does not determine release status.

Do not edit a released batch in place to create new questions. New work receives new IDs in a new candidate batch so provenance and duplicate history remain auditable.

## Teaching telemetry

v1.3 standard practice records correctness, selected option, confidence before answer, difficulty, objective, and attempt time. High-confidence misses should be treated as high-priority misconceptions. Bellringers are stored separately as self-scored integrative drills.

The original 56 questions still have legacy single explanations. Newly authored batches require a rationale for all four options; backfilling the legacy rationales is a future quality task.
