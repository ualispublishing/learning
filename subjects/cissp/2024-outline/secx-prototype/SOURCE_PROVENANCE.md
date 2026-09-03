# SecX source provenance lens

The Source Provenance lens is a learner-facing projection over source mappings that already exist in released CISSP Atlas data. It does not create new semantic curriculum relationships.

## Entry points

- Header control: **Sources · 20**
- Keyboard shortcut: `S`

The source root displays the released Atlas source registry from `CISSP_META.sources`.

## Explicit mappings only

For a selected source, the lens exposes two branches:

- **Objectives** — released objectives whose `source_ids` array contains the exact source ID.
- **Review cards** — Atlas-compatible review cards whose `source_ids` array contains the exact source ID.

The review-card registry is the same 140-card production-compatible set used by learner state: generated `OBJ-<objective-id>` cards plus released high-yield, AI, and precision cards.

No source membership is inferred from wording, topic similarity, shared labels, embeddings, or file proximity.

## Co-citation boundary

Two items citing the same source are **not** automatically related to one another.

Co-citation must not create or imply:

- `depends-on`
- `contrasts-with`
- `implemented-by`
- `mitigates`
- `measured-by`
- another cross-item semantic edge

The source lens shows provenance only. Future semantic relationships remain subject to the separate reviewer-only `RELATIONSHIP_REVIEW.json` gate.

## Scope notes

Atlas source-role metadata remains authoritative. A source may support only part of a broader CISSP decision rule, and a citation does not mean that source is the sole authority unless Atlas explicitly says so.

The lens displays source title, role, and URL already present in Atlas metadata. It does not edit source records.

## State isolation

Source Provenance does not read or write:

- `cissp_atlas_progress_v1`
- `cissp_secx_graph_state_v1`
- scenario answer/reveal state

Source navigation therefore cannot change mastery, review stage, due dates, or scenario evidence.

## Release isolation

The source lens does not discover question-bank files and does not read unreleased candidates. Its current item branches are objectives and review cards backed by data already loaded into Atlas/SecX.

## Validation

`source-audit.py` deterministically checks:

- Atlas source count against `meta.source_count`;
- source titles and role metadata;
- every objective/review-card source reference against the source registry;
- exact `source_ids.includes(...)` membership logic;
- absence of learner-state, question-bank discovery, and similarity logic;
- dependency load order after the study runtime;
- browser-smoke coverage.

`source-browser-smoke.html` + `source-browser-smoke.sh` exercise:

- the source-count control;
- `S` routing;
- all released source nodes;
- `ISC2_OUTLINE` routing;
- its explicit Objective branch;
- objective `1.1` provenance detail;
- Escape hierarchy;
- the 390px mobile shell.

As with the rest of the prototype, a browser PASS counts only when the committed gate actually executes against the exact candidate head.
