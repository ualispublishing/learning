# SecX content model

## Purpose

The SecX prototype is a graph view over the released CISSP Atlas curriculum, not a second curriculum. Stable Atlas IDs, source scope, release state, explicit mappings, and relationship-specific review remain authoritative.

## Hierarchy and current graph edges

Primary navigation remains:

`SecX → domain → objective → subtopic → concept → claim/card → example/trap/source/practice`

The current review surfaces expose these released or explicitly reviewed mappings:

- domain → objective;
- objective → subtopic;
- objective → retrieval card;
- objective → released scenario;
- subtopic → released scenario only by exact explicit released subtopic tag;
- source → objective only by explicit objective `source_ids`;
- source → review card only by explicit card `source_ids`;
- source → released scenario only by explicit scenario `source_ids`;
- relationship → stable released endpoint only when that relationship has passed the separate semantic-review and prototype-promotion pipeline.

Three cross-domain semantic relationships are currently prototype-released: `REL-001`, `REL-002`, and `REL-003`. No additional concept-level or cross-domain edge may be inferred automatically.

## Node identity

Preserve existing stable IDs whenever Atlas already supplies them. Do not generate replacement IDs for objectives, retrieval cards, or released scenarios merely to fit a graph library.

A normalized graph node may carry:

- `id`
- `node_type`
- `domain`
- `objective`
- `subtopic`
- `concept`
- `concept_type`
- `control_function`
- `security_properties`
- `decision_context`
- `source_ids`
- `source_scope`
- `difficulty`
- `relationships`
- `aliases`
- `semantic_review_state`
- `release_state`

Not every node needs every field. Unknown values should stay unknown rather than being inferred for visual completeness.

Temporary navigation IDs such as `sub:<objective-id>:<index>`, pager IDs, study-lens IDs, due-review IDs, source-lens IDs, `coverage:*` IDs, and `relationship:*` UI IDs are local interface identities only. They are not durable curriculum IDs and cannot become endpoints in a released semantic-relationship registry.

## Relationship types

Supported reviewed semantic edge types are:

- `depends-on`
- `contrasts-with`
- `implemented-by`
- `mitigates`
- `measured-by`
- `evidenced-by`
- `practiced-by`

Hierarchy/containment remains represented by the existing explicit Atlas graph and is not duplicated as a relationship-review record.

Search similarity is not relationship evidence. Shared `source_ids`, repeated terminology, embeddings, coverage co-occurrence, or two independently VERIFIED endpoints may surface a review lead but cannot create or approve an edge.

`RELATIONSHIP_REVIEW.json` is the separate reviewer-only semantic registry. It is intentionally never loaded by `next.html`.

Prototype publication is a separate stage:

- `RELEASED_RELATIONSHIPS.json` contains only relationships that passed relationship-specific review and promotion;
- `released-relationships.js` is the frozen learner-runtime copy;
- `relationship-release-audit.py` verifies exact reviewer-to-release/runtime integrity and reviewer-registry isolation;
- `relationship-lens.js` exposes only the released copy through the review-only **Links** lens.

The current prototype-released relationships are:

- `REL-001`: `5.1 depends-on 1.8`;
- `REL-002`: `7.6 evidenced-by 7.2`;
- `REL-003`: `7.10 depends-on 1.7`.

These supplement rather than replace the hierarchy. Prototype publication does not imply production Atlas publication.

Schedule-derived views such as **Due Reviews** and **Study Queue** are not relationship types. They are temporary learner-state projections over already released review-card nodes and must never be serialized back into curriculum relationships.

## Shared released-scenario registry

`next-layer.js` is the single learner-runtime release boundary for standard scenarios. It loads only paths listed by `question-bank/RELEASED_BATCHES.json` and publishes:

- `SECX_RELEASED_QUESTIONS` — the current manifest-released standard scenario snapshot;
- `SECX_RELEASED_BANK_STATE` — readiness/error/count state;
- `secx:released-bank` — readiness/change event.

