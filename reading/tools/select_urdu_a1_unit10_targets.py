import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/'reading/urdu/a1/passages.jsonl'; S8=ROOT/'reading/urdu/a1/staging/unit08'; S9=ROOT/'reading/urdu/a1/staging/unit09'; LEX=ROOT/'reading/lexicons/urdu.jsonl'; OUT=ROOT/'reading/audit/urdu_a1_unit10_target_selection_2026-08-21.json'
EXPECTED='b4fcf0bbc07d62cd3e743b8d0a6d49df2d6b0df3d03aa892384d0501a7ef1d4a'
SELECT=['ur-rank-0353','ur-rank-0362','ur-rank-0364','ur-rank-0365','ur-rank-0368','ur-rank-0397','ur-rank-0383','ur-rank-0390','ur-rank-0392','ur-rank-0398']
PASSAGES=['ur-a1-u10-p01','ur-a1-u10-p01','ur-a1-u10-p02','ur-a1-u10-p02','ur-a1-u10-p03','ur-a1-u10-p03','ur-a1-u10-p04','ur-a1-u10-p04','ur-a1-u10-p05','ur-a1-u10-p05']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(folder,u,start): return [json.loads((folder/f'ur-a1-u{u:02d}-p{i:02d}.json').read_text(encoding='utf-8')) for i in range(1,7)]
def agg(rows): return hashlib.sha256(''.join(json.dumps(p,ensure_ascii=False,sort_keys=True) for p in rows).encode('utf-8')).hexdigest()
def main():
 if sha(CANON)!=EXPECTED: raise SystemExit('canonical hash drift')
 canon=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]; s8=load(S8,8,43); s9=load(S9,9,49)
 if len(canon)!=42 or [p.get('sequence') for p in canon]!=list(range(1,43)) or [p.get('sequence') for p in s8]!=list(range(43,49)) or [p.get('sequence') for p in s9]!=list(range(49,55)): raise SystemExit('frontier structure drift')
 used_ids={t.get('id') for p in canon+s8+s9 for t in p.get('new_lexical_targets',[])}; used_forms={t.get('form') for p in canon+s8+s9 for t in p.get('new_lexical_targets',[])}
 lex={r['id']:r for r in [json.loads(x) for x in LEX.read_text(encoding='utf-8').splitlines() if x.strip()]}
 chosen=[]
 for tid,pid in zip(SELECT,PASSAGES):
  r=lex.get(tid)
  if not r: raise SystemExit(f'missing {tid}')
  if tid in used_ids or r.get('form') in used_forms: raise SystemExit(f'collision {tid} {r.get("form")}')
  if r.get('planning_band')!='A1_core_candidate' or r.get('source_file')!='urdu_top1000.csv': raise SystemExit(f'not A1 source-backed {tid}')
  chosen.append({'id':tid,'rank':r.get('rank'),'form':r.get('form'),'meaning_en_source':r.get('meaning_en_source'),'part_of_speech_source':r.get('part_of_speech_source'),'passage':pid})
 if len({x['id'] for x in chosen})!=10 or len({x['form'] for x in chosen})!=10: raise SystemExit('selection duplicate')
 OUT.write_text(json.dumps({'schema_version':1,'date':'2026-08-21','language':'ur','level':'A1','unit':10,'status':'TARGET_SELECTION_VERIFIED_FOR_STAGING','bound_canonical_sha256':EXPECTED,'bound_unit08_stage_aggregate_sha256':agg(s8),'bound_unit09_stage_aggregate_sha256':agg(s9),'used_target_count_through_staged_sequence54':len(used_ids),'selection_policy':['Exact IDs and forms verified unused through staged sequence 54.','All selected items are A1_core_candidate entries from urdu_top1000.csv.','Prefer concrete/high-utility everyday senses with low ambiguity or easily controlled polysemy.','Use two fresh targets in P01-P05 and zero new targets in P06.'],'theme':'everyday description, language, routines, social plans, and simple instructions','selected_targets':chosen,'checkpoint':{'passage':'ur-a1-u10-p06','new_targets':0,'reviews_all_ten_selected_targets':True},'release_effect':'Planning/staging evidence only; Urdu remains non-release-ready.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'selected':len(chosen),'forms':[x['form'] for x in chosen],'stage8':agg(s8),'stage9':agg(s9)},ensure_ascii=False))
if __name__=='__main__': main()
