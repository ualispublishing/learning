# SecX keyboard knowledge-web prototype

This is an isolated **review prototype**. It does not replace or alter the verified CISSP Atlas v1.28 production site.

## Review surfaces

- `index.html` is the conservative objective/subtopic comparison surface.
- `next.html` is the expanded review surface. It embeds `index.html`, then loads the Atlas-compatible review-card registry, released scenario layer, learner state, Due Reviews, Study Queue, Source Provenance, Coverage, Projection Search, and the separately promoted reviewed-relationship runtime in a fixed dependency order.

The expanded surface remains review-only. It is not the production Atlas surface and PR #133 remains draft/unmerged.

## Released-data boundaries

The prototype reuses released Atlas data rather than creating a second curriculum:

- **62** stable objectives from released domain chunks;
- **344** enriched subtopic mappings from `coverage-detail.js`;
- **140** Atlas-compatible review cards;
- **543** released standard scenarios loaded only through `question-bank/RELEASED_BATCHES.json`;
- **20** released source records from `CISSP_META.sources`;
- **3** relationship-specific, source-reviewed links promoted into the separate SecX review-prototype relationship artifact.

`next-layer.js` remains the single standard-scenario release boundary. It publishes:

- `SECX_RELEASED_QUESTIONS`;
- `SECX_RELEASED_BANK_STATE`;
- `secx:released-bank`.

Source Provenance and Coverage consume that shared scenario registry rather than reloading or discovering question-bank files.

Semantic relationships use a separate boundary:

- `RELATIONSHIP_REVIEW.json` — reviewer-only semantic-review registry; never learner-loaded;
- `RELEASED_RELATIONSHIPS.json` — dedicated prototype promotion artifact;
- `released-relationships.js` — frozen learner-runtime representation;
- `relationship-release-audit.py` — exact review/promotion/runtime integrity gate;
- `relationship-lens.js` — learner-facing review-prototype projection over only the released copy.

Current explicit mappings are therefore:

- domain → objective;
- objective → subtopic;
- objective → retrieval card;
- objective → released scenario;
- subtopic → released scenario only by exact explicit released subtopic tag;
- source → objective/review card/released scenario only by exact `source_ids` membership;
- relationship → stable released endpoint only after relationship-specific review and prototype promotion.

No semantic relationship is inferred from text similarity, co-citation, embeddings, shared labels, or Coverage proximity.

## Keyboard grammar

- Arrow keys: spatial traversal.
- Enter: descend.
- Escape: close detail first, then ascend while preserving local context.
- Space: cycle four disclosure depths.
- `/`: search released curriculum/projections.
- Home: return to SecX root.
- `1–4`: grade an open review card using Atlas Wrong / Hard / Good / Easy semantics.
- `R`: open **Due Reviews**.
- `Q`: open **Study Queue**.
- `S`: open **Source Provenance**.
- `C`: open **Coverage**.
- `L`: open **Reviewed Links**.

Pointer/touch remains supported, browser focus follows routed graph selection, and `prefers-reduced-motion` is respected. The expanded surface also provides visible Continue, Search/Close, and persistent detail Close/Depth/Open controls so keyboard-first does not become keyboard-only.

## Objective hubs and released scenarios

Expanded objective hubs expose separate **Subtopics / Retrieval cards / Released scenarios** branches so unlike relationship types are not flattened together.

Released scenarios are linked through explicit objective metadata and exact subtopic tags only. Scenario stem/options are available before answer reveal; the keyed answer and explanation remain at disclosure layer 4 so the graph stays retrieval-first.

Large card/scenario branches are paged locally rather than mounting the full bank at once.

## Learner state

Learner state is separate from curriculum content. See `LEARNER_STATE.md`.

Review-card grading reuses Atlas `cissp_atlas_progress_v1` and the same stage schedule:

`0, 1, 3, 7, 14, 30, 60, 120` days.

Graph-specific activity uses `cissp_secx_graph_state_v1` for visits, maximum disclosure depth, and scenario answer-reveal exposure. Relationship traversal may record separate graph visit/depth evidence, but it does not mutate Atlas mastery/progress state.