Read-only projections such as Source Provenance and Coverage consume this shared registry. They must not independently reload the manifest or discover question-bank files.

## Provenance projection

The **Source Provenance** lens uses the current Atlas source registry and exact `source_ids` arrays only.

It may display released sources and the objectives, review cards, and manifest-released standard scenarios that explicitly cite them. Scenario citation nodes are provenance-only and may show prompt/options but must not expose keyed answers or record scenario-answer-reveal or scenario-attempt evidence.

Source Provenance must not infer source membership from wording, treat co-citation as a semantic relationship, independently fetch question-bank candidates, or infer learner mastery/readiness.

## Coverage projection

The **Coverage** lens reports raw corpus/practice-exposure counts from explicit released mappings. It does not produce a synthetic coverage score.

It may display objective/subtopic/card/scenario/source counts, exact scenario-tag exposure, exact-tag practice-exposure gaps, and objectives with zero explicitly mapped released scenarios.

A practice-exposure gap exists only when an enriched subtopic mapped to objective O has no exact equal label in the `subtopics` array of any manifest-released scenario mapped to O. With the current released bank, **305/344** enriched subtopics have at least one exact released scenario tag and **39** are exact-tag gaps.

Those gaps are corpus-exposure observations, not curriculum omissions, factual deficiencies, learner weakness, mastery/readiness signals, or semantic relationships.

## Progressive disclosure

Each node supports four stable disclosure depths:

1. **Orient** — identity, compact rule/prompt, high-value labels.
2. **Understand** — explanation, decision context, why it matters.
3. **Discriminate** — traps, misconceptions, contrasts, failure modes.
4. **Apply / verify** — source traceability and application/practice.

For released scenarios in the real practice branch, the keyed answer and explanation belong only to layer 4. The scenario stem/options must be visible before the answer so the graph remains retrieval-first.

A scenario choice may be explicitly committed before layer 4, but commitment stores only the selected option and attempt timestamp. Correctness is finalized only when layer 4 is deliberately revealed. Revealing layer 4 without a pending commitment records exposure only and does not create a scored attempt.

For released semantic relationships, detail explains the reviewed relationship rationale and evidence, while endpoint traversal returns to the normal released objective/card/scenario context rather than duplicating curriculum nodes.

## Local graph mounting

Do not render the entire knowledge base simultaneously. The view should mount a local cluster around the current node:

- parent/path;
- siblings;
- children;
- selected reviewed and prototype-released cross-links;
- paged card/scenario records where necessary;
- schedule-derived learner-state projections;
- paged source-provenance projections;
- local domain/objective coverage projections;
- paged exact-tag coverage-gap projections.

This preserves spatial legibility and keyboard traversal as the corpus grows.

## Learner state is not content

Learner history must remain outside curriculum records.

The expanded prototype uses two state scopes:

- Atlas-compatible review-card progress: `cissp_atlas_progress_v1`.
- Graph-specific activity: `cissp_secx_graph_state_v1`.

The shared card state uses Atlas's existing Wrong / Hard / Good / Easy stage schedule so the same released review-card ID does not acquire two incompatible review histories.

The production-compatible review-card registry contains the same 140 Atlas review cards. Due Reviews and Study Queue filter those released IDs using existing Atlas card state; they do not discover files or create replacement card IDs.

Graph-specific state may record visits, maximum disclosure depth, last-seen time, scenario answer-reveal exposure, explicit scenario commitments, scored-attempt counts, correct-attempt counts, and the last scenario outcome. Relationship traversal may record graph visit/depth evidence only; it must not mutate Atlas mastery/progress state.

A scenario answer reveal by itself is not correctness, an attempt result, mastery, readiness, or a spaced-repetition success grade. A committed scenario choice may be scored correct/incorrect at layer 4, but that outcome is scoped only to that explicit scenario attempt and must not be promoted automatically into objective/domain/certification mastery or Atlas card scheduling. A due date is likewise only a scheduling fact.

