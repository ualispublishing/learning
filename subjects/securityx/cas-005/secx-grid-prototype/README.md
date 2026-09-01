# SecX Keyboard Knowledge Grid — review prototype

This is an isolated prototype for a next-generation CompTIA SecurityX CAS-005 study interface. It does **not** modify or replace the existing audited `study-site/`.

## Core interaction

- **Home/start:** `SecX` is centered with the four current SecurityX domains on the four arrow directions.
- **Arrow keys:** move one deterministic grid position.
- **Enter:** descend one hierarchy level.
- **Escape:** ascend one hierarchy level.
- **Space:** deepen the currently selected node without navigating away.
- **Home:** return to the SecX root.
- **/**: search all cards and jump to their hierarchy location.

## Hierarchy

`SecX → domain → objective → subdomain → topic → card`

The central `SecX` node can also be entered to open a complete index, which includes the official acronym-support deck. Acronyms are then grouped alphabetically.

## Progressive depth

For hierarchy nodes, Space cycles through:

0. Orientation/basic label
1. Scope/rule
2. Child concepts
3. Representative retrieval prompts
4. Supporting source families

For flashcards, Space uses the existing audited eight-layer model:

1. Direct answer
2. Concept expansion
3. Worked SecurityX scenario
4. Boundaries and misconceptions
5. Connections and memory
6. Transfer prompt
7. Mastery evidence
8. Sources

## Labels / future graph layer

The visual interface is deliberately a grid so keyboard movement is predictable, but the underlying data remains graph-friendly. Cards retain stable IDs plus domain, objective, subdomain, topic, card type, difficulty, stage, prerequisites, source IDs, tags, modalities, blueprint mappings, and concept IDs. Cross-domain relationships can therefore be added later without changing arrow-key navigation.

Recommended additional semantic labels for the production migration:

- security property / objective (confidentiality, integrity, availability, authenticity, accountability, privacy, resilience)
- control function (preventive, detective, corrective, compensating, deterrent, recovery)
- control class (administrative, technical, physical)
- decision context (architecture, governance, incident response, IAM, cloud, software, cryptography, network, endpoint, third-party)
- relationship type (`prerequisite_of`, `contrasts_with`, `implements`, `detects`, `mitigates`, `depends_on`, `evidence_for`)
- source scope (`direct_blueprint`, `primary_standard`, `supporting_standard`, `terminology_reference`)
- semantic-review state/date

Those richer labels should be added through an audited migration rather than guessed automatically.

## Data

The prototype consumes the existing audited SecurityX v4.1 deck from `../study-site/data/` at runtime. Expected baseline:

- 1,156 flashcards
- 8 layers per flashcard
- 23 numbered CAS-005 objectives
- 618 mapped public-blueprint examples
- 191 acronym cards

Serve the repository with a normal static HTTP server; the prototype dynamically loads the existing data chunks and `blueprint_index.json`.
