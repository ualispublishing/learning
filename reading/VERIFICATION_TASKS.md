# LANG-A1C2 Active Verification Queue

Updated: 2026-08-30

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

Current release position: fresh deterministic revalidation is **FAIL** with **2506** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.

Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **2496**. This is a release-evidence gate, not semantic approval.

NFC repair evidence: `reading/audit/arabic_nfc_repair_2026-08-30.json`; the rerun reduced open deterministic findings from **2,506** to **2,496** with the Unicode class at zero.

Open verification work:

- [x] fresh deterministic educator-release revalidation;
- [x] close the 10 fresh deterministic Unicode NFC findings with a byte-bounded normalization-only repair;
- [ ] substantively resolve the fresh deterministic release-evidence blockers without bulk-promoting draft/pending metadata;
- [ ] corpus-wide low-level metalinguistic/CEFR question audit and repair;
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
