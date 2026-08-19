# Highest-Assurance Educator Release Profile

This profile is the required release target when the user asks for the strongest practical correctness standard for teacher/educator/publication use.

It overlays `reading/planning/EDUCATOR_RELEASE_VERIFICATION_PROTOCOL.md` and makes the stricter option mandatory wherever the base protocol allows a weaker alternative.

## 1. Required coverage

For Arabic and French educator re-certification:

- deterministic structural/lexical/Q&A validation: **100% of records**;
- fresh internal linguistic/Q&A audit: **100% of learner-facing fields**;
- independent machine/tool scans: **100% of learner-facing text supported by each tool**;
- independent model-family audit: **100% of learner-facing records**, partitioning is allowed but no record may be omitted;
- native professional language review: **100% of learner-facing fields**;
- educator/curriculum review: **100% of passages and all question/answer sets**;
- blind second human review after repairs: **100% of learner-facing fields**.

A sample-only final human review is not sufficient for this profile.

## 2. Human independence

At least two independent qualified humans must inspect each released language after the final major repair cycle:

1. native-language proofreader/editor;
2. language educator/curriculum specialist.

For the strongest practical assurance, the blind post-repair reviewer should be a third person. If that is not feasible, one of the first two may perform the blind post-repair pass only if they did not author the repair and their first-pass notes are hidden until their new judgment is recorded.

No person may self-approve a repair they authored for a major or critical defect.

## 3. Model independence

Use at least three genuinely independent model families when credentials/access permit. Separate prompts or multiple runs of the same model do not count as three independent families.

If three independent families are unavailable, record the missing independence as a release blocker rather than silently treating repeated same-model reviews as equivalent.

## 4. External tool independence

### French

Target stack:

- LanguageTool;
- Antidote;
- DeepL Write.

### Arabic

Target stack:

- LanguageTool Arabic;
- CAMeL Tools / CALIMA MSA morphology diagnostics;
- at least one additional independent Arabic-capable checker/model.

These are detectors only. Suggestions require adjudication.

## 5. CEFR alignment

Use the current Council of Europe CEFR Companion Volume and descriptors as the authoritative framework reference, including official language versions where useful.

Do not claim that the Council of Europe has certified this curriculum. CEFR alignment is an evidence-based curriculum judgment made from descriptors, not a Council of Europe approval stamp.

Every passage must be checked for level appropriateness, and every level must be checked for progression consistency and unexplained difficulty spikes.

## 6. Defect threshold

Release requires:

- critical open defects = 0;
- major open defects = 0;
- minor known defects = 0;
- unresolved machine/model/human disagreements = 0;
- unreviewed learner-facing records = 0;
- stale release hashes = 0;
- missing required evidence artifacts = 0.

`UNKNOWN`, `NOT_CHECKED`, `NEEDS_REVIEW`, and equivalent states are release blockers.

## 7. Adversarial seeded calibration

Before paying or relying on an external reviewer, use a non-canonical calibration pack containing intentionally seeded defects across:

- grammar;
- naturalness;
- wrong/unsupported answer keys;
- ambiguous questions;
- target-sense errors;
- level-placement errors;
- morphology/agreement;
- reference/cohesion.

Reject a reviewer who misses any seeded major defect in the calibration set unless an adjudicator determines the seed itself was invalid.

Never seed defects into canonical files.

## 8. Repair freeze and rerun

After the final repair cycle:

1. freeze canonical content;
2. rerun deterministic validators;
3. rerun affected machine/tool checks;
4. rerun affected Q&A/lexical/progression checks;
5. perform the complete blind second human pass on the frozen content;
6. if any defect is found, repair and repeat the relevant gates;
7. only after a clean frozen pass may release hashes be issued.

## 9. Release artifact

A `HASH_BOUND_RELEASED` language must have a manifest valid against `reading/schema/release-verification-manifest.schema.json` plus a defect ledger using `reading/schema/verification-finding.schema.json`.

The release manifest must prove complete coverage and zero unresolved items against the exact canonical blobs.

## 10. Permitted final claim

Even under this highest-assurance profile, agents must not make a literal mathematical guarantee of perfection.

The strongest justified statement is:

**Full corpus independently re-audited under the highest-assurance educator release profile; every learner-facing record received complete deterministic, independent machine/model, native-language, educator, and blind post-repair review, and no known unresolved defects remain against the recorded canonical hashes.**
