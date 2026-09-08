# French confirmed-correction revision plan — 2026-09-08

This note records the exact source-locked remediation path for the two high-confidence French defects identified in the post-audit strongest-flag review. It does **not** alter the current v1.0 production candidate.

## Boundary

- Current reviewer/candidate binding remains the existing v1.0 production candidate.
- No row ledger, learner source CSV, generated CSV, PDF, release manifest, or reviewer package is changed by this note.
- Applying these corrections is a material candidate revision and must follow the project's existing fail-closed defect/rebuild loop.

## Confirmed correction 1 — French vocabulary rank 837

Current published candidate row:

```text
837,bosser,to work (informal); emboss/dent,verb
```

Exact candidate source evidence:
- `completed/languages/workbooks/v1.0/french/french_vocabulary_1000.csv`, rank 837.

Current audited vocabulary ledger record:
- `audit/language-workbooks/v1.0/row_by_row_vocab/french_0801_0850.csv`
- rank 837 currently has status `PASS` with no proposal.

Problem:
- `bosser` is valid in modern informal French for `to work`.
- The candidate's additional physical gloss `emboss/dent` is not an ordinary supported sense of this verb; the bump/dent/emboss family is represented by verbs such as `bosseler`/`bossuer`.

Proposed future ledger repair:

```csv
837,REPAIR,"Post-audit reference check: modern informal bosser = to work; the candidate's emboss/dent gloss belongs to bosseler/bossuer and is misleading for a learner.",bosser,"to work (informal)",verb
```

The repair script's vocabulary path is source-locked: it reads the audited vocabulary ledgers, verifies baseline/incremental source blobs, applies only declared REPAIR rows, and fails on unexpected duplicate/homograph drift.

## Confirmed correction 2 — French sentence rank 599

Current published candidate row:

```text
599,B,"Aide-moi avec mon devoir, s’il te plaît.","Help me with my homework, please.",...
```

Exact candidate source evidence:
- `completed/languages/workbooks/v1.0/french/french_sentence_bank_1000.csv`, rank 599.

Current audited sentence ledger record:
- `audit/language-workbooks/v1.0/row_by_row/french_0551_0600.csv`
- rank 599 currently has status `PASS` with no proposal.

Problem:
- The OQLF identifies French `aider quelqu’un avec quelque chose`, patterned on English `help somebody with`, as a syntactic calque.
- Standard learner-facing French uses constructions such as `aider quelqu’un à faire ses devoirs`.

Proposed future ledger repair:

```csv
599,REPAIR,"Post-audit reference check: aider quelqu'un avec quelque chose is an English syntactic calque; use standard aider quelqu'un à faire ses devoirs.","Aide-moi à faire mes devoirs, s’il te plaît.","Help me with my homework, please."
```

The English translation can remain unchanged. The repair script will recompute sentence word count/band if necessary and append the established editorial-correction attribution marker rather than erasing source attribution.

## Required revision sequence

When a deliberate new-candidate revision is authorized, use the existing project controls rather than editing published CSV/PDF output directly:

1. Change only the two exact audited ledger records above from `PASS` to `REPAIR`, with explicit proposed values.
2. Run `scripts/apply_language_workbook_linguistic_repairs.py` in dry-run mode first.
3. Require all source guards, ledger coverage, duplicate/uniqueness, and drift gates to pass.
4. Apply the repairs through the same script only after the dry-run is clean.
5. Rerun the established v1.0 quality-build sequence:
   - canonical vocabulary integrity;
   - sentence/curation integrity;
   - 6,000-row repair/adjudication checks;
   - post-repair vocabulary integrity;
   - corpus audit;
   - 42-PDF rebuild;
   - structural/render preflight;
   - final release cross-gate audit.
6. Update generated learner-facing French CSV/PDF artifacts only via the build/publish pipeline.
7. Produce new candidate hashes/bindings/manifest evidence.
8. Treat the previous French candidate/reviewer package binding as superseded for linguistic sign-off purposes.
9. Run full independent human review against the newly bound candidate as required by `FINAL_NATIVE_REVIEW_PACKET.md`.

## Why no direct patch is made now

The canonical final-review packet explicitly requires defects to be repaired through source-locked curation data, followed by workbook rebuild, automated/rendered-output gates, new artifact identifiers, invalidation of superseded sign-off bindings, and renewed human review as necessary. A direct edit to the generated French CSV or PDF would violate that defect loop.

## Current status after this planning pass

- Confirmed corrections ready for a future source-locked revision: **2**.
- Current production candidate changed: **no**.
- Existing master PDF / manifest / reviewer-package hashes changed: **no**.
- Human sign-off gate weakened or bypassed: **no**.
