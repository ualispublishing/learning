# SecX candidate hygiene gate

`candidate-hygiene-audit.py` is a deterministic pre-browser self-review gate for the SecX review prototype.

It runs after the release-boundary audit and before the production/content/browser gates.

## Candidate-wide text integrity

For changed UTF-8 text files in the prototype candidate and its dedicated workflow, the audit requires:

- UTF-8 decoding;
- a final newline;
- LF rather than CRLF line endings;
- no unresolved Git merge-conflict markers.

The gate derives the candidate file set from the real Git merge-base with `origin/main`, matching the release-boundary model rather than relying on a manually maintained filename list.

## Learner-runtime hygiene

The learner-facing runtime files are additionally rejected if they contain:

- unresolved `TODO`, `FIXME`, `HACK`, or `XXX` developer markers;
- a JavaScript `debugger` statement;
- stray `console.log`, `console.debug`, or `console.trace` calls;
- dedicated browser-smoke query tokens or `data-smoke` result markers.

Intentional failure diagnostics such as `console.error(...)` remain allowed.

The runtime scope is deliberately narrower than the entire prototype tree so test harnesses and audits can contain testing vocabulary without being mistaken for learner-runtime leakage.

## Current cleanup

The initial self-review found missing final newlines in:

- `next-layer.js`;
- `source-lens.js`;
- `coverage-lens.js`.

Those files were normalized without changing JavaScript behavior before the gate was enabled.

## Evidence boundary

A hygiene PASS means the candidate is free of the specific text-integrity, unresolved-marker, debug-statement, stray-console, and smoke-token defects checked above.

It does **not** prove:

- content correctness;
- browser behavior;
- accessibility behavior;
- learner-state correctness;
- source or coverage mapping correctness;
- semantic relationship correctness;
- production readiness.

Those claims remain owned by their dedicated deterministic and browser gates. The release-boundary audit separately requires this hygiene gate to remain wired into the exact-head workflow.
