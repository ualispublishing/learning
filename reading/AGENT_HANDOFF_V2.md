# Agent Handoff V2 — Graded Reading Curriculum

**Authoritative current handoff.** `reading/AGENT_HANDOFF.md` is legacy historical context and must not drive current work.

Updated: 2026-08-19

## 1. Mandatory read order

For graded-reading work, read:

1. relevant live canonical `reading/<language>/<level>/passages.jsonl`;
2. `reading/RELEASE_STATUS.json` for correctness, teacher use, publication, or release claims;
3. `reading/STATUS.json` for generation/progression state only;
4. this handoff;
5. `reading/planning/EDUCATOR_RELEASE_VERIFICATION_PROTOCOL.md`;
6. `reading/planning/HIGHEST_ASSURANCE_RELEASE_PROFILE.md` for maximum-assurance work;
7. `reading/planning/TEN_QUESTION_STANDARD.md`, current generation policy, schema, durable reading standards/research, roadmap/tasks as needed.

Generation precedence:

`live canonical JSONL > fresh audit artifacts > STATUS > this handoff > current policies/schema > historical artifacts`

Educator-release precedence:

`live canonical JSONL > RELEASE_STATUS > hash-bound verification evidence > highest-assurance protocol > this handoff > deterministic audits > STATUS generation labels > legacy history`

Never infer completion from chat memory.

## 2. Correctness / release rule

Historical `APPROVED`, `SEALED`, `PASS`, and `FINAL_APPROVED` labels prove only that the corpus passed the workflow that existed at that time. They do **not** independently prove educator-ready correctness.

Never claim literal `100% guaranteed correct`, `error-free`, or teacher-ready solely from internal audit status. Highest-assurance release requires complete recorded review coverage, zero unresolved defects/disagreements, and matching release hashes.

The strongest permitted claim after all gates is:

> full corpus independently re-audited; no known defects remain under the recorded protocol.

A teacher/publication release requires `HASH_BOUND_RELEASED` in `reading/RELEASE_STATUS.json` plus a matching manifest.

## 3. French current truth — post-repair Gate A FAIL

French generation is complete A1–C2: **360 passages / 3,600 questions / 3,600 answers**.

Known repaired classes:

- C1/C2 generic vocabulary answers and learner-facing production/meta-note leakage — repaired through PR #6.
- A1/A2 formal-metalinguistic/CEFR assessment class — repaired through PR #7 with superseding v2 human refinement.
- Seven additional exact duplicate A1 prompts discovered during that review were also repaired.
- `TEN_QUESTION_STANDARD.md` now requires operational A1/A2 grammar/form assessment by default and prohibits duplicate assessment roles.

These repairs do **not** recertify French. They changed canonical hashes and invalidated historical release evidence.

### Fresh post-repair deterministic Gate A

Evidence: `reading/audit/french_postrepair_deterministic_gate_a_2026-08-19.json`

Bound canonical commit: `3356eaffcb7bf04feb755d3356089b7a3e7906e8`

Fresh hashes:

- A1 `1cdb31ecb8b987c50051bb6f8fa5b2f7fda812cb3004c81ab8697f832fceacba`
- A2 `8fcd71903e6a495a2abaac8d436232b4b7ee00ae5ac0bce4d273aa4a134b3c15`
- B1 `7b1013fa606761bc7cc69fdaf67c66a0efcc9c91c478b1c8a5f8523458f9451b`
- B2 `bfa64c472a93d572d65fbe0217283b9d53bbb0a8d88fee7ea3a3aef1c7993942`
- C1 `dead8e5d6e6e60a7c6c5185996159670e6077ea2d5da31860de168674050b39a`
- C2 `c161c4551a6ce0222850778c02ed0662e00bb60e5386d5dc0b4f31a92cb9f277`

Structural baseline against those hashes:

- 60 records per level: PASS
- 10 questions + 10 linked answers per record: PASS
- total 360 / 3,600 / 3,600: PASS
- Unicode NFC findings: **0**

Release-evidence result: **FAIL — 2,160 findings**:

- 360 records with `quality.status != approved`
- 360 `coverage_check != pass`
- 360 missing/zero `estimated_known_token_coverage`
- 360 `linguistic_review != pass`
- 360 `pedagogical_review != pass`
- 360 `answer_key_check != pass`

These are evidence failures, not a claim of 2,160 prose mistakes. **Do not bulk-flip the fields.** Each must be backed by substantive record-level review/evidence.

Current French release state: **`REOPEN_REQUIRED`; educator_release_ready = false.**

### Exact next French action

