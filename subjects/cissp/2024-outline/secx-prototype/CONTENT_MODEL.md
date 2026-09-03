# SecX content model — prototype

## Goal
Every learner-facing card, claim, objective, scenario, and concept should be addressable as a node in one knowledge graph. The visual web, search/filtering, source traceability, practice generation, and progress model should all use the same labels rather than separate ad-hoc taxonomies.

## Required labels per card/claim
Each item should carry these labels where applicable:

- `domain`: CISSP domain number and name.
- `objective`: numbered ISC2 objective, e.g. `7.6`.
- `subdomains`: one or more enriched subtopics under that objective.
- `concepts`: normalized concept names, e.g. `containment`, `RTO`, `least privilege`.
- `concept_type`: definition, principle, process, model, control, protocol, metric, role, attack, lifecycle, decision rule, etc.
- `control_function`: preventive, detective, corrective, deterrent, compensating, recovery, directive, or `not-applicable`.
- `security_properties`: CIA plus authenticity, accountability, nonrepudiation, privacy, safety, etc. when materially relevant.
- `decision_context`: governance, architecture, operations, incident response, IAM, assessment, SDLC, BCP/DR, legal/privacy, third-party, etc.
- `source_ids`: exact registered sources supporting the claim.
- `source_scope`: direct-scope, primary technical authority, supporting context, or illustrative only.
- `difficulty`: Foundation / Exam-calibrated / Stretch / Bellringer where applicable.
- `relationships`: prerequisites, contrasts-with, part-of, implemented-by, measured-by, mitigates, depends-on, example-of.
- `aliases`: useful alternate names/acronyms for search.
- `review`: semantic-review state and date.

## Current implemented hierarchy
The review prototype now consumes released Atlas data for the first three levels:

`SecX → Domain → Objective → Enriched subtopic`

- Domain and objective records come from the released `data-meta.js` and `data-d1.js` … `data-d8.js` files.
- Enriched subtopic labels come from the released `coverage-detail.js` mapping keyed by objective ID.
- The prototype currently exposes 62 stable objective IDs and 344 enriched subtopic mappings.
- Subtopic node IDs in the prototype are deterministic local navigation IDs of the form `sub:<objective-id>:<index>`; they are not yet canonical curriculum IDs and must not be treated as durable public identifiers until a graph migration assigns explicit stable IDs.
- Objective summaries, direct rules, traps, and source IDs remain sourced from the released Atlas objective records rather than being rewritten in the graph layer.

No concept/card/scenario relationship is inferred merely from a matching word or label. Those deeper edges require explicit mapping and audit before they become part of the canonical graph.

## Example
```json
{
  "id": "PX-028",
  "title": "Volatile evidence first",
  "claim": "Volatile evidence can disappear rapidly, so authorized live collection normally prioritizes the most perishable relevant evidence while minimizing alteration.",
  "labels": {
    "domain": ["D7 Security Operations"],
    "objective": ["7.1"],
    "subdomains": ["evidence collection and handling", "digital forensics"],
    "concepts": ["order of volatility", "volatile evidence", "forensic preservation"],
    "concept_type": ["decision rule", "forensics principle"],
    "control_function": ["not-applicable"],
    "security_properties": ["integrity", "accountability"],
    "decision_context": ["incident response", "investigation", "forensics"],
    "source_ids": ["ISC2_OUTLINE", "NIST_800_86"],
    "source_scope": ["direct-scope", "primary technical authority"],
    "difficulty": ["Exam-calibrated"],
    "aliases": ["order of volatility"],
    "review": ["SEMANTIC_REVIEWED"]
  },
  "relationships": [
    {"type":"part-of","target":"7.1"},
    {"type":"depends-on","target":"chain-of-custody"},
    {"type":"contrasts-with","target":"static-media-collection"}
  ]
}
```

## Progressive depth layers
The same node should expose four progressively deeper layers.

1. **Orient** — name, one-line rule, core labels.
2. **Understand** — explanation, why it matters, key distinctions.
3. **Discriminate** — traps, counterexamples, contrasts, common exam errors.
4. **Apply / verify** — source traceability, related nodes, scenario prompt, practice links.

Space cycles these layers without losing the user's location in the graph.

## Navigation hierarchy
The graph is hierarchical but not restricted to a tree:

`SecX → Domain → Objective → Subtopic → Concept → Claim/Card → Example/Trap/Source/Practice`

Cross-links may connect concepts across domains. Examples: `least privilege` connects governance, architecture, IAM, operations, and software security; `risk ownership` connects governance, third-party risk, vulnerability management, exceptions, and incident decisions.

Typed cross-links must be explicitly mapped. Exact or fuzzy text similarity may be used to propose candidates for review, but it is not sufficient to publish a semantic relationship.

## Search model
The implemented prototype search palette indexes released domain names, objective IDs/labels/summaries/traps, and enriched subtopic labels. Search results reconstruct the appropriate local graph and focus the selected node.

Future concept/card/scenario search should use canonical IDs and aliases after those deeper graph layers are explicitly normalized.

## Keyboard grammar
- Arrow keys: spatially select the connected node best aligned to the requested direction.
- Enter: descend into the selected node's child cluster.
- Escape: close detail depth first, then ascend one hierarchy level while preserving the parent selection.
- Space: cycle depth 1→2→3→4→1.
- `/`: open global search/palette.
- `Home`: return to SecX root.
- `Tab`: remain available for normal browser accessibility instead of being hijacked.

## Design rule
A user should always know three things without opening another page: **where they are, what this node means, and what directions are available next.**
