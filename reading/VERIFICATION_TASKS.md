# LANG-A1C2 Active Verification Queue

Updated: 2026-09-04

This is the live verification queue only. Completed audit waves and detailed evidence remain in `reading/audit/` and Git history. Release claims are controlled by `reading/RELEASE_STATUS.json`.

## Gate 0 — route / continuation / state-bundle consistency

- [x] `PROJECT_TRACKS.json` routes the session to `LANG-A1C2` and excludes the workbook roots.
- [x] `reading/STATE_MANIFEST.json` matches the exact tracked live-state bytes and aggregate SHA-256.
- [x] `python reading/tools/validate_continuation_state.py` passes against the routed state bundle and live canonical files.
- [x] Stored production totals equal canonical JSONL counts.
- [x] Active frontier in `CONTINUATION.json`, `STATUS.json`, and `ACTIVE_GENERATION_PLAN.json` agrees.
- [x] Cached release summary in `CONTINUATION.json` agrees with `RELEASE_STATUS.json`.
- [x] Pinned Urdu A1 blob still matches the canonical file before relying on its final integrity audit.
- [ ] A zero-step/skipped CI run is never treated as verification success.

Fresh Gate 0 evidence: `reading/audit/post_generation_gate0_2026-08-30.json` (exact 1,080-passage corpus; release claim false).

## Arabic — educator release blocked

Current generation: 360/360 complete.

Current release position: fresh deterministic revalidation is **FAIL** with **1104** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.

Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1104**. This is a release-evidence gate, not semantic approval.

NFC repair evidence: `reading/audit/arabic_nfc_repair_2026-08-30.json`; the rerun reduced open deterministic findings from **2,506** to **2,496** with the Unicode class at zero.

Open verification work:

Arabic A1-C2 low-level/metalinguistic closure evidence: `reading/audit/arabic_b1_c2_metalinguistic_cefr_adjudication_2026-08-30.json` — all 3,600 current Arabic questions scanned; B1-C2 initial 344 candidates adjudicated as 333 contextual retains, 9 repairs, and 2 detector false positives; post-repair manual queue 0. This does not close naturalness, semantic, educator, or independent review.

A2 metalinguistic reconciliation evidence: `reading/audit/arabic_a2_metalinguistic_repair_2026-08-30.json` — original 83-item inventory fully adjudicated as 80 confirmed repairs plus 3 documented comprehension false positives; 600 questions / 600 answers rescanned with 0 unadjudicated formal-type or configured formal-prompt findings.

A1 Units 3–10 batch evidence: `reading/audit/arabic_a1_u03_u10_metalinguistic_repair_2026-08-30.json` — 48 current-corpus repairs; combined with Units 1–2, all 63 known A1 formal-type candidates are repaired and no formal metalinguistic question type remains across the 600 A1 questions. This does not close CEFR, naturalness, or independent educator review.

A1 Unit 2 metalinguistic repair evidence: `reading/audit/arabic_a1_u02_metalinguistic_repair_2026-08-30.json` — 6 repaired questions, 0 formal metalinguistic question types remaining in Unit 2, all records outside Unit 2 byte-identical.

A1 Unit 1 metalinguistic repair evidence: `reading/audit/arabic_a1_u01_metalinguistic_repair_2026-08-30.json` — 9 repaired questions, 0 formal metalinguistic question types remaining in Unit 1, records 7–60 byte-identical.

B2 Unit 1 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u01.json` — 6 current-corpus records reviewed, all 6 repaired, with 16 fresh high-confidence grammar/naturalness/reference/assessment findings closed.

B2 Unit 2 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u02.json` — 6 current-corpus records reviewed, all 6 repaired, with 17 fresh high-confidence grammar/naturalness/reference/semantic/assessment findings closed. After this batch Gate B stood at 192/360 records; this was not an educator/publication release claim.

