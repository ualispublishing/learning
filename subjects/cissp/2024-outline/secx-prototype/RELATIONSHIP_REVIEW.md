# SecX relationship review gate

This file defines how typed semantic relationships are reviewed without turning search similarity, shared vocabulary, shared citations, coverage co-occurrence, or item-level correctness review into learner-facing curriculum claims.

## Current state

`RELATIONSHIP_REVIEW.json` remains the **reviewer-only** registry and currently contains **three approved draft relationships**. The learner-facing review surface (`next.html`) never loads that reviewer registry.

A separate promotion stage now exists for relationships that pass the review gate:

- `RELEASED_RELATIONSHIPS.json` is the dedicated prototype release artifact;
- `released-relationships.js` is the frozen learner-runtime representation of that artifact;
- `relationship-release-audit.py` verifies the promoted copy against the reviewer-approved records and release metadata;
- `relationship-lens.js` consumes only the released runtime copy;
- `relationship-browser-smoke.html` / `.sh` verify the reviewed Links surface through Chromium on desktop and 390px mobile.

The current prototype release artifact has `scope: secx-review-prototype`, `publication_state: prototype-released`, and contains the same three source-reviewed relationships. This is **prototype publication only**. It does not publish relationships into production CISSP Atlas, change the default surface, or make `RELATIONSHIP_REVIEW.json` learner-loadable.

### First reviewed and prototype-released set

The first relationship-specific review pass on 2026-09-10 approved these records:

- `REL-001`: objective `5.1` **depends-on** objective `1.8` for personnel-lifecycle-driven access changes. Evidence: current ISC2 objectives 1.8/5.1 and NIST SP 800-53 Rev. 5 personnel termination/transfer controls.
- `REL-002`: objective `7.6` is **evidenced-by** objective `7.2` because logging and monitoring provide operational evidence used across incident detection, response, mitigation, recovery, and lessons learned. Evidence: current ISC2 objectives 7.2/7.6 and NIST SP 800-61 Rev. 3.
- `REL-003`: objective `7.10` **depends-on** objective `1.7` because recovery strategy selection should follow business-continuity requirements and BIA-derived disruption impacts/allowable downtime. Evidence: current ISC2 objectives 1.7/7.10 and NIST SP 800-34 Rev. 1 section 3.4.1.

The reviewer records remain `release_state: draft`; they are not themselves the publication source. Promotion copies only the approved semantic content into the separate prototype release artifact after deterministic review. Exact-head browser validation is then required before that artifact is accepted as usable by the review surface.

## What item verification does not mean

`SEMANTIC_ITEM_AUDIT.json` and `SEMANTIC_RELEASE_ADDITIONS.json` verify learner-facing items for correctness, source fit, answer-key validity, and related release criteria. They do **not** certify arbitrary relationships between two otherwise verified items.

A pair of VERIFIED items therefore has no semantic edge unless the relationship itself receives separate review and, for learner-facing prototype use, separate promotion.

## Candidate evidence

A candidate may be proposed from a review lead such as:

- an explicit statement inside a reviewed Atlas item;
- a reviewer-identified relationship supported by named source evidence;
- an exact repeated term, shared citation, or coverage co-occurrence used only to surface a review lead.

Exact shared wording, co-citation, coverage counts/tags, search similarity, embeddings, fuzzy matching, or another heuristic may help identify candidates, but none of those may set `status: approved` automatically or enter the released relationship artifact directly.

## Durable endpoints

Relationship endpoints must use stable released IDs:

- CISSP objective IDs such as `1.9`;
- released review-card IDs such as `OBJ-1.9`, `HY-014`, `AI-005`, or `PX-020`;
- released standard-scenario IDs such as `Q-001` or `C-472`.

Temporary navigation/projection IDs are not durable curriculum IDs and cannot be relationship endpoints. This includes:

- `sub:<objective-id>:<index>`;
- `source:*` and `source-item:*` provenance nodes;
- `study:*` learner-state nodes;
- `due:*` schedule nodes;
- `coverage:*` corpus-exposure nodes;
- `relationship:*` UI projection nodes;
- pager/facet/search-result positions.

A provenance-only `source-item:scenario:<id>` is therefore not a semantic endpoint even though it refers to a stable released scenario underneath. A semantic relationship must target the stable scenario ID itself.

## Allowed semantic types

The review registry accepts only:

- `depends-on`
- `contrasts-with`
- `implemented-by`
- `mitigates`
- `measured-by`
- `evidenced-by`
- `practiced-by`

`contains` is intentionally excluded from this registry because hierarchy and explicit Atlas mappings already represent containment/provenance relationships directly.

## Required review fields

A non-rejected relationship record is expected to contain:

- `id`
- `from_id`
- `to_id`
- `type`
- `status`
- `rationale`
- `evidence`
- `release_state`

An `approved` record additionally requires reviewer identity, review date, and explicit evidence. Approval is still a reviewer-stage state; it does not itself authorize learner runtime loading.

## Promotion and publication rule

The learner runtime must never load `RELATIONSHIP_REVIEW.json`. Runtime integration consumes a separate released relationship artifact.

A relationship may appear in the SecX **review prototype** only when all of the following are true:

1. both endpoints are stable released IDs;
2. the relationship type is supported;
3. the relationship itself has explicit semantic review;
4. its evidence and rationale pass deterministic validation;
5. it is copied into the dedicated `RELEASED_RELATIONSHIPS.json` promotion artifact;
6. the runtime copy is exact and reviewer-registry isolation is preserved;
7. the exact candidate head passes deterministic and browser gates.

The current three records satisfy those prototype gates and are exposed only through the review-only **Links · 3** lens. The browser gate verifies visible-button and `L` entry, relationship detail, stable endpoint traversal back to normal objective context, Escape ascent, Atlas-progress isolation, separate graph evidence, and 390px mobile render/focus/viewport behavior.

This keeps candidate discovery, semantic review, prototype promotion, runtime publication, and any future production migration as separate stages.
