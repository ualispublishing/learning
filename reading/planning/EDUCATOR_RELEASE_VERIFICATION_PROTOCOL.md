# Educator Release Verification Protocol

## Purpose

This protocol governs any claim that Arabic, French, Urdu, or another graded-reading corpus is ready for teachers, educators, schools, publication, or external distribution.

It exists because internal generation checks, status labels, and repeated self-review can still miss real linguistic or pedagogical defects. A repository label such as `APPROVED`, `SEALED`, `PASS`, or `FINAL_APPROVED` is **not by itself evidence that a corpus is error-free or educator-ready**.

The objective is the strongest practical correctness standard available: complete deterministic validation, independent tool/model review, native-language professional review, educator review, disagreement resolution, and hash-bound release evidence. No agent may promise literal mathematical 100% correctness; the permitted release claim is **"full corpus independently re-audited; no known defects remain under the recorded verification protocol."**

## 1. Release state machine

Use these release states. Generation state and release state are separate concepts.

1. `GENERATED`
2. `STRUCTURAL_PASS`
3. `INTERNAL_LANGUAGE_PASS`
4. `INDEPENDENT_MACHINE_PASS`
5. `NATIVE_EXPERT_PASS`
6. `EDUCATOR_PASS`
7. `BLIND_REVIEW_PASS`
8. `RELEASE_CANDIDATE`
9. `HASH_BOUND_RELEASED`
10. `REOPEN_REQUIRED`

A corpus may be generation-complete while still being release-pending.

### Hard rule

No language may enter `HASH_BOUND_RELEASED` unless every mandatory gate below is complete against the same canonical hashes.

## 2. Evidence precedence for educator release

For release-readiness questions, use this precedence:

1. live canonical JSONL on `main`;
2. `reading/RELEASE_STATUS.json`;
3. hash-bound verification manifests and issue-resolution artifacts;
4. `reading/AGENT_HANDOFF_V2.md`;
5. fresh deterministic audit outputs;
6. `reading/STATUS.json` for generation/progression state only;
7. legacy `reading/AGENT_HANDOFF.md` and historical audit artifacts.

`reading/STATUS.json` may say `APPROVED` for historical workflow reasons. That must never override a release state that says external revalidation is pending.

## 3. Mandatory Gate A — canonical identity and deterministic integrity

Run across **100% of the corpus**, not a sample.

Verify at minimum:

- expected levels and sequence continuity;
- unique passage IDs;
- schema validity;
- exact question count and answer count per passage;
- one-to-one question/answer linkage;
- no missing or duplicate answer IDs;
- passage word-band constraints;
- target vocabulary source identity and rank/ID integrity;
- exact target exposures where declared;
- review-target visibility and chronology;
- no future-target leakage where prohibited;
- checkpoint zero-new rules where applicable;
- local assessment targets are locally declared;
- source lexicons are unchanged/read-only;
- script contamination / unintended Roman text checks;
- Unicode normalization and punctuation sanity;
- canonical file hashes recorded before review starts.

Any failure blocks release.

## 4. Mandatory Gate B — passage-by-passage linguistic audit

Audit every learner-facing field in every canonical record:

- passage text;
- question wording;
- answer wording;
- vocabulary glosses/definitions shown to learners;
- summaries, hints, titles, labels, and explanatory text.

For each item assess:

- grammar and syntax;
- spelling and typography;
- morphology and agreement;
- naturalness/idiomaticity;
- semantic precision;
- ambiguity;
- register;
- dialect/variety consistency;
- pronoun/reference clarity;
- cohesion;
- unintended translationese;
- learner-facing language contamination;
- culturally or pragmatically implausible phrasing.

The reviewer must record defects at passage ID + field + exact span + proposed correction + severity.

## 5. Mandatory Gate C — comprehension and answer-grounding audit

For every question-answer pair verify:

- the question is answerable from the passage or explicitly intended inference;
- the keyed answer is correct;
- no competing answer is equally valid unless the question allows it;
- the answer does not rely on information absent from the passage;
- inference questions require legitimate inference rather than guessing;
- vocabulary questions test the intended sense in context;
- reference-resolution questions have a unique defensible referent;
- summaries preserve scope, polarity, time, causality, and author position;
- higher-level questions genuinely test the intended level rather than superficial recall.

