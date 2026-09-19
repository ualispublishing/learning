# SecX Candidate Completeness Gate

`candidate-completeness-audit.py` is a deterministic wiring audit for the review prototype.

It exists to catch a different class of release-candidate defect from syntax, content, browser, and hygiene checks: files that exist but are not actually reachable, duplicated runtime loads, runtime-order drift, validation artifacts that were added but never wired into the exact-head workflow, reviewer-only data accidentally entering learner runtime, or a partially initialized expanded surface that fails silently.

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
  11. `released-relationships.js`
  12. `relationship-lens.js`
- The expanded loader exposes an explicit `loading → ready/error` state on the embedded prototype frame.
- Script-resource failures and JavaScript execution failures during expanded initialization are wired to an accessible `role="alert"` status while leaving the conservative knowledge web available.
- The final `relationship-lens.js` load marks the expanded chain ready, and an earlier error cannot be overwritten by a later ready callback.
- Every candidate-local learner-runtime JavaScript file in the PR is part of the reviewed runtime set; an extra orphan runtime file fails the gate.
- `RELATIONSHIP_REVIEW.json` remains reviewer-only and is not referenced by the learner entrypoint.
- The learner relationship layer receives only the separately promoted `released-relationships.js` runtime artifact.
- Every candidate Python audit in the PR is referenced by the dedicated exact-head GitHub Actions workflow, including `relationship-audit.py` and `relationship-release-audit.py`.
- Every browser-smoke shell runner in the PR is referenced by the workflow and has a paired HTML fixture that it actually invokes.
- Every browser-smoke HTML fixture has a paired shell runner.
- The current candidate has **nine** paired/wired browser smoke suites, including dedicated relationship behavior and separate loader success, resource-failure, and execution-failure evidence.

## Browser evidence for normal success

The browser suite validates the current expanded surface through dedicated fixtures for:

- general expanded graph/card/scenario behavior;
- loader readiness;
- Continue learner routing;
- Source Provenance;
- Coverage;
- Projection Search;
- reviewed semantic relationships;
- missing-resource fallback;
- JavaScript execution-error fallback.

`relationship-browser-smoke.html` / `.sh` additionally requires the promoted three-link runtime to remain separate from the reviewer registry and validates desktop relationship traversal plus 390px mobile render, focus, and viewport behavior.

## Browser evidence for loader success

`loader-ready-smoke.html` / `loader-ready-smoke.sh` is a dedicated browser gate for the successful outer-shell transition. On desktop and a 390px mobile shell it requires:

- `data-secx-expanded-state="ready"` on the embedded conservative frame;
- the conservative `index.html` frame and domain graph to remain mounted;
- the success status to return to the visually hidden `sr` state with `role="status"` / `aria-live="polite"`;
- exact ready text;
- no visible `role="alert"` loader error on the successful path.

Because the relationship release/runtime scripts are now the final reviewed dependencies, readiness is not reached until both `released-relationships.js` and `relationship-lens.js` load successfully.

## Browser evidence for missing-resource failure

`loader-failure-smoke.html` / `loader-failure-smoke.sh` tests the fail-visible resource path without adding any test-only learner-runtime switch. The shell runner temporarily moves `projection-search.js` out of the served tree, starts the same local HTTP server used by the other browser smokes, and restores the file through an EXIT trap.

That produces a real HTTP 404 in the expanded dependency chain. On desktop and a 390px mobile shell the fixture requires:

- `data-secx-expanded-state="error"` rather than `ready`;
- a visible `role="alert"` / `aria-live="assertive"` status;
- the alert to name `projection-search.js` as the failed dependency;
- the alert to state that the conservative knowledge web remains available;
- the conservative eight-domain graph to remain mounted;
- no later relationship-script load or ready callback to overwrite the error state;
- the mobile fallback alert and document to remain within the 390px viewport without horizontal overflow.

## Browser evidence for JavaScript execution failure

`loader-execution-smoke.html` / `loader-execution-smoke.sh` exercises the distinct execution-error path. The shell runner first moves the real `projection-search.js` to a temporary backup, then places a syntactically valid replacement at the same URL whose only behavior is to throw an `Error` immediately. The HTTP request therefore succeeds, but script execution fails inside the expanded initialization chain.

On desktop and a 390px mobile shell the fixture requires the same fail-visible guarantees as the resource-failure smoke:

- `data-secx-expanded-state="error"` rather than `ready`;
- visible assertive alert semantics;
- the alert to identify `projection-search.js`;
- the conservative eight-domain graph to remain mounted;
- the error state not to be overwritten by the script element's later load callback or downstream relationship dependencies;
- no mobile horizontal overflow.

Both fault-injection runners execute only after all normal success-path browser suites, including the relationship browser smoke. Each uses an EXIT trap to restore the original dependency even if Chromium or an assertion fails. The workflow then independently verifies that the original file is present, the temporary backup is absent, and `git diff --exit-code -- projection-search.js` reports no checkout mutation.

## What the gate does not prove

A completeness PASS is not evidence that:

- JavaScript is syntactically valid beyond the separate syntax gates;
- every possible CDN, proxy, DNS, partial-response, cache, CSP, browser-extension, or deployment-network/runtime failure mode has been reproduced;
- browser behavior outside the dedicated smoke assertions is correct;
- learner-state calculations are correct;
- content mappings, answers, sources, or coverage counts are correct;
- accessibility behavior outside the tested contracts passes in a browser;
- an arbitrary new semantic relationship is approved merely because the relationship runtime exists;
- the prototype is production-ready or should replace the default surface.

The deterministic completeness checks prove wiring and isolation. The browser smokes add real Chromium evidence for the current success path, the reviewed relationship path, one concrete missing-resource path, and one concrete JavaScript execution-error path. Broader deployment/runtime resilience would still require environment-level testing if this review surface were ever promoted.

Relationship semantic correctness remains owned by `relationship-audit.py`; exact promotion/runtime-copy integrity remains owned by `relationship-release-audit.py`; interactive traversal remains owned by the relationship browser smoke.

## Release use

The exact-head workflow runs this audit immediately after candidate hygiene and before the production/content/browser gates. `release-boundary-audit.py` also requires the completeness gate to remain wired, so a workflow edit cannot silently remove it while preserving the outer release-boundary PASS.

This remains a review-prototype validation mechanism only. It does not merge, publish to production, deploy, migrate learner state, or alter production `study-site/` files.
