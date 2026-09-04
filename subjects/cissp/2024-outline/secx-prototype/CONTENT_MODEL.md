# SecX content model

## Purpose

The SecX prototype is a graph view over the released CISSP Atlas curriculum, not a second curriculum. Stable Atlas IDs, source scope, release state, and explicit mappings remain authoritative.

## Hierarchy

Primary navigation remains:

`SecX → domain → objective → subtopic → concept → claim/card → example/trap/source/practice`

The current implemented review surfaces stop at explicit released mappings:

- domain → objective;
- objective → subtopic;
- objective → retrieval card;
- objective → released scenario;
- subtopic → released scenario only by exact explicit released subtopic tag;
- source → objective only by explicit objective `source_ids`;
- source → review card only by explicit card `source_ids`;
- source → released scenario only by explicit scenario `source_ids`.

Concept-level or cross-domain semantic edges remain gated until reviewed mappings exist.

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

Temporary navigation IDs such as `sub:<objective-id>:<index>`, pager IDs, study-lens IDs, due-review IDs, source-lens IDs, and `coverage:*` IDs are local UI identities only. They are not durable curriculum IDs and cannot become endpoints in a released semantic-relationship registry.

## Relationship types

Potential typed semantic edges include:

- `contains`
- `depends-on`
- `contrasts-with`
- `implemented-by`
- `mitigates`
- `measured-by`
- `evidenced-by`
- `practiced-by`

Only hierarchy and relationships already explicit in released Atlas data are currently publishable by the prototype. Search similarity is not relationship evidence.

Explicit `source_ids` provenance can be shown as a source projection because the citation mapping already exists in Atlas. A shared citation does **not** imply that the two cited items depend on, contrast with, implement, mitigate, measure, or otherwise semantically relate to one another.

Coverage counts and exact-tag practice-exposure counts are likewise projections over explicit released mappings. They do **not** create semantic relationships between objectives, cards, subtopics, scenarios, or domains.

`RELATIONSHIP_REVIEW.json` is a separate reviewer-only draft registry for future semantic edges. It is intentionally not loaded by `next.html`. Item-level VERIFIED status does not approve a relationship between two verified items. Relationship approval requires its own rationale/evidence/reviewer gate, and even approved records remain draft-only until a separate released-relationship artifact exists.

Schedule-derived views such as **Due Reviews** and **Study Queue** are not relationship types. They are temporary learner-state projections over already released review-card nodes and must never be serialized back into curriculum relationships.

## Shared released-scenario registry

`next-layer.js` is the single learner-runtime release boundary for standard scenarios. It loads only paths listed by `question-bank/RELEASED_BATCHES.json` and publishes:

- `SECX_RELEASED_QUESTIONS` — the current manifest-released standard scenario snapshot;
- `SECX_RELEASED_BANK_STATE` — readiness/error/count state;
- `secx:released-bank` — readiness/change event.

Read-only projections such as Source Provenance and Coverage consume this shared registry. They must not independently reload the manifest or discover question-bank files. This keeps scenario release inclusion consistent across the graph and prevents two projections from observing different bank states.

## Provenance projection

The **Source Provenance** lens uses the current Atlas source registry and exact `source_ids` arrays only.

It may display:

- all released Atlas source records;
- objectives that explicitly cite a selected source;
- production-compatible review cards that explicitly cite a selected source;
- manifest-released standard scenarios that explicitly cite a selected source;
- source title, role, and URL already present in Atlas metadata.

Scenario citation nodes in Source Provenance use a distinct `source-scenario` node kind. They may expose the released prompt/options and provenance, but they must not expose the keyed answer/explanation or record scenario-answer-reveal evidence. Answer/reveal behavior belongs only to the real released-scenario practice branch.

Source Provenance must not:

- infer a source mapping from text similarity;
- treat co-citation as a semantic concept edge;
- independently fetch/discover question-bank files;
- infer learner correctness/mastery/readiness from source traversal;
- imply that one cited source is the sole authority unless Atlas explicitly says so.

## Coverage projection

The **Coverage** lens reports raw corpus/practice-exposure counts from explicit released mappings. It does not produce a synthetic coverage score.

It may display, by domain/objective:

- objective count;
- enriched subtopic count;
- Atlas review-card count;
- supplemental reviewed-card count;
- released scenario count;
- source count;
- enriched subtopics with at least one exact released scenario `subtopics` tag;
- objectives with zero explicitly mapped released scenarios.

A missing scenario mapping is a **practice-exposure gap**, not proof of curriculum omission. Coverage metrics are corpus properties and are not learner mastery/readiness measurements.

Coverage consumes the shared released-scenario registry, must not independently load the manifest or discover candidate-only files, must not read/write learner state, and must not infer semantic edges from counts, tags, or shared sources.

## Progressive disclosure

Each node supports four stable disclosure depths:

1. **Orient** — identity, compact rule/prompt, high-value labels.
2. **Understand** — explanation, decision context, why it matters.
3. **Discriminate** — traps, misconceptions, contrasts, failure modes.
4. **Apply / verify** — source traceability and application/practice.

For released scenarios in the real practice branch, the keyed answer and explanation belong only to layer 4. The scenario stem/options must be visible before the answer so the graph remains retrieval-first.

