# CISSP Atlas — Current Outline Study Workflow

Unofficial, original study site mapped to the current public ISC2 CISSP exam outline (effective 2024-04-15) and the AI-security cross-domain guidance currently published on ISC2's live outline page.

## Current release — v1.3

- 8 CISSP domains and current official weights: 16/10/13/13/13/12/13/10 = 100%;
- all 62 numbered public objectives mapped;
- 344 paraphrased public-outline subtopic checks;
- 33 current AI-security coverage areas across all 8 domains;
- 140 layered retrieval cards;
- **79 released standard scenario questions + 1 Bellringer = 80 released bank records**;
- released author-difficulty mix: **41 Foundation+ / 34 Exam-calibrated / 4 Stretch / 1 Bellringer**;
- **all 79 released standard questions have four-option teaching rationales**;
- **220 learner-facing items in the semantic-audit ledger**;
- 20 primary/reference sources.

`question-bank/RELEASED_BATCHES.json` is authoritative for promoted question batches. Batch 001 is released in v1.3. Batches 002 and 003 remain candidate-only until their repository gates are observed clean.

## Item-level semantic status

The semantic ledger now covers all 220 released learner-facing items: 62 objective cards, 38 high-yield cards, 8 AI cards, 32 precision cards, 79 standard questions, and 1 Bellringer.

Current audit summary:

- 217 verified unchanged;
- 1 verified after a wording correction (`HY-014`, digital signatures/nonrepudiation);
- 2 verified with explicit source-scope notes (`AI-005`, `PX-020`);
- **0 keyed-answer reversals**;
- **0 known remaining material factual errors identified by the documented review**.

This is a strong, auditable quality claim—not a mathematical guarantee that every sentence can never contain nuance or that studying the site guarantees a live CISSP pass. See `PRECISION_AUDIT.md` and `SEMANTIC_ITEM_AUDIT.json`.

## Study workflow

The interface is organized around **diagnose → retrieve → apply → repair weak areas → re-test later**. v1.3 includes:

- 16-question, two-per-domain first-run diagnostic used only for routing;
- local spaced-review state and retrieval-before-reveal cards;
- weighted domain mastery and weak-objective recommendations;
- expandable subtopic coverage and precision-depth cards;
- **difficulty-aware standard practice** with Foundation+, Exam-calibrated, Stretch, and Exam+Stretch filters;
- **confidence-before-answer** capture;
- high-confidence-miss tracking;
- **four individualized option rationales for every released standard question**;
- separate **NON-EXAM-REPRESENTATIVE INTEGRATIVE DRILL** Bellringer mode with constructed responses, rubric reveal, and self-scoring;
- global search, keyboard controls, progress export/reset, and responsive desktop/mobile layouts.

The original 56-question baseline was left semantically intact: its stems, option text, keyed answers, and original explanations were not changed. A separate reviewed rationale layer adds 224 option rationales (56 × 4). `LEGACY_RATIONALE_AUDIT.json` records that backfill and CI fails if any of the 56 rationale sets is missing or incomplete.

## Question-bank expansion

`question-bank/QUESTION_BANK_EXPANSION_PLAN.md` defines an 800-record maturity target:

- 15% Foundation+ — slightly easier than expected exam level;
- **60% Exam-calibrated** — center of gravity;
- 20% Stretch — somewhat harder through reasoning depth, not obscure trivia;
- 5% Bellringer — clearly labeled, non-exam-representative multi-domain cases.

Originality is enforced by decision-rule-first authoring from public scope/registered standards and audited knowledge, never from exam dumps, live-item recollections, leaked banks, or commercial-question wording/templates. `question-bank/quality_gate.py` compares unreleased candidates against the base bank, all promoted batches, and their own batch using exact, near-text, and structural duplicate checks.

`question-bank/coverage_report.py` adds a second planning layer: it measures objective/difficulty density and explicit subtopic-tag exposure so future questions target under-practiced areas rather than simply adding more volume.

### Current expansion state

- **Batch 001:** released in v1.3; 24 records = F4/E15/S4/B1.
- **Batch 002:** candidate-only; 16 standard MCQs = E12/S4, exactly two primary-domain questions per domain, zero Foundation+ filler.
- **Batch 003:** candidate-only; 16 standard MCQs = E12/S4, exactly two primary-domain questions per domain, zero Foundation+ filler.
- If both pending batches eventually promote, the bank becomes **112 records = F41/E58/S12/B1**.

Neither pending batch may be promoted until its full repository gate produces no unresolved failures or warnings.

## Continuous audit

`.github/workflows/cissp-study-site-audit.yml` runs:

1. `python audit.py`;
2. `python question-bank/quality_gate.py` against unreleased candidates and the released comparison corpus;
3. `python question-bank/coverage_report.py` to keep expansion coverage-aware;
4. JavaScript syntax checks, including the v1.3 bootstrap/calibration/practice/state/rationale files;
5. a 56 × 4 legacy-rationale completeness invariant;
6. static HTTP smoke checks for critical site, rationale, released-bank, and candidate assets.

The Pages workflow validates the immutable released corpus before deployment; unreleased candidate failures cannot block an already-valid release from publishing.

## Run locally

```bash
python -m http.server 8000
# open http://localhost:8000
python audit.py
python question-bank/quality_gate.py
python question-bank/coverage_report.py --human
```

Serve the folder over HTTP rather than opening `index.html` directly, because v1.3 loads the released batch manifest/JSONL through `fetch()` before the application initializes.

## GitHub Pages

`.github/workflows/cissp-pages.yml` deploys only after released-corpus validation. Expected project URL: `https://ualispublishing.github.io/learning/`.

If Pages has never been enabled for this repository, the one-time repository setting remains: **Settings → Pages → Build and deployment → Source → GitHub Actions**.
