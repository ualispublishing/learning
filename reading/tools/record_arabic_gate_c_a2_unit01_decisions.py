#!/usr/bin/env python3
"""Record Arabic Gate C A2 Unit 1 decisions and rebind affected Gate B evidence."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
CANON=READING/'arabic/a2/passages.jsonl'
OUT=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u01.json'
GATE_B=READING/'audit/arabic_gate_b_decisions_2026-08-30/a2_u01.json'
OLD_HASHES={
'ar-a2-u01-p01':'2c717d9708753010eafc75d00ad1672974e1ba3ddbb00a763f5da3636807a528',
'ar-a2-u01-p02':'c9744d7dbdfd7aced5e7b5ca84d78ff8fa9775d5dcfcfc798b27ca04e4342b77',
'ar-a2-u01-p03':'09b302371341fb67343660297dae933824adae9638e059c71e9c902fd222bac9',
'ar-a2-u01-p04':'14bba652c4616b6a0e3f038889a3e504c00767d9292f6a1f1d2b634a87ea5773',
'ar-a2-u01-p05':'83248a90a0636e3ef2ff893f159bfe6fc89c6f6f320c25a337763448c197f536',
'ar-a2-u01-p06':'cf3335a3cb51eca6158e7c1955f34056cefc437a5f3b434d9a9f4693304ba595'}
NEW_PROMPTS={
('ar-a2-u01-p01','q9'):'اختر من «الشارع» و«الخدمة»: يوجد البنك في _____ الرئيسي قرب السوق.',
('ar-a2-u01-p01','q10'):'اختر من «خدمة» و«شارع»: يقدم هذا المكتب _____ للسكان كل صباح.',
('ar-a2-u01-p02','q9'):'اختر من «الهاتف» و«البنك»: اتصلت بالمكتب عبر _____ لمعرفة الموعد.',
('ar-a2-u01-p02','q10'):'اختر من «البنك» و«الهاتف»: ذهبت إلى _____ لأقوم بمعاملة مالية.',
('ar-a2-u01-p03','q9'):'اختر من «إعلانًا» و«رسالة»: وضع المركز _____ عن تغيير وقت العمل.',
('ar-a2-u01-p03','q10'):'اختر من «رسالة» و«إعلانًا»: أرسلت إلى صديقتي _____ فيها الموعد الجديد.',
('ar-a2-u01-p04','q9'):'اختر من «زيارة» و«قسم»: كانت هذه أول _____ لي للمركز الجديد.',
('ar-a2-u01-p04','q10'):'اختر من «قسم» و«زيارة»: اسأل في _____ الاستقبال عن الموعد.',
('ar-a2-u01-p05','q9'):'اختر من «قائمة» و«سعر»: قرأت _____ الطعام قبل أن أطلب.',
('ar-a2-u01-p05','q10'):'اختر من «سعر» و«قائمة»: سألت عن _____ الكتاب قبل شرائه.'}
REVAL={'date':'2026-09-06','gate_c_artifact':'reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u01.json','scope':[f'{p} question {q}' for p,q in NEW_PROMPTS],'gate_b_language_recheck':'PASS','reason':'Gate C constrained ten underdetermined A2 Unit 1 service-transfer items so the intended street, service, phone, bank, announcement, message, visit, department, list, and price answers are uniquely defensible; replacements were rechecked for A2 MSA wording and Gate B was rebound to exact-current learner-facing content.','release_claim':False}

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def payload(r):
    a={x.get('question_id'):x for x in r.get('answer_key',[])}; notes='\n'.join(r.get('quality',{}).get('notes',[])); hist='naturalness' in notes.lower()
    return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8'))

def finding(pid,qid,idx):
    reasons={
      ('ar-a2-u01-p01','q9'):'The original location cloze admits طريق and other location nouns. Constrain it to the reviewed الشارع/الخدمة contrast.',
      ('ar-a2-u01-p01','q10'):'The original office-output cloze admits مساعدة, معلومات and other service nouns. Constrain it to the خدمة/شارع contrast.',
      ('ar-a2-u01-p02','q9'):'The original contact-channel cloze admits الإنترنت and other channels. Constrain it to the الهاتف/البنك contrast.',
      ('ar-a2-u01-p02','q10'):'The original financial-transaction cloze admits مصرف and other financial institutions. Constrain it to the البنك/الهاتف contrast.',
      ('ar-a2-u01-p03','q9'):'The original posted-change cloze admits إشعارًا and other public notices. Constrain it to the إعلانًا/رسالة contrast.',
      ('ar-a2-u01-p03','q10'):'The original direct communication cloze admits بريدًا and other message forms. Constrain it to the رسالة/إعلانًا contrast.',
      ('ar-a2-u01-p04','q9'):'The original first-time cloze admits مرة and other visit expressions. Constrain it to the زيارة/قسم contrast.',
      ('ar-a2-u01-p04','q10'):'The original reception-location cloze admits مكتب and other institutional place nouns. Constrain it to the قسم/زيارة contrast.',
      ('ar-a2-u01-p05','q9'):'The original food-reading cloze admits قائمة الطعام, المنيو and other menu expressions. Constrain it to the قائمة/سعر contrast.',
      ('ar-a2-u01-p05','q10'):'The original book-cost cloze admits ثمن and other price nouns. Constrain it to the سعر/قائمة contrast.'}
    return {'finding_id':f'{pid}-gC-{idx:02d}','field':f'question {qid}','dimension':'competing_answer_ambiguity','severity':'major','status':'REPAIRED','rationale':reasons[(pid,qid)]}

def build(rows,canon_sha):
    ids=[f'ar-a2-u01-p{i:02d}' for i in range(1,7)]; by={r['id']:r for r in rows}; hs={pid:lh(by[pid]) for pid in ids}
    for (pid,qid),new in NEW_PROMPTS.items():
        if {x['id']:x for x in by[pid]['questions']}[qid]['prompt']!=new: raise SystemExit(f'{pid}/{qid}: repaired prompt absent')
    repaired={p for p,_ in NEW_PROMPTS}
    for pid in ids:
        if pid in repaired:
            if hs[pid]==OLD_HASHES[pid]: raise SystemExit(f'{pid}: learner hash did not change')
        elif hs[pid]!=OLD_HASHES[pid]: raise SystemExit(f'{pid}: unexpected learner-facing drift')
    byf={pid:[] for pid in ids}
    for pid in ids:
        qs=[q for p,q in NEW_PROMPTS if p==pid]
        for idx,qid in enumerate(qs,1): byf[pid].append(finding(pid,qid,idx))
    dec=[{'passage_id':pid,'learner_facing_sha256':hs[pid],'decision':'PASS_AFTER_REPAIR' if byf[pid] else 'PASS','qa_pairs_reviewed':10,'finding_count':len(byf[pid]),'findings':byf[pid]} for pid in ids]
    doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'A2','unit':1,'date':'2026-09-06','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/a2/passages.jsonl','canonical_sha256':canon_sha,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'decisions':dec,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; the level SHA records the review-time snapshot.'}
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
        if json.loads(OUT.read_text(encoding='utf-8'))!=doc: raise SystemExit('existing A2 Unit 1 evidence drift')
        verify_gb(json.loads(GATE_B.read_text(encoding='utf-8')),hs)
        print(json.dumps({'level':'A2','unit':1,'idempotent_verification':True,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'release_claim':False},indent=2)); return
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    g=json.loads(GATE_B.read_text(encoding='utf-8')); bd={d['passage_id']:d for d in g['decisions']}
    if set(bd)!=set(OLD_HASHES): raise SystemExit('Gate B A2 Unit 1 scope drift')
    for pid,h in OLD_HASHES.items():
        if bd[pid]['learner_facing_sha256']!=h: raise SystemExit(f'{pid}: Gate B pre-rebind hash drift')
    g['canonical_sha256']=canon
    for pid,h in hs.items(): bd[pid]['learner_facing_sha256']=h
    rv=g.setdefault('post_gate_c_revalidations',[])
    if REVAL in rv: raise SystemExit('duplicate A2 Unit 1 revalidation')
    rv.append(REVAL); GATE_B.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'level':'A2','unit':1,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'canonical_sha256':canon,'release_claim':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
