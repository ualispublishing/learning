# Language Workbook Correctness Standard

The Arabic, French, and Urdu workbook set is not considered finished merely because structural, render, uniqueness, or corpus-shape checks pass.

## Required correctness gates

Every learner-facing vocabulary entry, translation, sentence, prompt, answer, and explanation must be treated as blocked if a known defect remains in any of the following areas:

1. semantic accuracy / translation fidelity;
2. grammar and morphology;
3. spelling and orthography;
4. naturalness and register;
5. CEFR / progression appropriateness;
6. prompt-answer consistency;
7. duplicate, filler, malformed, or contextually misleading content;
8. Arabic-script / Urdu-script hygiene and punctuation where applicable;
9. French accents, agreement, conjugation, contractions, and idiomatic usage;
10. misleading cultural, factual, or pedagogical framing.

Automated checks are evidence, not proof of linguistic correctness. A PASS on counts, hashes, uniqueness, source attribution, PDF structure, or renderability must never be interpreted as an error-free-content certification.

## Completion rule

A workbook may be called complete only when there are no known correctness defects after deterministic audits plus a full-content linguistic review process. Any uncertain item should be corrected, replaced, or explicitly held for adjudication rather than silently accepted.
