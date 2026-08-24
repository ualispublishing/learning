# CISSP Atlas Precision Audit — 2026-08-23

## Result

**Published-scope mapping: PASS, with an explicit mastery boundary.**

The site is mapped to the current public ISC2 CISSP exam outline, effective April 15, 2024, plus ISC2's current cross-domain guidance for AI security.

### Deterministic scope checks

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
- Metadata counts are recomputed and compared with the declared release metadata so stale claims fail validation.

## Semantic review performed

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

## Accuracy boundary

The audit proves **published-outline mapping and internal consistency**. It does not prove that memorizing 140 cards is sufficient to pass CISSP, and the UI does not make that claim. ISC2 describes CISSP as experiential and does not guarantee that a candidate will pass. The outline also provides examples rather than disclosing a complete live item bank.

A listed subtopic in `coverage-detail.js` means the site tracks that area and can route study toward it. It does **not** mean the learner has demonstrated deep mastery merely because the term appears in the blueprint view. Deep mastery requires retrieval, distinction from confusable concepts, scenario application, and later re-testing.

## Study-quality controls

The v1.2 workflow includes retrieval-before-reveal layered cards, local spaced review, weak-objective and weighted-domain routing, a 16-question diagnostic used only for routing, original scenario feedback, a CISSP decision lens, expandable subtopic coverage, current AI coverage, the new precision-depth layer, progress export/reset, responsive navigation, and CI regression checks.

## Primary scope references

- ISC2 CISSP Certification Exam Outline: https://www.isc2.org/certifications/cissp/cissp-certification-exam-outline
- ISC2 CISSP Exam Refresh FAQ: https://www.isc2.org/certifications/cissp/cissp-exam-refresh-faq
- ISC2 Code of Ethics: https://www.isc2.org/ethics

Supporting standards are listed in the site's Sources view and `data-meta.js`.
