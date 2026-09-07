#!/usr/bin/env python3
"""Record Arabic Gate C A2 Unit 4 decisions and rebind affected Gate B evidence."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'
CANON=READING/'arabic/a2/passages.jsonl'; OUT=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u04.json'; GATE_B=READING/'audit/arabic_gate_b_decisions_2026-08-30/a2_u04.json'
OLD_HASHES={'ar-a2-u04-p01':'05670a5a41799e767650d5575c4d158f3be5fa307a49f32d8379ad6e484ca804','ar-a2-u04-p02':'e6f4989c03c45d31687dca185a84d0917ddf68cf48df1346ae6ba75218ec52be','ar-a2-u04-p03':'75687e356faaa798ac04e4f798da31c9bd9fc942470c60521f39220f803c3d99','ar-a2-u04-p04':'58d4315213c46e418849e961f8798dfd9d17283eb8e3d223d410829199397c3c','ar-a2-u04-p05':'c0b61c7d9be0d3df546f4858124b131bbf0f0c316af116d68c1fb1625adf32a7','ar-a2-u04-p06':'98a4648aaa3a905b0cf83e33abebf4177d134a38082de102e8138da3b8de9b60'}
NEW_PROMPTS={('ar-a2-u04-p01','q9'):'اختر من «حجم» و«قطع»: أريد صندوقًا ذا _____ أكبر.',('ar-a2-u04-p01','q10'):'اختر من «قطع» و«حجم»: في العلبة عشر _____ من البسكويت.',('ar-a2-u04-p02','q9'):'اختر من «ثمن» و«صفقة»: سألت عن _____ الهاتف قبل شرائه.',('ar-a2-u04-p02','q10'):'اختر من «صفقة» و«ثمن»: اشتريت الكتابين بسعر منخفض؛ كانت _____ جيدة.',('ar-a2-u04-p03','q9'):'اختر من «يستحق» و«يستخدم»: هذا الكتاب مفيد جدًا و_____ ثمنه.',('ar-a2-u04-p03','q10'):'اختر من «تطبيقًا» و«اشتراكًا»: حملت _____ جديدًا لتنظيم وقتي.',('ar-a2-u04-p04','q9'):'اختر من «صالحًا» و«فاسدًا»: هذا الطعام ما زال _____ للأكل.',('ar-a2-u04-p04','q10'):'اختر من «بدل» و«مع»: أخذت كتابًا إلكترونيًا _____ النسخة الورقية.',('ar-a2-u04-p05','q9'):'اختر من «إصلاح» و«صفقة»: يحتاج الهاتف إلى _____ قبل أن أستخدمه مرة أخرى.',('ar-a2-u04-p05','q10'):'اختر من «أسوأ» و«أفضل»: بعد المشكلة ازداد سوءًا؛ أصبح الوضع _____ من قبل.'}
REVAL={'date':'2026-09-06','gate_c_artifact':'reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u04.json','scope':[f'{p} question {q}' for p,q in NEW_PROMPTS],'gate_b_language_recheck':'PASS','reason':'Gate C repaired ten A2 Unit 4 transfer-prompt defects: competing-answer ambiguity across size, pieces, price, deal, app, usable, instead-of, repair, and worse items, plus a malformed worth-it cloze and an unnatural shirt-size context. Keyed answers were preserved, replacements were rechecked for A2 MSA wording, and Gate B was rebound to exact-current learner-facing content.','release_claim':False}
def sha(b):return hashlib.sha256(b).hexdigest()
def payload(r):
 a={x.get('question_id'):x for x in r.get('answer_key',[])}; notes='\n'.join(r.get('quality',{}).get('notes',[])); hist='naturalness' in notes.lower(); return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
META={
 ('ar-a2-u04-p01','q9'):('answer_grounding_and_wording','The original shirt cloze both admitted the natural answer مقاس and made keyed حجم awkward in context. Move the target to the natural phrase صندوقًا ذا حجم أكبر and constrain it against قطع.'),
 ('ar-a2-u04-p01','q10'):('competing_answer_ambiguity','The biscuit-piece cloze admits حبات and similar count nouns. Constrain it to قطع/حجم.'),
 ('ar-a2-u04-p02','q9'):('competing_answer_ambiguity','The phone-price cloze admits سعر. Constrain it to ثمن/صفقة.'),
 ('ar-a2-u04-p02','q10'):('competing_answer_ambiguity','The good-purchase cloze admits several evaluative purchase nouns. Constrain it to صفقة/ثمن.'),
 ('ar-a2-u04-p03','q9'):('assessment_wording','The stem وي_____ combined with keyed يستحق would literally duplicate the initial ي; it also admits other verbs. Remove the prefixed ي and constrain يستحق against يستخدم.'),
 ('ar-a2-u04-p03','q10'):('competing_answer_ambiguity','The downloaded-program cloze admits برنامجًا and similar nouns. Constrain it to تطبيقًا/اشتراكًا.'),
 ('ar-a2-u04-p04','q9'):('competing_answer_ambiguity','The food-usability cloze admits مناسبًا and similar adjectives. Constrain it to صالحًا/فاسدًا.'),
 ('ar-a2-u04-p04','q10'):('competing_answer_ambiguity','The substitution cloze admits مكان and عوض. Constrain it to بدل/مع.'),
 ('ar-a2-u04-p05','q9'):('competing_answer_ambiguity','The phone-service cloze admits صيانة and other repair nouns. Constrain it to إصلاح/صفقة.'),
 ('ar-a2-u04-p05','q10'):('competing_answer_ambiguity','The post-problem comparison admits أصعب and other negative comparatives. Add an explicit worsening cue and constrain it to أسوأ/أفضل.')}
def main():
 raw=CANON.read_bytes(); canon=sha(raw); rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]; ids=[f'ar-a2-u04-p{i:02d}' for i in range(1,7)]; by={r['id']:r for r in rows}; hs={p:lh(by[p]) for p in ids}
 for (p,q),new in NEW_PROMPTS.items():
  if {x['id']:x for x in by[p]['questions']}[q]['prompt']!=new: raise SystemExit(f'{p}/{q}: repaired prompt absent')
 repaired={p for p,_ in NEW_PROMPTS}
 for p in ids:
  if p in repaired and hs[p]==OLD_HASHES[p]: raise SystemExit(f'{p}: hash unchanged')
  if p not in repaired and hs[p]!=OLD_HASHES[p]: raise SystemExit(f'{p}: clean record drift')
 dec=[]
 for p in ids:
  qs=[q for pp,q in NEW_PROMPTS if pp==p]; fs=[]
  for i,q in enumerate(qs,1):
   dim,why=META[(p,q)]; fs.append({'finding_id':f'{p}-gC-{i:02d}','field':f'question {q}','dimension':dim,'severity':'major','status':'REPAIRED','rationale':why})
  dec.append({'passage_id':p,'learner_facing_sha256':hs[p],'decision':'PASS_AFTER_REPAIR' if fs else 'PASS','qa_pairs_reviewed':10,'finding_count':len(fs),'findings':fs})
 doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'A2','unit':4,'date':'2026-09-06','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/a2/passages.jsonl','canonical_sha256':canon,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'decisions':dec,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; the level SHA records the review-time snapshot.'}
 if OUT.exists():
  if json.loads(OUT.read_text())!=doc: raise SystemExit('existing A2 Unit 4 evidence drift')
  g=json.loads(GATE_B.read_text()); bd={d['passage_id']:d for d in g['decisions']}
  if any(bd[p]['learner_facing_sha256']!=hs[p] for p in ids) or g.get('post_gate_c_revalidations',[]).count(REVAL)!=1: raise SystemExit('Gate B idempotent verification failed')
  print('A2 Unit 4 evidence verified idempotently'); return
 OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
 g=json.loads(GATE_B.read_text()); bd={d['passage_id']:d for d in g['decisions']}
 for p,h in OLD_HASHES.items():
  if bd[p]['learner_facing_sha256']!=h: raise SystemExit(f'{p}: Gate B pre-rebind drift')
 g['canonical_sha256']=canon
 for p,h in hs.items(): bd[p]['learner_facing_sha256']=h
 rv=g.setdefault('post_gate_c_revalidations',[])
 if REVAL in rv: raise SystemExit('duplicate revalidation')
 rv.append(REVAL); GATE_B.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'level':'A2','unit':4,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'release_claim':False},indent=2))
if __name__=='__main__':main()
