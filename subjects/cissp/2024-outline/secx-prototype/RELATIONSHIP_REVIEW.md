# SecX relationship review gate

This draft file defines how future typed semantic relationships can be reviewed without turning search similarity, shared vocabulary, shared citations, or item-level correctness review into learner-facing curriculum claims.

## Current state

`RELATIONSHIP_REVIEW.json` is reviewer-only and currently contains **zero** candidate, approved, or released relationships. The learner-facing review surface (`next.html`) does not load it.

The current graph may display only relationships already explicit in released Atlas data, including hierarchy, objective/card mappings, objective/scenario mappings, exact released subtopic tags, and source provenance from `source_ids`.

## What item verification does not mean

`SEMANTIC_ITEM_AUDIT.json` and `SEMANTIC_RELEASE_ADDITIONS.json` verify learner-facing items for correctness, source fit, answer-key validity, and related release criteria. They do **not** certify arbitrary relationships between two otherwise verified items.

A pair of VERIFIED items therefore has no semantic edge unless the relationship itself receives separate review.

## Candidate evidence

A future candidate may be proposed from a review lead such as:

- an explicit statement inside a reviewed Atlas item;
- a reviewer-identified relationship supported by named source evidence;
- an exact repeated term or shared citation used only to surface a review lead.

Exact shared wording, co-citation, search similarity, embeddings, fuzzy matching, or another heuristic may help identify candidates, but none of those may set `status: approved` automatically.

## Durable endpoints

Relationship endpoints must use stable released IDs:

- CISSP objective IDs such as `1.9`;
- released review-card IDs such as `OBJ-1.9`, `HY-014`, `AI-005`, or `PX-020`;
- released standard-scenario IDs such as `Q-001` or `C-472`.

Temporary navigation IDs such as `sub:<objective-id>:<index>`, pager IDs, learner-state lens IDs, source-lens IDs, and search-result positions are not durable curriculum IDs and cannot be relationship endpoints.

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
