#!/usr/bin/env python3
import json, re
from collections import Counter
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
ROOT=REPO/'subjects/cissp/2024-outline/study-site'
QB=ROOT/'question-bank'
TARGET='1.28.0'
TODAY='2026-08-31'
BATCH_IDS=[f'C-{i}' for i in range(472,488)]
CANDIDATE_FILES=['question-bank/candidates/batch-030-a.jsonl','question-bank/candidates/batch-030-b.jsonl']
EXPECTED_FP={'version':TARGET,'standard_questions':543,'manifest_released_records':488,'bellringers':1,'released_only':True}


def require(ok,msg):
    if not ok: raise SystemExit(f'PRECONDITION FAILED: {msg}')

def load_json(path): return json.loads(path.read_text(encoding='utf-8'))
def write_json(path,obj): path.write_text(json.dumps(obj,separators=(',',':'),ensure_ascii=False)+'\n',encoding='utf-8')
def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]

def parse_meta(path):
    s=path.read_text(encoding='utf-8').strip(); pre='window.CISSP_META='; marker=';window.CISSP_CHUNKS=[];'
    require(s.startswith(pre) and marker in s,'data-meta.js wrapper')
    return json.loads(s[len(pre):s.index(marker)])
def write_meta(path,obj):
    path.write_text('window.CISSP_META='+json.dumps(obj,separators=(',',':'),ensure_ascii=False)+';window.CISSP_CHUNKS=[];\n',encoding='utf-8')

def replace_exact(path,old,new,label):
    s=path.read_text(encoding='utf-8')
    require(old in s,label)
    path.write_text(s.replace(old,new),encoding='utf-8')

# Load and validate the verified v1.27 + fully isolated Batch 030 starting point.
meta_path=ROOT/'data-meta.js'; meta=parse_meta(meta_path); mm=meta['meta']
release_path=ROOT/'RELEASE_STATUS.json'; release=load_json(release_path)
status_path=QB/'STATUS.json'; status=load_json(status_path)
manifest_path=QB/'RELEASED_BATCHES.json'; manifest=load_json(manifest_path)
sem_path=ROOT/'SEMANTIC_RELEASE_ADDITIONS.json'; sem=load_json(sem_path)
review_path=QB/'BATCH_030_REVIEW.json'; review=load_json(review_path)
tracks_path=REPO/'PROJECT_TRACKS.json'; tracks=load_json(tracks_path)

require(mm.get('version')=='1.27.0','metadata must start at v1.27.0')
require(release.get('release')=='1.27.0','release ledger must start at v1.27.0')
require(status.get('release')=='1.27.0','question-bank status must start at v1.27.0')
require(sem.get('release')=='1.27.0','semantic additions must start at v1.27.0')
require(any(b.get('batch_id')=='BATCH-029' for b in manifest.get('released_batches',[])),'BATCH-029 must be released')
require(not any(b.get('batch_id')=='BATCH-030' for b in manifest.get('released_batches',[])),'BATCH-030 must not already be released')
require('C-472' not in sem.get('items',{}),'C-472 must not already be in semantic release additions')
require(review.get('candidate_validation',{}).get('candidate_merge_commit_sha')=='c9d10cff98b296135767cc577622ab7fa97aaac0','Batch 030 candidate merge evidence mismatch')

rows=[]
for rel in CANDIDATE_FILES:
    rows += read_jsonl(ROOT/rel)
require([r.get('id') for r in rows]==BATCH_IDS,'Batch 030 IDs/order must be C-472..C-487')
require(len(rows)==16 and all(r.get('format')=='mcq' for r in rows),'Batch 030 must be 16 standard MCQs')
require(Counter(r.get('difficulty_tier') for r in rows)==Counter({'E':12,'S':4}),'Batch 030 difficulty must be E12/S4')
require(Counter(r.get('answer') for r in rows)==Counter({0:4,1:4,2:4,3:4}),'Batch 030 answer positions must be 4/4/4/4')
require(Counter(r.get('domain_primary') for r in rows)==Counter({1:5,3:5,7:5,8:1}),'Batch 030 primary-domain mix mismatch')

