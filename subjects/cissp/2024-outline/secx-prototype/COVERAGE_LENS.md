# SecX explicit coverage lens

The Coverage lens is a read-only projection over released CISSP Atlas mappings. It is designed to answer **what has explicit curriculum/practice exposure?** without converting corpus counts into learner mastery, exam readiness, or semantic relationships.

## Entry points

- `C` opens the Coverage map.
- The **Coverage · N** button displays the number of standard released scenarios in the shared released-bank registry.

## Data sources

Coverage is computed only from released Atlas data:

- stable objectives from the released Atlas chunks;
- enriched objective → subtopic mappings from `coverage-detail.js`;
- the Atlas-compatible review-card registry;
- supplemental released high-yield / AI / precision cards;
- standard released scenarios from the shared `SECX_RELEASED_QUESTIONS` registry.

`next-layer.js` is the single scenario release boundary. It loads only files enumerated by `question-bank/RELEASED_BATCHES.json`, then publishes:

- `SECX_RELEASED_QUESTIONS`;
- `SECX_RELEASED_BANK_STATE`;
- the `secx:released-bank` readiness event.

Coverage consumes those records directly and performs no independent fetch. Candidate-only question files are never discovered by directory scanning and are never included simply because they exist in the repository.

## Metrics

The lens reports raw explicit counts rather than a synthetic score.

At domain/objective level it may show:

- objective count;
- enriched subtopic count;
- Atlas review-card count;
- supplemental reviewed-card count;
- released standard-scenario count;
- source count;
- enriched subtopics that have at least one **exact** released scenario `subtopics` tag;
- objectives with zero explicitly mapped released scenarios.

The exported `SECX_COVERAGE_SNAPSHOT` exists so deterministic/browser checks can reconcile rendered counts to Atlas metadata and the shared released-bank state.

## Interpretation boundary

A coverage count is a property of the released learning corpus, not of the learner.

Therefore:

- more scenarios does not mean a learner has mastered an objective;
- zero scenarios is a **practice-exposure gap**, not proof that the curriculum omits the objective;
- a subtopic without an exact scenario tag may still be covered by objective, card, explanation, or other released material;
- shared tags, counts, or sources do not create semantic cross-domain edges;
- exam-domain weight is blueprint scope, not a learner score.

## Relationship boundary

Coverage uses explicit membership/mapping only. It does not publish `depends-on`, `contrasts-with`, `implemented-by`, `mitigates`, `measured-by`, or other semantic links.

All temporary `coverage:*` node IDs are navigation-only and are forbidden as durable semantic relationship endpoints by `relationship-audit.py`.

## Learner-state boundary

`coverage-lens.js` does not read or write `cissp_atlas_progress_v1` or `cissp_secx_graph_state_v1`. Coverage is independent of learner scheduling and performance state.

The general graph learner-state decorator may still record ordinary graph visits/depth when a learner opens a Coverage detail panel; that activity remains graph history and does not alter the coverage calculation.

## Validation

`coverage-audit.py` recomputes the corpus counts from repository data and checks:

- Atlas objective/subtopic/review-card totals;
- released standard-scenario total;
- central release-manifest enforcement in `next-layer.js`;
- use of the shared released-scenario registry/event by Coverage;
- absence of a second Coverage fetch or manifest loader;
- exact subtopic-tag exposure logic;
- no candidate path hard-coding;
- no learner-state dependency;
- no inferred-relationship helper;
- correct runtime load order;
- continued isolation of `RELATIONSHIP_REVIEW.json`.

`coverage-browser-smoke.html` / `coverage-browser-smoke.sh` verify the desktop and 390px mobile interaction path, including shared-bank readiness/count equality, D1 and objective `1.1`, Escape hierarchy, and Atlas-count reconciliation.
