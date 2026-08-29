#!/usr/bin/env python3
import json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'subjects/cissp/2024-outline/study-site'
QB=SITE/'question-bank'
DATE='2026-08-29'
VERSION='1.25.0'
BATCH='027'

EVIDENCE={
 'candidate_pr_number':107,
 'candidate_pr_final_head_sha':'efae9fb1ebfb13092b9c590696cdc8ed1b3f3022',
 'candidate_pr_audit_workflow_run_id':33274571412,
 'candidate_merge_commit_sha':'57faaf1edd9cb4ed7aba89722511f2e99be38c29',
 'candidate_post_merge_main_workflow_run_id':33274739859,
 'candidate_pages_isolation_workflow_run_id':33274739801,
 'final_bookkeeping_pr_number':109,
 'final_bookkeeping_pr_head_sha':'60444b65cb8ded6734e41022133b6a6f18ebed52',
 'final_bookkeeping_pr_audit_workflow_run_id':33279472975,
 'final_bookkeeping_merge_sha':'61ec99d94bbbd592be1b391db41b88be6b5e91d1',
 'final_bookkeeping_main_audit_workflow_run_id':33279600905,
 'final_bookkeeping_pages_workflow_run_id':33279600874,
}

NEXT_OBJECTIVES=['4.1','2.6','1.3','2.5','1.4','1.5','1.8','8.3','1.1','3.6','3.8','3.9','4.3','5.6','7.11','7.12']
NEXT_DOMAINS={'1':5,'2':2,'3':3,'4':2,'5':1,'6':0,'7':2,'8':1}


def load(path): return json.loads(path.read_text(encoding='utf-8'))
def save(path,obj): path.write_text(json.dumps(obj,separators=(',',':'),ensure_ascii=False),encoding='utf-8')

def replace_once(text,old,new,label):
    n=text.count(old)
    if n < 1: raise SystemExit(f'{label}: missing expected text: {old!r}')
    return text.replace(old,new)

# 1) Batch 027 review -> promotion-eligible release state.
p=QB/'BATCH_027_REVIEW.json'; r=load(p)
r['schema_version']=5
r['status']='SEMANTIC_REVIEWED_RELEASE_PENDING_V1_25'
cv=r['candidate_validation']
cv.update({
 'final_bookkeeping_pr_number':109,
 'final_bookkeeping_pr_head_sha':EVIDENCE['final_bookkeeping_pr_head_sha'],
 'final_bookkeeping_pr_audit_workflow_run_id':EVIDENCE['final_bookkeeping_pr_audit_workflow_run_id'],
 'final_bookkeeping_pr_audit':'PASS',
 'final_bookkeeping_merge_sha':EVIDENCE['final_bookkeeping_merge_sha'],
 'final_bookkeeping_exact_main_audit_workflow_run_id':EVIDENCE['final_bookkeeping_main_audit_workflow_run_id'],
 'final_bookkeeping_exact_main_audit':'PASS',
 'final_bookkeeping_pages_workflow_run_id':EVIDENCE['final_bookkeeping_pages_workflow_run_id'],
 'final_bookkeeping_pages_isolation':'PASS',
 'promotion_allowed':True,
})
cv.pop('promotion_allowed_after_bookkeeping',None)
r['coverage_effect']={'explicit_subtopic_tags_before':304,'explicit_subtopic_tags_after':304,'total_mapped_subtopics':344,'new_explicit_tags':0,'boundary':'Released v1.25 would retain explicit enriched-subtopic practice exposure at 304/344 while adding scenario depth. This is an authoring metadata metric, not a learner-mastery claim.'}
r.pop('candidate_inclusive_projection',None)
r['release_projection']={'records':496,'standard_mcq':495,'bellringers':1,'difficulty_distribution':{'F':41,'E':345,'S':109,'B':1},'manifest_records':440,'semantic_items':636,'remaining_to_800':{'records':304,'F':79,'E':135,'S':51,'B':39}}
r['release_promotion']={'target_release':'1.25.0','status':'PENDING_RELEASE_PR_VALIDATION','required_before_authoritative':['Native v1.25 release PR CISSP audit PASS on exact final head','Merge exact validated release head','Post-merge exact-main CISSP audit PASS','Pages live fingerprint PASS for v1.25.0 / 495 standard / 440 manifest released / 1 Bellringer / released_only=true','Final release evidence bookkeeping']}
r['notes']=['All 16 records are original from public scope and registered standards with no external question seeds.','Candidate PR, candidate exact-main, candidate Pages isolation, final-bookkeeping PR, final-bookkeeping exact-main, and final-bookkeeping Pages isolation all passed.','C-437 source provenance was corrected before the authoritative candidate head; its answer, scenario, and rationale did not require correction.','This file records promotion eligibility, not a claim that v1.25 is authoritative before release-state and live post-merge verification pass.']
save(p,r)

