import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/'reading/urdu/a1/passages.jsonl'
STAGE=ROOT/'reading/urdu/a1/staging/unit09'
AUDIT=ROOT/'reading/audit/urdu_a1_unit09_promotion_2026-08-21.json'
EXPECTED='89fbbbaf5f7b376a274accb1dc0cbe6cae82eba496f24d4bfff57cf3e2977e63'
FILES=[f'ur-a1-u09-p0{i}.json' for i in range(1,7)]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def blob(p):
 b=p.read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def surfaces(p):
 yield p.get('text','')
 for q in p.get('questions',[]): yield q.get('prompt','')
 for a in p.get('answer_key',[]): yield a.get('answer','')
def main():
 before=sha(CANON)
 if before!=EXPECTED: raise SystemExit(f'canonical hash drift {before}')
 canon=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(canon)!=48 or [p.get('sequence') for p in canon]!=list(range(1,49)): raise SystemExit('canonical frontier mismatch')
 staged=[]; blobs={}
 for fn in FILES:
  p=STAGE/fn
  if not p.exists(): raise SystemExit(f'missing {fn}')
  blobs[fn]=blob(p); staged.append(json.loads(p.read_text(encoding='utf-8')))
 if [p.get('sequence') for p in staged]!=list(range(49,55)): raise SystemExit('staged sequence mismatch')
 if [p.get('id') for p in staged]!=[f'ur-a1-u09-p0{i}' for i in range(1,7)]: raise SystemExit('staged id mismatch')
 existing={t.get('id') for p in canon for t in p.get('new_lexical_targets',[]) if t.get('id')}
 new=[]; problems=[]
 for idx,p in enumerate(staged,1):
  qs=p.get('questions',[]); ans=p.get('answer_key',[])
  if len(qs)!=10 or len(ans)!=10: problems.append([p['id'],'cardinality'])
  if {q.get('id') for q in qs}!={a.get('question_id') for a in ans}: problems.append([p['id'],'linkage'])
  local={t.get('id') for t in p.get('new_lexical_targets',[])}|{t.get('id') for t in p.get('review_lexical_targets',[])}
  for q in qs:
   for tid in q.get('target_ids',[]):
    if tid not in local: problems.append([p['id'],q.get('id'),'target_not_local',tid])
  for t in p.get('new_lexical_targets',[]):
   tid=t.get('id'); form=t.get('form','')
   if tid in existing: problems.append([p['id'],'collision',tid])
   if tid: new.append(tid)
   if form and form not in p.get('text',''): problems.append([p['id'],'new_not_visible',form])
  for t in p.get('review_lexical_targets',[]):
   if t.get('representation')=='running_text' and t.get('form') and t['form'] not in p.get('text',''): problems.append([p['id'],'review_not_visible',t['form']])
  if idx==6 and p.get('new_lexical_targets'): problems.append([p['id'],'checkpoint_has_new'])
  wc=len((p.get('text') or '').split())
  if wc!=p.get('word_count') or not 90<=wc<=140: problems.append([p['id'],'word_count',wc,p.get('word_count')])
  for s in surfaces(p):
   if re.search(r'[A-Za-z]',s or ''): problems.append([p['id'],'roman_script'])
 if len(new)!=10 or len(set(new))!=10: problems.append(['unit09','new_target_count',len(new),len(set(new))])
 if problems: raise SystemExit('validation failed '+json.dumps(problems,ensure_ascii=False))
 CANON.write_text('\n'.join(json.dumps(p,ensure_ascii=False,sort_keys=True) for p in canon+staged)+'\n',encoding='utf-8')
 after=sha(CANON)
 AUDIT.write_text(json.dumps({'schema_version':1,'date':'2026-08-21','language':'ur','level':'A1','unit':9,'status':'GUARDED_PROMOTION_APPLIED_NEEDS_REVIEW','before_sha256':before,'after_sha256':after,'staged_git_blobs':blobs,'canonical_passages_after':54,'canonical_questions_after':540,'canonical_answers_after':540,'promoted_sequences':list(range(49,55)),'new_target_ids_added':new,'source_lexicon_mutated':False,'checks':{'frontier_sha256_exact':True,'staging_files_present':True,'sequences_contiguous':True,'a1_word_band_90_140':True,'ten_questions_and_answers':True,'answer_linkage':True,'question_targets_locally_declared':True,'new_targets_visible':True,'running_text_reviews_visible':True,'new_target_id_collisions':0,'p06_zero_new_targets':True,'learner_facing_roman_script_zero':True},'formal_final_audit':'deferred under generation-first policy','next_generation_frontier':'Urdu A1 Unit 10 sequences 55-60; staged already on the dependent Unit 10 branch.','release_effect':'Generation progress only; Urdu remains non-release-ready.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'status':'PASS_GUARDED_PROMOTION_UNIT09','after':after,'records':54},ensure_ascii=False))
if __name__=='__main__': main()
