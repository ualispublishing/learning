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
7. current generation policy, `reading/planning/TEN_QUESTION_STANDARD.md`, schema, durable reading standards/research, roadmap/tasks as needed.

Generation precedence:

`live canonical JSONL > fresh audit artifacts > STATUS > this handoff > current policies/schema > historical artifacts`

Educator-release precedence:

`live canonical JSONL > RELEASE_STATUS > hash-bound verification evidence > highest-assurance protocol > this handoff > deterministic audits > STATUS generation labels > legacy history`

Never infer completion from chat memory.

## 2. Correctness / release rule

Historical `APPROVED`, `SEALED`, `PASS`, and `FINAL_APPROVED` labels prove only that the corpus passed the workflow that existed at that time. They do **not** independently prove educator-ready correctness.

Never claim literal `100% guaranteed correct`, `error-free`, or teacher-ready solely from internal audit status. For this project, highest-assurance release requires complete recorded review coverage, zero unresolved defects/disagreements, and matching release hashes.

The strongest permitted claim after all gates is:

> full corpus independently re-audited; no known defects remain under the recorded protocol.

A teacher/publication release requires `HASH_BOUND_RELEASED` in `reading/RELEASE_STATUS.json` plus a matching manifest.

## 3. French repair history that affects current hashes

Two independent educator-repair streams changed canonical French on 2026-08-19.

### C1/C2 generic-answer / production-note class

Repaired through PR #6. Evidence:

- `reading/audit/french_c1_c2_educator_defect_repair_2026-08-19.json`
- `reading/audit/french_c1_u01_p06_followup_repair_2026-08-19.json`

Result:

- 11 passages repaired;
- 20 generic vocabulary answers replaced;
- learner-facing generation/review-note leakage removed;
- scheduled review forms and 10Q/10A linkage preserved;
- additional P06 human spot-check repair completed.

Recorded repaired hashes:

- C1 `dead8e5d6e6e60a7c6c5185996159670e6077ea2d5da31860de168674050b39a`
- C2 `c161c4551a6ce0222850778c02ed0662e00bb60e5386d5dc0b4f31a92cb9f277`

### A1/A2 low-level metalinguistic / CEFR class

A high-recall scan found 88 candidates (63 A1, 25 A2). Every candidate was semantically adjudicated rather than treated as an automatic defect. Evidence:

- original pre-repair inventory: `reading/audit/french_a1_a2_metalinguistic_inventory_2026-08-19.json`
- first guarded repair: `reading/audit/french_a1_a2_metalinguistic_repair_2026-08-19.json`
- post-repair rescan preserved separately: `reading/audit/french_a1_a2_metalinguistic_postrepair_rescan_2026-08-19.json`
- first human refinement, intentionally marked superseded after a direct semantic spot-check: `reading/audit/french_a1_a2_metalinguistic_human_refinement_2026-08-19.json`
- authoritative superseding review: `reading/audit/french_a1_a2_metalinguistic_human_refinement_v2_2026-08-19.json`

Current result for the **defined class**:

- 63 confirmed low-level formal-metalinguistic items repaired across 62 passages;
- 25 high-recall candidates retained as legitimate form-choice/comprehension/context questions;
- seven additional pre-existing exact duplicate prompts repaired;
- all 23 former A1 function-label replacements received a second semantic refinement so they test operational use/choice rather than duplicate existing meaning questions;
- all 120 A1/A2 passages passed the final exact-duplicate prompt scan;
- 10Q/10A, sequence, linkage, and target IDs preserved;
- defined formal-metalinguistic residue = 0 under the recorded adjudication rule.

Final recorded hashes from the v2 artifact:

- A1 `1cdb31ecb8b987c50051bb6f8fa5b2f7fda812cb3004c81ab8697f832fceacba`
- A2 `8fcd71903e6a495a2abaac8d436232b4b7ee00ae5ac0bce4d273aa4a134b3c15`

`TEN_QUESTION_STANDARD.md` was strengthened so A1/A2 grammar slots default to operational form/use/reference/choice tasks and do not require formal category labels without explicit pedagogical justification.

**None of these repairs re-certify French.** They invalidate older release hashes. French remains `REOPEN_REQUIRED` until the strengthened independent protocol is rerun against the final canonical corpus.

## 4. Arabic current state

- Generation: complete A1–C2; 360 passages / 3,600 questions / 3,600 answers.
- Historical internal audit: PASS under the prior protocol.
- Highest-assurance educator release: **not complete**.
- Known open content classes include low-level metalinguistic/CEFR task design and malformed/unnatural MSA grammar-target phrasing identified by the adversarial review.
- Current release state remains non-release-ready; consult `reading/RELEASE_STATUS.json`.

Next Arabic certification work:

1. substantively resolve/revalidate deterministic Gate A and rerun it;
2. repair/adjudicate the known Arabic defect classes corpus-wide;
3. perform fresh 100% linguistic + Q/A review;
4. LanguageTool Arabic + CAMeL MSA diagnostics;
5. three genuinely independent model-family audits;
6. 100% native MSA professional review;
7. 100% independent educator/curriculum review;
8. repair/regression/adjudication and complete blind post-repair human review;
9. issue a hash-bound release manifest only at zero unresolved defects.