# 2) Append Batch 027 to authoritative released-batch manifest.
p=QB/'RELEASED_BATCHES.json'; m=load(p)
if any(b.get('batch_id')=='BATCH-027' for b in m['released_batches']): raise SystemExit('BATCH-027 already released')
m['updated']=DATE
m['released_batches'].append({
 'batch_id':'BATCH-027','released_on':DATE,'release_version':VERSION,
 'files':['question-bank/candidates/batch-027-a.jsonl','question-bank/candidates/batch-027-b.jsonl','question-bank/candidates/batch-027-c.jsonl','question-bank/candidates/batch-027-d.jsonl'],
 'review_files':['question-bank/BATCH_027_REVIEW.json'],'records':16,'standard_mcq':16,'bellringers':0,
 'difficulty':{'F':0,'E':12,'S':4,'B':0},'semantic_review':'PASS','originality_preflight':'PASS',
 'quality_gate_evidence':{
   'evidence_type':'native-candidate-pr-plus-exact-main-plus-final-bookkeeping',
   'candidate_pr_number':107,'candidate_pr_workflow_run_id':33274571412,'candidate_pr_head_sha':EVIDENCE['candidate_pr_final_head_sha'],
   'candidate_post_merge_main_workflow_run_id':33274739859,'candidate_main_sha':EVIDENCE['candidate_merge_commit_sha'],
   'candidate_pages_isolation_workflow_run_id':33274739801,
   'final_bookkeeping_pr_number':109,'final_bookkeeping_pr_workflow_run_id':33279472975,
   'final_bookkeeping_main_workflow_run_id':33279600905,'final_bookkeeping_pages_workflow_run_id':33279600874,
   'final_bookkeeping_sha':EVIDENCE['final_bookkeeping_merge_sha'],'warnings':0,'logical_batch_mix':'PASS','browser_smoke':'PASS','aggregate_gate':'PASS'
 },
 'coverage_effect':{'explicit_subtopic_tags_before':304,'explicit_subtopic_tags_after':304,'mapped_subtopics':344}
})
save(p,m)

# 3) Semantic additions ledger -> 636 combined items.
p=SITE/'SEMANTIC_RELEASE_ADDITIONS.json'; s=load(p)
s['release']=VERSION; s['audit_date']=DATE
if 'BATCH-027' not in s['source_batches']: s['source_batches'].append('BATCH-027')
if not any(e.get('batch')=='BATCH-027' for e in s['quality_gate_evidence']):
    s['quality_gate_evidence'].append({'batch':'BATCH-027','evidence_type':'native-candidate-pr-plus-exact-main-plus-final-bookkeeping','candidate_pr_number':107,'candidate_pr_workflow_run_id':33274571412,'candidate_pr_head_sha':EVIDENCE['candidate_pr_final_head_sha'],'candidate_post_merge_main_workflow_run_id':33274739859,'candidate_main_sha':EVIDENCE['candidate_merge_commit_sha'],'candidate_pages_isolation_workflow_run_id':33274739801,'final_bookkeeping_pr_number':109,'final_bookkeeping_pr_workflow_run_id':33279472975,'final_bookkeeping_main_workflow_run_id':33279600905,'final_bookkeeping_pages_workflow_run_id':33279600874,'final_bookkeeping_sha':EVIDENCE['final_bookkeeping_merge_sha'],'warnings':0})