# Promote Batch 030 into the release manifest.
batch030={
 'batch_id':'BATCH-030','released_on':TODAY,'release_version':TARGET,
 'files':CANDIDATE_FILES,'review_files':['question-bank/BATCH_030_REVIEW.json'],
 'records':16,'standard_mcq':16,'bellringers':0,'difficulty':{'F':0,'E':12,'S':4,'B':0},
 'semantic_review':'PASS','originality_preflight':'PASS',
 'quality_gate_evidence':{
   'evidence_type':'native-candidate-pr-plus-exact-main-plus-final-bookkeeping',
   'candidate_pr_number':129,'candidate_pr_workflow_run_id':33426305066,
   'candidate_pr_head_sha':'c194be4b23b23c2dbc500d18a3380dc456b989d1',
   'candidate_post_merge_main_workflow_run_id':33442608747,
   'candidate_main_sha':'c9d10cff98b296135767cc577622ab7fa97aaac0',
   'candidate_pages_isolation_workflow_run_id':33442608732,
   'final_bookkeeping_pr_number':130,'final_bookkeeping_pr_workflow_run_id':33443706809,
   'final_bookkeeping_pr_head_sha':'97b12a18fb86e6ce14f6842e984bc95cf98f95f1',
   'final_bookkeeping_main_workflow_run_id':33443994068,
   'final_bookkeeping_pages_workflow_run_id':33443994077,
   'final_bookkeeping_sha':'774e30f21ae8f2d0f80c2647f673b78ab98d44e9',
   'warnings':0,'logical_batch_mix':'PASS','browser_smoke':'PASS','aggregate_gate':'PASS'
 },
 'coverage_effect':{'explicit_subtopic_tags_before':306,'explicit_subtopic_tags_after':306,'mapped_subtopics':344}
}
manifest['updated']=TODAY
manifest['released_batches'].append(batch030)
write_json(manifest_path,manifest)

# Extend the semantic release ledger to every promoted learner-facing item.
sem['release']=TARGET; sem['audit_date']=TODAY; sem['added_items']=384; sem['total_items']=684
if 'BATCH-030' not in sem['source_batches']: sem['source_batches'].append('BATCH-030')
sem['quality_gate_evidence'].append({
 'batch':'BATCH-030','evidence_type':'native-candidate-pr-plus-exact-main-plus-final-bookkeeping',
 'candidate_pr_number':129,'candidate_pr_workflow_run_id':33426305066,
 'candidate_pr_head_sha':'c194be4b23b23c2dbc500d18a3380dc456b989d1',
 'candidate_post_merge_main_workflow_run_id':33442608747,'candidate_main_sha':'c9d10cff98b296135767cc577622ab7fa97aaac0',
 'candidate_pages_isolation_workflow_run_id':33442608732,
 'final_bookkeeping_pr_number':130,'final_bookkeeping_pr_workflow_run_id':33443706809,
 'final_bookkeeping_pr_head_sha':'97b12a18fb86e6ce14f6842e984bc95cf98f95f1',
 'final_bookkeeping_main_workflow_run_id':33443994068,'final_bookkeeping_pages_workflow_run_id':33443994077,
 'final_bookkeeping_sha':'774e30f21ae8f2d0f80c2647f673b78ab98d44e9','warnings':0
})
for qid in BATCH_IDS: sem['items'][qid]={'status':'VERIFIED'}
sem['summary']={'verified':384,'verified_after_correction':0,'verified_with_source_scope_note':0,'answer_key_reversals':0,'material_factual_errors_remaining':0}
require(len(sem['items'])==384,'semantic additions must contain 384 promoted items')
write_json(sem_path,sem)

# Runtime metadata.
mm.update({'version':TARGET,'audited_on':TODAY,'question_count':543,'bellringer_count':1,'question_bank_records':544,'question_difficulty':{'F':41,'E':381,'S':121,'B':1},'semantic_items_reviewed':684,'semantic_answer_key_reversals':0})
write_meta(meta_path,meta)

