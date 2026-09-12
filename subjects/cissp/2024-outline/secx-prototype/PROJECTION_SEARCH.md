# SecX projection search

The expanded review surface reuses the existing `/` search palette for explicit navigation into Source Provenance, Coverage, and prototype-released Reviewed Links. It does not create a second search UI and it does not turn search similarity into curriculum relationships.

## Indexed projection targets

`projection-search.js` adds only these navigation records:

- released Atlas sources from the source registry;
- the eight Coverage domain views;
- released objectives as Coverage objective targets;
- relationships already present in the audited `window.SECX_RELEASED_RELATIONSHIPS` runtime.

Existing curriculum/card/scenario search remains owned by the base graph and `next-layer.js`.

Relationship projection entries are not built from reviewer data or repository discovery. `projection-search.js` loads before the relationship runtime, listens for the `secx:relationships-ready` event emitted after the reviewed relationship lens is initialized, then adds only the already prototype-released relationship IDs/content from the frozen runtime copy.

## Routing

Selecting a projection search result reconstructs an existing lens rather than creating a new graph relationship:

- source result → existing Source Provenance hub for that exact source ID;
- Coverage domain result → existing Coverage domain view;
- Coverage objective result → its domain Coverage view with the exact released objective selected;
- Reviewed Link result → existing relationship hub for that exact released `REL-*` ID.

The search layer preserves the previous `navigateSearch` handler for all existing curriculum/card/scenario result kinds.

For example, searching `REL-001` routes to `relationship:REL-001` and its two stable released endpoints. Search does not create a second relationship record or duplicate either endpoint.

## Semantic boundary

Search text is discovery/navigation data only.

Projection search must not:

- create or approve semantic edges;
- read `RELATIONSHIP_REVIEW.json`;
- directly read/fetch raw `RELEASED_RELATIONSHIPS.json`;
- discover candidate relationships;
- read or write learner progress/state;
- invent source membership;
- invent objective/domain mappings;
- use fuzzy/similarity scores, co-citation, coverage proximity, or shared wording as relationship evidence.

Source and Coverage content continue to be populated by their existing explicit released-data rules. Relationship search content comes only from the separate audited prototype release/runtime channel.

## Accessibility and focus

Projection Search keeps the existing combobox/listbox behavior:

- active results are exposed with `aria-activedescendant`;
- result options stay out of the Tab order;
- Tab / Shift+Tab remain contained inside the open search dialog;
- visible Search and Close controls preserve pointer/touch access;
- Escape and visible Close restore focus to the opener;
- routed Source, Coverage, and Reviewed Link results transfer focus to the selected graph context.

## Validation

`projection-search-audit.py` checks explicit Source/Coverage/Reviewed-Link target kinds, existing-lens routing, released-relationship-runtime provenance, relationship-runtime readiness signaling, load order, preservation of prior search routing, learner-state isolation, reviewer-registry isolation, raw-release-JSON isolation, and the prohibition on inferred relationship helpers.

`projection-search-smoke.html` / `projection-search-smoke.sh` exercise:

- `/` search for `ISC2_OUTLINE` into its Source Provenance hub;
- Escape back to root;
- `/` search for Coverage objective `1.1` into D1 Coverage with that exact objective focused;
- `/` search for prototype-released `REL-001` into its existing Reviewed Links hub with both stable endpoints present;
- confirmation that the reviewer registry is never fetched before or after relationship search routing;
- combobox/listbox focus behavior and persistent pointer/touch controls on the 390px mobile shell.

A browser PASS counts only when the committed harness executes against the exact candidate head. Projection-search success does not authorize a new relationship, production migration, merge, or deployment.
