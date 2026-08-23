# SecurityX CAS-005 Layered Study Site v4.1

A self-contained, offline-capable static study site for CompTIA SecurityX CAS-005.

## Audited contents

- **1156 layered flashcards**, each with 8 progressively deeper back layers.
- **618 / 618 normalized published CAS-005 blueprint examples explicitly mapped** across all 23 objective sections.
- **191 acronym cards**, including exam-vs-current terminology notes where needed.
- **100 original hard scenario questions** with 20/27/31/22 domain weighting and balanced A/B/C/D answer positions.
- **12 original PBQ-style drills**.
- Browser-enforced **retrieve first; expand second** workflow.
- Local, transparent spaced-review state (0/1/3/7/14/30/60/120-day stages).
- Post-first-pass retrieval/spaced/interleaved study plan.
- Source registry and machine-readable final audit.
- No external JavaScript frameworks or build step.

## Use locally

Open `index.html` in a browser. The GitHub Pages build loads deterministic local JavaScript data chunks. For local use, serve the folder with any simple static server (for example `python3 -m http.server`) and open the shown localhost URL. Review progress is stored only in that browser's local storage.

## Publish

See `docs/PUBLISHING.md` for GitHub Pages steps.

## Important limitation

No legitimate study resource can guarantee a passing score. CompTIA states the public objective examples are non-exhaustive. This project's completeness claim applies to the **published blueprint examples audited on 2026-08-22**, not to protected live questions or every related technology that could be tested within those objectives.


## GitHub Pages build

This directory is self-contained and is the exact directory deployed by the repository Pages workflow. The large flashcard deck is split into deterministic `data/cards-*.js` chunks for reliable static hosting; `data/meta.js` initializes the deck metadata, question bank, PBQs, blueprint map, and source registry.
