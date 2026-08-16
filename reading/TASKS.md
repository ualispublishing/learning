# Reading Curriculum Task List

This is the **active operational queue**. Historical calibration work is preserved in git history and audit artifacts; do not use old unchecked calibration items to infer current state.

Current-state precedence is defined in `reading/planning/FINAL_REVIEW_EXECUTION_PROTOCOL.md`.

## Arabic — generation

- [x] A1: 60 canonical passages / 600 questions / 600 answers.
- [x] A2: 60 canonical passages / 600 questions / 600 answers.
- [x] B1: 60 canonical passages / 600 questions / 600 answers.
- [x] B2: 60 canonical passages / 600 questions / 600 answers.
- [x] C1: 60 canonical passages / 600 questions / 600 answers.
- [x] C2: 60 canonical passages / 600 questions / 600 answers.
- [x] Arabic A1–C2 generation complete: 360 passages / 3,600 questions / 3,600 answers.

Do not restart Arabic generation or early calibration units.

## Arabic — final review completed

- [x] Pass 01 data/integrity gate recorded clean before current final refresh.
- [x] Pass 02 lexical exposure/integrity gate recorded clean before current final refresh.
- [x] Pass 05 script/orthography hygiene recorded clean before current final refresh.
- [x] Pass 06 lexical source identity recorded clean before current final refresh.
- [x] Pass 07 CEFR/length diagnostic: `PASS`, 0 actionable flags; all 360 passages inside standard production bands.
- [x] Pass 08 continuity/duplicate/balance gate recorded clean before current final refresh.
- [x] Pass 09 fluency/checkpoint gate recorded clean before current final refresh.
- [x] Pass 10 source adjudication closed as `PASS_WITH_SOURCE_ADJUDICATION` before current final refresh.
- [x] Pass 11 manual naturalness review: `COMPLETE`, 360/360 passages reviewed.
- [x] Re-read all 66 A1/A2 passages whose prose changed after their original Pass 11 review.

### Coverage note

- [x] Correct Pass 07 so unmeasured `estimated_known_token_coverage = 0` placeholders are not treated as measured 0% failures.
- [ ] Implement a defensible actual known-token coverage measurement only when the curriculum-known/morphology method is proven. Do not fabricate percentages merely to close a gate.

## Arabic — current closing queue

### Pass 03 — question composition

- [x] Correct the role classifier so genuine overlapping discourse/grammar and lexical-contrast roles are counted only when semantics/metadata support them.
- [x] Repair C1/C2 synthesis distribution using existing central-summary tasks rather than inventing unrelated questions.
- [x] Repair 81 A1/A2 grammar-deficient passages with guarded redundant-question repurposing.
- [x] Preserve independent lexical assessment for every target whose redundant definition item was repurposed.
- [ ] Resolve the final **8 A2 lexical-composition flags** using already scheduled review vocabulary only.
- [ ] Rerun Pass 03 and require `PASS` before final approval.

### Pass 04 — answer/evidence alignment

- [x] Regenerate Pass 04 against current canonical data after question remediation.
- [ ] Audit the 52 current diagnostic flags by code before changing content.
- [ ] Exclude/resolve classifier false positives such as repeated grammatical-category answers where duplication is pedagogically expected.
- [ ] Exclude grammar/category answers from inappropriate direct-text surface-overlap assumptions where the question is not a literal-evidence task.
- [ ] Review remaining direct-answer/contrast flags manually and repair only genuine answer/evidence defects.
- [ ] Rerun Pass 04 and require no unresolved substantive defects before final approval.

### Pass 12 — final adversarial gate

- [ ] Repair Pass 12 so Pass 04 is a required upstream gate.
- [ ] Accept Pass 11 `COMPLETE` as the documented completion state.
- [ ] Remove hard-coded obsolete blocker explanations; derive blockers from fresh upstream artifacts.
- [ ] Regenerate all final audit artifacts sequentially from current canonical data.
- [ ] Run Pass 12 last.
- [ ] Set Arabic final approval only if fresh Pass 12 returns `PASS` with no hard regressions or blockers.

## Final refresh discipline

At the final approval attempt:

- [ ] verify live `main` and 360 unique Arabic passage IDs;
- [ ] regenerate Passes 01–11 sequentially as applicable from current canonical data;
- [ ] avoid simultaneous workflows that push the same audit artifacts;
- [ ] run Pass 12 after all upstream artifacts are fresh;
- [ ] synchronize `reading/STATUS.json` and `reading/AGENT_HANDOFF.md` with the result.

## French / Urdu

French and Urdu are intentionally paused while Arabic final review closes.

After Arabic final approval:

- [ ] re-read `STATUS.json`, handoff, roadmap, standards, and current source/lexical audit evidence;
- [ ] determine each language's true canonical generation state from repo data rather than old checklist assumptions;
- [ ] continue generation/review under the generation-first/final-audit policy;
- [ ] do not copy Arabic passages by translation; preserve language-specific naturalness and independent curriculum design;
- [ ] apply the same final-review execution protocol once each generated corpus reaches its final audit phase.

## Reader integration / telemetry

After the language corpus work reaches an appropriate stable state:

- [ ] confirm the reader import contract;
- [ ] keep JSONL canonical regardless of export format;
- [ ] create adapters as required;
- [ ] preserve rendering order: passage → all questions → answers/reveal;
- [ ] integrate timing/comprehension telemetry if available;
- [ ] never count speed gains when comprehension is below the project gate.

## Immediate next task

**Resolve the eight remaining A2 Pass 03 lexical-composition cases as one guarded batch, then adjudicate Pass 04's 52 diagnostics before making any answer/evidence edits.**
