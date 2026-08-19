# Educator Release Verification Queue

Updated: 2026-08-19

This queue is separate from generation work. `reading/TASKS.md` tracks curriculum production; this file tracks correctness/release certification.

## French post-repair deterministic Gate A — current frontier

- [x] Merge French A1/A2 repair PR #7 into `main` at `3356eaffcb7bf04feb755d3356089b7a3e7906e8`.
- [x] Bind fresh post-repair SHA-256 hashes for all six French levels.
- [x] Rerun the baseline-equivalent deterministic release-evidence categories over all **360 passages / 3,600 questions / 3,600 answers**.
- [x] Preserve the fresh result at `reading/audit/french_postrepair_deterministic_gate_a_2026-08-19.json`.
- [x] Structural assertions: 60 records per level, contiguous sequences, exactly 10 linked questions/answers per record — PASS.
- [x] Unicode NFC findings in the fresh French run: **0**.
- [ ] **BLOCKER: post-repair deterministic Gate A = FAIL with 2,160 release-evidence findings.**
  - 360 `quality.status != approved`
  - 360 `quality.coverage_check != pass`
  - 360 missing/zero `estimated_known_token_coverage`
  - 360 `quality.linguistic_review != pass`
  - 360 `quality.pedagogical_review != pass`
  - 360 `quality.answer_key_check != pass`
- [ ] Substantively revalidate these record-level evidence fields across 100% of French. **Do not bulk-flip draft/pending metadata merely to clear the gate.**
- [ ] After evidence is actually established, rerun deterministic Gate A and require PASS before educator release can advance.
- [ ] Continue the independent 100% semantic/linguistic/Q&A/educator review against the same final hashes.

Fresh bound hashes:

- A1 `1cdb31ecb8b987c50051bb6f8fa5b2f7fda812cb3004c81ab8697f832fceacba`
- A2 `8fcd71903e6a495a2abaac8d436232b4b7ee00ae5ac0bce4d273aa4a134b3c15`
- B1 `7b1013fa606761bc7cc69fdaf67c66a0efcc9c91c478b1c8a5f8523458f9451b`
- B2 `bfa64c472a93d572d65fbe0217283b9d53bbb0a8d88fee7ea3a3aef1c7993942`
- C1 `dead8e5d6e6e60a7c6c5185996159670e6077ea2d5da31860de168674050b39a`
- C2 `c161c4551a6ce0222850778c02ed0662e00bb60e5386d5dc0b4f31a92cb9f277`

Interpretation: the 2,160 findings are **release-evidence failures**, not a claim that there are 2,160 independent prose mistakes. The earlier repair work demonstrated that real content defects can coexist with stale metadata, so evidence revalidation and semantic review are both required.

## French A1/A2 metalinguistic / CEFR repair — 2026-08-19

- [x] Inventory 88 high-recall candidates (63 A1, 25 A2) against pre-repair hashes.
- [x] Semantically adjudicate all 88 candidates; do not treat scanner hits as automatic defects.
- [x] Repair **63** confirmed formal-metalinguistic/CEFR-inappropriate items across **62 passages**; retain 25 legitimate items.
- [x] Repair seven additional exact duplicate prompts (`corps`, `boire`, `dormir`, `ami`, `travail`, `prix`, `chaussure`).
- [x] Reject the first machine cloze strategy after human review found malformed quotation, sense-drift, and assessment-diversity problems.
- [x] Mark the first human refinement superseded after direct canonical spot-check found semantic role duplication.
- [x] Re-review all 23 former A1 function-label items and convert them to operational use/choice/context-selection tasks.
- [x] Final exact-duplicate scan over all 120 A1/A2 passages: PASS.
- [x] Defined formal-metalinguistic residue under the recorded adjudication rule: **0**.
- [x] Strengthen `reading/planning/TEN_QUESTION_STANDARD.md` so A1/A2 grammar defaults to operational use/form tasks and duplicate assessment roles are prohibited.
- [x] Merge PR #7.