B2 Unit 3 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u03.json` — 6 current-corpus records reviewed, 5 repaired and 1 clean PASS, with 15 fresh high-confidence grammar/naturalness/semantic findings closed. Fresh Gate B progress is now 198/360 records; B2 remains in progress and this is not an educator/publication release claim.

B2 Unit 4 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u04.json` — 6 current-corpus records reviewed, 4 repaired and 2 clean PASS records, with 6 fresh high-confidence naturalness/assessment/semantic/reference findings closed. Fresh Gate B progress is now 204/360 records; B2 remains in progress and this is not an educator/publication release claim.

B2 Unit 5 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u05.json` — 6 current-corpus records reviewed, 4 repaired and 2 clean PASS records, with 12 fresh high-confidence grammar/naturalness/reference/semantic/assessment findings closed. Fresh Gate B progress is now 210/360 records; B2 remains in progress and this is not an educator/publication release claim.

B2 Unit 6 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u06.json` — 6 current-corpus records reviewed, 5 repaired and 1 clean PASS record, with 16 fresh high-confidence grammar/naturalness/reference/semantic/assessment findings closed. Fresh Gate B progress is now 216/360 records; B2 remains in progress and this is not an educator/publication release claim.

B2 Unit 7 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u07.json` — 6 current-corpus records reviewed, 3 repaired and 3 clean PASS records, with 5 fresh high-confidence grammar/naturalness/reference/assessment findings closed. Fresh Gate B progress is now 222/360 records; B2 remains in progress and this is not an educator/publication release claim.

B2 Unit 8 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u08.json` — 6 current-corpus records reviewed, 3 repaired and 3 clean PASS records, with 3 fresh high-confidence naturalness/grammar findings closed. Fresh Gate B progress is now 228/360 records; B2 remains in progress and this is not an educator/publication release claim.

B2 Unit 9 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u09.json` — 6 current-corpus records reviewed, 5 repaired and 1 clean PASS record, with 14 fresh high-confidence grammar/naturalness/semantic/assessment findings closed. Fresh Gate B progress is now 234/360 records; B2 remains in progress and this is not an educator/publication release claim.

B2 Unit 10 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u10.json` — 6 current-corpus records reviewed, 5 repaired and 1 clean PASS record, with 12 fresh high-confidence grammar/naturalness/semantic/reference findings closed. Fresh Gate B progress is now 240/360 records; B2 Gate B is complete, the next ordered frontier is C1 Unit 1, and this is not an educator/publication release claim.

C1 Unit 1 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c1_u01.json` — 6 current-corpus records reviewed, 5 repaired and 1 clean PASS record, with 10 fresh high-confidence grammar/naturalness/reference/semantic/assessment findings closed. Fresh Gate B progress is now 246/360 records; C1 is in progress and this is not an educator/publication release claim.

C1 Unit 2 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c1_u02.json` — 6 current-corpus records reviewed and repaired, with 8 fresh high-confidence grammar/naturalness/semantic findings closed. Fresh Gate B progress is now 252/360 records; C1 remains in progress and this is not an educator/publication release claim.

C1 Unit 3 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c1_u03.json` — 6 current-corpus records reviewed and repaired, with 10 fresh high-confidence grammar/naturalness/semantic findings closed. Fresh Gate B progress is now 258/360 records; C1 remains in progress and this is not an educator/publication release claim.

C1 Unit 4 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c1_u04.json` — 6 current-corpus records reviewed, 4 repaired and 2 clean PASS records, with 6 fresh high-confidence grammar/reference/semantic/assessment findings closed. Fresh Gate B progress is now 264/360 records; C1 remains in progress and this is not an educator/publication release claim.

C1 Unit 5 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c1_u05.json` — 6 current-corpus records reviewed, 3 repaired and 3 clean PASS records, with 5 fresh high-confidence grammar/naturalness/semantic findings closed. Fresh Gate B progress is now 270/360 records; C1 remains in progress and this is not an educator/publication release claim.

C1 Unit 6 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c1_u06.json` — 6 current-corpus records reviewed, 5 repaired and 1 clean PASS record, with 5 fresh high-confidence grammar/assessment findings closed. Fresh Gate B progress is now 276/360 records; C1 remains in progress and this is not an educator/publication release claim.