for i in range(424,440): s['items'][f'C-{i}']={'status':'VERIFIED'}
s['added_items']=len(s['items']); s['total_items']=s['base_items']+s['added_items']
summary=s.setdefault('summary',{})
summary['verified']=sum(1 for v in s['items'].values() if v.get('status')=='VERIFIED')
summary['verified_after_correction']=sum(1 for v in s['items'].values() if v.get('status')=='VERIFIED_AFTER_CORRECTION')
summary['verified_with_source_scope_note']=sum(1 for v in s['items'].values() if v.get('status')=='VERIFIED_WITH_SOURCE_SCOPE_NOTE')
summary['answer_key_reversals']=0; summary['material_factual_errors_remaining']=0
assert s['added_items']==336 and s['total_items']==636
save(p,s)

# 4) Runtime metadata counts/version.
p=SITE/'data-meta.js'; text=p.read_text(encoding='utf-8'); pre='window.CISSP_META='; marker=';window.CISSP_CHUNKS=[];'
assert text.startswith(pre) and marker in text
obj=json.loads(text[len(pre):text.index(marker)])
obj['meta'].update({'version':VERSION,'audited_on':DATE,'question_count':495,'bellringer_count':1,'question_bank_records':496,'semantic_items_reviewed':636})
p.write_text(pre+json.dumps(obj,separators=(',',':'),ensure_ascii=False)+marker+text[text.index(marker)+len(marker):],encoding='utf-8')

# 5) Question-bank status -> release candidate state.
p=QB/'STATUS.json'; q=load(p)
q['schema_version']=43; q['updated']=DATE; q['release']=VERSION
q['released']={'bank_records':496,'standard_mcq':495,'bellringer_cases':1,'manifest_released_records':440,'difficulty_distribution':{'F':41,'E':345,'S':109,'B':1},'base_classification_manifest':'RELEASED_QUESTION_CLASSIFICATION.json','released_batch_manifest':'RELEASED_BATCHES.json'}
q['latest_released_batch']={'batch_id':'027','status':'RELEASED_V1_25_0_PENDING_PUBLIC_VERIFICATION','records':16,'standard_mcq':16,'bellringer':0,'difficulty_distribution':{'F':0,'E':12,'S':4,'B':0},'primary_domain_distribution':{'1':5,'2':3,'3':2,'4':1,'5':1,'6':1,'7':0,'8':3},'answer_position_distribution':{'0':4,'1':4,'2':4,'3':4},'review':'BATCH_027_REVIEW.json','candidate_pr_number':107,'candidate_pr_final_head_sha':EVIDENCE['candidate_pr_final_head_sha'],'candidate_pr_audit_workflow_run_id':33274571412,'candidate_merge_commit_sha':EVIDENCE['candidate_merge_commit_sha'],'candidate_post_merge_main_audit_workflow_run_id':33274739859,'candidate_pages_isolation_workflow_run_id':33274739801,'candidate_final_bookkeeping_pr_number':109,'candidate_final_bookkeeping_pr_audit_workflow_run_id':33279472975,'candidate_final_bookkeeping_merge_sha':EVIDENCE['final_bookkeeping_merge_sha'],'candidate_final_bookkeeping_main_audit_workflow_run_id':33279600905,'candidate_final_bookkeeping_pages_workflow_run_id':33279600874,'quality_gate_warnings':0,'logical_batch_mix':'PASS','browser_smoke':'PASS','aggregate_gate':'PASS','explicit_subtopic_tags_after':304}
q['candidate_batches']={}; q['pending_candidate_summary']={'records':0,'standard_mcq':0,'bellringer_cases':0,'difficulty_distribution':{'F':0,'E':0,'S':0,'B':0}}
q['coverage']={'numbered_objectives_with_standard_mcq_exposure':'62/62','mapped_subtopics':344,'explicit_enriched_subtopic_exposure':304,'explicit_enriched_subtopic_unexposed':40,'boundary':'304/344 is the proposed v1.25 released explicit enriched-subtopic practice exposure. It is an authoring metadata metric, not a learner-mastery claim.'}
q.pop('remaining_to_target_from_released',None); q.pop('remaining_to_target_if_current_candidates_promote',None); q.pop('provisional_next_planned_batch',None)
q['remaining_to_target']={'bank_records':304,'F':79,'E':135,'S':51,'B':39}
q['next_planned_batch']={'batch_id':'028','basis_workflow_run_id':33274739859,'basis_release':'1.25.0-after-Batch-027-promotion','size':16,'difficulty_target':{'E':12,'S':4},'primary_domain_distribution':NEXT_DOMAINS,'objective_targets':NEXT_OBJECTIVES,'boundary':'Authoring recommendation only. Batch 028 must not begin until v1.25 has passed release-PR validation, exact post-merge main audit, live Pages fingerprint, and final evidence closure.'}
q['release_verification']={'target_release':VERSION,'status':'PENDING_RELEASE_PR_AND_POST_MERGE_VERIFICATION','last_confirmed_public_release':'1.24.0','last_confirmed_public_standard_questions':479,'last_confirmed_public_manifest_released_records':424,'last_confirmed_public_bellringers':1,'last_confirmed_public_released_only':True,'required_live_fingerprint':{'version':VERSION,'standard_questions':495,'manifest_released_records':440,'bellringers':1,'released_only':True}}
q['next_priority']=['Run the exact v1.25 release PR through the full CISSP gate before merge.','After merge, require exact-main CISSP audit and Pages live fingerprint v1.25.0 / 495 / 440 / 1 / released_only=true.','Close release evidence in a separate bookkeeping PR before beginning Batch 028.']
save(p,q)

