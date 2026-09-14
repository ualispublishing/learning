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
- the first objective-`1.9` scenario in runtime order has a stable ID, prompt, **2–9 options**, and a valid keyed answer so the browser can exercise the contextual `1…N` scenario-commit shortcut before the depth-4 answer boundary;
- `learner-state.js` still contains the contextual numeric scenario branch, advertises its `1…N` shortcut, and routes that shortcut through the same explicit `commitScenarioAttempt(...)` mutator used by the visible commitment flow;
- the visible scenario commitment path still reads the selected radio option and hands focus to the persistent visible **Depth** control after commitment;
- the expanded desktop browser smoke commits a deterministic wrong option through the numeric shortcut, verifies that commitment remains unscored before layer 4, verifies one score at layer 4, and verifies a later reveal without a new commitment remains exposure-only;
- the expanded 390px mobile browser phase traverses into the same released objective/scenario through visible **Open** controls, selects the keyed radio answer, activates visible **Commit answer**, proves the pending choice is unscored and locked, proves focus moves to visible **Depth**, then uses that control to reach layer 4 and score the committed answer exactly once;
- the mobile scenario phase also proves the attempt panel and layer-4 detail remain horizontally contained, and that the attempt does not mutate `cissp_atlas_progress_v1`;
- scenario `C-472` exists exactly once in the released runtime standard-scenario set and has a routable explicit objective;
- generated objective-card IDs plus released high-yield IDs remain unique and reconcile to `CISSP_META.meta.card_count`;
- runtime standard scenarios reconcile to `CISSP_META.meta.question_count`;
- `browser-smoke.html` still contains the fixture tokens the audit is protecting (`1.9`, the card/scenario facets, desktop keyboard commitment assertions, mobile radio/Commit/Depth assertions, `C-472`, the Study weak facet, and card-count reconciliation).

The numeric answer keys are contextual: an open scenario uses `1…N` to commit that numbered option, while an open retrieval card retains the existing `1–4` Wrong / Hard / Good / Easy grading semantics. The radio options and visible **Commit answer** control remain available for pointer/Tab users, and the 390px smoke now validates that visible path directly rather than only checking the mobile shell.

If any of those assumptions changes intentionally, update the browser smoke and this preflight in the same candidate head.

The GitHub Actions exact-head workflow compiles and runs this audit before launching browser smoke. A PASS from this audit is **static fixture evidence only**; promotion still requires the real browser gates on the same exact SHA.

Earlier keyboard-attempt evidence remains historical only. The current candidate head must pass the complete exact-head workflow, including the mobile radio/Commit/Depth scenario path, before this refinement is treated as validated. This file does not self-authorize promotion.
