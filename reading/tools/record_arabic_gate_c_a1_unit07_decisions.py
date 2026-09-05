#!/usr/bin/env python3
"""Record Arabic Gate C A1 Unit 7 decisions and rebind affected Gate B evidence."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
CANON=READING/'arabic/a1/passages.jsonl'
OUT=READING/'audit/arabic_gate_c_decisions_2026-09-05/a1_u07.json'
GATE_B=READING/'audit/arabic_gate_b_decisions_2026-08-30/a1_u07.json'
OLD_HASHES={
'ar-a1-u07-p01':'9e5f6dfda4407514315ac7f2cc85c5259393caca53c0f0e58d88159ae2a22d14',
'ar-a1-u07-p02':'0018e786b4a6cd431bdcabfe3d08897a08aaffe0fc82e1d6ea49a70b4e8b838b',
'ar-a1-u07-p03':'c476e320e30c9e01838a9b9f875e2d37842168bb8f390b423a1a1897adf206d8',
'ar-a1-u07-p04':'e92a22933f9f6cc24c41971409e8935cd022f09e501ccf90cddfda472caca452',
'ar-a1-u07-p05':'63021348615578e41f6695e7ac66a86cf6f064a6b4aca1257361ef5b5a6462f0',
'ar-a1-u07-p06':'46f85a2b35eee7075e15e884da93feed6d53d5a0f67e59e396910d67170fe45e'}
NEW_PROMPTS={
('ar-a1-u07-p01','q9'):'اختر من «السماء» و«الموسم»: في _____ غيوم كثيرة اليوم.',
('ar-a1-u07-p01','q10'):'اختر من «موسم» و«صباح»: الشتاء _____ بارد في بلاد كثيرة.',
('ar-a1-u07-p02','q9'):'اختر من «درجة» و«موسم»: الحرارة اليوم عشرون _____.',
('ar-a1-u07-p02','q10'):'اختر من «يبدو» و«يجب»: من الغيوم _____ أن المطر قريب.',
('ar-a1-u07-p03','q9'):'اختر من «القادم» و«الماضي»: في الأسبوع _____ عندنا نشاط جديد.',
('ar-a1-u07-p03','q10'):'اختر من «ربما» و«يجب»: _____ أزور صديقي مساءً إذا انتهيت مبكرًا.',
('ar-a1-u07-p04','q10'):'إذا كانت المدة من الاثنين إلى الأربعاء، أكمل: بقيت هناك ثلاثة _____.',
('ar-a1-u07-p05','q9'):'إذا بقيت ستين دقيقة، أكمل: بقيت في المكتبة _____ واحدة.',
('ar-a1-u07-p05','q10'):'اختر من «الأسبوع» و«الساعة»: في هذا _____ عندنا خمسة أيام مدرسة.'}
REVAL={'date':'2026-09-05','gate_c_artifact':'reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u07.json','scope':[f'{p} question {q}' for p,q in NEW_PROMPTS],'gate_b_language_recheck':'PASS','reason':'Gate C constrained nine underdetermined weather/time transfer items across A1 Unit 7 so the intended sky, season, temperature, seeming, coming, possibility, days, hour, and week answers are uniquely defensible; replacements were rechecked for A1 MSA wording and Gate B was rebound to exact-current learner-facing content.','release_claim':False}

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def payload(r):
    a={x.get('question_id'):x for x in r.get('answer_key',[])}
    notes='\n'.join(r.get('quality',{}).get('notes',[])); hist='naturalness' in notes.lower()
    return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8'))

def finding(pid,qid,idx):
    reasons={
      ('ar-a1-u07-p01','q9'):'The original weather cloze allowed multiple location nouns such as الجو. Constrain it to the reviewed السماء/الموسم contrast.',
      ('ar-a1-u07-p01','q10'):'The original winter cloze allowed other period nouns such as فصل. Constrain it to a simple موسم/صباح choice.',
      ('ar-a1-u07-p02','q9'):'The original temperature cloze did not explicitly identify the measurement unit. Constrain it to the reviewed درجة/موسم contrast.',
      ('ar-a1-u07-p02','q10'):'The original inference cloze admits other verbs such as يظهر. Constrain it to the يبدو/يجب contrast.',
      ('ar-a1-u07-p03','q9'):'The original future-week cloze allows القادم, المقبل, and التالي. Constrain it to the القادم/الماضي contrast.',
      ('ar-a1-u07-p03','q10'):'The original possibility cloze also admits قد. Constrain it to the reviewed ربما/يجب contrast.',
      ('ar-a1-u07-p04','q10'):'The original duration cloze allows many time units. Supply a Monday-to-Wednesday interval so أيام is uniquely grounded.',
      ('ar-a1-u07-p05','q9'):'The original duration cloze allows several feminine time units. Specify sixty minutes so ساعة is uniquely grounded.',
      ('ar-a1-u07-p05','q10'):'The original school-days cloze can plausibly take الشهر. Constrain it to the الأسبوع/الساعة contrast.'}
    return {'finding_id':f'{pid}-gC-{idx:02d}','field':f'question {qid}','dimension':'competing_answer_ambiguity','severity':'major','status':'REPAIRED','rationale':reasons[(pid,qid)]}

def build(rows,canon_sha):
    ids=[f'ar-a1-u07-p{i:02d}' for i in range(1,7)]; by={r['id']:r for r in rows}; hs={pid:lh(by[pid]) for pid in ids}
    for (pid,qid),new in NEW_PROMPTS.items():
        if {x['id']:x for x in by[pid]['questions']}[qid]['prompt']!=new: raise SystemExit(f'{pid}/{qid}: repaired prompt absent')
    repaired={p for p,_ in NEW_PROMPTS}
    for pid in ids:
        if pid in repaired:
            if hs[pid]==OLD_HASHES[pid]: raise SystemExit(f'{pid}: learner hash did not change')
        elif hs[pid]!=OLD_HASHES[pid]: raise SystemExit(f'{pid}: unexpected learner-facing drift')
    by_findings={pid:[] for pid in ids}
    for pid in ids:
        qs=[qid for p,qid in NEW_PROMPTS if p==pid]
        for idx,qid in enumerate(qs,1): by_findings[pid].append(finding(pid,qid,idx))
    dec=[]
    for pid in ids:
        fs=by_findings[pid]
        dec.append({'passage_id':pid,'learner_facing_sha256':hs[pid],'decision':'PASS_AFTER_REPAIR' if fs else 'PASS','qa_pairs_reviewed':10,'finding_count':len(fs),'findings':fs})
    doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'A1','unit':7,'date':'2026-09-05','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/a1/passages.jsonl','canonical_sha256':canon_sha,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':9,'decisions':dec,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; the level SHA records the review-time snapshot.'}
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
        if json.loads(OUT.read_text(encoding='utf-8'))!=doc: raise SystemExit('existing Unit 7 evidence drift')
        verify_gb(json.loads(GATE_B.read_text(encoding='utf-8')),hs)
        print(json.dumps({'unit':7,'idempotent_verification':True,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':9,'release_claim':False},indent=2)); return
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    g=json.loads(GATE_B.read_text(encoding='utf-8')); bd={d['passage_id']:d for d in g['decisions']}
    if set(bd)!=set(OLD_HASHES): raise SystemExit('Gate B Unit 7 scope drift')
    for pid,h in OLD_HASHES.items():
        if bd[pid]['learner_facing_sha256']!=h: raise SystemExit(f'{pid}: Gate B pre-rebind hash drift')
    g['canonical_sha256']=canon
    for pid,h in hs.items(): bd[pid]['learner_facing_sha256']=h
    rv=g.setdefault('post_gate_c_revalidations',[])
    if REVAL in rv: raise SystemExit('duplicate Unit 7 revalidation')
    rv.append(REVAL); GATE_B.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'unit':7,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':9,'canonical_sha256':canon,'release_claim':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