A question with a wrong, unsupported, or materially ambiguous answer is a **major defect**.

## 6. Mandatory Gate D — CEFR / pedagogy audit

Evaluate every passage against its declared level using repository standards plus current CEFR descriptors where applicable.

Check:

- lexical burden;
- sentence complexity;
- discourse structure;
- inference demand;
- abstraction;
- genre expectations;
- task/question demand;
- scaffolding;
- target introduction load;
- review spacing;
- progression between adjacent levels;
- appropriateness for independent learner use;
- absence of unexplained difficulty spikes.

Frequency rank must never be treated as a CEFR label.

## 7. Mandatory Gate E — independent machine/tool disagreement pass

Run independent tools as **error detectors, not authorities**. Preserve raw findings and resolution decisions.

### French

Use at least two independent French-capable systems, preferably three:

- LanguageTool (grammar/spelling/style detector);
- Antidote French corrector;
- DeepL Write French.

A suggestion is not automatically accepted. Every suggested change must be checked against meaning, level, target exposures, review scheduling, and answer keys.

### Arabic

Use at least two independent Arabic-capable systems:

- LanguageTool Arabic;
- CAMeL Tools / CALIMA MSA morphological analysis for token morphology, lemma/features, and suspicious forms;
- an additional independent Arabic-capable model/checker when available.

Arabic morphology output is diagnostic. Multiple analyses can be valid; context must be adjudicated by a qualified reviewer.

### Rule

Tool agreement never substitutes for native/expert review. Tool disagreement creates a review item that must be resolved.

## 8. Mandatory Gate F — independent model-family audit

Use at least **three independent model families** where available. Do not show later reviewers the prior model verdict before their initial judgment.

Each model gets the same rubric and must return structured findings only:

- passage ID;
- field;
- quoted span;
- defect category;
- severity;
- explanation;
- proposed repair;
- confidence.

Then run a separate adjudication pass over disagreements.

A model that generated or repaired a passage may not be the sole reviewer that approves it.

## 9. Mandatory Gate G — native professional language review

Before educator release, obtain a professional native-language proofreader/editor review of the complete learner-facing corpus or a formally partitioned complete review in which 100% of records are covered.

Reviewer requirements:

- native or demonstrably near-native command of the target standard variety;
- professional editing/proofreading or language-teaching experience;
- instructed to flag naturalness as well as grammatical errors;
- no access to an earlier "PASS" verdict until their first review is complete;
- all findings logged and resolved.

For Arabic, explicitly require Modern Standard Arabic competence if MSA is the product standard.

For French, specify the intended reference variety and permit standard international French unless the curriculum deliberately targets a regional variety.

## 10. Mandatory Gate H — educator / curriculum specialist review

A language can be linguistically correct and still be pedagogically wrong. A qualified educator must independently assess:

- level placement;
- question quality;
- learning progression;
- vocabulary load;
- infer/verify/transfer sequence;
- clarity of instructions;
- classroom/self-study usability;
- age/context appropriateness where relevant.

This reviewer should not be the same person as the primary proofreader when feasible.

## 11. Mandatory Gate I — blind second review

After all repairs, perform a blind post-repair review.

Minimum:

- risk-based sample covering every level and every unit;
- oversample passages that had major defects, large edits, high disagreement, or dense target metadata;
- include a random component chosen after repairs are frozen.

If any **critical or major** defect is found, release reopens and the affected defect class must be searched across the entire corpus, not just the sampled passage.

For the strongest release, use complete second review rather than sampling.

## 12. Defect severity

### Critical

A defect that makes content materially wrong, unsafe, unusable, corrupted, mislevelled at scale, or invalidates release evidence.

Examples: wrong canonical file, corrupted linkage, systematic incorrect answer keys, major language-variety mismatch, false release hash.

### Major

A learner/teacher could reasonably learn something wrong or be materially confused.

Examples: incorrect grammar presented as normal, wrong answer, unsupported inference, wrong target meaning, substantial CEFR mismatch.

