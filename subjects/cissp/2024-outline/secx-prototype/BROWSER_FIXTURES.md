# SecX browser fixture preflight

`browser-fixtures-audit.py` is a deterministic preflight for assumptions that the expanded browser smoke intentionally relies on.

It does **not** replace browser execution and must never be cited as proof that keyboard, pointer, focus, disclosure, storage, or mobile behavior works in Chromium. Its purpose is to fail early when released data or smoke fixture IDs drift.

The audit reconstructs the runtime standard-scenario ordering used by `next-layer.js`:

1. standard base questions from the loaded released `CISSP_CHUNKS`;
2. then `format == "mcq"` rows from files listed by `question-bank/RELEASED_BATCHES.json`, in manifest order.

It verifies the current expanded smoke assumptions:

- exactly eight released domains are present;
- objective `1.9` exists in D1;
- D1 is still named **Security and Risk Management**;
- D1 remains the unique highest exam-weight domain, which is required for the fresh/tied lowest-review-score expectation;
- objective `1.9` has at least one high-yield retrieval card, because the browser smoke intentionally opens the first `SECX_HIGH_CARDS` match;
- the first objective-`1.9` scenario in runtime order has a stable ID, prompt, options, and valid keyed answer for the depth-4 answer-boundary test;
- scenario `C-472` exists exactly once in the released runtime standard-scenario set and has a routable explicit objective;
- generated objective-card IDs plus released high-yield IDs remain unique and reconcile to `CISSP_META.meta.card_count`;
- runtime standard scenarios reconcile to `CISSP_META.meta.question_count`;
- `browser-smoke.html` still contains the fixture tokens the audit is protecting (`1.9`, the card/scenario facets, `C-472`, the Study weak facet, and card-count reconciliation).

If any of those assumptions changes intentionally, update the browser smoke and this preflight in the same candidate head.

The GitHub Actions exact-head workflow compiles and runs this audit before launching browser smoke. A PASS from this audit is **static fixture evidence only**; promotion still requires the real browser gates on the same exact SHA.
