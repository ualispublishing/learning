# SecX keyboard knowledge-web prototype

This is an isolated review prototype. It does not replace or alter the verified CISSP Atlas v1.28 production site.

## Review surfaces

- `index.html` is the conservative objective/subtopic prototype.
- `next.html` is the expanded review surface. It embeds `index.html`, then loads the Atlas-compatible review-card registry, card/scenario graph layer, learner state, Due Reviews, Study Queue, and Source Provenance in dependency order.

The expanded surface is still review-only and is not the default prototype entry point or production Atlas.

## Released-data boundaries

The prototype reuses released Atlas data rather than creating a second curriculum:

- **62** stable objectives from released domain chunks;
- **344** enriched subtopic mappings from `coverage-detail.js`;
- **140** Atlas-compatible review cards: generated `OBJ-<objective-id>` cards plus released high-yield/AI/precision cards;
- released standard scenarios loaded only through `question-bank/RELEASED_BATCHES.json`;
- **20** released source records from `CISSP_META.sources`.

Candidate scenario files that are not in the released manifest remain excluded.

Current explicit mappings are:

- domain → objective;
- objective → subtopic;
- objective → retrieval card;
- objective → released scenario;
- subtopic → released scenario only by exact explicit released subtopic tag;
- source → objective/review card only by exact `source_ids` membership.

No concept-level cross-domain semantic relationship is inferred from text similarity or co-citation.

## Keyboard grammar

- Arrow keys: spatial traversal.
- Enter: descend.
- Escape: close detail first, then ascend while preserving local context.
- Space: cycle four disclosure depths.
- `/`: search released domains/objectives/subtopics/cards/scenarios.
- Home: return to SecX root.
- `1–4`: grade an open review card using Atlas Wrong / Hard / Good / Easy semantics.
- `R`: open **Due Reviews**.
- `Q`: open **Study Queue**.
- `S`: open **Source Provenance**.

Pointer/touch remains supported, actual browser focus follows keyboard selection, and `prefers-reduced-motion` is respected.

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

For a selected source, the lens exposes:

- objectives whose released `source_ids` contain the exact source ID;
- Atlas-compatible review cards whose released `source_ids` contain the exact source ID.

The lens does not read/write learner state, discover question-bank files, or infer source membership from wording.

A shared citation is provenance evidence only. It does not create a semantic relationship between the cited items, and a citation does not imply the source is the sole authority unless Atlas explicitly says so.

## Semantic relationship gate

Future typed relationships such as `depends-on`, `contrasts-with`, `implemented-by`, `mitigates`, `measured-by`, `evidenced-by`, and `practiced-by` require relationship-specific review.

`RELATIONSHIP_REVIEW.json` is a reviewer-only draft registry and currently contains **zero relationships**. `next.html` does not load it. See `RELATIONSHIP_REVIEW.md`.

Two items independently marked VERIFIED in Atlas semantic ledgers do not automatically have a verified relationship. Shared labels, search similarity, embeddings, or shared `source_ids` may at most identify a review lead; they cannot auto-approve an edge.

Relationship endpoints must use durable released IDs. Temporary UI IDs such as `sub:<objective>:<index>`, source/study/due nodes, pagers, and facets are forbidden as semantic endpoints.

## Progressive disclosure

Each node exposes four depths:

1. **Orient** — identity, prompt/rule, labels.
2. **Understand** — explanation and decision context.
3. **Discriminate** — traps, misconceptions, contrasts, failure modes.
4. **Apply / verify** — sources and application/practice.

Space changes depth without losing graph position.

## Exact-head validation

The draft now includes deterministic gates for each major layer:

- `audit.py` — released graph counts/mappings, manifest isolation, exact subtopic tags, answer boundary, learner-state compatibility;
- `due-audit.py` — complete 140-card review registry and Due Reviews;
- `study-audit.py` — Study Queue modes and production-compatible stage scoring;
- `source-audit.py` — 20-source registry, exact `source_ids` mappings, provenance/state isolation;
- `relationship-audit.py` — stable endpoints, relationship-specific review requirements, and proof that reviewer-only relationship data is not learner-loaded.

Browser harnesses:

- `browser-smoke.html` + `browser-smoke.sh` — expanded graph, cards, learner state, Due Reviews, Study Queue, scenarios, search, Home, mobile;
- `source-browser-smoke.html` + `source-browser-smoke.sh` — source count, `S` routing, `ISC2_OUTLINE`, exact objective citation mapping, Escape hierarchy, mobile header/layout.

`.github/workflows/secx-prototype-smoke.yml` is prepared to run the production CISSP deterministic audit and browser smoke, all SecX deterministic/syntax gates, the expanded SecX smoke, and the Source Provenance smoke against one candidate head.

A browser PASS counts only when the committed gate actually executes against the exact candidate head. Static syntax checks are preflight evidence, not browser evidence.

## Production architecture rules

1. Preserve stable released IDs and explicit source/release scope.
2. Keep unreleased question candidates out of learner-facing runtime.
3. Keep learner state separate from curriculum records.
4. Treat Due Reviews and Study Queue as learner-state projections, not curriculum edges.
5. Treat Source Provenance as an exact citation projection, not a semantic cross-link generator.
6. Keep relationship candidate discovery, relationship review, release, and runtime publication as separate stages.
7. Reject unknown IDs, invalid source references, temporary semantic endpoints, and reviewer-only relationship data in learner runtime.
8. Keep local graph mounting/pagination rather than rendering the entire corpus at once.
9. Require deterministic and browser gates before any production migration.

## Promotion boundary

`next.html` remains review-only. Do not replace `index.html`, merge to production, or claim browser validation until the exact candidate head passes the committed gates through a browser-capable runner.

## Naming note

The prototype uses the requested center label **SecX**. Public product naming/trademark review remains separate from interface implementation.
