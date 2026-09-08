# French confirmed-correction revision plan — feasibility amendment — 2026-09-08

This amendment supersedes the **application sequencing** in `french-confirmed-correction-revision-plan-20260908.md` after checking the current fail-closed repair runner, current source blobs, the existing incremental vocabulary lock, the historical bounded repair PR, and the reviewer/sign-off binding machinery.

It does **not** alter the current v1.0 production candidate.

## Current correction set

Three high-confidence French learner-facing correction candidates are now documented.

### Vocabulary rank 608 — `situation`

Current source/candidate meaning:

```text
situation (all meanings)
```

Current ledger:
- `audit/language-workbooks/v1.0/row_by_row_vocab/french_0601_0650.csv`
- rank 608: `PASS`

Proposed future ledger record:

```csv
608,REPAIR,"Post-audit reference check: 'situation (all meanings)' overclaims one-to-one equivalence; use explicit context-bounded learner senses.",situation,"situation; circumstances; location; job (context-dependent)",noun
```

### Vocabulary rank 837 — `bosser`

Current source/candidate meaning:

```text
to work (informal); emboss/dent
```

Current ledger:
- `audit/language-workbooks/v1.0/row_by_row_vocab/french_0801_0850.csv`
- rank 837: `PASS`

Proposed future ledger record:

```csv
837,REPAIR,"Post-audit reference check: modern informal bosser = to work; the candidate's emboss/dent gloss belongs to bosseler/bossuer and is misleading for a learner.",bosser,"to work (informal)",verb
```

### Sentence rank 599 — homework sentence

Current source/candidate:

```text
Aide-moi avec mon devoir, s’il te plaît.
```

Current ledger:
- `audit/language-workbooks/v1.0/row_by_row/french_0551_0600.csv`
- rank 599: `PASS`

Proposed future ledger record:

```csv
599,REPAIR,"Post-audit reference check: aider quelqu'un avec quelque chose is an English syntactic calque; use standard aider quelqu'un à faire ses devoirs.","Aide-moi à faire mes devoirs, s’il te plaît.","Help me with my homework, please."
```

## Critical correction to the earlier sequencing

The two new **vocabulary** repairs cannot safely be applied merely by changing their ledger rows and running `scripts/apply_language_workbook_linguistic_repairs.py` against current `main`.

Current French vocabulary source:
- `french_top1000.csv`
- Git blob: `c79f8729dd5e089e0647723bfc81822bb89586a1`

Current repair report identifies that blob as the output of the previous French incremental repair round. The current incremental vocabulary manifest (`langwb-v1.0-lexical-qa-v5-2026-09-03`) instead locks the preceding French input blob `bee21fb1d123e93b4aada6b26f12d8239ac5818b` and authorizes only the old ranks:

```text
85, 137, 207, 267, 330, 351, 353, 399, 612, 644, 728, 761, 973
```

The repair runner is intentionally fail-closed:
- a genuinely new vocabulary change is accepted from an `incremental_baseline` only when its rank is explicitly in `allowed_new_repair_ranks`;
- the set actually applied must equal the locked set exactly;
- a new vocabulary difference encountered while the source is merely `prior_repaired` is rejected.

Therefore ranks **608 and 837 require a new exact incremental vocabulary repair round before application**.

## Required new vocabulary lock

For a future authorized candidate revision, prepare a new bounded incremental vocabulary round (conceptually the next lexical-QA round) with at least these properties:

- French `input_git_blob`: `c79f8729dd5e089e0647723bfc81822bb89586a1`
- French `historical_audited_baseline_git_blob`: preserve `419d96467a78c205996358caaf4ae9ba1ac3caa9`
- French `prior_repair_report_output_git_blob`: `c79f8729dd5e089e0647723bfc81822bb89586a1`
- French `allowed_new_repair_ranks`: `[608, 837]`
- French `expected_new_repair_count`: `2`
- bind the preparation to the then-current exact repository commit and exact repair-runner blob;
- recompute any ledger-patch manifest/checksum fields required by the controlled round instead of copying the prior round's values.

The current runner does not require an incremental entry for languages with no new vocabulary repair. Do not accidentally carry old non-empty rank locks forward as though those old ranks were being newly applied again.

