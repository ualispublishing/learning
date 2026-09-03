# SecX keyboard knowledge-web prototype

This is an isolated review prototype. It does not replace or alter the verified CISSP Atlas v1.28 production site.

## Review surfaces

- `index.html` is the stable objective/subtopic prototype. It loads the released Atlas domain metadata and the 344 enriched subtopic mappings and remains the conservative comparison surface.
- `next.html` is the expanded review surface. It embeds `index.html`, then adds the reviewed retrieval-card layer and released-only scenario layer through `next-layer.js`. It is intentionally not the default prototype entry point yet.

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

Keyboard selection moves actual browser focus to the selected node, pointer/touch selection remains available, and the prototype respects `prefers-reduced-motion`.

## Current Atlas integration

The stable prototype loads the released Atlas metadata, all eight released domain chunks, and `coverage-detail.js` directly from the sibling `study-site/` directory. This gives the knowledge web the current **62 stable objective records** and **344 mapped enriched subtopics** without duplicating or rewriting the released curriculum.

For each objective node the prototype consumes the released Atlas objective ID, label, summary/direct rule, misconception trap, and source IDs. Source IDs are resolved through the released Atlas source registry. Each objective can then descend into the enriched subtopic labels already mapped to that objective in `coverage-detail.js`.

The expanded review surface additionally loads the released retrieval-card chunk from `data-precision.js` and the released scenario bank from the release manifest. Its objective hub exposes separate **Subtopics**, **Retrieval cards**, and **Released scenarios** branches so provenance is visible rather than flattening unlike relationship types into one cluster.

The domain layer uses the released Atlas domain names/weights and shows the number of objective nodes available in each domain. Large objective and subtopic sets use radial clusters; large retrieval-card and scenario sets are paged so the local graph remains readable.

The search palette indexes the released domain names, objective labels/summaries/traps, and mapped subtopic labels. The expanded review layer adds reviewed retrieval cards and released scenarios to the same palette. Selecting a result reconstructs the appropriate local graph and focuses the exact node.

If released Atlas data cannot be loaded, the prototype fails visibly rather than inventing replacement objective, subtopic, card, or scenario content.

## Relationship gate

Typed semantic cross-links are deliberately **not** generated from word similarity alone. A repeated phrase such as `least privilege` can suggest a candidate relationship, but publishing `depends-on`, `contrasts-with`, `implemented-by`, `mitigates`, `measured-by`, or another semantic edge requires an explicit reviewed mapping. This prevents the graph from turning search similarity into unsupported curriculum claims.

Current relationship rules are intentionally narrower:

- domain → objective: released Atlas domain/objective record;
- objective → subtopic: released `coverage-detail.js` mapping;
- objective → retrieval card: explicit card `objective` field;
- objective → released scenario: explicit scenario `objectives` field;
- subtopic → released scenario: exact explicit scenario `subtopics` tag match.

No concept-level cross-domain relationship is published from lexical similarity alone.

## Progressive disclosure

The same node should expose four progressively deeper layers.

1. **Orient** — name, prompt/rule, and core labels.
2. **Understand** — explanation or decision context.
3. **Discriminate** — traps, misconceptions, contrasts, or common errors.
4. **Apply / verify** — source traceability and application; for scenarios this is where the keyed answer and explanation are revealed.

Space cycles these layers without losing the user's location in the graph.

## Recommended production architecture

1. Normalize the remaining Atlas content layers into a graph-oriented model while preserving released objective IDs and current explicit subtopic/card/scenario mappings.
2. Keep existing stable item IDs; add labels/relationships rather than rewriting content IDs.
3. Build a migration/audit script that rejects unknown objective IDs, source IDs, relationship targets, malformed label values, or links to unreleased question-bank records.
4. Generate deeper graph layers from the normalized model instead of hand-authoring a second curriculum.
5. Keep current question-bank release isolation: unreleased candidates must not appear in the production graph.
6. Store learner state separately from content: node visits, depth reached, retrieval grade, practice evidence, weak relationships, and spaced-review due dates.
7. Extend search with filters and typed relationship traversal only after those relationships are explicitly mapped and audited.
8. Keep views local rather than rendering thousands of nodes simultaneously; mount or page only the current node, parents, siblings, children, and selected reviewed cross-links.

## Promotion boundary

`next.html` is a review surface, not a production migration and not yet a replacement for `index.html`. Before promoting its card/scenario layer into the default prototype or production Atlas, run the established browser smoke/interaction checks plus deterministic release-isolation checks against the exact candidate head. Do not treat static syntax validation alone as browser evidence.

## Suggested visual behavior

- Center node is visually dominant but not oversized.
- Current node receives a clear focus halo.
- Parent path remains visible with brighter edges.
- Non-active distant nodes fade slightly.
- Cross-domain links use a distinct but subtle line treatment from hierarchy edges.
- A small breadcrumb remains visible at all times.
- Animations should communicate topology changes, not add decorative motion.
- Continue respecting `prefers-reduced-motion` as deeper transitions are added.

## Important naming note

The prototype uses the requested center label **SecX**. If this evolves into a public product name, trademark/branding review should be done separately from the interface implementation.
