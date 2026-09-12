# SecX prototype release boundary

This prototype remains review-only. Passing its validation gates does not itself authorize promotion to production, merge, deployment, or replacement of the production CISSP Atlas surface.

## Executable boundary

`release-boundary-audit.py` runs before the production/content/browser gates and verifies the current candidate against its Git merge-base with `origin/main`.

The audit requires:

- every PR-diff file to be either under `subjects/cissp/2024-outline/secx-prototype/` or the dedicated `.github/workflows/secx-prototype-smoke.yml` workflow;
- no changed file under `subjects/cissp/2024-outline/study-site/`;
- `next.html` to remain an expanded **Review** surface embedding the conservative `index.html` prototype;
- reviewer-only relationship data to remain `scope: reviewer-only`, `learner_runtime_loaded: false`, and `publication_state: draft-only`;
- `next.html` never to load `RELATIONSHIP_REVIEW.json` or raw `RELEASED_RELATIONSHIPS.json`;
- the only learner relationship publication channel to be the dedicated `released-relationships.js` runtime followed by `relationship-lens.js`, each exactly once and in that order;
- the released relationship artifact to remain `scope: secx-review-prototype`, `publication_state: prototype-released`, linked back to `RELATIONSHIP_REVIEW.json`, and explicitly marked as learner-runtime data for the review prototype only;
- `relationship-audit.py`, `relationship-release-audit.py`, and the relationship browser smoke to remain wired into the exact-head workflow;
- exact-head checkout and an explicit `ACTUAL_HEAD == EXPECTED_HEAD` assertion in CI;
- workflow permissions to remain `contents: read`;
- full Git history in CI so merge-base isolation can be checked;
- the release-boundary, hygiene, and completeness audits themselves to remain wired;
- no recognized deployment/publishing actions or write permissions in the prototype workflow.

`candidate-completeness-audit.py` separately enforces the complete expanded dependency order and paired browser-fixture wiring. `relationship-release-audit.py` owns exact reviewer→promotion→runtime copy integrity. The release-boundary audit ensures those mechanisms remain inside the isolated review-prototype envelope.

## What this proves

A PASS proves that the candidate is still structurally isolated as a review prototype, production `study-site/` files are unchanged, reviewer-only semantic data is not learner-loaded, the explicit prototype relationship release channel has not been bypassed, and the dedicated CI workflow has not acquired a deployment/publishing path.

It does **not** prove content correctness, browser behavior, accessibility, or semantic validity. Those are covered by the separate deterministic and browser gates.

It also does not change PR state. The PR remains draft/unmerged unless a separate explicit action changes that state.

## Relationship publication distinction

`prototype-released` means released **inside the isolated SecX review prototype** after relationship-specific review and promotion. It does not mean released into production CISSP Atlas.

The reviewer registry, promotion artifact, learner runtime copy, and production migration are four distinct states. The boundary intentionally prevents those stages from collapsing into one another.

## Promotion rule

A future production promotion must be a separate reviewed decision. At minimum it should preserve released IDs/data boundaries, re-run production and SecX deterministic/browser gates on the exact promotion candidate, explicitly review any production-file changes introduced by that promotion, and decide how prototype relationship data would be represented in production rather than treating the prototype release artifact as automatically production-authorized.
