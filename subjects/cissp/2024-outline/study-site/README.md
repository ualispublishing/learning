# CISSP Atlas — Current Outline Study Workflow

Unofficial, original study site mapped to the current public ISC2 CISSP exam outline (effective 2024-04-15).

## v1.27.0 release candidate

- 8 CISSP domains; official weights total **100%**.
- **62** numbered public objectives and **344** paraphrased subtopic checks.
- **306/344** checks with explicit enriched-subtopic practice exposure.
- **33** AI-security coverage areas and **140** layered retrieval cards.
- **527 released standard scenario questions + 1 Bellringer = 528 released bank records** in the v1.27 release candidate.
- Author-difficulty mix: **F41 / E369 / S117 / B1**.
- **527/527** standard questions have four-option teaching rationales.
- **668 learner-facing item IDs** in the combined semantic-audit ledger.
- **20** primary/reference sources.

Batch 029 completed candidate PR #125 and bookkeeping PR #126 with exact-head, exact-main, originality, logical-mix, browser, aggregate, and Pages-isolation controls passing. This branch promotes those 16 reviewed questions to v1.27.0. Public production remains the verified v1.26.0 release until this exact release head is validated, merged, and the live Pages fingerprint passes.

## Semantic-review boundary

The combined ledgers cover **668 learner-facing item IDs** after Batch 029 promotion. Batch 029 contributes 16 reviewed items. The release candidate records zero known keyed-answer reversals and zero known remaining material factual errors within the documented review boundary. This is an auditable quality claim, not an infallibility or exam-pass guarantee.

## Study workflow

Use **diagnose → retrieve → apply → repair → re-test later**. Run the diagnostic once for routing, retrieve before revealing, use Exam + Stretch for standard practice, commit confidence before answering, review all four rationales, repair high-confidence misses first, and use Bellringers separately as non-exam-representative integrative drills.

Keyboard review flow: **Space toggles reveal/hide; ←/→ move cards while hidden and layers while revealed; 1–4 grades the revealed card.**

## Question-bank expansion

The long-term target remains **800 records** with an authoring mix of 15% Foundation+, 60% Exam-calibrated, 20% Stretch, and 5% Bellringer. After Batch 029 promotion, remaining deficits are **F79 / E111 / S43 / B39**, or **272 records**. All 62 objectives have at least one standard-MCQ exposure. Explicit enriched-subtopic exposure is **306/344**; this is authoring coverage, not learner mastery.

Batch 030 is provisionally planned at E12/S4 across `7.5, 7.7, 7.8, 1.12, 7.9, 7.12, 8.4, 1.2, 1.6, 1.9, 1.7, 3.10, 3.2, 3.4, 3.5, 3.3`. Do not begin it as authoritative released-only work until v1.27 post-merge and public verification close.

## Continuous audit

`.github/workflows/cissp-study-site-audit.yml` enforces knowledge/schema consistency, semantic coverage, originality/duplicate controls, logical batch composition, planning, JavaScript syntax, rationales, static assets, interactive browser flows, and an aggregate gate. `.github/workflows/cissp-pages.yml` independently audits and assembles a released-only artifact and verifies the public runtime fingerprint.

## Accuracy boundary

The strongest warranted v1.27 release-candidate claim is: **no known material factual errors or incorrect keyed answers are recorded as remaining; 668 learner-facing item IDs have explicit semantic status, and the release records zero known keyed-answer reversals.** Standards and public scope can change, reviews can miss nuance, and ISC2's adaptive live item bank is not public.

## Primary scope references

- ISC2 CISSP Certification Exam Outline: https://www.isc2.org/certifications/cissp/cissp-certification-exam-outline
- ISC2 CISSP Exam Refresh FAQ: https://www.isc2.org/certifications/cissp/cissp-exam-refresh-faq
- ISC2 Code of Ethics: https://www.isc2.org/ethics