# 6) Release status -> v1.25 candidate, preserving generic workflow/limitations.
p=SITE/'RELEASE_STATUS.json'; rel=load(p)
rel['release']=VERSION; rel['status']='READY_FOR_STUDY'; rel['prepared_on']=DATE; rel['last_semantic_audit']=DATE
rel['scope'].update({'explicit_enriched_subtopic_exposure':304,'explicit_enriched_subtopic_exposure_status':'PROPOSED_RELEASED_304','standard_scenario_questions':495,'bellringers':1,'question_bank_records':496,'released_difficulty_distribution':{'F':41,'E':345,'S':109,'B':1},'standard_questions_with_four_option_rationales':495,'semantic_items_reviewed':636})
rel['release_change']={'from':'1.24.0','promoted_batch':'027','promoted_standard_questions':16,'promoted_difficulty_distribution':{'F':0,'E':12,'S':4,'B':0},'primary_domain_distribution':{'1':5,'2':3,'3':2,'4':1,'5':1,'6':1,'7':0,'8':3},'semantic_review_status':'PASS','originality_duplicate_gate':'PASS','candidate_validation_pr':107,'candidate_pr_final_head_sha':EVIDENCE['candidate_pr_final_head_sha'],'candidate_pr_audit_workflow_run_id':33274571412,'candidate_merge_commit_sha':EVIDENCE['candidate_merge_commit_sha'],'candidate_post_merge_main_workflow_run_id':33274739859,'candidate_pages_isolation_workflow_run_id':33274739801,'candidate_final_bookkeeping_pr_number':109,'candidate_final_bookkeeping_pr_head_sha':EVIDENCE['final_bookkeeping_pr_head_sha'],'candidate_final_bookkeeping_pr_audit_workflow_run_id':33279472975,'candidate_final_bookkeeping_merge_sha':EVIDENCE['final_bookkeeping_merge_sha'],'candidate_final_bookkeeping_main_audit_workflow_run_id':33279600905,'candidate_final_bookkeeping_pages_workflow_run_id':33279600874,'candidate_quality_gate_warnings':0,'logical_batch_mix':'PASS','browser_smoke':'PASS','aggregate_gate':'PASS','explicit_enriched_subtopic_exposure_before':304,'explicit_enriched_subtopic_exposure_after':304,'objective_exposure':'62/62 numbered objectives have at least one standard MCQ exposure','release_pr_state':'PENDING_NATIVE_RELEASE_PR_AUDIT','post_promotion_main_audit':'PENDING','public_pages_runtime':'PENDING'}
rel['pending_candidate']=None
rel['validation']['v1_25_release_evidence']='subjects/cissp/2024-outline/study-site/question-bank/BATCH_027_REVIEW.json'
exp=rel['question_bank_expansion_target']; exp.update({'current_released_records':496,'current_released_difficulty':{'F':41,'E':345,'S':109,'B':1},'remaining_to_target':{'records':304,'F':79,'E':135,'S':51,'B':39},'current_unreleased_candidates':0,'next_bias':'After v1.25 release-state, live fingerprint, and final evidence closure pass, use the released-only planner for Batch 028 with materially new scenario families and thin concepts.','next_planner_basis_workflow_run_id':33274739859,'next_planner_objectives':NEXT_OBJECTIVES,'next_planner_primary_domain_distribution':NEXT_DOMAINS,'next_planner_difficulty_distribution':{'E':12,'S':4}})
for k in ['remaining_from_released','candidate_inclusive_records','candidate_inclusive_difficulty','remaining_if_current_candidates_promote','provisional_next_planner_basis_workflow_run_id','provisional_next_planner_scope','provisional_next_planner_objectives','provisional_next_planner_primary_domain_distribution','provisional_next_planner_difficulty_distribution']:
    exp.pop(k,None)
