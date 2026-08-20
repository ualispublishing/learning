import hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/'reading/urdu/a1/passages.jsonl'; STAGE=ROOT/'reading/urdu/a1/staging/unit08'; LEX=ROOT/'reading/lexicons/urdu.jsonl'; OUT=ROOT/'reading/audit/urdu_a1_unit08_staging_result_2026-08-20.json'
EXPECTED='b4fcf0bbc07d62cd3e743b8d0a6d49df2d6b0df3d03aa892384d0501a7ef1d4a'
FILES=[f'ur-a1-u08-p{i:02d}.json' for i in range(1,7)]
def count_words(text): return len([x for x in str(text).split() if x])
def occurrences(text, form): return len(re.findall(r'(?<!\w)'+re.escape(form)+r'(?!\w)', text))
def main():
 bound=hashlib.sha256(CANON.read_bytes()).hexdigest()
 if bound!=EXPECTED: raise SystemExit(f'canonical hash drift {bound}')
 canon=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(canon)!=42 or [p.get('sequence') for p in canon]!=list(range(1,43)): raise SystemExit('expected canonical 1-42 frontier')
 used_ids={t.get('id') for p in canon for t in p.get('new_lexical_targets',[])}; used_forms={t.get('form') for p in canon for t in p.get('new_lexical_targets',[])}
 lex={r['id']:r for r in [json.loads(x) for x in LEX.read_text(encoding='utf-8').splitlines() if x.strip()]}
 staged=[]; added_ids=set(); added_forms=set(); problems=[]; evidence=[]
 for seq,name in enumerate(FILES,start=43):
  path=STAGE/name
  if not path.exists(): problems.append({'file':name,'kind':'missing'}); continue
  p=json.loads(path.read_text(encoding='utf-8')); staged.append(p)
  if p.get('id')!=f'ur-a1-u08-p{seq-42:02d}' or p.get('sequence')!=seq or p.get('unit')!=8: problems.append({'file':name,'kind':'identity_sequence_unit'})
  if p.get('language')!='ur' or p.get('cefr')!='A1': problems.append({'file':name,'kind':'language_cefr'})
  actual_wc=count_words(p.get('text',''))
  if p.get('word_count')!=actual_wc: problems.append({'file':name,'kind':'word_count_metadata','metadata':p.get('word_count'),'actual':actual_wc})
  if not 90<=actual_wc<=140: problems.append({'file':name,'kind':'word_band','actual':actual_wc})
  actual_sent=p.get('text','').count('۔')
  if p.get('sentence_count')!=actual_sent: problems.append({'file':name,'kind':'sentence_count_metadata','metadata':p.get('sentence_count'),'actual':actual_sent})
  qs=p.get('questions',[]); ans=p.get('answer_key',[])
  if len(qs)!=10 or len(ans)!=10: problems.append({'file':name,'kind':'10q10a','q':len(qs),'a':len(ans)})
  if {q.get('id') for q in qs}!={a.get('question_id') for a in ans}: problems.append({'file':name,'kind':'qa_linkage'})
  declared={x.get('id') for x in p.get('new_lexical_targets',[])+p.get('review_lexical_targets',[])}
  for q in qs:
   unknown=set(q.get('target_ids',[]))-declared
   if unknown: problems.append({'file':name,'kind':'undeclared_question_target','question':q.get('id'),'ids':sorted(unknown)})
  text=p.get('text','')
  new_info=[]
  for t in p.get('new_lexical_targets',[]):
   tid=t.get('id'); form=t.get('form'); n=occurrences(text,form)
   if tid in used_ids or tid in added_ids: problems.append({'file':name,'kind':'new_target_id_collision','id':tid})
   if form in used_forms or form in added_forms: problems.append({'file':name,'kind':'new_target_form_collision','form':form})
   lr=lex.get(tid)
   if not lr: problems.append({'file':name,'kind':'missing_lexicon_id','id':tid})
   else:
    if lr.get('form')!=form or lr.get('rank')!=t.get('source_rank') or lr.get('source_file')!=t.get('source_lexicon'): problems.append({'file':name,'kind':'source_identity_mismatch','id':tid,'lexicon':{'form':lr.get('form'),'rank':lr.get('rank'),'source_file':lr.get('source_file')},'target':{'form':form,'rank':t.get('source_rank'),'source_file':t.get('source_lexicon')}})
   if n==0: problems.append({'file':name,'kind':'new_target_not_visible','id':tid,'form':form})
   if t.get('exposures_in_text')!=n: problems.append({'file':name,'kind':'exposure_count_mismatch','id':tid,'metadata':t.get('exposures_in_text'),'actual':n})
   new_info.append({'id':tid,'form':form,'occurrences':n}); added_ids.add(tid); added_forms.add(form)
  for r in p.get('review_lexical_targets',[]):
   if r.get('representation')=='running_text' and occurrences(text,r.get('form',''))==0: problems.append({'file':name,'kind':'running_text_review_not_visible','id':r.get('id'),'form':r.get('form')})
  if seq==48 and p.get('new_lexical_targets'): problems.append({'file':name,'kind':'p06_not_zero_new'})
  learner=' '.join([p.get('title',''),p.get('text','')]+[q.get('prompt','')+' '+' '.join(q.get('options',[]) or []) for q in qs]+[a.get('answer','') for a in ans])
  if re.search(r'[A-Za-z]',learner): problems.append({'file':name,'kind':'learner_facing_roman_script'})
  evidence.append({'file':name,'id':p.get('id'),'sequence':p.get('sequence'),'word_count_actual':actual_wc,'sentence_count_actual':actual_sent,'new_targets':new_info})
 # check future target leakage before formal intro
 first_intro={t.get('form'):p.get('sequence') for p in staged for t in p.get('new_lexical_targets',[])}
 for p in staged:
  for form,intro_seq in first_intro.items():
   if p.get('sequence')<intro_seq and occurrences(p.get('text',''),form)>0: problems.append({'file':p.get('id'),'kind':'premature_future_target_form','form':form,'formal_intro_sequence':intro_seq})
 out={'schema_version':1,'date':'2026-08-20','language':'ur','level':'A1','unit':8,'bound_canonical_sha256':bound,'status':'STAGED_STRUCTURALLY_CHECKED' if not problems else 'STAGING_VALIDATION_FAIL','canonical_promotion':'STACKED_FRONTIER_READY_FOR_REVIEW_NOT_PROMOTED' if not problems else 'BLOCKED','staging_path':'reading/urdu/a1/staging/unit08','sequences':[43,44,45,46,47,48],'passages':len(staged),'questions':sum(len(p.get('questions',[])) for p in staged),'answers':sum(len(p.get('answer_key',[])) for p in staged),'word_counts':[count_words(p.get('text','')) for p in staged],'new_targets':[t.get('form') for p in staged for t in p.get('new_lexical_targets',[])],'source_lexicon':'urdu_top1000.csv','source_lexicon_mutated':False,'checks':{'six_passages':len(staged)==6,'sequences_contiguous':len(staged)==6 and [p.get('sequence') for p in staged]==list(range(43,49)),'a1_word_band_90_140':not any(x.get('kind')=='word_band' for x in problems),'word_count_metadata_checked':not any(x.get('kind')=='word_count_metadata' for x in problems),'sentence_count_metadata_checked':not any(x.get('kind')=='sentence_count_metadata' for x in problems),'ten_questions_each':all(len(p.get('questions',[]))==10 for p in staged),'ten_answers_each':all(len(p.get('answer_key',[]))==10 for p in staged),'question_answer_linkage':not any(x.get('kind')=='qa_linkage' for x in problems),'question_targets_locally_declared':not any(x.get('kind')=='undeclared_question_target' for x in problems),'new_target_forms_visible':not any(x.get('kind')=='new_target_not_visible' for x in problems),'new_target_exposure_counts_checked':not any(x.get('kind')=='exposure_count_mismatch' for x in problems),'declared_running_text_reviews_visible':not any(x.get('kind')=='running_text_review_not_visible' for x in problems),'source_identity_checked':not any(x.get('kind') in {'missing_lexicon_id','source_identity_mismatch'} for x in problems),'target_collisions_zero':not any(x.get('kind') in {'new_target_id_collision','new_target_form_collision'} for x in problems),'within_unit_first_introduction_order_checked':not any(x.get('kind')=='premature_future_target_form' for x in problems),'p06_zero_new_targets':not any(x.get('kind')=='p06_not_zero_new' for x in problems),'learner_facing_roman_script_zero':not any(x.get('kind')=='learner_facing_roman_script' for x in problems)},'problems':problems,'record_evidence':evidence,'formal_final_audit':'deferred under generation-first policy','promotion_precondition':'The stacked Unit07 frontier is present on this branch; main still requires the earlier Urdu promotion stack before Unit08 can ever be canonicalized.','next_generation_frontier_after_promotion':'Unit 09 sequences 49-54','release_effect':'Staging/generation progress only; Urdu remains non-release-ready.'}
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps({'status':out['status'],'problems':len(problems),'word_counts':out['word_counts']},ensure_ascii=False))
 if problems: raise SystemExit('Unit08 staging validation failed')
if __name__=='__main__': main()
