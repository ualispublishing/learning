#!/usr/bin/env python3
"""Record Arabic Gate C A1 Unit 6 decisions and rebind affected Gate B evidence."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
CANON=READING/'arabic/a1/passages.jsonl'
OUT=READING/'audit/arabic_gate_c_decisions_2026-09-05/a1_u06.json'
GATE_B=READING/'audit/arabic_gate_b_decisions_2026-08-30/a1_u06.json'
OLD_HASHES={
'ar-a1-u06-p01':'1af319eb2858c8c1087ba2d110b407c6f393cb599c4afa752f4671c47e108584',
'ar-a1-u06-p02':'ab20dadf13a257667002d14a2883f40aec6793ef7da01d97995dee2cabb5b62f',
'ar-a1-u06-p03':'c1e702105b8385827045caa5645d197ed49fe409ae1deae90ce48c486bce6a65',
'ar-a1-u06-p04':'19867db7e1d6d6daf6b02349fa4bb51458aa9119333f9c5c6411defa7cf31924',
'ar-a1-u06-p05':'ad17db327f44a4be7e51da8d32aa68d2f84ac68fe0a2d2657c11f2019862e921',
'ar-a1-u06-p06':'4f62eab28396c814da7c560da46940b075732cd770db4983e059e7de2d5b7b0e'}
NEW_PROMPTS={
('ar-a1-u06-p01','q9'):'اختر من «طريق» و«موقع»: هذا _____ قصير إلى السوق.',
('ar-a1-u06-p01','q10'):'اختر من «نحو» و«تحت»: مشيت _____ الباب.',
('ar-a1-u06-p02','q9'):'اختر من «السيارة» و«الطريق»: أبي يقود _____ إلى العمل.',
('ar-a1-u06-p02','q10'):'اختر من «يصل» و«يبدأ»: القطار _____ إلى المحطة في الثامنة.',
('ar-a1-u06-p03','q9'):'إذا كانت الحقيبة أسفل الكرسي، أكمل: الحقيبة _____ الكرسي.',
('ar-a1-u06-p04','q9'):'إذا كنت تطلب من سامر التوجه إلى الصف، أكمل الأمر: _____ إلى الصف الآن.',
('ar-a1-u06-p04','q10'):'أكمل بالفعل الذي يعني أنه يبقى عند الباب حتى تأتي الحافلة: سامر _____ الحافلة عند الباب.',
('ar-a1-u06-p05','q9'):'اختر من «موقع» و«وسط»: ما _____ المدرسة على هذه الخريطة؟',
('ar-a1-u06-p05','q10'):'إذا كانت الشجرة في المنتصف، أكمل: الشجرة في _____ الحديقة.'}
REVAL={'date':'2026-09-05','gate_c_artifact':'reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u06.json','scope':[f'{p} question {q}' for p,q in NEW_PROMPTS],'gate_b_language_recheck':'PASS','reason':'Gate C constrained nine underdetermined transfer items across A1 Unit 6 so the intended route, direction, transport, arrival, spatial, imperative, waiting, map-location, and center answers are uniquely defensible; replacements were rechecked for A1 MSA wording and Gate B was rebound to exact-current learner-facing content.','release_claim':False}

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def payload(r):
    a={x.get('question_id'):x for x in r.get('answer_key',[])}
    notes='\n'.join(r.get('quality',{}).get('notes',[])); hist='naturalness' in notes.lower()
    return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8'))

def finding(pid,qid):
    reasons={
      ('ar-a1-u06-p01','q9'):'The original route cloze also admits مسار and similar nouns. Constrain it to the reviewed طريق/موقع contrast.',
      ('ar-a1-u06-p01','q10'):'The original motion cloze admits إلى and other direction expressions. Constrain it to the reviewed نحو/تحت contrast.',
      ('ar-a1-u06-p02','q9'):'The original object cloze allows سيارة, سيارته and other vehicles. Constrain it to the reviewed السيارة/الطريق choice.',
      ('ar-a1-u06-p02','q10'):'The original train cloze allows several motion verbs. Constrain it to the يصل/يبدأ contrast.',
      ('ar-a1-u06-p03','q9'):'The original location cloze allows multiple spatial relations. Add the explicit below relation so تحت is uniquely grounded.',
      ('ar-a1-u06-p04','q9'):'The original imperative cloze does not identify the addressee, so gender/number forms compete. Name Samer so اذهب is uniquely appropriate.',
      ('ar-a1-u06-p04','q10'):'The original bus cloze admits several plausible actions. Constrain it to the waiting meaning tested by ينتظر.',
      ('ar-a1-u06-p05','q9'):'The original map cloze can take مكان, عنوان and other location nouns. Constrain it to the موقع/وسط contrast.',
      ('ar-a1-u06-p05','q10'):'The original garden cloze admits several location words. Add the explicit middle relation so وسط is uniquely grounded.'}
    ordinal=1 if qid=='q9' else 2
    return {'finding_id':f'{pid}-gC-{ordinal:02d}','field':f'question {qid}','dimension':'competing_answer_ambiguity','severity':'major','status':'REPAIRED','rationale':reasons[(pid,qid)]}

def build(rows,canon_sha):
    ids=[f'ar-a1-u06-p{i:02d}' for i in range(1,7)]; by={r['id']:r for r in rows}; hs={pid:lh(by[pid]) for pid in ids}
    for (pid,qid),new in NEW_PROMPTS.items():
        if {x['id']:x for x in by[pid]['questions']}[qid]['prompt']!=new: raise SystemExit(f'{pid}/{qid}: repaired prompt absent')
    repaired={p for p,_ in NEW_PROMPTS}
    for pid in ids:
        if pid in repaired:
            if hs[pid]==OLD_HASHES[pid]: raise SystemExit(f'{pid}: learner hash did not change')
        elif hs[pid]!=OLD_HASHES[pid]: raise SystemExit(f'{pid}: unexpected learner-facing drift')
    dec=[]
    by_findings={pid:[] for pid in ids}
    for pid,qid in NEW_PROMPTS: by_findings[pid].append(finding(pid,qid))
    for pid in ids:
        fs=by_findings[pid]
        dec.append({'passage_id':pid,'learner_facing_sha256':hs[pid],'decision':'PASS_AFTER_REPAIR' if fs else 'PASS','qa_pairs_reviewed':10,'finding_count':len(fs),'findings':fs})
    doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'A1','unit':6,'date':'2026-09-05','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/a1/passages.jsonl','canonical_sha256':canon_sha,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':9,'decisions':dec,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; the level SHA records the review-time snapshot.'}
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
        if json.loads(OUT.read_text(encoding='utf-8'))!=doc: raise SystemExit('existing Unit 6 evidence drift')
        verify_gb(json.loads(GATE_B.read_text(encoding='utf-8')),hs)
        print(json.dumps({'unit':6,'idempotent_verification':True,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':9,'release_claim':False},indent=2)); return
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    g=json.loads(GATE_B.read_text(encoding='utf-8')); bd={d['passage_id']:d for d in g['decisions']}
    if set(bd)!=set(OLD_HASHES): raise SystemExit('Gate B Unit 6 scope drift')
    for pid,h in OLD_HASHES.items():
        if bd[pid]['learner_facing_sha256']!=h: raise SystemExit(f'{pid}: Gate B pre-rebind hash drift')
    g['canonical_sha256']=canon
    for pid,h in hs.items(): bd[pid]['learner_facing_sha256']=h
    rv=g.setdefault('post_gate_c_revalidations',[])
    if REVAL in rv: raise SystemExit('duplicate Unit 6 revalidation')
    rv.append(REVAL); GATE_B.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'unit':6,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':9,'canonical_sha256':canon,'release_claim':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
