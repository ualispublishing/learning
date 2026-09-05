#!/usr/bin/env python3
"""Apply fresh Arabic Gate B C1 Unit 9 assessment/naturalness repairs."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; R=ROOT/'reading'; PATH=R/'arabic/c1/passages.jsonl'; RELEASE=R/'RELEASE_STATUS.json'; INV=R/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; DD=R/'audit/arabic_gate_b_decisions_2026-08-30'
IDS=[f'ar-c1-u09-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-04 fresh Gate B naturalness review (C1 Unit 9): learner-facing prose/Q/A reviewed passage by passage; only high-confidence MSA grammar, idiom, reference, semantic, and assessment-wording repairs applied; no educator/publication release claim.'
REPAIRS={
'ar-c1-u09-p01':[('answer q1','لأن السبق الزمني لا يستبعد أسبابًا أو وسائط أخرى.','القضية هي أن السبق الزمني يقيّد التفسير التاريخي لكنه لا يثبت السببية وحده، إذ تحتاج السببية إلى آليات وأدلة ومقارنات إضافية.','assessment_wording')],
'ar-c1-u09-p02':[('answer q1','يعترف بأن السؤال راهن لكنه يفصل مفاهيمه عن ألفاظ الماضي ويختبر المعاني في سياقها.','القضية هي أن المؤرخ يستطيع أن يبدأ بسؤال راهن من دون إسقاط فئات الحاضر على الماضي إذا أعلن مفاهيمه واختبرها في سياق المصادر التاريخية.','assessment_wording')],
'ar-c1-u09-p03':[('answer q1','لأنها صممت لمهمة نقل فركزت على عناصر تخدم ذلك الغرض.','القضية هي أن قيمة المصدر الجغرافي تتحدد بقدرته على الإجابة عن أسئلة مرتبطة بغرضه ومجال رؤيته، لا بكونه محايدًا أو متحيزًا بإطلاق.','assessment_wording'),('answer q6','الزاوية تحدد مجال الرؤية، أما الكذب فيتعلق بتقديم معلومات غير صحيحة عمدًا أو بوضوح.','الزاوية تحدد مجال ما يستطيع المصدر رؤيته وتسجيله، أما الكذب فيتعلق بتقديم معلومات غير صحيحة مع العلم بعدم صحتها.','semantic_precision')],
'ar-c1-u09-p04':[('answer q1','لأن قربها من الحدث قد يصاحبه ضغط سياسي أو مؤسسي على ما يمكن قوله.','القضية هي أن توقيت المصدر لا يحدد موثوقيته آليًا، لأن القرب من الحدث والبعد عنه يقدمان مزايا وقيودًا مختلفة يجب وزنها بحسب نوع الادعاء.','assessment_wording')],
'ar-c1-u09-p05':[('answer q1','قد توحي بأن الرحيل حدث موحد في لحظة واحدة رغم أنه كان ممتدًا ومتعدد المسارات.','القضية هي أن ترتيب المواد الوثائقية قد يضغط تجربة تاريخية ممتدة في سرد موحد، حتى عندما تكون كل لقطة صحيحة منفردة.','assessment_wording')],
'ar-c1-u09-p06':[('answer q1','إنها بناء حجة ورواية مقيدة بما تسمح به المصادر وحدودها وليست نسخة مباشرة من الماضي.','القضية هي أن الرواية التاريخية حجة مبنية من مصادر ناقصة ومحدودة، ويجب أن تعلن اختياراتها وحدود أدلتها ودرجات الثقة بدل أن تدعي نسخ الماضي مباشرة.','assessment_wording')],
}
META={pid:[(f,d,'moderate',('The q1 prompt explicitly asks for a one-sentence summary, while the keyed response retains an older fragment or context-dependent formulation; replace it with a complete standalone summary aligned to the current prompt.' if d=='assessment_wording' else 'The answer conflates clearly inaccurate information with lying by saying false information may be presented deliberately “or clearly”; lying requires a deception/knowledge condition, whereas source viewpoint merely constrains what the source sees and records.'))) for f,_,__,d in reps] for pid,reps in REPAIRS.items()}
def sha(b): return hashlib.sha256(b).hexdigest()
def wc(t): return len(TOKEN.findall(t))
def targets(r):
 fs=[]
 for k in ('new_lexical_targets','review_lexical_targets'):
  for x in r.get(k,[]):
   f=x.get('form')
   if isinstance(f,str) and f and f not in fs: fs.append(f)
 t=r.get('text',''); return {f:t.count(f) for f in fs}
def main():
 raw=PATH.read_bytes(); pre=sha(raw); rel=json.loads(RELEASE.read_text()); ar=rel['languages']['arabic']; p=ar['naturalness_review_progress']; d=ar['latest_deterministic_gate']
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False: raise SystemExit('release gate drift')
 if (p.get('fresh_records_reviewed'),p.get('fresh_records_with_findings'),p.get('fresh_findings'),d.get('open_findings'))!=(288,241,469,1368) or p.get('levels_completed')!=['A1','A2','B1','B2']: raise SystemExit('C1 Unit 9 frontier drift')
 if not (DD/'c1_u08.json').exists() or (DD/'c1_u09.json').exists(): raise SystemExit('decision frontier drift')
 inv=json.loads(INV.read_text()); c1=inv.get('levels',{}).get('c1',{})
 if c1.get('canonical_sha256')!=pre or c1.get('fresh_review_status')!='IN_PROGRESS': raise SystemExit('inventory/hash frontier drift')
 rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]
 if len(rows)!=60 or [rows[i].get('id') for i in range(48,54)]!=IDS: raise SystemExit('C1 Unit 9 layout drift')
 by={r['id']:r for r in rows}; before={pid:targets(by[pid]) for pid in IDS}
 for pid in IDS:
  r=by[pid]; q=r.get('quality',{})
  if q.get('status')!='draft' or q.get('coverage_check')!='pending' or any(q.get(f)!='pending' for f in ('linguistic_review','pedagogical_review','answer_key_check','schema_check')): raise SystemExit(f'{pid}: quality frontier drift')
  qs={x['id']:x for x in r.get('questions',[])}; ans={a['question_id']:a for a in r.get('answer_key',[])}
  if qs.get('q1',{}).get('type')!='summary' or qs.get('q1',{}).get('prompt')!='لخّص في جملة واحدة القضية المركزية التي يعالجها النص.': raise SystemExit(f'{pid}: q1 summary prompt drift')
  for field,old,new,_dim in REPAIRS[pid]:
   qid=field.split()[-1]
   if ans.get(qid,{}).get('answer')!=old: raise SystemExit(f'{pid}/{qid}: answer drift')
   ans[qid]['answer']=new
  r['word_count']=wc(r['text'])
  if not 500<=r['word_count']<=800: raise SystemExit(f'{pid}: word band drift')
  if targets(r)!=before[pid]: raise SystemExit(f'{pid}: lexical target drift')
  if len(r.get('questions',[]))!=10 or len(r.get('answer_key',[]))!=10: raise SystemExit(f'{pid}: 10Q/10A invariant failed')
  aid={a['id']:a for a in r['answer_key']}
  for qq in r['questions']:
   a=qq.get('answer_id')
   if a not in aid or aid[a].get('question_id')!=qq.get('id'): raise SystemExit(f'{pid}: answer linkage drift')
  r['revision']=int(r.get('revision',0) or 0)+1; q=r.setdefault('quality',{})
  for f in ('linguistic_review','pedagogical_review','answer_key_check','schema_check'): q[f]='pass'
  if NOTE not in q.setdefault('notes',[]): q['notes'].append(NOTE)
 if (sum(len(META[x]) for x in IDS),sum(bool(META[x]) for x in IDS))!=(7,6): raise SystemExit('finding metadata drift')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows))
 print(json.dumps({'level':'C1','unit':9,'records_reviewed':6,'records_with_findings':6,'fresh_findings':7,'pre_repair_canonical_sha256':pre,'post_repair_canonical_sha256':sha(PATH.read_bytes())},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