dep=rel['deployment']; dep.update({'repository_release_candidate':VERSION,'last_confirmed_public_pages_release':'1.24.0','public_v1_25_verification_pending':True,'public_runtime_verified_for_v1_25':False,'candidate_final_bookkeeping_isolation_evidence':{'pages_workflow_run_id':33279600874,'bookkeeping_main_sha':EVIDENCE['final_bookkeeping_merge_sha'],'version':'1.24.0','standard_questions':479,'manifest_released_records':424,'bellringers':1,'released_only':True},'required_v1_25_live_fingerprint':{'version':VERSION,'standard_questions':495,'manifest_released_records':440,'bellringers':1,'released_only':True},'activation_status':'v1.25.0 is the release candidate. Public v1.24.0 remains authoritative until the exact v1.25 release PR passes the full CISSP gate, the validated release head is merged, and exact-main plus live Pages verification prove v1.25.0 / 495 standard / 440 manifest released / 1 Bellringer / released_only=true.'})
# Keep prior v1.24 health evidence but make the latest verified runtime explicit.
dep['last_verified_release_runtime_evidence']={'pages_workflow_run_id':33279191598,'release_content_sha':'10560511eb56cf7197e072eefdbef76dcbee7a10','version':'1.24.0','standard_questions':479,'manifest_released_records':424,'bellringers':1,'released_only':True}
rel['precision_boundary']='The proposed CISSP Atlas v1.25 corpus contains 495 standard scenario questions, 1 Bellringer, 496 total bank records, and 636 semantically reviewed learner-facing item IDs with zero known keyed-answer reversals and no known remaining material factual error within the documented review boundary. Batch 027 passed candidate PR audit 33274571412, candidate exact-main audit 33274739859, candidate Pages isolation 33274739801, final-bookkeeping PR audit 33279472975, final-bookkeeping exact-main audit 33279600905, and final-bookkeeping Pages isolation 33279600874 with zero originality warnings and all CISSP controls PASS. Explicit enriched-subtopic exposure remains 304/344 in the proposed release. Public v1.24.0 remains authoritative until v1.25 release-state and live fingerprint verification pass. This resource remains unofficial and does not guarantee passing the live adaptive CISSP exam.'
save(p,rel)

