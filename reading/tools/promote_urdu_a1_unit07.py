import hashlib, json, re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/'reading/urdu/a1/passages.jsonl'; STAGING=ROOT/'reading/urdu/a1/staging/unit07'; OUT=ROOT/'reading/audit/urdu_a1_unit07_promotion_2026-08-20.json'
EXPECTED_CANON_BLOB='2bba9c1f8b26274f1801d2ea34d9260dfd5e34d3'
STAGED={'ur-a1-u07-p01.json':'0bc16f15656f19986a6b9ac6ac1f206c87304bbd','ur-a1-u07-p02.json':'6a3af534bb933c0c771b4c5567de58cc328c6a4a','ur-a1-u07-p03.json':'f671fd1a3bf6f531db279e4dd5de425698d95cc5','ur-a1-u07-p04.json':'5b6adc2b33c9422beb523bd31e797d137f099170','ur-a1-u07-p05.json':'cebfe1a803e6875c3f2264e692621a2cb77b4cab','ur-a1-u07-p06.json':'c104059e8c2876125321ee4ddaaf6e51bcb50998'}
def blob(p): return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if blob(CANON)!=EXPECTED_CANON_BLOB: raise SystemExit('canonical seq36 frontier drift')
 before=sha(CANON); rows=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=36 or [r.get('sequence') for r in rows]!=list(range(1,37)): raise SystemExit('canonical frontier is not 1-36')
 oldids={t.get('id') for r in rows for t in r.get('new_lexical_targets',[])}; added=set(); staged=[]; evidence={}
 for seq,name in enumerate(STAGED,start=37):
  pth=STAGING/name; actual=blob(pth)
  if actual!=STAGED[name]: raise SystemExit(f'staging drift {name}')
  evidence[name]=actual; p=json.loads(pth.read_text(encoding='utf-8'))
  if p.get('sequence')!=seq or p.get('unit')!=7 or p.get('id')!=f'ur-a1-u07-p{seq-36:02d}': raise SystemExit(f'identity mismatch {name}')
  if p.get('language')!='ur' or p.get('cefr')!='A1' or not 90<=p.get('word_count',0)<=140: raise SystemExit(f'level/word-band failure {name}')
  qs=p.get('questions',[]); ans=p.get('answer_key',[])
  if len(qs)!=10 or len(ans)!=10 or {q.get('id') for q in qs}!={a.get('question_id') for a in ans}: raise SystemExit(f'Q/A failure {name}')
  declared={x.get('id') for x in p.get('new_lexical_targets',[])+p.get('review_lexical_targets',[])}
  if any(set(q.get('target_ids',[]))-declared for q in qs): raise SystemExit(f'undeclared q target {name}')
  text=p.get('text','')
  if any(not t.get('form') or t.get('form') not in text for t in p.get('new_lexical_targets',[])): raise SystemExit(f'new target invisible {name}')
  if any(r.get('representation')=='running_text' and r.get('form') not in text for r in p.get('review_lexical_targets',[])): raise SystemExit(f'review invisible {name}')
  if seq==42 and p.get('new_lexical_targets'): raise SystemExit('P06 must be zero-new')
  learner=' '.join([p.get('title',''),text]+[q.get('prompt','') for q in qs]+[a.get('answer','') for a in ans])
  if re.search(r'[A-Za-z]',learner): raise SystemExit(f'Roman leakage {name}')
  nids={t.get('id') for t in p.get('new_lexical_targets',[])}
  if nids&(oldids|added): raise SystemExit(f'target collision {name}')
  added|=nids; staged.append(p)
 combined=rows+staged
 if len(combined)!=42 or [r.get('sequence') for r in combined]!=list(range(1,43)): raise SystemExit('post-promotion continuity failure')
 CANON.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in combined)+'\n',encoding='utf-8'); after=sha(CANON)
 out={'schema_version':1,'date':'2026-08-20','language':'ur','level':'A1','unit':7,'status':'GUARDED_PROMOTION_APPLIED_NEEDS_REVIEW','before_git_blob':EXPECTED_CANON_BLOB,'before_sha256':before,'after_sha256':after,'staged_git_blobs':evidence,'canonical_passages_after':42,'canonical_questions_after':420,'canonical_answers_after':420,'promoted_sequences':[37,38,39,40,41,42],'new_target_ids_added':sorted(added),'source_lexicon_mutated':False,'checks':{'frontier_blob_exact':True,'staging_blobs_exact':True,'sequences_contiguous':True,'a1_word_band_90_140':True,'ten_questions_and_answers':True,'answer_linkage':True,'question_targets_locally_declared':True,'new_targets_visible':True,'running_text_reviews_visible':True,'new_target_id_collisions':0,'p06_zero_new_targets':True,'learner_facing_roman_script_zero':True},'formal_final_audit':'deferred under generation-first policy','next_generation_frontier':'Urdu A1 Unit 08 sequences 43-48; generate/stage next against this hash.','release_effect':'Generation progress only; Urdu remains non-release-ready.'}
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps({'status':out['status'],'after':after},ensure_ascii=False))
if __name__=='__main__': main()
