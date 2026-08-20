import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/'reading/urdu/a1/passages.jsonl'; LEX=ROOT/'reading/lexicons/urdu.jsonl'; OUT=ROOT/'reading/audit/urdu_a1_unit08_target_probe_400_700_2026-08-20.json'; EXPECTED='b4fcf0bbc07d62cd3e743b8d0a6d49df2d6b0df3d03aa892384d0501a7ef1d4a'
def main():
 if hashlib.sha256(CANON.read_bytes()).hexdigest()!=EXPECTED: raise SystemExit('canonical hash drift')
 rows=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]; used={t.get('id') for p in rows for t in p.get('new_lexical_targets',[])}
 lex=[json.loads(x) for x in LEX.read_text(encoding='utf-8').splitlines() if x.strip()]
 c=[]
 for r in lex:
  rank=r.get('rank') or 0
  if not 400<=rank<=700 or r.get('planning_band')!='A1_core_candidate' or r.get('source_file')!='urdu_top1000.csv' or r.get('id') in used: continue
  c.append({k:r.get(k) for k in ['id','rank','form','meaning_en_source','part_of_speech_source']})
 OUT.write_text(json.dumps({'schema_version':1,'date':'2026-08-20','language':'ur','level':'A1','unit':8,'bound_canonical_sha256':EXPECTED,'candidate_count':len(c),'candidates':c,'note':'Manual selection required; this probe does not assert pedagogical suitability or sense safety.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(len(c))
if __name__=='__main__': main()
