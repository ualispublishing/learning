# Educator Release Verification Queue

Updated: 2026-08-19

This queue is separate from generation work. `reading/TASKS.md` tracks curriculum production; this file tracks correctness/release certification.

## French A1/A2 metalinguistic / CEFR repair — 2026-08-19

- [x] Use the adversarial educator finding as a defect-class trigger rather than trusting historical approval.
- [x] Run a high-recall French A1/A2 candidate inventory against the pre-repair hashes: **88 candidates** (63 A1, 25 A2).
- [x] Preserve the original inventory at `reading/audit/french_a1_a2_metalinguistic_inventory_2026-08-19.json`; do not overwrite it with post-repair rescans.
- [x] Semantically adjudicate all 88 candidates instead of treating scanner hits as automatic defects.
- [x] Confirm and repair **63** formal-metalinguistic/CEFR-inappropriate items across **62 passages**; retain 25 legitimate form-choice/comprehension/context items.
- [x] Preserve target IDs, sequences, and 10Q/10A linkage.
- [x] Detect and repair seven additional pre-existing exact duplicate prompts (`corps`, `boire`, `dormir`, `ami`, `travail`, `prix`, `chaussure`).
- [x] Human-review the first machine repair and reject copied-passage clozes, malformed nested quotation cases, and target-sense drift (`avec`, `encore`, `même`).
- [x] Mark the first human refinement **superseded** after direct canonical spot-check found semantic assessment duplication.
- [x] Re-review all **23 former A1 function-label items** and convert them to operational use/choice/context-selection tasks so existing meaning questions remain distinct.
- [x] Run final exact-duplicate scan across all **120 A1/A2 passages**: PASS.
- [x] Final defined formal-metalinguistic residue: **0** under the recorded adjudication rule.
- [x] Strengthen `TEN_QUESTION_STANDARD.md`: A1/A2 grammar defaults to operational form/use/reference/choice; formal grammatical labels require explicit justification; duplicate assessment roles are prohibited.
- [x] Preserve post-repair raw scanner output separately at `reading/audit/french_a1_a2_metalinguistic_postrepair_rescan_2026-08-19.json`; raw candidate counts are not unresolved-defect counts.
- [x] Authoritative final repair evidence: `reading/audit/french_a1_a2_metalinguistic_human_refinement_v2_2026-08-19.json`.
- [x] Final recorded A1 hash: `1cdb31ecb8b987c50051bb6f8fa5b2f7fda812cb3004c81ab8697f832fceacba`.
- [x] Final recorded A2 hash: `8fcd71903e6a495a2abaac8d436232b4b7ee00ae5ac0bce4d273aa4a134b3c15`.
- [ ] Merge PR #7 after final diff/scaffolding cleanup.
- [ ] Bind fresh post-repair hashes for **all six French levels** and rerun deterministic Gate A.
- [ ] Continue fresh 100% French semantic educator recertification; this repair does **not** make French educator-ready.

## French C1/C2 confirmed-defect repair — 2026-08-19

- [x] Confirm C1 Unit 01 P01–P05 contained 20 generic vocabulary answers.
- [x] Confirm C1 Unit 01 P01–P06 contained learner-facing production/meta language.
- [x] Confirm C2 Unit 01 P01–P05 contained learner-facing `Révision C1 intégrée` production notes.
- [x] Repair all 20 generic C1 vocabulary answers with context-specific answers.
- [x] Replace identified C1/C2 production notes with natural learner-facing language while preserving exact scheduled review terms.
- [x] Repair the additional C1 P06 wording defects found by human spot-check after the first machine-clean pass.
- [x] Preserve 10Q/10A linkage, sequence continuity, review vocabulary and level word bands.
- [x] Run identified C1/C2 defect-class residue scan: zero remaining hits for the known patterns.
- [x] Merge guarded repair through PR #6.
- [x] Mark French release state `REOPEN_REQUIRED`; historical French release hashes are invalid after canonical edits.
- [x] Preserve evidence at `reading/audit/french_c1_c2_educator_defect_repair_2026-08-19.json` and `reading/audit/french_c1_u01_p06_followup_repair_2026-08-19.json`.

Recorded repaired hashes:

- French C1: `dead8e5d6e6e60a7c6c5185996159670e6077ea2d5da31860de168674050b39a`
- French C2: `c161c4551a6ce0222850778c02ed0662e00bb60e5386d5dc0b4f31a92cb9f277`

## Independent educator recertification baseline — 2026-08-19

- [x] Bind baseline SHA-256 hashes for Arabic/French A1–C2.
- [x] Scan all 720 passages / 7,200 questions / 7,200 answers without trusting historical PASS/SEALED verdicts.
- [x] Record baseline ledger and fail-closed recertification decision.
- [ ] Regenerate French baseline hashes/results after all current repairs; original French hashes are historical only.
- [ ] Resolve/revalidate deterministic Gate A evidence failures with substantive evidence; do **not** bulk-flip draft/pending metadata merely to pass.

Interpretation: the baseline 4,310 deterministic findings were release-evidence failures, not 4,310 proven prose errors. Later educator review demonstrated that real content/Q&A defects existed, so both evidence repair and full semantic review are required.

## Arabic A1–C2 re-certification

- [x] Bind baseline hashes for all six canonical levels.
- [x] Run 100% deterministic baseline; unresolved evidence blockers remain.
- [ ] Repair/adjudicate known Arabic low-level metalinguistic/CEFR and malformed MSA defect classes corpus-wide.
- [ ] Substantively resolve deterministic Gate A blockers and rerun to PASS.
- [ ] Run fresh 100% linguistic and answer-grounding audit independent of prior PASS artifacts.
- [ ] Run LanguageTool Arabic disagreement scan and CAMeL Tools MSA morphology diagnostics.
- [ ] Run three genuinely independent model-family audits with blinded initial judgments.
- [ ] Complete 100% native professional and 100% independent educator/curriculum review.
- [ ] Repair/adjudicate all accepted findings and complete blind post-repair human review.
- [ ] Confirm zero unresolved findings/disagreements and generate hash-bound Arabic release manifest.

## French A1–C2 re-certification

- [x] Bind historical baseline hashes for all six levels.
- [x] Repair C1/C2 generic-answer/production-note class.
- [x] Repair defined A1/A2 formal-metalinguistic/CEFR class under superseding v2 human refinement.
- [ ] Bind fresh post-repair hashes for **all six** French levels and rerun deterministic Gate A.
- [ ] Resolve remaining Gate A evidence blockers with substantive review evidence.
- [ ] Run fresh 100% linguistic, naturalness, pedagogy, target-sense, and answer-grounding audit independent of prior PASS artifacts and repairer judgments.
- [ ] Search for additional templated/generic Q/A, duplicate assessment roles, production/meta leakage, and target-sense mismatches beyond the known repaired classes.
- [ ] Run LanguageTool French, Antidote, and DeepL Write disagreement scans.
- [ ] Run three genuinely independent model-family audits with blinded initial judgments.
- [ ] Complete 100% native professional French review and 100% independent FLE/CEFR educator review.
- [ ] Repair/adjudicate all accepted findings and rerun regressions.
- [ ] Complete blind post-repair human review over 100% of learner-facing content.
- [ ] Confirm zero unresolved critical/major/minor/disagreement items.
- [ ] Generate a new hash-bound French release manifest and set `HASH_BOUND_RELEASED` only when every gate matches final hashes.

## Urdu

- [ ] Continue guarded A1 generation from the verified canonical frontier.
- [ ] Apply deterministic quality guards during generation.
- [ ] At each level completion, run level-level internal final audit.
- [ ] At language release milestone, execute the same independent educator-release/highest-assurance protocol.

## Reviewer calibration requirement

Before assigning a full external review:

- [ ] Create non-canonical calibration copies of 10–20 passages.
- [ ] Seed known linguistic, naturalness, answer-key, and level-placement defects.
- [ ] Blind the candidate reviewer to seeded locations.
- [ ] Reject reviewers who miss seeded major defects.
- [ ] Compare two candidates on a shared subset when feasible.
- [ ] Record qualifications, target variety, calibration results, and coverage assignment with privacy-safe reviewer IDs.

## Release claim

Until a language reaches `HASH_BOUND_RELEASED` in `reading/RELEASE_STATUS.json`, do not describe it as guaranteed error-free or educator-ready. Use the exact current release state instead.