C1 Unit 7 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c1_u07.json` — 6 current-corpus records reviewed and repaired, with 6 fresh high-confidence assessment-alignment findings closed. Fresh Gate B progress is now 282/360 records; C1 remains in progress and this is not an educator/publication release claim.

C1 Unit 8 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c1_u08.json` — 6 current-corpus records reviewed and repaired, with 6 fresh high-confidence summary-answer assessment-alignment findings closed. Fresh Gate B progress is now 288/360 records; C1 remains in progress and this is not an educator/publication release claim.

C1 Unit 9 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c1_u09.json` — 6 current-corpus records reviewed and repaired, with 7 fresh high-confidence assessment-alignment and semantic findings closed. Fresh Gate B progress is now 294/360 records; C1 remains in progress and this is not an educator/publication release claim.

C1 Unit 10 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c1_u10.json` — 6 current-corpus records reviewed and repaired, with 6 fresh high-confidence assessment-alignment/naturalness findings closed. Fresh Gate B progress is now 300/360 records; C1 Gate B is complete, the next ordered frontier is C2 Unit 1, and this is not an educator/publication release claim.

C2 Unit 1 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c2_u01.json` — 6 current-corpus records reviewed and repaired, with 6 fresh high-confidence assessment-alignment/naturalness findings closed. Fresh Gate B progress is now 306/360 records; C2 remains in progress and this is not an educator/publication release claim.

C2 Unit 2 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c2_u02.json` — 6 current-corpus records reviewed and repaired, with 6 fresh high-confidence summary-answer assessment-alignment findings closed. Fresh Gate B progress is now 312/360 records; C2 remains in progress and this is not an educator/publication release claim.

C2 Unit 3 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c2_u03.json` — 6 current-corpus records reviewed, 4 repaired and 2 clean PASS records, with 4 fresh high-confidence summary-answer assessment/reference findings closed. Fresh Gate B progress is now 318/360 records; C2 remains in progress and this is not an educator/publication release claim.

C2 Unit 4 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c2_u04.json` — 6 current-corpus records reviewed and repaired, with 8 fresh high-confidence summary-answer assessment/naturalness/semantic findings closed. Fresh Gate B progress is now 324/360 records; C2 remains in progress and this is not an educator/publication release claim.

C2 Unit 5 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c2_u05.json` — 6 current-corpus records reviewed, 5 repaired and 1 clean PASS record, with 5 fresh high-confidence summary-answer assessment-alignment findings closed. Fresh Gate B progress is now 330/360 records; C2 remains in progress and this is not an educator/publication release claim.

C2 Unit 6 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c2_u06.json` — 6 current-corpus records reviewed and repaired, with 8 fresh high-confidence summary-answer assessment-alignment/naturalness findings closed. Fresh Gate B progress is now 336/360 records; C2 remains in progress and this is not an educator/publication release claim.

C2 Unit 7 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c2_u07.json` — 6 current-corpus records reviewed, 4 repaired and 2 clean PASS records, with 4 fresh high-confidence summary-answer assessment-alignment findings closed. Fresh Gate B progress is now 342/360 records; C2 remains in progress and this is not an educator/publication release claim.

C2 Unit 8 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c2_u08.json` — 6 current-corpus records reviewed and repaired, with 6 fresh high-confidence summary-answer assessment-alignment findings closed. Fresh Gate B progress is now 348/360 records; C2 remains in progress and this is not an educator/publication release claim.

