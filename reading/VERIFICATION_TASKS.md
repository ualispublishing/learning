# Educator Release Verification Queue

Updated: 2026-08-19

This queue is separate from generation work. `reading/TASKS.md` tracks curriculum production; this file tracks correctness/release certification.

## Independent educator recertification event — 2026-08-19

- [x] Bind fresh SHA-256 hashes for all Arabic and French A1–C2 canonical JSONL files.
- [x] Run a fresh deterministic scan over all 720 passages / 7,200 questions / 7,200 answers without trusting historical PASS/SEALED verdicts.
- [x] Record the full finding ledger at `reading/audit/independent_educator_deterministic_2026-08-19.json` and compact summary at `reading/audit/independent_educator_deterministic_2026-08-19.summary.json`.
- [x] Record the fail-closed educator decision at `reading/audit/independent_educator_recertification_2026-08-19.json`.
- [ ] **BLOCKER:** deterministic Gate A currently FAILS: 720 `quality.status != approved`, 720 coverage checks not pass, 720 missing/zero known-token coverage values, 714 pending linguistic reviews, 714 pending pedagogical reviews, 714 pending answer-key reviews, and 8 Unicode NFC findings.
- [ ] Substantively revalidate each failed field; do **not** bulk-flip draft/pending metadata merely to pass the audit.
- [ ] Complete fresh 100% learner-facing semantic educator review only after/alongside evidenced record-level revalidation.

Interpretation: the 4,310 open deterministic findings are release-evidence failures, not a claim that 4,310 independent prose errors exist. Stale/unsubstantiated metadata is nevertheless a release blocker under the highest-assurance protocol.

## Global setup

- [x] Add `reading/planning/EDUCATOR_RELEASE_VERIFICATION_PROTOCOL.md`.
- [x] Add independent `reading/RELEASE_STATUS.json` so historical `APPROVED/SEALED` labels cannot be mistaken for educator-release certification.
- [x] Add concise authoritative `reading/AGENT_HANDOFF_V2.md` and demote legacy handoff to historical context.
- [x] Add/standardize machine-readable verification-manifest schema.
- [x] Build deterministic full-corpus verifier that emits per-passage and aggregate findings without auto-rewriting canonical content.
- [x] Build defect ledger format with severity, source, adjudication, repair hash, and recheck status.
- [x] Build canonical hash manifest for all Arabic/French levels before independent review begins (bound in the 2026-08-19 deterministic summary and recertification artifact).

## Arabic A1–C2 re-certification

- [x] Bind hashes for all six canonical levels.
- [x] Run 100% deterministic structural/lexical/Q&A integrity baseline; **result FAIL, blockers unresolved**.
- [ ] Resolve deterministic Gate A blockers with substantive evidence and rerun to PASS.
- [ ] Run fresh 100% linguistic and answer-grounding audit independent of prior PASS artifacts.
- [ ] Run LanguageTool Arabic disagreement scan.
- [ ] Run CAMeL Tools MSA morphology diagnostic scan.
- [ ] Run three independent model-family audits with blinded initial judgments.
- [ ] Adjudicate all machine/model disagreements.
- [ ] Recruit/calibrate native MSA professional proofreader/editor.
- [ ] Complete 100% native professional review.
- [ ] Recruit/calibrate independent Arabic educator/curriculum reviewer.
- [ ] Complete educator review over 100% of learner-facing content.
- [ ] Repair all accepted defects and rerun affected regression checks.
- [ ] Complete blind post-repair human review over 100% of learner-facing content.
- [ ] Confirm zero unresolved critical/major/minor/disagreement items.
- [ ] Generate hash-bound Arabic release manifest.
- [ ] Set Arabic `HASH_BOUND_RELEASED` only after all gates are evidenced against matching hashes.

## French A1–C2 re-certification

- [x] Bind hashes for all six canonical levels.
- [x] Run 100% deterministic structural/lexical/Q&A integrity baseline; **result FAIL, blockers unresolved**.
- [ ] Resolve deterministic Gate A blockers with substantive evidence and rerun to PASS.
- [ ] Run fresh 100% linguistic and answer-grounding audit independent of prior PASS artifacts.
- [ ] Run LanguageTool French disagreement scan.
- [ ] Run Antidote French disagreement scan.
- [ ] Run DeepL Write French disagreement scan.
- [ ] Run three independent model-family audits with blinded initial judgments.
- [ ] Adjudicate all machine/model disagreements.
- [ ] Recruit/calibrate native professional French proofreader/editor.
- [ ] Complete 100% native professional review.
- [ ] Recruit/calibrate independent FLE/CEFR educator/curriculum reviewer.
- [ ] Complete educator review over 100% of learner-facing content.
- [ ] Repair all accepted defects and rerun affected regression checks.
- [ ] Complete blind post-repair human review over 100% of learner-facing content.
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