## Local graph mounting

Do not render the entire knowledge base simultaneously. The view should mount a local cluster around the current node:

- parent/path;
- siblings;
- children;
- selected reviewed cross-links;
- paged card/scenario records where necessary;
- schedule-derived learner-state projections;
- paged source-provenance projections;
- local domain/objective coverage projections.

This preserves spatial legibility and keyboard traversal as the corpus grows.

## Learner state is not content

Learner history must remain outside curriculum records.

The expanded prototype currently uses two state scopes:

- Atlas-compatible review-card progress: `cissp_atlas_progress_v1`.
- Graph-specific activity: `cissp_secx_graph_state_v1`.

The shared card state intentionally uses Atlas's existing Wrong / Hard / Good / Easy stage schedule so the same released review-card ID does not acquire two incompatible review histories.

The production-compatible review-card registry contains the same 140 Atlas review cards: generated `OBJ-<objective-id>` cards plus released high-yield/AI/precision cards from loaded `CISSP_CHUNKS`. Due Reviews and Study Queue filter these released IDs using the existing Atlas card state; they do not discover files or create replacement card IDs.

Study Queue may derive:

- due;
- new;
- learning;
- mature;
- lowest current review-stage-score domain.

The lowest review-stage score uses the same objective/domain stage aggregation and higher-exam-weight tie-break as production Atlas. It is a study-priority signal only, not proof of weakness, mastery, or exam readiness.

Graph-specific state may record:

- visits;
- maximum disclosure depth reached;
- last-seen time;
- scenario answer-reveal exposure.

A scenario answer reveal is **not** correctness, an attempt result, mastery, readiness, or a spaced-repetition success grade. If scenario correctness is added later, it must be derived from an explicit committed answer attempt.

A due date is likewise only a scheduling fact. It is **not** a semantic claim that the card, objective, or domain is weak or unmastered.

Learner-state records must never rewrite:

- objective/source mappings;
- release state;
- scenario answer keys;
- semantic-review state;
- curriculum relationships.

## Search

Search may index released domains, objectives, subtopics, retrieval cards, and released scenarios. Search results may route the learner to an exact local graph context.

Search similarity may support discovery but must not create semantic graph edges automatically.

Future search filters can include node type, domain, objective, source, due-card state, coverage/exposure state, and explicitly released relationship type.

## Relationship review pipeline

Future semantic relationships are staged separately from learner runtime.

Current draft stages are:

1. candidate discovery/reviewer entry;
2. relationship-specific semantic review;
3. deterministic validation against stable released endpoint IDs and semantic item ledgers;
4. separate release/promotion artifact;
5. learner-runtime integration only after exact-head gates pass.

`RELATIONSHIP_REVIEW.json` currently has no relationships. Candidate or approved-draft records in that file are not learner-facing.

Automatic approval is forbidden from:

- repeated words or labels;
- fuzzy/string similarity;
- embeddings or semantic-distance scores;
- shared `source_ids`;
- coverage co-occurrence/counts;
- two endpoints independently being VERIFIED.

## Release isolation

Released scenarios must be loaded only through the released question-bank manifest by the central `next-layer.js` loader. Presence of a candidate file in the repository is not sufficient for learner-facing graph inclusion.

Released review-card learner-state views must derive from the Atlas-compatible 140-card registry, not repository file discovery.

Source Provenance must derive from `CISSP_META.sources`, exact released `source_ids`, and the shared released-scenario registry.

Coverage must derive from released objectives/subtopics/cards plus the shared released-scenario registry and exact scenario subtopic tags.

Reviewer-only semantic relationship data must not be loaded by learner runtime. A future learner-facing relationship layer requires a separate released artifact.

Before any graph surface becomes production-facing, deterministic validation must reject:

- unknown objective IDs;
- unknown source IDs;
- duplicate stable IDs;
- malformed release-manifest paths;
- unreleased scenario leakage;
- independent projection-specific scenario loaders that bypass the shared released bank;
- unsupported relationship targets/types;
- temporary navigation IDs used as semantic endpoints;
- relationship approval without explicit relationship review evidence;
- reviewer-only relationship data loaded by learner runtime;
- invalid learner-state/content coupling;
- answer exposure before the required retrieval boundary;
- source-provenance scenario nodes that expose answers or record false answer-reveal evidence;
- due/study inputs that are not Atlas-compatible review cards/state;
- source-provenance membership not backed by exact `source_ids`;
- coverage inputs not backed by released objective/subtopic/card/scenario mappings;
- coverage code coupled to learner state or inferred relationship logic.

## Keyboard grammar

- Arrow keys: spatial move.
- Enter: descend.
- Escape: close detail first, then ascend one hierarchy level while preserving parent context.
- Space: cycle disclosure depth.
- `/`: search.
- Home: root.
- `1–4`: grade a retrieval card when card detail is open.
- `R`: open the schedule-derived Due Reviews graph.
- `Q`: open Study Queue.
- `S`: open Source Provenance.
- `C`: open Coverage.
- Tab remains normal browser accessibility behavior.

Pointer/touch remains supported; keyboard-first must not become keyboard-only.