C2 Unit 9 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c2_u09.json` — 6 current-corpus records reviewed and repaired, with 12 fresh high-confidence summary-answer assessment-alignment/naturalness findings closed. Fresh Gate B progress is now 354/360 records; C2 remains in progress and this is not an educator/publication release claim.

- [x] fresh deterministic educator-release revalidation;
- [x] close the 10 fresh deterministic Unicode NFC findings with a byte-bounded normalization-only repair;
- [ ] substantively resolve the fresh deterministic release-evidence blockers without bulk-promoting draft/pending metadata;
- [ ] corpus-wide low-level metalinguistic/CEFR question audit and repair;
- [x] Arabic A2 historical inventory: adjudicated all 83 candidates as 80 confirmed repairs plus 3 documented comprehension false positives; 600 questions / 600 answers rescanned with no unadjudicated formal-item findings;
- [x] Arabic A1 Units 3-10 batch: re-adjudicated and repaired the remaining 48 formal-label items; combined A1 total is 63 repairs and 0 formal question types across 600 questions;
- [x] Arabic A1 Unit 2 sub-batch: re-adjudicated and replaced 6 formal-label items with operational A1 use/form tasks;
- [x] Arabic A1 Unit 1 sub-batch: reviewed 6 passages / 60 questions and replaced 9 formal-label items with A1 reading/use tasks;
- [x] Arabic B2 Unit 1 Gate B batch: reviewed 6 passages / 60 questions / 60 answers and closed 16 fresh learner-facing findings with hash-bound decision evidence;
- [x] Arabic B2 Unit 2 Gate B batch: reviewed 6 passages / 60 questions / 60 answers and closed 17 fresh learner-facing findings with hash-bound decision evidence;
- [x] Arabic B2 Unit 3 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 15 fresh learner-facing findings across 5 records and recorded 1 clean PASS with hash-bound decision evidence;
- [x] Arabic B2 Unit 4 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 6 fresh learner-facing findings across 4 records and recorded 2 clean PASS records with hash-bound decision evidence;
- [x] Arabic B2 Unit 5 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 12 fresh learner-facing findings across 4 records and recorded 2 clean PASS records with hash-bound decision evidence;
- [x] Arabic B2 Unit 6 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 16 fresh learner-facing findings across 5 records and recorded 1 clean PASS with hash-bound decision evidence;
- [x] Arabic B2 Unit 7 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 5 fresh learner-facing findings across 3 records and recorded 3 clean PASS records with hash-bound decision evidence;
- [x] Arabic B2 Unit 8 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 3 fresh learner-facing findings across 3 records and recorded 3 clean PASS records with hash-bound decision evidence;
- [x] Arabic B2 Unit 9 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 14 fresh learner-facing findings across 5 records and recorded 1 clean PASS with hash-bound decision evidence;
- [x] Arabic B2 Unit 10 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 12 fresh learner-facing findings across 5 records and recorded 1 clean PASS with hash-bound decision evidence; B2 Gate B is complete and C1 Unit 1 is next;
- [x] Arabic C1 Unit 1 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 10 fresh learner-facing findings across 5 records and recorded 1 clean PASS with hash-bound decision evidence;
- [x] Arabic C1 Unit 2 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 8 fresh learner-facing findings across all 6 records with hash-bound decision evidence;
- [x] Arabic C1 Unit 3 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 10 fresh learner-facing findings across all 6 records with hash-bound decision evidence;
- [x] Arabic C1 Unit 4 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 6 fresh learner-facing findings across 4 records and recorded 2 clean PASS records with hash-bound decision evidence;
- [x] Arabic C1 Unit 5 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 5 fresh learner-facing findings across 3 records and recorded 3 clean PASS records with hash-bound decision evidence;
- [x] Arabic C1 Unit 6 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 5 fresh learner-facing findings across 5 records and recorded 1 clean PASS with hash-bound decision evidence;
- [x] Arabic C1 Unit 7 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 6 fresh summary-answer alignment findings across all 6 records with hash-bound decision evidence;
- [x] Arabic C1 Unit 8 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 6 fresh summary-answer alignment findings across all 6 records with hash-bound decision evidence;
- [x] Arabic C1 Unit 9 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 7 fresh findings across all 6 records with hash-bound decision evidence;
- [x] Arabic C1 Unit 10 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 6 fresh findings across all 6 records with hash-bound decision evidence; C1 Gate B is complete and C2 Unit 1 is next;
- [x] Arabic C2 Unit 1 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 6 fresh findings across all 6 records with hash-bound decision evidence;
- [x] Arabic C2 Unit 2 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 6 fresh summary-answer alignment findings across all 6 records with hash-bound decision evidence;
- [x] Arabic C2 Unit 3 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 4 fresh summary-answer assessment/reference findings across 4 records and recorded 2 clean PASS records with hash-bound decision evidence;
- [x] Arabic C2 Unit 4 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 8 fresh summary-answer assessment/naturalness/semantic findings across all 6 records with hash-bound decision evidence;
- [x] Arabic C2 Unit 5 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 5 fresh summary-answer assessment-alignment findings across 5 records and recorded 1 clean PASS record with hash-bound decision evidence;
- [x] Arabic C2 Unit 6 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 8 fresh summary-answer assessment-alignment/naturalness findings across all 6 records with hash-bound decision evidence;
- [x] Arabic C2 Unit 7 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 4 fresh summary-answer assessment-alignment findings across 4 records and recorded 2 clean PASS records with hash-bound decision evidence;
- [x] Arabic C2 Unit 8 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 6 fresh summary-answer assessment-alignment findings across all 6 records with hash-bound decision evidence;
- [x] Arabic C2 Unit 9 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 12 fresh summary-answer assessment-alignment/naturalness findings across all 6 records with hash-bound decision evidence;
- [ ] corpus-wide Arabic grammar-in-context naturalness audit;
- [ ] full passage language/question/answer semantic review;
- [ ] independent professional/native and model-family disagreement passes;
- [ ] educator curriculum review;
- [ ] blind post-repair human review;
- [ ] final hash-bound release manifest only after all required gates are clean.

Primary current evidence pointers are maintained in `reading/RELEASE_STATUS.json`.

## French — `REOPEN_REQUIRED`

Current generation: 360/360 complete.

Latest post-repair deterministic Gate A:

- status: **FAIL**;
- records: 360;
- questions: 3,600;
- answers: 3,600;
- open release-evidence findings: **2,160**.

Open verification work:

- [ ] substantively revalidate record-level coverage, linguistic, pedagogical, answer-key, and approval evidence;
- [ ] never bulk-promote pending metadata merely to make Gate A pass;
- [ ] rerun post-revalidation Gate A from the current canonical hashes;
- [ ] complete fresh full semantic language/question/answer review;
- [ ] complete independent professional/native/tool/model-family disagreement passes;
- [ ] complete educator and blind post-repair human review;
- [ ] create a hash-bound release manifest only after all required gates pass.

Evidence: `reading/audit/french_postrepair_deterministic_gate_a_2026-08-19.json`.

## Urdu A1 — integrity clean, quality not promoted

Canonical A1:

- path: `reading/urdu/a1/passages.jsonl`;
- passages: 60;
- pinned Git blob: `ec0970dc1916ce523dd3320d2f4dca4c7f8bc677`.

Final integrity evidence: `reading/audit/urdu_a1_final_integrity_2026-08-23.json`.

Recorded integrity result:

- 60 passages;
- 600 questions;
- 600 answers;
- 130 cloze questions reconstruct;
- 0 hard errors;
- 0 warnings;
- `quality_promotion: false`.

Therefore:

- [x] exact-corpus deterministic/integrity audit closed for the pinned blob;
- [ ] semantic naturalness/idiomaticity review;
- [ ] pedagogy and CEFR calibration review;
- [ ] question/answer/evidence quality review;
- [ ] lexical exposure/coverage review where required;
- [ ] independent/native/educator review at the designated assurance milestone;
- [ ] release decision only after applicable release gates are satisfied.

Do not reopen deterministic repair work simply because quality review remains pending. Conversely, do not call A1 educator-ready merely because integrity is green.

## Freshness and invalidation rules

- Any audit is evidence only for the canonical bytes/fields it examined.
- Any tracked live-state edit invalidates `STATE_MANIFEST.json` until it is refreshed.
- Passage-prose edits invalidate affected language/naturalness, word-band/CEFR, and evidence-alignment checks.
- Question/answer edits invalidate the affected question/evidence/answer-key gates.
- Target/exposure edits invalidate lexical/source/exposure gates.
- Schema/ID/order edits invalidate data-integrity gates.
- Final release attempts must regenerate the required final evidence sequentially from the current canonical state.
- Tooling/environment failures are blockers, not content defects; record them separately.

## Completion rule

No language is educator/publication ready until `reading/RELEASE_STATUS.json` records readiness from fresh hash-bound evidence. Generation completion by itself is never sufficient.