# Batch 030 release-candidate evidence.
review['schema_version']=10
review['status']='SEMANTIC_REVIEWED_RELEASE_PENDING_V1_28'
cv=review['candidate_validation']
cv.update({
 'status':'PASS','final_bookkeeping_pr_number':130,'final_bookkeeping_pr_head_sha':'97b12a18fb86e6ce14f6842e984bc95cf98f95f1',
 'final_bookkeeping_pr_audit_workflow_run_id':33443706809,'final_bookkeeping_pr_audit':'PASS',
 'final_bookkeeping_merge_sha':'774e30f21ae8f2d0f80c2647f673b78ab98d44e9',
 'final_bookkeeping_exact_main_audit_workflow_run_id':33443994068,'final_bookkeeping_exact_main_audit':'PASS',
 'final_bookkeeping_pages_workflow_run_id':33443994077,'final_bookkeeping_pages_isolation':'PASS',
 'promotion_allowed_after_bookkeeping':True,'promotion_allowed':True
})
review['release_promotion']={
 'target_release':TARGET,'status':'PENDING_RELEASE_PR_VALIDATION','release_pr_number':None,'release_pr_final_head_sha':None,
 'release_pr_exact_head_audit_workflow_run_id':None,'release_merge_commit_sha':None,'post_promotion_exact_main_audit_workflow_run_id':None,
 'public_pages_workflow_run_id':None,'verified_live_fingerprint':None,
 'required_before_authoritative':['Native v1.28 release PR CISSP audit PASS on the exact final head','Merge the exact validated release head','Post-merge exact-main CISSP audit PASS','Pages live fingerprint PASS for v1.28.0 / 543 standard / 488 manifest released / 1 Bellringer / released_only=true','Final release evidence bookkeeping']
}
review['release_projection']={'records':544,'standard_mcq':543,'bellringers':1,'difficulty_distribution':{'F':41,'E':381,'S':121,'B':1},'manifest_records':488,'semantic_items':684,'explicit_enriched_subtopic_exposure':306,'remaining_to_800':{'records':256,'F':79,'E':99,'S':39,'B':39}}
review['notes']=[
 'All 16 Batch 030 records are original from public CISSP scope and registered public standards/guidance with no external question seeds.',
 'Candidate PR #129, exact-main audit, and candidate Pages isolation passed with zero originality warnings.',
 'Bookkeeping PR #130 exact head 97b12a18fb86e6ce14f6842e984bc95cf98f95f1, audit 33443706809, merge 774e30f21ae8f2d0f80c2647f673b78ab98d44e9, exact-main audit 33443994068, and Pages isolation 33443994077 passed.',
 'Public production remained v1.27.0 / 527 standard / 472 manifest released / 1 Bellringer / released_only=true through the complete candidate/bookkeeping chain.',
 'This review records v1.28 promotion eligibility; v1.28 is not authoritative until the release PR, post-merge exact-main audit, and live Pages fingerprint pass.'
]
write_json(review_path,review)

