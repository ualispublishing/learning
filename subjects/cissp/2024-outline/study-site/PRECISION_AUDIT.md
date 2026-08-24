# CISSP Atlas Precision Audit — 2026-08-24

## Result

**Published-scope mapping: PASS. Item-level semantic review: PASS, with explicit nuance notes.**

The site is mapped to the current public ISC2 CISSP exam outline, effective April 15, 2024, plus ISC2's current cross-domain guidance for AI security. The live ISC2 outline was re-checked on 2026-08-24 before this semantic pass.

## 2026-08-24 item-level semantic audit

Every current learner-facing knowledge/question item was individually reviewed for factual precision, misleading absolutes, answer-key validity, and consistency with the current public outline and primary references where material.

Scope: **196 items total**

- 62 objective cards;
- 38 high-yield cards;
- 8 AI cards;
- 32 precision-depth cards;
- 56 scenario questions, including every option set, keyed answer, and explanation.

Result:

- **193 VERIFIED unchanged**;
- **1 VERIFIED_AFTER_CORRECTION**;
- **2 VERIFIED_WITH_SOURCE_SCOPE_NOTE**;
- **0 answer-key reversals**;
- **0 material factual errors identified as remaining after this pass**.

`SEMANTIC_ITEM_AUDIT.json` records a status for all 196 item IDs, and `audit.py` now fails if a current card/question is added or removed without a corresponding semantic-audit status.

### Correction made

`HY-014` (digital signatures) was tightened. The old wording could be read as implying that a digital signature itself guarantees nonrepudiation. The corrected card states that digital signatures provide integrity and origin authentication and can **support** nonrepudiation when signer identity, private-key control, key/certificate validity, and supporting evidence are trustworthy. A signature does not itself provide confidentiality or guarantee nonrepudiation under weak identity/key custody.

### Source-scope notes

`AI-005` and `PX-020` remain factually valid: the current CISSP outline explicitly includes non-human/AI-agent identities and service-account governance. However, NIST SP 800-63-4 is explicitly scoped to identity proofing, authentication, and federation of **users** such as employees, contractors, or private individuals. It can be useful supporting IAM context, but it should not be treated as the sole primary authority for non-human/service identities. The ISC2 outline is the direct scope authority for those two items.

These notes are intentionally recorded rather than silently flattening “correct content” and “perfect source fit” into the same claim.

## Deterministic scope checks

- 8/8 domains present.
- 62/62 numbered public objectives present exactly once.
- Official weights: 16/10/13/13/13/12/13/10 = 100%.
- 344 paraphrased public-outline subtopic checks distributed across the 62 objectives.
- 33 current AI-security coverage areas distributed across all 8 domains.
- 140 layered retrieval cards.
- 56 original scenario questions.
- 20 primary/reference sources.
- Every high-yield/precision card maps to a valid objective and valid source ID.
- Every practice item maps to a valid objective, has four options, a valid answer index, and an explanation.
- Duplicate objective/card/question identifiers are rejected by `audit.py`.
- The complete 196-item semantic audit manifest is now required by `audit.py`.
- Metadata counts are recomputed and compared with the declared release metadata so stale claims fail validation.

## Semantic scope review

The objective/subtopic map was compared against the current ISC2 web outline rather than relying on historical CISSP summaries. This specifically surfaced and preserved detail that an objective-only audit can miss, including:

- Domain 3 architecture variants, cryptographic lifecycle/methods, cryptanalytic/implementation attacks, facility controls, and system lifecycle stages.
- Domain 4's unusually dense network-architecture scope: models, IPv4/IPv6 communication modes, secure and converged protocols, planes/topology, performance metrics, traffic directions, physical/logical/micro-segmentation, wireless/mobile, CDN, SDN/SD-WAN/NFV, VPC, and network observability/management.
- Domain 5 identity proofing, session management, credential systems, JIT, federation contexts, authorization models, policy decision/enforcement, access review, role transitions, privilege escalation, and service accounts.
- Domain 6 assessment types, red/blue/purple exercises, synthetic testing, misuse cases, coverage/interface testing, breach simulations, process evidence, remediation/exceptions, ethical disclosure, and audit contexts.
- Domain 7 investigations, SIEM/IDPS/UEBA/threat hunting, configuration management, privileged operations, incident lifecycle, preventive/detective tooling, recovery options, DR test types, continuity, physical security, and personnel safety.
- Domain 8 development methods/maturity, development ecosystem components, SAST/DAST/SCA/IAST, acquired-software models, API/source-level security, and secure coding.

## Precision-depth layer

A further 32 cards and 16 scenarios were added specifically to prevent shallow objective coverage from being mistaken for operational understanding. The depth layer covers four curated distinctions per domain, including:

