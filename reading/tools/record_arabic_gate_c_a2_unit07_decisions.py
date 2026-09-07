#!/usr/bin/env python3
"""Record Arabic Gate C A2 Unit 7 decisions and rebind affected Gate B evidence."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];READING=ROOT/'reading';CANON=READING/'arabic/a2/passages.jsonl';OUT=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u07.json';GATE_B=READING/'audit/arabic_gate_b_decisions_2026-08-30/a2_u07.json'
OLD_HASHES={'ar-a2-u07-p01':'5c3cbeab314697af17d54f2388a75ffb634ba3c285d1c86fb5c0780b3f64c39a','ar-a2-u07-p02':'c70a30a796eed986600213a2a3d07146fdaf6038dfa952d3b7490a2e1d94a077','ar-a2-u07-p03':'e11430121fc09b49c1dbdd8b1b13b9cb0bbaf9f6c17551975a2cd51d74b1b397','ar-a2-u07-p04':'90b6015c4ea9ce4f3330f302a39095e935b831c70e84e81915fa62f4b4e6eb02','ar-a2-u07-p05':'248af34dd10a65866f740b60bcf0336f3220e978acc2470e239e4772344db26e','ar-a2-u07-p06':'aa2f8a9b004ceeb373377610d5fe074b2ebbf6f6a08fb805e9b4724d5e9a96db'}
NEW_PROMPTS={('ar-a2-u07-p01','q9'):'اختر من «مناسبة» و«جمهور»: نظم المركز _____ ثقافية يوم الجمعة.',('ar-a2-u07-p01','q10'):'اختر من «الجمهور» و«المناسبة»: صفق _____ بعد انتهاء العرض.',('ar-a2-u07-p02','q9'):'اختر من «الصحافة» و«البيان»: نشرت _____ المحلية خبر افتتاح المركز.',('ar-a2-u07-p02','q10'):'اختر من «بيانًا» و«صحافة»: أصدرت المدرسة _____ عن وقت الإغلاق.',('ar-a2-u07-p03','q9'):'اختر من «تحقيقًا» و«تأثيرًا»: أجرى الفريق _____ لمعرفة سبب المشكلة.',('ar-a2-u07-p03','q10'):'اختر من «تأثير» و«تحقيق»: للطقس _____ على خطة الرحلة.',('ar-a2-u07-p04','q9'):'اختر من «أعلن» و«أظهرت»: _____ النادي موعد الفعالية الجديدة.',('ar-a2-u07-p04','q10'):'اختر من «أظهرت» و«أعلن»: _____ الدراسة أن معظم المشاركين فضلوا الوقت المسائي.',('ar-a2-u07-p05','q9'):'اختر من «رئيسية» و«ثانوية»: كتبت ثلاث أفكار _____ في الملخص.',('ar-a2-u07-p05','q10'):'اختر من «يتوقع» و«يؤكد»: _____ المنظمون، على سبيل التقدير لا التأكيد، حضور عدد كبير إذا كان الطقس مناسبًا.'}
REVAL={'date':'2026-09-07','gate_c_artifact':'reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u07.json','scope':[f'{p} question {q}' for p,q in NEW_PROMPTS],'gate_b_language_recheck':'PASS','reason':'Gate C constrained ten underdetermined A2 Unit 7 community/news transfer items covering occasion, audience, press, statement, inquiry, effect, announcement, observed result, main idea, and forecast; keyed answers were preserved and Gate B was rebound to exact-current learner-facing content.','release_claim':False}
def sha(b):return hashlib.sha256(b).hexdigest()
def payload(r):
 a={x.get('question_id'):x for x in r.get('answer_key',[])};notes='\n'.join(r.get('quality',{}).get('notes',[]));hist='naturalness' in notes.lower();return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
R={('ar-a2-u07-p01','q9'):'The original event cloze admits فعالية and similar event nouns. Constrain it to مناسبة/جمهور.',('ar-a2-u07-p01','q10'):'The original applause cloze admits الحاضرون and الناس. Constrain it to الجمهور/المناسبة.',('ar-a2-u07-p02','q9'):'The original local-news cloze admits الصحيفة and other media nouns. Constrain it to الصحافة/البيان.',('ar-a2-u07-p02','q10'):'The original official-text cloze admits إعلانًا and similar nouns. Constrain it to بيانًا/صحافة.',('ar-a2-u07-p03','q9'):'The original inquiry cloze admits بحثًا and دراسة. Constrain it to تحقيقًا/تأثيرًا.',('ar-a2-u07-p03','q10'):'The original weather-effect cloze admits أثر. Constrain it to تأثير/تحقيق.',('ar-a2-u07-p04','q9'):'The original announcement cloze admits حدد and ذكر. Constrain it to أعلن/أظهرت.',('ar-a2-u07-p04','q10'):'The original study-result cloze admits بينت and كشفت. Constrain it to أظهرت/أعلن.',('ar-a2-u07-p05','q9'):'The original main-ideas cloze admits مهمة and أساسية. Constrain it to رئيسية/ثانوية.',('ar-a2-u07-p05','q10'):'The original forecast cloze admits other expectation verbs. Add a non-confirmation cue and constrain it to يتوقع/يؤكد.'}
def main():
 raw=CANON.read_bytes();canon=sha(raw);rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()];ids=[f'ar-a2-u07-p{i:02d}' for i in range(1,7)];by={r['id']:r for r in rows};hs={p:lh(by[p]) for p in ids}
 for (p,q),new in NEW_PROMPTS.items():
  if {x['id']:x for x in by[p]['questions']}[q]['prompt']!=new:raise SystemExit(f'{p}/{q}: repaired prompt absent')
 repaired={p for p,_ in NEW_PROMPTS}
 for p in ids:
  if p in repaired and hs[p]==OLD_HASHES[p]:raise SystemExit(f'{p}: hash unchanged')
  if p not in repaired and hs[p]!=OLD_HASHES[p]:raise SystemExit(f'{p}: clean record drift')
 dec=[]
 for p in ids:
  qs=[q for pp,q in NEW_PROMPTS if pp==p];fs=[{'finding_id':f'{p}-gC-{i:02d}','field':f'question {q}','dimension':'competing_answer_ambiguity','severity':'major','status':'REPAIRED','rationale':R[(p,q)]} for i,q in enumerate(qs,1)];dec.append({'passage_id':p,'learner_facing_sha256':hs[p],'decision':'PASS_AFTER_REPAIR' if fs else 'PASS','qa_pairs_reviewed':10,'finding_count':len(fs),'findings':fs})
 doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'A2','unit':7,'date':'2026-09-07','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/a2/passages.jsonl','canonical_sha256':canon,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'decisions':dec,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; the level SHA records the review-time snapshot.'}
 if OUT.exists():
  if json.loads(OUT.read_text())!=doc:raise SystemExit('existing A2 Unit 7 evidence drift')
  g=json.loads(GATE_B.read_text());bd={d['passage_id']:d for d in g['decisions']}
  if any(bd[p]['learner_facing_sha256']!=hs[p] for p in ids) or g.get('post_gate_c_revalidations',[]).count(REVAL)!=1:raise SystemExit('Gate B idempotent verification failed')
  print('A2 Unit 7 evidence verified idempotently');return
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
 g=json.loads(GATE_B.read_text());bd={d['passage_id']:d for d in g['decisions']}
 for p,h in OLD_HASHES.items():
  if bd[p]['learner_facing_sha256']!=h:raise SystemExit(f'{p}: Gate B pre-rebind drift')
 g['canonical_sha256']=canon
 for p,h in hs.items():bd[p]['learner_facing_sha256']=h
 rv=g.setdefault('post_gate_c_revalidations',[])
 if REVAL in rv:raise SystemExit('duplicate revalidation')
 rv.append(REVAL);GATE_B.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'level':'A2','unit':7,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'release_claim':False},indent=2))
if __name__=='__main__':main()
