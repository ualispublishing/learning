import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl'; OUT=ROOT/'reading/audit/arabic_a1_u07_u10_formal_inventory_2026-08-20.json'
EXPECTED='d6142ee56ec830c4a41cb7244fe99c65824cebbe59ff2e9b8f44d4640c9e228b'
FORMAL={'grammar_category','grammar_function','grammar_identification','person_form'}
PATS=[re.compile(r'التصنيف\s+النحوي|التصنيف\s+الصرفي|ما\s+نوع\s+«|ما\s+نوع\s+كلمة'),re.compile(r'الوظيفة\s+النحوية|ما\s+وظيفة\s+«|ما\s+وظيفة\s+كلمة|ما\s+الدور\s+النحوي')]
def main():
 bound=hashlib.sha256(PATH.read_bytes()).hexdigest()
 if bound!=EXPECTED: raise SystemExit(f'hash drift {bound}')
 rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
 findings=[]; by_unit={}
 for p in rows:
  if p.get('unit') not in {7,8,9,10}: continue
  amap={a.get('question_id'):a for a in p.get('answer_key',[])}
  for q in p.get('questions',[]):
   prompt=q.get('prompt') or ''; typ=q.get('type')
   if typ in FORMAL or any(pat.search(prompt) for pat in PATS):
    a=amap.get(q.get('id'),{})
    rec={'unit':p.get('unit'),'sequence':p.get('sequence'),'passage_id':p.get('id'),'question_id':q.get('id'),'type':typ,'prompt':prompt,'answer':a.get('answer'),'explanation':a.get('explanation'),'target_ids':q.get('target_ids',[])}
    findings.append(rec); by_unit[str(p.get('unit'))]=by_unit.get(str(p.get('unit')),0)+1
 OUT.write_text(json.dumps({'schema_version':1,'date':'2026-08-20','language':'ar','level':'A1','scope':'Units 07-10 / sequences 37-60','bound_sha256':bound,'finding_count':len(findings),'by_unit':by_unit,'findings':findings,'status':'INVENTORY_ONLY_NO_REPAIR','release_effect':'Audit evidence only; Arabic remains educator-blocked.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'count':len(findings),'by_unit':by_unit},ensure_ascii=False))
if __name__=='__main__': main()