## 5. French current state

- Generation: complete A1–C2; 360 passages / 3,600 questions / 3,600 answers.
- Historical internal/hash-bound audit: PASS under the previous protocol, now insufficient and hash-invalidated by canonical repairs.
- Defined C1/C2 generic-answer/production-note class: **repaired**.
- Defined A1/A2 formal-metalinguistic/CEFR class: **repaired under superseding v2 human refinement**.
- Current educator release state: **`REOPEN_REQUIRED`**.
- The raw post-repair high-recall scanner may still report candidates because it intentionally flags valid `grammar_choice` items and semantic uses of words such as *rôle*; candidate count is not an unresolved-defect count. Use the adjudication/v2 artifacts for this defect class.
- Do not restore historical approval merely because known defects were fixed.

Next French certification work:

1. bind fresh hashes for **all six French levels** after the final repairs;
2. rerun deterministic Gate A and substantively resolve remaining evidence failures;
3. run a fresh 100% learner-facing linguistic + naturalness + answer-grounding + educator review across A1–C2, independent of the repairer’s own judgments;
4. search for other templated/generic Q/A, production/meta leakage, duplicated assessment roles, and target-sense mismatches beyond the repaired classes;
5. LanguageTool French, Antidote, and DeepL Write disagreement passes;
6. three genuinely independent model-family audits;
7. 100% native professional French review;
8. 100% independent FLE/CEFR educator review;
9. adjudicate/repair all accepted findings and rerun regressions;
10. complete blind post-repair human review over 100% of learner-facing content;
11. create a new hash-bound release manifest only with zero unresolved findings.

## 6. Urdu current generation frontier

Urdu remains the active generation language.

Confirmed canonical state at this handoff write:

- A1 sequences 1–30 canonical;
- 30 passages / 300 questions / 300 answers;
- Units 01–05 canonical;
- Unit 06 sequences 31–36 staged but not confirmed canonical at this handoff write;
- Unit 07 sequences 37–42 staged and must remain non-canonical until Unit 06 promotion is verified;
- source lexicon remains read-only.

Exact generation continuation:

1. verify live main for Unit 06 result and sequences 31–36;
2. if absent, retrigger the existing guarded promotion without weakening guards or merging trigger-only PRs;
3. once Unit 06 is canonical, bind the new blob and promote Unit 07;
4. continue Unit 08 after strict sequence order is restored;
5. continue A1 to sequence 60 before normal level-level final audit unless a severe defect requires immediate repair.

Never count staging as canonical.

## 7. Non-negotiables

Generation:

- canonical data is JSONL;
- exactly 10 questions + 10 linked answers per passage unless policy explicitly changes;
- A1/A2 grammar/form assessment is operational by default, not formal grammatical-label recall;
- avoid duplicate assessment roles within a passage;
- validated source lexicons remain read-only;
- source rank/ID/form/sense identity must be verifiable;
- deliberate review scheduling and checkpoint zero-new rules must survive repairs;
- fail closed on hash/source drift, IDs/sequences, collisions, exposure/review failures, schema/linkage failures, or learner-facing contamination;
- repair content/metadata rather than weakening valid guards;
- verify live main before canonical writes and serialize writers to the same artifact.

Independent review:

- primary linguistic/Q&A/educator review covers 100% of learner-facing content;
- model/tool outputs are detectors, not sole authorities;
- a generator/repairer cannot be the sole approver of its own work;
- repeated runs of one model do not count as independent model families;
- log exact defect, location, severity, repair, adjudication, and recheck evidence;
- highest-assurance release requires zero unresolved critical/major/minor/disagreement items;
- final blind human review covers 100% for this project;
- any canonical edit invalidates affected release hashes.

## 8. Handoff hygiene

At durable session boundaries:

1. verify live canonical counts/hashes;
2. update `STATUS.json` only for verified generation state;
3. update `RELEASE_STATUS.json` only from actual release evidence;
4. keep **one current frontier** in this handoff rather than append-only history;
5. update `VERIFICATION_TASKS.md` for release/correctness work and `TASKS.md` for generation work;
6. store detailed history in audit artifacts/git history;
7. remove temporary repair workflows/triggers after use;
8. preserve pre-repair and post-repair audit artifacts separately rather than overwriting history;
9. never leave contradictory `IMMEDIATE NEXT` sections.

## 9. Stop / fail-closed conditions

Stop rather than guess when:

- live canonical state disagrees with release/generation records;
- required audit evidence is absent;
- a claimed release hash does not match canonical content;
- vocabulary source identity cannot be verified;
- a reviewer disagreement remains unresolved;
- external/human review coverage is incomplete;
- required independent reviewer/model families are unavailable;
- the only evidence for correctness is an older PASS/SEALED label.

Record the blocker and the exact next verification action.
