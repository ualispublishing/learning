# CISSP Atlas — Current Outline Study Workflow

Unofficial, original study site mapped to the current public ISC2 CISSP exam outline (effective 2024-04-15) and the cross-domain AI-security coverage currently represented in the public outline.

## Current verified release — v1.22.0

- 8 CISSP domains and current official weights: **16/10/13/13/13/12/13/10 = 100%**;
- all **62 numbered public objectives** mapped;
- **344** paraphrased public-outline subtopic checks;
- **302/344** subtopic checks currently have explicit enriched-subtopic practice exposure;
- **33** AI-security coverage areas across all 8 domains;
- **140** layered retrieval cards;
- **447 released standard scenario questions + 1 Bellringer = 448 released bank records**;
- released author-difficulty mix: **F41 / E309 / S97 / B1**;
- **447/447 released standard questions have four-option teaching rationales**;
- **588 learner-facing item IDs** in the combined semantic-audit ledger;
- **20** primary/reference sources;
- **0 unreleased candidate records** in the current release state.

`question-bank/RELEASED_BATCHES.json` is authoritative for promoted question batches. `RELEASE_STATUS.json` is authoritative for the current release/deployment state. Public v1.22.0 has passed released-state audit, exact post-promotion main audit, and live GitHub Pages fingerprint verification.

## Item-level semantic status

The combined semantic ledgers cover all **588** currently released learner-facing item IDs. The base ledger contains 300 items and the release-additions ledger contributes 288 more.

Current documented audit summary:

- **585 VERIFIED**;
- **1 VERIFIED_AFTER_CORRECTION** (`HY-014`, digital signatures/nonrepudiation wording);
- **2 VERIFIED_WITH_SOURCE_SCOPE_NOTE** (`AI-005`, `PX-020`);
- **0 keyed-answer reversals**;
- **0 known remaining material factual errors identified by the documented review**.

This is a strong, auditable quality claim—not a mathematical guarantee that every sentence can never contain nuance or that studying the site guarantees a live CISSP pass. See `PRECISION_AUDIT.md`, `SEMANTIC_ITEM_AUDIT.json`, and `SEMANTIC_RELEASE_ADDITIONS.json`.

## Study workflow

The interface is organized around **diagnose → retrieve → apply → repair weak areas → re-test later**.

- 16-question, two-per-domain first-run diagnostic used only for routing;
- local spaced-review state and retrieval-before-reveal cards;
- weighted domain mastery and weak-objective recommendations;
- expandable subtopic coverage and precision-depth cards;
- difficulty-aware standard practice with Foundation+, Exam-calibrated, Stretch, Exam+Stretch, and All Available filters;
- confidence-before-answer capture;
- high-confidence-miss tracking;
- four individualized option rationales for every released standard question;
- separate **NON-EXAM-REPRESENTATIVE INTEGRATIVE DRILL** Bellringer mode with constructed responses, rubric reveal, and self-scoring;
- global search, keyboard controls, progress export/reset, and responsive desktop/mobile layouts.

The original 56-question baseline remains semantically frozen in its stem/option/key layer. A separate reviewed rationale layer adds 224 option rationales (56 × 4). `LEGACY_RATIONALE_AUDIT.json` records that backfill and CI fails if any baseline rationale set is missing or incomplete.

## Recommended learner sequence

1. Run the diagnostic once if no baseline exists.
2. Study the lowest diagnostic domain with retrieval-before-reveal cards.
3. Use Layer 4/misconception content whenever recall is uncertain.
4. Practice with **Exam + Stretch** as the default calibrated filter.
5. Commit confidence before answering.
6. Repair high-confidence misses first.
7. Read why all four options win or lose.
8. Use Bellringers separately after normal study, not as exam-format simulation.
9. Re-test later instead of immediately repeating the same items to recognition.

`TOMORROW_START.md` is the concise learner-facing version of this workflow.

## Question-bank expansion

