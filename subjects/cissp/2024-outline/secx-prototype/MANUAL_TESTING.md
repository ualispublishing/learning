# SecX manual testing

The expanded SecX surface is a draft/review-only prototype. Manual testing does not authorize merge, promotion, production replacement, or deployment.

## Start the exact checked-out prototype locally

From the repository root, with `secx-web-prototype-20260901` (or the exact candidate SHA under review) checked out:

```bash
python3 subjects/cissp/2024-outline/secx-prototype/serve-preview.py
```

The launcher binds only to `127.0.0.1`, serves from `subjects/cissp/2024-outline/` so `../study-site` dependencies resolve normally, and opens:

```text
http://127.0.0.1:8000/secx-prototype/next.html
```

At startup the terminal also prints the Git branch, full commit SHA, and whether the checkout is clean. A detached exact-SHA checkout is valid. If a different named branch is active, the launcher prints a warning; if the working tree has uncommitted or untracked changes, it prints a **DIRTY** warning so manual observations are not accidentally attributed to the reviewed candidate.

Use `--port 8001` (or another free port) if 8000 is occupied. Use `--no-browser` to suppress automatic browser opening. Stop the server with Ctrl-C.

Do not open `next.html` directly with `file://`; the prototype expects normal same-origin HTTP loading for its embedded surface, runtime scripts, local-storage behavior, and reload tests.

## Suggested manual pass

1. Confirm the root shows **SecX**, eight domains, and the expanded review controls.
2. Try keyboard navigation: arrows, Enter, Escape, Space, `/`, Home, `R`, `Q`, `S`, `C`, and `L`.
3. Open a retrieval card and confirm `1–4` still means Wrong / Hard / Good / Easy.
4. Open a released scenario before depth 4. Select a radio option and activate **Commit answer**. Confirm the choice becomes locked and the scenario node shows a **pending** badge rather than a mastery label.
5. Reload the page before revealing the answer. Navigate back to that scenario and confirm the same pending choice remains locked and unscored.
6. Reach depth 4 deliberately and confirm that one pending attempt is scored once, then the node returns to ordinary attempted/scored/reveal evidence with no pending label.
7. Confirm the scenario workflow does not change retrieval-card due/stage state unexpectedly.
8. Try **Sources**, **Coverage**, `/` search (including `Personnel security`), and **Links · 3**.
9. In responsive/device mode at 390px width, repeat the visible Open → radio → Commit → reload → Depth flow and check that no horizontal page overflow appears.
10. Verify the conservative `index.html` surface still works independently.

## Resetting local manual-test state

The prototype intentionally persists learner activity in browser local storage. For a clean manual pass, clear these keys for `127.0.0.1` in browser developer tools, or use a fresh private browsing session:

- `cissp_atlas_progress_v1`
- `cissp_secx_graph_state_v1`

Only clear these in the localhost preview origin you are using for manual testing.

## Boundary

The authoritative release evidence remains the exact-head deterministic and Chromium workflow. A successful manual pass is additional reviewer feedback; it does not replace CI and does not by itself authorize production migration.
