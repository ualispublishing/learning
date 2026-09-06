#!/usr/bin/env python3
"""Record Arabic Gate C A2 Unit 2 decisions and rebind affected Gate B evidence."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'
CANON=READING/'arabic/a2/passages.jsonl'; OUT=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u02.json'; GATE_B=READING/'audit/arabic_gate_b_decisions_2026-08-30/a2_u02.json'
OLD_HASHES={'ar-a2-u02-p01':'f0ddd08048992da6aa1cae9d38fb7fbc757e9890ec0ea0574318e95f1fa25ab5','ar-a2-u02-p02':'8efd49493d72329080fa5cec08c82e8da17f19830932d6de9bf08959b55f2411','ar-a2-u02-p03':'376948ee333a7d7854ad501f0b37c91edd8762c21836504c43f86be70278c278','ar-a2-u02-p04':'48a890d56c9a0e928b1757d0ba2bcc833f8ba95f065bb04be09dd853902431b3','ar-a2-u02-p05':'5bda48414cb4b98289aa21bb1e687b37545a5dd3193910807d7bb6e9f111e232','ar-a2-u02-p06':'6c6358339134caa48f7f5b56c4375e5dbc1b3e90ba49b7bc2961e0771dfb16dc'}
NEW_PROMPTS={('ar-a2-u02-p01','q9'):'اختر من «موعد» و«رد»: عندي _____ مع طبيب الأسنان في العاشرة.',('ar-a2-u02-p01','q10'):'اختر من «رده» و«موعده»: أرسلت رسالة إلى صديقي وانتظرت _____.',('ar-a2-u02-p02','q9'):'اختر من «متأكدًا» و«بعيدًا»: لست _____ من رقم القاعة؛ سأتحقق منه.',('ar-a2-u02-p02','q10'):'اختر من «التالي» و«السابق»: انتهى هذا الدرس، والدرس _____ يبدأ بعد عشر دقائق.',('ar-a2-u02-p03','q9'):'اختر من «اتصلت» و«انتظرت»: عندما تغير الموعد _____ بصديقي لأخبره.',('ar-a2-u02-p03','q10'):'اختر من «لاحق» و«سابق»: لا أستطيع الآن؛ سأتحدث معك في وقت _____.',('ar-a2-u02-p04','q9'):'اختر من «اختيار» و«موعد»: عندي أكثر من _____ للوصول إلى الجامعة.',('ar-a2-u02-p04','q10'):'اختر من «الحالي» و«التالي»: عنواني _____ مختلف عن عنواني القديم.',('ar-a2-u02-p05','q9'):'اختر من «دورة» و«زيارة»: سجلت في _____ قصيرة لتعلم التصوير.',('ar-a2-u02-p05','q10'):'اختر من «تنظيم» و«سعر»: يحتاج السفر إلى _____ جيد للوقت والحجوزات.'}
REVAL={'date':'2026-09-06','gate_c_artifact':'reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u02.json','scope':[f'{p} question {q}' for p,q in NEW_PROMPTS],'gate_b_language_recheck':'PASS','reason':'Gate C constrained ten underdetermined A2 Unit 2 scheduling-transfer items so the intended appointment, reply, certain, next, called, later, choice, current, course, and organization answers are uniquely defensible; replacements were rechecked for A2 MSA wording and Gate B was rebound to exact-current learner-facing content.','release_claim':False}
def sha(b):return hashlib.sha256(b).hexdigest()
def payload(r):
 a={x.get('question_id'):x for x in r.get('answer_key',[])}; notes='\n'.join(r.get('quality',{}).get('notes',[])); hist='naturalness' in notes.lower(); return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def reason(pid,qid):
 return {('ar-a2-u02-p01','q9'):'The original appointment cloze admits حجز and related scheduling nouns. Constrain it to موعد/رد.',('ar-a2-u02-p01','q10'):'The original waiting-for-a-response cloze admits جوابه and other response nouns. Constrain it to رده/موعده.',('ar-a2-u02-p02','q9'):'The original certainty cloze admits واثقًا and similar adjectives. Constrain it to متأكدًا/بعيدًا.',('ar-a2-u02-p02','q10'):'The original following-lesson cloze admits القادم. Constrain it to التالي/السابق.',('ar-a2-u02-p03','q9'):'The original change-notification cloze admits كلمت and other contact verbs. Constrain it to اتصلت/انتظرت.',('ar-a2-u02-p03','q10'):'The original later-time cloze admits آخر and other temporal adjectives. Constrain it to لاحق/سابق.',('ar-a2-u02-p04','q9'):'The original alternatives cloze admits طريق and خيار. Constrain it to اختيار/موعد.',('ar-a2-u02-p04','q10'):'The original current-address cloze admits الجديد. Constrain it to الحالي/التالي.',('ar-a2-u02-p05','q9'):'The original learning-program cloze admits ورشة and برنامج. Constrain it to دورة/زيارة.',('ar-a2-u02-p05','q10'):'The original travel-planning cloze admits تخطيط. Constrain it to تنظيم/سعر.'}[(pid,qid)]
def main():
 raw=CANON.read_bytes(); canon=sha(raw); rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]; ids=[f'ar-a2-u02-p{i:02d}' for i in range(1,7)]; by={r['id']:r for r in rows}; hs={p:lh(by[p]) for p in ids}
 for (p,q),new in NEW_PROMPTS.items():
  if {x['id']:x for x in by[p]['questions']}[q]['prompt']!=new: raise SystemExit(f'{p}/{q}: repaired prompt absent')
 repaired={p for p,_ in NEW_PROMPTS}
 for p in ids:
  if p in repaired and hs[p]==OLD_HASHES[p]: raise SystemExit(f'{p}: hash unchanged')
  if p not in repaired and hs[p]!=OLD_HASHES[p]: raise SystemExit(f'{p}: clean record drift')
 dec=[]
 for p in ids:
  qs=[q for pp,q in NEW_PROMPTS if pp==p]; fs=[{'finding_id':f'{p}-gC-{i:02d}','field':f'question {q}','dimension':'competing_answer_ambiguity','severity':'major','status':'REPAIRED','rationale':reason(p,q)} for i,q in enumerate(qs,1)]; dec.append({'passage_id':p,'learner_facing_sha256':hs[p],'decision':'PASS_AFTER_REPAIR' if fs else 'PASS','qa_pairs_reviewed':10,'finding_count':len(fs),'findings':fs})
 doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'A2','unit':2,'date':'2026-09-06','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/a2/passages.jsonl','canonical_sha256':canon,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'decisions':dec,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; the level SHA records the review-time snapshot.'}
 if OUT.exists():
  if json.loads(OUT.read_text())!=doc: raise SystemExit('existing A2 Unit 2 evidence drift')
  g=json.loads(GATE_B.read_text()); bd={d['passage_id']:d for d in g['decisions']}
  if any(bd[p]['learner_facing_sha256']!=hs[p] for p in ids) or g.get('post_gate_c_revalidations',[]).count(REVAL)!=1: raise SystemExit('Gate B idempotent verification failed')
  print('A2 Unit 2 evidence verified idempotently'); return
 OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
 g=json.loads(GATE_B.read_text()); bd={d['passage_id']:d for d in g['decisions']}
 for p,h in OLD_HASHES.items():
  if bd[p]['learner_facing_sha256']!=h: raise SystemExit(f'{p}: Gate B pre-rebind drift')
 g['canonical_sha256']=canon
 for p,h in hs.items(): bd[p]['learner_facing_sha256']=h
 rv=g.setdefault('post_gate_c_revalidations',[])
 if REVAL in rv: raise SystemExit('duplicate revalidation')
 rv.append(REVAL); GATE_B.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'level':'A2','unit':2,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'release_claim':False},indent=2))
if __name__=='__main__':main()