Durable evidence:

- pre-repair inventory: `reading/audit/french_a1_a2_metalinguistic_inventory_2026-08-19.json`
- first guarded repair: `reading/audit/french_a1_a2_metalinguistic_repair_2026-08-19.json`
- post-repair raw rescan: `reading/audit/french_a1_a2_metalinguistic_postrepair_rescan_2026-08-19.json`
- superseded first refinement: `reading/audit/french_a1_a2_metalinguistic_human_refinement_2026-08-19.json`
- authoritative v2 refinement: `reading/audit/french_a1_a2_metalinguistic_human_refinement_v2_2026-08-19.json`

## French C1/C2 confirmed-defect repair — 2026-08-19

- [x] Repair C1 U1 P01–P05 generic vocabulary answers (20 answers).
- [x] Remove C1 U1 P01–P06 learner-facing production/meta language.
- [x] Remove C2 U1 P01–P05 `Révision C1 intégrée` production notes while preserving required review vocabulary.
- [x] Human spot-check and repair C1 P06 after the first machine-clean pass.
- [x] Preserve 10Q/10A linkage, sequence continuity, review vocabulary and broad word bands.
- [x] Merge PR #6.

Evidence:

- `reading/audit/french_c1_c2_educator_defect_repair_2026-08-19.json`
- `reading/audit/french_c1_u01_p06_followup_repair_2026-08-19.json`

## French A1–C2 remaining certification gates

- [ ] Substantively revalidate record-level deterministic Gate A evidence for all 360 records.
- [ ] Rerun deterministic Gate A to PASS.
- [ ] Fresh 100% linguistic, naturalness, pedagogy, target-sense, and answer-grounding audit independent of prior PASS artifacts and repairer judgments.
- [ ] Search for additional templated/generic Q&A, duplicated assessment roles, production/meta leakage, and target-sense mismatches beyond repaired classes.
- [ ] LanguageTool French disagreement pass.
- [ ] Antidote French disagreement pass.
- [ ] DeepL Write French disagreement pass.
- [ ] Three genuinely independent model-family audits with blinded initial judgments.
- [ ] 100% native professional French review.
- [ ] 100% independent FLE/CEFR educator review.
- [ ] Adjudicate/repair all accepted findings and rerun regressions.
- [ ] Complete blind post-repair human review over 100% of learner-facing content.
- [ ] Confirm zero unresolved critical/major/minor/disagreement items.
- [ ] Generate a new hash-bound French release manifest and set `HASH_BOUND_RELEASED` only when every gate matches final hashes.

## Arabic A1–C2 re-certification

- [x] Bind historical baseline hashes for all six canonical levels.
- [x] Run baseline deterministic audit; unresolved evidence blockers remain.
- [ ] Repair/adjudicate known Arabic low-level metalinguistic/CEFR and malformed MSA defect classes corpus-wide.
- [ ] Substantively resolve deterministic Gate A blockers and rerun to PASS.
- [ ] Run fresh 100% linguistic and answer-grounding audit.
- [ ] Run LanguageTool Arabic and CAMeL Tools MSA diagnostics.
- [ ] Run three genuinely independent model-family audits.
- [ ] Complete 100% native professional and independent educator/curriculum review.
- [ ] Complete repair/regression/adjudication and blind post-repair human review.
- [ ] Generate hash-bound Arabic release manifest only at zero unresolved findings.

## Urdu

- [ ] Continue guarded A1 generation from the verified canonical frontier.
- [ ] At each level completion, run the level-level internal final audit.
- [ ] At language release milestone, execute the same highest-assurance independent educator-release protocol.

## Release claim

Until a language reaches `HASH_BOUND_RELEASED` in `reading/RELEASE_STATUS.json`, do not describe it as guaranteed error-free or educator-ready. Use the exact current release state instead.
