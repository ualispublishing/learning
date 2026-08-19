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
7. current generation policy, ten-question standard, schema, durable reading standards/research, roadmap/tasks as needed.

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

## 3. Independent recertification findings — current truth

A fresh 2026-08-19 recertification attempt bound Arabic/French A1–C2 hashes and scanned all 720 passages / 7,200 questions / 7,200 answers. Deterministic Gate A remains incomplete because much canonical record-level quality evidence is stale/pending; do not bulk-flip metadata merely to obtain PASS.

A subsequent adversarial in-chat educator review found **concrete major French canonical defects** that the historical approval workflow had missed:

- French C1 Unit 01 P01–P05 contained 20 generic vocabulary answers that did not answer the target-specific questions.
- French C1 Unit 01 P01–P06 contained learner-facing production/meta language, including an English theme label and internal progression/checkpoint wording.
- French C2 Unit 01 P01–P05 contained learner-facing `Révision C1 intégrée` production notes.

These defects were repaired on `main` through PR #6. Evidence:

- `reading/audit/french_c1_c2_educator_defect_repair_2026-08-19.json`
- `reading/audit/french_c1_u01_p06_followup_repair_2026-08-19.json`

Repair result:

- 11 affected passages repaired;
- 20 generic vocabulary answers replaced with context-specific answers;
- exact scheduled review forms preserved;
- 10-question/10-answer linkage preserved;
- full C1/C2 scan for the identified production-note/generic-answer patterns returned zero residue;
- C1 Unit 01 P06 received an additional human spot-check repair after the first machine-clean pass exposed awkward wording.

Post-repair SHA-256 evidence recorded by the repair artifacts:

- French C1: `dead8e5d6e6e60a7c6c5185996159670e6077ea2d5da31860de168674050b39a`
- French C2: `c161c4551a6ce0222850778c02ed0662e00bb60e5386d5dc0b4f31a92cb9f277`

**Important:** this repair does not re-certify French. It invalidates the old French release hashes. French is now `REOPEN_REQUIRED` until the strengthened independent gates are rerun against the repaired corpus.

## 4. Arabic current state

- Generation: complete A1–C2; 360 passages / 3,600 questions / 3,600 answers.
- Historical internal audit: PASS under the prior protocol.
- Highest-assurance educator release: **not complete**.
- Current release state remains non-release-ready; consult `reading/RELEASE_STATUS.json` for exact state.
- Known deterministic concerns include pending/stale record-level evidence and previously detected Unicode normalization findings; substantive linguistic/native review remains required.

Next Arabic certification work:

1. substantively resolve/revalidate deterministic Gate A and rerun it;
2. perform fresh 100% linguistic + Q/A review;
3. LanguageTool Arabic + CAMeL MSA diagnostics;
4. three genuinely independent model-family audits;
5. 100% native MSA professional review;
6. 100% independent educator/curriculum review;
7. repair/regression/adjudication;
8. complete blind post-repair human review;
9. issue a hash-bound release manifest only at zero unresolved defects.

## 5. French current state

- Generation: complete A1–C2; 360 passages / 3,600 questions / 3,600 answers.
- Historical internal/hash-bound audit: PASS under the previous protocol, now insufficient and hash-invalidated by canonical repairs.
- Confirmed C1/C2 defect class described above: **repaired**.
- Current educator release state: **`REOPEN_REQUIRED`**.
- Do not restore historical approval merely because the identified defects were fixed.

Next French certification work:

1. rerun deterministic Gate A against the repaired canonical hashes and substantively resolve remaining evidence failures;
2. run a fresh 100% learner-facing linguistic + answer-grounding + educator review, with explicit corpus-wide searches for templated/generic Q/A and production/meta-language leakage;
3. LanguageTool French, Antidote, and DeepL Write disagreement passes;
4. three genuinely independent model-family audits;
5. 100% native professional French review;
6. 100% independent FLE/CEFR educator review;
7. adjudicate all disagreements and repair accepted defects;
8. rerun affected deterministic/lexical/progression/Q&A checks;
9. complete blind post-repair human review over 100% of learner-facing content;
10. create a new hash-bound release manifest only with zero unresolved findings.

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
8. never leave contradictory `IMMEDIATE NEXT` sections.

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
