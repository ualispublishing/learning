# Job Application Queue — Pages Only

Current runtime: **GitHub Pages only**.

## Current queue
- 118 candidate-complete prepared applications in the encrypted queue.
- Queue content is decrypted in the browser from the seeded URL fragment and then stored in local browser storage.
- Public runner code contains no candidate profile, passwords, or plaintext resume documents.

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

## Safety/truth rules
- No CAPTCHA bypass.
- No invented candidate answers.
- No guessed legal/privacy/compensation/relocation/travel/demographic/security-clearance answers.
- Do not mark `submitted` without applicant-confirmed employer success.
- Treat dead/stale postings as `closed`, not submitted or blocked.
- Preserve duplicate prevention and prior local outcomes across queue refreshes.

## Public data policy
Do not commit plaintext resumes, cover letters, candidate PII, passwords, application credentials, or private tracker exports to the public Pages repository. Keep the public site limited to runner code and encrypted/minimized queue data.
