# SecX prototype release boundary

This prototype remains review-only. Passing its validation gates does not itself authorize promotion, merge, deployment, or replacement of the production CISSP Atlas surface.

## Executable boundary

`release-boundary-audit.py` runs before the production/content/browser gates and verifies the current candidate against its Git merge-base with `origin/main`.

The audit requires:

- every PR-diff file to be either under `subjects/cissp/2024-outline/secx-prototype/` or the dedicated `.github/workflows/secx-prototype-smoke.yml` workflow;
- no changed file under `subjects/cissp/2024-outline/study-site/`;
- `next.html` to remain an expanded **Review** surface embedding the conservative `index.html` prototype;
- reviewer-only relationship data to remain `scope: reviewer-only`, `learner_runtime_loaded: false`, and `publication_state: draft-only`;
- `next.html` not to load `RELATIONSHIP_REVIEW.json` or an unexpected released-relationship runtime channel;
- exact-head checkout and an explicit `ACTUAL_HEAD == EXPECTED_HEAD` assertion in CI;
- workflow permissions to remain `contents: read`;
- full Git history in CI so merge-base isolation can be checked;
- the release-boundary audit itself to remain wired into the exact-head workflow;
- no recognized deployment/publishing actions or write permissions in the prototype workflow.

## What this proves

A PASS proves that the candidate is still structurally isolated as a review prototype and that the dedicated CI workflow has not acquired a deployment/publishing path.

It does **not** prove content correctness, browser behavior, accessibility, or semantic validity. Those are covered by the separate deterministic and browser gates.

It also does not change PR state. The PR remains draft/unmerged unless a separate explicit action changes that state.

## Promotion rule

A future promotion must be a separate reviewed decision. At minimum it should preserve released IDs/data boundaries, re-run production and SecX deterministic/browser gates on the exact promotion candidate, and explicitly review any production-file changes introduced by the promotion itself.
