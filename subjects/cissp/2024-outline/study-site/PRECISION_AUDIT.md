# CISSP Atlas Precision Audit — 2026-08-24

## Result

**Published-scope mapping: PASS. Released-item semantic review: PASS, with explicit nuance notes.**

The site remains mapped to the current public ISC2 CISSP exam outline, effective April 15, 2024, plus ISC2's current cross-domain AI-security guidance.

## v1.3 released scope

- 8/8 domains with official weights 16/10/13/13/13/12/13/10 = 100%.
- 62/62 numbered public objectives.
- 344 paraphrased public-outline subtopic checks.
- 33 AI-security coverage areas across all 8 domains.
- 140 layered retrieval cards.
- **79 released standard scenario questions.**
- **1 released Bellringer**, explicitly non-exam-representative.
- **80 total released question-bank records.**
- **79/79 released standard questions have four-option teaching rationales.**
- 20 primary/reference sources.
- **220 learner-facing items represented in `SEMANTIC_ITEM_AUDIT.json`.**

Released author-difficulty distribution is currently F41 / E34 / S4 / B1. This still skews easier than the mature-bank target because the original 56-question baseline contains 37 Foundation+ items; subsequent expansion is therefore intentionally biased toward Exam-calibrated and Stretch reasoning.

## Item-level semantic audit

Every released learner-facing item has an explicit semantic status. Current ledger:

- **217 VERIFIED**;
- **1 VERIFIED_AFTER_CORRECTION**;
- **2 VERIFIED_WITH_SOURCE_SCOPE_NOTE**;
- **0 answer-key reversals**;
- **0 material factual errors recorded as remaining after review**.

### Correction retained

`HY-014` states that digital signatures provide integrity and origin authentication and can **support** nonrepudiation when signer identity, private-key control, certificate/key validity, and supporting evidence are trustworthy. A signature does not itself provide confidentiality or automatically guarantee nonrepudiation.

### Source-scope notes retained

`AI-005` and `PX-020` remain factually valid under the CISSP outline's non-human/agent/service-account scope. NIST SP 800-63-4 is useful supporting digital-identity context but is not treated as the sole primary authority for those non-human identity claims.

## Batch 001 release audit

Batch 001 is released in v1.3 through `question-bank/RELEASED_BATCHES.json`:

- 24 records total;
- 23 standard MCQs;
- 1 Bellringer;
- F4 / E15 / S4 / B1;
- all 24 carry semantic-review status and original-from-public-scope provenance;
- all 23 MCQs include four answer choices, one keyed answer, a teaching explanation, and four option rationales;
- the Bellringer contains linked constructed-response prompts and an explicit rubric;
- pre-release review recorded zero duplicate IDs, unknown objectives/subtopics/sources, structural duplicate fingerprints, similarity-warning matches, external question seeds, or answer-key reversals.

The historical source files remain under `question-bank/candidates/`, but the release manifest is authoritative and the quality gate excludes released paths from the unreleased candidate set while continuing to use them as duplicate-comparison corpus.

## Legacy 56-question rationale backfill

The original Q-001..Q-056 set remains semantically frozen: **0 stem changes, 0 option-text changes, and 0 keyed-answer changes** were introduced during the teaching-depth pass.

A separate `legacy-rationales.js` layer provides four individualized option rationales for each of those 56 questions, for **224 reviewed rationale statements** total. `LEGACY_RATIONALE_AUDIT.json` records the method and results. CI evaluates the rationale layer and fails unless all Q-001..Q-056 IDs each expose exactly four non-empty rationales.

Combined with Batch 001's native rationales, this means **all 79 released standard questions now support four-option teaching feedback**.

## v1.3 study-quality controls

In addition to the prior retrieval/spaced-review workflow, v1.3 adds:

