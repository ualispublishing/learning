# CISSP Atlas Question Bank

This directory governs future expansion of the original CISSP Atlas practice bank.

## Start here

1. Read `QUESTION_BANK_EXPANSION_PLAN.md`.
2. Author candidates to `CANDIDATE_SCHEMA.json` as JSONL records.
3. Put reviewed candidates under `question-bank/candidates/`.
4. Run:

```bash
python question-bank/quality_gate.py question-bank/candidates/<batch>.jsonl
```

5. Resolve every FAIL and manually review every WARN.
6. Perform semantic/factual review before moving a question into released runtime data.

With no candidate file, the gate validates that the current released question bank can be loaded:

```bash
python question-bank/quality_gate.py
```

## Non-negotiable originality rule

Candidates are authored from the public CISSP scope, registered primary standards, and audited CISSP Atlas knowledge—not from live-exam recollections, exam dumps, leaked items, or commercial practice questions.

A wording rewrite is not sufficient originality. A candidate must represent a materially distinct scenario/decision path or an explicitly approved sibling that tests a different boundary, exception, sequence, or tradeoff.

## Difficulty tiers

- `F`: Foundation+ — slightly easier than expected exam level.
- `E`: Exam-calibrated — majority of the bank.
- `S`: Stretch — deliberately a little harder through reasoning depth, not trivia.
- `B`: Bellringer — non-exam-representative multi-domain integrative case drill.

See the expansion plan for the 15/60/20/5 target distribution and the 800-record maturity target.
