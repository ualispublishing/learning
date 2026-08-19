# Educator Release Verification Queue

Updated: 2026-08-19

This queue is separate from generation work. `reading/TASKS.md` tracks curriculum production; this file tracks correctness/release certification.

## Global setup

- [x] Add `reading/planning/EDUCATOR_RELEASE_VERIFICATION_PROTOCOL.md`.
- [x] Add independent `reading/RELEASE_STATUS.json` so historical `APPROVED/SEALED` labels cannot be mistaken for educator-release certification.
- [x] Add concise authoritative `reading/AGENT_HANDOFF_V2.md` and demote legacy handoff to historical context.
- [ ] Add/standardize machine-readable verification-manifest schema.
- [ ] Build deterministic full-corpus verifier that emits per-passage and aggregate findings without auto-rewriting canonical content.
- [ ] Build defect ledger format with severity, source, adjudication, repair hash, and recheck status.
- [ ] Build canonical hash manifest for all levels before independent review begins.

## Arabic A1–C2 re-certification

- [ ] Bind hashes for all six canonical levels.
- [ ] Run 100% deterministic structural/lexical/Q&A integrity pass.
- [ ] Run fresh 100% linguistic and answer-grounding audit independent of prior PASS artifacts.
- [ ] Run LanguageTool Arabic disagreement scan.
- [ ] Run CAMeL Tools MSA morphology diagnostic scan.
- [ ] Run three independent model-family audits with blinded initial judgments.
- [ ] Adjudicate all machine/model disagreements.
- [ ] Recruit/calibrate native MSA professional proofreader/editor.
- [ ] Complete 100% native professional review.
- [ ] Recruit/calibrate independent Arabic educator/curriculum reviewer.
- [ ] Complete educator review.
- [ ] Repair all accepted defects and rerun affected regression checks.
- [ ] Blind post-repair review with risk-based + random coverage; strongest target is complete second review.
- [ ] Confirm zero unresolved critical/major/minor/disagreement items.
- [ ] Generate hash-bound Arabic release manifest.
- [ ] Set Arabic `HASH_BOUND_RELEASED` only after all gates are evidenced against matching hashes.

## French A1–C2 re-certification

- [ ] Bind hashes for all six canonical levels.
- [ ] Run 100% deterministic structural/lexical/Q&A integrity pass.
- [ ] Run fresh 100% linguistic and answer-grounding audit independent of prior PASS artifacts.
- [ ] Run LanguageTool French disagreement scan.
- [ ] Run Antidote French disagreement scan.
- [ ] Run DeepL Write French disagreement scan.
- [ ] Run three independent model-family audits with blinded initial judgments.
- [ ] Adjudicate all machine/model disagreements.
- [ ] Recruit/calibrate native professional French proofreader/editor.
- [ ] Complete 100% native professional review.
- [ ] Recruit/calibrate independent FLE/CEFR educator/curriculum reviewer.
- [ ] Complete educator review.
- [ ] Repair all accepted defects and rerun affected regression checks.
- [ ] Blind post-repair review with risk-based + random coverage; strongest target is complete second review.
- [ ] Confirm zero unresolved critical/major/minor/disagreement items.
- [ ] Generate hash-bound French release manifest.
- [ ] Set French `HASH_BOUND_RELEASED` only after all gates are evidenced against matching hashes.

## Urdu

- [ ] Continue guarded A1 generation from the verified canonical frontier.
- [ ] Apply deterministic quality guards during generation.
- [ ] Do not spend full external-certification effort on incomplete language-wide corpus unless a severe defect justifies early specialist review.
- [ ] At each level completion, run level-level internal final audit.
- [ ] At language release milestone, execute the same independent educator-release protocol used for Arabic/French.

## Reviewer calibration requirement

Before assigning a full external review:

- [ ] Create non-canonical calibration copies of 10–20 passages.
- [ ] Seed known linguistic, naturalness, answer-key, and level-placement defects.
- [ ] Blind the candidate reviewer to seeded locations.
- [ ] Reject any reviewer who misses seeded major defects.
- [ ] Compare two candidate reviewers on a shared subset when feasible.
- [ ] Record qualifications, target variety, calibration results, and coverage assignment with privacy-safe reviewer IDs.

## Release claim

Until a language reaches `HASH_BOUND_RELEASED` in `reading/RELEASE_STATUS.json`, do not describe it as guaranteed error-free or educator-ready. Use the exact current release state instead.
