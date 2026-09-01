# SecX keyboard knowledge-web prototype

This is an isolated review prototype. It does not replace or alter the verified CISSP Atlas v1.28 production site.

## Core interaction

The landing state places **SecX** in the middle of the canvas with the eight CISSP domains arranged around it. The user navigates with arrow keys using spatial graph traversal rather than a traditional sidebar/menu.

- Arrow: move to the connected node best aligned with that direction.
- Enter: descend into a node's child cluster.
- Escape: ascend or close the depth panel.
- Space: progressively reveal more depth while remaining on the same concept.

The prototype includes a few sample objective clusters for Domains 1, 3, 5, and 7; other domains show generic children to demonstrate the hierarchy.

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

1. Normalize current Atlas content into a graph-oriented JSON model.
2. Keep existing stable item IDs; add labels/relationships rather than rewriting content IDs.
3. Build a migration/audit script that rejects unknown objective IDs, source IDs, relationship targets, or malformed label values.
4. Generate the graph UI from the normalized model.
5. Keep current question-bank release isolation: unreleased candidates must not appear in the production graph.
6. Store learner state separately from content: node visits, depth reached, retrieval grade, practice evidence, weak relationships, and spaced-review due dates.
7. Add search/palette and breadcrumb/history after the spatial navigation is stable.
8. Add zoomed local clusters instead of rendering thousands of nodes simultaneously; only the current node, parents, siblings, children, and selected cross-links need to be mounted.

## Suggested visual behavior

- Center node is visually dominant but not oversized.
- Current node receives a clear focus halo.
- Parent path remains visible with brighter edges.
- Non-active distant nodes fade slightly.
- Cross-domain links use a distinct but subtle line treatment from hierarchy edges.
- A small breadcrumb remains visible at all times.
- Animations should communicate topology changes, not add decorative motion.
- Respect `prefers-reduced-motion` in production.

## Important naming note

The prototype uses the requested center label **SecX**. If this evolves into a public product name, trademark/branding review should be done separately from the interface implementation.
