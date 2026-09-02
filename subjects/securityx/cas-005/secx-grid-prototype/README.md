# SecX Keyboard Knowledge Grid — alternate SecurityX site

This is an isolated next-generation CompTIA SecurityX CAS-005 study interface. It reuses the existing audited `study-site/data/` corpus and does **not** replace that stable site yet.

## Core model

`SecX → domain → objective → subdomain → topic → card`

The visible interface is a deterministic grid so keyboard movement is predictable. The underlying content remains graph-friendly through stable card IDs, concept IDs, prerequisites, blueprint mappings, topic membership, tags, and sources.

## Keyboard controls

- **Arrow keys** — move one grid cell.
- **Enter** — descend one hierarchy level.
- **Escape** — ascend and restore the exact parent tile you came from.
- **Space** — reveal one deeper information layer.
- **Shift+Space** — move one information layer shallower.
- **M** — cycle local study state: Seen → Learning → Strong → Mastered.
- **R** — open exact related cards for the selected card.
- **Home** — return to the centered SecX root.
- **/** — search all cards by concept, objective, acronym, source, tag, or tool.

Progress is stored only in browser `localStorage`.

## Root layout

`SecX` is centered. The four public CAS-005 domains occupy the four cardinal directions:

- ↑ Governance, Risk, and Compliance — 20%
- → Security Architecture — 27%
- ↓ Security Engineering — 31%
- ← Security Operations — 22%

Entering the centered SecX tile opens the complete index, including the acronym reference and local progress views.

## Progressive depth

Hierarchy nodes use five layers: orientation, scope, coverage, representative retrieval prompts, and source families.

Cards retain the audited eight-layer model:

1. Direct answer
2. Concept expansion
3. Worked SecurityX scenario
4. Boundaries and misconceptions
5. Connections and memory
6. Transfer prompt
7. Mastery evidence
8. Sources

## Labels on every card

The alternate UI surfaces the exact metadata already attached to each card instead of collapsing it into a single domain label:

- card ID
- concept ID
- domain
- objective
- subdomain
- topic
- card type
- difficulty
- learning stage
- current local progress state
- mapped public-blueprint topics
- source IDs
- tags
- modalities

Additional semantic labels such as security property, control function/class, and decision context should be added only through an audited metadata migration rather than guessed automatically.

## Relationship grid

`R` opens relationships derived only from existing deterministic metadata:

- `PREREQUISITE` — explicit prerequisite card ID
- `SAME CONCEPT` — identical concept ID
- `SAME BLUEPRINT` — shared mapped public-blueprint item
- `SAME TOPIC` — identical domain/objective/subdomain/topic cluster

This preserves the user's desired knowledge-web behavior without making arrow navigation ambiguous.

## Data baseline

The alternate site consumes the existing SecurityX v4.1 audited corpus:

- 1,156 flashcards
- 8 layers per flashcard
- 23 numbered CAS-005 objectives
- 618 mapped public-blueprint examples
- 191 acronym cards

## Validation

`.github/workflows/securityx-secx-grid-audit.yml` runs:

1. JavaScript syntax validation.
2. A deterministic corpus/hierarchy audit proving all 1,156 cards remain intact and all numbered cards are reachable through the hierarchy.
3. A Playwright browser smoke test covering root keyboard movement, hierarchy navigation, parent restoration, depth controls, search jump, progress state, and relationship navigation.

The current implementation entry point is `app-v2.js`. `app.js` is retained temporarily as the first prototype for comparison during review.
