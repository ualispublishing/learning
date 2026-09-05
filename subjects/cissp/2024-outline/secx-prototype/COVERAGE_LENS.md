# SecX explicit coverage lens

The Coverage lens is a read-only projection over released CISSP Atlas mappings. It is designed to answer **what has explicit curriculum/practice exposure?** without converting corpus counts into learner mastery, exam readiness, curriculum deficiency, or semantic relationships.

## Entry points

- `C` opens the Coverage map.
- The **Coverage · N** button displays the number of standard released scenarios in the shared released-bank registry.
- Enter on the Coverage center opens the paged **Practice Exposure Gaps** view.

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
- enriched subtopics that lack such an exact released scenario tag;
- objectives with zero explicitly mapped released scenarios.

The exported `SECX_COVERAGE_SNAPSHOT` exists so deterministic/browser checks can reconcile rendered counts to Atlas metadata and the shared released-bank state. It includes the exact-tag gap records as well as aggregate counts.

## Practice Exposure Gaps

A gap is defined narrowly and deterministically:

> An enriched subtopic mapped to objective O is a practice-exposure gap when no manifest-released standard scenario mapped to O contains that exact subtopic label in its released `subtopics` array.

For the current released Atlas bank:

- **344** enriched subtopics exist;
- **305** have at least one exact released scenario tag under their mapped objective;
- **39** are exact-tag practice-exposure gaps;
- **0** objectives lack all released scenario mappings.

The gap list is paged at 16 records per local graph page. Gap navigation IDs use `coverage:gap:<objective-id>:<coverage-index>`. These are projection-only UI IDs derived from the released coverage mapping; they are not durable semantic curriculum IDs.

Each gap retains its parent objective and original released coverage label. Selecting a gap explains the exact-tag absence and then repeats the interpretation boundary before deeper disclosure.

## Interpretation boundary

A coverage count or gap is a property of the released learning corpus, not of the learner.

Therefore:

- more scenarios does not mean a learner has mastered an objective;
- zero scenarios is a **practice-exposure gap**, not proof that the curriculum omits the objective;
- an exact-tag gap is not evidence that a subtopic is missing, incorrect, or insufficiently taught;
- a subtopic without an exact scenario tag may still be covered by objective, card, explanation, or broader released scenario context;
- a gap is not learner weakness, mastery, readiness, or a remediation prescription;
- shared tags, counts, or sources do not create semantic cross-domain edges;
- exam-domain weight is blueprint scope, not a learner score.

## Relationship boundary

Coverage uses explicit membership/mapping only. It does not publish `depends-on`, `contrasts-with`, `implemented-by`, `mitigates`, `measured-by`, or other semantic links.

All temporary `coverage:*` node IDs—including `coverage:gap:*`—are navigation-only and are forbidden as durable semantic relationship endpoints by `relationship-audit.py`.

## Learner-state boundary

`coverage-lens.js` does not read or write `cissp_atlas_progress_v1` or `cissp_secx_graph_state_v1`. Coverage is independent of learner scheduling and performance state.

The general graph learner-state decorator may still record ordinary graph visits/depth when a learner opens a Coverage detail panel; that activity remains graph history and does not alter the coverage calculation.

## Validation

`coverage-audit.py` recomputes the corpus counts and gap set from repository data and checks:

- Atlas objective/subtopic/review-card totals;
- released standard-scenario total;
- central release-manifest enforcement in `next-layer.js`;
- use of the shared released-scenario registry/event by Coverage;
- absence of a second Coverage fetch or manifest loader;
- exact subtopic-tag exposure logic;
- exact gap count and deterministic projection IDs;
- Coverage-center → gap-view routing and Escape hierarchy;
- no candidate path hard-coding;
- no learner-state dependency;
- no inferred-relationship helper;
- correct runtime load order;
- continued isolation of `RELATIONSHIP_REVIEW.json`.

`coverage-browser-smoke.html` / `coverage-browser-smoke.sh` verify the desktop and 390px mobile interaction path, including shared-bank readiness/count equality, visible Coverage control, `C`, Coverage center → gap traversal, exact gap detail boundaries, D1 and objective `1.1`, Escape hierarchy, and horizontal-overflow safety.