# 7) Project router release scope.
p=ROOT/'PROJECT_TRACKS.json'; tracks=load(p); cs=tracks['tracks']['CISSP-ATLAS']['current_scope']
cs.update({'version':VERSION,'last_semantic_audit':DATE,'explicit_enriched_subtopic_exposure':304,'released_standard_questions':495,'released_bellringers':1,'released_bank_records':496,'released_question_difficulty':{'F':41,'E':345,'S':109,'B':1},'standard_questions_with_four_option_rationales':495,'semantic_items_reviewed':636,'semantic_answer_key_reversals':0,'pending_candidate_records':0,'candidate_inclusive_bank_records':496,'candidate_inclusive_question_difficulty':{'F':41,'E':345,'S':109,'B':1},'next_action':'Validate and merge the exact v1.25 release candidate, prove exact-main and live Pages fingerprint, then close final release evidence before Batch 028.','next_batch':'028','next_batch_scope':'provisional-v1.25-released','next_batch_basis_workflow_run_id':33274739859,'next_batch_target_difficulty':{'E':12,'S':4},'public_release_verified':False})
save(p,tracks)

# 8) User-facing docs rewritten with current, non-overstated release-candidate state.
readme=f'''# CISSP Atlas — Current Outline Study Workflow\n\nUnofficial, original study site mapped to the current public ISC2 CISSP exam outline (effective 2024-04-15).\n\n## Current release candidate — v1.25.0\n\n- 8 CISSP domains; official weights total **100%**.\n- **62** numbered public objectives and **344** paraphrased subtopic checks.\n- **304/344** checks with explicit enriched-subtopic practice exposure.\n- **33** AI-security coverage areas and **140** layered retrieval cards.\n- **495 released standard scenario questions + 1 Bellringer = 496 released bank records** in the proposed v1.25 release state.\n- Author-difficulty mix: **F41 / E345 / S109 / B1**.\n- **495/495** standard questions have four-option teaching rationales.\n- **636 learner-facing item IDs** in the combined semantic-audit ledger.\n- **20** primary/reference sources.\n\n`question-bank/RELEASED_BATCHES.json` is authoritative for promoted batches and `RELEASE_STATUS.json` for release/deployment state. Public v1.24.0 remains authoritative until the exact v1.25 release head is merged and exact-main plus live Pages verification pass.\n\n## Semantic-review boundary\n\nThe combined ledgers cover **636 learner-facing item IDs**: 300 base items plus 336 release-addition items. The retained historical semantic statuses include one verified-after-correction item and two source-scope-note items; Batch 027 contributes 16 `VERIFIED` items. The release records **0 keyed-answer reversals** and **0 known remaining material factual errors** within the documented review boundary. This is an auditable quality claim, not an infallibility or exam-pass guarantee.\n\n## Study workflow\n\nUse **diagnose → retrieve → apply → repair → re-test later**. Run the 16-question diagnostic once for routing, retrieve before revealing, use Exam + Stretch for standard practice, commit confidence before answering, review all four rationales, repair high-confidence misses first, and use Bellringers separately as non-exam-representative integrative drills.\n\nKeyboard review flow: **Space toggles reveal/hide; ←/→ move cards while hidden and layers while revealed; 1–4 grades the revealed card.**\n\n## Question-bank expansion\n\nThe long-term target remains **800 records** with an authoring mix of 15% Foundation+, 60% Exam-calibrated, 20% Stretch, and 5% Bellringer. After Batch 027 promotion, remaining deficits are **F79 / E135 / S51 / B39**, or **304 records**. All 62 objectives have at least one standard-MCQ exposure. Explicit enriched-subtopic exposure remains **304/344**; this is authoring coverage, not learner mastery.\n\nBatch 028 remains blocked until v1.25 release PR validation, exact post-merge main audit, live Pages fingerprint, and final evidence closure pass. Its provisional E12/S4 slate is: `{', '.join(NEXT_OBJECTIVES)}`.\n\n## Continuous audit\n\n`.github/workflows/cissp-study-site-audit.yml` enforces knowledge/schema consistency, semantic coverage, originality/duplicate controls, logical batch composition, planning, JavaScript syntax, rationales, static assets, interactive browser flows, and an aggregate gate. `.github/workflows/cissp-pages.yml` independently audits and assembles a released-only artifact and verifies the public runtime fingerprint.\n\n## Accuracy boundary\n\nThe strongest warranted v1.25 release-candidate claim is: **no known material factual errors or incorrect keyed answers are recorded as remaining; 636 learner-facing item IDs have explicit semantic status, and the release records zero known keyed-answer reversals.** Standards and public scope can change, reviews can miss nuance, and ISC2's adaptive live item bank is not public.\n\n## Run locally\n\n```bash\npython -m http.server 8000\npython audit.py\npython question-bank/quality_gate.py\npython question-bank/coverage_report.py --human\npython question-bank/batch_planner.py --human\n```\n\n## Primary scope references\n\n- ISC2 CISSP Certification Exam Outline: https://www.isc2.org/certifications/cissp/cissp-certification-exam-outline\n- ISC2 CISSP Exam Refresh FAQ: https://www.isc2.org/certifications/cissp/cissp-exam-refresh-faq\n- ISC2 Code of Ethics: https://www.isc2.org/ethics\n\nSupporting standards are registered in `data-meta.js` and surfaced in the Sources view.\n'''
(SITE/'README.md').write_text(readme,encoding='utf-8')

