#!/usr/bin/env python3
"""Record Arabic Gate C A1 Unit 10 decisions and rebind affected Gate B evidence."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
CANON=READING/'arabic/a1/passages.jsonl'
OUT=READING/'audit/arabic_gate_c_decisions_2026-09-05/a1_u10.json'
GATE_B=READING/'audit/arabic_gate_b_decisions_2026-08-30/a1_u10.json'
OLD_HASHES={
'ar-a1-u10-p01':'06309f22b3e7d37e7112e78bd5ec3f6e638b0a4b9aef2998ff0d01dd6b20127c',
'ar-a1-u10-p02':'826dc0eef3ae85ffa8f4625bac727b1fe6bce1ac9b22e68e9e248ad51199ee79',
'ar-a1-u10-p03':'3e2fb77851a982ad89e554b4772e3cae878d2b3e9ab3f2efc8e1d6779f54ea7d',
'ar-a1-u10-p04':'bd4536493167713ee4c00dc355cfc34099a865278d8420ebe4e47d67545787db',
'ar-a1-u10-p05':'534fc8605ada428fb01d183db2235bbc0c18f3e13dc124519defd633708f16e4',
'ar-a1-u10-p06':'2f217fbbc82411744bf9157ba6a0aa3befde3c2ccd96edbccba79c7ddba7c8f1'}
NEW_PROMPTS={
('ar-a1-u10-p01','q9'):'اختر من «دائمًا» و«أحيانًا»: أنا _____ أضع كتابي في الحقيبة قبل المدرسة.',
('ar-a1-u10-p01','q10'):'اختر من «قليل» و«كثير»: بقي _____ من الماء في الكأس.',
('ar-a1-u10-p02','q9'):'اختر من «طريقة» و«نهاية»: هذه _____ سهلة لحفظ الكلمات.',
('ar-a1-u10-p02','q10'):'اختر من «مختلفًا» و«قليلًا»: اليوم أخذت طريقًا _____ إلى المدرسة.',
('ar-a1-u10-p03','q9'):'اختر من «مجموعة» و«نهاية»: تعمل _____ من الطلاب على المشروع.',
('ar-a1-u10-p03','q10'):'اختر من «نهاية» و«مجموعة»: في _____ الدرس نراجع الكلمات.',
('ar-a1-u10-p04','q9'):'إذا كان المقصود وقتًا قصيرًا جدًا، اختر من «لحظة» و«صورة»: انتظر _____ واحدة.',
('ar-a1-u10-p04','q10'):'اختر من «صورة» و«صفحة»: التقطنا _____ أمام المدرسة.',
('ar-a1-u10-p05','q9'):'اختر من «الصفحة» و«النادي»: اقرأ _____ الأولى من الكتاب.',
('ar-a1-u10-p05','q10'):'إذا كنت أريد جوابًا، اختر من «سؤال» و«نهاية»: عندي _____ عن النص.'}
REVAL={'date':'2026-09-05','gate_c_artifact':'reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u10.json','scope':[f'{p} question {q}' for p,q in NEW_PROMPTS],'gate_b_language_recheck':'PASS','reason':'Gate C constrained ten underdetermined A1 cumulative transfer items so the intended always, little, way, different, group, end, moment, picture, page, and question answers are uniquely defensible; replacements were rechecked for A1 MSA wording and Gate B was rebound to exact-current learner-facing content.','release_claim':False}

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def payload(r):
    a={x.get('question_id'):x for x in r.get('answer_key',[])}; notes='\n'.join(r.get('quality',{}).get('notes',[])); hist='naturalness' in notes.lower()
    return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8'))

def finding(pid,qid,idx):
    reasons={
      ('ar-a1-u10-p01','q9'):'The original routine cloze admits عادةً and other frequency expressions. Constrain it to the دائمًا/أحيانًا contrast.',
      ('ar-a1-u10-p01','q10'):'The original remaining-water cloze admits بعض and other quantity expressions. Constrain it to the قليل/كثير contrast.',
      ('ar-a1-u10-p02','q9'):'The original learning-method cloze admits وسيلة and other method nouns. Constrain it to the طريقة/نهاية contrast.',
      ('ar-a1-u10-p02','q10'):'The original route-description cloze admits جديدًا and other adjectives. Constrain it to the مختلفًا/قليلًا contrast.',
      ('ar-a1-u10-p03','q9'):'The original student-group cloze admits فريق and other collective nouns. Constrain it to the مجموعة/نهاية contrast.',
      ('ar-a1-u10-p03','q10'):'The original lesson-time cloze admits آخر and other end expressions. Constrain it to the نهاية/مجموعة contrast.',
      ('ar-a1-u10-p04','q9'):'The original waiting cloze admits دقيقة and other short time units. Add an explicit very-short-time cue and contrast لحظة with صورة.',
      ('ar-a1-u10-p04','q10'):'The original camera cloze admits لقطة and other image nouns. Constrain it to the صورة/صفحة contrast.',
      ('ar-a1-u10-p05','q9'):'The original book-reading cloze admits فقرة and other book-part nouns. Constrain it to the الصفحة/النادي contrast.',
      ('ar-a1-u10-p05','q10'):'The original text-query cloze admits استفسار and other request nouns. Add an answer-seeking cue and contrast سؤال with نهاية.'}
    return {'finding_id':f'{pid}-gC-{idx:02d}','field':f'question {qid}','dimension':'competing_answer_ambiguity','severity':'major','status':'REPAIRED','rationale':reasons[(pid,qid)]}

def build(rows,canon_sha):
    ids=[f'ar-a1-u10-p{i:02d}' for i in range(1,7)]; by={r['id']:r for r in rows}; hs={pid:lh(by[pid]) for pid in ids}
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
    doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'A1','unit':10,'date':'2026-09-05','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/a1/passages.jsonl','canonical_sha256':canon_sha,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'decisions':dec,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; the level SHA records the review-time snapshot.'}
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
        if json.loads(OUT.read_text(encoding='utf-8'))!=doc: raise SystemExit('existing Unit 10 evidence drift')
        verify_gb(json.loads(GATE_B.read_text(encoding='utf-8')),hs)
        print(json.dumps({'unit':10,'idempotent_verification':True,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'release_claim':False},indent=2)); return
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    g=json.loads(GATE_B.read_text(encoding='utf-8')); bd={d['passage_id']:d for d in g['decisions']}
    if set(bd)!=set(OLD_HASHES): raise SystemExit('Gate B Unit 10 scope drift')
    for pid,h in OLD_HASHES.items():
        if bd[pid]['learner_facing_sha256']!=h: raise SystemExit(f'{pid}: Gate B pre-rebind hash drift')
    g['canonical_sha256']=canon
    for pid,h in hs.items(): bd[pid]['learner_facing_sha256']=h
    rv=g.setdefault('post_gate_c_revalidations',[])
    if REVAL in rv: raise SystemExit('duplicate Unit 10 revalidation')
    rv.append(REVAL); GATE_B.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'unit':10,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'canonical_sha256':canon,'release_claim':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
