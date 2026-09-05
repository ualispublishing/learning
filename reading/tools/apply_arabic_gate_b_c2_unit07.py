#!/usr/bin/env python3
"""Apply fresh Arabic Gate B C2 Unit 7 assessment-alignment repairs."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; R=ROOT/'reading'; PATH=R/'arabic/c2/passages.jsonl'; RELEASE=R/'RELEASE_STATUS.json'; INV=R/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; DD=R/'audit/arabic_gate_b_decisions_2026-08-30'
IDS=[f'ar-c2-u07-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-04 fresh Gate B naturalness review (C2 Unit 7): learner-facing prose/Q/A reviewed passage by passage; only high-confidence summary-answer assessment-alignment repairs applied; no educator/publication release claim.'
SUMMARY_PROMPT='لخّص في جملة واحدة القضية أو الإشكال المركزي الذي ينظم النص حوله تحليله أو تأويله.'
REPAIRS={
'ar-c2-u07-p02':('لأن المترجم والزمن والجمهور قد يصنعون الفرق.','القضية هي أن الفروق بين الترجمات لا تكشف الأصل وحده، لأن المترجم والجمهور والزمن وسلسلة النقل قد تصنعها، ولذلك يحتاج تفسيرها إلى أدلة مستقلة تتتبع مصدر الاختلاف.'),
'ar-c2-u07-p03':('لأن تفاصيل النسخ وأصوات الشخصيات تدعم قراءات متعارضة.','القضية هي أن تعدد قراءات الأسطورة يمكن أن يكون منضبطًا إذا ربط كل تفسير بتفاصيل البنية والأصوات والسياق واختبر ما يتركه بلا تفسير وما قد يضعفه.'),
'ar-c2-u07-p05':('لأن السماع يفرض ذاكرة خطية ولا يتيح الرجوع البصري نفسه.','القضية هي أن نقل النص من الصفحة إلى وسيط صوتي يغير شروط الذاكرة والإحالة والسرعة والرجوع، ولذلك قد تتطلب الوظيفة نفسها إعادة صياغة وتعويضات تناسب الأداء المسموع.'),
'ar-c2-u07-p06':('أن الترجمة تفسير مقيد بالوظيفة والسياق والأدلة وليست نسخًا شفافًا.','القضية هي أن الترجمة والتكييف والنقل بين الوسائط أشكال من تفسير مسؤول تقيده الوظيفة والسياق والأدلة والجمهور، لا عمليات نسخ شفافة أو حرية بلا حدود.'),
}
CLEAN={
'ar-c2-u07-p01':'قد تحفظ الكلمات ولا تحفظ الفعل الاجتماعي المقصود.',
'ar-c2-u07-p04':'يحافظ على شبكة علاقات أساسية مع تغيير الإشارات لتناسب جمهورًا جديدًا.',
}
META={pid:[] for pid in IDS}
for pid in REPAIRS:
 META[pid]=[('answer q1','assessment_wording','moderate','The current C2 q1 prompt requires a standalone one-sentence summary, but the keyed response is a causal or أن-fragment inherited from the earlier task shape; replace it with a complete declarative summary of the passage’s organizing issue.')]
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
 if (p.get('fresh_records_reviewed'),p.get('fresh_records_with_findings'),p.get('fresh_findings'),d.get('open_findings'))!=(336,286,519,1176) or p.get('levels_completed')!=['A1','A2','B1','B2','C1']: raise SystemExit('C2 Unit 7 frontier drift')
 if not (DD/'c2_u06.json').exists() or (DD/'c2_u07.json').exists(): raise SystemExit('decision frontier drift')
 inv=json.loads(INV.read_text()); c2=inv.get('levels',{}).get('c2',{})
 if c2.get('canonical_sha256')!=pre or c2.get('fresh_review_status')!='IN_PROGRESS': raise SystemExit('inventory/hash frontier drift')
 rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]
 if len(rows)!=60 or [rows[i].get('id') for i in range(36,42)]!=IDS: raise SystemExit('C2 Unit 7 layout drift')
 by={r['id']:r for r in rows}; before={pid:targets(by[pid]) for pid in IDS}
 for pid in IDS:
  r=by[pid]; q=r.get('quality',{})
  if q.get('status')!='draft' or q.get('coverage_check')!='pending' or any(q.get(f)!='pending' for f in ('linguistic_review','pedagogical_review','answer_key_check','schema_check')): raise SystemExit(f'{pid}: quality frontier drift')
  qs={x['id']:x for x in r.get('questions',[])}; ans={a['question_id']:a for a in r.get('answer_key',[])}
  if qs.get('q1',{}).get('type')!='summary' or qs.get('q1',{}).get('prompt')!=SUMMARY_PROMPT: raise SystemExit(f'{pid}: q1 summary prompt drift')
  if pid in REPAIRS:
   old,new=REPAIRS[pid]
   if ans.get('q1',{}).get('answer')!=old: raise SystemExit(f'{pid}/q1: answer drift')
   ans['q1']['answer']=new
  else:
   if ans.get('q1',{}).get('answer')!=CLEAN[pid]: raise SystemExit(f'{pid}/q1: clean-answer drift')
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
 if (sum(len(META[x]) for x in IDS),sum(bool(META[x]) for x in IDS))!=(4,4): raise SystemExit('finding metadata drift')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows))
 print(json.dumps({'level':'C2','unit':7,'records_reviewed':6,'records_with_findings':4,'fresh_findings':4,'pre_repair_canonical_sha256':pre,'post_repair_canonical_sha256':sha(PATH.read_bytes())},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