A scenario answer reveal is exposure only. It is not correctness, an attempt result, mastery, readiness, or a spaced-review success grade.

### Due Reviews

`R` or **Review due · N** opens a paged local graph of Atlas review cards whose existing `due <= today`. The queue uses no scenario/candidate data and no second scheduling algorithm. Visible-button and `R` entry share the same settled focus handoff so desktop and nested 390px mobile navigation land on the Due Reviews root without changing learner state.

### Study Queue

`Q` or **Study · N due** opens five learner-state branches: Due reviews, New cards, Learning, Mature, and Lowest review-stage-score domain.

The lowest-domain calculation mirrors Atlas objective/domain stage aggregation and the higher-exam-weight tie-break. It is a study-priority signal, not proof of weakness or exam readiness.

### Continue

The visible **Continue · …** control chooses work in this order:

1. currently due review card;
2. Learning card;
3. new card in the current lowest-review-score domain;
4. any remaining new card;
5. Study Queue root when no due, learning, or new cards remain.

Continue never auto-reveals an answer, auto-grades a card, creates a second learner-state record, or converts review stage into a mastery/readiness claim.

## Source Provenance

`S` or **Sources · 20** opens the released source registry. See `SOURCE_PROVENANCE.md`.

For a selected source, the lens exposes exact `source_ids` membership for released objectives, review cards, and manifest-released standard scenarios.

Source scenario nodes are provenance-only. They can show the scenario prompt/options and citation mapping but never the keyed answer/explanation, and deepest Source disclosure must not record a scenario answer reveal.

A shared citation is provenance evidence only. It does not create a semantic relationship.

## Coverage

`C` or **Coverage · N** opens a read-only corpus/practice-exposure projection. See `COVERAGE_LENS.md`.

Coverage reports explicit released counts by domain/objective. With the current released bank, **305/344** enriched subtopics have at least one exact released scenario tag and **39** are exact-tag practice-exposure gaps.

Those gaps are corpus-exposure observations only. They are not curriculum omissions, factual deficiencies, learner weakness, mastery/readiness signals, or semantic relationships.

## Projection Search

Projection Search extends `/` with exact Source Provenance, Coverage-domain, Coverage-objective, and prototype-released Reviewed Link navigation entries. Relationship search indexes only `window.SECX_RELEASED_RELATIONSHIPS` after the relationship runtime signals readiness and routes by stable `REL-*` ID into the existing Links hub.

Projection Search never loads `RELATIONSHIP_REVIEW.json` or raw `RELEASED_RELATIONSHIPS.json`, never discovers relationship candidates, and never turns wording similarity or search proximity into a semantic edge. The browser gate explicitly searches `REL-001`, routes to its reviewed hub, verifies both stable endpoints, and rechecks reviewer-registry isolation.

The search UI uses a combobox/listbox pattern with active-descendant state, modal focus containment, visible Search/Close controls, and opener-focus restoration.

## Reviewed semantic Links

`L` or **Links · 3** opens only relationships that passed the separate review + promotion pipeline.

The current prototype-released set is:

- `REL-001`: `5.1 depends-on 1.8` — access control depends on personnel lifecycle signals for onboarding, transfer, and termination changes;
- `REL-002`: `7.6 evidenced-by 7.2` — incident-management decisions use evidence from operational logging and monitoring;
- `REL-003`: `7.10 depends-on 1.7` — recovery strategy depends on BIA/business-continuity requirements.

The relationship lens displays the source-reviewed rationale, then exposes the two stable released endpoints. Opening an endpoint returns to that objective's normal Atlas graph context rather than creating a duplicate curriculum node.

`RELATIONSHIP_REVIEW.json` remains reviewer-only even though those three relationships have been separately promoted. New relationships cannot appear in the Links lens or relationship search merely because their endpoints are VERIFIED or share sources/terminology.

See `RELATIONSHIP_REVIEW.md` and `CONTENT_MODEL.md`.

## Progressive disclosure

Each node exposes four depths:

1. **Orient** — identity, prompt/rule, labels.
2. **Understand** — explanation and decision context.
3. **Discriminate** — traps, misconceptions, contrasts, failure modes.
4. **Apply / verify** — sources and application/practice.

Space changes depth without losing graph position.

## Loader and failure behavior

The expanded loader exposes `loading → ready/error` on the embedded conservative frame. The reviewed dependency chain now ends with:

1. `projection-search.js`;
2. `released-relationships.js`;
3. `relationship-lens.js`;
4. then `ready`.

A resource failure or JavaScript execution failure produces an accessible assertive error while leaving the conservative knowledge web available. A later load callback cannot overwrite an earlier error.

Dedicated browser smokes verify successful desktop/mobile readiness, a real HTTP-404 dependency failure, and a served-JavaScript execution failure. Fault-injection runners restore the original dependency and CI verifies a clean checkout afterward.

## Exact-head validation

The draft includes deterministic gates for each major layer:

- `audit.py` — released graph counts/mappings, manifest isolation, exact subtopic tags, answer boundary, learner-state compatibility;
- `browser-fixtures-audit.py` — deterministic smoke fixtures;
- `due-audit.py` — complete 140-card review registry and settled desktop/mobile Due Reviews entry focus;
- `study-audit.py` — Study Queue and Continue priority/routing contract;
- `source-audit.py` — exact Source Provenance mappings and answer/state isolation;
- `coverage-audit.py` — count reconciliation and exact-tag exposure/gaps;
- `projection-search-audit.py` — explicit Source/Coverage/released-Link routing, reviewer-registry isolation, and accessibility behavior;
- `relationship-audit.py` — stable endpoints and relationship-specific review requirements;
- `relationship-release-audit.py` — exact reviewer/promotion/runtime-copy integrity and reviewer-registry isolation;
- release-boundary, hygiene, and completeness gates.

Browser suites verify:

- expanded graph/cards/scenarios/learner state;
- loader readiness;
- Continue routing and mobile Due focus handoff;
- Source Provenance;
- Coverage;
- Projection Search including exact `REL-001` routing;
- Reviewed Links on desktop and 390px mobile;
- loader HTTP-404 fallback;
- loader JavaScript execution-error fallback.

`.github/workflows/secx-prototype-smoke.yml` runs production CISSP preservation checks plus all SecX deterministic/syntax/browser gates against one exact candidate head.

The last runtime head before this documentation-only update was `55bce7817125dd653b9be303c7e48f98578b25c5`; **SecX Prototype Smoke #485 (`34700013413`) passed every required gate** on that exact SHA, including production preservation, settled mobile Due Reviews focus, released-`REL-001` Projection Search routing, Reviewed Links, and both loader fault-injection regressions. This documentation head must pass the same exact-head workflow before it becomes current evidence.

## Production architecture rules

1. Preserve stable released IDs and explicit source/release scope.
2. Keep one manifest-enforced released-scenario loader and let read-only projections consume its shared runtime registry.
3. Keep unreleased question candidates out of learner-facing runtime.
4. Keep learner state separate from curriculum records.
5. Treat Due Reviews, Study Queue, and Continue as learner-state projections/navigation, not curriculum edges or mastery claims.
6. Treat Source Provenance as an exact citation projection, not a semantic cross-link generator.
7. Treat Coverage counts/gaps as corpus/practice-exposure projections, not learner scores or semantic edge generators.
8. Keep relationship candidate discovery, relationship review, prototype promotion, runtime publication/search projection, and any production migration as separate stages.
9. Reject unknown IDs, invalid source references, temporary semantic endpoints, reviewer-registry loading, and review/release/runtime drift.
10. Keep local graph mounting/pagination rather than rendering the entire corpus at once.
11. Require deterministic and browser gates before any production migration.

## Promotion boundary

`next.html` remains review-only. Do not replace `index.html`, merge to production, mark the PR ready, or deploy merely because the review prototype gates pass. Production migration is a separate decision and validation boundary.

## Naming note

The prototype uses the requested center label **SecX**. Public product naming/trademark review remains separate from interface implementation.