Historical model: merged PR #138 (`repair: apply bounded LANG-WB v1.0 linguistic repairs v2`) used the same exact-input / exact-rank-lock pattern and ran the complete 6,000-row/build checks.

## Sentence rank 599 does not need a vocabulary-style rank lock

Current staged French sentence source:
- `audit/language-workbooks/v1.0/staging_v3/french_sentences.csv`
- Git blob: `b09fc4158e8e0c4c09e47ad75d1a9a9b0bea6688`

The current repair report also identifies this as the prior repaired French sentence output. The sentence planner accepts a newly declared `REPAIR` from this source state, provided the exact source guard, 1,000-row ledger coverage, target/English uniqueness, attribution, and other fail-closed checks remain satisfied.

Thus the future revision can apply sentence rank 599 through the normal sentence ledger/repair path in the same controlled repair run.

## Correct future application sequence

Only after deliberate authorization to create a new production candidate:

1. Capture the exact current repository/source state and confirm no conflicting learner-source drift.
2. Prepare the **new French incremental vocabulary baseline/lock** authorizing exactly ranks `608` and `837` against input blob `c79f8729dd5e089e0647723bfc81822bb89586a1`.
3. Change only these three audited ledger records from `PASS` to `REPAIR` with the proposed values above:
   - French vocabulary 608;
   - French vocabulary 837;
   - French sentence 599.
4. Run `scripts/apply_language_workbook_linguistic_repairs.py` **without `--write`** first.
5. Require the dry-run to show the expected new changes only:
   - French vocabulary newly applied ranks exactly `[608, 837]`;
   - French sentence rank `599` newly applied;
   - no HOLD rows;
   - 1,000 distinct normalized French vocabulary fronts;
   - no blocking vocabulary duplicate groups;
   - 1,000 unique French sentence targets and 1,000 unique English sentence strings;
   - no unexpected source drift.
6. Only after the dry-run is clean, run the same repair script with `--write`.
7. Rerun the established v1.0 quality-build sequence, including canonical vocabulary integrity, sentence/curation integrity, all 6,000 row checks, post-repair vocabulary integrity, corpus audit, 42-PDF rebuild, structural/render preflight, and final release cross-gate audit.
8. Publish generated learner-facing CSV/PDF artifacts only through the established build/publish pipeline; never patch the completed CSVs/PDFs directly.
9. Produce new candidate hashes and a new `RELEASE_MANIFEST.json` binding.
10. Refresh reviewer/sign-off materials against the new exact candidate before human certification.

## Global release-manifest binding consequence

The current human sign-off schema binds **every language sign-off** not only to that language's master workbook and sentence-decision hash but also to the Git blob of the global:

```text
completed/languages/workbooks/v1.0/RELEASE_MANIFEST.json
```

The final promotion gate independently compares that manifest blob for Arabic, French, and Urdu records. The reviewer-bundle builder likewise:

- copies the global release manifest into every language bundle;
- records its Git blob and SHA-256 in each language's `CANDIDATE_BINDING.json`;
- creates the sign-off draft from current-candidate bindings.

Consequently, a French rebuild that changes the global release manifest makes old manifest-bound reviewer/sign-off materials stale **for all three languages**, even when Arabic and Urdu master-workbook bytes and sentence-decision hashes remain unchanged.

After an authorized French revision/rebuild:

- regenerate Arabic, French, and Urdu reviewer bundles/bindings against the new manifest;
- any human sign-off carrying the superseded manifest blob cannot count as a current-candidate sign-off under the existing validator/promotion gate;
- do not reuse the currently published reviewer package bindings as current-candidate certification evidence.

At present this causes no loss of completed human certification because no Arabic/French/Urdu native sign-off JSON has been committed.

## Current candidate remains unchanged

At the time of this amendment:

- current `RELEASE_MANIFEST.json` Git blob: `edbbe8971579a1957d5c965b8b2e3b7b3ba0d180`;
- current release status: `production_candidate`;
- current learner-facing French source remains unchanged;
- the three ledger records remain `PASS`;
- the three proposed repairs have **not** been applied;
- no master PDF, companion CSV, release manifest, candidate hash, reviewer package, or sign-off binding has been invalidated by this planning work.

This amendment is QA/revision-planning evidence only. It does not authorize or perform the material candidate revision.