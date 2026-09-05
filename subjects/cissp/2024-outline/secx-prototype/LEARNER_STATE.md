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

## Read-only learner API

`learner-state.js` is the learner-state owner. It keeps grading/persistence private and publishes a frozen read-only facade as `window.SECX_LEARNER` for downstream learner projections.

The facade exposes only:

- the shared Atlas progress-key identifier;
- `cardState(id)` as a frozen snapshot;
- `cardStatus(id)`;
- `isDue(id)`;
- `isMature(id)`;
- `todayISO()`;
- a frozen copy of the Atlas interval schedule.

It does **not** expose grading, saving, `localStorage.setItem`, graph-state mutation, or any curriculum mutation method.

The API keeps a cached Atlas progress object but compares the underlying storage string before reads. If another same-window tool/test writes the Atlas key directly, the next read resynchronizes automatically. Cross-tab `storage` events also invalidate/resynchronize the cache. This preserves current same-window behavior without forcing every projection to parse storage independently.

`due-review.js` and `study-lens.js` consume `SECX_LEARNER` and do not parse or write local storage themselves. This keeps `new` / `learning` / `due` / `mature` semantics in one runtime owner rather than allowing each projection to drift.

## Due Reviews

`due-review.js` creates a schedule-derived **Due Reviews** branch over the released-card registry.

A card is included only when the shared learner API reports its existing Atlas card state as due. The queue:

- uses the production Atlas scheduling state rather than a second scheduler;
- contains released retrieval cards only;
- does not use candidate question files or released scenario records;
- can be opened from the Due Reviews control or with `R`;
- pages large queues locally;
- updates its count immediately after a card grade in the same browser tab;
- removes a card from the due queue when a new grade schedules it into the future;
- may continue to show a card graded Wrong when its next due date remains today.

Due Reviews is a learner-state filter, not a new curriculum relationship. A card being due does not imply that the objective is weak or unmastered.

## Continue routing

The visible **Continue** control is a navigation helper over the same released-card registry and Atlas progress state. It does not maintain its own scheduler or score.

Its priority is deterministic:

1. a currently due card;
2. otherwise a card in the **Learning** state;
3. otherwise a new card in the current lowest-review-score domain;
4. otherwise any remaining new card;
5. otherwise the Study Queue root.

For card choices, Continue reuses the existing Study Queue ordering and routes to the page containing the selected released card. It selects the card but does not reveal its answer or grade it.

The lowest-review-score domain is used only as a tie-breaking study-priority hint after due and learning work are absent. It remains a stage-based scheduling signal, not a diagnosis of learner weakness or exam readiness.

If all released cards are mature and scheduled in the future, Continue falls back to the Study Queue rather than manufacturing extra work. The control refreshes after same-window grades and Atlas progress-storage changes, and it never writes `cissp_atlas_progress_v1` itself.

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
- **Continue** routes due → learning → lowest-review-score-domain new → any new → Study Queue using Atlas state only.
- Continue selects an existing review card but never auto-reveals or auto-grades it.
- Graph nodes may show the deepest disclosure layer previously reached.
- Scenario nodes may show answer-reveal exposure, labeled as exposure rather than performance.
- The footer may show the number of currently due released retrieval cards.

## Validation requirements

Before the learner-state/due-review layer can replace the conservative prototype surface, the exact candidate head must pass:

1. production CISSP deterministic audit;
2. SecX graph/learner-state deterministic audit;
3. SecX due-review deterministic audit;
4. SecX Study/Continue deterministic audit;
5. production CISSP browser smoke;
6. expanded SecX browser smoke;
7. dedicated Continue routing browser smoke.

The deterministic learner audits must verify that `SECX_LEARNER` is frozen/read-only, that Due/Study consumers do not directly parse/write local storage, and that shared status helpers remain the source for due/learning/mature classification.

The expanded smoke must verify card-grade persistence, same-window due-count refresh, `R` routing into the due-card branch, the separate graph-state key, the depth-4 scenario answer gate, and the rule that answer reveal does not create correctness or mastery evidence.

The Continue smoke must additionally verify the frozen API surface, absence of mutation methods, frozen card snapshots, same-window storage resynchronization, fresh-state weakest-domain new routing, Learning fallback, Due priority over simultaneous Learning work, caught-up fallback to Study Queue, and mobile layout without introducing a second learner-state store.
