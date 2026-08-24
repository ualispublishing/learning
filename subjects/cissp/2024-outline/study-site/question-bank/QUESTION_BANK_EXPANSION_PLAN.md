# CISSP Atlas Question Bank Expansion Gameplan

## Goal

Expand the current 56-question original scenario bank into a **large, auditable, non-duplicate, original question system** that trains both CISSP-style judgment and deeper security application without using exam dumps or copying commercial questions.

The long-term target is **800 bank records**. Standard multiple-choice questions remain exam-oriented; bellringers are deliberately more integrative than the real test and are clearly labeled as such.

## Target difficulty distribution

| Tier | Target | Purpose | Internal difficulty | Typical solve time |
|---|---:|---|---|---|
| **F — Foundation+** | 15% / 120 | Slightly easier than the expected CISSP level; build clean distinctions and eliminate weak fundamentals | 35–49/100 | ~45–75 sec |
| **E — Exam-calibrated** | **60% / 480** | Majority of the bank; best/first/most questions, plausible distractors, technical + managerial judgment, realistic ambiguity resolvable from scenario evidence | 50–69/100 | ~60–120 sec |
| **S — Stretch** | 20% / 160 | A little harder than expected CISSP level; more constraints, cross-topic reasoning, stronger distractors, fewer obvious cues | 70–84/100 | ~90–180 sec |
| **B — Bellringer** | 5% / 40 case sets | Not intended to imitate the exam. Multi-domain case drills that force retrieval, prioritization, architecture, governance, incident judgment, and explanation together | 85–100/100 | ~5–12 min |

The 1–100 score is an **internal authoring/calibration scale**, not a claim about an ISC2 psychometric scale.

## Domain allocation

Use the current official blueprint weights as the default primary-domain allocation across the completed 800-record bank:

- D1 Security and Risk Management: 128
- D2 Asset Security: 80
- D3 Security Architecture and Engineering: 104
- D4 Communication and Network Security: 104
- D5 Identity and Access Management: 104
- D6 Security Assessment and Testing: 96
- D7 Security Operations: 104
- D8 Software Development Security: 80

Bellringers may cover 3–6 domains at once. They still receive one `domain_primary` for accounting, plus `domains_secondary` and objective/subtopic exposure metadata.

## Coverage requirements

Before the bank is called mature:

1. Every one of the 62 numbered objectives must have multiple independent scenarios.
2. Every one of the 344 mapped public-outline subtopics must have at least one recorded question exposure, either directly or as a meaningful secondary concept.
3. Every objective should eventually have at least:
   - 1 Foundation+ item;
   - 4 Exam-calibrated items;
   - 1 Stretch item.
4. High-weight/high-confusion areas receive additional items based on blueprint weight, error history, and distinction density.
5. AI-specific coverage remains distributed across all eight domains instead of becoming a fake ninth domain.
6. No objective is considered deeply practiced because its term merely appears in a stem; the tested decision rule must be recorded in `knowledge_atoms` / `correct_rule_id`.

## Originality protocol — mandatory

### Allowed source material

Questions may be authored from:

- the public ISC2 CISSP exam outline;
- current primary standards/specifications already registered by CISSP Atlas;
- the audited CISSP Atlas knowledge cards/subtopic map;
- genuinely original scenarios constructed from those knowledge sources.

Questions **must not** be generated from, paraphrased from, or compared against:

- remembered live exam items;
- exam dumps / braindumps;
- copied commercial practice questions;
- leaked item banks;
- another vendor's wording used as a seed.

Public standards teach the rule. They do **not** supply a question template to lightly rewrite.

### Author from a decision rule, not from another question

Every new question starts with this sequence:

1. Choose objective/subtopic(s).
2. Write the `correct_rule_id` and one-sentence decision rule.
3. Choose a `scenario_family` (e.g., acquisition, incident, architecture review, audit, IAM lifecycle, DR planning).
4. Choose the decision operation (`FIRST`, `BEST`, `MOST`, classification, design choice, sequence, tradeoff, root cause, control selection).
5. Add scenario-specific constraints that make one answer best.
6. Build the correct option from the rule.
7. Build each distractor from a **named misconception**, not random nonsense.
8. Write a rationale for the correct answer **and all distractors**.
9. Run duplicate/originality gates before acceptance.
10. Run semantic/factual audit before release.

Changing names, products, numbers, or synonyms does not create a new original question if the underlying scenario and decision are the same.

## Duplicate prevention

Every candidate must pass four layers.

