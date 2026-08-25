# CISSP Atlas Question Bank

This directory governs the original CISSP Atlas practice bank from candidate authoring through immutable release batches.

## Current state — v1.4

- Released: **160 records** = **159 standard MCQs + 1 Bellringer**.
- Released difficulty: **F41 / E93 / S25 / B1**.
- All **159 released standard questions** provide four-option teaching rationales.
- Batches 002–006 were promoted in v1.4 after semantic review plus the repository-wide released+candidate originality/duplicate gate passed with **80 candidates and 0 warnings** (Actions run `32791694987`).
- Current unreleased candidates: **0**.
- Numbered-objective standard-MCQ exposure: **62/62**.
- Explicit enriched-record subtopic tags: **164/344**; the remaining 180 are the next authoring-depth opportunity, with the important caveat that legacy Q-001..Q-056 predate explicit subtopic tags.
- Long-term target: **800 records** at F15% / E60% / S20% / B5%.
- Remaining toward that target: **F79 / E387 / S135 / B39**.

The original 56-question baseline remains Foundation+-heavy. v1.4 deliberately adds 80 Exam/Stretch-centered scenarios so practice is less recognition-heavy and more judgment-heavy.

## Author → review → gate → release

1. Read `QUESTION_BANK_EXPANSION_PLAN.md`.
2. Run `coverage_report.py` and `batch_planner.py` to select objective, difficulty, and subtopic gaps before authoring.
3. Author candidates to `CANDIDATE_SCHEMA.json` as JSONL records with unique IDs, explicit decision points, source mappings, four option rationales, and originality provenance.
4. Semantically review every record before setting `review_status`.
5. Run:

```bash
python question-bank/quality_gate.py
```

The default gate excludes paths already listed in `RELEASED_BATCHES.json` from the candidate set while still using every released record as the duplicate-comparison corpus.

6. Resolve every `FAIL`; manually inspect and resolve every `WARN`.
7. Promote an approved batch only by adding its immutable file path/counts/difficulty to `RELEASED_BATCHES.json` and synchronizing the release/semantic metadata.
8. Run:

```bash
python audit.py
python question-bank/quality_gate.py --released-only
python question-bank/coverage_report.py --human
```

9. Pages then packages release files **from the release manifest itself**, runs the interactive browser smoke test, deploys, and verifies the exact public Git SHA plus runtime bank counts. Candidate files not named in the release manifest are required to remain unavailable from the public Pages artifact.

## Coverage-gap planning

`coverage_report.py` prevents a large bank from becoming repetitive. It reports released/candidate difficulty distributions, per-objective F/E/S exposure, weighted objective deficits, explicit subtopic-tag exposure, and remaining counts toward the 800-record target.

The current minimum authoring-depth model is **F1 / E4 / S1 per objective**. This is a planning heuristic, not an ISC2 psychometric standard and not evidence of learner mastery.

After v1.4, the highest objective deficits include 7.13, 7.14, 1.1, 1.10, 1.12, 1.2, 1.3, 1.5, 1.6, 1.8, 3.10, 3.2, 3.3, 3.7, 3.8, 5.3, 7.11, 7.12, 7.15, and 7.3. The planner’s next 16-item shape is **E12 / S4**, with no more than five primary questions from any one domain.

## Per-batch concentration guard

For candidate batches with at least 16 records, the automated gate requires:

- Exam-calibrated items at **≥50%** of the batch;
- Bellringers at **≤10%**;
- no single primary domain above **35%** of standard MCQs.

Coverage deficit is not permission to create a narrow or repetitive tranche.

## Non-negotiable originality rule

Questions are authored from the public CISSP scope, registered primary/supporting standards, and audited CISSP Atlas knowledge—not from live-exam recollections, exam dumps, leaked items, or commercial practice-question wording/templates.

Changing names, vendors, numbers, or synonyms does **not** make a question original if the underlying scenario, decision rule, evidence, and misconception path are materially the same.

The gate checks exact normalized text, near-text sequence similarity, token-shingle similarity, structural fingerprints, valid objective/subtopic/source mappings, semantic-review state, difficulty calibration, required option rationales, batch composition, and primary-domain concentration.

## Difficulty tiers

- `F`: **Foundation+** — slightly easier than expected exam level; foundation repair.
- `E`: **Exam-calibrated** — intended center of gravity; plausible distractors and resolvable managerial/technical judgment.
- `S`: **Stretch** — somewhat harder through additional constraints and reasoning steps, not obscure trivia.
- `B`: **Bellringer** — explicitly non-exam-representative, multi-domain constructed-response practice.

These are internal authoring labels, not ISC2 psychometric scores.

## Released-batch rule

`RELEASED_BATCHES.json` is authoritative. A JSONL file can physically remain under `candidates/` while being an immutable released input if the release manifest lists it. Do not edit released question content in place to create new questions; new work receives new IDs in a new candidate batch.

Historical review manifests for Batches 002–006 were written before the automated gate could be observed directly and may retain pre-promotion wording. The current release manifest, `STATUS.json`, semantic ledger, and CI results are authoritative for release state and aggregate difficulty.

## Teaching telemetry

Standard practice records correctness, selected option, confidence before answer, difficulty, objective, and attempt time. High-confidence misses are high-priority misconceptions. Bellringers remain separately tracked, non-exam-representative integrative drills.

The original Q-001..Q-056 stems/options/keys remain unchanged. `legacy-rationales.js` supplies four reviewed rationales for each legacy question (224 option rationales), so all 159 released standard questions now use the four-option teaching model.
