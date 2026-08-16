# Reading Curriculum Task List

This is the **active operational queue**. Historical calibration/review work belongs in git history and audit artifacts; do not infer current state from old unchecked items.

## Arabic — COMPLETE / APPROVED

- [x] A1–C2: 360 passages / 3,600 questions / 3,600 linked answers.
- [x] Final Arabic review through Pass 12 = `PASS`; formal final approval = `true`.
- [x] Zero current final-approval blockers.

Do not reopen Arabic unless canonical Arabic content is deliberately changed.

## French — ACTIVE

### A1 — GENERATED / GENERATION-INTEGRITY PASS

- [x] Units 01–10 / sequences 1–60 generated.
- [x] 60 passages / 600 questions / 600 linked answers.
- [x] 100 deliberate lexical targets.
- [x] Every Unit P06 checkpoint has zero deliberately new lexical targets.
- [x] Generation-integrity artifact: `reading/audit/french_a1_generation_integrity.json` = `PASS`.
- [x] Canonical blob: `0493a2fa13e51b5997db05e91cdea4d8dc5e647b`.

### A2 — GENERATED / GENERATION-INTEGRITY PASS

- [x] Units 01–10 / sequences 1–60 generated.
- [x] 60 passages / 600 questions / 600 linked answers.
- [x] 100 unique deliberate lexical targets.
- [x] Zero A1↔A2 deliberate-target collisions by source ID or visible form.
- [x] Every Unit P06 checkpoint has zero deliberately new lexical targets.
- [x] Generation-integrity artifact: `reading/audit/french_a2_generation_integrity.json` = `PASS` with no failures.
- [x] Canonical blob: `d0a80b8866071f426019aa0ad143e1d270dba4de`.
- [x] Canonical completion commit: `b529f730e743e3a3b077750f31be31632b8b9afc`.

A2 Unit 08 targets: `étrange`, `répéter`, `appartenir`, `signe`, `plusieurs`, `compagnie`, `douter`, `test`, `but`, `parole`.

A2 Unit 09 targets: `excuse`, `surprise`, `bruit`, `fonctionner`, `moitié`, `rater`, `cerveau`, `respirer`, `chacun`, `pourtant`.

A2 Unit 10 targets: `habiter`, `milieu`, `cuisine`, `fenêtre`, `vidéo`, `caméra`, `retenir`, `image`, `proposer`, `gérer`.

A1 and A2 have not yet gone through the final language-wide multi-pass French approval audit; do not broadly regenerate them.

### B1 — NEXT / CALIBRATION UNIT

- [ ] Unit 01 / sequences 1–6: generate as one guarded calibration unit.
- [ ] Use the standard B1 220–350-word band.
- [ ] Use the B1 3–6 new lexical types per standard passage as a planning range, not a quota; keep the unit’s deliberate lexical load controlled.
- [ ] Use 10 questions + 10 linked answers per passage under the project-wide ten-question standard.
- [ ] Add multi-sentence inference, motive/reason, summary, and grammar-in-context while preserving answer support in the passage.
- [ ] Move older vocabulary across related but non-identical topics/genres rather than merely repeating A2 narrow-reading settings.
- [ ] Check every new B1 deliberate target against all deliberate French A1+A2 targets before any canonical write.
- [ ] P06 checkpoint: zero deliberately new lexical targets, high known-vocabulary emphasis, timed-reading eligible where appropriate.
- [ ] Fail closed on source blob drift, source identity, cross-level duplication, schema/linkage errors, exact deliberate-review visibility, word band, or sequence collision.

Remaining French levels after A2:

- [ ] B1: 60 passages.
- [ ] B2: 60 passages.
- [ ] C1: 60 passages.
- [ ] C2: 60 passages.

Production policy:

- generation-first; full multi-pass French audit remains deferred until the completed French A1–C2 corpus milestone;
- standard bands: B1 220–350, B2 350–550, C1 500–800, C2 700–1,200 words;
- B1 starts broader context transfer and paragraph/multi-sentence inference;
- fail closed on lexical-source drift, cross-level target duplication, canonical blob drift, schema failure, linkage failure, invisible deliberate review, reader-facing contamination, or sequence collision;
- do not mutate the validated root lexical CSV merely to simplify passage production.

## Urdu — QUEUED

- [x] A1 sequences 1–6 exist in `reading/urdu/a1/passages.jsonl`.
- [ ] A1 sequences 7–60.
- [ ] A2–C2: 60 passages each.

Keep Urdu unchanged while French is active unless explicitly reprioritized.

## Throughput rules

- Work in coherent unit/batch scopes, not passage-by-passage workflows.
- One live-state/collision check + one guarded script + one relevant validation run per batch.
- Full multi-pass audit is a final-stage operation, not a per-generation-batch tax.
- Fail closed on source drift or invariant failure, then repair the same batch rather than weakening the guard.
- Serialize writers to the same canonical/audit artifact.

## Immediate next task

**Generate French B1 Unit 01 / sequences 1–6 as the B1 calibration unit, fresh against completed A1+A2. Keep Arabic sealed.**
