#!/usr/bin/env python3
"""Record Arabic Gate C A2 Unit 6 decisions and rebind affected Gate B evidence."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];READING=ROOT/'reading';CANON=READING/'arabic/a2/passages.jsonl';OUT=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u06.json';GATE_B=READING/'audit/arabic_gate_b_decisions_2026-08-30/a2_u06.json'
OLD_HASHES={'ar-a2-u06-p01':'66db0c4fd621d7d77d74f8ae2e3e8b7c9f4174ae7e45d3a94b15f529d2298e5c','ar-a2-u06-p02':'97b735d3c817d27b316ff4cc94d4fa129e41c0c7645d331f33189ae4cee116df','ar-a2-u06-p03':'0f7a222bf5d5bbdac527ad97d4fc4d9fc9eb7a76106818d848eef7d79c0ee5ad','ar-a2-u06-p04':'ba4bcc253739d7294d2e72ad8ad9acf97378759214a28c40283ebeacd4a9eff7','ar-a2-u06-p05':'1c8fff4b092449aa407f350e88161b4efc8bfcae8ed6c1ec32bf7065a27c1f48','ar-a2-u06-p06':'80d1c318085899eb3c37c4fc5bc8e33d282c4454c342d71d1725cb8b9e66036b'}
NEW_PROMPTS={('ar-a2-u06-p01','q9'):'اختر من «طائرة» و«قطار»: سافرنا جوًا إلى المدينة بال_____.',('ar-a2-u06-p01','q10'):'اختر من «المطار» و«القرية»: وصلنا إلى _____ لإنهاء إجراءات الرحلة قبل الإقلاع بساعتين.',('ar-a2-u06-p02','q9'):'اختر من «قطارًا» و«طائرة»: أخذنا _____ يسير على السكة من المحطة إلى المدينة التالية.',('ar-a2-u06-p02','q10'):'اختر من «الانتظار» و«الوصول»: استمر _____ عشر دقائق قبل فتح الباب.',('ar-a2-u06-p03','q9'):'اختر من «النقل» و«الانتظار»: القطار والحافلة من وسائل _____ داخل المدينة.',('ar-a2-u06-p03','q10'):'اختر من «وسائل» و«قرى»: توجد _____ نقل مختلفة داخل المدينة.',('ar-a2-u06-p04','q9'):'اختر من «يتوقف» و«يطير»: القطار _____ في هذه المحطة خمس دقائق.',('ar-a2-u06-p04','q10'):'اختر من «مناسب» و«أسوأ»: هذا الوقت _____ للاجتماع عندي.',('ar-a2-u06-p05','q9'):'اختر من «قرية» و«بحر»: زاروا _____ صغيرة بين الجبال.',('ar-a2-u06-p05','q10'):'اختر من «البحر» و«القرية»: أبحرت السفينة في _____.'}
REVAL={'date':'2026-09-06','gate_c_artifact':'reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u06.json','scope':[f'{p} question {q}' for p,q in NEW_PROMPTS],'gate_b_language_recheck':'PASS','reason':'Gate C constrained ten underdetermined A2 Unit 6 travel-transfer items with explicit air, rail, waiting, transport, stopping, suitability, village, and sea cues; keyed answers were preserved and Gate B was rebound to exact-current learner-facing content.','release_claim':False}
def sha(b):return hashlib.sha256(b).hexdigest()
def payload(r):
 a={x.get('question_id'):x for x in r.get('answer_key',[])};notes='\n'.join(r.get('quality',{}).get('notes',[]));hist='naturalness' in notes.lower();return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
R={('ar-a2-u06-p01','q9'):'The original travel-mode cloze admits train, car, and other modes. Add an air-travel cue and constrain it to airplane/train.',('ar-a2-u06-p01','q10'):'The original pre-trip location cloze admits station and other places. Anchor it to pre-flight procedures and constrain airport/village.',('ar-a2-u06-p02','q9'):'The original station-to-city cloze admits bus and other modes. Add a rail cue and constrain train/airplane.',('ar-a2-u06-p02','q10'):'The original duration cloze admits delay. Constrain waiting/arrival.',('ar-a2-u06-p03','q9'):'The transport-category cloze admits مواصلات and other category nouns. Constrain transport/waiting.',('ar-a2-u06-p03','q10'):'The transport-means cloze admits طرق and أنواع. Constrain وسائل/قرى.',('ar-a2-u06-p04','q9'):'The station-action cloze admits يبقى and ينتظر. Constrain stops/flies.',('ar-a2-u06-p04','q10'):'The suitable-time cloze admits ملائم. Constrain suitable/worse.',('ar-a2-u06-p05','q9'):'The small-settlement cloze admits بلدة. Constrain village/sea.',('ar-a2-u06-p05','q10'):'The beach-nearby cloze admits water or village in some contexts. Replace it with a sea-navigation transfer and constrain sea/village.'}
def main():
 raw=CANON.read_bytes();canon=sha(raw);rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()];ids=[f'ar-a2-u06-p{i:02d}' for i in range(1,7)];by={r['id']:r for r in rows};hs={p:lh(by[p]) for p in ids}
 for (p,q),new in NEW_PROMPTS.items():
  if {x['id']:x for x in by[p]['questions']}[q]['prompt']!=new:raise SystemExit(f'{p}/{q}: repaired prompt absent')
 repaired={p for p,_ in NEW_PROMPTS}
 for p in ids:
  if p in repaired and hs[p]==OLD_HASHES[p]:raise SystemExit(f'{p}: hash unchanged')
  if p not in repaired and hs[p]!=OLD_HASHES[p]:raise SystemExit(f'{p}: clean record drift')
 dec=[]
 for p in ids:
  qs=[q for pp,q in NEW_PROMPTS if pp==p];fs=[{'finding_id':f'{p}-gC-{i:02d}','field':f'question {q}','dimension':'competing_answer_ambiguity','severity':'major','status':'REPAIRED','rationale':R[(p,q)]} for i,q in enumerate(qs,1)];dec.append({'passage_id':p,'learner_facing_sha256':hs[p],'decision':'PASS_AFTER_REPAIR' if fs else 'PASS','qa_pairs_reviewed':10,'finding_count':len(fs),'findings':fs})
 doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'A2','unit':6,'date':'2026-09-06','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/a2/passages.jsonl','canonical_sha256':canon,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'decisions':dec,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; the level SHA records the review-time snapshot.'}
 if OUT.exists():
  if json.loads(OUT.read_text())!=doc:raise SystemExit('existing A2 Unit 6 evidence drift')
  g=json.loads(GATE_B.read_text());bd={d['passage_id']:d for d in g['decisions']}
  if any(bd[p]['learner_facing_sha256']!=hs[p] for p in ids) or g.get('post_gate_c_revalidations',[]).count(REVAL)!=1:raise SystemExit('Gate B idempotent verification failed')
  print('A2 Unit 6 evidence verified idempotently');return
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
 g=json.loads(GATE_B.read_text());bd={d['passage_id']:d for d in g['decisions']}
 for p,h in OLD_HASHES.items():
  if bd[p]['learner_facing_sha256']!=h:raise SystemExit(f'{p}: Gate B pre-rebind drift')
 g['canonical_sha256']=canon
 for p,h in hs.items():bd[p]['learner_facing_sha256']=h
 rv=g.setdefault('post_gate_c_revalidations',[])
 if REVAL in rv:raise SystemExit('duplicate revalidation')
 rv.append(REVAL);GATE_B.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'level':'A2','unit':6,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':5,'fresh_findings':10,'release_claim':False},indent=2))
if __name__=='__main__':main()
