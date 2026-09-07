#!/usr/bin/env python3
"""Record Arabic Gate C A2 Unit 9 decisions and rebind affected Gate B evidence."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];READING=ROOT/'reading';CANON=READING/'arabic/a2/passages.jsonl';OUT=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u09.json';GATE_B=READING/'audit/arabic_gate_b_decisions_2026-08-30/a2_u09.json'
OLD_HASHES={'ar-a2-u09-p01':'37ff23ebacdd4b3c2882710327045fefa8cc5a7b02c7ca31e819d6c330a4e608','ar-a2-u09-p02':'47fc502d817836480effe720ac78bb49955f30a7beaf445487848f893dd46a26','ar-a2-u09-p03':'2eae1f541dff70796c7aef6a81edf68740e80651a8a55a38dc4f220e1557a86f','ar-a2-u09-p04':'a69e6488d8b14ccc7a13fc495b5d177e2cd7308534672a184665edea9e582eb6','ar-a2-u09-p05':'41e7cc291eb5af9abc30c2f6f0050de7fab0a25d5719fff11074d130835480d8','ar-a2-u09-p06':'766ab5de9d0504e48e79aee7723d295e14c8abd65045d48396ca0e8f35c172b5'}
NEW_PROMPTS={('ar-a2-u09-p01','q9'):'اختر من «قصة» و«نسخة»: حكت الجدة _____ عن طفولتها.',('ar-a2-u09-p02','q9'):'اختر من «نسخة» و«قصة»: عندي _____ إلكترونية من الكتاب.',('ar-a2-u09-p03','q9'):'اختر من «مطعم» و«مطار»: حجزنا طاولة للعشاء في _____ قريب.'}
REVAL={'date':'2026-09-07','gate_c_artifact':'reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u09.json','scope':[f'{p} question {q}' for p,q in NEW_PROMPTS],'gate_b_language_recheck':'PASS','reason':'Gate C constrained three underdetermined A2 Unit 9 transfer items covering story, version/copy, and restaurant; keyed answers were preserved and Gate B was rebound to exact-current learner-facing content.','release_claim':False}
def sha(b):return hashlib.sha256(b).hexdigest()
def payload(r):
 a={x.get('question_id'):x for x in r.get('answer_key',[])};notes='\n'.join(r.get('quality',{}).get('notes',[]));hist='naturalness' in notes.lower();return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
R={('ar-a2-u09-p01','q9'):'The original childhood-story cloze admits حكاية and related narrative nouns. Constrain it to قصة/نسخة.',('ar-a2-u09-p02','q9'):'The original electronic-book cloze admits طبعة in some contexts. Constrain it to نسخة/قصة.',('ar-a2-u09-p03','q9'):'The original table-reservation cloze admits مقهى and other venues. Add a dinner cue and constrain it to مطعم/مطار.'}
def main():
 raw=CANON.read_bytes();canon=sha(raw);rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()];ids=[f'ar-a2-u09-p{i:02d}' for i in range(1,7)];by={r['id']:r for r in rows};hs={p:lh(by[p]) for p in ids}
 for (p,q),new in NEW_PROMPTS.items():
  if {x['id']:x for x in by[p]['questions']}[q]['prompt']!=new:raise SystemExit(f'{p}/{q}: repaired prompt absent')
 repaired={p for p,_ in NEW_PROMPTS}
 for p in ids:
  if p in repaired and hs[p]==OLD_HASHES[p]:raise SystemExit(f'{p}: hash unchanged')
  if p not in repaired and hs[p]!=OLD_HASHES[p]:raise SystemExit(f'{p}: clean record drift')
 dec=[]
 for p in ids:
  qs=[q for pp,q in NEW_PROMPTS if pp==p];fs=[{'finding_id':f'{p}-gC-{i:02d}','field':f'question {q}','dimension':'competing_answer_ambiguity','severity':'major','status':'REPAIRED','rationale':R[(p,q)]} for i,q in enumerate(qs,1)];dec.append({'passage_id':p,'learner_facing_sha256':hs[p],'decision':'PASS_AFTER_REPAIR' if fs else 'PASS','qa_pairs_reviewed':10,'finding_count':len(fs),'findings':fs})
 doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'A2','unit':9,'date':'2026-09-07','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/a2/passages.jsonl','canonical_sha256':canon,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':3,'fresh_findings':3,'decisions':dec,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; the level SHA records the review-time snapshot.'}
 if OUT.exists():
  if json.loads(OUT.read_text())!=doc:raise SystemExit('existing A2 Unit 9 evidence drift')
  g=json.loads(GATE_B.read_text());bd={d['passage_id']:d for d in g['decisions']}
  if any(bd[p]['learner_facing_sha256']!=hs[p] for p in ids) or g.get('post_gate_c_revalidations',[]).count(REVAL)!=1:raise SystemExit('Gate B idempotent verification failed')
  print('A2 Unit 9 evidence verified idempotently');return
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
 g=json.loads(GATE_B.read_text());bd={d['passage_id']:d for d in g['decisions']}
 for p,h in OLD_HASHES.items():
  if bd[p]['learner_facing_sha256']!=h:raise SystemExit(f'{p}: Gate B pre-rebind drift')
 g['canonical_sha256']=canon
 for p,h in hs.items():bd[p]['learner_facing_sha256']=h
 rv=g.setdefault('post_gate_c_revalidations',[])
 if REVAL in rv:raise SystemExit('duplicate revalidation')
 rv.append(REVAL);GATE_B.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'level':'A2','unit':9,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':3,'fresh_findings':3,'release_claim':False},indent=2))
if __name__=='__main__':main()
