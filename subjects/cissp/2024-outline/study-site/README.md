# CISSP Atlas — Current Outline Study Workflow

Unofficial, original study site mapped to the current public ISC2 CISSP exam outline (effective 2024-04-15).

## Current release candidate — v1.25.0

- 8 CISSP domains; official weights total **100%**.
- **62** numbered public objectives and **344** paraphrased subtopic checks.
- **304/344** checks with explicit enriched-subtopic practice exposure.
- **33** AI-security coverage areas and **140** layered retrieval cards.
- **495 released standard scenario questions + 1 Bellringer = 496 released bank records** in the proposed v1.25 release state.
- Author-difficulty mix: **F41 / E345 / S109 / B1**.
- **495/495** standard questions have four-option teaching rationales.
- **636 learner-facing item IDs** in the combined semantic-audit ledger.
- **20** primary/reference sources.

`question-bank/RELEASED_BATCHES.json` is authoritative for promoted batches and `RELEASE_STATUS.json` for release/deployment state. Public v1.24.0 remains authoritative until the exact v1.25 release head is merged and exact-main plus live Pages verification pass.

## Semantic-review boundary

The combined ledgers cover **636 learner-facing item IDs**: 300 base items plus 336 release-addition items. The retained historical semantic statuses include one verified-after-correction item and two source-scope-note items; Batch 027 contributes 16 `VERIFIED` items. The release records **0 keyed-answer reversals** and **0 known remaining material factual errors** within the documented review boundary. This is an auditable quality claim, not an infallibility or exam-pass guarantee.

## Study workflow

Use **diagnose → retrieve → apply → repair → re-test later**. Run the 16-question diagnostic once for routing, retrieve before revealing, use Exam + Stretch for standard practice, commit confidence before answering, review all four rationales, repair high-confidence misses first, and use Bellringers separately as non-exam-representative integrative drills.

Keyboard review flow: **Space toggles reveal/hide; ←/→ move cards while hidden and layers while revealed; 1–4 grades the revealed card.**

## Question-bank expansion

The long-term target remains **800 records** with an authoring mix of 15% Foundation+, 60% Exam-calibrated, 20% Stretch, and 5% Bellringer. After Batch 027 promotion, remaining deficits are **F79 / E135 / S51 / B39**, or **304 records**. All 62 objectives have at least one standard-MCQ exposure. Explicit enriched-subtopic exposure remains **304/344**; this is authoring coverage, not learner mastery.

Batch 028 remains blocked until v1.25 release PR validation, exact post-merge main audit, live Pages fingerprint, and final evidence closure pass. Its provisional E12/S4 slate is: `4.1, 2.6, 1.3, 2.5, 1.4, 1.5, 1.8, 8.3, 1.1, 3.6, 3.8, 3.9, 4.3, 5.6, 7.11, 7.12`.

## Continuous audit

`.github/workflows/cissp-study-site-audit.yml` enforces knowledge/schema consistency, semantic coverage, originality/duplicate controls, logical batch composition, planning, JavaScript syntax, rationales, static assets, interactive browser flows, and an aggregate gate. `.github/workflows/cissp-pages.yml` independently audits and assembles a released-only artifact and verifies the public runtime fingerprint.

## Accuracy boundary

The strongest warranted v1.25 release-candidate claim is: **no known material factual errors or incorrect keyed answers are recorded as remaining; 636 learner-facing item IDs have explicit semantic status, and the release records zero known keyed-answer reversals.** Standards and public scope can change, reviews can miss nuance, and ISC2's adaptive live item bank is not public.

## Run locally

```bash
python -m http.server 8000
python audit.py
python question-bank/quality_gate.py
python question-bank/coverage_report.py --human
python question-bank/batch_planner.py --human
```

## Primary scope references

- ISC2 CISSP Certification Exam Outline: https://www.isc2.org/certifications/cissp/cissp-certification-exam-outline
- ISC2 CISSP Exam Refresh FAQ: https://www.isc2.org/certifications/cissp/cissp-exam-refresh-faq
- ISC2 Code of Ethics: https://www.isc2.org/ethics

Supporting standards are registered in `data-meta.js` and surfaced in the Sources view.
