#!/usr/bin/env python3
"""Record Arabic Gate C A1 Unit 5 decisions and rebind affected Gate B evidence."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
CANON=READING/'arabic/a1/passages.jsonl'
OUT=READING/'audit/arabic_gate_c_decisions_2026-09-05/a1_u05.json'
GATE_B=READING/'audit/arabic_gate_b_decisions_2026-08-30/a1_u05.json'
OLD_HASHES={
'ar-a1-u05-p01':'799ba2283396e61a881753a07d0baa1d32ab36d87c897a5408951df29f3e2c05',
'ar-a1-u05-p02':'07dfd7d1112bc6acd0b9b053e01d8af31632dabfe508f1651136f2f17c8324d6',
'ar-a1-u05-p03':'2ad9179c4514ace468dc98ad983abd395478a5ca5c9865e9a08e736f298063e0',
'ar-a1-u05-p04':'af0811be7cf6419fed3a6e92eb4f77d578fb790e387b811c14b2cae01169a404',
'ar-a1-u05-p05':'62373f6759d36f1c21ba9c6de9f6e5b76c0686781d1055bab2459e1d91a64257',
'ar-a1-u05-p06':'b0ea75b6d7e67d0bb840873011220b7c4bf7e044801c455d66439aad756b28a6'}
NEW_PROMPTS={
('ar-a1-u05-p01','q9'):'اختر من «بدأ» و«يبدأ» ثم أكمل عن أمس: _____ الدرس في الثامنة.',
('ar-a1-u05-p01','q10'):'اختر من «يأتي» و«يعود»: المعلم في غرفة المعلمين، ثم _____ إلى الصف للمرة الأولى هذا الصباح.',
('ar-a1-u05-p02','q9'):'أكمل بالفعل الذي يعني وجود شيء في المكان: _____ كتاب على الطاولة.',
('ar-a1-u05-p02','q10'):'أكمل بكلمة الشخص المسؤول عن المدرسة: _____ المدرسة يتحدث مع المعلمين.',
('ar-a1-u05-p03','q9'):'اختر من «دور» و«داخل»: دوري أن أكتب، و_____ أخي أن يقرأ.',
('ar-a1-u05-p03','q10'):'اختر من «داخل» و«خارج»: الطلاب _____ الصف الآن، وليسوا في الساحة.',
('ar-a1-u05-p04','q9'):'أكمل بالفعل الذي يعني أنه يتكلم: الطالب _____ عن كتابه أمام الصف.',
('ar-a1-u05-p04','q10'):'أكمل بالفعل الذي يعني أنه يقوم بعمله هناك: أبي _____ في مكتب قريب.',
('ar-a1-u05-p05','q9'):'اختر من «المقبل» و«الماضي»: في الشهر _____ سأزور صديقي.',
('ar-a1-u05-p05','q10'):'اختر من «يأتي» و«يعود»: بعد المدرسة _____ الطالب إلى منزله من جديد.'}
REVAL={'date':'2026-09-05','gate_c_artifact':'reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u05.json','scope':[f'{p} question {q}' for p,q in NEW_PROMPTS],'gate_b_language_recheck':'PASS','reason':'Gate C constrained ten underdetermined transfer clozes across A1 Unit 5 so each keyed target is uniquely defensible; replacements were rechecked for A1 MSA wording and Gate B was rebound to exact-current learner-facing content.','release_claim':False}

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def payload(r):
    a={x.get('question_id'):x for x in r.get('answer_key',[])}
    notes='\n'.join(r.get('quality',{}).get('notes',[])); hist='naturalness' in notes.lower()
    return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8'))

def finding(pid,qid):
    details={
      ('ar-a1-u05-p01','q9'):'The original cloze could take both بدأ and يبدأ because no time frame was supplied. Constrain it to a past event and explicit choice.',
      ('ar-a1-u05-p01','q10'):'The original arrival cloze could reasonably take يأتي or يعود. Constrain the first-arrival context and provide the contrast.',
      ('ar-a1-u05-p02','q9'):'The original existential cloze allowed several ways to state presence. Constrain the prompt to the target existence meaning.',
      ('ar-a1-u05-p02','q10'):'The original school-role cloze allowed several people who could speak with teachers. Constrain it to the person responsible for the school.',
      ('ar-a1-u05-p03','q9'):'The original role cloze admitted synonymous task nouns. Constrain it to the reviewed دور/داخل contrast.',
      ('ar-a1-u05-p03','q10'):'The original location cloze allowed داخل, خارج, or other location words. Constrain it with an explicit inside/outside contrast.',
      ('ar-a1-u05-p04','q9'):'The original verb cloze allowed several actions about a book. Constrain it to the speaking meaning tested by يتحدث.',
      ('ar-a1-u05-p04','q10'):'The original office cloze allowed many plausible actions. Constrain it to doing one’s work so يعمل is uniquely intended.',
      ('ar-a1-u05-p05','q9'):'The original future-month cloze allowed المقبل, القادم, التالي and similar answers. Constrain it to the المقبل/الماضي contrast.',
      ('ar-a1-u05-p05','q10'):'The original homeward cloze allowed several motion verbs. Constrain it to the يأتي/يعود contrast and explicit return sense.'}
    return {'finding_id':f'{pid}-gC-{1 if qid=="q9" else 2:02d}','field':f'question {qid}','dimension':'competing_answer_ambiguity','severity':'major','status':'REPAIRED','rationale':details[(pid,qid)]}

def build(rows,canon_sha):
    ids=[f'ar-a1-u05-p{i:02d}' for i in range(1,7)]; by={r['id']:r for r in rows}; hs={pid:lh(by[pid]) for pid in ids}
    for key,new in NEW_PROMPTS.items():
        pid,qid=key; q={x['id']:x for x in by[pid]['questions']}[qid]
        if q['prompt']!=new: raise SystemExit(f'{pid}/{qid}: repaired prompt absent')
    repaired={p for p,_ in NEW_PROMPTS}
    for pid in ids:
        if pid in repaired:
            if hs[pid]==OLD_HASHES[pid]: raise SystemExit(f'{pid}: learner hash did not change')
        elif hs[pid]!=OLD_HASHES[pid]: raise SystemExit(f'{pid}: unexpected learner-facing drift')
    dec=[]
    for pid in ids:
        if pid in repaired:
            fs=[finding(pid,'q9'),finding(pid,'q10')]
            dec.append({'passage_id':pid,'learner_facing_sha256':hs[pid],'decision':'PASS_AFTER_REPAIR','qa_pairs_reviewed':10,'finding_count':2,'findings':fs})
        else:
            dec.append({'passage_id':pid,'learner_facing_sha256':hs[pid],'decision':'PASS','qa_pairs_reviewed':10,'finding_count':0,'findings':[]})
    doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'A1','unit':5,'date':'2026-09-05','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/a1/passages.jsonl','canonical_sha256':canon_sha,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'decisions':dec,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; the level SHA records the review-time snapshot.'}
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
        if json.loads(OUT.read_text(encoding='utf-8'))!=doc: raise SystemExit('existing Unit 5 evidence drift')
        verify_gb(json.loads(GATE_B.read_text(encoding='utf-8')),hs)
        print(json.dumps({'unit':5,'idempotent_verification':True,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'release_claim':False},indent=2)); return
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    g=json.loads(GATE_B.read_text(encoding='utf-8')); bd={d['passage_id']:d for d in g['decisions']}
    if set(bd)!=set(OLD_HASHES): raise SystemExit('Gate B Unit 5 scope drift')
    for pid,h in OLD_HASHES.items():
        if bd[pid]['learner_facing_sha256']!=h: raise SystemExit(f'{pid}: Gate B pre-rebind hash drift')
    g['canonical_sha256']=canon
    for pid,h in hs.items(): bd[pid]['learner_facing_sha256']=h
    rv=g.setdefault('post_gate_c_revalidations',[])
    if REVAL in rv: raise SystemExit('duplicate Unit 5 revalidation')
    rv.append(REVAL); GATE_B.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'unit':5,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'canonical_sha256':canon,'release_claim':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
