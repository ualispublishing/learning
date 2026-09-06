#!/usr/bin/env python3
"""Record Arabic Gate C A1 Unit 9 decisions and rebind affected Gate B evidence."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
CANON=READING/'arabic/a1/passages.jsonl'
OUT=READING/'audit/arabic_gate_c_decisions_2026-09-05/a1_u09.json'
GATE_B=READING/'audit/arabic_gate_b_decisions_2026-08-30/a1_u09.json'
OLD_HASHES={
'ar-a1-u09-p01':'4335ca0e480027ddd8a68b127e55a6293a43a0db7c375cbad826b60ebaaaa9e6',
'ar-a1-u09-p02':'3ca192ced46a6ab9bc36e32edc14233fb85c7a7bb2b48db5dffd95931625a60b',
'ar-a1-u09-p03':'a5d59239d40f551545e702ffceb73ca45766807cc27e09f0f5e576a3e64c3b9f',
'ar-a1-u09-p04':'fd6b7b0d0d7fd880018c3cbec003c2948c02aef8fde6d4841b617182ea855079',
'ar-a1-u09-p05':'8ba35c3a4f28fde518ff37693830e39eaaece6e3a378047c69be9540bfb11a96',
'ar-a1-u09-p06':'327848cf5df58294e2c1896fc4bd67fb284b5d9b69e6403bea8c9d48626489ec'}
NEW_PROMPTS={
('ar-a1-u09-p01','q9'):'اختر من «الكرة» و«اللاعب»: رميت _____ إلى صديقي.',
('ar-a1-u09-p01','q10'):'اختر من «لاعب» و«كرة»: سامر _____ في الفريق.',
('ar-a1-u09-p02','q9'):'اختر من «مباراة» و«نادي»: شاهدنا _____ كرة في المساء.',
('ar-a1-u09-p02','q10'):'اختر من «نادي» و«مباراة»: أذهب إلى _____ القراءة يوم الخميس.',
('ar-a1-u09-p03','q9'):'اختر من «أصدقائي» و«المباراة»: ألعب مع _____ بعد المدرسة.',
('ar-a1-u09-p03','q10'):'اختر من «سعيد» و«بعيد»: أنا _____ لأن صديقي جاء.',
('ar-a1-u09-p04','q9'):'اختر من «فرصة» و«مشاركة»: عندي _____ لزيارة المكتبة اليوم.',
('ar-a1-u09-p04','q10'):'اختر من «المشاركة» و«الفرصة»: أحب _____ في أنشطة الصف.',
('ar-a1-u09-p05','q9'):'اختر من «هدفًا» و«فوزًا»: سجل الفريق _____ في الشوط الأول.',
('ar-a1-u09-p05','q10'):'اختر من «فوز» و«فرصة»: انتهت المباراة ب_____ فريقنا.'}
REVAL={'date':'2026-09-05','gate_c_artifact':'reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u09.json','scope':[f'{p} question {q}' for p,q in NEW_PROMPTS],'gate_b_language_recheck':'PASS','reason':'Gate C constrained ten underdetermined leisure transfer items across A1 Unit 9 so the intended ball, player, match, club, friends, happy, opportunity, participation, goal, and win answers are uniquely defensible; replacements were rechecked for A1 MSA wording and Gate B was rebound to exact-current learner-facing content.','release_claim':False}

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def payload(r):
    a={x.get('question_id'):x for x in r.get('answer_key',[])}; notes='\n'.join(r.get('quality',{}).get('notes',[])); hist='naturalness' in notes.lower()
    return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8'))

def finding(pid,qid,idx):
    reasons={
      ('ar-a1-u09-p01','q9'):'The original throwing cloze can take several thrown objects. Constrain it to the reviewed الكرة/اللاعب contrast.',
      ('ar-a1-u09-p01','q10'):'The original team-role cloze admits عضو, حارس, مهاجم and other roles. Constrain it to the لاعب/كرة contrast.',
      ('ar-a1-u09-p02','q9'):'The original viewing cloze can take لعبة and other event nouns. Constrain it to the مباراة/نادي contrast.',
      ('ar-a1-u09-p02','q10'):'The original reading-place cloze can take حلقة, مجموعة and other nouns. Constrain it to the نادي/مباراة contrast.',
      ('ar-a1-u09-p03','q9'):'The original play-with cloze admits many people or groups. Constrain it to the أصدقائي/المباراة contrast.',
      ('ar-a1-u09-p03','q10'):'The original positive-feeling cloze admits مسرور and other adjectives. Constrain it to the سعيد/بعيد contrast.',
      ('ar-a1-u09-p04','q9'):'The original library-visit cloze admits وقت and other opportunity nouns. Constrain it to the فرصة/مشاركة contrast.',
      ('ar-a1-u09-p04','q10'):'The original classroom-activity cloze admits الانضمام and other participation expressions. Constrain it to the المشاركة/الفرصة contrast.',
      ('ar-a1-u09-p05','q9'):'The original scoring cloze admits points or multiple-score expressions. Constrain it to the هدفًا/فوزًا contrast.',
      ('ar-a1-u09-p05','q10'):'The original match-result cloze admits تعادل, تقدم and other results. Constrain it to the فوز/فرصة contrast.'}
    return {'finding_id':f'{pid}-gC-{idx:02d}','field':f'question {qid}','dimension':'competing_answer_ambiguity','severity':'major','status':'REPAIRED','rationale':reasons[(pid,qid)]}

def build(rows,canon_sha):
    ids=[f'ar-a1-u09-p{i:02d}' for i in range(1,7)]; by={r['id']:r for r in rows}; hs={pid:lh(by[pid]) for pid in ids}
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
    doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'A1','unit':9,'date':'2026-09-05','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/a1/passages.jsonl','canonical_sha256':canon_sha,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'decisions':dec,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; the level SHA records the review-time snapshot.'}
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
        if json.loads(OUT.read_text(encoding='utf-8'))!=doc: raise SystemExit('existing Unit 9 evidence drift')
        verify_gb(json.loads(GATE_B.read_text(encoding='utf-8')),hs)
        print(json.dumps({'unit':9,'idempotent_verification':True,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'release_claim':False},indent=2)); return
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    g=json.loads(GATE_B.read_text(encoding='utf-8')); bd={d['passage_id']:d for d in g['decisions']}
    if set(bd)!=set(OLD_HASHES): raise SystemExit('Gate B Unit 9 scope drift')
    for pid,h in OLD_HASHES.items():
        if bd[pid]['learner_facing_sha256']!=h: raise SystemExit(f'{pid}: Gate B pre-rebind hash drift')
    g['canonical_sha256']=canon
    for pid,h in hs.items(): bd[pid]['learner_facing_sha256']=h
    rv=g.setdefault('post_gate_c_revalidations',[])
    if REVAL in rv: raise SystemExit('duplicate Unit 9 revalidation')
    rv.append(REVAL); GATE_B.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'unit':9,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'canonical_sha256':canon,'release_claim':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
