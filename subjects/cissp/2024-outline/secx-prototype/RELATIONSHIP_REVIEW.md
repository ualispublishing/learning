# SecX relationship review gate

This draft file defines how future typed semantic relationships can be reviewed without turning search similarity, shared vocabulary, shared citations, coverage co-occurrence, or item-level correctness review into learner-facing curriculum claims.

## Current state

`RELATIONSHIP_REVIEW.json` is reviewer-only and currently contains **three approved draft relationships**. The learner-facing review surface (`next.html`) does not load it, and none of these relationships is published or learner-facing.

The current graph may display only relationships already explicit in released Atlas data, including hierarchy, objective/card mappings, objective/scenario mappings, exact released subtopic tags, and source provenance from `source_ids`.

### First reviewed draft set

The first relationship-specific review pass on 2026-09-10 approved these records for the reviewer queue only:

- `REL-001`: objective `5.1` **depends-on** objective `1.8` for personnel-lifecycle-driven access changes. Evidence: current ISC2 objectives 1.8/5.1 and NIST SP 800-53 Rev. 5 personnel termination/transfer controls.
- `REL-002`: objective `7.6` is **evidenced-by** objective `7.2` because logging and monitoring provide operational evidence used across incident detection, response, mitigation, recovery, and lessons learned. Evidence: current ISC2 objectives 7.2/7.6 and NIST SP 800-61 Rev. 3.
- `REL-003`: objective `7.10` **depends-on** objective `1.7` because recovery strategy selection should follow business-continuity requirements and BIA-derived disruption impacts/allowable downtime. Evidence: current ISC2 objectives 1.7/7.10 and NIST SP 800-34 Rev. 1 section 3.4.1.

Approval here means only that the relationship itself received an explicit source-backed semantic review. Every record remains `release_state: draft`. A separate released relationship artifact, promotion gate, runtime implementation, and exact-head browser validation are still required before any relationship may appear in the learner surface.

## What item verification does not mean

`SEMANTIC_ITEM_AUDIT.json` and `SEMANTIC_RELEASE_ADDITIONS.json` verify learner-facing items for correctness, source fit, answer-key validity, and related release criteria. They do **not** certify arbitrary relationships between two otherwise verified items.

A pair of VERIFIED items therefore has no semantic edge unless the relationship itself receives separate review.

## Candidate evidence

A future candidate may be proposed from a review lead such as:

- an explicit statement inside a reviewed Atlas item;
- a reviewer-identified relationship supported by named source evidence;
- an exact repeated term, shared citation, or coverage co-occurrence used only to surface a review lead.

Exact shared wording, co-citation, coverage counts/tags, search similarity, embeddings, fuzzy matching, or another heuristic may help identify candidates, but none of those may set `status: approved` automatically.

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
- pager/facet/search-result positions.

A provenance-only `source-item:scenario:<id>` is therefore not a semantic endpoint even though it refers to a stable released scenario underneath. A future semantic relationship must target the stable scenario ID itself.

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

An `approved` record additionally requires reviewer identity, review date, and explicit evidence. Approval is still **draft-only** in this prototype. A separate released relationship manifest and promotion gate would be required before learner-facing rendering.

## Publication rule

The current learner runtime must never load `RELATIONSHIP_REVIEW.json`. Future runtime integration must consume a separate released relationship artifact rather than treating this reviewer queue as published data.

No relationship is learner-facing until all of the following are true:

1. both endpoints are stable released IDs;
2. the relationship type is supported;
3. the relationship itself has explicit semantic review;
4. its evidence and rationale pass deterministic validation;
5. a dedicated released relationship artifact exists;
6. the exact candidate head passes deterministic and browser gates.

This keeps candidate discovery, semantic review, and publication as separate stages.
