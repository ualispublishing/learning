import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/'reading/urdu/a1/passages.jsonl'; LEX=ROOT/'reading/lexicons/urdu.jsonl'; OUT=ROOT/'reading/audit/urdu_a1_unit08_target_probe_2026-08-20.json'
EXPECTED='b4fcf0bbc07d62cd3e743b8d0a6d49df2d6b0df3d03aa892384d0501a7ef1d4a'
def main():
 bound=hashlib.sha256(CANON.read_bytes()).hexdigest()
 if bound!=EXPECTED: raise SystemExit(f'canonical hash drift: {bound}')
 rows=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=42 or [r.get('sequence') for r in rows]!=list(range(1,43)): raise SystemExit('expected canonical sequences 1-42')
 used_ids={t.get('id') for p in rows for t in p.get('new_lexical_targets',[])}; used_forms={t.get('form') for p in rows for t in p.get('new_lexical_targets',[])}
 lex=[json.loads(x) for x in LEX.read_text(encoding='utf-8').splitlines() if x.strip()]
 candidates=[]
 for r in lex:
  if r.get('planning_band')!='A1_core_candidate' or r.get('source_file')!='urdu_top1000.csv': continue
  if r.get('id') in used_ids or r.get('form') in used_forms: continue
  candidates.append({k:r.get(k) for k in ['id','rank','form','match_form','meaning_en_source','part_of_speech_source','planning_band','source_file']})
 out={'schema_version':1,'date':'2026-08-20','language':'ur','level':'A1','unit':8,'status':'TARGET_PROBE_ONLY_NO_SELECTION','bound_canonical_sha256':bound,'canonical_passages':42,'used_deliberate_target_count':len(used_ids),'unused_a1_core_candidate_count':len(candidates),'first_160_unused_by_rank':candidates[:160],'selection_rules':['Select only source-backed unused IDs/forms.','Prefer unambiguous, concrete or high-utility A1 senses.','Reject politically specialized, highly polysemous, malformed, transliteration-only, or domain-narrow items unless context safely fixes the sense.','Use two fresh targets in P01-P05 and zero new in P06.','Recheck collisions against the final Unit07 canonical hash before staging.'],'release_effect':'Planning only; no learner-facing content changed.'}
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps({'unused':len(candidates),'shown':min(160,len(candidates))},ensure_ascii=False))
if __name__=='__main__': main()
