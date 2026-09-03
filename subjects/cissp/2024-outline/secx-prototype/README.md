# SecX keyboard knowledge-web prototype

This is an isolated review prototype. It does not replace or alter the verified CISSP Atlas v1.28 production site.

## Core interaction

The landing state places **SecX** in the middle of the canvas with the eight CISSP domains arranged around it. The user navigates with arrow keys using spatial graph traversal rather than a traditional sidebar/menu.

- Arrow: move to the connected node best aligned with that direction.
- Enter: descend through `domain → objective → subtopic`.
- Escape: close the depth panel first, then ascend one hierarchy level while preserving the parent selection.
- Space: progressively reveal more depth while remaining on the same node.
- `/`: open the keyboard search palette.
- `Home`: return to the SecX root.

Keyboard selection moves actual browser focus to the selected node, pointer/touch selection remains available, and the prototype respects `prefers-reduced-motion`.

## Current Atlas integration

The prototype loads the released Atlas metadata, all eight released domain chunks, and `coverage-detail.js` directly from the sibling `study-site/` directory. This gives the knowledge web the current **62 stable objective records** and **344 mapped enriched subtopics** without duplicating or rewriting the released curriculum.

For each objective node the prototype consumes the released Atlas objective ID, label, summary/direct rule, misconception trap, and source IDs. Source IDs are resolved through the released Atlas source registry. Each objective can then descend into the enriched subtopic labels already mapped to that objective in `coverage-detail.js`.

The domain layer uses the released Atlas domain names/weights and shows the number of objective nodes available in each domain. Large objective and subtopic sets use two radial rings so local clusters remain readable rather than collapsing into one crowded circle.

The search palette indexes the released domain names, objective labels/summaries/traps, and all mapped subtopic labels. Selecting a result reconstructs the appropriate local graph and focuses the exact domain, objective, or subtopic node.

If released Atlas data cannot be loaded, the prototype fails visibly rather than inventing replacement objective or subtopic content.

This is now a subtopic-level integration. Retrieval cards, scenarios, learner state, typed concept relationships, and cross-domain links remain future graph layers rather than being silently inferred from incomplete mappings.

## Relationship gate

Typed semantic cross-links are deliberately **not** generated from word similarity alone. A repeated phrase such as `least privilege` can suggest a candidate relationship, but publishing `depends-on`, `contrasts-with`, `implemented-by`, `mitigates`, `measured-by`, or another semantic edge requires an explicit reviewed mapping. This prevents the graph from turning search similarity into unsupported curriculum claims.

## Refined product concept

### 1. The web is the curriculum
Do not render the syllabus as a long list and then separately create a graph. The graph should be generated from the same canonical content model that powers cards, claims, practice questions, sources, progress, and search.

### 2. Hierarchy plus cross-links
Primary traversal is hierarchical:

`SecX → domain → objective → subtopic → concept → card/claim`

But concept nodes may have typed cross-domain relationships such as `depends-on`, `contrasts-with`, `implemented-by`, `mitigates`, or `measured-by`. This keeps the model closer to how security knowledge actually relates.

### 3. Space is progressive disclosure
Space should not simply open a modal. It advances through stable depth layers:

- Layer 1: name + one-line rule.
- Layer 2: explanation + why it matters.
- Layer 3: traps + distinctions + examples.
- Layer 4: sources + related concepts + scenario/application.

The graph remains visible behind the detail panel so users do not lose their place.

### 4. Keyboard-first, not keyboard-only
Pointer/touch selection should still work. Tab should retain normal accessible browser behavior. The arrow/space/enter/escape grammar is an enhancement for fast study, not a replacement for accessibility.

### 5. Labels become both metadata and visual affordances
Each claim/card should expose compact chips for its most useful labels. Full labels appear at deeper disclosure. This enables filtering, search, source audits, cross-domain discovery, and future auto-generated pathways such as “show every decision rule involving residual risk.”

## Recommended production architecture

1. Normalize the remaining Atlas content layers into a graph-oriented model while preserving the released objective IDs and current subtopic mappings already consumed by the prototype.
2. Keep existing stable item IDs; add labels/relationships rather than rewriting content IDs.
3. Build a migration/audit script that rejects unknown objective IDs, source IDs, relationship targets, or malformed label values.
4. Generate deeper graph layers from the normalized model instead of hand-authoring a second curriculum.
5. Keep current question-bank release isolation: unreleased candidates must not appear in the production graph.
6. Store learner state separately from content: node visits, depth reached, retrieval grade, practice evidence, weak relationships, and spaced-review due dates.
7. Extend search with filters and typed relationship traversal only after those relationships are explicitly mapped and audited.
8. Keep views local rather than rendering thousands of nodes simultaneously; mount only the current node, parents, siblings, children, and selected cross-links.

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
