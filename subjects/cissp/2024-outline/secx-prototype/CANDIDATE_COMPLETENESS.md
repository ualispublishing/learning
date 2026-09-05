# SecX Candidate Completeness Gate

`candidate-completeness-audit.py` is a deterministic wiring audit for the review prototype.

It exists to catch a different class of release-candidate defect from syntax, content, browser, and hygiene checks: files that exist but are not actually reachable, duplicated runtime loads, runtime-order drift, validation artifacts that were added but never wired into the exact-head workflow, or a partially initialized expanded surface that fails silently.

## What the gate proves

On PASS, the current candidate demonstrates all of the following:

- `next.html` embeds the conservative `index.html` comparison surface exactly once.
- The expanded runtime dependencies are referenced exactly once and in the reviewed order:
  1. `../study-site/data-ai.js`
  2. `../study-site/data-precision.js`
  3. `learner-registry.js`
  4. `next-layer.js`
  5. `learner-state.js`
  6. `due-review.js`
  7. `study-lens.js`
  8. `source-lens.js`
  9. `coverage-lens.js`
  10. `projection-search.js`
- The expanded loader exposes an explicit `loading → ready/error` state on the embedded prototype frame.
- Script-resource failures and JavaScript execution failures during expanded initialization are wired to an accessible `role="alert"` status while leaving the conservative knowledge web available.
- The final `projection-search.js` load marks the expanded chain ready, and an earlier error cannot be overwritten by a later ready callback.
- Every candidate-local JavaScript file in the PR is part of that reviewed runtime set; an extra orphan runtime file fails the gate.
- Reviewer-only relationship data and release/audit documentation are not referenced by the learner entrypoint.
- Every candidate Python audit in the PR is referenced by the dedicated exact-head GitHub Actions workflow.
- Every browser-smoke shell runner in the PR is referenced by the workflow and has a paired HTML fixture that it actually invokes.
- Every browser-smoke HTML fixture has a paired shell runner.

## What the gate does not prove

A completeness PASS is not evidence that:

- JavaScript is syntactically valid;
- a real failed network request was browser-simulated in CI;
- browser behavior is otherwise correct;
- learner-state calculations are correct;
- content mappings, answers, sources, or coverage counts are correct;
- accessibility behavior passes in a browser;
- semantic relationships are approved;
- the prototype is production-ready or should replace the default surface.

The fail-visible checks are deterministic wiring evidence. Browser success-path behavior remains owned by the existing smoke suites, while real deployment/network failure behavior would require separate environment-level testing if this review surface were ever promoted.

Those claims remain owned by the existing syntax, deterministic domain audits, browser smokes, relationship review boundary, and release-boundary checks.

## Release use

The exact-head workflow runs this audit immediately after candidate hygiene and before the production/content/browser gates. `release-boundary-audit.py` also requires the completeness gate to remain wired, so a workflow edit cannot silently remove it while preserving the outer release-boundary PASS.

This remains a review-prototype validation mechanism only. It does not merge, publish, deploy, migrate learner state, or alter production `study-site/` files.
