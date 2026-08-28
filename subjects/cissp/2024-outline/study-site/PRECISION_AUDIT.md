# CISSP Atlas Precision Audit — Current Released State

## Result

**Published-scope mapping: PASS. Released-item semantic review: PASS, with explicit nuance notes. Public release verification: PASS for v1.22.0.**

The site remains mapped to the current public ISC2 CISSP exam outline, effective April 15, 2024, plus the cross-domain AI-security coverage represented in the live public outline.

## v1.22.0 released scope

- 8/8 domains with official weights **16/10/13/13/13/12/13/10 = 100%**.
- **62/62** numbered public objectives.
- **344** paraphrased public-outline subtopic checks.
- **302/344** subtopic checks currently carry explicit enriched-subtopic practice exposure.
- **33** AI-security coverage areas across all 8 domains.
- **140** layered retrieval cards.
- **447 released standard scenario questions**.
- **1 released Bellringer**, explicitly non-exam-representative.
- **448 total released question-bank records**.
- **447/447** released standard questions have four-option teaching rationales.
- **20** primary/reference sources.
- 588 learner-facing item IDs represented across `SEMANTIC_ITEM_AUDIT.json` and `SEMANTIC_RELEASE_ADDITIONS.json`.

Released author-difficulty distribution is **F41 / E309 / S97 / B1**. Difficulty labels are an authoring/calibration scale rather than an empirically equated promise of live-exam difficulty.

## Item-level semantic audit

Every currently released learner-facing item ID has an explicit semantic status in the combined ledgers.

- Base semantic ledger: **300 items**.
- Release-additions ledger: **288 items**.
- Combined: **588 items**.
- **585 VERIFIED**.
- **1 VERIFIED_AFTER_CORRECTION**.
- **2 VERIFIED_WITH_SOURCE_SCOPE_NOTE**.
- **0 answer-key reversals**.
- **0 material factual errors recorded as remaining after review**.

### Correction retained

`HY-014` states that digital signatures provide integrity and origin authentication and can **support** nonrepudiation when signer identity, private-key control, certificate/key validity, and supporting evidence are trustworthy. A signature does not itself provide confidentiality or automatically guarantee nonrepudiation.

### Source-scope notes retained

`AI-005` and `PX-020` remain factually valid under the CISSP outline's non-human/agent/service-account scope. NIST SP 800-63-4 is supporting digital-identity context rather than the sole primary authority for those non-human identity claims.

## Released question-bank state

The current bank contains the frozen 56-question baseline plus promoted original batches tracked by `question-bank/RELEASED_BATCHES.json`.

- Baseline standard questions: **56**.
- Manifest-promoted records: **392**.
- Current total standard questions: **447**.
- Current Bellringers: **1**.
- Current total bank records: **448**.
- Current released difficulty: **F41 / E309 / S97 / B1**.
- Current unreleased candidates: **0**.

Every promoted record must carry semantic-review status and `original-from-public-scope` provenance. Candidate/release controls reject external question seeds and compare against the released corpus using exact, near-text, and structural duplicate checks.

## Legacy 56-question rationale backfill

The original Q-001..Q-056 set remains semantically frozen in its stem, option text, and keyed-answer layer.

A separate `legacy-rationales.js` layer provides four individualized option rationales for each of those 56 questions, for **224 reviewed rationale statements** total. `LEGACY_RATIONALE_AUDIT.json` records the method and results. CI fails unless all Q-001..Q-056 IDs each expose exactly four non-empty rationales.

Together with native rationales on promoted standard questions, **447/447** currently released standard questions support four-option teaching feedback.

## Study-quality controls

The current release includes:

- a 16-question diagnostic used only as a routing signal;
- retrieval-before-reveal layered cards and browser-local spaced-review state;
- weighted domain mastery and weak-objective recommendations;
- Foundation+, Exam-calibrated, Stretch, Exam+Stretch, and All Available practice filters;
- confidence commitment before standard-question answering;
- persistent attempt history and high-confidence-miss prioritization;
- four-option rationale rendering on every released standard question;
- a separate Bellringer mode labeled **NON-EXAM-REPRESENTATIVE INTEGRATIVE DRILL**;
- constructed-response Bellringer prompts, delayed rubric reveal, and self-scoring;
- progress export/reset plus current-state display;
- global search, keyboard controls, responsive desktop/mobile layouts, and browser-smoke coverage for startup, review, practice, progress, sources, and navigation.

