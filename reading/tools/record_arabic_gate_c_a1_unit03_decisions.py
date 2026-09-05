#!/usr/bin/env python3
"""Record Arabic Gate C A1 Unit 3 decisions and rebind affected Gate B evidence."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; CANON=READING/'arabic/a1/passages.jsonl'
OUT=READING/'audit/arabic_gate_c_decisions_2026-09-05/a1_u03.json'; GATE_B=READING/'audit/arabic_gate_b_decisions_2026-08-30/a1_u03.json'
OLD_HASHES={
'ar-a1-u03-p01':'3700402b6143b4979fc7817037958d369aab03b79c129a9e839d0c4fa28099a5','ar-a1-u03-p02':'838e38a3b37d10890e64368760d0d6a50bbaeed280d89cf0b1dd79c6c11efca5','ar-a1-u03-p03':'dd134f963a00e141c8b1f3fcd71cd3dfcf0a65ac737b0a2d6ef7b16386a089f4','ar-a1-u03-p04':'b4dc7cbdd74ba97320671ec67dae4cfd573034ff34c21919664c0cf281fdf95b','ar-a1-u03-p05':'3d205239ca7cf963427d9c5f6861b33b609220fa2509de9e419ae6952a61b072','ar-a1-u03-p06':'e440fbea2aeb84ded07f530715b777d6baa9d03b52029805778187eb0531f978'}
NEW_PROMPT='أكمل بما يعني واحدة إضافية: هذه تفاحة صغيرة؛ أريد تفاحة _____. '
REVAL={'date':'2026-09-05','gate_c_artifact':'reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u03.json','scope':['ar-a1-u03-p05 question q10'],'gate_b_language_recheck':'PASS','reason':'Gate C constrained an open cloze so أخرى is the uniquely intended additional-item answer; the replacement was rechecked for A1 MSA wording and Gate B was rebound to exact-current learner-facing content.','release_claim':False}
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def payload(r):
 a={x.get('question_id'):x for x in r.get('answer_key',[])}; notes='\n'.join(r.get('quality',{}).get('notes',[])); hist='naturalness' in notes.lower()
 return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def build(rows,canon_sha):
 ids=[f'ar-a1-u03-p{i:02d}' for i in range(1,7)]; by={r['id']:r for r in rows}; hs={pid:lh(by[pid]) for pid in ids}
 q={x['id']:x for x in by['ar-a1-u03-p05']['questions']}['q10']
 if q['prompt']!=NEW_PROMPT.rstrip(): raise SystemExit('p05/q10 repaired prompt absent')
 for pid in ids:
  if pid=='ar-a1-u03-p05':
   if hs[pid]==OLD_HASHES[pid]: raise SystemExit('p05 learner hash did not change')
  elif hs[pid]!=OLD_HASHES[pid]: raise SystemExit(f'{pid}: unexpected learner-facing drift')
 dec=[]
 for pid in ids:
  if pid=='ar-a1-u03-p05': dec.append({'passage_id':pid,'learner_facing_sha256':hs[pid],'decision':'PASS_AFTER_REPAIR','qa_pairs_reviewed':10,'finding_count':1,'findings':[{'finding_id':f'{pid}-gC-01','field':'question q10','dimension':'competing_answer_ambiguity','severity':'major','status':'REPAIRED','rationale':'The original cloze «هذه تفاحة صغيرة؛ أريد تفاحة ___» allows many plausible adjectives, so أخرى was not uniquely defensible. Constrain the task to the meaning “one additional” while preserving the target and keyed answer.'}]})
  else: dec.append({'passage_id':pid,'learner_facing_sha256':hs[pid],'decision':'PASS','qa_pairs_reviewed':10,'finding_count':0,'findings':[]})
 doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'A1','unit':3,'date':'2026-09-05','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/a1/passages.jsonl','canonical_sha256':canon_sha,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':1,'fresh_findings':1,'decisions':dec,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; the level SHA records the review-time snapshot.'}
 return doc,hs
def verify_gb(g,hs):
 bd={d['passage_id']:d for d in g['decisions']}
 for pid,h in hs.items():
  if bd[pid]['learner_facing_sha256']!=h: raise SystemExit(f'{pid}: Gate B hash mismatch')
 if g.get('post_gate_c_revalidations',[]).count(REVAL)!=1: raise SystemExit('missing/duplicate Gate B revalidation')
def main():
 raw=CANON.read_bytes(); canon=sha(raw); rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]
 doc,hs=build(rows,canon)
 if OUT.exists():
  if json.loads(OUT.read_text())!=doc: raise SystemExit('existing Unit 3 evidence drift')
  verify_gb(json.loads(GATE_B.read_text()),hs); print(json.dumps({'unit':3,'idempotent_verification':True,'records_reviewed':6,'qa_pairs_reviewed':60,'fresh_findings':1,'release_claim':False},indent=2)); return
 OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
 g=json.loads(GATE_B.read_text()); bd={d['passage_id']:d for d in g['decisions']}
 if set(bd)!=set(OLD_HASHES): raise SystemExit('Gate B Unit 3 scope drift')
 for pid,h in OLD_HASHES.items():
  if bd[pid]['learner_facing_sha256']!=h: raise SystemExit(f'{pid}: Gate B pre-rebind hash drift')
 g['canonical_sha256']=canon
 for pid,h in hs.items(): bd[pid]['learner_facing_sha256']=h
 rv=g.setdefault('post_gate_c_revalidations',[])
 if REVAL in rv: raise SystemExit('duplicate Unit 3 revalidation')
 rv.append(REVAL); GATE_B.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'unit':3,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':1,'fresh_findings':1,'canonical_sha256':canon,'release_claim':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
