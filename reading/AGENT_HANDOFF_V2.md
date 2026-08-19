# Agent Handoff V2 — Graded Reading Curriculum

**Authoritative current handoff.** This file replaces `reading/AGENT_HANDOFF.md` for current execution. The legacy handoff is historical context only and contains stale frontier sections that must not drive work.

Updated: 2026-08-19

## 1. Mandatory read order

Before doing graded-reading work, read in this order:

1. live canonical `reading/<language>/<level>/passages.jsonl` relevant to the task;
2. `reading/RELEASE_STATUS.json` if the request involves correctness, approval, teacher/educator use, publication, or release;
3. `reading/STATUS.json` for generation/progression state;
4. this file;
5. `reading/planning/EDUCATOR_RELEASE_VERIFICATION_PROTOCOL.md` for correctness/release work;
6. `reading/planning/HIGHEST_ASSURANCE_RELEASE_PROFILE.md` when the user asks for maximum practical correctness/teacher-ready confidence;
7. `reading/planning/GENERATION_FIRST_FINAL_AUDIT_POLICY.md`;
8. `reading/planning/TEN_QUESTION_STANDARD.md`;
9. `reading/schema/passage.schema.json`;
10. `docs/READING_PASSAGE_STANDARD.md` and `docs/READING_PASSAGE_RESEARCH.md`;
11. `reading/ROADMAP.md` and `reading/TASKS.md` when needed.

### State precedence

For generation/progression:

`live canonical JSONL > fresh audit artifacts > STATUS > this handoff > current policies/schema > durable standards > historical artifacts`

For educator/publication release:

`live canonical JSONL > RELEASE_STATUS > hash-bound verification manifests > highest-assurance profile + educator protocol > this handoff > fresh deterministic audits > STATUS (generation state only) > legacy handoff/history`

Never infer completion from chat memory.

## 2. Critical correctness rule

`APPROVED`, `SEALED`, `PASS`, and `FINAL_APPROVED` in historical status/audit files mean that the corpus passed the workflow that existed at that time. They do **not** independently prove educator-ready correctness.

No agent may claim:

- literal `100% guaranteed correct`;
- `error-free`;
- `teacher-ready` or `educator-ready` solely from internal audit status.

The strongest permitted claim after the new protocol is:

> full corpus independently re-audited; no known defects remain under the recorded protocol.

For this project, Arabic/French educator re-certification targets the **highest-assurance profile**, including a complete blind second human review over 100% of learner-facing content rather than a sample-only final gate.

A teacher/publication release requires `HASH_BOUND_RELEASED` in `reading/RELEASE_STATUS.json` and a matching release manifest.

## 2A. Latest independent educator recertification attempt — BLOCKED

A fresh independent run on 2026-08-19 did **not** inherit historical PASS/SEALED verdicts. It bound fresh SHA-256 hashes for all Arabic/French A1–C2 canonical files and deterministically scanned all **720 passages / 7,200 questions / 7,200 answers**.

Evidence:

- `reading/audit/independent_educator_deterministic_2026-08-19.json`
- `reading/audit/independent_educator_deterministic_2026-08-19.summary.json`
- `reading/audit/independent_educator_recertification_2026-08-19.json`

Result: **deterministic Gate A = FAIL; educator recertification = BLOCKED.** The scan recorded 4,310 open release-evidence findings: 720 canonical records with `quality.status != approved`, 720 coverage checks not pass, 720 missing/zero known-token coverage values, 714 pending linguistic reviews, 714 pending pedagogical reviews, 714 pending answer-key checks, and 8 Unicode NFC findings.

These counts do **not** establish 4,310 separate prose mistakes. They establish that the live canonical per-record evidence is not sufficient to support educator certification. The draft/pending fields may be stale, but agents must not bulk-flip them to PASS. Each failed field must be backed by substantive revalidation.

Exact next certification action: resolve/revalidate Gate A across the full corpus without weakening guards, rerun the deterministic audit to PASS against bound hashes, then perform/record the fresh 100% learner-facing linguistic/Q&A/educator review and the remaining independent external/native/human gates. Until then Arabic and French remain `INTERNAL_LANGUAGE_PASS`, not educator-ready.

## 3. Arabic current state

- Generation: complete, A1–C2.
- Canonical: 360 passages / 3,600 questions / 3,600 answers.
- Historical internal final audit: PASS through the prior final protocol.
- Fresh educator recertification: **BLOCKED at deterministic Gate A**.
- **Educator release state: `INTERNAL_LANGUAGE_PASS`; external/native/educator re-certification required.**
- Do not regenerate broadly unless the new verification protocol identifies a concrete defect class requiring repair.
- Do not change draft/pending quality metadata merely to make Gate A pass; substantively revalidate first.

### Arabic verification next actions

