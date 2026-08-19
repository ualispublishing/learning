# Educator Release Verification Queue

Updated: 2026-08-19

This queue is separate from generation work. `reading/TASKS.md` tracks curriculum production; this file tracks correctness/release certification.

## French C1/C2 confirmed-defect repair — 2026-08-19

- [x] Independently identify concrete canonical French defects rather than trusting historical approval labels.
- [x] Confirm C1 Unit 01 P01–P05 contained 20 generic vocabulary answers that did not answer the requested target-specific questions.
- [x] Confirm C1 Unit 01 P01–P06 contained learner-facing production/meta language.
- [x] Confirm C2 Unit 01 P01–P05 contained learner-facing `Révision C1 intégrée` production notes.
- [x] Repair all 20 generic C1 vocabulary answers with context-specific answers.
- [x] Replace identified C1/C2 production notes with natural learner-facing language while preserving exact scheduled review terms.
- [x] Repair the additional C1 P06 wording defects found by human spot-check after the first machine-clean pass.
- [x] Preserve 10Q/10A linkage, sequence continuity, review vocabulary and level word bands.
- [x] Run the identified C1/C2 defect-class residue scan: zero remaining hits for the known generic-answer/production-note patterns.
- [x] Merge the guarded repair through PR #6.
- [x] Mark French release state `REOPEN_REQUIRED`; historical French release hashes are invalid after canonical edits.
- [x] Preserve repair evidence at `reading/audit/french_c1_c2_educator_defect_repair_2026-08-19.json` and `reading/audit/french_c1_u01_p06_followup_repair_2026-08-19.json`.
- [x] Remove temporary repair workflows, runner script, and trigger markers after merge.
- [ ] Rerun the full deterministic/semantic educator recertification against the repaired canonical corpus.
- [ ] Search all French A1–C2 learner-facing content for **other** templated/generic Q/A classes and production/meta-language patterns beyond the specific strings already repaired.
- [ ] Do not restore French approval until every strengthened release gate is independently evidenced against current hashes.

Current recorded post-repair SHA-256 evidence:

- French C1: `dead8e5d6e6e60a7c6c5185996159670e6077ea2d5da31860de168674050b39a`
- French C2: `c161c4551a6ce0222850778c02ed0662e00bb60e5386d5dc0b4f31a92cb9f277`

## Independent educator recertification baseline — 2026-08-19

- [x] Bind fresh SHA-256 hashes for all Arabic and French A1–C2 canonical JSONL files at baseline.
- [x] Run a fresh deterministic scan over all 720 passages / 7,200 questions / 7,200 answers without trusting historical PASS/SEALED verdicts.
- [x] Record the baseline ledger at `reading/audit/independent_educator_deterministic_2026-08-19.json` and compact summary at `reading/audit/independent_educator_deterministic_2026-08-19.summary.json`.
- [x] Record the fail-closed decision at `reading/audit/independent_educator_recertification_2026-08-19.json`.
- [ ] Resolve/revalidate deterministic Gate A evidence failures with substantive evidence; do **not** bulk-flip draft/pending metadata merely to pass.
- [ ] Regenerate baseline hashes/audit results after canonical changes; the original French C1/C2 hashes are historical only.

Interpretation: the earlier 4,310 deterministic findings were release-evidence failures, not 4,310 proven prose errors. The later educator review nevertheless demonstrated that real prose/Q&A defects existed, so both evidence repair and content review are required.

## Global setup

- [x] Add `reading/planning/EDUCATOR_RELEASE_VERIFICATION_PROTOCOL.md`.
- [x] Add `reading/planning/HIGHEST_ASSURANCE_RELEASE_PROFILE.md`.
- [x] Add `reading/RELEASE_STATUS.json` so historical `APPROVED/SEALED` labels cannot be mistaken for educator-release certification.
- [x] Add concise authoritative `reading/AGENT_HANDOFF_V2.md` and demote legacy handoff to historical context.
- [x] Add/standardize verification finding and release-manifest schemas.
- [x] Build deterministic full-corpus verifier/ledger infrastructure.

## Arabic A1–C2 re-certification

- [x] Bind baseline hashes for all six canonical levels.
- [x] Run 100% deterministic baseline; result contains unresolved evidence blockers.
- [ ] Substantively resolve deterministic Gate A blockers and rerun to PASS.
- [ ] Run fresh 100% linguistic and answer-grounding audit independent of prior PASS artifacts.
- [ ] Run LanguageTool Arabic disagreement scan.
- [ ] Run CAMeL Tools MSA morphology diagnostic scan.
- [ ] Run three genuinely independent model-family audits with blinded initial judgments.
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

- [x] Bind baseline hashes for all six canonical levels.
- [x] Run 100% deterministic baseline; result contains unresolved evidence blockers.
- [x] Repair the confirmed C1/C2 generic-answer and production-language defect class described above.
- [ ] Bind fresh post-repair hashes for all six French levels and rerun deterministic Gate A.
- [ ] Resolve remaining Gate A evidence blockers with substantive review evidence.
- [ ] Run fresh 100% linguistic, naturalness, pedagogy, and answer-grounding audit independent of prior PASS artifacts.
- [ ] Run LanguageTool French disagreement scan.
- [ ] Run Antidote French disagreement scan.
- [ ] Run DeepL Write French disagreement scan.
- [ ] Run three genuinely independent model-family audits with blinded initial judgments.
- [ ] Adjudicate all machine/model disagreements.
- [ ] Recruit/calibrate native professional French proofreader/editor.
- [ ] Complete 100% native professional review.
- [ ] Recruit/calibrate independent FLE/CEFR educator/curriculum reviewer.
- [ ] Complete educator review over 100% of learner-facing content.
- [ ] Repair all newly accepted defects and rerun affected regression checks.
- [ ] Complete blind post-repair human review over 100% of learner-facing content.
- [ ] Confirm zero unresolved critical/major/minor/disagreement items.
- [ ] Generate a new hash-bound French release manifest.
- [ ] Set French `HASH_BOUND_RELEASED` only after all gates are evidenced against matching hashes.

## Urdu

- [ ] Continue guarded A1 generation from the verified canonical frontier.
- [ ] Apply deterministic quality guards during generation.
- [ ] Do not spend full external-certification effort on the incomplete language-wide corpus unless a severe defect justifies early specialist review.
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
