# CISSP Atlas — Current Outline Study Workflow

Unofficial, original study site mapped to the current public ISC2 CISSP exam outline (effective 2024-04-15).

## v1.26.0 release candidate

- 8 CISSP domains; official weights total **100%**.
- **62** numbered public objectives and **344** paraphrased subtopic checks.
- **305/344** checks with explicit enriched-subtopic practice exposure.
- **33** AI-security coverage areas and **140** layered retrieval cards.
- **511 released standard scenario questions + 1 Bellringer = 512 released bank records** in the v1.26 release candidate.
- Author-difficulty mix: **F41 / E357 / S113 / B1**.
- **511/511** standard questions have four-option teaching rationales.
- **652 learner-facing item IDs** in the combined semantic-audit ledger.
- **20** primary/reference sources.

Batch 028 completed candidate PR #112 and bookkeeping PR #113 with exact-head, exact-main, originality, logical-mix, browser, aggregate, and Pages-isolation controls passing. This branch promotes those 16 reviewed questions to v1.26.0. Public production remains the verified v1.25.0 release until this exact release head is validated, merged, and the live Pages fingerprint passes.

## Semantic-review boundary

The combined ledgers cover **652 learner-facing item IDs** after promotion: 300 base items plus 352 release-addition items. Batch 028 contributes 16 `VERIFIED` items. The release candidate records zero known keyed-answer reversals and zero known remaining material factual errors within the documented review boundary. This is an auditable quality claim, not an infallibility or exam-pass guarantee.

## Study workflow

Use **diagnose → retrieve → apply → repair → re-test later**. Run the diagnostic once for routing, retrieve before revealing, use Exam + Stretch for standard practice, commit confidence before answering, review all four rationales, repair high-confidence misses first, and use Bellringers separately as non-exam-representative integrative drills.

Keyboard review flow: **Space toggles reveal/hide; ←/→ move cards while hidden and layers while revealed; 1–4 grades the revealed card.**

## Question-bank expansion

The long-term target remains **800 records** with an authoring mix of 15% Foundation+, 60% Exam-calibrated, 20% Stretch, and 5% Bellringer. After Batch 028 promotion, remaining deficits are **F79 / E123 / S47 / B39**, or **288 records**. All 62 objectives have at least one standard-MCQ exposure. Explicit enriched-subtopic exposure is **305/344**; this is authoring coverage, not learner mastery.

Batch 029 is provisionally planned at E12/S4 across `4.1, 1.4, 7.13, 2.5, 7.14, 7.15, 7.3, 8.3, 7.4, 3.1, 3.6, 1.10, 6.1, 6.4, 2.3, 1.11`. Do not begin it as authoritative released-only work until v1.26 post-merge and public verification close.

## Continuous audit

`.github/workflows/cissp-study-site-audit.yml` enforces knowledge/schema consistency, semantic coverage, originality/duplicate controls, logical batch composition, planning, JavaScript syntax, rationales, static assets, interactive browser flows, and an aggregate gate. `.github/workflows/cissp-pages.yml` independently audits and assembles a released-only artifact and verifies the public runtime fingerprint.

## Accuracy boundary

The strongest warranted v1.26 release-candidate claim is: **no known material factual errors or incorrect keyed answers are recorded as remaining; 652 learner-facing item IDs have explicit semantic status, and the release records zero known keyed-answer reversals.** Standards and public scope can change, reviews can miss nuance, and ISC2's adaptive live item bank is not public.

## Primary scope references

- ISC2 CISSP Certification Exam Outline: https://www.isc2.org/certifications/cissp/cissp-certification-exam-outline
- ISC2 CISSP Exam Refresh FAQ: https://www.isc2.org/certifications/cissp/cissp-exam-refresh-faq
- ISC2 Code of Ethics: https://www.isc2.org/ethics
