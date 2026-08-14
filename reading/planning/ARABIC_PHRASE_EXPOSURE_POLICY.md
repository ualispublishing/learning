# Arabic Phrase Exposure Policy

## Purpose

Keep Arabic multiword expressions pedagogically distinct from the ranked 1–3000 single-word prerequisite backbone.

## Source of truth

- Canonical phrase content: `arabic_phrase_bank.csv`
- Derived exposure ledger: `reading/ledgers/arabic_phrase_exposure.jsonl`
- Derived build summary: `reading/ledgers/arabic_phrase_exposure_summary.json`

The canonical phrase bank must not be reordered merely to imply difficulty.

## Stable identifiers

Each canonical CSV row receives a derived ID of the form `ar-pNNN` based on its current canonical row position. The phrase text remains the content identity checked by the builder; duplicate fronts are a build failure.

## CEFR rule

Phrase-bank order is **not** a CEFR ranking. Every derived phrase begins with:

`cefr_eligibility: unreviewed`

A phrase may enter an A1 passage only after a separate pedagogical decision marks that exact phrase as A1-eligible. High-frequency-looking placement, short length, or familiar component words are not sufficient evidence by themselves.

## Exposure state

Phrase exposure is tracked independently from `ar-rNN` ranked-word exposure. Initial generated state does not assume learner mastery:

- `introduced_in: null`
- `meaningful_contacts: 0`
- `learner_successes: 0`
- `learner_failures: 0`
- `last_contact_passage: null`
- `next_reinforcement_stage: R0`

When a reviewed phrase is deliberately introduced in the reading curriculum, those fields may be updated from canonical passage metadata and learner evidence using the same no-fabricated-mastery principle as the ranked-word ledger.

## A1 selection principles

A1 phrase eligibility should favor expressions that are:

1. natural contemporary MSA in ordinary communication;
2. semantically transparent enough for a beginner context;
3. useful across multiple everyday situations;
4. teachable without requiring advanced discourse, legal, political, scientific, literary, or idiomatic background;
5. compatible with the passage's existing supported-coverage budget.

Expressions that are highly formal, specialized, rhetorically elaborate, rare, domain-specific, or semantically opaque should remain unreviewed or be assigned to later levels even if their individual words are common.

## Guardrail

Do not import all 665 phrases into A1. The phrase bank is a resource pool, not a beginner syllabus.
