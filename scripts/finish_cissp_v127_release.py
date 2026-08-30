#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path('subjects/cissp/2024-outline/study-site')
QB = ROOT / 'question-bank'
TODAY = '2026-08-30'
RELEASE = '1.27.0'
CANDIDATE_HEAD = '17bff315baa0f5de701125a85cbc75257de481e2'
CANDIDATE_MERGE = '152dfce1a2a2074c1d99d8075f846f9e9eb1c804'
BOOKKEEPING_HEAD = '91a960dedf6ca529b0c4d95c229ab42ca6819c7a'
BOOKKEEPING_MERGE = '10a4a4a096af0a8752850f0b65b6fc493b39dfe8'


def loadj(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def savej(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')


# Preconditions: the branch already contains the staged v1.27 manifest/runtime promotion.
meta_raw = (ROOT / 'data-meta.js').read_text(encoding='utf-8').strip()
meta_pre = 'window.CISSP_META='
meta_marker = ';window.CISSP_CHUNKS=[];'
assert meta_raw.startswith(meta_pre) and meta_marker in meta_raw
meta = json.loads(meta_raw[len(meta_pre):meta_raw.index(meta_marker)])
assert meta['meta']['version'] == RELEASE
assert meta['meta']['question_count'] == 527
assert meta['meta']['question_bank_records'] == 528
assert meta['meta']['semantic_items_reviewed'] == 668

manifest = loadj(QB / 'RELEASED_BATCHES.json')
b29 = [b for b in manifest['released_batches'] if b.get('batch_id') == 'BATCH-029']
assert len(b29) == 1 and b29[0]['release_version'] == RELEASE and b29[0]['records'] == 16
semantic = loadj(ROOT / 'SEMANTIC_RELEASE_ADDITIONS.json')
assert semantic['release'] == RELEASE and semantic['total_items'] == 668

# Close Batch 029 candidate/bookkeeping evidence and mark it release-PR eligible.
p = QB / 'BATCH_029_REVIEW.json'
r = loadj(p)
assert r['records'] == 16 and r['standard_mcq'] == 16
assert r['semantic_review']['status'] == 'PASS'
assert r['candidate_validation']['candidate_pr_audit'] == 'PASS'
assert r['candidate_validation']['post_merge_exact_main_audit'] == 'PASS'
assert r['candidate_validation']['candidate_pages_isolation'] == 'PASS'
r['schema_version'] = max(int(r.get('schema_version', 0)), 7)
r['status'] = 'SEMANTIC_REVIEWED_RELEASE_PENDING_V1_27'
cv = r['candidate_validation']
cv.update({
    'final_bookkeeping_pr_number': 126,
    'final_bookkeeping_pr_head_sha': BOOKKEEPING_HEAD,
    'final_bookkeeping_pr_audit_workflow_run_id': 33334471118,
    'final_bookkeeping_pr_audit': 'PASS',
    'final_bookkeeping_merge_sha': BOOKKEEPING_MERGE,
    'final_bookkeeping_exact_main_audit_workflow_run_id': 33334622206,
    'final_bookkeeping_exact_main_audit': 'PASS',
    'final_bookkeeping_pages_workflow_run_id': 33334622157,
    'final_bookkeeping_pages_isolation': 'PASS',
    'promotion_allowed': True,
})
r['release_promotion'] = {
    'target_release': RELEASE,
    'status': 'PENDING_RELEASE_PR_VALIDATION',
    'required_before_authoritative': [
        'Native v1.27 release PR CISSP audit PASS on the exact final head',
        'Merge the exact validated release head',
        'Post-merge exact-main CISSP audit PASS',
        'Pages live fingerprint PASS for v1.27.0 / 527 standard / 472 manifest released / 1 Bellringer / released_only=true',
        'Final release evidence bookkeeping',
    ],
}
r['release_projection'] = {
    'records': 528,
    'standard_mcq': 527,
    'bellringers': 1,
    'difficulty_distribution': {'F': 41, 'E': 369, 'S': 117, 'B': 1},
    'manifest_records': 472,
    'semantic_items': 668,
    'explicit_enriched_subtopic_exposure': 306,
    'remaining_to_800': {'records': 272, 'F': 79, 'E': 111, 'S': 43, 'B': 39},
}
r['notes'] = [
    'All 16 Batch 029 records are original from public CISSP scope and registered standards with no external question seeds.',
    'Candidate PR #125, exact-main audit, and candidate Pages isolation passed.',
    'Candidate-bookkeeping PR #126 exact-head audit 33334471118, merge exact-main audit 33334622206, and Pages isolation 33334622157 passed.',
    'The public site remained v1.26.0 / 511 standard / 456 manifest released / 1 Bellringer / released_only=true through the complete candidate/bookkeeping chain.',
    'This review records v1.27 promotion eligibility; v1.27 is not authoritative until the release PR, post-merge exact-main audit, and live Pages fingerprint pass.',
]
savej(p, r)

# Question-bank release-candidate state.
p = QB / 'STATUS.json'
st = loadj(p)
st['schema_version'] = max(int(st.get('schema_version', 0)) + 1, 49)
st['updated'] = TODAY
st['release'] = RELEASE
st['released'].update({
    'bank_records': 528,
    'standard_mcq': 527,
    'bellringer_cases': 1,
    'manifest_released_records': 472,
    'difficulty_distribution': {'F': 41, 'E': 369, 'S': 117, 'B': 1},
})
st['latest_released_batch'] = {
    'batch_id': '029',
    'status': 'RELEASED_V1_27_0_PENDING_VERIFICATION',
    'records': 16,
    'standard_mcq': 16,
    'bellringer': 0,
    'difficulty_distribution': {'F': 0, 'E': 12, 'S': 4, 'B': 0},
    'primary_domain_distribution': {'1': 3, '2': 2, '3': 2, '4': 1, '5': 0, '6': 2, '7': 5, '8': 1},
    'answer_position_distribution': {'0': 4, '1': 4, '2': 4, '3': 4},
    'review': 'BATCH_029_REVIEW.json',
    'candidate_pr_number': 125,
    'candidate_pr_final_head_sha': CANDIDATE_HEAD,
    'candidate_pr_audit_workflow_run_id': 33330316959,
    'candidate_merge_commit_sha': CANDIDATE_MERGE,
    'candidate_post_merge_main_audit_workflow_run_id': 33330580189,
    'candidate_pages_isolation_workflow_run_id': 33330580084,
    'candidate_final_bookkeeping_pr_number': 126,
    'candidate_final_bookkeeping_pr_head_sha': BOOKKEEPING_HEAD,
    'candidate_final_bookkeeping_pr_audit_workflow_run_id': 33334471118,
    'candidate_final_bookkeeping_merge_sha': BOOKKEEPING_MERGE,
    'candidate_final_bookkeeping_main_audit_workflow_run_id': 33334622206,
    'candidate_final_bookkeeping_pages_workflow_run_id': 33334622157,
    'quality_gate_warnings': 0,
    'logical_batch_mix': 'PASS',
    'browser_smoke': 'PASS',
    'aggregate_gate': 'PASS',
    'explicit_subtopic_tags_after': 306,
    'release_pr_state': 'PENDING_EXACT_HEAD_VALIDATION',
    'public_runtime': 'PENDING',
}
st['candidate_batches'] = {}
st['pending_candidate_summary'] = {
    'records': 0,
    'standard_mcq': 0,
    'bellringer_cases': 0,
    'difficulty_distribution': {'F': 0, 'E': 0, 'S': 0, 'B': 0},
}
st['coverage'] = {
    'numbered_objectives_with_standard_mcq_exposure': '62/62',
    'mapped_subtopics': 344,
    'released_explicit_enriched_subtopic_exposure': 306,
    'released_explicit_enriched_subtopic_unexposed': 38,
    'candidate_inclusive_explicit_enriched_subtopic_exposure': 306,
    'candidate_inclusive_explicit_enriched_subtopic_unexposed': 38,
    'boundary': '306/344 is the v1.27 release-candidate explicit enriched-subtopic practice exposure after promoting Batch 029. This is authoring metadata, not a learner-mastery claim.',
}
st['release_verification'] = {
    'target_release': RELEASE,
    'status': 'PENDING_RELEASE_PR_VALIDATION',
    'previous_verified_public_release': '1.26.0',
    'previous_release_merge_sha': '25ff2935232687a573d1a60e9b9d5182af97294f',
    'previous_exact_main_audit_workflow_run_id': 33326374653,
    'previous_pages_workflow_run_id': 33326374656,
    'batch_029_candidate_pr_number': 125,
    'batch_029_candidate_pr_audit_workflow_run_id': 33330316959,
    'batch_029_candidate_main_audit_workflow_run_id': 33330580189,
    'batch_029_candidate_pages_isolation_workflow_run_id': 33330580084,
    'batch_029_bookkeeping_pr_number': 126,
    'batch_029_bookkeeping_pr_audit_workflow_run_id': 33334471118,
    'batch_029_bookkeeping_main_audit_workflow_run_id': 33334622206,
    'batch_029_bookkeeping_pages_workflow_run_id': 33334622157,
    'last_confirmed_public_release': '1.26.0',
    'last_confirmed_public_standard_questions': 511,
    'last_confirmed_public_manifest_released_records': 456,
    'last_confirmed_public_bellringers': 1,
    'last_confirmed_public_released_only': True,
    'expected_v1_27_live_fingerprint': {
        'version': RELEASE,
        'standard_questions': 527,
        'manifest_released_records': 472,
        'bellringers': 1,
        'released_only': True,
    },
}
st['remaining_to_target_from_released'] = {'bank_records': 272, 'F': 79, 'E': 111, 'S': 43, 'B': 39}
st['remaining_to_target_if_current_candidates_promote'] = {'bank_records': 272, 'F': 79, 'E': 111, 'S': 43, 'B': 39}
st['provisional_next_planned_batch'] = {
    'batch_id': '030',
    'basis_workflow_run_id': 33334622206,
    'basis_scope': 'Batch-029-bookkeeping-main; equivalent content basis for v1.27',
    'size': 16,
    'difficulty_target': {'E': 12, 'S': 4},
    'primary_domain_distribution': {'1': 5, '2': 0, '3': 5, '4': 0, '5': 0, '6': 0, '7': 5, '8': 1},
    'objective_targets': ['7.5', '7.7', '7.8', '1.12', '7.9', '7.12', '8.4', '1.2', '1.6', '1.9', '1.7', '3.10', '3.2', '3.4', '3.5', '3.3'],
    'boundary': 'Provisional until v1.27 release verification closes; then this becomes the released-only Batch 030 planning slate.',
}
st['next_priority'] = [
    'Validate the exact final v1.27 release PR head.',
    'Merge only that validated release head.',
    'Require exact-main CISSP audit and live Pages fingerprint for v1.27.0, then close final release evidence.',
]
savej(p, st)

# Release ledger.
p = ROOT / 'RELEASE_STATUS.json'
rs = loadj(p)
rs['release'] = RELEASE
rs['status'] = 'READY_FOR_STUDY'
rs['prepared_on'] = TODAY
rs['last_semantic_audit'] = TODAY
rs['scope'].update({
    'explicit_enriched_subtopic_exposure': 306,
    'explicit_enriched_subtopic_exposure_status': 'RELEASE_CANDIDATE_306',
    'standard_scenario_questions': 527,
    'bellringers': 1,
    'question_bank_records': 528,
    'released_difficulty_distribution': {'F': 41, 'E': 369, 'S': 117, 'B': 1},
    'standard_questions_with_four_option_rationales': 527,
    'semantic_items_reviewed': 668,
    'semantic_answer_key_reversals': 0,
})
rs['release_change'] = {
    'from': '1.26.0',
    'promoted_batch': '029',
    'promoted_standard_questions': 16,
    'promoted_difficulty_distribution': {'F': 0, 'E': 12, 'S': 4, 'B': 0},
    'primary_domain_distribution': {'1': 3, '2': 2, '3': 2, '4': 1, '5': 0, '6': 2, '7': 5, '8': 1},
    'semantic_review_status': 'PASS',
    'originality_duplicate_gate': 'PASS',
    'candidate_validation_pr': 125,
    'candidate_pr_final_head_sha': CANDIDATE_HEAD,
    'candidate_pr_audit_workflow_run_id': 33330316959,
    'candidate_merge_commit_sha': CANDIDATE_MERGE,
    'candidate_post_merge_main_workflow_run_id': 33330580189,
    'candidate_pages_isolation_workflow_run_id': 33330580084,
    'candidate_final_bookkeeping_pr_number': 126,
    'candidate_final_bookkeeping_pr_head_sha': BOOKKEEPING_HEAD,
    'candidate_final_bookkeeping_pr_audit_workflow_run_id': 33334471118,
    'candidate_final_bookkeeping_merge_sha': BOOKKEEPING_MERGE,
    'candidate_final_bookkeeping_main_audit_workflow_run_id': 33334622206,
    'candidate_final_bookkeeping_pages_workflow_run_id': 33334622157,
    'candidate_quality_gate_warnings': 0,
    'logical_batch_mix': 'PASS',
    'browser_smoke': 'PASS',
    'aggregate_gate': 'PASS',
    'explicit_enriched_subtopic_exposure_before': 305,
    'explicit_enriched_subtopic_exposure_after': 306,
    'objective_exposure': '62/62 numbered objectives have at least one standard MCQ exposure',
    'release_pr_state': 'PENDING_EXACT_HEAD_VALIDATION',
    'public_pages_runtime': 'PENDING',
}
rs['pending_candidate'] = None
rs['validation']['v1_27_release_evidence'] = 'subjects/cissp/2024-outline/study-site/question-bank/BATCH_029_REVIEW.json'
rs['question_bank_expansion_target'].update({
    'current_released_records': 528,
    'current_released_difficulty': {'F': 41, 'E': 369, 'S': 117, 'B': 1},
    'current_unreleased_candidates': 0,
    'candidate_inclusive_records': 528,
    'candidate_inclusive_difficulty': {'F': 41, 'E': 369, 'S': 117, 'B': 1},
    'remaining_from_released': {'records': 272, 'F': 79, 'E': 111, 'S': 43, 'B': 39},
    'remaining_if_current_candidates_promote': {'records': 272, 'F': 79, 'E': 111, 'S': 43, 'B': 39},
    'next_bias': 'Finish v1.27 release verification, then begin Batch 030 from the validated released-only planner state.',
    'provisional_next_planner_basis_workflow_run_id': 33334622206,
    'provisional_next_planner_scope': 'Batch-029-bookkeeping-main; equivalent content basis for v1.27',
    'provisional_next_planner_objectives': ['7.5', '7.7', '7.8', '1.12', '7.9', '7.12', '8.4', '1.2', '1.6', '1.9', '1.7', '3.10', '3.2', '3.4', '3.5', '3.3'],
    'provisional_next_planner_primary_domain_distribution': {'1': 5, '2': 0, '3': 5, '4': 0, '5': 0, '6': 0, '7': 5, '8': 1},
    'provisional_next_planner_difficulty_distribution': {'E': 12, 'S': 4},
})
dep = rs['deployment']
dep.update({
    'repository_release_candidate': RELEASE,
    'last_confirmed_public_pages_release': '1.26.0',
    'public_v1_27_verification_pending': True,
    'public_runtime_verified_for_v1_27': False,
    'latest_candidate_isolation_evidence': {
        'pages_workflow_run_id': 33334622157,
        'bookkeeping_merge_sha': BOOKKEEPING_MERGE,
        'version': '1.26.0',
        'standard_questions': 511,
        'manifest_released_records': 456,
        'bellringers': 1,
        'released_only': True,
    },
    'release_pr_exact_head_audit_workflow_run_id': None,
    'activation_status': 'v1.27.0 is a release candidate on the promotion branch. Public production remains the verified v1.26.0 release until the exact release head, post-merge main audit, and live Pages fingerprint all pass.',
})
rs['precision_boundary'] = 'The v1.27 release candidate contains 527 standard scenario questions, 1 Bellringer, 528 release-manifest bank records, and 668 semantically reviewed learner-facing item IDs with zero known keyed-answer reversals and no known remaining material factual error within the documented review boundary. It is not authoritative public v1.27 until post-merge and live Pages verification pass, and it does not guarantee passing the live adaptive CISSP exam.'
savej(p, rs)

# Cross-project continuation router: mutate only CISSP scope.
p = Path('PROJECT_TRACKS.json')
tracks = loadj(p)
cs = tracks['tracks']['CISSP-ATLAS']['current_scope']
cs.update({
    'version': RELEASE,
    'last_semantic_audit': TODAY,
    'explicit_enriched_subtopic_exposure': 306,
    'candidate_inclusive_explicit_enriched_subtopic_exposure': 306,
    'released_standard_questions': 527,
    'released_bellringers': 1,
    'released_bank_records': 528,
    'released_question_difficulty': {'F': 41, 'E': 369, 'S': 117, 'B': 1},
    'standard_questions_with_four_option_rationales': 527,
    'semantic_items_reviewed': 668,
    'semantic_answer_key_reversals': 0,
    'pending_candidate_records': 0,
    'candidate_inclusive_bank_records': 528,
    'candidate_inclusive_question_difficulty': {'F': 41, 'E': 369, 'S': 117, 'B': 1},
    'next_action': 'Validate and merge the exact v1.27 release head, then require exact-main and live Pages verification before final release evidence closure.',
    'next_batch': '030',
    'next_batch_scope': 'provisional-v1.27-released-only-after-verification',
    'next_batch_basis_workflow_run_id': 33334622206,
    'next_batch_target_difficulty': {'E': 12, 'S': 4},
    'public_release_verified': False,
    'latest_candidate_merge_sha': CANDIDATE_MERGE,
    'latest_candidate_pr_number': 125,
    'latest_candidate_pr_audit_workflow_run_id': 33330316959,
    'latest_candidate_main_audit_workflow_run_id': 33330580189,
    'latest_candidate_pages_isolation_workflow_run_id': 33330580084,
    'latest_candidate_bookkeeping_pr_number': 126,
    'latest_candidate_bookkeeping_pr_audit_workflow_run_id': 33334471118,
    'latest_candidate_bookkeeping_main_audit_workflow_run_id': 33334622206,
    'latest_candidate_bookkeeping_pages_workflow_run_id': 33334622157,
})
savej(p, tracks)

# Learner-facing release-candidate documentation.
(ROOT / 'README.md').write_text('''# CISSP Atlas — Current Outline Study Workflow

Unofficial, original study site mapped to the current public ISC2 CISSP exam outline (effective 2024-04-15).

## v1.27.0 release candidate

- 8 CISSP domains; official weights total **100%**.
- **62** numbered public objectives and **344** paraphrased subtopic checks.
- **306/344** checks with explicit enriched-subtopic practice exposure.
- **33** AI-security coverage areas and **140** layered retrieval cards.
- **527 released standard scenario questions + 1 Bellringer = 528 released bank records** in the v1.27 release candidate.
- Author-difficulty mix: **F41 / E369 / S117 / B1**.
- **527/527** standard questions have four-option teaching rationales.
- **668 learner-facing item IDs** in the combined semantic-audit ledger.
- **20** primary/reference sources.

Batch 029 completed candidate PR #125 and bookkeeping PR #126 with exact-head, exact-main, originality, logical-mix, browser, aggregate, and Pages-isolation controls passing. This branch promotes those 16 reviewed questions to v1.27.0. Public production remains the verified v1.26.0 release until this exact release head is validated, merged, and the live Pages fingerprint passes.

## Semantic-review boundary

The combined ledgers cover **668 learner-facing item IDs** after Batch 029 promotion. Batch 029 contributes 16 reviewed items. The release candidate records zero known keyed-answer reversals and zero known remaining material factual errors within the documented review boundary. This is an auditable quality claim, not an infallibility or exam-pass guarantee.

## Study workflow

Use **diagnose → retrieve → apply → repair → re-test later**. Run the diagnostic once for routing, retrieve before revealing, use Exam + Stretch for standard practice, commit confidence before answering, review all four rationales, repair high-confidence misses first, and use Bellringers separately as non-exam-representative integrative drills.

Keyboard review flow: **Space toggles reveal/hide; ←/→ move cards while hidden and layers while revealed; 1–4 grades the revealed card.**

## Question-bank expansion

The long-term target remains **800 records** with an authoring mix of 15% Foundation+, 60% Exam-calibrated, 20% Stretch, and 5% Bellringer. After Batch 029 promotion, remaining deficits are **F79 / E111 / S43 / B39**, or **272 records**. All 62 objectives have at least one standard-MCQ exposure. Explicit enriched-subtopic exposure is **306/344**; this is authoring coverage, not learner mastery.

Batch 030 is provisionally planned at E12/S4 across `7.5, 7.7, 7.8, 1.12, 7.9, 7.12, 8.4, 1.2, 1.6, 1.9, 1.7, 3.10, 3.2, 3.4, 3.5, 3.3`. Do not begin it as authoritative released-only work until v1.27 post-merge and public verification close.

## Continuous audit

`.github/workflows/cissp-study-site-audit.yml` enforces knowledge/schema consistency, semantic coverage, originality/duplicate controls, logical batch composition, planning, JavaScript syntax, rationales, static assets, interactive browser flows, and an aggregate gate. `.github/workflows/cissp-pages.yml` independently audits and assembles a released-only artifact and verifies the public runtime fingerprint.

## Accuracy boundary

The strongest warranted v1.27 release-candidate claim is: **no known material factual errors or incorrect keyed answers are recorded as remaining; 668 learner-facing item IDs have explicit semantic status, and the release records zero known keyed-answer reversals.** Standards and public scope can change, reviews can miss nuance, and ISC2's adaptive live item bank is not public.

## Primary scope references

- ISC2 CISSP Certification Exam Outline: https://www.isc2.org/certifications/cissp/cissp-certification-exam-outline
- ISC2 CISSP Exam Refresh FAQ: https://www.isc2.org/certifications/cissp/cissp-exam-refresh-faq
- ISC2 Code of Ethics: https://www.isc2.org/ethics
''', encoding='utf-8')

(ROOT / 'TOMORROW_START.md').write_text('''# CISSP Atlas — Start Here

Use this sequence the first time you open the current release candidate.

1. Run the diagnostic once if you do not already have a baseline. Treat it as routing, not an exam-readiness score.
2. Retrieve before revealing in the weakest domain.
3. Use the misconception layer on misses or hesitation.
4. Run 10–20 standard scenarios with **Exam + Stretch** selected.
5. Commit confidence before choosing an answer; repair high-confidence misses first.
6. Read all four option rationales.
7. Use a Bellringer only after a normal study block; it is non-exam-representative.
8. Re-test later rather than repeating immediately to recognition.

Keyboard: **Space toggles reveal/hide; ←/→ move cards when hidden and layers when revealed; 1–4 grades.**

## Current v1.27.0 scope

- 8 domains; official weights total 100%.
- 62 numbered public objectives.
- 344 mapped subtopic checks; 306/344 with explicit enriched-subtopic practice exposure.
- 33 AI-security coverage areas.
- 140 layered retrieval cards.
- **527 released standard scenario questions + 1 Bellringer = 528 question-bank records**.
- Difficulty mix: **F41 / E369 / S117 / B1**.
- Four-option teaching rationales on **527/527** standard questions.
- **668 semantically reviewed learner-facing item IDs**, with zero known keyed-answer reversals and no known remaining material factual error in the documented audit boundary.
- 20 primary/reference sources.

Batch 029 is promotion-eligible after candidate PR #125 and bookkeeping PR #126 completed exact-head, post-merge, and Pages-isolation controls. v1.27.0 still requires exact release-head validation, merge, exact-main validation, and the live Pages fingerprint before it is called the verified public release.

## Next authoring step

Batch 030 remains provisional until v1.27 verification closes. Its current E12/S4 target is `7.5, 7.7, 7.8, 1.12, 7.9, 7.12, 8.4, 1.2, 1.6, 1.9, 1.7, 3.10, 3.2, 3.4, 3.5, 3.3`.

See `RELEASE_STATUS.json` for machine-readable evidence and `PRECISION_AUDIT.md` for the accuracy boundary. CISSP Atlas is unofficial and does not guarantee a pass on the live adaptive exam.
''', encoding='utf-8')

(ROOT / 'PRECISION_AUDIT.md').write_text('''# CISSP Atlas Precision Audit — v1.27 Release Candidate

## Result

**Published-scope mapping: PASS. Batch 029 semantic/originality validation and candidate/bookkeeping closure: PASS within the documented audit boundary. v1.27 exact release-head, post-merge, and public runtime verification remain required before public verification is claimed.**

## v1.27.0 release-candidate scope

- 8/8 domains; official weights total 100%.
- 62/62 numbered public objectives.
- 344 paraphrased public-outline subtopic checks; **306/344** explicitly exposed by enriched-subtopic practice metadata.
- 33 AI-security coverage areas and 140 layered retrieval cards.
- **527 released standard scenario questions** in the promotion manifest.
- **1 released Bellringer**, explicitly non-exam-representative.
- **528 total released question-bank records** in the promotion manifest.
- 527/527 standard questions have four-option teaching rationales.
- 20 primary/reference sources.
- **668 learner-facing item IDs** in the combined semantic ledgers.
- Author-difficulty distribution: **F41 / E369 / S117 / B1**.

## Batch 029 validation closure

Batch 029 contributes 16 original standard questions, E12/S4, balanced answer positions 4/4/4/4, and primary-domain distribution D1=3, D2=2, D3=2, D4=1, D6=2, D7=5, D8=1. The review records 0 answer-key conflicts, 0 remaining source/objective mapping conflicts, 0 known material factual errors remaining, and 0 external question seeds.

Evidence chain:
- Candidate PR #125 exact head `17bff315baa0f5de701125a85cbc75257de481e2`; audit **33330316959: PASS**.
- Candidate merge `152dfce1a2a2074c1d99d8075f846f9e9eb1c804`; exact-main audit **33330580189: PASS**; Pages isolation **33330580084: PASS**.
- Candidate-bookkeeping PR #126 exact head `91a960dedf6ca529b0c4d95c229ab42ca6819c7a`; audit **33334471118: PASS**.
- Candidate-bookkeeping merge `10a4a4a096af0a8752850f0b65b6fc493b39dfe8`; exact-main audit **33334622206: PASS**; Pages isolation **33334622157: PASS**.

The bookkeeping Pages run verified that public production remained **v1.26.0 / 511 standard / 456 manifest released / 1 Bellringer / released_only=true** before promotion.

## Semantic audit

The combined semantic ledgers contain **668 learner-facing item IDs** after Batch 029 promotion. The release candidate records zero keyed-answer reversals and zero known material factual errors remaining after review within the documented boundary.

## Next expansion state

After v1.27 verification, the 800-record target leaves **F79 / E111 / S43 / B39**, or **272 records total**. Batch 030 is provisionally E12/S4 across `7.5, 7.7, 7.8, 1.12, 7.9, 7.12, 8.4, 1.2, 1.6, 1.9, 1.7, 3.10, 3.2, 3.4, 3.5, 3.3`.

## Accuracy boundary

The strongest warranted claim for the v1.27 documented audit boundary is: **No known material factual errors or incorrect keyed answers are recorded as remaining; 668 learner-facing item IDs have explicit semantic audit status, and the release candidate records zero known keyed-answer reversals.** This is not an absolute infallibility guarantee and does not guarantee passing the live adaptive CISSP exam.
''', encoding='utf-8')

# Final consistency markers before CI validates the exact branch state.
assert loadj(QB / 'RELEASED_BATCHES.json')['released_batches'][-1]['batch_id'] == 'BATCH-029'
assert loadj(ROOT / 'SEMANTIC_RELEASE_ADDITIONS.json')['total_items'] == 668
assert loadj(QB / 'STATUS.json')['released']['manifest_released_records'] == 472
assert loadj(ROOT / 'RELEASE_STATUS.json')['scope']['standard_scenario_questions'] == 527
assert loadj(Path('PROJECT_TRACKS.json'))['tracks']['CISSP-ATLAS']['current_scope']['version'] == RELEASE
print('Finished CISSP Atlas v1.27 release-candidate ledgers and documentation')
