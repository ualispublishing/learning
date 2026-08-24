# CISSP Atlas Question Bank

This directory governs the original CISSP Atlas practice bank from candidate authoring through immutable release batches.

## Current state

- Released: **80 records** = 79 standard MCQs + 1 Bellringer.
- Released difficulty: **F41 / E34 / S4 / B1**.
- All **79 released standard questions** now provide four-option teaching rationales.
- Batch 001: released in v1.3 through `RELEASED_BATCHES.json`.
- Batch 002: **candidate-only**, 16 MCQs = E12/S4, pending automated repository gate.
- Batch 003: **candidate-only**, 16 MCQs = E12/S4, pending automated repository gate.
- Long-term target: 800 records at F15% / E60% / S20% / B5%.

## Author → review → gate → release

1. Read `QUESTION_BANK_EXPANSION_PLAN.md`.
2. Use `coverage_report.py` to identify objective/difficulty gaps before choosing the next authoring targets.
3. Author candidates to `CANDIDATE_SCHEMA.json` as JSONL records.
4. Put semantically reviewed candidates under `question-bank/candidates/` with `review_status` and originality provenance.
5. Run:

```bash
python question-bank/quality_gate.py
```

The default gate automatically excludes file paths already listed in `RELEASED_BATCHES.json` from the candidate set, while still using all released batches as duplicate-comparison corpus.

6. Resolve every `FAIL`; manually inspect and resolve every `WARN`.
7. Promote an approved batch by adding its immutable file paths/counts/difficulty distribution to `RELEASED_BATCHES.json` and updating release metadata/audits.
8. Run:

```bash
python audit.py
python question-bank/quality_gate.py
python question-bank/coverage_report.py --human
```

9. Only then is the batch eligible for the live site/Pages deployment.

## Coverage-gap planning

`coverage_report.py` keeps expansion from becoming repetitive in a less obvious way: over-practicing a few objectives while other objectives remain thin.

It reports:

- released and candidate difficulty distributions;
- per-objective F/E/S exposure counts;
- the current minimum target of at least **1 Foundation+ / 4 Exam-calibrated / 1 Stretch** standard item per objective before the bank is considered mature;
- a weighted objective-priority queue using the official domain weights and current item density;
- explicit subtopic-tag exposure from enriched released/candidate records;
- remaining counts toward the 800-record F120/E480/S160/B40 target.

The subtopic report deliberately notes a limitation: Q-001..Q-056 predate explicit subtopic tags. Therefore an “unexposed” subtopic label in that report means **not explicitly tagged by enriched records**, not proof that the concept never appears in a legacy question.

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

The original Q-001..Q-056 stems/options/keys remain unchanged, but `legacy-rationales.js` now supplies four reviewed rationales for each question (224 option rationales total). `LEGACY_RATIONALE_AUDIT.json` records that backfill, so all 79 released standard questions now use the same four-option teaching model.
