# SecX keyboard knowledge-web prototype

This is an isolated review prototype. It does not replace or alter the verified CISSP Atlas v1.28 production site.

## Review surfaces

- `index.html` is the stable objective/subtopic prototype. It loads the released Atlas domain metadata and the 344 enriched subtopic mappings and remains the conservative comparison surface.
- `next.html` is the expanded review surface. It embeds `index.html`, then loads the reviewed retrieval-card data, a released-card learner registry, the card/scenario graph layer, learner state, and the due-review UX in dependency order. It is intentionally not the default prototype entry point yet.

The expanded page reuses the production release boundary for scenarios: it loads only question files enumerated by `study-site/question-bank/RELEASED_BATCHES.json`. Candidate files that are not in that released manifest are excluded. Retrieval cards are linked by their explicit Atlas `objective` field. Released scenarios are linked by their explicit `objectives` array, and subtopic-to-scenario navigation is created only when a scenario contains the exact released subtopic tag.

The review surface uses local pagination for large card/scenario clusters. Scenario answers and explanations remain behind progressive disclosure layer 4 so the graph supports retrieval before reveal rather than turning into an answer browser.

## Core interaction

The landing state places **SecX** in the middle of the canvas with the eight CISSP domains arranged around it. The user navigates with arrow keys using spatial graph traversal rather than a traditional sidebar/menu.

- Arrow: move to the connected node best aligned with that direction.
- Enter: descend through the current graph branch.
- Escape: close the depth panel first, then ascend one hierarchy level while preserving the parent selection.
- Space: progressively reveal more depth while remaining on the same node.
- `/`: open the keyboard search palette.
- `Home`: return to the SecX root.
- `1–4`: grade a retrieval card using the same Wrong / Hard / Good / Easy model as Atlas when a card detail is open.
- `R`: open the local **Due Reviews** graph generated from Atlas's scheduled released-card state.

Keyboard selection moves actual browser focus to the selected node, pointer/touch selection remains available, and the prototype respects `prefers-reduced-motion`.

## Current Atlas integration

The stable prototype loads the released Atlas metadata, all eight released domain chunks, and `coverage-detail.js` directly from the sibling `study-site/` directory. This gives the knowledge web the current **62 stable objective records** and **344 mapped enriched subtopics** without duplicating or rewriting the released curriculum.

For each objective node the prototype consumes the released Atlas objective ID, label, summary/direct rule, misconception trap, and source IDs. Source IDs are resolved through the released Atlas source registry. Each objective can then descend into the enriched subtopic labels already mapped to that objective in `coverage-detail.js`.

The expanded review surface additionally loads the released retrieval-card chunk from `data-precision.js` and the released scenario bank from the release manifest. Its objective hub exposes separate **Subtopics**, **Retrieval cards**, and **Released scenarios** branches so provenance is visible rather than flattening unlike relationship types into one cluster.

The released-card learner registry is derived from `CISSP_CHUNKS[].high` after `data-precision.js` loads. The **Due Reviews** branch filters only those released retrieval-card IDs by their existing Atlas `due` date; it does not use scenario files, candidate data, lexical similarity, or a second scheduling model. Large due queues are paged locally.

The domain layer uses the released Atlas domain names/weights and shows the number of objective nodes available in each domain. Large objective and subtopic sets use radial clusters; large retrieval-card, scenario, and due-review sets are paged so the local graph remains readable.

The search palette indexes the released domain names, objective labels/summaries/traps, and mapped subtopic labels. The expanded review layer adds reviewed retrieval cards and released scenarios to the same palette. Selecting a result reconstructs the appropriate local graph and focuses the exact node.

If released Atlas data cannot be loaded, the prototype fails visibly rather than inventing replacement objective, subtopic, card, or scenario content.

## Learner state

Learner state is separate from curriculum content. Full behavior is documented in `LEARNER_STATE.md`.

Released retrieval-card grading reuses Atlas's existing `cissp_atlas_progress_v1` state and its same stage schedule (`0, 1, 3, 7, 14, 30, 60, 120` days), so a card graded in the graph remains compatible with the production Atlas review workflow.

Graph-specific activity uses `cissp_secx_graph_state_v1` and records visits, maximum disclosure depth, and scenario answer-reveal exposure. Scenario reveal is explicitly **not** recorded as correctness, an attempt, mastery, or readiness.

The graph can display card `new / learning / due / mature` state, prior disclosure depth, scenario reveal exposure, and the current number of due released retrieval cards without mutating the released content model. Grading a card updates the Due Reviews count in the same browser tab; if a due card is rescheduled into the future while reviewing the due branch, it is removed from the current due queue on refresh.

## Relationship gate

