# SecX learner-state contract

The expanded SecX review surface keeps curriculum content immutable and stores learner activity separately.

## Shared Atlas retrieval-card progress

Retrieval-card grades intentionally reuse the production Atlas local-storage key:

- `cissp_atlas_progress_v1`

The graph uses the same four grades and stage schedule already used by Atlas:

- 1 · Wrong
- 2 · Hard
- 3 · Good
- 4 · Easy
- intervals: `0, 1, 3, 7, 14, 30, 60, 120` days

This means a grade applied to a released retrieval card in the expanded graph is visible to the existing Atlas study workflow instead of creating a second incompatible card-history system.

## Released-card registry

`learner-registry.js` derives the learner-facing retrieval-card registry from the already loaded released `CISSP_CHUNKS[].high` data after `data-precision.js` loads. It does not read the scenario question bank or candidate files.

The registry exists so learner-state views use the same released card objects and stable IDs as Atlas rather than reconstructing a second list.

## Due Reviews

`due-review.js` creates a schedule-derived **Due Reviews** branch over the released-card registry.

A card is included only when its existing Atlas card state has `due <= today`. The queue:

- uses the production Atlas scheduling state rather than a second scheduler;
- contains released retrieval cards only;
- does not use candidate question files or released scenario records;
- can be opened from the Due Reviews control or with `R`;
- pages large queues locally;
- updates its count immediately after a card grade in the same browser tab;
- removes a card from the due queue when a new grade schedules it into the future;
- may continue to show a card graded Wrong when its next due date remains today.

Due Reviews is a learner-state filter, not a new curriculum relationship. A card being due does not imply that the objective is weak or unmastered.

## Graph-specific activity

Graph navigation and scenario exposure use a separate key:

- `cissp_secx_graph_state_v1`

This store records only graph-specific evidence such as:

- node visits;
- maximum disclosure depth reached;
- last-seen timestamp;
- scenario answer-reveal count and timestamp.

It does **not** write curriculum content, source mappings, objective relationships, answer keys, correctness, or mastery claims.

## Evidence boundary

A scenario answer reveal is exposure only. It must never be interpreted as:

- a correct answer;
- a completed attempt;
- mastery;
- readiness;
- a spaced-repetition success grade.

If scenario-level correctness is added later, it must come from an explicit answer commitment/attempt workflow and remain distinguishable from simply opening layer 4.

Likewise, due status is a scheduling fact only. It must not be promoted into a semantic claim that the card, objective, or domain is weak.

## UI behavior

- Card nodes show `new`, `learning`, `due`, or `mature` from the shared Atlas card state.
- Card details expose the same four Atlas retrieval grades.
- The Due Reviews control shows the current released-card due count.
- `R` opens a local graph containing only currently due released retrieval cards.
- Graph nodes may show the deepest disclosure layer previously reached.
- Scenario nodes may show answer-reveal exposure, labeled as exposure rather than performance.
- The footer may show the number of currently due released retrieval cards.

## Validation requirements

Before the learner-state/due-review layer can replace the conservative prototype surface, the exact candidate head must pass:

1. production CISSP deterministic audit;
2. SecX graph/learner-state deterministic audit;
3. SecX due-review deterministic audit;
4. production CISSP browser smoke;
5. expanded SecX browser smoke.

The expanded smoke must verify card-grade persistence, same-window due-count refresh, `R` routing into the due-card branch, the separate graph-state key, the depth-4 scenario answer gate, and the rule that answer reveal does not create correctness or mastery evidence.
