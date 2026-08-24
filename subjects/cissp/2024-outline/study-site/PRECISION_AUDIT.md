# CISSP Atlas Precision Audit — 2026-08-23

## Result

**Published-scope mapping: PASS, with an explicit mastery boundary.**

The site is mapped to the current public ISC2 CISSP exam outline, effective April 15, 2024, plus ISC2's current 2026 cross-domain guidance for AI security.

### Deterministic scope checks

- 8/8 domains present.
- 62/62 numbered public objectives present exactly once.
- Official weights: 16/10/13/13/13/12/13/10 = 100%.
- 344 paraphrased public-outline subtopic checks distributed across the 62 objectives.
- 33 current AI-security coverage areas distributed across all 8 domains.
- 108 layered retrieval cards.
- 40 original scenario questions.
- 11 primary/reference sources.
- Every high-yield card maps to a valid objective and valid source ID.
- Every practice item maps to a valid objective, has four options, a valid answer index, and an explanation.
- Duplicate objective/card/question identifiers are rejected by `audit.py`.

## Semantic review performed

The objective/subtopic map was compared against the current ISC2 web outline rather than relying on historical CISSP summaries. This specifically surfaced and preserved detail that an objective-only audit can miss, including:

- Domain 3 architecture variants, cryptographic lifecycle/methods, cryptanalytic/implementation attacks, facility controls, and system lifecycle stages.
- Domain 4's unusually dense network-architecture scope: models, IPv4/IPv6 communication modes, secure and converged protocols, planes/topology, performance metrics, traffic directions, physical/logical/micro-segmentation, wireless/mobile, CDN, SDN/SD-WAN/NFV, VPC, and network observability/management.
- Domain 5 identity proofing, session management, credential systems, JIT, federation contexts, authorization models, policy decision/enforcement, access review, role transitions, privilege escalation, and service accounts.
- Domain 6 assessment types, red/blue/purple exercises, synthetic testing, misuse cases, coverage/interface testing, breach simulations, process evidence, remediation/exceptions, ethical disclosure, and audit contexts.
- Domain 7 investigations, SIEM/IDPS/UEBA/threat hunting, configuration management, privileged operations, incident lifecycle, preventive/detective tooling, recovery options, DR test types, continuity, physical security, and personnel safety.
- Domain 8 development methods/maturity, development ecosystem components, SAST/DAST/SCA/IAST, acquired-software models, API/source-level security, and secure coding.

## Current AI overlay

ISC2's current CISSP page explicitly integrates AI security across all eight domains rather than creating a separate AI domain. The site therefore includes AI coverage for:

1. governance, ethics/bias, legal/privacy and AI third-party risk;
2. training data, model weights, poisoning/integrity and AI privacy;
3. AI compute isolation, prompt/adversarial input, shared responsibility and explainability;
4. AI data flows, segmentation/zero trust, AI-driven NDR and edge inference;
5. non-human/AI-agent identities, least privilege and adaptive authentication;
6. AI red teaming, evasion/extraction, logic flaws and AI-assisted assessment;
7. AI-assisted SOAR, alert correlation, model drift and adversarial monitoring;
8. AI-generated code, CI/CD controls, ML supply chain, model hijacking and inference attacks.

## Accuracy boundary

The audit proves **published-outline mapping and internal consistency**. It does not prove that memorizing 108 cards is sufficient to pass CISSP, and the UI does not make that claim. ISC2 describes CISSP as experiential and states that it cannot guarantee a candidate will pass. The outline also provides examples rather than disclosing a complete live item bank.

A listed subtopic in `coverage-detail.js` means the site tracks that area and can route study toward it. It does **not** mean the learner has demonstrated deep mastery merely because the term appears in the blueprint view. Deep mastery requires retrieval, distinction from confusable concepts, scenario application, and later re-testing.

## Study-quality controls added

- retrieval before answer reveal;
- eight-layer card backs;
- local spaced-review scheduling;
- weak-objective and weighted-domain routing;
- 16-question baseline diagnostic with two original scenarios per domain;
- explicit warning that the diagnostic is a routing signal, not a readiness predictor;
- scenario feedback requiring reasoning rather than answer-letter memorization;
- CISSP decision lens for management/risk judgment;
- expandable subtopic coverage under every objective;
- current AI cross-domain overlay;
- progress export/reset;
- responsive desktop/mobile navigation;
- CI audit for data/schema/asset/syntax/static-serving regressions.

## Primary scope references

- ISC2 CISSP Certification Exam Outline: https://www.isc2.org/certifications/cissp/cissp-certification-exam-outline
- ISC2 CISSP Exam Refresh FAQ: https://www.isc2.org/certifications/cissp/cissp-exam-refresh-faq
- ISC2 Code of Ethics: https://www.isc2.org/ethics

Supporting standards are listed in the site's Sources view and `data-meta.js`.
