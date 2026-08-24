# CISSP Atlas — Current Outline Study Workflow

Unofficial, original study site mapped to the current public ISC2 CISSP exam outline (effective 2024-04-15) and the AI-security cross-domain guidance currently published on ISC2's live outline page.

## Audited scope

- 8 CISSP domains;
- all 62 numbered public objectives mapped;
- 108 layered retrieval cards, including 8 current AI cross-domain cards;
- 40 original scenario questions, including one AI-security scenario per domain;
- current official domain weights (16/10/13/13/13/12/13/10 = 100%);
- 11 primary/reference sources, including current NIST SP 800-63-4 (2025) and SP 800-61 Rev. 3 (2025).

## Study workflow

The interface is organized around **diagnose → retrieve → apply → repair weak areas → re-test later** rather than passive content browsing. It includes local spaced-review state, weighted domain mastery, weak-objective recommendations, global search, keyboard study controls, progress export/reset, responsive desktop/mobile layouts, and source traceability.

## Precision boundary

`audit.py` verifies structural and mapping correctness: objective IDs/counts, official weights, source references, answer indices, duplicate IDs, runtime card counts, and required application assets. Content was also reviewed against the current public ISC2 outline and current primary supporting standards where used.

This is **published-outline coverage**, not a claim that a public deck contains every live adaptive-exam fact or can guarantee a pass. ISC2 states that its exam is experiential and that it cannot guarantee a candidate will pass. All practice questions here are original; no exam dumps or copied commercial questions are included.

## Run locally

```bash
python -m http.server 8000
# open http://localhost:8000
python audit.py
```

## GitHub Pages

The folder is static and includes `.nojekyll`; it can be served directly from a Pages-supported path/branch.
