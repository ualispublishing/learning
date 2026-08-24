# CISSP Atlas — Current Outline Study Workflow

Unofficial, original study site mapped to the current public ISC2 CISSP exam outline (effective 2024-04-15).

## What this version adds

- all 8 domains and all 62 numbered public objectives mapped;
- layered retrieval cards following the repository Knowledge Atlas standard;
- high-yield precision/distinction cards;
- original scenario practice;
- local spaced-review state and 0–4-style mastery;
- weak-area recommendations and weighted domain progress;
- keyboard-first study flow, responsive/mobile layout, accessibility basics;
- deterministic integrity audit in `audit.py`;
- source traceability to ISC2 and primary/current standards.

## Precision boundary

`audit.py` verifies structural and mapping correctness (IDs, weights, sources, answer indices, coverage, duplicates). It cannot prove that a public study resource contains every fact that could appear on a live adaptive exam. The site therefore says “published-outline coverage,” not “guaranteed exam coverage.” All practice questions here are original.

## Run locally

```bash
python -m http.server 8000
# open http://localhost:8000
python audit.py
```

## GitHub Pages

The folder is static and includes `.nojekyll`; it can be served directly from a Pages-supported path/branch.