- control functions, separation of duties vs least privilege, BIA-first recovery design, and residual-risk ownership;
- clear/purge/destroy sanitization, owner vs custodian, DLP/CASB/DRM, and scoping vs tailoring;
- PKI trust chains, TPM capabilities, container vs VM isolation, and fail-secure design;
- TCP vs UDP, IPv6 communication modes, IPsec AH vs ESP, and IPsec transport vs tunnel mode;
- OAuth vs OIDC, SAML vs OIDC, Kerberos TGT/service tickets, and service-account governance;
- red/blue/purple roles, KPI vs KRI, synthetic transactions vs benchmarks, and audit vs technical assessment;
- full/incremental/differential backups, hot/warm/cold sites, SIEM/SOAR/UEBA, and volatile-evidence handling;
- parameterized queries, validation vs encoding vs authorization, acquired-software responsibility, and build/CI-CD provenance.

Primary references were expanded for these distinctions, including NIST SP 800-88 Rev. 2, SP 800-115, SP 800-34 Rev. 1, SP 800-86, RFC 4301 (IPsec), RFC 4120 (Kerberos), RFC 6749 (OAuth 2.0), OpenID Connect Core, and OASIS SAML V2.0.

## Current AI overlay

ISC2's current CISSP page explicitly integrates AI security across all eight domains rather than creating a separate AI domain. The site therefore includes AI coverage for governance/ethics and supplier risk; AI data/model assets; AI architecture and prompt/adversarial threats; AI network isolation and NDR; non-human/agent identities; AI red teaming; AI-assisted operations/model drift; and AI-assisted development/supply-chain risks.

## Current-standards checks relevant to this release

- NIST SP 800-61 Rev. 3 (April 2025) is the current NIST incident-response publication and supersedes Rev. 2.
- NIST SP 800-63-4 (July 2025) is the current NIST Digital Identity Guidelines and supersedes SP 800-63-3.
- NIST SP 800-88 Rev. 2 (September 2025) is the current media-sanitization publication and supersedes Rev. 1.
- RFC 4301 continues to support the site's high-level distinction that AH provides integrity/data-origin authentication but not confidentiality, while ESP can provide confidentiality and can satisfy most IPsec security requirements; both transport and tunnel modes exist.

## Accuracy boundary

The audits provide strong evidence of **published-outline alignment, item-level review, answer-key consistency, and internal traceability**. They do not create a mathematically valid “100% infallible forever” guarantee. Standards can change, a reviewer can still miss nuance, and ISC2's live adaptive item bank is not public.

The correct claim for this release is therefore:

> **No known material factual errors or incorrect keyed answers remain after the 2026-08-24 item-level audit; every current item has an explicit semantic review status.**

That is materially stronger and more auditable than saying “100% correct” without qualification.

A listed subtopic in `coverage-detail.js` means the site tracks that area and can route study toward it. It does **not** mean the learner has demonstrated deep mastery merely because the term appears in the blueprint view. Deep mastery requires retrieval, distinction from confusable concepts, scenario application, and later re-testing.

## Question-bank expansion controls

The expansion design is documented in `question-bank/QUESTION_BANK_EXPANSION_PLAN.md` and includes:

- a target 800-record bank;
- a 15% Foundation+ / 60% Exam-calibrated / 20% Stretch / 5% Bellringer distribution;
- no exam dumps or commercial-question seeds;
- decision-rule-first original authoring;
- exact, near-text, and structural duplicate gates;
- explicit distractor rationales;
- objective/subtopic exposure metadata;
- a separate non-exam-representative bellringer case format;
- `question-bank/quality_gate.py` for automated originality/duplicate validation;
- `question-bank/CANDIDATE_SCHEMA.json` for future candidate structure.

CI now runs the question-bank quality gate alongside the deterministic knowledge audit.

## Study-quality controls

The v1.2 workflow includes retrieval-before-reveal layered cards, local spaced review, weak-objective and weighted-domain routing, a 16-question diagnostic used only for routing, original scenario feedback, a CISSP decision lens, expandable subtopic coverage, current AI coverage, the precision-depth layer, progress export/reset, responsive navigation, and CI regression checks.

## Primary scope references

- ISC2 CISSP Certification Exam Outline: https://www.isc2.org/certifications/cissp/cissp-certification-exam-outline
- ISC2 CISSP Exam Refresh FAQ: https://www.isc2.org/certifications/cissp/cissp-exam-refresh-faq
- ISC2 Code of Ethics: https://www.isc2.org/ethics

Supporting standards are listed in the site's Sources view and `data-meta.js`.
