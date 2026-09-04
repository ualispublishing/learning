# SecX keyboard knowledge-web prototype

This is an isolated review prototype. It does not replace or alter the verified CISSP Atlas v1.28 production site.

## Review surfaces

- `index.html` is the conservative objective/subtopic prototype.
- `next.html` is the expanded review surface. It embeds `index.html`, then loads the Atlas-compatible review-card registry, card/scenario graph layer, learner state, Due Reviews, Study Queue, Source Provenance, Coverage, and Projection Search in dependency order.

The expanded surface is still review-only and is not the default prototype entry point or production Atlas.

## Released-data boundaries

The prototype reuses released Atlas data rather than creating a second curriculum:

- **62** stable objectives from released domain chunks;
- **344** enriched subtopic mappings from `coverage-detail.js`;
- **140** Atlas-compatible review cards: generated `OBJ-<objective-id>` cards plus released high-yield/AI/precision cards;
- released standard scenarios loaded only through `question-bank/RELEASED_BATCHES.json`;
- **20** released source records from `CISSP_META.sources`.

`next-layer.js` is the single scenario release boundary. After loading only manifest-listed standard scenarios, it publishes a shared read-only-by-convention runtime snapshot:

- `SECX_RELEASED_QUESTIONS`;
- `SECX_RELEASED_BANK_STATE`;
- `secx:released-bank` readiness event.

Source Provenance and Coverage consume that shared registry rather than fetching the question bank again. Candidate scenario files that are not in the released manifest remain excluded.

Current explicit mappings are:

- domain → objective;
- objective → subtopic;
- objective → retrieval card;
- objective → released scenario;
- subtopic → released scenario only by exact explicit released subtopic tag;
- source → objective/review card/released scenario only by exact `source_ids` membership.

No concept-level cross-domain semantic relationship is inferred from text similarity or co-citation.

## Keyboard grammar

- Arrow keys: spatial traversal.
- Enter: descend.
- Escape: close detail first, then ascend while preserving local context.
- Space: cycle four disclosure depths.
- `/`: search released domains/objectives/subtopics/cards/scenarios/sources/coverage projections.
- Home: return to SecX root.
- `1–4`: grade an open review card using Atlas Wrong / Hard / Good / Easy semantics.
- `R`: open **Due Reviews**.
- `Q`: open **Study Queue**.
- `S`: open **Source Provenance**.
- `C`: open **Coverage**.

Pointer/touch remains supported, actual browser focus follows keyboard selection, and `prefers-reduced-motion` is respected. The expanded review surface also provides visible Search/Close controls and persistent detail Close/Depth/Open controls so keyboard-first does not become keyboard-only.

## Objective hub and released scenarios

The expanded objective hub exposes separate **Subtopics / Retrieval cards / Released scenarios** branches so unlike relationship types are not flattened together.

Released scenarios are linked through explicit objective metadata and exact subtopic tags only. Scenario stem/options are available before answer reveal; the keyed answer and explanation remain at disclosure layer 4 so the graph stays retrieval-first.

Large card/scenario branches are paged locally rather than mounting the full bank at once.

## Learner state

Learner state is separate from curriculum content. See `LEARNER_STATE.md`.

Review-card grading reuses Atlas `cissp_atlas_progress_v1` and the same stage schedule:

`0, 1, 3, 7, 14, 30, 60, 120` days.

Graph-specific activity uses `cissp_secx_graph_state_v1` for visits, maximum disclosure depth, and scenario answer-reveal exposure.

A scenario answer reveal is exposure only. It is not correctness, an attempt result, mastery, readiness, or a spaced-review success grade.

### Due Reviews

`R` or **Review due · N** opens a paged local graph of Atlas review cards whose existing `due <= today`.

The queue uses no scenario/candidate data and no second scheduling algorithm. Grading updates the due count in the same tab.

### Study Queue

`Q` or **Study · N due** opens five learner-state branches:

- Due reviews;
- New cards;
- Learning;
- Mature;
- Lowest review-stage-score domain.

The lowest-domain calculation mirrors Atlas objective/domain stage aggregation and higher-exam-weight tie-break. It is a study-priority signal, not proof of weakness or exam readiness.

## Source Provenance

`S` or **Sources · 20** opens the released source registry. See `SOURCE_PROVENANCE.md`.

For a selected source, the lens exposes exact `source_ids` membership for:

- released objectives;
- Atlas-compatible review cards;
- manifest-released standard scenarios from the shared released-bank registry.

Source scenario nodes are provenance-only (`source-scenario`). They can show the scenario prompt/options and citation mapping but never the keyed answer/explanation, and deepest Source disclosure must not record a scenario answer reveal. To attempt/reveal a scenario, use its real objective → Released scenarios practice branch.

The lens does not independently discover/fetch question-bank files or infer source membership from wording.

A shared citation is provenance evidence only. It does not create a semantic relationship between the cited items, and a citation does not imply the source is the sole authority unless Atlas explicitly says so.

## Coverage

`C` or **Coverage · N** opens a read-only corpus/practice-exposure projection. See `COVERAGE_LENS.md`.

Coverage consumes the same shared released-scenario registry as the main graph and reports raw explicit counts by domain/objective, including enriched subtopics, review/supplemental cards, released scenarios, sources, exact scenario-tagged subtopics, and exact-tag practice-exposure gaps.

Enter on the Coverage center opens a paged **Practice Exposure Gaps** view. A gap exists only when an enriched subtopic has no exact matching released scenario `subtopics` tag under its mapped objective. With the current released bank, **305/344** enriched subtopics have at least one exact released scenario tag and **39** are exact-tag gaps.

Those 39 records are corpus-exposure observations only. They are not curriculum omissions, factual deficiencies, learner weakness, mastery/readiness signals, or semantic relationships. Coverage performs no independent network fetch and does not read learner progress.

