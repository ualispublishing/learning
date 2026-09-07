#!/usr/bin/env python3
"""Record Arabic Gate C A2 Unit 8 decisions and rebind affected Gate B evidence."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];READING=ROOT/'reading';CANON=READING/'arabic/a2/passages.jsonl';OUT=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u08.json';GATE_B=READING/'audit/arabic_gate_b_decisions_2026-08-30/a2_u08.json'
OLD_HASHES={'ar-a2-u08-p01':'7ef010028486b6c6c0a3b54148aac86ea9f39ddc45fbf55deb69d665360c4db8','ar-a2-u08-p02':'37a6fa53ac6bd42411e6fdc624f45398827c53fa098c1f416709ffbf5ac304ca','ar-a2-u08-p03':'ae86039b0fe04b3c4f0ec6ff0f3ff0b240560df52577f43516c12075e38fefa7','ar-a2-u08-p04':'58a9dad1fbecd192fb2e0706386f8f0b06d3aae2f8d41b9de67429c30cba2f2a','ar-a2-u08-p05':'e3159a90b9e62a0b2c2ad715a83bd2e2bb27783d9f0e8af1e9a06505997ba937','ar-a2-u08-p06':'059ae26479b79fc43a660032a521039aa4fe62c65b6664bd1fd4cd1c9f8f3dd5'}
NEW_PROMPTS={('ar-a2-u08-p01','q9'):'اختر من «منطقة» و«مواد»: هذه _____ هادئة من الحديقة.',('ar-a2-u08-p01','q10'):'اختر من «مواد» و«منطقة»: صنع الطلاب النموذج من _____ بسيطة معاد استخدامها.',('ar-a2-u08-p02','q9'):'اختر من «استخدام» و«طاقة»: نحاول تقليل _____ الورق عندما لا نحتاج إليه.',('ar-a2-u08-p02','q10'):'اختر من «طاقة» و«استخدام»: تحتاج الأجهزة الكهربائية إلى _____.',('ar-a2-u08-p03','q9'):'اختر من «نمو» و«منطقة»: يحتاج _____ النبات إلى ماء وضوء مناسبين.',('ar-a2-u08-p05','q9'):'اختر من «المجتمع» و«الطاقة»: شارك أفراد _____ في اقتراح حلول للحي.'}
REVAL={'date':'2026-09-07','gate_c_artifact':'reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u08.json','scope':[f'{p} question {q}' for p,q in NEW_PROMPTS],'gate_b_language_recheck':'PASS','reason':'Gate C constrained six underdetermined A2 Unit 8 environmental transfer items covering area, materials, usage, energy, growth, and community; keyed answers were preserved and Gate B was rebound to exact-current learner-facing content.','release_claim':False}
def sha(b):return hashlib.sha256(b).hexdigest()
def payload(r):
 a={x.get('question_id'):x for x in r.get('answer_key',[])};notes='\n'.join(r.get('quality',{}).get('notes',[]));hist='naturalness' in notes.lower();return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
R={('ar-a2-u08-p01','q9'):'The original quiet-area cloze admits بقعة and other place nouns. Constrain it to منطقة/مواد.',('ar-a2-u08-p01','q10'):'The original reused-materials cloze admits أشياء and خامات. Constrain it to مواد/منطقة.',('ar-a2-u08-p02','q9'):'The original paper-use cloze admits استهلاك. Constrain it to استخدام/طاقة.',('ar-a2-u08-p02','q10'):'The original device-energy cloze admits كهرباء. Constrain it to طاقة/استخدام.',('ar-a2-u08-p03','q9'):'The original plant-growth cloze admits تطور and ازدهار. Constrain it to نمو/منطقة.',('ar-a2-u08-p05','q9'):'The original community-members cloze admits الحي and الأسرة in other contexts. Constrain it to المجتمع/الطاقة.'}
def main():
 raw=CANON.read_bytes();canon=sha(raw);rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()];ids=[f'ar-a2-u08-p{i:02d}' for i in range(1,7)];by={r['id']:r for r in rows};hs={p:lh(by[p]) for p in ids}
 for (p,q),new in NEW_PROMPTS.items():
  if {x['id']:x for x in by[p]['questions']}[q]['prompt']!=new:raise SystemExit(f'{p}/{q}: repaired prompt absent')
 repaired={p for p,_ in NEW_PROMPTS}
 for p in ids:
  if p in repaired and hs[p]==OLD_HASHES[p]:raise SystemExit(f'{p}: hash unchanged')
  if p not in repaired and hs[p]!=OLD_HASHES[p]:raise SystemExit(f'{p}: clean record drift')
 dec=[]
 for p in ids:
  qs=[q for pp,q in NEW_PROMPTS if pp==p];fs=[{'finding_id':f'{p}-gC-{i:02d}','field':f'question {q}','dimension':'competing_answer_ambiguity','severity':'major','status':'REPAIRED','rationale':R[(p,q)]} for i,q in enumerate(qs,1)];dec.append({'passage_id':p,'learner_facing_sha256':hs[p],'decision':'PASS_AFTER_REPAIR' if fs else 'PASS','qa_pairs_reviewed':10,'finding_count':len(fs),'findings':fs})
 doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'A2','unit':8,'date':'2026-09-07','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/a2/passages.jsonl','canonical_sha256':canon,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':4,'fresh_findings':6,'decisions':dec,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; the level SHA records the review-time snapshot.'}
 if OUT.exists():
  if json.loads(OUT.read_text())!=doc:raise SystemExit('existing A2 Unit 8 evidence drift')
  g=json.loads(GATE_B.read_text());bd={d['passage_id']:d for d in g['decisions']}
  if any(bd[p]['learner_facing_sha256']!=hs[p] for p in ids) or g.get('post_gate_c_revalidations',[]).count(REVAL)!=1:raise SystemExit('Gate B idempotent verification failed')
  print('A2 Unit 8 evidence verified idempotently');return
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
 g=json.loads(GATE_B.read_text());bd={d['passage_id']:d for d in g['decisions']}
 for p,h in OLD_HASHES.items():
  if bd[p]['learner_facing_sha256']!=h:raise SystemExit(f'{p}: Gate B pre-rebind drift')
 g['canonical_sha256']=canon
 for p,h in hs.items():bd[p]['learner_facing_sha256']=h
 rv=g.setdefault('post_gate_c_revalidations',[])
 if REVAL in rv:raise SystemExit('duplicate revalidation')
 rv.append(REVAL);GATE_B.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'level':'A2','unit':8,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':4,'fresh_findings':6,'release_claim':False},indent=2))
if __name__=='__main__':main()
