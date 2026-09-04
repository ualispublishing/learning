# SecX projection search

The expanded review surface reuses the existing `/` search palette for explicit navigation into Source Provenance and Coverage. It does not create a second search UI and it does not turn search similarity into curriculum relationships.

## Indexed projection targets

`projection-search.js` adds only these navigation records:

- released Atlas sources from the source registry;
- the eight Coverage domain views;
- released objectives as Coverage objective targets.

Existing curriculum/card/scenario search remains owned by the base graph and `next-layer.js`.

## Routing

Selecting a projection search result reconstructs an existing lens rather than creating a new graph relationship:

- source result → existing Source Provenance hub for that exact source ID;
- Coverage domain result → existing Coverage domain view;
- Coverage objective result → its domain Coverage view with the exact released objective selected.

The search layer preserves the previous `navigateSearch` handler for all existing curriculum/card/scenario result kinds.

## Semantic boundary

Search text is discovery/navigation data only.

Projection search must not:

- create or approve semantic edges;
- read `RELATIONSHIP_REVIEW.json`;
- read or write learner progress/state;
- invent source membership;
- invent objective/domain mappings;
- use fuzzy/similarity scores as relationship evidence.

Source and Coverage content continue to be populated by their existing explicit released-data rules.

## Validation

`projection-search-audit.py` checks explicit target kinds, existing-lens routing, load order, preservation of prior search routing, state isolation, and relationship-registry isolation.

`projection-search-smoke.html` / `projection-search-smoke.sh` exercise:

- `/` search for `ISC2_OUTLINE` into its Source Provenance hub;
- Escape back to root;
- `/` search for Coverage objective `1.1` into D1 Coverage with that exact objective focused;
- the 390px mobile search shell.

A browser PASS counts only when the committed harness executes against the exact candidate head.