`question-bank/QUESTION_BANK_EXPANSION_PLAN.md` defines an **800-record** maturity target:

- 15% Foundation+;
- 60% Exam-calibrated;
- 20% Stretch;
- 5% Bellringer.

Current released distribution is **F41 / E309 / S97 / B1**, leaving target deficits of **F79 / E171 / S63 / B39**. Difficulty is an authoring scale until sufficient learner-response data exists for empirical calibration.

Originality is enforced by decision-rule-first authoring from public scope/registered standards and audited knowledge, never from exam dumps, live-item recollections, leaked banks, or commercial-question wording/templates. `question-bank/quality_gate.py` compares candidates against the released bank and within each candidate batch using exact, near-text, and structural duplicate checks.

`question-bank/coverage_report.py` measures objective/difficulty density and explicit enriched-subtopic-tag exposure. `question-bank/batch_planner.py` turns that state into a deterministic next-batch slate; it recommends targets only and does not author, validate, or release questions.

### Next expansion state

There is currently **no unreleased candidate batch**. The released-only v1.22 planner recommends Batch 025 as **E12 / S4**, with emphasis on thin objectives and materially new scenario families. The current planner slate is recorded in `RELEASE_STATUS.json` so authoring does not rely on stale prose.

All 62 numbered objectives currently have at least one standard-MCQ exposure in the released corpus. That is a coverage milestone only: one mapped question is not sufficient instructional depth and mapped exposure is not evidence of learner mastery.

For standard candidate batches of at least 16 records, the quality gate requires Exam-calibrated items at ≥50%, Bellringers at ≤10%, and caps any one primary domain at **35%**.

## Continuous audit

`.github/workflows/cissp-study-site-audit.yml` runs the deterministic release audit plus the question-bank originality/quality, coverage/planning, syntax/static, browser-smoke, and aggregate controls used by the project. The Pages workflow independently validates the released-only corpus before deployment and verifies the public runtime fingerprint.

The deterministic audit checks, among other things:

- 8 domains, current official weights, 62 objectives, 344 subtopic checks, 33 AI areas, 140 cards, and 20 sources;
- valid objective/source mappings and unique IDs;
- question option/key/rationale structure;
- semantic-review coverage and zero recorded answer-key reversals/material unresolved errors;
- release/metadata count consistency;
- released-batch manifest and review evidence;
- application shell/runtime controls and browser-smoke expectations;
- learner-facing release-document freshness against `RELEASE_STATUS.json`.

## Accuracy boundary

The strongest warranted claim for public v1.22.0 is:

> No known material factual errors or incorrect keyed answers are recorded as remaining in the documented semantic audit boundary; 588 released learner-facing item IDs have explicit review status, and the current release records zero known keyed-answer reversals.

This is not an absolute guarantee of infallibility. Standards and public scope can change, reviews can miss nuance, and ISC2's live adaptive item bank is not public. CISSP Atlas does not claim that memorization guarantees passing.

## Run locally

```bash
python -m http.server 8000
# open http://localhost:8000
python audit.py
python question-bank/quality_gate.py
python question-bank/coverage_report.py --human
python question-bank/batch_planner.py --human
```

Serve the folder over HTTP rather than opening `index.html` directly because the released batch manifest/JSONL is loaded through `fetch()` before the application initializes.

## GitHub Pages

`.github/workflows/cissp-pages.yml` deploys only after released-corpus validation. Project URL: `https://ualispublishing.github.io/learning/`.

## Primary scope references

- ISC2 CISSP Certification Exam Outline: https://www.isc2.org/certifications/cissp/cissp-certification-exam-outline
- ISC2 CISSP Exam Refresh FAQ: https://www.isc2.org/certifications/cissp/cissp-exam-refresh-faq
- ISC2 Code of Ethics: https://www.isc2.org/ethics

Supporting standards are registered in `data-meta.js` and surfaced in the site's Sources view.
