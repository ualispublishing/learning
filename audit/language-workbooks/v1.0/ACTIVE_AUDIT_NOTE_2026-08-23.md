# Active linguistic correctness audit — 2026-08-23

Current scope: Arabic, French, and Urdu v1.0 language-learning workbooks on `release/language-workbooks-v1-final`.

The active objective is zero known learner-facing correctness defects. Product-listing work and absolute commercial certification claims are out of scope for this pass.

Audit sequence:

- verify current corpus/QA artifacts and their exact branch state;
- inspect full-content audit evidence rather than relying on structural PASS labels;
- identify provable semantic, grammatical, orthographic, naturalness, level, translation, or answer-consistency defects;
- make only bounded, evidence-backed repairs;
- rebuild/re-run dependent workbook QA after content changes;
- keep unresolved or uncertain items explicitly blocked rather than accepting them.

This note is an audit marker, not a release approval.