# Machine-readable question-bank release state.
status['schema_version']=52; status['updated']=TODAY; status['release']=TARGET
status['released']={'bank_records':544,'standard_mcq':543,'bellringer_cases':1,'manifest_released_records':488,'difficulty_distribution':{'F':41,'E':381,'S':121,'B':1},'base_classification_manifest':'RELEASED_QUESTION_CLASSIFICATION.json','released_batch_manifest':'RELEASED_BATCHES.json'}
status['latest_released_batch']={
 'batch_id':'030','status':'RELEASED_V1_28_0_PENDING_VERIFICATION','records':16,'standard_mcq':16,'bellringer':0,
 'difficulty_distribution':{'F':0,'E':12,'S':4,'B':0},'primary_domain_distribution':{'1':5,'2':0,'3':5,'4':0,'5':0,'6':0,'7':5,'8':1},
 'answer_position_distribution':{'0':4,'1':4,'2':4,'3':4},'review':'BATCH_030_REVIEW.json',
 'candidate_pr_number':129,'candidate_pr_final_head_sha':'c194be4b23b23c2dbc500d18a3380dc456b989d1','candidate_pr_audit_workflow_run_id':33426305066,
 'candidate_merge_commit_sha':'c9d10cff98b296135767cc577622ab7fa97aaac0','candidate_post_merge_main_audit_workflow_run_id':33442608747,'candidate_pages_isolation_workflow_run_id':33442608732,
 'candidate_final_bookkeeping_pr_number':130,'candidate_final_bookkeeping_pr_head_sha':'97b12a18fb86e6ce14f6842e984bc95cf98f95f1','candidate_final_bookkeeping_pr_audit_workflow_run_id':33443706809,
 'candidate_final_bookkeeping_merge_sha':'774e30f21ae8f2d0f80c2647f673b78ab98d44e9','candidate_final_bookkeeping_main_audit_workflow_run_id':33443994068,'candidate_final_bookkeeping_pages_workflow_run_id':33443994077,
 'quality_gate_warnings':0,'logical_batch_mix':'PASS','browser_smoke':'PASS','aggregate_gate':'PASS','explicit_subtopic_tags_after':306,'release_pr_state':'PENDING_EXACT_HEAD_VALIDATION','public_runtime':'PENDING'
}
status['candidate_batches']={}; status['pending_candidate_summary']={'records':0,'standard_mcq':0,'bellringer_cases':0,'difficulty_distribution':{'F':0,'E':0,'S':0,'B':0}}
status['coverage']={'numbered_objectives_with_standard_mcq_exposure':'62/62','mapped_subtopics':344,'released_explicit_enriched_subtopic_exposure':306,'released_explicit_enriched_subtopic_unexposed':38,'candidate_inclusive_explicit_enriched_subtopic_exposure':306,'candidate_inclusive_explicit_enriched_subtopic_unexposed':38,'boundary':'306/344 is the v1.28 release-candidate explicit enriched-subtopic practice exposure after promoting Batch 030. This is authoring metadata, not a learner-mastery claim.'}
status['release_verification']={
 'target_release':TARGET,'status':'PENDING_RELEASE_PR_VALIDATION','previous_verified_public_release':'1.27.0','previous_release_merge_sha':'7791e9cea3fa67048bc56e02c6710167a6adc4ef',
 'previous_exact_main_audit_workflow_run_id':33338429753,'previous_pages_workflow_run_id':33338429738,
 'batch_030_candidate_pr_number':129,'batch_030_candidate_pr_audit_workflow_run_id':33426305066,'batch_030_candidate_main_audit_workflow_run_id':33442608747,'batch_030_candidate_pages_isolation_workflow_run_id':33442608732,
 'batch_030_bookkeeping_pr_number':130,'batch_030_bookkeeping_pr_audit_workflow_run_id':33443706809,'batch_030_bookkeeping_main_audit_workflow_run_id':33443994068,'batch_030_bookkeeping_pages_workflow_run_id':33443994077,
 'last_confirmed_public_release':'1.27.0','last_confirmed_public_standard_questions':527,'last_confirmed_public_manifest_released_records':472,'last_confirmed_public_bellringers':1,'last_confirmed_public_released_only':True,
 'expected_v1_28_live_fingerprint':EXPECTED_FP
}
status['remaining_to_target_from_released']={'bank_records':256,'F':79,'E':99,'S':39,'B':39}; status['remaining_to_target_if_current_candidates_promote']=dict(status['remaining_to_target_from_released'])
status['provisional_next_planned_batch']={'batch_id':'031','basis_workflow_run_id':33443994068,'basis_scope':'Batch-030-bookkeeping-main; equivalent content basis for v1.28','size':16,'difficulty_target':{'E':12,'S':4},'primary_domain_distribution':{'1':3,'2':0,'3':2,'4':1,'5':4,'6':2,'7':4,'8':0},'objective_targets':['7.6','3.7','4.2','1.3','5.1','5.3','7.1','1.5','7.2','5.4','7.10','1.8','5.2','6.3','6.5','3.8'],'boundary':'Provisional until v1.28 release verification closes; then regenerate the released-only Batch 031 planning slate.'}
status['next_priority']=['Validate the exact final v1.28 release PR head.','Merge only that validated release head.','Require exact-main CISSP audit and live Pages fingerprint for v1.28.0, then close final release evidence.']
write_json(status_path,status)