### 1. Exact duplicate gate — automatic FAIL

Reject if the normalized stem or normalized full question matches an existing item.

Normalization removes capitalization, punctuation, repeated whitespace, and superficial formatting differences.

### 2. Near-text duplicate gate — automatic FAIL / review

Compare every candidate against the current bank and same batch using at least:

- sequence similarity;
- token-shingle Jaccard similarity;
- option-set overlap.

Recommended starting thresholds:

- normalized exact match: **FAIL**;
- SequenceMatcher ratio >= **0.90**: **FAIL**;
- token 3-gram Jaccard >= **0.72**: **FAIL**;
- 0.82–0.90 sequence similarity or 0.60–0.72 Jaccard: **manual semantic review**.

Thresholds can be tuned after the bank becomes larger.

### 3. Structural duplicate gate

Reject a candidate when it reproduces the same combination of:

- primary objective;
- scenario family;
- decision point;
- correct rule;
- materially identical misconception set;
- materially identical evidence/clues.

A question is still a duplicate if the prose is different but a learner could answer it by remembering the previous rationale without reading the new scenario.

Approved sibling questions must test a **different decision**, exception, boundary condition, ordering question, or competing control tradeoff and must declare `sibling_of`.

### 4. Semantic originality review

Ask during review:

> If I remove names and cosmetic details, is this substantially the same problem, same reasoning path, and same answer as an existing item?

If yes, reject or redesign it.

The goal is not 800 paraphrases. The goal is 800 materially different retrieval/application events.

## Difficulty rubric

### F — Foundation+ (slightly easier)

Characteristics:

- one primary concept;
- short scenario;
- correct rule is relatively explicit;
- distractors reflect common beginner confusion but usually only one or two are strongly plausible;
- little cross-domain load;
- still application-oriented where possible rather than vocabulary-only.

Use these to repair foundations, not dominate the bank.

### E — Exam-calibrated (majority)

Characteristics:

- scenario contains enough evidence to resolve ambiguity;
- two to four answers may look technically possible;
- asks BEST / FIRST / MOST appropriate action or tests a managerial-security tradeoff where appropriate;
- requires distinguishing business requirement, accountable owner, risk, control function, implementation sequence, or operational priority;
- distractors are credible and correspond to real misconceptions;
- avoids obscure trivia unless the public outline makes the knowledge operationally relevant;
- normally one primary domain with supporting knowledge from another domain when natural.

This tier should define the bank's center of gravity.

### S — Stretch (slightly harder)

Characteristics:

- multiple relevant constraints;
- three plausible distractors;
- requires two or three reasoning steps;
- may require choosing between technically strong options based on governance, sequence, ownership, evidence preservation, business impact, or scope;
- can combine closely related objectives/domains;
- removes obvious vocabulary cues;
- still has one defensible keyed answer supported by the scenario.

Harder must mean **deeper reasoning**, not arbitrary obscurity, trick wording, or knowledge outside reasonable CISSP scope.

### B — Bellringer (deliberately beyond exam format)

Bellringers are case drills, not ordinary MCQs. A bellringer should contain one coherent environment/incident/design problem and 4–8 linked prompts such as:

- identify the highest business/security risks;
- identify accountable owners;
- choose what happens FIRST and explain why;
- propose architecture/control layers;
- determine evidence/incident handling sequence;
- identify IAM/data/software implications;
- choose recovery targets/strategy from supplied business facts;
- critique a flawed proposed solution;
- explain which assumptions would change the answer.

A strong bellringer should naturally touch 3–6 domains and 8–20 knowledge atoms. It should take several minutes and force written or mentally constructed reasoning.

Bellringers must be marked **NON-EXAM-REPRESENTATIVE INTEGRATIVE DRILL** in the UI so difficulty is not confused with real CISSP item format.

## Distractor standard

Every standard MCQ must have exactly four options and a rationale for each option.

Wrong options should come from:

- wrong sequence (good action, wrong time);
- wrong owner/accountability;
- control vs governance confusion;
- technical fix before requirements/risk;
- confidentiality/integrity/availability mix-up;
- authentication vs authorization/federation confusion;
- risk vs vulnerability/severity confusion;
- detection vs prevention/correction confusion;
- business continuity vs disaster recovery/HA confusion;
- scope/authority/evidence mistakes;
- overly broad or overly absolute statements;
- a valid control that does not solve the scenario's stated requirement.

Avoid joke answers and obviously irrelevant distractors in E/S tiers.

## Question acceptance checklist