Typed semantic cross-links are deliberately **not** generated from word similarity alone. A repeated phrase such as `least privilege` can suggest a candidate relationship, but publishing `depends-on`, `contrasts-with`, `implemented-by`, `mitigates`, `measured-by`, or another semantic edge requires an explicit reviewed mapping. This prevents the graph from turning search similarity into unsupported curriculum claims.

Current relationship rules are intentionally narrower:

- domain → objective: released Atlas domain/objective record;
- objective → subtopic: released `coverage-detail.js` mapping;
- objective → retrieval card: explicit card `objective` field;
- objective → released scenario: explicit scenario `objectives` field;
- subtopic → released scenario: exact explicit scenario `subtopics` tag match.

The Due Reviews view is a learner-state filter over released cards, not a semantic curriculum relationship.

No concept-level cross-domain relationship is published from lexical similarity alone.

## Progressive disclosure

The same node should expose four progressively deeper layers.

1. **Orient** — name, prompt/rule, and core labels.
2. **Understand** — explanation, decision context, why it matters.
3. **Discriminate** — traps, misconceptions, contrasts, failure modes.
4. **Apply / verify** — source traceability and application/practice.

For released scenarios, the keyed answer and explanation belong only to layer 4. The scenario stem/options must be visible before the answer so the graph remains retrieval-first.

## Exact-head validation

The draft includes dedicated deterministic audits and a browser harness:

- `audit.py` validates counts, explicit objective/source mappings, released-manifest isolation, exact-tag subtopic relationships, answer disclosure, and learner-state compatibility/separation.
- `due-audit.py` validates the released-card registry, dependency load order, Atlas-progress-only due filtering, same-window queue refresh, absence of question-bank/candidate dependencies, and browser coverage of the Due Reviews branch.
- `browser-smoke.html` exercises the expanded page in same-origin desktop and 390px mobile iframes.
- `browser-smoke.sh` serves the whole `2024-outline` directory so the prototype can load the real sibling Atlas datasets and released question-bank files; it uses a fresh temporary browser profile so prior Atlas storage cannot contaminate the result.
- `.github/workflows/secx-prototype-smoke.yml` is prepared to run the existing CISSP deterministic release audit, both SecX deterministic audits, JavaScript/shell syntax gates, the existing production CISSP browser smoke, and the expanded SecX browser smoke.

The expanded smoke verifies released Atlas counts, domain/objective/facet traversal, reviewed retrieval cards, shared Atlas card-grade persistence, same-window Due Reviews count updates, `R` routing into the due-card graph, separate graph-state persistence, released scenarios, the scenario answer-reveal boundary, search routing to an exact released item, `Home` return-to-root behavior, and the compact mobile shell.

A smoke result counts as evidence only when it is attached to the exact candidate head being reviewed. Do not reuse an earlier run after the branch moves.

## Recommended production architecture

1. Normalize remaining concept-level material only where explicit reviewed mappings exist; do not infer curriculum edges from lexical similarity.
2. Keep existing stable item IDs; add labels/relationships rather than rewriting content IDs.
3. Reject unknown objective IDs, source IDs, relationship targets, malformed label values, or links to unreleased question-bank records.
4. Generate deeper graph layers from normalized reviewed mappings instead of hand-authoring a second curriculum.
5. Keep current question-bank release isolation: unreleased candidates must not appear in the production graph.
6. Keep learner state separate from content and preserve compatibility with Atlas card progress.
7. Keep schedule-derived views such as Due Reviews as learner-state filters rather than curriculum edges.
8. Extend search with filters and typed relationship traversal only after those relationships are explicitly mapped and audited.
9. Keep views local rather than rendering thousands of nodes simultaneously; mount or page only the current node, parents, siblings, children, and selected reviewed cross-links.

## Promotion boundary

`next.html` is a review surface, not a production migration and not yet a replacement for `index.html`. Before promoting its card/scenario/learner-state/due-review layer into the default prototype or production Atlas, require a successful exact-head deterministic audit plus both production and expanded browser smoke checks. Static syntax validation and code review are useful preflight evidence but are not browser PASS evidence.

## Suggested visual behavior

- Center node is visually dominant but not oversized.
- Current node receives a clear focus halo.
- Parent path remains visible with brighter edges.
- Non-active distant nodes fade slightly.
- Cross-domain links use a distinct but subtle line treatment from hierarchy edges.
- A small breadcrumb remains visible at all times.
- Schedule-derived controls such as Due Reviews should remain visually distinct from curriculum hierarchy nodes.
- Animations should communicate topology changes, not add decorative motion.
- Continue respecting `prefers-reduced-motion` as deeper transitions are added.

## Important naming note

The prototype uses the requested center label **SecX**. If this evolves into a public product name, trademark/branding review should be done separately from the interface implementation.