1. substantively revalidate the six record-level Gate A evidence dimensions across all 360 records without changing a field merely to clear the gate;
2. if a content/Q&A defect is found, log and repair it before approving the affected evidence;
3. rerun deterministic Gate A and require PASS;
4. continue fresh 100% semantic/linguistic/naturalness/answer-grounding/educator review independent of the repairer’s judgments;
5. complete independent tool/model/native/educator/blind-human gates before any release claim.

Before computing `estimated_known_token_coverage`, inspect the project’s intended coverage method and existing coverage tooling. Do not invent percentages.

## 4. French durable repair evidence

C1/C2:

- `reading/audit/french_c1_c2_educator_defect_repair_2026-08-19.json`
- `reading/audit/french_c1_u01_p06_followup_repair_2026-08-19.json`

A1/A2:

- pre-repair inventory: `reading/audit/french_a1_a2_metalinguistic_inventory_2026-08-19.json`
- first guarded repair: `reading/audit/french_a1_a2_metalinguistic_repair_2026-08-19.json`
- post-repair raw rescan: `reading/audit/french_a1_a2_metalinguistic_postrepair_rescan_2026-08-19.json`
- superseded first refinement: `reading/audit/french_a1_a2_metalinguistic_human_refinement_2026-08-19.json`
- authoritative v2 refinement: `reading/audit/french_a1_a2_metalinguistic_human_refinement_v2_2026-08-19.json`

Raw high-recall scanner candidate counts are not unresolved-defect counts; use the adjudication/v2 artifact for the repaired class.

## 5. Arabic current state

- Generation complete A1–C2: 360 passages / 3,600 questions / 3,600 answers.
- Historical internal audit passed the prior protocol; highest-assurance educator release is not complete.
- Known open content classes include low-level metalinguistic/CEFR task design and malformed/unnatural MSA grammar-target phrasing from the adversarial review.
- Current state remains non-release-ready; consult `RELEASE_STATUS.json`.

Next Arabic work:

1. repair/adjudicate known content defect classes corpus-wide;
2. substantively resolve/revalidate deterministic evidence blockers;
3. fresh 100% linguistic + Q&A review;
4. LanguageTool Arabic + CAMeL MSA diagnostics;
5. three genuinely independent model-family audits;
6. 100% native MSA professional review;
7. 100% independent educator/curriculum review;
8. repair/regression/adjudication + blind post-repair human review;
9. release manifest only at zero unresolved findings and matching hashes.

## 6. Urdu current generation frontier

Urdu remains the active generation language outside the current correctness priority.

Last confirmed handoff state:

- A1 sequences 1–30 canonical;
- 30 passages / 300 questions / 300 answers;
- Units 01–05 canonical;
- Unit 06 sequences 31–36 staged but not confirmed canonical at that handoff;
- Unit 07 sequences 37–42 staged and non-canonical until Unit 06 promotion is verified;
- source lexicon read-only.

Before resuming Urdu, verify live `main`; do not count staging as canonical.

## 7. Non-negotiables

Generation:

- canonical data is JSONL;
- exactly 10 questions + 10 linked answers per passage unless current policy explicitly changes;
- A1/A2 grammar/form assessment is operational by default, not formal grammatical-label recall;
- avoid duplicate assessment roles;
- validated source lexicons remain read-only;
- target rank/ID/form/sense identity must be source-backed;
- deliberate review and checkpoint zero-new rules must survive repairs;
- fail closed on source/hash drift, IDs/sequences, collisions, exposure/review failures, schema/linkage failures, or learner-facing contamination;
- repair content/metadata rather than weakening valid guards.

Independent review:

- primary language/Q&A/educator review covers 100% of learner-facing content;
- tools/models are detectors, not sole authorities;
- a generator/repairer cannot be its own sole final approver;
- repeated passes from one model do not count as independent model families;
- log exact defect, location, severity, correction, adjudication, and recheck;
- any canonical edit invalidates affected release hashes;
- highest-assurance release requires zero unresolved critical/major/minor/disagreement items and a complete blind human review.

## 8. Handoff hygiene

At durable boundaries:

1. verify live canonical counts/hashes;
2. update `STATUS.json` only for verified generation state;
3. update `RELEASE_STATUS.json` only from actual release evidence;
4. keep one current frontier in this handoff;
5. update `VERIFICATION_TASKS.md` for release/correctness work;
6. store detail in audit artifacts/git history;
7. remove temporary workflows/triggers/scripts after use;
8. preserve pre/post-repair evidence separately;
9. never leave contradictory next-action sections.

## 9. Fail-closed conditions

Stop rather than guess when:

- canonical state disagrees with status/handoff;
- required audit evidence is absent;
- a release hash does not match canonical content;
- vocabulary source identity cannot be verified;
- a reviewer disagreement remains unresolved;
- independent/human coverage is incomplete;
- the only evidence for correctness is an older PASS/SEALED label.

Record the blocker and exact next verification action.