## Originality, coverage, and expansion controls

`question-bank/quality_gate.py` treats the released bank as permanent comparison corpus. New candidates must pass:

- valid objective/subtopic/source mappings;
- semantic-review status;
- originality provenance (`original-from-public-scope`, no external question seed);
- tier/score calibration rules;
- exact normalized duplicate rejection;
- near-text sequence and token-shingle checks;
- structural scenario/rule/misconception duplicate checks;
- four option rationales for MCQs;
- Bellringer structure/rubric rules.

For each candidate batch with at least 16 records, Exam-calibrated items must remain at least 50%, Bellringers may not exceed 10%, and no single primary domain may exceed **35% of the standard MCQs in that batch**.

`question-bank/coverage_report.py` reports per-objective F/E/S density, explicit enriched-subtopic exposure, remaining difficulty counts toward the 800-record target, and a weighted priority queue. `question-bank/batch_planner.py` converts that state into an executable next-batch target without authoring questions.

All **62/62** numbered objectives currently have at least one standard-MCQ exposure in the released corpus. Explicit enriched-subtopic tagging currently measures **302/344** checks. Neither metric is a learner-mastery claim, and one mapped question does not imply sufficient depth.

## Next expansion state

There is currently **no unreleased candidate batch**. The released-only v1.22 planner recommends Batch 025 with an **E12 / S4** mix, using materially new scenario families and thin concepts. The authoritative objective/domain slate is stored in `RELEASE_STATUS.json` rather than duplicated here so that planning prose cannot silently outrun the executable planner.

The 800-record maturity target currently leaves authoring deficits of **F79 / E171 / S63 / B39** relative to its 15% / 60% / 20% / 5% target mix.

## Release and public-runtime evidence

Public **v1.22.0** is verified rather than merely staged.

- Candidate Batch 024 native PR validation: PASS.
- Candidate exact-main validation: PASS.
- Candidate Pages isolation: PASS.
- Released-state PR #90 audit: **PASS**.
- Release merge commit: `4a82d17521dae08791e8b2cf66b92e21fe11167b`.
- Exact post-promotion main audit workflow `33192924868`: **PASS**.
- GitHub Pages workflow `33192924697`: **PASS**.
- Live public fingerprint: **v1.22.0 / 447 standard / 392 manifest released records / 1 Bellringer / released_only=true**.

The release ledger intentionally stores stable historical verification evidence rather than claiming a self-referential deployment SHA after every bookkeeping edit.

## Accuracy boundary

The strongest warranted claim for the current release is:

> **No known material factual errors or incorrect keyed answers are recorded as remaining in the documented semantic audit boundary; 588 released learner-facing item IDs have explicit audit status, and the current release records zero known keyed-answer reversals.**

That is not the same as an absolute “100% infallible forever” guarantee. Standards and public scope can change, reviews can miss nuance, and ISC2's live adaptive item bank is not public. CISSP Atlas does not claim that memorization guarantees passing.

## Known non-blocking limitations

- Browser-local progress does not sync across devices unless exported manually.
- The diagnostic is intentionally a routing signal, not an exam-readiness prediction.
- Blueprint subtopic labels are paraphrased; the ISC2 source remains authoritative for exact wording.
- Legacy Q-001..Q-056 predate explicit enriched-subtopic tags, so enriched exposure is a metadata measurement rather than proof that an untagged concept has never appeared.
- Difficulty is an authoring scale until sufficient real learner-response data exists for empirical calibration.

## Primary scope references

- ISC2 CISSP Certification Exam Outline: https://www.isc2.org/certifications/cissp/cissp-certification-exam-outline
- ISC2 CISSP Exam Refresh FAQ: https://www.isc2.org/certifications/cissp/cissp-exam-refresh-faq
- ISC2 Code of Ethics: https://www.isc2.org/ethics

Supporting standards are registered in `data-meta.js` and shown in the site's Sources view.
