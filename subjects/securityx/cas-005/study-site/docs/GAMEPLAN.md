# SecurityX CAS-005 — Post-First-Pass Study Gameplan

This plan begins AFTER your planned first complete pass through the material.

## Why the sequence is designed this way

Your first pass is for acquisition and building a mental map. After that, the plan deliberately becomes harder:
- retrieval practice instead of rereading,
- spaced review instead of massed review,
- interleaving instead of long single-topic blocks,
- scenario discrimination instead of simple recognition,
- error-driven practice instead of repeating comfortable material.

The goal is not to make studying feel fluent. The goal is durable retrieval and correct decisions under unfamiliar scenarios.

---

# Phase 0 — Complete your first pass

Move through all 23 public objective sections:
1.1–1.5, 2.1–2.6, 3.1–3.8, and 4.1–4.4.

During the first pass:
- Do not try to memorize the whole flashcard deck.
- Mark each objective Green / Yellow / Red.
- Write no more than one short note for each genuinely new idea.
- Perform a few representative labs so the terms have concrete meaning.
- Keep moving until every objective has been seen once.

Exit condition:
You have encountered every objective and can describe what belongs in each of the four domains.

---


# How to use the 8-layer flashcards

Use the cards as retrieval prompts, not as eight-page notes to read every time.

1. **Front only — retrieve first.** Answer aloud or in writing before revealing anything.
2. **Layer 1 · Direct Answer.** Grade whether your retrieval was substantively correct.
3. Open **Layer 2 · Concept Expansion** only when the definition/mechanism was incomplete.
4. Open **Layer 3 · Worked / SecurityX Scenario** when you know the fact but cannot recognize it in context.
5. Open **Layer 4 · Boundaries and Misconceptions** for confusions, traps, scope limits, and nearest alternatives.
6. Use **Layer 5 · Connections and Memory** to link the concept to adjacent CAS-005 topics; do not substitute the mnemonic for understanding.
7. Attempt **Layer 6 · Transfer Prompt** without notes. This is the bridge from memorization to SecurityX application.
8. Use **Layer 7 · Mastery Evidence** as the proof standard: explain, recognize, apply/troubleshoot, contrast, and state a limitation or tradeoff.
9. Use **Layer 8 · Sources** when resolving uncertainty, auditing a card, or deepening a weak topic.

**Do not automatically read Layers 2–8 after every correct answer.** A clean retrieval should remain fast. Expand only far enough to repair the actual gap.

The browser reviewer uses transparent review stages of **0 / 1 / 3 / 7 / 14 / 30 / 60 / 120 days**. A wrong answer resets the card; Hard, Good, and Easy move it through progressively longer intervals. **These exact intervals are a practical heuristic, not a scientifically unique optimum.** Spacing research supports distributed review, while the best interval depends on retention horizon, difficulty, prior knowledge, and successful retrieval; shorten or lengthen intervals when performance data justifies it.

# Phase 1 — Baseline diagnostic

Day 1 after the first pass:

1. Take 50 mixed questions from the included hard bank.
2. No notes.
3. Give every answer a confidence score from 1–5.
4. Record the error type:
   - knowledge gap,
   - confused similar concepts,
   - missed BEST/FIRST/MOST qualifier,
   - architecture tradeoff,
   - incident-ordering error,
   - careless reading.

Do not immediately reread entire chapters. Diagnose first.

Highest-priority errors:
1. wrong + high confidence,
2. repeated misses in the same objective,
3. correct + low confidence,
4. one-off wrong guesses.

A high-confidence wrong answer indicates a faulty mental model and should be repaired aggressively.

---

# Phase 2 — Daily retrieval + spacing

Daily core session:

1. Due flashcards — 25 to 60 minutes.
2. 20–30 mixed scenario questions.
3. Review every wrong answer AND every low-confidence correct answer.
4. 20–30 minutes of a lab, architecture diagram, log analysis, or PBQ drill.
5. Convert each genuine mistake into exactly one retrievable rule/card/action.

Suggested first intervals:
- failed: same session / next day,
- correct but hard: 1 day,
- solid: 3 days,
- then 7 days,
- 14 days,
- 30 days,
- 60+ days.

Never reveal the back of a card before attempting a complete answer.

Recognition is not mastery.

---

# Phase 3 — Interleaving

Once the first pass is complete, stop reviewing entire domains in isolation.

Use the real domain weighting in mixed practice:
- 20% Governance, Risk, and Compliance
- 27% Security Architecture
- 31% Security Engineering
- 22% Security Operations

Deliberately interleave look-alike concepts:

- policy / standard / procedure / guideline
- RTO / RPO / business continuity / disaster recovery
- ATT&CK / CAPEC / STRIDE / Kill Chain / Diamond Model
- SAST / DAST / IAST / RASP / SCA / SBOM
- RBAC / ABAC / MAC / DAC
- CASB / CSPM / CWPP
- OAuth / OIDC / SAML / Kerberos / 802.1X / EAP
- SPF / DKIM / DMARC / S/MIME
- TPM / HSM / vTPM / secure enclave
- Secure Boot / measured boot
- CVE / CPE / CVSS
- symmetric / asymmetric / hashing / signatures / tokenization
- CSRF / SSRF / XSS / injection / TOCTOU / deserialization
- Sigma / YARA / Snort
- IoC / IoA / TTP

The point of interleaving is discrimination:
you must decide WHICH concept fits instead of being told the topic in advance.

---

# Phase 4 — Application training

Three times per week, do a 30–45 minute application block.

For every scenario, explicitly identify:

1. Asset
2. Threat or failure
3. Business/security constraint
4. Trust boundary
5. Most direct control
6. Why the tempting alternatives solve a different problem
7. Whether the question asks for BEST, FIRST, MOST likely, or NEXT

Practice outputs:
- architecture diagrams,
- threat models,
- decision trees,
- log triage,
- IAM troubleshooting,
- email/DNS/TLS troubleshooting,
- CI/CD security flows,
- incident timelines,
- SOAR workflows,
- crypto design choices.

For every multiple-choice question, explain why all three wrong answers are wrong.
If you cannot do that, count the question as only partially mastered.

---

# Phase 5 — Hands-on minimum

Complete at least one practical exercise in each area:

## IAM
- Inspect an OAuth/OIDC token.
- Explain authorization vs authentication.
- Trace a SAML assertion.
- Diagnose a Kerberos clock/trust problem.
- Model 802.1X supplicant/authenticator/authentication server roles.

## PKI / TLS / email
- Build or inspect a certificate chain.
- Diagnose expiry, hostname, trust-chain, and cipher mismatch cases.
- Explain SPF, DKIM, DMARC, and S/MIME from packet/message evidence.

## Network
- Read a packet capture.
- Place IDS vs IPS sensors.
- Model segmentation and microsegmentation.
- Explain where encrypted traffic becomes inspectable.

## Software / CI-CD
- Run SAST and dependency/SCA checks.
- Generate or inspect an SBOM.
- Detect a committed secret.
- Protect a branch and design a canary release.
- Scan an IaC or container configuration.

## SIEM / threat hunting
- Parse sample logs.
- Correlate endpoint + identity + network events.
- Write a simple Sigma rule.
- Write a simple YARA rule.
- Explain when a Snort-style network rule is more appropriate.

## Incident response / forensics
- Analyze a small PCAP.
- Build a timeline from multiple logs.
- Explain when volatile memory must be captured.
- Detonate only safe training malware/samples in a properly isolated environment.
- Perform root-cause analysis after containment.

## Architecture / threat modeling
- Draw at least five data-flow diagrams.
- Mark trust boundaries.
- Apply STRIDE.
- Place WAF, API gateway, logging, DLP, IAM, and segmentation controls.

---

# Six-week post-first-pass schedule

## Week 1 — Baseline + repair
Goal: identify faulty mental models.

Daily:
- 30–50 due cards
- 20 mixed questions
- one weak-objective repair block

End of week:
- 60-question mixed test
- build ranked error list

## Week 2 — Discrimination
Goal: stop confusing similar technologies.

Daily:
- due cards
- 25 mixed questions
- one contrast cluster
- one 20-minute lab

Focus heavily on:
IAM, app testing types, cloud controls, crypto, email authentication, threat-intel languages.

## Week 3 — Architecture
Goal: answer “where does the control go and why?”

Daily:
- due cards
- 25–30 mixed questions
- one architecture diagram

Complete PBQ-02, PBQ-04, PBQ-05, PBQ-06.

## Week 4 — Troubleshooting + operations
Goal: diagnose symptoms rather than recite definitions.

Daily:
- due cards
- 30 questions
- logs / TLS / DNS / email / IAM troubleshooting

Complete PBQ-07, PBQ-08, PBQ-11, PBQ-12.

## Week 5 — Hard mixed simulation
Goal: remove domain cues and develop pacing.

Twice this week:
- 90-question mixed simulated exam
- maximum 165 minutes
- no pauses
- mark uncertain questions
- deep review afterward

Other days:
- error-derived cards only
- targeted labs
- PBQ-09 and PBQ-10

## Week 6 — Readiness + taper
Goal: consistency, not cramming.

Take 2–3 different mixed mocks on separate days.
Revisit only:
- repeated misses,
- high-confidence wrong answers,
- weak objective sections,
- PBQ weaknesses.

Final 24 hours:
- light due-card review,
- acronym pass,
- key contrasts,
- sleep,
- no marathon cramming.

