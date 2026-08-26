#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATHS={l:ROOT/f'reading/arabic/{l}/passages.jsonl' for l in ('b1','b2','c1','c2')}
REPORT=ROOT/'reading/audit/arabic_b1_c2_sentence_count_repair_2026-08-23.json'
EXPECTED={'b1':'53f114cd16a15f5da144b5a86a240ab131271ec1','b2':'a9486b2c38dc53661143e734c9797cd26fa1f742','c1':'3f68da825c50c3018f9e054cbeec27ba01b17be0','c2':'eb4105692d37c2dc38dc5241cee0edcabcf64585'}
REPAIRS={
'ar-b1-u02-p03':(15,16),'ar-b1-u02-p05':(17,19),'ar-b1-u04-p01':(16,17),'ar-b1-u04-p04':(17,18),
'ar-b1-u05-p01':(15,17),'ar-b1-u07-p01':(15,16),'ar-b1-u07-p02':(16,17),'ar-b1-u07-p03':(18,19),
'ar-b1-u08-p04':(14,16),'ar-b1-u08-p05':(17,19),'ar-b1-u08-p06':(21,22),'ar-b1-u10-p01':(16,18),
'ar-c2-u05-p03':(58,60),'ar-c2-u05-p05':(57,61),'ar-c2-u08-p06':(66,70),'ar-c2-u10-p01':(44,46),
}

def blob(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def load(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def dump(p,rows):p.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
def calc(text):return sum(str(text).count(p) for p in ('.','؟','!','۔'))
def main():
 actual={l:blob(p) for l,p in PATHS.items()}
 if actual!=EXPECTED:raise SystemExit(f'unexpected input blobs {actual}')
 rows={l:load(p) for l,p in PATHS.items()}; idx={l:{r['id']:r for r in rs} for l,rs in rows.items()};changes=[]
 for pid,(old,new) in REPAIRS.items():
  level=pid.split('-')[1];r=idx[level][pid]
  if r.get('sentence_count')!=old:raise SystemExit(f'{pid}: expected metadata {old}, got {r.get("sentence_count")}')
  actual_count=calc(r.get('text',''))
  if actual_count!=new:raise SystemExit(f'{pid}: expected calculated {new}, got {actual_count}')
  r['sentence_count']=new
  q=r.setdefault('quality',{});q['schema_check']='pending';q['status']='draft'
  notes=q.setdefault('notes',[]);note='Sentence-count metadata corrected 2026-08-23 from current learner text; learner-facing content unchanged.'
  if note not in notes:notes.append(note)
  changes.append({'passage_id':pid,'old':old,'new':new})
 if len(changes)!=16:raise SystemExit(f'expected 16 changes, got {len(changes)}')
 for l,p in PATHS.items():dump(p,rows[l])
 out={'schema_version':1,'date':'2026-08-23','input_blobs':actual,'output_blobs':{l:blob(p) for l,p in PATHS.items()},'changes':changes,'count':len(changes),'learner_text_changes':0,'quality_promotion':False,'status':'PASS_BOUNDED_METADATA_REPAIR'}
 REPORT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()
