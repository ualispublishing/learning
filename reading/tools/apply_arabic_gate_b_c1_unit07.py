#!/usr/bin/env python3
"""Apply fresh Arabic Gate B C1 Unit 7 assessment-alignment repairs."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; R=ROOT/'reading'; PATH=R/'arabic/c1/passages.jsonl'; RELEASE=R/'RELEASE_STATUS.json'; INV=R/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; DD=R/'audit/arabic_gate_b_decisions_2026-08-30'
IDS=[f'ar-c1-u07-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-04 fresh Gate B naturalness review (C1 Unit 7): learner-facing prose/Q/A reviewed passage by passage; only high-confidence MSA grammar, idiom, reference, semantic, and assessment-wording repairs applied; no educator/publication release claim.'
Q1_REPAIRS={
'ar-c1-u07-p01':('أنه يثبت معنى واحدًا قبل تتبع جميع مواضع المفتاح وعلاقاتها.','القضية هي أن تثبيت معنى رمزي واحد قبل تتبع جميع مواضع المفتاح وعلاقاتها يجعل القراءة أسرع من الأدلة.'),
'ar-c1-u07-p02':('أنها تربط حالتين وتسمح بقياس التحول من خلال ما تغير في الصياغة.','القضية هي أن صدى المطلع يربط بين حالتين ويتيح قياس التحول من خلال ما تغير في الصياغة من دون حسم سببه النفسي.'),
'ar-c1-u07-p03':('في العلاقات غير المتوقعة بين الأشياء وظلالها وانعكاساتها لا في الأشياء نفسها.','القضية هي أن غرابة العمل تنشأ من العلاقات غير المتوقعة بين الأشياء وظلالها وانعكاساتها لا من الأشياء نفسها.'),
'ar-c1-u07-p04':('تفسر الحنين لكنها تتجاهل تغير الصور وكسر القافية والتوتر المرتبط بالبيت.','القضية هي أن قراءة القصيدة بوصفها حنينًا خالصًا تفسر جانبًا منها لكنها تتجاهل تغير الصور وكسر القافية والتوتر المرتبط بالبيت.'),
'ar-c1-u07-p05':('لأن النص يقدم أدلة متعارضة ولا يثبت توقف الكتابة أو عودتها صراحة.','القضية هي أن ختام النص يرجح بقاء إمكان العودة إلى الكتابة من دون أن يحسم توقفها أو عودتها صراحة.'),
'ar-c1-u07-p06':('فسر أكبر قدر من التفاصيل مع إبقاء قوة الادعاء متناسبة مع الأدلة.','القضية هي بناء قراءة تفسر أكبر قدر من التفاصيل مع إبقاء قوة الادعاء متناسبة مع وزن الأدلة.'),
}
META={pid:[('answer q1','assessment_wording','moderate','The q1 prompt explicitly asks for a one-sentence summary, while the keyed response retains a fragment, causal clause, pronoun without an explicit antecedent, or imperative-like formulation from an earlier task shape; convert it to a complete declarative summary without changing the passage interpretation.')] for pid in IDS}
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
 raw=PATH.read_bytes(); pre=sha(raw); rel=json.loads(RELEASE.read_text()); ar=rel['languages']['arabic']; p=ar['naturalness_review_progress']
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False: raise SystemExit('release gate drift')
 if p.get('fresh_records_reviewed')!=276 or p.get('levels_completed')!=['A1','A2','B1','B2']: raise SystemExit('C1 Unit 7 frontier drift')
 if not (DD/'c1_u06.json').exists() or (DD/'c1_u07.json').exists(): raise SystemExit('decision frontier drift')
 inv=json.loads(INV.read_text()); c1=inv.get('levels',{}).get('c1',{})
 if c1.get('canonical_sha256')!=pre or c1.get('fresh_review_status')!='IN_PROGRESS': raise SystemExit('inventory/hash frontier drift')
 rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]
 if len(rows)!=60 or [rows[i].get('id') for i in range(36,42)]!=IDS: raise SystemExit('C1 Unit 7 layout drift')
 by={r['id']:r for r in rows}; before={pid:targets(by[pid]) for pid in IDS}
 for pid in IDS:
  r=by[pid]; q=r.get('quality',{})
  if q.get('status')!='draft' or q.get('coverage_check')!='pending' or any(q.get(f)!='pending' for f in ('linguistic_review','pedagogical_review','answer_key_check','schema_check')): raise SystemExit(f'{pid}: quality frontier drift')
  qs={x['id']:x for x in r.get('questions',[])}; ans={a['question_id']:a for a in r.get('answer_key',[])}
  if qs.get('q1',{}).get('type')!='summary' or qs.get('q1',{}).get('prompt')!='لخّص في جملة واحدة القضية المركزية التي يعالجها النص.': raise SystemExit(f'{pid}: q1 summary prompt drift')
  old,new=Q1_REPAIRS[pid]
  if ans.get('q1',{}).get('answer')!=old: raise SystemExit(f'{pid}/q1: answer drift')
  ans['q1']['answer']=new
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
 if (sum(len(META[x]) for x in IDS),sum(bool(META[x]) for x in IDS))!=(6,6): raise SystemExit('finding metadata drift')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows))
 print(json.dumps({'level':'C1','unit':7,'records_reviewed':6,'records_with_findings':6,'fresh_findings':6,'pre_repair_canonical_sha256':pre,'post_repair_canonical_sha256':sha(PATH.read_bytes())},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
