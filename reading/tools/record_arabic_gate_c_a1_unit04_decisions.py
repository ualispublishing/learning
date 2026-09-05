#!/usr/bin/env python3
"""Record Arabic Gate C A1 Unit 4 decisions and rebind affected Gate B evidence."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
CANON=READING/'arabic/a1/passages.jsonl'
OUT=READING/'audit/arabic_gate_c_decisions_2026-09-05/a1_u04.json'
GATE_B=READING/'audit/arabic_gate_b_decisions_2026-08-30/a1_u04.json'
OLD_HASHES={
'ar-a1-u04-p01':'fad03007b5eedfc2f4a1d6a687ab5ff4619fea29b82bba74bd0426178cf05a11',
'ar-a1-u04-p02':'f24e17c93d2d25ec52e76cd797e14652234f89e5915651bf3b4b2ecf6072d7f8',
'ar-a1-u04-p03':'b90880d4e9cf5460c2b9ca5fb08e4ff9264cc076888fb2afe6a0cc3c8fc686f1',
'ar-a1-u04-p04':'9ba2a0ee057e272698d956e6c780da5c332aba783fd8a8b2dc1104e5bdddebb0',
'ar-a1-u04-p05':'b18d8a8d5efed737882b1e624aa186b64869dae84691e8000d315e1c35c17742',
'ar-a1-u04-p06':'5bee7d2ac90cd1e1f2fa52ff6c15aaa822f5f3398248888a917ae5f7cf13a9fa'}
P01_NEW='اختر من «أب» و«ابن»: هذا والدي؛ هو _____ي.'
P05_NEW='إذا كان المعلم خلف الطالب، أكمل: يقف الطالب _____ المعلم.'
REVAL={'date':'2026-09-05','gate_c_artifact':'reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u04.json','scope':['ar-a1-u04-p01 question q10','ar-a1-u04-p05 question q9'],'gate_b_language_recheck':'PASS','reason':'Gate C constrained two open clozes so the intended kinship and spatial answers are uniquely defensible; replacements were rechecked for A1 MSA wording and Gate B was rebound to exact-current learner-facing content.','release_claim':False}

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def payload(r):
    a={x.get('question_id'):x for x in r.get('answer_key',[])}
    notes='\n'.join(r.get('quality',{}).get('notes',[]))
    hist='naturalness' in notes.lower()
    return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8'))

def build(rows,canon_sha):
    ids=[f'ar-a1-u04-p{i:02d}' for i in range(1,7)]
    by={r['id']:r for r in rows}
    hs={pid:lh(by[pid]) for pid in ids}
    q1={x['id']:x for x in by['ar-a1-u04-p01']['questions']}['q10']
    q5={x['id']:x for x in by['ar-a1-u04-p05']['questions']}['q9']
    if q1['prompt']!=P01_NEW: raise SystemExit('p01/q10 repaired prompt absent')
    if q5['prompt']!=P05_NEW: raise SystemExit('p05/q9 repaired prompt absent')
    repaired={'ar-a1-u04-p01','ar-a1-u04-p05'}
    for pid in ids:
        if pid in repaired:
            if hs[pid]==OLD_HASHES[pid]: raise SystemExit(f'{pid}: learner hash did not change')
        elif hs[pid]!=OLD_HASHES[pid]:
            raise SystemExit(f'{pid}: unexpected learner-facing drift')
    dec=[]
    for pid in ids:
        if pid=='ar-a1-u04-p01':
            dec.append({'passage_id':pid,'learner_facing_sha256':hs[pid],'decision':'PASS_AFTER_REPAIR','qa_pairs_reviewed':10,'finding_count':1,'findings':[{'finding_id':f'{pid}-gC-01','field':'question q10','dimension':'competing_answer_ambiguity','severity':'major','status':'REPAIRED','rationale':'The original cloze «هذا والدي؛ هو ___ي» admits both أب and والد as valid kinship completions, so the keyed أب was not unique. Constrain the item to a choice between أب and ابن while preserving the keyed target.'}]})
        elif pid=='ar-a1-u04-p05':
            dec.append({'passage_id':pid,'learner_facing_sha256':hs[pid],'decision':'PASS_AFTER_REPAIR','qa_pairs_reviewed':10,'finding_count':1,'findings':[{'finding_id':f'{pid}-gC-01','field':'question q9','dimension':'competing_answer_ambiguity','severity':'major','status':'REPAIRED','rationale':'The original cloze «يقف الطالب ___ المعلم» admits several plausible spatial relations. Add the explicit condition that the teacher is behind the student so أمام is uniquely grounded.'}]})
        else:
            dec.append({'passage_id':pid,'learner_facing_sha256':hs[pid],'decision':'PASS','qa_pairs_reviewed':10,'finding_count':0,'findings':[]})
    doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'A1','unit':4,'date':'2026-09-05','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/a1/passages.jsonl','canonical_sha256':canon_sha,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':2,'fresh_findings':2,'decisions':dec,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; the level SHA records the review-time snapshot.'}
    return doc,hs

def verify_gb(g,hs):
    bd={d['passage_id']:d for d in g['decisions']}
    for pid,h in hs.items():
        if bd[pid]['learner_facing_sha256']!=h: raise SystemExit(f'{pid}: Gate B hash mismatch')
    if g.get('post_gate_c_revalidations',[]).count(REVAL)!=1: raise SystemExit('missing/duplicate Gate B revalidation')

def main():
    raw=CANON.read_bytes(); canon=sha(raw); rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
    doc,hs=build(rows,canon)
    if OUT.exists():
        if json.loads(OUT.read_text(encoding='utf-8'))!=doc: raise SystemExit('existing Unit 4 evidence drift')
        verify_gb(json.loads(GATE_B.read_text(encoding='utf-8')),hs)
        print(json.dumps({'unit':4,'idempotent_verification':True,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':2,'fresh_findings':2,'release_claim':False},indent=2)); return
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    g=json.loads(GATE_B.read_text(encoding='utf-8')); bd={d['passage_id']:d for d in g['decisions']}
    if set(bd)!=set(OLD_HASHES): raise SystemExit('Gate B Unit 4 scope drift')
    for pid,h in OLD_HASHES.items():
        if bd[pid]['learner_facing_sha256']!=h: raise SystemExit(f'{pid}: Gate B pre-rebind hash drift')
    g['canonical_sha256']=canon
    for pid,h in hs.items(): bd[pid]['learner_facing_sha256']=h
    rv=g.setdefault('post_gate_c_revalidations',[])
    if REVAL in rv: raise SystemExit('duplicate Unit 4 revalidation')
    rv.append(REVAL)
    GATE_B.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'unit':4,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':2,'fresh_findings':2,'canonical_sha256':canon,'release_claim':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
