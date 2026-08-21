import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/'reading/urdu/a1/passages.jsonl'; STAGE8=ROOT/'reading/urdu/a1/staging/unit08'; STAGE9=ROOT/'reading/urdu/a1/staging/unit09'; LEX=ROOT/'reading/lexicons/urdu.jsonl'; OUT=ROOT/'reading/audit/urdu_a1_unit10_target_probe_2026-08-21.json'
EXPECTED_CANON='b4fcf0bbc07d62cd3e743b8d0a6d49df2d6b0df3d03aa892384d0501a7ef1d4a'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load_stage(folder,unit,start): return [json.loads((folder/f'ur-a1-u{unit:02d}-p{i:02d}.json').read_text(encoding='utf-8')) for i in range(1,7)]
def agg(rows): return hashlib.sha256(''.join(json.dumps(p,ensure_ascii=False,sort_keys=True) for p in rows).encode('utf-8')).hexdigest()
def main():
 if sha(CANON)!=EXPECTED_CANON: raise SystemExit('canonical hash drift')
 canon=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
 s8=load_stage(STAGE8,8,43); s9=load_stage(STAGE9,9,49)
 if len(canon)!=42 or [p.get('sequence') for p in canon]!=list(range(1,43)): raise SystemExit('canonical frontier drift')
 if [p.get('sequence') for p in s8]!=list(range(43,49)) or [p.get('sequence') for p in s9]!=list(range(49,55)): raise SystemExit('staged frontier drift')
 used_ids={t.get('id') for p in canon+s8+s9 for t in p.get('new_lexical_targets',[])}; used_forms={t.get('form') for p in canon+s8+s9 for t in p.get('new_lexical_targets',[])}
 lex=[json.loads(x) for x in LEX.read_text(encoding='utf-8').splitlines() if x.strip()]
 c=[]
 for r in lex:
  rank=r.get('rank') or 0
  if not 350<=rank<=499: continue
  if r.get('planning_band')!='A1_core_candidate' or r.get('source_file')!='urdu_top1000.csv': continue
  if r.get('id') in used_ids or r.get('form') in used_forms: continue
  c.append({k:r.get(k) for k in ['id','rank','form','meaning_en_source','part_of_speech_source']})
 c=sorted(c,key=lambda x:x['rank'])
 OUT.write_text(json.dumps({'schema_version':1,'date':'2026-08-21','language':'ur','level':'A1','unit':10,'status':'TARGET_PROBE_ONLY_NO_SELECTION','bound_canonical_sha256':EXPECTED_CANON,'bound_unit08_stage_aggregate_sha256':agg(s8),'bound_unit09_stage_aggregate_sha256':agg(s9),'used_target_count_through_staged_sequence54':len(used_ids),'focused_rank_window':'350-499','candidate_count':len(c),'candidates':c,'selection_rules':['Use source-backed unused IDs/forms only.','Prefer concrete/high-utility A1 senses with low ambiguity or easily controlled polysemy.','Use two fresh targets in P01-P05 and zero new targets in P06.','Validate first-introduction order, source identity, exposure counts, review visibility, learner-facing script, and staged-frontier binding.'],'release_effect':'Planning only; no learner-facing content changed.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'used':len(used_ids),'candidates':len(c),'stage8':agg(s8),'stage9':agg(s9)},ensure_ascii=False))
if __name__=='__main__': main()
