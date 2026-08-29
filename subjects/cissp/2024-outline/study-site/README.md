# CISSP Atlas — Current Outline Study Workflow

Unofficial, original study site mapped to the current public ISC2 CISSP exam outline (effective 2024-04-15) and the cross-domain AI-security coverage represented in the public outline.

## Current release metadata — v1.23.0

- 8 CISSP domains and official weights: **16/10/13/13/13/12/13/10 = 100%**;
- all **62 numbered public objectives** mapped;
- **344** paraphrased public-outline subtopic checks;
- **303/344** subtopic checks with explicit enriched-subtopic practice exposure;
- **33** AI-security coverage areas across all 8 domains;
- **140** layered retrieval cards;
- **463 released standard scenario questions + 1 Bellringer = 464 released bank records**;
- released author-difficulty mix: **F41 / E321 / S101 / B1**;
- **463/463** released standard questions have four-option teaching rationales;
- **604 learner-facing item IDs** in the combined semantic-audit ledger;
- **20** primary/reference sources.

`question-bank/RELEASED_BATCHES.json` is authoritative for promoted question batches. `RELEASE_STATUS.json` is authoritative for release/deployment state. During a release PR, the prior public version remains authoritative until the validated release head is merged and exact-main plus live Pages verification pass.

## Semantic-review boundary

The combined semantic ledgers cover all 604 learner-facing item IDs. The base ledger contains 300 items and the release-additions ledger contributes 304.

- **601 VERIFIED**;
- **1 VERIFIED_AFTER_CORRECTION** (`HY-014`, digital-signature/nonrepudiation wording);
- **2 VERIFIED_WITH_SOURCE_SCOPE_NOTE** (`AI-005`, `PX-020`);
- **0 keyed-answer reversals**;
- **0 known remaining material factual errors recorded in the documented review boundary**.

This is an auditable quality claim, not a mathematical guarantee that every sentence can never contain nuance or that the resource guarantees a live CISSP pass.

## Study workflow

Use **diagnose → retrieve → apply → repair → re-test later**:

1. Run the 16-question diagnostic once if no baseline exists. Treat it as routing, not a readiness prediction.
2. Study the weakest domain with retrieval-before-reveal cards.
3. Use the misconception layer when recall is uncertain.
4. Practice with **Exam + Stretch** as the default calibrated filter.
5. Commit confidence before answering; repair high-confidence misses first.
6. Read why all four options win or lose.
7. Use Bellringers separately as non-exam-representative integrative drills.
8. Re-test later rather than repeating immediately to recognition.

The original Q-001..Q-056 stems/options/keys remain semantically frozen. `legacy-rationales.js` supplies 224 reviewed option rationales (56 × 4), and CI enforces completeness.

## Question-bank expansion

The maturity target remains **800 records** with an authoring mix of 15% Foundation+, 60% Exam-calibrated, 20% Stretch, and 5% Bellringer. After Batch 025, remaining target deficits are **F79 / E159 / S59 / B39**.

All 62 numbered objectives have at least one standard-MCQ exposure. Explicit enriched-subtopic exposure is 303/344. These are authoring-coverage metrics, not learner-mastery claims.

After v1.23 is fully live-verified and evidence-closed, the planner's Batch 026 slate is E12/S4 across objectives `5.4, 7.1, 7.2, 2.5, 7.10, 5.2, 6.5, 8.3, 6.3, 4.1, 5.5, 8.5, 6.2, 2.1, 2.2, 2.4`. Do not begin Batch 026 before v1.23 release closure.

Originality is enforced against the released corpus: candidates must be original from public scope/registered standards, use no external question seed, and pass exact, near-text, structural, mapping, rationale, composition, browser, and aggregate gates. For standard batches of at least 16 records, Exam-calibrated items must be ≥50%, Bellringers ≤10%, and any one primary domain ≤35%.

## Continuous audit

`.github/workflows/cissp-study-site-audit.yml` checks knowledge/schema consistency, release counts, semantic coverage, originality/duplicate controls, logical batch composition, planning, JavaScript syntax, legacy rationales, static assets, interactive browser flows, and aggregate enforcement. `.github/workflows/cissp-pages.yml` independently assembles a released-only artifact and verifies the public runtime fingerprint.

The deterministic audit also fails if `README.md`, `TOMORROW_START.md`, `PRECISION_AUDIT.md`, or `PROJECT_TRACKS.json` silently lag `RELEASE_STATUS.json`.

## Accuracy boundary

The strongest warranted v1.23 claim is:

> No known material factual errors or incorrect keyed answers are recorded as remaining in the documented semantic audit boundary; 604 released learner-facing item IDs have explicit review status and the release records zero known keyed-answer reversals.

Standards and public scope can change, reviews can miss nuance, and ISC2's adaptive live item bank is not public. CISSP Atlas does not claim that memorization guarantees passing.

## Run locally

```bash
python -m http.server 8000
# open http://localhost:8000
python audit.py
python question-bank/quality_gate.py
python question-bank/coverage_report.py --human
python question-bank/batch_planner.py --human
```

Serve the folder over HTTP because released batch JSONL is loaded through `fetch()` before application initialization.

## Primary scope references

- ISC2 CISSP Certification Exam Outline: https://www.isc2.org/certifications/cissp/cissp-certification-exam-outline
- ISC2 CISSP Exam Refresh FAQ: https://www.isc2.org/certifications/cissp/cissp-exam-refresh-faq
- ISC2 Code of Ethics: https://www.isc2.org/ethics

Supporting standards are registered in `data-meta.js` and surfaced in the Sources view.