tomorrow=f'''# CISSP Atlas — Start Here\n\nUse this sequence the first time you open the current release.\n\n1. Run the 16-question diagnostic once if you do not already have a baseline. Treat it as routing, not an exam-readiness score.\n2. Open the weakest domain in Learn and retrieve before revealing.\n3. Use the misconception layer on misses or hesitation.\n4. Run 10–20 standard scenarios with **Exam + Stretch** selected.\n5. Commit confidence before choosing an answer; repair high-confidence misses first.\n6. Read all four option rationales.\n7. Use a Bellringer only after a normal study block; it is non-exam-representative.\n8. Re-test later rather than repeating immediately to recognition.\n\nKeyboard: **Space toggles reveal/hide; ←/→ move cards when hidden and layers when revealed; 1–4 grades.**\n\n## Current v1.25.0 scope\n\n- 8 domains; official weights total 100%.\n- 62 numbered public objectives.\n- 344 mapped subtopic checks; 304/344 with explicit enriched-subtopic practice exposure.\n- 33 AI-security coverage areas.\n- 140 layered retrieval cards.\n- **495 released standard scenario questions + 1 Bellringer = 496 question-bank records** in the proposed release state.\n- Difficulty mix: **F41 / E345 / S109 / B1**.\n- Four-option teaching rationales on **495/495** standard questions.\n- **636 semantically reviewed learner-facing item IDs**, with zero known keyed-answer reversals and no known remaining material factual error in the documented audit boundary.\n- 20 primary/reference sources.\n\nThere are no unreleased candidate records in the proposed v1.25 release state. Batch 028 must not begin until v1.25 passes exact release-PR validation, post-merge main audit, live Pages fingerprint verification, and final evidence closure.\n\nSee `RELEASE_STATUS.json` for machine-readable evidence and `PRECISION_AUDIT.md` for the accuracy boundary. CISSP Atlas is unofficial and does not guarantee a pass on the live adaptive exam.\n'''
(SITE/'TOMORROW_START.md').write_text(tomorrow,encoding='utf-8')

