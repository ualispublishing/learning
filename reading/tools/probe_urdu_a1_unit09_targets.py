import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/'reading/urdu/a1/passages.jsonl'
STAGE8=ROOT/'reading/urdu/a1/staging/unit08'
LEX=ROOT/'reading/lexicons/urdu.jsonl'
OUT=ROOT/'reading/audit/urdu_a1_unit09_target_probe_2026-08-20.json'
EXPECTED_CANON='b4fcf0bbc07d62cd3e743b8d0a6d49df2d6b0df3d03aa892384d0501a7ef1d4a'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if sha(CANON)!=EXPECTED_CANON: raise SystemExit('canonical hash drift')
 canon=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(canon)!=42 or [p.get('sequence') for p in canon]!=list(range(1,43)): raise SystemExit('expected canonical 1-42')
 stage=[]
 for i in range(1,7):
  p=STAGE8/f'ur-a1-u08-p{i:02d}.json'
  if not p.exists(): raise SystemExit(f'missing {p.name}')
  stage.append(json.loads(p.read_text(encoding='utf-8')))
 if [p.get('sequence') for p in stage]!=list(range(43,49)): raise SystemExit('Unit08 staging sequence drift')
 used_ids={t.get('id') for p in canon+stage for t in p.get('new_lexical_targets',[])}
 used_forms={t.get('form') for p in canon+stage for t in p.get('new_lexical_targets',[])}
 lex=[json.loads(x) for x in LEX.read_text(encoding='utf-8').splitlines() if x.strip()]
 c=[]
 for r in lex:
  rank=r.get('rank') or 0
  if not 500<=rank<=850: continue
  if r.get('planning_band')!='A1_core_candidate' or r.get('source_file')!='urdu_top1000.csv': continue
  if r.get('id') in used_ids or r.get('form') in used_forms: continue
  c.append({k:r.get(k) for k in ['id','rank','form','meaning_en_source','part_of_speech_source']})
 stage8_hash=hashlib.sha256(''.join(json.dumps(p,ensure_ascii=False,sort_keys=True) for p in stage).encode('utf-8')).hexdigest()
 OUT.write_text(json.dumps({'schema_version':1,'date':'2026-08-20','language':'ur','level':'A1','unit':9,'status':'TARGET_PROBE_ONLY_NO_SELECTION','bound_canonical_sha256':EXPECTED_CANON,'bound_unit08_stage_aggregate_sha256':stage8_hash,'used_target_count_through_staged_sequence48':len(used_ids),'candidate_count':len(c),'candidates':c,'selection_rules':['Use source-backed unused IDs/forms only.','Prefer concrete, high-utility A1 senses with low ambiguity.','Use two fresh targets in P01-P05 and zero new targets in P06.','Validate first-introduction order, source identity, exposure counts, review visibility, and learner-facing script before staging is considered complete.'],'release_effect':'Planning only; no learner-facing content changed.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'candidates':len(c),'stage8_hash':stage8_hash},ensure_ascii=False))
if __name__=='__main__': main()