# Release ledger. Preserve workflow/features, replace release/candidate/accounting surfaces.
release['release']=TARGET; release['prepared_on']=TODAY; release['last_semantic_audit']=TODAY
release['scope'].update({'explicit_enriched_subtopic_exposure':306,'explicit_enriched_subtopic_exposure_status':'RELEASE_CANDIDATE_306','standard_scenario_questions':543,'bellringers':1,'question_bank_records':544,'released_difficulty_distribution':{'F':41,'E':381,'S':121,'B':1},'standard_questions_with_four_option_rationales':543,'semantic_items_reviewed':684,'semantic_answer_key_reversals':0})
release['release_change']={
 'from':'1.27.0','promoted_batch':'030','promoted_standard_questions':16,'promoted_difficulty_distribution':{'F':0,'E':12,'S':4,'B':0},'primary_domain_distribution':{'1':5,'2':0,'3':5,'4':0,'5':0,'6':0,'7':5,'8':1},
 'semantic_review_status':'PASS','originality_duplicate_gate':'PASS','candidate_validation_pr':129,'candidate_pr_final_head_sha':'c194be4b23b23c2dbc500d18a3380dc456b989d1','candidate_pr_audit_workflow_run_id':33426305066,
 'candidate_merge_commit_sha':'c9d10cff98b296135767cc577622ab7fa97aaac0','candidate_post_merge_main_workflow_run_id':33442608747,'candidate_pages_isolation_workflow_run_id':33442608732,
 'candidate_final_bookkeeping_pr_number':130,'candidate_final_bookkeeping_pr_head_sha':'97b12a18fb86e6ce14f6842e984bc95cf98f95f1','candidate_final_bookkeeping_pr_audit_workflow_run_id':33443706809,
 'candidate_final_bookkeeping_merge_sha':'774e30f21ae8f2d0f80c2647f673b78ab98d44e9','candidate_final_bookkeeping_main_audit_workflow_run_id':33443994068,'candidate_final_bookkeeping_pages_workflow_run_id':33443994077,
 'candidate_quality_gate_warnings':0,'logical_batch_mix':'PASS','browser_smoke':'PASS','aggregate_gate':'PASS','explicit_enriched_subtopic_exposure_before':306,'explicit_enriched_subtopic_exposure_after':306,
 'objective_exposure':'62/62 numbered objectives have at least one standard MCQ exposure','release_pr_state':'PENDING_EXACT_HEAD_VALIDATION','public_pages_runtime':'PENDING'
}
release['pending_candidate']=None
release['validation']['batch_030_candidate_evidence']='subjects/cissp/2024-outline/study-site/question-bank/BATCH_030_REVIEW.json'; release['validation']['v1_28_release_evidence']='subjects/cissp/2024-outline/study-site/question-bank/BATCH_030_REVIEW.json'
qbt=release['question_bank_expansion_target']; qbt.update({'current_released_records':544,'current_released_difficulty':{'F':41,'E':381,'S':121,'B':1},'current_unreleased_candidates':0,'candidate_inclusive_records':544,'candidate_inclusive_difficulty':{'F':41,'E':381,'S':121,'B':1},'remaining_from_released':{'records':256,'F':79,'E':99,'S':39,'B':39},'remaining_if_current_candidates_promote':{'records':256,'F':79,'E':99,'S':39,'B':39},'next_bias':'Finish v1.28 release verification, then begin Batch 031 from the validated released-only planner state.','provisional_next_planner_basis_workflow_run_id':33443994068,'provisional_next_planner_scope':'Batch-030-bookkeeping-main; equivalent content basis for v1.28','provisional_next_planner_objectives':['7.6','3.7','4.2','1.3','5.1','5.3','7.1','1.5','7.2','5.4','7.10','1.8','5.2','6.3','6.5','3.8'],'provisional_next_planner_primary_domain_distribution':{'1':3,'2':0,'3':2,'4':1,'5':4,'6':2,'7':4,'8':0},'provisional_next_planner_difficulty_distribution':{'E':12,'S':4}})
dep=release['deployment']; dep.update({'repository_release':'1.27.0','repository_release_candidate':TARGET,'last_confirmed_public_pages_release':'1.27.0','release_pr_exact_head_audit_workflow_run_id':None,'public_v1_28_verification_pending':True,'public_runtime_verified_for_v1_28':False,'activation_status':'v1.28.0 is a release candidate on the promotion branch. Public production remains the verified v1.27.0 release until the exact release head, post-merge main audit, and live Pages fingerprint all pass.'})
release['precision_boundary']='The v1.28 release candidate contains 543 standard scenario questions, 1 Bellringer, 544 release-manifest bank records, and 684 semantically reviewed learner-facing item IDs with zero known keyed-answer reversals and no known remaining material factual error within the documented review boundary. It is not authoritative public v1.28 until post-merge and live Pages verification pass, and it does not guarantee passing the live adaptive CISSP exam.'
write_json(release_path,release)

