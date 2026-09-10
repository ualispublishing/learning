# Job Application Automation

Current runtime: **GitHub Actions scheduled public-job discovery + graduated-candidate filtering + prioritized review queue + GitHub Pages manual application queue**.

## Scheduled discovery backend

The repository has a plugin-free discovery worker:

- Workflow: `.github/workflows/job-discovery.yml`
- Worker: `job-automation/discover_jobs.py`
- Graduated/Canada filter: `job-automation/filter_graduated_jobs.py`
- Priority worker: `job-automation/prioritize_jobs.py`
- Public ATS source list: `job-automation/discovery_sources.json`
- Raw filtered output: `job-automation/discovered.json`
- Prioritized output: `job-automation/actionable.json`
- Health/status output: `job-automation/discovery_status.json`
- Schedule: every six hours at minute 17 in `America/Toronto`, plus manual `workflow_dispatch` and relevant code/config pushes.
- Providers currently supported: public Greenhouse, Lever and Ashby job-board APIs.
- Current source set: 37 employer boards, including established Canadian and Canada-hiring technology employers.
- Candidate mode: `graduated_2026_new_grad_junior`.
- Scope: public Canada/remote-Canada technology opportunity discovery and first-pass early-career triage only.

The discovery backend contains **no candidate profile, email address, résumé, cover letter, credentials, application answers, private tracker export, or other candidate PII**. It commits only public job metadata, prioritization metadata and discovery health data.

The graduated filter removes student-only internship/co-op roles and rejects obvious foreign-location false positives where Canada appears only in job text. The priority worker ranks explicit junior/new-grad/associate/entry-level technical roles above merely fresh roles, penalizes senior and level II/III/IV titles, and prevents freshness alone from putting a role into the high-priority band.

`actionable.json` is a triage queue, **not application authorization**. Before any application, re-check the current posting, candidate truth, employer AI restrictions, duplicate state and all application fields under the private job-application workflow.

## Verified runtime state

The expanded 37-source configuration and the tightened priority model have both completed successful GitHub Actions runs. The expanded validation run reached 37/37 public sources with zero source failures. The priority-model validation also completed successfully after the level/seniority penalties were added.

Runtime counts are intentionally read from `discovery_status.json` and `actionable.json` rather than hard-coded here because they change each scheduled run.

## Existing private application queue

The encrypted Pages queue remains a separate manual runner for candidate-complete prepared applications. Its last published payload contains **47** tech-focused prepared applications from the earlier queue snapshot.

- The private canonical tracker remains outside the public repository.
- The public encrypted payload is minimized to runtime fields; résumé and cover-letter references are reduced to basenames.
- Queue content is decrypted in the browser from its seeded URL fragment and stored in local browser storage.
- Other user-field, user-file, future-consideration, stale, excluded, or otherwise non-runnable statuses remain outside that queue.

## Pages runner behavior

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

A static GitHub Pages site cannot read or modify DOM fields in a different employer origin, trigger a file input there, bypass CAPTCHA, inspect a cross-origin submission result, or operate an authenticated ATS session. GitHub Actions likewise must not be treated as a generic authenticated applicant browser: it has no applicant session, résumé, candidate answers, or authority to guess form fields.

Do not change this project to claim cross-origin autofill or unattended ATS submission is possible from Pages alone.

## Safety / quality rules

- Tech-focused discovery/application scope: software, QA, security, IT/support, data/AI, implementation, or genuinely technical systems/operations roles.
- Current candidate mode is graduated/new-grad, not enrolled/student-only.
- No CAPTCHA/anti-bot bypass.
- No invented candidate answers or qualifications.
- No guessed legal/privacy/compensation/relocation/travel/demographic/security-clearance answers.
- Do not mark `submitted` without authoritative employer success evidence.
- Treat dead/stale postings as `closed`, not submitted or blocked.
- Preserve duplicate prevention and prior outcomes.
- Prefer official employer/ATS routes and remove stale or materially mismatched roles when verified.
- Re-verify the employer posting immediately before final submission when freshness or route identity is uncertain.

## Runtime policy

Active zero-plugin automation is intentionally split into two layers:

1. **GitHub Actions** — unattended public discovery, source health checks, graduated/Canada filtering, deduplicated metadata refreshes and priority-queue generation.
2. **GitHub Pages** — privacy-minimized manual queue/navigation UI.

Application submission remains gated unless a separately authorized, authenticated and truthful write-capable route is available. Historical extension, Vercel, Playwright and other browser/backend artifacts remain legacy unless deliberately reactivated under current workflow rules.

## Public data policy

Do not commit plaintext résumés, cover letters, candidate PII, passwords, application credentials, private tracker exports, or private Library paths to this public repository. Keep public automation limited to public job metadata, runner code, health/status data and encrypted/minimized queue data.
