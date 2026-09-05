#!/usr/bin/env python3
"""Record Arabic Gate C A1 Unit 8 decisions and rebind affected Gate B evidence."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
CANON=READING/'arabic/a1/passages.jsonl'
OUT=READING/'audit/arabic_gate_c_decisions_2026-09-05/a1_u08.json'
GATE_B=READING/'audit/arabic_gate_b_decisions_2026-08-30/a1_u08.json'
OLD_HASHES={
'ar-a1-u08-p01':'0d9b339a895757a5a5a04640edd0e09db2b0596ab419f6ebe79a2fc1a0e39e9b',
'ar-a1-u08-p02':'b5bfa64529e7f978e481d76baad56ba6771d76fa5a7f4972255d1f50183228d4',
'ar-a1-u08-p03':'274e6d674b5b1b2778544f7e2a9baf95e9c8f07816bdf646a0877105a4ddf8da',
'ar-a1-u08-p04':'619d0d3a4ae9f5e43b3699c0c231b7b04c3d9b8641704bcef36c68edbb68083f',
'ar-a1-u08-p05':'0db76d5f001fd63f8faf70d22926c884ad1ca0a1a214fa97b9bb4f9a4f59efe0',
'ar-a1-u08-p06':'cc5388925d4738353962fecfdb221f20fd546b62ff3a6fdff8df2a629cc95ac8'}
NEW_PROMPTS={
('ar-a1-u08-p01','q9'):'اختر من «يشعر» و«يصل»: سامر _____ بالتعب بعد يوم طويل.',
('ar-a1-u08-p01','q10'):'اختر من «مشكلة» و«مساعدة»: لا أجد كتابي؛ عندي _____.',
('ar-a1-u08-p02','q9'):'اختر من «حاجة» و«مساعدة»: عندي _____ إلى ماء.',
('ar-a1-u08-p02','q10'):'اختر من «مساعدة» و«حاجة»: طلبت _____ من صديقتي.',
('ar-a1-u08-p03','q9'):'اختر من «يدي» و«رأسي»: أمسك القلم ب_____.',
('ar-a1-u08-p03','q10'):'اختر من «رأسي» و«يدي»: أضع القبعة على _____.',
('ar-a1-u08-p04','q9'):'اختر من «قلبي» و«يدي»: أشعر بنبض _____ بعد الجري.',
('ar-a1-u08-p04','q10'):'اختر من «سالمًا» و«متعبًا»: سقط الكتاب لكنه بقي _____.',
('ar-a1-u08-p05','q9'):'اختر من «سأحاول» و«سأرفض»: _____ أن أقرأ الصفحة وحدي.',
('ar-a1-u08-p05','q10'):'اختر من «قوة» و«مشكلة»: بعد النوم عندي _____ أكثر.'}
REVAL={'date':'2026-09-05','gate_c_artifact':'reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u08.json','scope':[f'{p} question {q}' for p,q in NEW_PROMPTS],'gate_b_language_recheck':'PASS','reason':'Gate C constrained ten underdetermined needs/body transfer items across A1 Unit 8 so the intended feeling, problem, need, help, hand, head, heart, safe, try, and strength answers are uniquely defensible; replacements were rechecked for A1 MSA wording and Gate B was rebound to exact-current learner-facing content.','release_claim':False}

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def payload(r):
    a={x.get('question_id'):x for x in r.get('answer_key',[])}; notes='\n'.join(r.get('quality',{}).get('notes',[])); hist='naturalness' in notes.lower()
    return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8'))

def finding(pid,qid,idx):
    reasons={
      ('ar-a1-u08-p01','q9'):'The original feeling cloze also admits يحس and similar verbs. Constrain it to the reviewed يشعر/يصل contrast.',
      ('ar-a1-u08-p01','q10'):'The original missing-book cloze admits several nouns for a difficulty or need. Constrain it to the مشكلة/مساعدة contrast.',
      ('ar-a1-u08-p02','q9'):'The original need cloze admits ضرورة and similar nouns. Constrain it to the حاجة/مساعدة contrast.',
      ('ar-a1-u08-p02','q10'):'The original request cloze can take many requested objects. Constrain it to the مساعدة/حاجة contrast.',
      ('ar-a1-u08-p03','q9'):'The original hand cloze allows other body parts or instruments. Constrain it to the يدي/رأسي contrast.',
      ('ar-a1-u08-p03','q10'):'The original hat cloze allows other locations. Constrain it to the رأسي/يدي contrast.',
      ('ar-a1-u08-p04','q9'):'The original pulse cloze can refer to several body locations. Constrain it to the قلبي/يدي contrast.',
      ('ar-a1-u08-p04','q10'):'The original state cloze admits synonyms such as سليمًا. Constrain it to the سالمًا/متعبًا contrast.',
      ('ar-a1-u08-p05','q9'):'The original attempt cloze admits أريد, أستطيع, and other verbs. Constrain it to the سأحاول/سأرفض contrast.',
      ('ar-a1-u08-p05','q10'):'The original post-sleep cloze admits طاقة and other nouns. Constrain it to the قوة/مشكلة contrast.'}
    return {'finding_id':f'{pid}-gC-{idx:02d}','field':f'question {qid}','dimension':'competing_answer_ambiguity','severity':'major','status':'REPAIRED','rationale':reasons[(pid,qid)]}

def build(rows,canon_sha):
    ids=[f'ar-a1-u08-p{i:02d}' for i in range(1,7)]; by={r['id']:r for r in rows}; hs={pid:lh(by[pid]) for pid in ids}
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
    doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'A1','unit':8,'date':'2026-09-05','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/a1/passages.jsonl','canonical_sha256':canon_sha,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'decisions':dec,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; the level SHA records the review-time snapshot.'}
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
        if json.loads(OUT.read_text(encoding='utf-8'))!=doc: raise SystemExit('existing Unit 8 evidence drift')
        verify_gb(json.loads(GATE_B.read_text(encoding='utf-8')),hs)
        print(json.dumps({'unit':8,'idempotent_verification':True,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'release_claim':False},indent=2)); return
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    g=json.loads(GATE_B.read_text(encoding='utf-8')); bd={d['passage_id']:d for d in g['decisions']}
    if set(bd)!=set(OLD_HASHES): raise SystemExit('Gate B Unit 8 scope drift')
    for pid,h in OLD_HASHES.items():
        if bd[pid]['learner_facing_sha256']!=h: raise SystemExit(f'{pid}: Gate B pre-rebind hash drift')
    g['canonical_sha256']=canon
    for pid,h in hs.items(): bd[pid]['learner_facing_sha256']=h
    rv=g.setdefault('post_gate_c_revalidations',[])
    if REVAL in rv: raise SystemExit('duplicate Unit 8 revalidation')
    rv.append(REVAL); GATE_B.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'unit':8,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'canonical_sha256':canon,'release_claim':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
