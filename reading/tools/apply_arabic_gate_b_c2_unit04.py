#!/usr/bin/env python3
"""Apply fresh Arabic Gate B C2 Unit 4 assessment/naturalness repairs."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; R=ROOT/'reading'; PATH=R/'arabic/c2/passages.jsonl'; RELEASE=R/'RELEASE_STATUS.json'; INV=R/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; DD=R/'audit/arabic_gate_b_decisions_2026-08-30'
IDS=[f'ar-c2-u04-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-04 fresh Gate B naturalness review (C2 Unit 4): learner-facing prose/Q/A reviewed passage by passage; only high-confidence assessment-alignment and MSA wording repairs applied; no educator/publication release claim.'
SUMMARY_PROMPT='لخّص في جملة واحدة القضية أو الإشكال المركزي الذي ينظم النص حوله تحليله أو تأويله.'
REPAIRS={
'ar-c2-u04-p01':{
 'q1':('لأن سرعة الاستهلاك والتوريد وزمن التعويض تحدد مدة بقاء المخزون.','القضية هي أن أمان المخزون لا تحدده كميته الحالية وحدها، بل يتوقف على معدلات الدخول والخروج وزمن التعويض وحدود التخزين ومسارات التوريد عبر الزمن.'),
 'q8':('تجعل فائدة البديل مشروطة باستقلال مساره عن سبب التعطل؛ فإذا شارك المصدر نفسه للبنية الحرجة لا يزيل الخطر النظامي نفسه.','تجعل فائدة البديل مشروطة باستقلال مساره عن سبب التعطل؛ فإذا اشترك مع المصدر الأصلي في البنية الحرجة نفسها، لم يُزِل الخطر النظامي ذاته.'),
},
'ar-c2-u04-p02':{'q1':('لأن الإيرادات والمدفوعات تصل في أوقات مختلفة داخل السنة.','القضية هي أن الربحية أو الرصيد المحاسبي على مدى فترة لا يساوي السيولة المتاحة في كل لحظة، لأن توقيت القبض والدفع والالتزامات قد يخلق فجوات تشغيلية مؤقتة.')},
'ar-c2-u04-p03':{'q1':('لأن الشركات تكيفت وتغير عدد المنتجين والأسعار، فصار التصدير مجديًا لبعض الكبار.','القضية هي أن أثر صدمة تكلفة الوقود لا يبقى خطيًا، لأن تكيف الشركات والتأخيرات وتغير بنية السوق والتوقعات تولد ردود فعل تغير مسار التصدير عبر الزمن.')},
'ar-c2-u04-p04':{
 'q1':('عندما تتبنى شركات كثيرة الطلب اللحظي فيرتفع التذبذب والازدحام عند المورد.','القضية هي أن خفض المخزون قد يحسن كفاءة شركة منفردة لكنه يخلق ازدحامًا وكلفًا جديدة عندما تعمم الشركات الاستراتيجية نفسها على شبكة موردين ذات قدرة مشتركة.'),
 'q3':('لأن المصنع الكبير يحتكر جزءًا من المورد حتى عندما لا يستخدمه كاملًا.','لأن المصنع الكبير يحتكر جزءًا من قدرة المورد حتى عندما لا يستخدم ذلك الجزء كاملًا.'),
},
'ar-c2-u04-p05':{'q1':('لأن القيمة المقدرة تعتمد على سعر هامشي وقد يتغير السعر عند بيع كمية كبيرة.','القضية هي أن سعر السوق والقيمة المقدرة والسيولة القابلة للتحقق ليست شيئًا واحدًا، لأن حجم البيع والتوقعات والتمويل وردود الفعل يمكن أن تغير السعر والأثر الاقتصادي.')},
'ar-c2-u04-p06':{'q1':('أن النتائج تنشأ من تراكم وردود فعل وتفاعل بين قرارات تغير بيئة بعضها بعضًا.','القضية هي أن نتائج الأنظمة الاقتصادية المعقدة تنشأ من تراكمات وردود فعل وتفاعلات تجعل قرارات الجهات تغير البيئة التي تواجهها جهات أخرى عبر أزمنة مختلفة.')},
}
META={pid:[] for pid in IDS}
for pid in IDS:
 META[pid].append(('answer q1','assessment_wording','moderate','The current C2 q1 prompt requires a standalone one-sentence summary, but the keyed response is a causal, temporal, or nominal fragment inherited from the earlier task shape; replace it with a complete declarative summary of the passage’s organizing issue.'))
META['ar-c2-u04-p01'].append(('answer q8','naturalness','moderate','The phrase «شارك المصدر نفسه للبنية الحرجة» is not idiomatic for two suppliers sharing a critical dependency; express the intended relationship as sharing the same critical infrastructure.'))
META['ar-c2-u04-p04'].append(('answer q3','semantic_wording','moderate','The answer says the large factory monopolizes «جزءًا من المورد», but the passage concerns reserved production capacity; name the supplier’s capacity explicitly to preserve the intended system relation.'))
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
 if (p.get('fresh_records_reviewed'),p.get('fresh_records_with_findings'),p.get('fresh_findings'),d.get('open_findings'))!=(318,269,498,1248) or p.get('levels_completed')!=['A1','A2','B1','B2','C1']: raise SystemExit('C2 Unit 4 frontier drift')
 if not (DD/'c2_u03.json').exists() or (DD/'c2_u04.json').exists(): raise SystemExit('decision frontier drift')
 inv=json.loads(INV.read_text()); c2=inv.get('levels',{}).get('c2',{})
 if c2.get('canonical_sha256')!=pre or c2.get('fresh_review_status')!='IN_PROGRESS': raise SystemExit('inventory/hash frontier drift')
 rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]
 if len(rows)!=60 or [rows[i].get('id') for i in range(18,24)]!=IDS: raise SystemExit('C2 Unit 4 layout drift')
 by={r['id']:r for r in rows}; before={pid:targets(by[pid]) for pid in IDS}
 for pid in IDS:
  r=by[pid]; q=r.get('quality',{})
  if q.get('status')!='draft' or q.get('coverage_check')!='pending' or any(q.get(f)!='pending' for f in ('linguistic_review','pedagogical_review','answer_key_check','schema_check')): raise SystemExit(f'{pid}: quality frontier drift')
  qs={x['id']:x for x in r.get('questions',[])}; ans={a['question_id']:a for a in r.get('answer_key',[])}
  if qs.get('q1',{}).get('type')!='summary' or qs.get('q1',{}).get('prompt')!=SUMMARY_PROMPT: raise SystemExit(f'{pid}: q1 summary prompt drift')
  for qid,(old,new) in REPAIRS[pid].items():
   if ans.get(qid,{}).get('answer')!=old: raise SystemExit(f'{pid}/{qid}: answer drift')
   ans[qid]['answer']=new
  r['word_count']=wc(r['text'])
  if not 700<=r['word_count']<=1200: raise SystemExit(f'{pid}: C2 word band drift')
  if targets(r)!=before[pid]: raise SystemExit(f'{pid}: lexical target drift')
  if len(r.get('questions',[]))!=10 or len(r.get('answer_key',[]))!=10: raise SystemExit(f'{pid}: 10Q/10A invariant failed')
  aid={a['id']:a for a in r['answer_key']}
  for qq in r['questions']:
   a=qq.get('answer_id')
   if a not in aid or aid[a].get('question_id')!=qq.get('id'): raise SystemExit(f'{pid}: answer linkage drift')
  r['revision']=int(r.get('revision',0) or 0)+1; q=r.setdefault('quality',{})
  for f in ('linguistic_review','pedagogical_review','answer_key_check','schema_check'): q[f]='pass'
  if NOTE not in q.setdefault('notes',[]): q['notes'].append(NOTE)
 if (sum(len(META[x]) for x in IDS),sum(bool(META[x]) for x in IDS))!=(8,6): raise SystemExit('finding metadata drift')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows))
 print(json.dumps({'level':'C2','unit':4,'records_reviewed':6,'records_with_findings':6,'fresh_findings':8,'pre_repair_canonical_sha256':pre,'post_repair_canonical_sha256':sha(PATH.read_bytes())},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