---

# Readiness gates

Do not use one lucky practice-test score as your signal.

Conservative readiness targets:
- >= 85% on this original hard mixed question bank after spacing,
- >= 80% on an independent unseen scenario bank,
- no major domain consistently below 75%,
- >= 90% mature recall on acronym/basic fact cards,
- can explain why wrong options are wrong,
- can complete the PBQ drills without looking up core concepts,
- stable performance across at least three mixed mocks on separate days.

These are preparation thresholds, NOT an official CompTIA passing score.

---

# Error-log protocol

Every miss creates exactly one action:

- Missing fact -> add/rewrite a flashcard.
- Confused concepts -> contrast card.
- Bad scenario choice -> one-sentence decision rule.
- Tool/command weakness -> hands-on lab.
- Missed qualifier -> write the qualifier and why it changed the answer.
- Repeated careless miss -> slow the first read and summarize the question in five words before answering.

Do not create giant notes.

Turn mistakes into future retrieval.

---

# Scientific-study principles used

## Retrieval practice
Attempt to recall before reviewing. Practice tests and active recall should dominate the post-first-pass phase.

## Distributed/spaced practice
Revisit information after increasing delays instead of massing all study in one sitting.

## Interleaving
Mix related problem types after initial exposure so you must select the correct method/control rather than applying a method that has already been cued.

## Elaboration/self-explanation
Explain why the correct answer solves the stated problem and why the alternatives do not.

## Concrete examples
Tie abstract terms to logs, architectures, IAM flows, PKI failures, cloud configurations, and incident artifacts.

## Dual coding
For architecture-heavy material, pair verbal recall with diagrams: trust boundaries, data flows, Zero Trust paths, PKI chains, and incident timelines.

---

# Exam-style decision rules

- BEST = the option that most directly reduces the stated risk while respecting constraints.
- FIRST = prerequisite, evidence preservation, containment, validation, or safety before later optimization.
- Never pick a technology merely because it sounds stronger; match the layer and failure mode.
- Separate authentication from authorization.
- Separate governance ownership from technical implementation.
- Prefer least privilege, secure defaults, segmentation, validated trust, and centralized visibility.
- In incident response, preserve volatile evidence when appropriate, contain safely, eradicate, recover, then fix root causes.
- In OT/ICS, safety and availability constraints can change the normal enterprise answer.
- In AI scenarios, treat user/model content as untrusted, minimize agency, and gate high-impact actions.


---

# Evidence notes for the study method

The study design intentionally separates well-supported principles from implementation heuristics:

- **Retrieval practice:** Reviews and meta-analyses find that attempting recall improves later retention compared with restudy across many settings, especially when recall is effortful and followed by corrective feedback. The deck therefore requires an answer before reveal.
- **Spacing/distributed practice:** A large quantitative review found robust benefits from distributing study and showed that effective spacing depends jointly on the interval between reviews and the desired retention interval. The site's exact 0/1/3/7/14/30/60/120-day schedule is therefore adjustable rather than treated as a universal law.
- **Interleaving:** Meta-analytic evidence supports interleaving for some classes of learning, especially where the learner must discriminate similar categories or problem types, but the effect depends on the material. That is why this plan uses initial acquisition first and then interleaves SecurityX look-alikes rather than randomizing everything from the beginning.
- **Transfer:** Retrieval improves memory, but memory practice alone is not sufficient proof of complex reasoning. SecurityX application is therefore trained separately through unseen scenarios, architecture work, troubleshooting, PBQs, and hands-on labs.
- **Calibration:** High-confidence errors receive extra attention because they indicate a wrong mental model rather than a simple admitted gap. Confidence scores are a diagnostic aid, not an exam-scoring method.

Primary/review references:
- Roediger HL III, Butler AC. *The critical role of retrieval practice in long-term retention.* Trends in Cognitive Sciences (2011). https://pubmed.ncbi.nlm.nih.gov/20951630/
- McDermott KB. *Practicing Retrieval Facilitates Learning.* Annual Review of Psychology (2021). https://pubmed.ncbi.nlm.nih.gov/33006925/
- Yang C, et al. *Testing (quizzing) boosts classroom learning: A systematic and meta-analytic review.* Psychological Bulletin (2021). https://pubmed.ncbi.nlm.nih.gov/33683913/
- Cepeda NJ, et al. *Distributed practice in verbal recall tasks: A review and quantitative synthesis.* Psychological Bulletin (2006). https://pubmed.ncbi.nlm.nih.gov/16719566/
- Brunmair M, Richter T. *Similarity matters: A meta-analysis of interleaved learning and its moderators.* Psychological Bulletin (2019). https://pubmed.ncbi.nlm.nih.gov/31556629/
