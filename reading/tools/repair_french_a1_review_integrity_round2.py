import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/french/a1/passages.jsonl'; OUT=ROOT/'reading/audit/french_a1_review_integrity_repair_round2_2026-08-20.json'
EXPECTED='714cf8d41df917d2deb745f1cd9e82586a75f59cdaa4bff2eb494144a5345037'
REMOVE={
 ('fr-a1-u03-p03','fr-rank-0032','si'),('fr-a1-u03-p04','fr-rank-0044','sur'),('fr-a1-u03-p05','fr-rank-0037','plus'),
 ('fr-a1-u04-p02','fr-rank-0024','qui'),('fr-a1-u04-p02','fr-rank-0025','mais'),('fr-a1-u04-p03','fr-rank-0027','nous'),
 ('fr-a1-u04-p04','fr-rank-0030','bien'),('fr-a1-u04-p04','fr-rank-0041','moi'),('fr-a1-u04-p05','fr-rank-0042','oui')}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 before=sha(PATH)
 if before!=EXPECTED: raise SystemExit(f'hash drift {before}')
 rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]; removed=[]; seen=set()
 for p in rows:
  nr=[]
  for r in p.get('review_lexical_targets',[]):
   key=(p['id'],r.get('id'),r.get('form'))
   if key in REMOVE:
    if r.get('review_stage')!='R2' or r.get('representation')!='other': raise SystemExit(f'precondition mismatch {key}: {r}')
    removed.append({'passage_id':p['id'],'target_id':r.get('id'),'form':r.get('form'),'stage':r.get('review_stage'),'representation':r.get('representation')}); seen.add(key); continue
   nr.append(r)
  p['review_lexical_targets']=nr
 if seen!=REMOVE or len(removed)!=9: raise SystemExit(f'coverage mismatch missing={sorted(REMOVE-seen)} removed={len(removed)}')
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)): raise SystemExit('structural regression')
 if any(len(r.get('questions',[]))!=10 or len(r.get('answer_key',[]))!=10 for r in rows): raise SystemExit('Q/A cardinality regression')
 PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8'); after=sha(PATH)
 out={'schema_version':1,'date':'2026-08-20','language':'fr','level':'A1','status':'SECOND_BOUNDED_REPAIR_APPLIED_NEEDS_POSTREPAIR_AUDIT','before_sha256':before,'after_sha256':after,'review_declarations_removed':9,'learner_facing_text_changed':False,'questions_changed':False,'answers_changed':False,'evidence_basis':['No exact form/lemma on any learner-facing surface.','No explicit target_id linkage in any question.','High-confidence morphology pass found no applicable variant; all nine forms are non-inflecting in the intended lexical identity.','All nine declarations were representation=other, review_stage=R2.'],'removed':removed,'preserved_as_valid_from_same_candidate_set':['fr-rank-0019 ce via question prompts','fr-rank-0039 voir via voit','fr-rank-0047 venir via vient','fr-rank-0060 prendre via prend/prends','fr-rank-0014 faire via fait','fr-rank-0022 dire via dit','fr-rank-0036 devoir via devons','fr-rank-0043 tout via tous'],'known_unresolved_spacing_item':'fr-rank-0047 venir still lacks a natural later R3 opportunity; this repair does not fabricate one.','release_effect':'French remains REOPEN_REQUIRED.'}
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps({'removed':9,'after':after},ensure_ascii=False))
if __name__=='__main__': main()