precision=f'''# CISSP Atlas Precision Audit — v1.25 Release Candidate\n\n## Result\n\n**Published-scope mapping: PASS. Batch 027 semantic/originality and candidate-bookkeeping validation: PASS within the documented audit boundary. v1.25 release PR and post-merge public verification are still required before v1.25 becomes authoritative.**\n\n## v1.25.0 proposed released scope\n\n- 8/8 domains; official weights total 100%.\n- 62/62 numbered public objectives.\n- 344 paraphrased public-outline subtopic checks; **304/344** explicitly exposed by enriched-subtopic practice metadata.\n- 33 AI-security coverage areas and 140 layered retrieval cards.\n- **495 released standard scenario questions**.\n- **1 released Bellringer**, explicitly non-exam-representative.\n- **496 total released question-bank records**.\n- 495/495 standard questions have four-option teaching rationales.\n- 20 primary/reference sources.\n- **636 learner-facing item IDs** in the combined semantic ledgers.\n- Released author-difficulty distribution: **F41 / E345 / S109 / B1**.\n\n## Batch 027 validation closure\n\nBatch 027 contributes 16 original standard questions, E12/S4, balanced answer positions 4/4/4/4, and primary-domain distribution D1=5, D2=3, D3=2, D4=1, D5=1, D6=1, D8=3. The review records 0 answer-key conflicts, 0 remaining source/objective mapping conflicts, 0 known material factual errors remaining, and 0 external question seeds. C-437's earlier FIPS 197 provenance mapping was removed before the authoritative candidate head; its answer, scenario, and rationale were unchanged.\n\nEvidence chain:\n- Candidate PR #107 exact head `{EVIDENCE['candidate_pr_final_head_sha']}`; audit **33274571412: PASS**.\n- Candidate merge `{EVIDENCE['candidate_merge_commit_sha']}`; exact-main audit **33274739859: PASS**; Pages isolation **33274739801: PASS**.\n- Candidate-bookkeeping PR #109 exact head `{EVIDENCE['final_bookkeeping_pr_head_sha']}`; audit **33279472975: PASS**.\n- Candidate-bookkeeping merge `{EVIDENCE['final_bookkeeping_merge_sha']}`; exact-main audit **33279600905: PASS**; Pages isolation **33279600874: PASS**.\n\nAll required candidate and bookkeeping controls passed with zero originality warnings. Public v1.24.0 remained isolated at 479 standard / 424 manifest released / 1 Bellringer / released_only=true through the bookkeeping chain.\n\n## Semantic audit\n\nThe base semantic ledger contains 300 items; the release-additions ledger contains 336, for **636 learner-facing item IDs**. Batch 027's 16 additions are `VERIFIED`. The release records 0 keyed-answer reversals and 0 known material factual errors remaining after review within the documented boundary. Historical correction/source-scope statuses from earlier releases remain preserved.\n\n## Release controls still required\n\nThe exact v1.25 release head must pass deterministic knowledge, originality/duplicate, logical mix, planning, JavaScript syntax, rationale, static, browser-smoke, and aggregate gates. After merge, the exact main SHA must pass again and Pages must prove **v1.25.0 / 495 standard / 440 manifest released records / 1 Bellringer / released_only=true**. Final release evidence is then closed before Batch 028 begins.\n\n## Next expansion state\n\nThe 800-record target would leave **F79 / E135 / S51 / B39**, or **304 records total**, after v1.25 promotion. Provisional Batch 028 slate: `{', '.join(NEXT_OBJECTIVES)}`.\n\n## Accuracy boundary\n\nThe strongest warranted claim for the v1.25 documented audit boundary is: **No known material factual errors or incorrect keyed answers are recorded as remaining; 636 learner-facing item IDs have explicit semantic audit status, and the release records zero known keyed-answer reversals.** This is not an absolute infallibility guarantee and does not guarantee passing the live adaptive CISSP exam.\n'''
(SITE/'PRECISION_AUDIT.md').write_text(precision,encoding='utf-8')

# 9) Release badge/base footer, runtime polish footer, and browser smoke expectation.
p=SITE/'index.html'; t=p.read_text(encoding='utf-8'); t=replace_once(t,'RELEASE v1.24','RELEASE v1.25','index release badge'); t=t.replace('v1.24 · local-first progress','v1.25 · local-first progress'); p.write_text(t,encoding='utf-8')
p=SITE/'product-polish.js'; t=p.read_text(encoding='utf-8'); t=replace_once(t,"v1.24 · local progress","v1.25 · local progress",'runtime footer'); p.write_text(t,encoding='utf-8')
p=SITE/'browser-smoke.html'; t=p.read_text(encoding='utf-8'); t=replace_once(t,"includes('v1.24')","includes('v1.25')",'browser footer assertion'); p.write_text(t,encoding='utf-8')

# Final internal consistency assertions before CI.
assert len(m['released_batches'][-1]['files'])==4
assert load(QB/'STATUS.json')['released']['manifest_released_records']==440
assert load(SITE/'RELEASE_STATUS.json')['scope']['semantic_items_reviewed']==636
print('PASS build_cissp_v125_release release=1.25.0 standard=495 bank=496 manifest=440 semantic=636')
