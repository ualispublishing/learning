import hashlib,json,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/french/a1/passages.jsonl'; OUT=ROOT/'reading/audit/french_a1_review_integrity_round2_postrepair_2026-08-20.json'
EXPECTED='42c6455db972afd1fe6158a2f58c6e9ed2725204dd12aa80a4f7961ef1b130d5'
REMOVED={('fr-a1-u03-p03','fr-rank-0032'),('fr-a1-u03-p04','fr-rank-0044'),('fr-a1-u03-p05','fr-rank-0037'),('fr-a1-u04-p02','fr-rank-0024'),('fr-a1-u04-p02','fr-rank-0025'),('fr-a1-u04-p03','fr-rank-0027'),('fr-a1-u04-p04','fr-rank-0030'),('fr-a1-u04-p04','fr-rank-0041'),('fr-a1-u04-p05','fr-rank-0042')}
VALID={('fr-a1-u04-p01','fr-rank-0019'),('fr-a1-u01-p05','fr-rank-0039'),('fr-a1-u01-p06','fr-rank-0047'),('fr-a1-u02-p03','fr-rank-0060'),('fr-a1-u02-p04','fr-rank-0060'),('fr-a1-u03-p01','fr-rank-0014'),('fr-a1-u03-p02','fr-rank-0022'),('fr-a1-u03-p03','fr-rank-0036'),('fr-a1-u03-p05','fr-rank-0043')}
STAGE={'R1':1,'R2':2,'R3':3,'R4':4,'R5':5,'long_term':6}
def main():
 bound=hashlib.sha256(PATH.read_bytes()).hexdigest()
 if bound!=EXPECTED: raise SystemExit(f'hash drift {bound}')
 rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
 problems=[]; present=set(); histories={}
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)): problems.append({'kind':'structure'})
 for p in rows:
  if len(p.get('questions',[]))!=10 or len(p.get('answer_key',[]))!=10: problems.append({'passage_id':p['id'],'kind':'10q10a'})
  if {q.get('id') for q in p.get('questions',[])}!={a.get('question_id') for a in p.get('answer_key',[])}: problems.append({'passage_id':p['id'],'kind':'linkage'})
  for r in p.get('review_lexical_targets',[]):
   key=(p['id'],r.get('id')); present.add(key); histories.setdefault(r.get('id'),[]).append({'sequence':p['sequence'],'stage':r.get('review_stage'),'passage_id':p['id']})
 for key in REMOVED:
  if key in present: problems.append({'kind':'round2_removed_review_survived','passage_id':key[0],'target_id':key[1]})
 missing_valid=[{'passage_id':p,'target_id':t} for p,t in VALID if (p,t) not in present]
 if missing_valid: problems.append({'kind':'adjudicated_valid_reviews_missing','items':missing_valid})
 regressions=[]
 for tid,h in histories.items():
  hi=0
  for e in sorted(h,key=lambda x:x['sequence']):
   cur=STAGE.get(e['stage'],0)
   if cur<hi: regressions.append({'target_id':tid,**e})
   hi=max(hi,cur)
 if regressions: problems.append({'kind':'stage_regressions','items':regressions})
 out={'schema_version':1,'date':'2026-08-20','language':'fr','level':'A1','bound_sha256':bound,'status':'PASS_DETERMINISTIC_REVIEW_INTEGRITY_ROUND2' if not problems else 'FAIL','scope':{'records':60,'questions':600,'answers':600},'round1_removed_count':18,'round1_stage_relabels':2,'round2_candidate_adjudication':{'initial_residual_candidates':18,'valid_exact_surface':1,'valid_high_confidence_morphology':8,'removed_as_phantom':9},'round2_removed_survivor_count':sum(1 for p in problems if p.get('kind')=='round2_removed_review_survived'),'adjudicated_valid_reviews_preserved':not missing_valid,'stage_regression_count':len(regressions),'problems':problems,'known_unresolved_spacing_item':{'target_id':'fr-rank-0047','lemma':'venir','kind':'missing_later_R3_opportunity','status':'UNRESOLVED_DO_NOT_FABRICATE'},'limitations':'This closes the deterministic visibility/metadata candidate set adjudicated in this repair branch. It does not establish review spacing adequacy, semantic correctness, coverage, naturalness, Gate A evidence, or educator release readiness.','release_effect':'French remains REOPEN_REQUIRED.'}
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps({'status':out['status'],'problems':len(problems),'stage_regressions':len(regressions)},ensure_ascii=False))
 if problems: raise SystemExit('French round2 postrepair audit failed')
if __name__=='__main__': main()