1. resolve/revalidate the full deterministic Gate A findings and rerun to PASS;
2. fresh 100% linguistic + Q/A audit;
3. LanguageTool Arabic disagreement scan;
4. CAMeL Tools MSA morphology diagnostics;
5. three independent model-family reviews with blinded first judgments;
6. native MSA professional review covering 100% of learner-facing content;
7. independent educator/curriculum review covering 100% of passages and Q/A;
8. complete blind post-repair human review covering 100% of learner-facing content;
9. create release manifest only with zero unresolved defects.

## 4. French current state

- Generation: complete, A1–C2.
- Canonical: 360 passages / 3,600 questions / 3,600 answers.
- Historical internal/hash-bound final audit: PASS under the previous protocol.
- Fresh educator recertification: **BLOCKED at deterministic Gate A**.
- **Educator release state: `INTERNAL_LANGUAGE_PASS`; strengthened independent re-certification required.**
- Do not treat the old hash-bound approval as sufficient for a new teacher-ready claim.
- Do not change draft/pending quality metadata merely to make Gate A pass; substantively revalidate first.

### French verification next actions

1. resolve/revalidate the full deterministic Gate A findings and rerun to PASS;
2. fresh 100% linguistic + Q/A audit;
3. LanguageTool French disagreement scan;
4. Antidote French disagreement scan;
5. DeepL Write French disagreement scan;
6. three independent model-family reviews with blinded first judgments;
7. native professional French proofreader/editor review covering 100% of learner-facing content;
8. independent educator/FLE curriculum review covering 100% of passages and Q/A;
9. complete blind post-repair human review covering 100% of learner-facing content;
10. create release manifest only with zero unresolved defects.

## 5. Urdu current generation frontier

Urdu remains the active generation language.

Confirmed canonical state at this handoff write:

- A1 sequences 1–30 canonical;
- 30 passages / 300 questions / 300 answers;
- Units 01–05 canonical;
- Unit 06 sequences 31–36 are staged but **not confirmed canonical** because `reading/audit/urdu_a1_unit06_generation_result.json` is absent at this write;
- Unit 07 sequences 37–42 are staged and must remain non-canonical until Unit 06 promotion is verified;
- source lexicon remains read-only.

### Exact next action

1. Verify live main for Unit 06 result/canonical sequences 31–36.
2. If absent, run/retrigger the existing guarded Unit 06 promotion mechanism without weakening guards and without merging trigger-only PRs.
3. If Unit 06 becomes canonical, bind the new canonical blob and promote Unit 07 under the same fail-closed rules.
4. Continue Unit 08 generation after strict sequence order is restored.
5. Continue A1 to sequence 60 before the normal level-level final audit unless a severe defect requires immediate repair.

Do not count staging as canonical.

## 6. Generation non-negotiables

- canonical data is JSONL;
- exactly 10 questions and 10 linked answers per passage unless canonical policy explicitly changes;
- passage first, then all questions, then answer reveal in reader-facing rendering;
- vocabulary progression follows contextual infer → verify → transfer plus spaced review;
- validated source lexicons are read-only;
- target rank/ID/form/sense identity must be source-backed;
- frequency rank is not CEFR level;
- deliberate reviews must be visible according to current policy;
- checkpoint zero-new rules must be preserved;
- fail closed on source/hash drift, ID/sequence errors, collisions, exposure/review failures, schema/linkage failures, or learner-facing contamination;
- repair failed content/metadata rather than weakening a valid guard;
- verify live main before every canonical write;
- serialize workflows that write the same canonical artifact.

## 7. Independent-review non-negotiables

For correctness/release work:

- review **100%** of learner-facing content for the primary language/Q&A pass;
- use independent tools/models as detectors, never as sole authority;
- do not reveal earlier PASS verdicts to independent reviewers before their first judgment;
- a model that generated/repaired an item cannot be its sole approver;
- same-model repeated passes do not count as independent model families;
- log exact defect location, category, severity, correction, and resolution;
- zero unresolved critical, major, minor, or disagreement items for the highest-assurance release;
- the final blind human review is 100% coverage for this project's highest-assurance profile;
- any critical/major defect found in the final blind review reopens the defect class across the corpus;
- any canonical edit invalidates affected release hashes and triggers regression review.

## 8. Handoff hygiene

At the end of a durable work session:

1. verify canonical counts/hashes directly from live main;
2. update `reading/STATUS.json` only with verified generation state;
3. update `reading/RELEASE_STATUS.json` only when release evidence changes;
4. update this handoff with the **single current frontier**, not an append-only history;
5. update `reading/TASKS.md` or the active verification task file;
6. put detailed historical events in git history/audit artifacts, not in the current handoff;
7. remove or explicitly deprecate stale frontier instructions;
8. never leave contradictory `IMMEDIATE NEXT` sections in the authoritative handoff.

## 9. Stop conditions

Stop and fail closed rather than guessing when:

- live canonical state disagrees with status/handoff;
- a required audit artifact is absent;
- a release hash does not match canonical content;
- source vocabulary identity cannot be verified;
- a reviewer disagreement remains unresolved;
- external review coverage is incomplete;
- fewer than the required independent model families are available for a gate that requires them;
- the only evidence of correctness is an older PASS/SEALED label.

Record the blocker and the exact next verification action.
