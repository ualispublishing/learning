# CISSP Atlas — Current Outline Study Workflow

Unofficial, original study site mapped to the current public ISC2 CISSP exam outline (effective 2024-04-15) and the AI-security cross-domain guidance currently published on ISC2's live outline page.

## Audited scope

- 8 CISSP domains;
- all 62 numbered public objectives mapped;
- 344 paraphrased public-outline subtopic checks across those objectives;
- 33 current AI-security coverage areas across all 8 domains;
- 140 layered retrieval cards: objective coverage, high-yield distinctions, AI cross-domain cards, and a 32-card precision-depth layer;
- 56 original scenario questions, including AI scenarios and 16 additional precision scenarios;
- current official domain weights (16/10/13/13/13/12/13/10 = 100%);
- 20 primary/reference sources, including current NIST SP 800-63-4 (2025), SP 800-61 Rev. 3 (2025), SP 800-88 Rev. 2 (2025), IETF IPsec/Kerberos/OAuth specifications, OpenID Connect, OASIS SAML, and OWASP ASVS.

See `PRECISION_AUDIT.md` for the semantic audit and the exact boundary between mapped scope and demonstrated mastery.

## Study workflow

The interface is organized around **diagnose → retrieve → apply → repair weak areas → re-test later** rather than passive content browsing. It includes:

- a 16-question, two-per-domain first-run diagnostic used only for routing;
- local spaced-review state and retrieval-before-reveal cards;
- weighted domain mastery and weak-objective recommendations;
- expandable subtopic coverage under every objective;
- a precision-depth deck for commonly confused technical and managerial distinctions;
- 10/20/40/56-question scenario sets;
- global search across cards, objectives, and mapped subtopics;
- keyboard study controls and a CISSP decision lens for management/risk scenarios;
- progress export/reset;
- responsive desktop/mobile layouts;
- primary/reference source traceability.

## Precision boundary

`audit.py` verifies structural and mapping correctness: objective IDs/counts, official weights, exact subtopic-map coverage, AI coverage across all eight domains, source references, answer indices, duplicate IDs, per-domain precision/scenario coverage, runtime card/question/source counts, release-status agreement, metadata-count agreement, and required application assets. Content was also reviewed against the current public ISC2 outline and current primary supporting standards where used.

This is **published-outline coverage**, not a claim that a public deck contains every live adaptive-exam fact or can guarantee a pass. ISC2 describes CISSP as experiential and does not guarantee that a candidate will pass. All practice questions here are original; no exam dumps or copied commercial questions are included.

## Continuous audit

`.github/workflows/cissp-study-site-audit.yml` runs the deterministic knowledge audit, JavaScript syntax checks, and a static HTTP asset smoke test whenever this site changes.

## Tomorrow start

Read `TOMORROW_START.md` or simply open the site and run the 16-question diagnostic. `RELEASE_STATUS.json` is the machine-readable release marker.

## Run locally

```bash
python -m http.server 8000
# open http://localhost:8000
python audit.py
```

## GitHub Pages

`.github/workflows/cissp-pages.yml` is the standard audited Pages deployment: it runs `audit.py`, uploads only this static study-site folder, and deploys it with GitHub's Pages actions. The expected project URL is `https://ualispublishing.github.io/learning/`.

If Pages has never been enabled for this repository, GitHub requires a one-time repository setting before the workflow can deploy: **Settings → Pages → Build and deployment → Source → GitHub Actions**. The normal `GITHUB_TOKEN` cannot perform that initial enablement itself. Once enabled, pushes affecting this site trigger the deployment workflow automatically.
