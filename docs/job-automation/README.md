# Job Application Queue — Pages Only

Current runtime: **GitHub Pages only**.

## Current queue
- **115** candidate-complete, tech-focused prepared applications in the encrypted queue.
- The August 24 quality audit removed three records from the runnable set: one closed posting, one non-tech customer-service role, and one materially low-fit degree/domain mismatch.
- Queue content is decrypted in the browser from the seeded URL fragment and then stored in local browser storage.
- The public encrypted payload is minimized to runtime fields; résumé and cover-letter references are reduced to basenames.
- Public runner code contains no candidate profile, passwords, or plaintext résumé/cover-letter documents.

## Runner behavior
1. Preserve matching progress when the encrypted queue is refreshed.
2. Remove duplicate posting URLs.
3. Default to a balanced ordering that favors high fit and penalizes expected ATS friction.
4. Reuse one named employer tab rather than opening a batch of tabs.
5. Require an explicit outcome: submitted, blocked, closed/dead, or skipped.
6. Never infer submission from merely opening or closing an employer tab.
7. Categorize blockers and allow retry later.
8. Support undo plus JSON progress export/import.
9. Keep all outcome state in browser localStorage.

## Hard browser boundary
A static GitHub Pages site cannot read or modify DOM fields in a different employer origin, trigger a file input there, bypass CAPTCHA, inspect a cross-origin submission result, or operate an authenticated ATS session. Browser-native autofill may still operate independently on employer pages.

Do not change this project to claim cross-origin autofill is possible from Pages alone.

## Safety / quality rules
- Tech-only runnable queue: software, QA, security, IT/support, data/AI, or genuinely technical systems/operations roles.
- No CAPTCHA bypass.
- No invented candidate answers.
- No guessed legal/privacy/compensation/relocation/travel/demographic/security-clearance answers.
- Do not mark `submitted` without applicant-confirmed employer success.
- Treat dead/stale postings as `closed`, not submitted or blocked.
- Preserve duplicate prevention and prior local outcomes across queue refreshes.
- Prefer official employer routes and remove stale or materially mismatched roles when verified.

## Runtime policy
The active automation path is Pages only. Historical extension, Vercel, Playwright, routing, and re-verification artifacts belong in the private Library `Legacy` folder and are not active dependencies.

## Public data policy
Do not commit plaintext résumés, cover letters, candidate PII, passwords, application credentials, private tracker exports, or full private Library paths to the public Pages repository. Keep the public site limited to runner code and encrypted/minimized queue data.