# Continuation router.
cis=tracks['tracks']['CISSP-ATLAS']; cs=cis['current_scope']
cs.update({'version':TARGET,'last_semantic_audit':TODAY,'explicit_enriched_subtopic_exposure':306,'candidate_inclusive_explicit_enriched_subtopic_exposure':306,'released_standard_questions':543,'released_bellringers':1,'released_bank_records':544,'released_question_difficulty':{'F':41,'E':381,'S':121,'B':1},'standard_questions_with_four_option_rationales':543,'semantic_items_reviewed':684,'pending_candidate_records':0,'candidate_inclusive_bank_records':544,'candidate_inclusive_question_difficulty':{'F':41,'E':381,'S':121,'B':1},'next_action':'Validate and merge the exact v1.28 release head, then require exact-main and live Pages verification before final release evidence closure.','next_batch':'031','next_batch_scope':'provisional-v1.28-released-only-after-verification','next_batch_basis_workflow_run_id':33443994068,'next_batch_target_difficulty':{'E':12,'S':4},'next_batch_primary_domain_distribution':{'1':3,'2':0,'3':2,'4':1,'5':4,'6':2,'7':4,'8':0},'next_batch_objective_targets':['7.6','3.7','4.2','1.3','5.1','5.3','7.1','1.5','7.2','5.4','7.10','1.8','5.2','6.3','6.5','3.8'],'public_release_verified':False,'verified_release_merge_sha':'7791e9cea3fa67048bc56e02c6710167a6adc4ef','verified_release_pr_number':127,'verified_release_pr_audit_workflow_run_id':33338110246,'verified_release_main_audit_workflow_run_id':33338429753,'verified_release_pages_workflow_run_id':33338429738,'latest_candidate_merge_sha':'c9d10cff98b296135767cc577622ab7fa97aaac0','latest_candidate_pr_number':129,'latest_candidate_pr_final_head_sha':'c194be4b23b23c2dbc500d18a3380dc456b989d1','latest_candidate_pr_audit_workflow_run_id':33426305066,'latest_candidate_main_audit_workflow_run_id':33442608747,'latest_candidate_pages_isolation_workflow_run_id':33442608732,'latest_candidate_bookkeeping_pr_number':130,'latest_candidate_bookkeeping_pr_audit_workflow_run_id':33443706809,'latest_candidate_bookkeeping_main_audit_workflow_run_id':33443994068,'latest_candidate_bookkeeping_pages_workflow_run_id':33443994077})
tracks['updated']=TODAY
write_json(tracks_path,tracks)

