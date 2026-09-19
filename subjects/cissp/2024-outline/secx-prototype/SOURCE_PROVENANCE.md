# SecX source provenance lens

The Source Provenance lens is a learner-facing projection over source mappings that already exist in released CISSP Atlas data. It does not create new semantic curriculum relationships.

## Entry points

- Header control: **Sources · 20**
- Keyboard shortcut: `S`

The source root displays the released Atlas source registry from `CISSP_META.sources`.

## Explicit mappings only

For a selected source, the lens exposes three branches:

- **Objectives** — released objectives whose `source_ids` array contains the exact source ID.
- **Review cards** — Atlas-compatible review cards whose `source_ids` array contains the exact source ID.
- **Released scenarios** — standard released scenarios whose `source_ids` array contains the exact source ID.

The review-card registry is the same 140-card production-compatible set used by learner state: generated `OBJ-<objective-id>` cards plus released high-yield, AI, and precision cards.

Released scenarios are not fetched independently by this lens. `next-layer.js` remains the single question-bank release boundary: it loads only `RELEASED_BATCHES.json` entries, then publishes `SECX_RELEASED_QUESTIONS`, `SECX_RELEASED_BANK_STATE`, and the `secx:released-bank` readiness event. Source Provenance consumes that shared released-only registry.

No source membership is inferred from wording, topic similarity, shared labels, embeddings, or file proximity.

## Scenario answer boundary

Scenario provenance is intentionally not the scenario-practice view.

Source scenario nodes use a distinct provenance-only node kind (`source-scenario`) and may show the released stem/options plus source mapping, but they never expose the keyed answer or explanation. Opening a scenario through Source Provenance therefore must not create `scenario answer reveal` evidence in `cissp_secx_graph_state_v1`.

To attempt a scenario and reveal the answer, the learner must use the real objective → Released scenarios practice branch, where the depth-4 answer gate applies.

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

Source Provenance does not read or write learner progress state directly:

- it does not grade `cissp_atlas_progress_v1` merely by traversing provenance;
- its provenance-only scenario nodes do not record `scenario answer reveal` evidence;
- it does not infer mastery, readiness, weakness, or correctness from source traversal.

Ordinary graph visit/depth history may still be recorded by the generic graph-state decorator when a detail panel is opened. That navigation history is separate from card grading and scenario-answer evidence.

## Release isolation

The source lens does not discover question-bank files and does not read unreleased candidates. It consumes the same shared released-scenario registry used by the main graph, so the release manifest is loaded exactly once by `next-layer.js`.

## Validation

`source-audit.py` deterministically checks:

- Atlas source count against `meta.source_count`;
- source titles and role metadata;
- every objective/review-card/released-scenario source reference against the source registry;
- exact `source_ids.includes(...)` membership logic;
- shared released-bank consumption rather than a second manifest fetch;
- absence of learner-progress writes, candidate discovery, answer-key exposure, and similarity logic;
- the distinct `source-scenario` node kind;
- dependency load order and browser-smoke coverage.

`source-browser-smoke.html` + `source-browser-smoke.sh` exercise:

- the source-count control;
- `S` routing;
- all released source nodes;
- `ISC2_OUTLINE` → objective `1.1` provenance;
- a dynamically selected released scenario with a valid source citation;
- exact source → scenario routing;
- deepest source-scenario disclosure remaining answer-free;
- no false scenario-answer-reveal evidence;
- Home/root navigation;
- the 390px mobile shell.

As with the rest of the prototype, a browser PASS counts only when the committed gate actually executes against the exact candidate head.
