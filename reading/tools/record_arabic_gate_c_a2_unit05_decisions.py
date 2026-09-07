#!/usr/bin/env python3
"""Record Arabic Gate C A2 Unit 5 decisions and rebind affected Gate B evidence."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'
CANON=READING/'arabic/a2/passages.jsonl'; OUT=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u05.json'; GATE_B=READING/'audit/arabic_gate_b_decisions_2026-08-30/a2_u05.json'
OLD_HASHES={'ar-a2-u05-p01':'00319daf7d0092d6a9af571d7d45d31da14c6d232072e4d01e3d9c239c3ab415','ar-a2-u05-p02':'2e1310627048a8730557b5bc70d2051fd4c7d44511a69eeae08c00d3b4193b39','ar-a2-u05-p03':'a47e96895b358e66aa678cac1cfd109f5430ee3570d195356962ceef9f14600b','ar-a2-u05-p04':'e773a4b6012b83083367a81cf979ca387348abdded338fcd17037e29f62e0519','ar-a2-u05-p05':'30d8e9380082c04ae067e132d47913bcb6b171f2f2ea8408ecd9fb44431296c9','ar-a2-u05-p06':'a5dbc9b2447d8321c81eb51c7828a788fe974bbfb68e0ee4bb0c7f370b6f935e'}
NEW_PROMPTS={('ar-a2-u05-p01','q9'):'اختر من «تصوير» و«مسابقة»: أحب _____ الأماكن القديمة في المدينة.',('ar-a2-u05-p01','q10'):'اختر من «مسابقة» و«تصوير»: شاركت المدرسة في _____ للقراءة.',('ar-a2-u05-p02','q9'):'اختر من «تفكير» و«تصوير»: يحتاج هذا القرار إلى _____ قبل أن أختار.',('ar-a2-u05-p02','q10'):'اختر من «متابعة» و«مسابقة»: بعد الموعد نحتاج إلى _____ النتيجة الأسبوع القادم.',('ar-a2-u05-p03','q9'):'اختر من «خطوة» و«مشاريع»: أول _____ في الخطة هي اختيار الموضوع.',('ar-a2-u05-p03','q10'):'اختر من «مشاريع» و«مشروع»: يعمل الطلاب على عدة _____ علمية صغيرة.',('ar-a2-u05-p04','q9'):'اختر من «عادة» و«مسابقة»: المشي بعد العشاء أصبح _____ يومية عندي.',('ar-a2-u05-p04','q10'):'اختر من «يتعرف» و«ينسى»: بدأ الطفل _____ إلى زملائه الجدد.',('ar-a2-u05-p05','q9'):'اختر من «تدريب» و«مسابقة»: يحتاج العزف الجيد إلى _____ منتظم.',('ar-a2-u05-p05','q10'):'اختر من «خبرة» و«خطوة»: لديه _____ طويلة في العمل مع الأطفال.'}
REVAL={'date':'2026-09-06','gate_c_artifact':'reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u05.json','scope':[f'{p} question {q}' for p,q in NEW_PROMPTS],'gate_b_language_recheck':'PASS','reason':'Gate C constrained ten underdetermined A2 Unit 5 learning-process transfer items so the intended photography, contest, thinking, follow-up, step, projects, habit, get-to-know, training, and experience answers are uniquely defensible; replacements were rechecked for A2 MSA wording and Gate B was rebound to exact-current learner-facing content.','release_claim':False}
def sha(b):return hashlib.sha256(b).hexdigest()
def payload(r):
 a={x.get('question_id'):x for x in r.get('answer_key',[])}; notes='\n'.join(r.get('quality',{}).get('notes',[])); hist='naturalness' in notes.lower(); return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
REASONS={
 ('ar-a2-u05-p01','q9'):'The original photography cloze admits زيارة and other activities. Constrain it to تصوير/مسابقة.',('ar-a2-u05-p01','q10'):'The original school-reading event cloze admits فعالية and نشاط. Constrain it to مسابقة/تصوير.',('ar-a2-u05-p02','q9'):'The original decision-reflection cloze admits دراسة and تأنٍ. Constrain it to تفكير/تصوير.',('ar-a2-u05-p02','q10'):'The original follow-up cloze admits مراجعة and فحص. Constrain it to متابعة/مسابقة.',('ar-a2-u05-p03','q9'):'The original first-stage cloze admits مرحلة. Constrain it to خطوة/مشاريع.',('ar-a2-u05-p03','q10'):'The original science-project cloze can take singular or other work nouns. Add عدة and constrain it to مشاريع/مشروع.',('ar-a2-u05-p04','q9'):'The original daily-habit cloze admits ممارسة and رياضة. Constrain it to عادة/مسابقة.',('ar-a2-u05-p04','q10'):'The original getting-acquainted cloze admits يتقرب and similar verbs. Constrain it to يتعرف/ينسى while preserving the complete-word cloze.',('ar-a2-u05-p05','q9'):'The original regular-practice cloze admits تمرين. Constrain it to تدريب/مسابقة.',('ar-a2-u05-p05','q10'):'The original work-experience cloze admits تجربة in some readings. Constrain it to خبرة/خطوة.'}
def main():
 raw=CANON.read_bytes(); canon=sha(raw); rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]; ids=[f'ar-a2-u05-p{i:02d}' for i in range(1,7)]; by={r['id']:r for r in rows}; hs={p:lh(by[p]) for p in ids}
 for (p,q),new in NEW_PROMPTS.items():
  if {x['id']:x for x in by[p]['questions']}[q]['prompt']!=new: raise SystemExit(f'{p}/{q}: repaired prompt absent')
 repaired={p for p,_ in NEW_PROMPTS}
 for p in ids:
  if p in repaired and hs[p]==OLD_HASHES[p]: raise SystemExit(f'{p}: hash unchanged')
  if p not in repaired and hs[p]!=OLD_HASHES[p]: raise SystemExit(f'{p}: clean record drift')
 dec=[]
 for p in ids:
  qs=[q for pp,q in NEW_PROMPTS if pp==p]; fs=[{'finding_id':f'{p}-gC-{i:02d}','field':f'question {q}','dimension':'competing_answer_ambiguity','severity':'major','status':'REPAIRED','rationale':REASONS[(p,q)]} for i,q in enumerate(qs,1)]; dec.append({'passage_id':p,'learner_facing_sha256':hs[p],'decision':'PASS_AFTER_REPAIR' if fs else 'PASS','qa_pairs_reviewed':10,'finding_count':len(fs),'findings':fs})
 doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'A2','unit':5,'date':'2026-09-06','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/a2/passages.jsonl','canonical_sha256':canon,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'decisions':dec,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; the level SHA records the review-time snapshot.'}
 if OUT.exists():
  if json.loads(OUT.read_text())!=doc: raise SystemExit('existing A2 Unit 5 evidence drift')
  g=json.loads(GATE_B.read_text()); bd={d['passage_id']:d for d in g['decisions']}
  if any(bd[p]['learner_facing_sha256']!=hs[p] for p in ids) or g.get('post_gate_c_revalidations',[]).count(REVAL)!=1: raise SystemExit('Gate B idempotent verification failed')
  print('A2 Unit 5 evidence verified idempotently'); return
 OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
 g=json.loads(GATE_B.read_text()); bd={d['passage_id']:d for d in g['decisions']}
 for p,h in OLD_HASHES.items():
  if bd[p]['learner_facing_sha256']!=h: raise SystemExit(f'{p}: Gate B pre-rebind drift')
 g['canonical_sha256']=canon
 for p,h in hs.items(): bd[p]['learner_facing_sha256']=h
 rv=g.setdefault('post_gate_c_revalidations',[])
 if REVAL in rv: raise SystemExit('duplicate revalidation')
 rv.append(REVAL); GATE_B.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'level':'A2','unit':5,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'release_claim':False},indent=2))
if __name__=='__main__':main()
