# SecX browser fixture preflight

`browser-fixtures-audit.py` is a deterministic preflight for assumptions that the expanded browser smoke intentionally relies on.

It does **not** replace browser execution and must never be cited as proof that keyboard, pointer, focus, disclosure, storage, reload persistence, or mobile behavior works in Chromium. Its purpose is to fail early when released data or smoke fixture IDs drift.

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
- scenario nodes visibly distinguish a locked unscored commitment with a `pending` badge from ordinary scored-attempt evidence, without introducing a mastery/readiness label;
- card/scenario local branches use a dedicated tighter mobile radial radius while preserving the existing desktop radius, keeping their 390px node geometry inside the viewport;
- expanded mobile detail uses an in-place opacity animation rather than the desktop 28px horizontal slide so the open detail does not transiently widen the 390px document;
- the expanded desktop browser smoke commits a deterministic wrong option through the numeric shortcut, verifies that commitment remains unscored before layer 4, verifies one score at layer 4, and verifies a later reveal without a new commitment remains exposure-only;
- the expanded 390px mobile browser phase traverses into the same released objective/scenario through visible **Open** controls, selects the keyed radio answer, activates visible **Commit answer**, proves the pending choice is unscored and locked, proves the scenario node reports `pending`, and proves focus moves to visible **Depth**;
- before scoring that mobile commitment, the smoke performs a full reload of the mobile `next.html` iframe, proves the same pending choice and `committedAt` timestamp survive in `cissp_secx_graph_state_v1`, proves scored/correct counts remain unchanged, navigates back to the scenario branch and proves its node still reports `pending`, reopens the scenario through visible controls, and proves the persisted choice returns locked without exposing a duplicate Commit control or keyed answer;
- after that reload, the smoke uses the visible **Depth** control to reach layer 4 and score the original committed answer exactly once, then proves the scenario badge clears `pending` and returns to ordinary committed/scored/reveal evidence;
- the mobile scenario phase also proves the attempt panel, committed state, reloaded pending state, and layer-4 detail remain horizontally contained, and that neither commitment, reload, nor scoring mutates `cissp_atlas_progress_v1`;
- scenario `C-472` exists exactly once in the released runtime standard-scenario set and has a routable explicit objective;
- generated objective-card IDs plus released high-yield IDs remain unique and reconcile to `CISSP_META.meta.card_count`;
- runtime standard scenarios reconcile to `CISSP_META.meta.question_count`;
- `browser-smoke.html` still contains the fixture tokens the audit is protecting (`1.9`, the card/scenario facets, desktop keyboard commitment assertions, mobile radio/Commit/reload/pending-badge/Depth/containment assertions, `C-472`, the Study weak facet, and card-count reconciliation).

The numeric answer keys are contextual: an open scenario uses `1…N` to commit that numbered option, while an open retrieval card retains the existing `1–4` Wrong / Hard / Good / Easy grading semantics. The radio options and visible **Commit answer** control remain available for pointer/Tab users, and the 390px smoke validates that visible path directly rather than only checking the mobile shell.

The reload check is a persistence boundary, not a second attempt path. A pending commitment must remain exactly one unscored commitment across reload, with the same choice and timestamp, until deliberate layer-4 disclosure scores it. The learner-visible node badge must remain `pending` across that reload and must clear only when the pending attempt is actually scored. Reload must not manufacture another attempt, expose correctness, or touch Atlas review state.

The mobile containment rules are geometry rules, not a request to hide overflow: card/scenario centers move inward on narrow viewports, and the detail animation no longer translates outside the viewport. The browser test still checks actual document width after commitment, after reload/reopen, and again at layer 4.

If any of those assumptions changes intentionally, update the browser smoke and this preflight in the same candidate head.

The GitHub Actions exact-head workflow compiles and runs this audit before launching browser smoke. A PASS from this audit is **static fixture evidence only**; promotion still requires the real browser gates on the same exact SHA.

Earlier keyboard-attempt evidence remains historical only. The current candidate head must pass the complete exact-head workflow, including the mobile radio/Commit → pending badge → full reload → restored pending badge/choice → Depth-4 score → cleared pending badge path and viewport-containment assertions, before this refinement is treated as validated. This file does not self-authorize promotion.
