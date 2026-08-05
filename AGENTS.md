# Agent Operating Manual — Learning Repository

This repository is the source of truth for the user's long-term self-study system. Agents must preserve its taxonomy, progression state, flashcard quality, and playlist quality rather than treating each conversation as an isolated recommendation task.

## 1. Repository model

Two independent structures are maintained:

- `subjects/` = what the knowledge is.
- `playlists/` = how the user consumes the learning material.

Never store subject knowledge according to its YouTube channel. Never store playlist state inside a flashcard deck.

### Subject path

Use the smallest meaningful hierarchy:

`subjects/<subject>/<track>/<module>/`

Example:

`subjects/mats/mechanics-of-materials/poissons-ratio/`

Add extra nesting only when it represents a stable curricular distinction. Avoid redundant folders such as `mats/materials/materials-science/...`.

### Playlist path

Use:

`playlists/<medium>/<subject>/<track-name>/playlist.json`

Current audio-led tracks belong under `playlists/audio/`. A YouTube video may still be classified as audio-led if its narration carries most of the instructional value. Store `visual_dependency` separately so agents can flag lessons where diagrams deserve screen attention.

## 2. Progress protocol

`progress/current.json` is the machine-readable current state. `NEXT.md` is the human-readable pointer.

When the user says a lesson is finished:

1. Read the active playlist from the repo.
2. Mark that item `completed`.
3. Change the next prerequisite-appropriate item to `next`.
4. Update `progress/current.json`.
5. Update `NEXT.md`.
6. Extract the completed lesson's main ideas.
7. Add only new or meaningfully deepened flashcards to the correct subject module.
8. Do not duplicate cards merely because the same concept appears in another source.

If multiple videos reinforce one concept, attach multiple source IDs to the same canonical card or deepen its higher layers.

## 3. Flashcard generation standard

Cards are retrieval tools, not miniature textbook chapters.

### Selection rule

Generate cards only for concepts that satisfy at least one of these:

- foundational vocabulary required to understand later concepts;
- a core causal relationship or mechanism;
- a formula whose meaning and use matter;
- a common conceptual distinction or misconception;
- a transferable principle used in problem solving;
- an important boundary/assumption that prevents misuse.

Do not create standalone cards for incidental wording, examples, names, numbers, or facts that can be reconstructed from a core concept.

### Atomicity

Each card should test one retrievable idea. If answering the front correctly requires several unrelated lists or concepts, split the card. Closely coupled relationships may remain together when separating them would damage understanding.

### Canonical layered back

Every Knowledge Atlas card should support these layers:

1. **Direct Answer** — shortest correct answer; must stand alone.
2. **Concept Expansion** — mechanism, meaning, or deeper explanation.
3. **Worked / Physical Example** — concrete application, preferably intuitive before numerical.
4. **Boundaries and Misconceptions** — assumptions, nearby confusions, failure cases.
5. **Connections and Memory** — prerequisites, downstream concepts, useful cue/analogy.
6. **Transfer Prompt** — a new situation requiring application rather than repetition.
7. **Mastery Evidence** — what the learner should be able to do without notes.
8. **Sources** — stable source IDs, not unsupported prose claims.

The first layer must remain concise enough for rapid spaced-repetition review. Deeper layers should not be required every review.

### Knowledge vs practice cards

Keep two classes distinct:

- `knowledge.json`: concepts, definitions, relationships, mechanisms, equations, distinctions.
- `practice.json`: worked reasoning, calculations, diagram interpretation, derivations, scenario application.

Do not overload conceptual cards with long calculations merely to make them look comprehensive.

### Difficulty and prerequisites

Difficulty should reflect retrieval/reasoning complexity, not how important a concept is.

Prerequisites must form a useful learning graph. Do not make every earlier card a prerequisite. Include only concepts that are genuinely needed to understand the target card.

### Mastery scale

Use a 0–4 model when recording mastery:

- 0 — blank/incorrect.
- 1 — partial recognition or major omissions.
- 2 — correct core answer but fragile, prompted, or unable to apply.
- 3 — correct, independently explained, and applied to a nearby case.
- 4 — flexible understanding: can transfer, contrast, explain assumptions, or teach it.

### Deduplication

Before adding a card, search existing cards by concept ID, title, synonyms, and semantic meaning. Prefer updating a canonical card's sources or deeper layers over creating a duplicate.

## 4. Playlist research methodology

A playlist is a curriculum, not a list of popular videos.

### Step A — define the coverage map

Before selecting videos, list the knowledge areas a competent learner should cover. For technical subjects this should normally include foundations, mechanisms, mathematical/analytical tools, applications, common failure modes/misconceptions, and bridges to advanced study.

### Step B — build prerequisite ordering

Create a prerequisite graph. Order lessons so later items depend primarily on already-covered concepts. Do not blindly copy channel upload order or a platform playlist if a better pedagogical order is available.

### Step C — source search

For every curriculum region, search multiple high-quality sources. Prefer:

1. university/open-course lectures and authoritative educational institutions;
2. specialist educators with a strong teaching record;
3. professional societies/research institutions;
4. high-quality expert podcasts/interviews for synthesis and context.

Use community recommendations only as discovery signals, not sole evidence of correctness.

### Step D — audio suitability

Because these are primarily audio learning tracks, score each item separately for:

- explanation clarity without looking at the screen;
- density of diagrams/equations;
- dependence on animation;
- whether the video still makes sense while walking/driving/etc.

Store `visual_dependency` as one of:

- `none`
- `helpful`
- `periodic`
- `high`

Do not reject an excellent lesson solely because visuals are helpful; instead flag it.

### Step E — coverage and redundancy audit

Before finalizing a track, ask:

- Is any foundational concept missing?
- Is an advanced lesson introduced before its prerequisites?
- Are two lessons substantially redundant?
- Does a second explanation add a useful perspective or merely repeat?
- Are there enough application/synthesis lessons after foundations?
- Does the track create a bridge to the next learning level?

Prefer the shortest sequence that still provides comprehensive conceptual coverage. Extra material should be marked optional/deepening rather than silently extending the required core.

### Step F — verify exact media

Record exact title, channel/author, canonical URL, source page if available, and ordering rationale. Never invent a video ID. Verify URLs before writing them into a playlist.

## 5. Current broad audio learning flows

These are scaffolds, not immutable curricula. Research video-level sequences before marking them active.

- MATS: Efficient Engineer foundations → university materials fundamentals → deeper MSE → professional/research lectures.
- Natural sciences: broad science orientation → subject foundations → university depth → interdisciplinary synthesis.
- Chemistry: Tyler DeWitt → Professor Dave general chemistry → university general chemistry → problem-solving reinforcement → organic/biochemistry.
- Psychology: introductory university psychology → research/APA material → Sapolsky behavioral biology → discussion/synthesis.
- Finance: Plain Bagel foundations → Damodaran corporate finance → Damodaran valuation → evidence-based investing → markets/macroeconomic synthesis.
- Music: Music Matters → David Bennett Piano → Signals Music Studio → analytical listening/theory channels → advanced synthesis.

Agents should improve these flows when research justifies it. Record the rationale for meaningful changes.

## 6. Source handling

Each source should have a stable source ID and canonical URL. Distinguish primary lesson sources from companion references. Prefer creator pages, university pages, textbooks, professional standards, or original research where appropriate.

Do not cite a search-result snippet as if it were the underlying authority when a canonical page is available.

## 7. Definition of done for a completed lesson

A lesson is fully processed when:

- playlist status is updated;
- progress/current and NEXT agree;
- main ideas are identified;
- existing cards are checked for overlap;
- new/deepened cards are stored in the correct subject module;
- source references are stored;
- prerequisites still make sense;
- the next lesson remains pedagogically appropriate.

This protocol should allow a new agent to continue the learning program solely from repository state even without access to earlier chat context.
