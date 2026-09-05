#!/usr/bin/env python3
"""Apply fresh Arabic Gate B C2 Unit 9 assessment/naturalness repairs."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; R=ROOT/'reading'; PATH=R/'arabic/c2/passages.jsonl'; RELEASE=R/'RELEASE_STATUS.json'; INV=R/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; DD=R/'audit/arabic_gate_b_decisions_2026-08-30'
IDS=[f'ar-c2-u09-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-05 fresh Gate B naturalness review (C2 Unit 9): learner-facing prose/Q/A reviewed passage by passage; only high-confidence summary-answer assessment-alignment and MSA naturalness repairs applied; no educator/publication release claim.'
SUMMARY_PROMPT='لخّص في جملة واحدة القضية أو الإشكال المركزي الذي ينظم النص حوله تحليله أو تأويله.'
OLD_SUMMARY='اتخاذ قرار تقني أخلاقي تحت عدم يقين مع فصل الأداة عن سلطة القرار.'
SUMMARIES={
'ar-c2-u09-p01':'القضية هي أن تقييم القرار التقني أخلاقيًا لا يتوقف على دقة الأداة أو سرعتها، بل على كيفية توزيع سلطة الاختيار وكلفة الاعتراض وحجم الضرر وقابلية الرجوع والمسؤولية.',
'ar-c2-u09-p02':'القضية هي أن التخطيط تحت عدم اليقين يحتاج إلى سيناريوهات متعددة تختبر متانة القرار وتحافظ على المرونة، لا إلى تحويل أسوأ مسار أو أوضحه إلى تنبؤ مؤكد.',
'ar-c2-u09-p03':'القضية هي أن الإشراف البشري لا يصبح فعليًا بمجرد وجود مراجع، بل يحتاج إلى معلومات ووقت وخبرة وسلطة وحوافز تسمح باكتشاف الخطأ والاعتراض عليه والتعلم منه.',
'ar-c2-u09-p04':'القضية هي أن المسؤولية في النظام الموزع لا يمكن اختزالها في مكون منفرد، بل يجب الجمع بين مسؤوليات محلية واضحة وملكية للمخاطر والتفاعلات التي تعبر حدود الفرق.',
'ar-c2-u09-p05':'القضية هي أن نشر تقنية ناجحة أوليًا تحت عدم اليقين ينبغي أن يكون مرحليًا وقابلًا للتراجع، بحيث تجمع كل خطوة معلومات قبل إغلاق البدائل وتحدد مسبقًا شروط التوسع أو التوقف.',
'ar-c2-u09-p06':'القضية هي أن أخلاق التقنية تحت عدم اليقين تتطلب تصميمًا للقرار يربط الأداء بالسلطة والمعلومات والضرر والإشراف والمسؤولية وقابلية الرجوع، بدل السعي إلى إزالة كل خطأ مسبقًا.',
}
TEXT_REPAIRS={
'ar-c2-u09-p01':[('قاسوا ليس السرعة فقط، بل نسبة التعديل، ووقت فهم سبب الاقتراح، والفرق بين الموظفين الذين يملكون خبرة بالنظام ومن لا يملكونها.','لم يقيسوا السرعة فقط، بل قاسوا نسبة التعديل، ووقت فهم سبب الاقتراح، والفرق بين الموظفين الذين يملكون خبرة بالنظام ومن لا يملكونها.')],
'ar-c2-u09-p02':[('إذا استخدم الفريق المتوسطات منفصلة، فإنه يقلل من تقدير خطر اجتماعها.','إذا تعامل الفريق مع المتوسطات على نحو منفصل، فإنه يقلل من تقدير خطر اجتماعها.')],
'ar-c2-u09-p03':[('وفي حالات أخرى يزيد عدد المراجعين المسؤولية الموزعة ويجعل كل شخص يتوقع أن غيره سيلتقط المشكلة.','وفي حالات أخرى يزيد عدد المراجعين من تشتت المسؤولية ويجعل كل شخص يتوقع أن غيره سيلتقط المشكلة.'),('اقترحت الباحثة اختبارات دورية تدخل حالات معروفة الخطأ وتقيس هل يلتقطها المراجعون.','اقترحت الباحثة اختبارات دورية تتضمن حالات معروفة الخطأ وتقيس ما إذا كان المراجعون يلتقطونها.')],
'ar-c2-u09-p04':[('إذا كوفئت السرعات منفصلة، قد يزيد الخطر الكلي.','إذا كوفئ كل فريق على سرعته منفردًا، قد يزيد الخطر الكلي.')],
'ar-c2-u09-p05':[('قالت اللجنة إن التوقف الذي يكشف مشكلة قبل التوسع نجاح لوظيفة التجربة.','قالت اللجنة إن التوقف الذي يكشف مشكلة قبل التوسع نجاح للتجربة في أداء وظيفتها.')],
'ar-c2-u09-p06':[],
}
META={pid:[('answer q1','assessment_wording','moderate','The current C2 q1 prompt requires a standalone one-sentence summary, but the keyed response is the same nominal phrase reused across six distinct passages; replace it with a complete passage-specific declarative summary of the organizing issue.')] for pid in IDS}
META['ar-c2-u09-p01'].append(('text','naturalness','moderate','The coordination «قاسوا ليس ... فقط، بل ...» is a calque-like negation pattern in MSA; use the idiomatic «لم يقيسوا ... فقط، بل قاسوا ...».'))
META['ar-c2-u09-p02'].append(('text','naturalness','moderate','The adverbial phrase «استخدم الفريق المتوسطات منفصلة» is awkward because the averages are being considered separately; use an idiomatic construction such as «تعامل ... مع المتوسطات على نحو منفصل».'))
META['ar-c2-u09-p03'].extend([('text','naturalness','moderate','The phrase «يزيد عدد المراجعين المسؤولية الموزعة» is semantically and collocationally awkward; express diffusion explicitly as «يزيد ... من تشتت المسؤولية».'),('text','naturalness','moderate','The sequence «اختبارات دورية تدخل حالات ... وتقيس هل» is not idiomatic MSA; tests «تتضمن حالات» and measure «ما إذا» reviewers detect them.')])
META['ar-c2-u09-p04'].append(('text','naturalness','moderate','The phrase «كوفئت السرعات منفصلة» treats speeds themselves as reward recipients and uses an awkward adverbial; state that each team is rewarded separately for speed.'))
META['ar-c2-u09-p05'].append(('text','naturalness','moderate','The phrase «نجاح لوظيفة التجربة» is an unnatural relation in MSA; state that stopping can be a success for the experiment in performing its function.'))
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
 if (p.get('fresh_records_reviewed'),p.get('fresh_records_with_findings'),p.get('fresh_findings'),d.get('open_findings'))!=(348,296,529,1128) or p.get('levels_completed')!=['A1','A2','B1','B2','C1']: raise SystemExit('C2 Unit 9 frontier drift')
 if not (DD/'c2_u08.json').exists() or (DD/'c2_u09.json').exists(): raise SystemExit('decision frontier drift')
 inv=json.loads(INV.read_text()); c2=inv.get('levels',{}).get('c2',{})
 if c2.get('canonical_sha256')!=pre or c2.get('fresh_review_status')!='IN_PROGRESS': raise SystemExit('inventory/hash frontier drift')
 rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]
 if len(rows)!=60 or [rows[i].get('id') for i in range(48,54)]!=IDS: raise SystemExit('C2 Unit 9 layout drift')
 by={r['id']:r for r in rows}; before={pid:targets(by[pid]) for pid in IDS}
 for pid in IDS:
  r=by[pid]; q=r.get('quality',{})
  if q.get('status')!='draft' or q.get('coverage_check')!='pending' or any(q.get(f)!='pending' for f in ('linguistic_review','pedagogical_review','answer_key_check','schema_check')): raise SystemExit(f'{pid}: quality frontier drift')
  qs={x['id']:x for x in r.get('questions',[])}; ans={a['question_id']:a for a in r.get('answer_key',[])}
  if qs.get('q1',{}).get('type')!='summary' or qs.get('q1',{}).get('prompt')!=SUMMARY_PROMPT: raise SystemExit(f'{pid}: q1 summary prompt drift')
  if ans.get('q1',{}).get('answer')!=OLD_SUMMARY: raise SystemExit(f'{pid}/q1: answer drift')
  ans['q1']['answer']=SUMMARIES[pid]
  for old,new in TEXT_REPAIRS[pid]:
   if r.get('text','').count(old)!=1: raise SystemExit(f'{pid}: text repair anchor drift')
   r['text']=r['text'].replace(old,new,1)
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
 if (sum(len(META[x]) for x in IDS),sum(bool(META[x]) for x in IDS))!=(12,6): raise SystemExit('finding metadata drift')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows))
 print(json.dumps({'level':'C2','unit':9,'records_reviewed':6,'records_with_findings':6,'fresh_findings':12,'pre_repair_canonical_sha256':pre,'post_repair_canonical_sha256':sha(PATH.read_bytes())},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
