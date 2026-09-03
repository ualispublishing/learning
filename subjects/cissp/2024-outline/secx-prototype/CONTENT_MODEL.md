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
- subtopic → released scenario only by exact explicit released subtopic tag.

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

## Relationship types

Potential typed edges include:

- `contains`
- `depends-on`
- `contrasts-with`
- `implemented-by`
- `mitigates`
- `measured-by`
- `evidenced-by`
- `practiced-by`

Only `contains`-style hierarchy and explicitly represented Atlas mappings are currently publishable by the prototype. Other semantic relationship types require explicit reviewed mappings. Search similarity is not relationship evidence.

## Progressive disclosure

Each node supports four stable disclosure depths:

1. **Orient** — identity, compact rule/prompt, high-value labels.
2. **Understand** — explanation, decision context, why it matters.
3. **Discriminate** — traps, misconceptions, contrasts, failure modes.
4. **Apply / verify** — source traceability and application/practice.

For released scenarios, the keyed answer and explanation belong only to layer 4. The scenario stem/options must be visible before the answer so the graph remains retrieval-first.

## Local graph mounting

Do not render the entire knowledge base simultaneously. The view should mount a local cluster around the current node:

- parent/path;
- siblings;
- children;
- selected reviewed cross-links;
- paged card/scenario records where necessary.

This preserves spatial legibility and keyboard traversal as the corpus grows.

## Learner state is not content

Learner history must remain outside curriculum records.

The expanded prototype currently uses two state scopes:

- Atlas-compatible retrieval-card progress: `cissp_atlas_progress_v1`.
- Graph-specific activity: `cissp_secx_graph_state_v1`.

The shared card state intentionally uses Atlas's existing Wrong / Hard / Good / Easy stage schedule so the same released retrieval-card ID does not acquire two incompatible review histories.

Graph-specific state may record:

- visits;
- maximum disclosure depth reached;
- last-seen time;
- scenario answer-reveal exposure.

A scenario answer reveal is **not** correctness, an attempt result, mastery, readiness, or a spaced-repetition success grade. If scenario correctness is added later, it must be derived from an explicit committed answer attempt.

Learner-state records must never rewrite:

- objective/source mappings;
- release state;
- scenario answer keys;
- semantic-review state;
- curriculum relationships.

## Search

Search may index released domains, objectives, subtopics, retrieval cards, and released scenarios. Search results may route the learner to an exact local graph context.

Search similarity may support discovery but must not create semantic graph edges automatically.

Future search filters can include node type, domain, objective, source, due-card state, and explicitly reviewed relationship type.

## Release isolation

Released scenarios must be loaded only through the released question-bank manifest. Presence of a candidate file in the repository is not sufficient for learner-facing graph inclusion.

Before any graph surface becomes production-facing, deterministic validation must reject:

- unknown objective IDs;
- unknown source IDs;
- duplicate stable IDs;
- malformed release-manifest paths;
- unreleased scenario leakage;
- unsupported relationship targets;
- invalid learner-state/content coupling;
- answer exposure before the required retrieval boundary.

## Keyboard grammar

- Arrow keys: spatial move.
- Enter: descend.
- Escape: close detail first, then ascend one hierarchy level while preserving parent context.
- Space: cycle disclosure depth.
- `/`: search.
- Home: root.
- `1–4`: grade a retrieval card when card detail is open.
- Tab remains normal browser accessibility behavior.

Pointer/touch remains supported; keyboard-first must not become keyboard-only.