- author-difficulty filters for Foundation+, Exam-calibrated, Stretch, Exam+Stretch, or all standard questions;
- confidence commitment before a standard answer can be selected;
- persistent attempt history including choice, confidence, difficulty, objective, and correctness;
- explicit prioritization of high-confidence misses as misconception signals;
- four-option rationale rendering for every released standard question;
- a separate Bellringer mode labeled **NON-EXAM-REPRESENTATIVE INTEGRATIVE DRILL**;
- constructed-response Bellringer prompts, delayed rubric reveal, and self-scoring;
- a progress-state bridge so later flashcard grading does not erase newer confidence/Bellringer history created by the practice layer;
- current-state Progress/Export behavior and an intentional full reset path.

## Question-bank originality and coverage controls

`question-bank/quality_gate.py` treats the current released bank as permanent comparison corpus. Unreleased candidates must pass:

- valid objective/subtopic/source mappings;
- semantic-review status;
- originality provenance (`original-from-public-scope`, no external question seed);
- tier/score calibration rules;
- exact normalized duplicate rejection;
- near-text sequence and token-shingle checks;
- structural scenario/rule/misconception duplicate checks;
- four option rationales for MCQs;
- Bellringer structure/rubric rules.

For each candidate batch with at least 16 records, Exam-calibrated items must remain at least 50%, Bellringers may not exceed 10%, and no single primary domain may exceed **35% of the standard MCQs in that batch**. The domain cap prevents a raw coverage deficit from creating a narrowly repetitive training tranche.

`question-bank/coverage_report.py` is a separate planning tool. It reports per-objective F/E/S density, explicit enriched-subtopic exposure, remaining difficulty counts toward the 800-record target, and a weighted priority queue so future authoring targets thin areas rather than repeatedly exercising already-dense objectives. The report does not treat missing explicit subtopic tags on the legacy 56 as proof that those concepts have never been tested.

## Pending candidate state

Batches 002, 003, and 004 are **not released**.

- **Batch 002:** 16 semantically reviewed MCQs = E12 / S4 / F0 / B0; exactly two primary-domain scenarios per domain.
- **Batch 003:** 16 semantically reviewed MCQs = E12 / S4 / F0 / B0; exactly two primary-domain scenarios per domain.
- **Batch 004:** 16 semantically reviewed MCQs = E12 / S4 / F0 / B0; planner-driven primary distribution D1=5, D2=1, D3=1, D4=1, D5=1, D6=1, D7=5, D8=1, so the maximum single-domain share is 31.25%.
- Combined pending candidates: **48 records = E36 / S12**.
- If all three eventually promote, the bank becomes **128 records = F41 / E70 / S16 / B1**.

Batch 004 deliberately targeted the final five objectives with zero standard-MCQ exposure in the released-plus-candidate planning state: **1.2, 1.12, 7.5, 7.7, and 7.14**. With Batch 004 included, the planning corpus now has at least one standard MCQ mapped to **62/62 objectives**.

That 62/62 figure is a planning/exposure milestone only. Batch 004 is unreleased, the released bank remains 80 records, one standard question is not sufficient instructional depth, and mapped question exposure is not evidence of learner mastery.

All three pending batches remain candidate-only until the repository quality gate is observed clean and every similarity warning, if any, is resolved semantically.

## Accuracy boundary

The strongest warranted claim for the current release is:

> **No known material factual errors or incorrect keyed answers are recorded as remaining after the 2026-08-24 semantic review; every released learner-facing item has an explicit audit status.**

That is not the same as an absolute “100% infallible forever” guarantee. Standards and public scope can change, reviews can miss nuance, and ISC2's live adaptive item bank is not public. CISSP Atlas does not claim that memorization guarantees passing.

## Primary scope references

- ISC2 CISSP Certification Exam Outline: https://www.isc2.org/certifications/cissp/cissp-certification-exam-outline
- ISC2 CISSP Exam Refresh FAQ: https://www.isc2.org/certifications/cissp/cissp-exam-refresh-faq
- ISC2 Code of Ethics: https://www.isc2.org/ethics

Supporting standards are registered in `data-meta.js` and shown in the site's Sources view.
