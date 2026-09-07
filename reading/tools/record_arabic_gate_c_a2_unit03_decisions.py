#!/usr/bin/env python3
"""Record Arabic Gate C A2 Unit 3 decisions and rebind affected Gate B evidence."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'
CANON=READING/'arabic/a2/passages.jsonl'; OUT=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u03.json'; GATE_B=READING/'audit/arabic_gate_b_decisions_2026-08-30/a2_u03.json'
OLD_HASHES={'ar-a2-u03-p01':'f6f1080b83c8d9a386879f3b8958fb450852b20ac8a0e76491e7430c6f8a1ade','ar-a2-u03-p02':'c411d2f5eea91e6a5f9a3207f1a814368f8efbe84c893e60b8c03e897f29b691','ar-a2-u03-p03':'cb242eab4a7ea35a08752a11727e74ee3a1a7e9f031dae60e707341ebddd9ade','ar-a2-u03-p04':'59ced338c2e94ffd148b6dc1eb39eef2266602044adc1cd1df0fa7e0031d58d8','ar-a2-u03-p05':'3eff5d85dd17af66ac414b1655de6499cd1694e634bb8b76bdeec5671665a258','ar-a2-u03-p06':'988d470197f3f9cbb15f324bd8e4c0e2e70f4e4d83ce102c8f86716fb2f93a7e'}
NEW_PROMPTS={('ar-a2-u03-p01','q9'):'اختر من «مؤخرًا» و«مجددًا»: زرت هذا المكان _____، أي قبل أيام قليلة.',('ar-a2-u03-p01','q10'):'اختر من «مجددا» و«مؤخرا»: لم أفهم الجملة، فقرأتها _____.',('ar-a2-u03-p02','q9'):'اختر من «تسجيل» و«نظرة»: استمعت إلى _____ للمحاضرة بعد العودة إلى البيت.',('ar-a2-u03-p02','q10'):'اختر من «نظرة» و«تسجيل»: ألقيت _____ على الخريطة قبل الخروج.',('ar-a2-u03-p03','q9'):'اختر من «حفل» و«زمن»: حضرنا _____ تخرج أخي العام الماضي.',('ar-a2-u03-p03','q10'):'اختر من «الزمن» و«الحفل»: تغير الحي كثيرًا مع مرور _____.',('ar-a2-u03-p04','q9'):'اختر من «معظم» و«جميع»: حضر _____ الطلاب إلى النشاط، لكن بعضهم غاب.',('ar-a2-u03-p04','q10'):'اختر من «ظننت» و«علمت»: _____ أن المتجر مفتوح، لكنه كان مغلقًا.',('ar-a2-u03-p05','q9'):'اختر من «أثرًا» و«فوزًا»: تركت الرحلة _____ جميلًا في ذاكرتي.',('ar-a2-u03-p05','q10'):'اختر من «فاز» و«خسر»: _____ فريقنا في المباراة الأخيرة.'}
REVAL={'date':'2026-09-06','gate_c_artifact':'reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u03.json','scope':[f'{p} question {q}' for p,q in NEW_PROMPTS],'gate_b_language_recheck':'PASS','reason':'Gate C constrained ten underdetermined A2 Unit 3 memory-transfer items so the intended recently, again, recording, look, ceremony, time, most, thought, effect, and won answers are uniquely defensible; replacements were rechecked for A2 MSA wording and Gate B was rebound to exact-current learner-facing content.','release_claim':False}
def sha(b):return hashlib.sha256(b).hexdigest()
def payload(r):
 a={x.get('question_id'):x for x in r.get('answer_key',[])}; notes='\n'.join(r.get('quality',{}).get('notes',[])); hist='naturalness' in notes.lower(); return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def reason(pid,qid):
 return {('ar-a2-u03-p01','q9'):'The original recent-time cloze admits حديثًا and similar recent-time expressions. Constrain it to مؤخرًا/مجددًا.',('ar-a2-u03-p01','q10'):'The original rereading cloze admits ثانية and مرة أخرى. Constrain it to مجددا/مؤخرا.',('ar-a2-u03-p02','q9'):'The original lecture-audio cloze admits تسجيلًا صوتيًا and ملفًا. Constrain it to تسجيل/نظرة.',('ar-a2-u03-p02','q10'):'The original map-glance cloze admits نظرة سريعة and similar phrases. Constrain it to نظرة/تسجيل.',('ar-a2-u03-p03','q9'):'The original graduation-event cloze admits حفلة and مناسبة. Constrain it to حفل/زمن.',('ar-a2-u03-p03','q10'):'The original passage-of-time cloze admits الوقت and السنوات. Constrain it to الزمن/الحفل.',('ar-a2-u03-p04','q9'):'The original majority cloze admits أغلب. Constrain it to معظم/جميع.',('ar-a2-u03-p04','q10'):'The original mistaken-belief cloze admits اعتقدت and حسبت. Constrain it to ظننت/علمت.',('ar-a2-u03-p05','q9'):'The original lasting-impression cloze admits تأثيرًا and similar nouns. Constrain it to أثرًا/فوزًا.',('ar-a2-u03-p05','q10'):'The original match-result cloze admits انتصر. Constrain it to فاز/خسر.'}[(pid,qid)]
def main():
 raw=CANON.read_bytes(); canon=sha(raw); rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]; ids=[f'ar-a2-u03-p{i:02d}' for i in range(1,7)]; by={r['id']:r for r in rows}; hs={p:lh(by[p]) for p in ids}
 for (p,q),new in NEW_PROMPTS.items():
  if {x['id']:x for x in by[p]['questions']}[q]['prompt']!=new: raise SystemExit(f'{p}/{q}: repaired prompt absent')
 repaired={p for p,_ in NEW_PROMPTS}
 for p in ids:
  if p in repaired and hs[p]==OLD_HASHES[p]: raise SystemExit(f'{p}: hash unchanged')
  if p not in repaired and hs[p]!=OLD_HASHES[p]: raise SystemExit(f'{p}: clean record drift')
 dec=[]
 for p in ids:
  qs=[q for pp,q in NEW_PROMPTS if pp==p]; fs=[{'finding_id':f'{p}-gC-{i:02d}','field':f'question {q}','dimension':'competing_answer_ambiguity','severity':'major','status':'REPAIRED','rationale':reason(p,q)} for i,q in enumerate(qs,1)]; dec.append({'passage_id':p,'learner_facing_sha256':hs[p],'decision':'PASS_AFTER_REPAIR' if fs else 'PASS','qa_pairs_reviewed':10,'finding_count':len(fs),'findings':fs})
 doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'A2','unit':3,'date':'2026-09-06','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/a2/passages.jsonl','canonical_sha256':canon,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'decisions':dec,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; the level SHA records the review-time snapshot.'}
 if OUT.exists():
  if json.loads(OUT.read_text())!=doc: raise SystemExit('existing A2 Unit 3 evidence drift')
  g=json.loads(GATE_B.read_text()); bd={d['passage_id']:d for d in g['decisions']}
  if any(bd[p]['learner_facing_sha256']!=hs[p] for p in ids) or g.get('post_gate_c_revalidations',[]).count(REVAL)!=1: raise SystemExit('Gate B idempotent verification failed')
  print('A2 Unit 3 evidence verified idempotently'); return
 OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
 g=json.loads(GATE_B.read_text()); bd={d['passage_id']:d for d in g['decisions']}
 for p,h in OLD_HASHES.items():
  if bd[p]['learner_facing_sha256']!=h: raise SystemExit(f'{p}: Gate B pre-rebind drift')
 g['canonical_sha256']=canon
 for p,h in hs.items(): bd[p]['learner_facing_sha256']=h
 rv=g.setdefault('post_gate_c_revalidations',[])
 if REVAL in rv: raise SystemExit('duplicate revalidation')
 rv.append(REVAL); GATE_B.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'level':'A2','unit':3,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'release_claim':False},indent=2))
if __name__=='__main__':main()