# Learner-facing handoff docs: exact marker wording intentionally matches audit.py.
(ROOT/'README.md').write_text(f'''# CISSP Atlas — Current Outline Study Workflow\n\nUnofficial, original study site mapped to the current public ISC2 CISSP exam outline (effective 2024-04-15).\n\n## v{TARGET} release candidate\n\n- 8 domains; official weights total **100%**.\n- **62** numbered objectives and **344** paraphrased subtopic checks.\n- **306/344** checks with explicit enriched-subtopic practice exposure.\n- **33** AI-security coverage areas and **140** layered retrieval cards.\n- **543 released standard scenario questions + 1 Bellringer = 544 released bank records** in the v1.28 release candidate.\n- Author-difficulty mix: **F41 / E381 / S121 / B1**.\n- **543/543** standard questions have four-option teaching rationales.\n- **684 learner-facing item IDs** in the combined semantic-audit ledger.\n- **20** primary/reference sources.\n\nBatch 030 completed candidate PR #129 and bookkeeping PR #130 with exact-head, exact-main, originality, logical-mix, browser, aggregate, and Pages-isolation controls passing. This branch promotes those 16 reviewed questions to v1.28.0. Public production remains the verified v1.27.0 release until this exact release head is validated, merged, and the live Pages fingerprint passes.\n\n## Study workflow\nUse **diagnose → retrieve → apply → repair → re-test later**. Run the diagnostic once for routing, retrieve before revealing, use Exam + Stretch for standard practice, commit confidence before answering, review all four rationales, repair high-confidence misses first, and use Bellringers separately as non-exam-representative integrative drills.\n\n## Expansion state\nAfter v1.28 verification, the 800-record target leaves **F79 / E99 / S39 / B39**, or **256 records**. Batch 031 remains provisional until the verified released-only v1.28 planner is regenerated.\n\n## Accuracy boundary\nNo known material factual errors or incorrect keyed answers are recorded as remaining within the documented review boundary; **684 learner-facing item IDs** have explicit semantic status. This is not an infallibility or exam-pass guarantee.\n''',encoding='utf-8')
(ROOT/'TOMORROW_START.md').write_text(f'''# CISSP Atlas — Start Here\n\n1. Run the diagnostic once if you do not already have a baseline.\n2. Retrieve before revealing in the weakest domain.\n3. Use the misconception layer on misses or hesitation.\n4. Run 10–20 standard scenarios with **Exam + Stretch** selected.\n5. Commit confidence before choosing an answer; repair high-confidence misses first.\n6. Read all four option rationales.\n7. Use a Bellringer only after a normal study block; it is non-exam-representative.\n8. Re-test later rather than repeating immediately to recognition.\n\n## Current v{TARGET} scope\n- **543 released standard scenario questions + 1 Bellringer = 544 question-bank records**.\n- Difficulty mix **F41 / E381 / S121 / B1**.\n- **684 semantically reviewed learner-facing item IDs**.\n- 306/344 explicit enriched-subtopic practice exposure.\n\nBatch 030 is promotion-eligible after its complete candidate and bookkeeping chains passed. v1.28.0 still requires exact release-head validation, merge, exact-main validation, and the live Pages fingerprint before it is the verified public release. Batch 031 remains provisional until then.\n''',encoding='utf-8')
(ROOT/'PRECISION_AUDIT.md').write_text(f'''# CISSP Atlas Precision Audit — v{TARGET} Release Candidate\n\n## Result\n**Published-scope mapping: PASS. Batch 030 semantic/originality validation and candidate/bookkeeping closure: PASS within the documented audit boundary. v1.28 exact release-head, post-merge, and public runtime verification remain required before public verification is claimed.**\n\n## v{TARGET} release-candidate scope\n- 8/8 domains; official weights total 100%.\n- 62/62 numbered public objectives.\n- 344 paraphrased subtopic checks; **306/344** explicitly exposed by enriched-subtopic practice metadata.\n- 33 AI-security coverage areas and 140 layered retrieval cards.\n- **543 released standard scenario questions** in the promotion manifest.\n- **1 released Bellringer**, explicitly non-exam-representative.\n- **544 total released question-bank records** in the promotion manifest.\n- 543/543 standard questions have four-option teaching rationales.\n- **684 learner-facing item IDs** in the combined semantic ledgers.\n- Author-difficulty distribution **F41 / E381 / S121 / B1**.\n\n## Batch 030 evidence\nCandidate PR #129 head `c194be4b23b23c2dbc500d18a3380dc456b989d1` passed audit **33426305066**. Candidate merge `c9d10cff98b296135767cc577622ab7fa97aaac0` passed exact-main audit **33442608747** and Pages isolation **33442608732**. Bookkeeping PR #130 head `97b12a18fb86e6ce14f6842e984bc95cf98f95f1` passed audit **33443706809**; merge `774e30f21ae8f2d0f80c2647f673b78ab98d44e9` passed exact-main audit **33443994068** and Pages isolation **33443994077**.\n\n## Accuracy boundary\nNo known material factual errors or incorrect keyed answers are recorded as remaining within this documented review boundary. **684 learner-facing item IDs** have explicit semantic status and the release candidate records zero known keyed-answer reversals. This does not guarantee passing the live adaptive CISSP exam.\n''',encoding='utf-8')

# Runtime labels/version assertions.
replace_exact(ROOT/'index.html','CURRENT CISSP OUTLINE · AUDITED 2026-08-30 · RELEASE v1.27','CURRENT CISSP OUTLINE · AUDITED 2026-08-31 · RELEASE v1.28','index release eyebrow')
replace_exact(ROOT/'index.html','v1.27 · local-first progress','v1.28 · local-first progress','index footer version')
replace_exact(ROOT/'product-polish.js',"v1.27 · local progress","v1.28 · local progress",'product polish footer')
replace_exact(ROOT/'browser-smoke.html',"includes('v1.27')","includes('v1.28')",'browser smoke release assertion')

print('Built CISSP Atlas v1.28.0 release candidate: 543 standard / 488 manifest / 1 Bellringer / 544 bank / 684 semantic items')