Learner-state records must never rewrite objective/source mappings, release state, scenario answer keys, semantic-review state, or curriculum relationships.

## Search and accessibility projections

Search may index released domains, objectives, subtopics, retrieval cards, released scenarios, sources, Coverage domain/objective projections, and the exact IDs/content of prototype-released semantic relationships from `window.SECX_RELEASED_RELATIONSHIPS`. Search results may route the learner to an exact local graph context.

Reviewed-link search is a navigation projection only. It is populated only after the released relationship runtime signals readiness and routes by stable `REL-*` ID into the existing relationship hub. It never reads `RELATIONSHIP_REVIEW.json` or raw `RELEASED_RELATIONSHIPS.json`, never discovers candidate relationships, and never promotes search similarity into a semantic edge.

Search similarity may support discovery of already indexed content, but it must not create semantic graph edges automatically. Only explicitly prototype-released relationship IDs may appear as relationship search results.

The expanded search palette follows a combobox/listbox interaction model. Search result options use active-descendant state; Tab and Shift+Tab are contained within the dialog controls. Visible Search/Close, detail Close/Depth/Open, and scenario option/Commit controls preserve equivalent pointer/touch access without creating alternate content or state models.

## Relationship review and promotion pipeline

Semantic relationships are staged separately from learner runtime:

1. candidate discovery/reviewer entry;
2. relationship-specific semantic review;
3. deterministic validation against stable released endpoint IDs and semantic item ledgers;
4. separate release/promotion artifact;
5. exact runtime-copy audit;
6. learner-runtime integration only after exact-head deterministic and browser gates pass;
7. any future production migration remains a separate decision and gate.

`RELATIONSHIP_REVIEW.json` currently contains three `approved` / draft-stage reviewer records. The learner runtime does not load that file. `RELEASED_RELATIONSHIPS.json` separately contains the three promoted copies for `scope: secx-review-prototype`, and `released-relationships.js` supplies the audited runtime representation.

Automatic approval is forbidden from repeated words/labels, fuzzy/string similarity, embeddings, shared `source_ids`, coverage co-occurrence/counts/gaps, or two endpoints independently being VERIFIED.

## Release isolation

Released scenarios are loaded only through the question-bank release manifest by `next-layer.js`. Presence of a candidate file in the repository is not sufficient for learner-facing inclusion.

Released review-card learner-state views derive from the Atlas-compatible 140-card registry, not repository file discovery.

Source Provenance derives from `CISSP_META.sources`, exact released `source_ids`, and the shared released-scenario registry. Coverage derives from released objectives/subtopics/cards plus the shared scenario registry and exact scenario subtopic tags.

Reviewer-only semantic relationship data must never be loaded by learner runtime. Learner-facing prototype relationships and their search projection must come only from the separate audited released artifact/runtime copy.

Before any graph surface becomes production-facing, deterministic validation must reject unknown IDs, malformed release inputs, unreleased scenario leakage, invalid scenario answer keys/options, scenario correctness without prior explicit commitment, unsupported relationship targets/types, temporary UI IDs used as semantic endpoints, relationship approval without explicit evidence, reviewer-registry loading, released-relationship/runtime-copy drift, invalid learner-state/content coupling, premature answer exposure, provenance answer leakage, and projection logic that invents semantic edges.

## Keyboard grammar

- Arrow keys: spatial move.
- Enter: descend.
- Escape: close detail first, then ascend one hierarchy level while preserving parent context.
- Space: cycle disclosure depth.
- `/`: search.
- Home: root.
- `1–4`: grade a retrieval card when card detail is open.
- `R`: open Due Reviews.
- `Q`: open Study Queue.
- `S`: open Source Provenance.
- `C`: open Coverage.
- `L`: open reviewed/prototype-released semantic Links.
- Tab remains normal browser accessibility behavior outside the open search modal; inside search, Tab/Shift+Tab are contained within the dialog controls.

Pointer/touch remains supported; keyboard-first must not become keyboard-only.