## Projection Search

Projection Search extends the existing `/` palette with exact Source Provenance, Coverage-domain, and Coverage-objective navigation entries. It routes into existing projection functions; it does not create curriculum edges or learner-state evidence.

The expanded search UI uses a combobox/listbox pattern with active-descendant state. Result options stay out of the Tab order; Tab/Shift+Tab remain contained between the search input and visible Close button while the palette is open. The visible Search button synchronously transfers focus into the input, and dismissing by Close or Escape restores focus to the opener when it still exists. Navigation through a selected search result clears the opener state so routed graph focus is preserved.

## Touch detail actions

Expanded detail panels provide persistent **Close / Depth / Open** controls:

- **Close** delegates to the same ascend/cleanup path as Escape and returns focus to the selected graph node;
- **Depth** cycles the same four disclosure layers as Space and preserves control focus across detail rerenders;
- **Open** delegates to the same descend path as Enter when the selected node has a deeper graph context.

These controls are review-layer affordances and do not change content relationships or learner-state semantics.

## Semantic relationship gate

Future typed relationships such as `depends-on`, `contrasts-with`, `implemented-by`, `mitigates`, `measured-by`, `evidenced-by`, and `practiced-by` require relationship-specific review.

`RELATIONSHIP_REVIEW.json` is a reviewer-only draft registry and currently contains **zero relationships**. `next.html` does not load it. See `RELATIONSHIP_REVIEW.md`.

Two items independently marked VERIFIED in Atlas semantic ledgers do not automatically have a verified relationship. Shared labels, search similarity, embeddings, shared `source_ids`, or coverage co-occurrence may at most identify a review lead; they cannot auto-approve an edge.

Relationship endpoints must use durable released IDs. Temporary UI/projection IDs such as `sub:<objective>:<index>`, `source:*`, `source-item:*`, `study:*`, `due:*`, `coverage:*`, pagers, and facets are forbidden as semantic endpoints. This includes `coverage:gap:<objective>:<index>` projection IDs. A provenance node such as `source-item:scenario:C-472` refers to a stable scenario for navigation only; a reviewed semantic edge would target `C-472` itself.

## Progressive disclosure

Each node exposes four depths:

1. **Orient** — identity, prompt/rule, labels.
2. **Understand** — explanation and decision context.
3. **Discriminate** — traps, misconceptions, contrasts, failure modes.
4. **Apply / verify** — sources and application/practice.

Space changes depth without losing graph position.

## Exact-head validation

The draft includes deterministic gates for each major layer:

- `audit.py` — released graph counts/mappings, manifest isolation, exact subtopic tags, answer boundary, learner-state compatibility;
- `due-audit.py` — complete 140-card review registry and Due Reviews;
- `study-audit.py` — Study Queue modes and production-compatible stage scoring;
- `source-audit.py` — 20-source registry, exact objective/card/scenario `source_ids`, shared-bank use, provenance/state/answer isolation;
- `coverage-audit.py` — Atlas count reconciliation, shared released-bank use, exact-tag exposure/gap recomputation, learner-state/semantic isolation;
- `projection-search-audit.py` — explicit projection routing, combobox/listbox semantics, touch controls, focus containment/restoration, no learner-state/semantic coupling;
- `relationship-audit.py` — stable endpoints, relationship-specific review requirements, and proof that reviewer-only relationship data is not learner-loaded.

Browser harnesses:

- `browser-smoke.html` + `browser-smoke.sh` — expanded graph, cards, learner state, Due Reviews, Study Queue, scenarios, search, Home, mobile;
- `source-browser-smoke.html` + `source-browser-smoke.sh` — source count, `S`, exact objective citation mapping, released-scenario provenance, answer-reveal isolation, Home, mobile;
- `coverage-browser-smoke.html` + `coverage-browser-smoke.sh` — shared-bank count equality, visible Coverage control, `C`, 39-gap traversal/detail boundaries, eight-domain coverage, D1/objective `1.1`, Escape hierarchy, mobile;
- `projection-search-smoke.html` + `projection-search-smoke.sh` — source/coverage projection routing, combobox state, modal focus containment/restoration, visible Search/Close, and persistent mobile detail controls.

`.github/workflows/secx-prototype-smoke.yml` runs the production CISSP deterministic audit/browser smoke, all SecX deterministic/syntax gates, and all prototype browser harnesses against one exact candidate head.

A browser PASS counts only when the committed gate actually executes against the exact candidate head. Static syntax checks are preflight evidence, not browser evidence.

## Production architecture rules

1. Preserve stable released IDs and explicit source/release scope.
2. Keep one manifest-enforced released-scenario loader and let read-only projections consume its shared runtime registry.
3. Keep unreleased question candidates out of learner-facing runtime.
4. Keep learner state separate from curriculum records.
5. Treat Due Reviews and Study Queue as learner-state projections, not curriculum edges.
6. Treat Source Provenance as an exact citation projection, not a semantic cross-link generator.
7. Treat Coverage counts and exact-tag gaps as corpus/practice-exposure projections, not learner scores, curriculum-deficiency claims, or semantic edge generators.
8. Keep relationship candidate discovery, relationship review, release, and runtime publication as separate stages.
9. Reject unknown IDs, invalid source references, temporary semantic endpoints, and reviewer-only relationship data in learner runtime.
10. Keep local graph mounting/pagination rather than rendering the entire corpus at once.
11. Require deterministic and browser gates before any production migration.

## Promotion boundary

`next.html` remains review-only. Do not replace `index.html`, merge to production, or claim browser validation until the exact candidate head passes the committed gates through a browser-capable runner.

## Naming note

The prototype uses the requested center label **SecX**. Public product naming/trademark review remains separate from interface implementation.