A candidate cannot enter the released bank unless all are true:

- [ ] Originality provenance says `original-from-public-scope`.
- [ ] No external question was used as a wording/template seed.
- [ ] Objective and subtopics exist in the audited coverage map.
- [ ] Correct answer is supported by the scenario and source material.
- [ ] All distractors have explicit rationales.
- [ ] There is exactly one best answer for standard MCQ format.
- [ ] Difficulty tier matches the rubric.
- [ ] Automated duplicate checks pass.
- [ ] Structural/semantic duplicate review passes.
- [ ] No hidden trivia or unstated assumption is required.
- [ ] `FIRST/BEST/MOST` wording has enough context to establish the ordering or preference.
- [ ] Explanation teaches the rule, not merely repeats the option.
- [ ] Sources are primary or appropriate supporting standards.
- [ ] Item passed semantic audit status before release.

## Calibration after use

Keep **author difficulty** separate from **personal observed difficulty**.

Record per attempt where possible:

- correct/incorrect;
- response time;
- confidence before reveal (low/medium/high or 1–3);
- chosen distractor;
- repeat performance after spacing.

Useful signals:

- confident wrong = high-priority misconception;
- slow correct = incomplete fluency;
- fast repeated correct after long spacing = stronger mastery evidence;
- universally easy within one user's history does not prove a globally easy item.

Do not claim population-level psychometric calibration from one learner. If anonymous multi-user data ever exists with sufficient sample size, item difficulty/discrimination can be estimated separately.

## Expansion phases

### Phase 0 — Current-bank baseline

- Keep the current 56 questions frozen as the initial audited baseline.
- Tag each existing question with a provisional difficulty tier and scenario family before using it for calibration.
- Most current questions are intentionally clean/direct and therefore should not be assumed to represent the future 60% exam-calibrated center.

### Phase 1 — 200 total

Add 144 questions, prioritizing missing objective/subtopic application and exam-calibrated decision quality.

Gate: no objective without multiple scenarios; duplicate checker clean; all distractors explained.

### Phase 2 — 400 total

Increase scenario diversity, stronger distractors, and inter-domain application. Introduce first bellringer case sets.

Gate: every mapped subtopic has meaningful exposure or an explicit reason why it should remain knowledge-only.

### Phase 3 — 600 total

Fill weakness clusters, broaden scenario families, and increase delayed-transfer questions that test the same rule in a genuinely different context.

Gate: difficulty distribution within +/-3 percentage points of target.

### Phase 4 — 800 total

Complete target mix:

- 120 Foundation+
- 480 Exam-calibrated
- 160 Stretch
- 40 Bellringer cases

Gate: full semantic audit, duplicate/originality audit, domain-weight audit, objective/subtopic coverage audit, difficulty audit, and UI workflow test.

## Generation batch size

Generate in small reviewed batches, not hundreds blindly.

Recommended batch:

- 16–32 candidate questions at a time;
- cover multiple domains/objectives per batch;
- run automatic quality gates;
- semantic-review every survivor;
- reject aggressively;
- only then merge into the released bank.

A smaller acceptance rate is preferable to a large low-quality bank.

## Interleaving strategy

Default practice sets should mix:

- domains according to intended mode;
- difficulty tiers;
- cognitive operations;
- scenario families;
- recent weak concepts with spaced stronger concepts.

Avoid blocks where ten consecutive questions ask the same rule with different nouns.

## Recommended UI additions during expansion

1. Difficulty selector: Foundation+ / Exam / Stretch / Bellringer.
2. “Exam-calibrated mix” preset: 10% F, 70% E, 20% S, no bellringers.
3. “Deep drill” preset: 10% E, 50% S, 40% bellringer prompts/cases.
4. Confidence-before-answer control.
5. Full distractor rationales after commit.
6. “Why did I miss this?” misconception tag.
7. New-question / unseen-question filtering.
8. Never repeat a question in the same session unless explicitly reviewing a miss.
9. Cooldown before a missed question reappears so recognition does not masquerade as retrieval.
10. Bellringer case workspace with multi-part response and rubric.

## Definition of done

The expanded bank is ready only when its size is not the impressive part. It must demonstrate:

- originality;
- audited factual accuracy;
- no material duplicates;
- defensible keyed answers;
- plausible distractors;
- current blueprint coverage;
- deliberate difficulty distribution;
- enough scenario diversity to prevent memorizing question templates;
- a separate integrative bellringer mode that deepens understanding without being mislabeled as real-exam format.