### Minor

Real issue but unlikely to teach a false concept.

Examples: awkward but grammatical wording, typography, stylistic inconsistency.

### Release threshold

- critical defects: **0**
- major defects: **0**
- unresolved reviewer/tool disagreements: **0**
- known minor defects: **0** for the intended highest-assurance release

Do not hide defects by downgrading severity to pass a gate.

## 13. Repair protocol

Every accepted repair must trigger:

1. passage-local language/Q&A recheck;
2. target exposure/review recheck;
3. schema/linkage recheck;
4. affected level deterministic recheck;
5. any cross-level lexical/progression checks affected by the edit;
6. hash regeneration;
7. reviewer confirmation if the repair changes meaning or pedagogy.

Do not make broad stylistic rewrites during final verification unless required to fix an identified defect; broad rewrites create new unreviewed surface area.

## 14. Adjudication protocol

For every disagreement:

- preserve both opinions;
- identify the exact linguistic/pedagogical question;
- consult authoritative references where possible;
- prefer a native specialist decision for naturalness/usage;
- require a second adjudicator for major/critical disputes;
- record final decision and rationale.

`UNKNOWN`, `UNRESOLVED`, and `NEEDS_REVIEW` are release blockers.

## 15. External service strategy

Services can reduce error probability but must be layered.

Recommended current stack:

- **LanguageTool**: whole-corpus grammar/spelling/style detector for French and Arabic; automate only under service terms/appropriate API or self-hosting.
- **Antidote**: independent high-quality French grammar, agreement, spelling, typography, and style check.
- **DeepL Write**: independent French phrasing/grammar/clarity disagreement detector.
- **CAMeL Tools**: Arabic MSA morphological analysis, generation/reinflection diagnostics, token features, and suspicious-form investigation.
- **Professional reviewer marketplace/directory such as ProZ**: recruit native Arabic MSA and French proofreaders/editors. Selection must be based on qualifications, relevant language variety, editing/education experience, and a paid calibration sample before full assignment.

Never outsource final approval to one vendor or one automated score.

## 16. Professional-review calibration before full spend

Before assigning hundreds of passages to an external reviewer:

1. prepare a 10–20 passage calibration set containing known clean items plus intentionally seeded defects;
2. do not tell the reviewer which are seeded;
3. measure recall of seeded defects, false positives, naturalness judgment, and explanation quality;
4. reject reviewers who miss major seeded defects;
5. use two reviewers on a shared calibration subset to estimate agreement;
6. only then assign the full corpus.

Seeded-defect copies must never overwrite canonical content.

## 17. Release manifest

A final language release must have a machine-readable manifest containing at minimum:

- language;
- release date;
- canonical hash for every level;
- whole-language hash/manifest hash;
- deterministic audit version + result;
- external tool names/versions/dates + issue counts;
- independent model review identifiers/dates + issue counts;
- professional reviewer role/qualification record (privacy-safe identifier is acceptable);
- educator reviewer role/qualification record;
- defect ledger totals by severity and resolution;
- blind-review method/result;
- final unresolved count = 0;
- approval statement;
- invalidation rule.

## 18. Invalidation rule

Any canonical learner-facing change after release invalidates the release hash.

The changed passage must re-enter verification, and all dependent lexical/progression/Q&A checks must rerun. If the edit can affect language-wide invariants, regenerate the full release manifest.

## 19. Agent communication rule

Agents must use precise language:

Allowed:

- "generation complete"
- "internal audit complete"
- "external verification pending"
- "full independent verification complete; no known defects remain under the recorded protocol"
- "hash-bound educator release"

Not allowed without evidence:

- "100% guaranteed correct"
- "error-free"
- "teacher-ready" merely because `STATUS.json` or an audit artifact says `PASS`
- "sealed means correct"

## 20. Current application

Arabic and French have substantial completed internal audit evidence, but because prior educator-readiness claims were stronger than the evidence justified, both must undergo this protocol before a new educator-release claim is made.

Urdu is still under active generation. Apply deterministic generation guards now, but defer the expensive complete external release audit until a logical corpus milestone unless a severe defect requires immediate repair.
