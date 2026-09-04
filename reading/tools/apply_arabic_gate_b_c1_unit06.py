#!/usr/bin/env python3
"""Apply fresh Arabic Gate B C1 Unit 6 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; R=ROOT/'reading'; PATH=R/'arabic/c1/passages.jsonl'; RELEASE=R/'RELEASE_STATUS.json'; INV=R/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; DD=R/'audit/arabic_gate_b_decisions_2026-08-30'
IDS=[f'ar-c1-u06-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-04 fresh Gate B naturalness review (C1 Unit 6): learner-facing prose/Q/A reviewed passage by passage; only high-confidence MSA grammar, idiom, reference, semantic, and assessment-wording repairs applied; no educator/publication release claim.'
QA_REPAIRS={
 'ar-c1-u06-p01':{'q1':('هل ذكر القاعة قيد مكاني مقصود أم وصف للوسيلة التي كانت متاحة لتحقيق حق المشاركة.','القضية هي ما إذا كان ذكر القاعة قيدًا مكانيًا مقصودًا أم وصفًا للوسيلة التي كانت متاحة لتحقيق حق المشاركة.')},
 'ar-c1-u06-p02':{'q7':('لأن ليس كل فرق في النتائج ناشئًا من عائق مؤسسي ذي صلة أو قابل للتعديل.','لأن كل فرق في النتائج ليس بالضرورة ناشئًا من عائق مؤسسي ذي صلة أو قابل للتعديل.')},
 'ar-c1-u06-p04':{'q1':('لأن اللجنة الأدنى قد لا تملك سلطة مخالفة ضمان وضعه الميثاق الأعلى.','القضية هي أن الجهة الأدنى قد لا تملك سلطة مخالفة ضمان وضعه الميثاق الأعلى.')},
 'ar-c1-u06-p05':{'q1':('لأن المطلوب تقييم نطاق الإجراء وفعاليته وبدائله وعبئه لا اختيار أقصى حل أو عدم فعل شيء.','القضية هي تقييم نطاق الإجراء وفعاليته وبدائله وعبئه بدل الاختيار بين أقصى حل وعدم فعل شيء.')},
 'ar-c1-u06-p06':{'q1':('معنى النص، وسلطة تطبيقه أو تغييره، والإجراءات التي تحمي المصالح المتعارضة.','القضية هي الجمع بين معنى النص وسلطة تطبيقه أو تغييره والإجراءات التي تحمي المصالح المتعارضة.')},
}
META={
 'ar-c1-u06-p01':[("answer q1","assessment_wording","moderate","The keyed summary is phrased as a bare question rather than a one-sentence summary of the central interpretive issue; convert it to a declarative summary.")],
 'ar-c1-u06-p02':[("answer q7","grammar_wording","moderate","لأن ليس كل فرق is awkward clause ordering; state directly that not every outcome difference necessarily arises from a relevant modifiable institutional barrier.")],
 'ar-c1-u06-p03':[],
 'ar-c1-u06-p04':[("answer q1","assessment_wording","moderate","The keyed response begins with لأن despite q1 asking for a one-sentence central summary; state the hierarchy issue directly and use الجهة الأدنى for the lower-level body.")],
 'ar-c1-u06-p05':[("answer q1","assessment_wording","moderate","The keyed response begins as a causal explanation rather than a summary; state the proportionality issue directly as evaluation of scope, effectiveness, alternatives, and burden.")],
 'ar-c1-u06-p06':[("answer q1","assessment_wording","moderate","The keyed answer is a noun-list fragment rather than a one-sentence summary; express the integration of meaning, authority, and procedure as a complete sentence.")],
}
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
 if p.get('fresh_records_reviewed')!=270 or p.get('levels_completed')!=['A1','A2','B1','B2']: raise SystemExit('C1 Unit 6 frontier drift')
 if not (DD/'c1_u05.json').exists() or (DD/'c1_u06.json').exists(): raise SystemExit('decision frontier drift')
 inv=json.loads(INV.read_text()); c1=inv.get('levels',{}).get('c1',{})
 if c1.get('canonical_sha256')!=pre or c1.get('fresh_review_status')!='IN_PROGRESS': raise SystemExit('inventory/hash frontier drift')
 rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]
 if len(rows)!=60 or [rows[i].get('id') for i in range(30,36)]!=IDS: raise SystemExit('C1 Unit 6 layout drift')
 by={r['id']:r for r in rows}; before={pid:targets(by[pid]) for pid in IDS}
 for pid in IDS:
  r=by[pid]; q=r.get('quality',{})
  if q.get('status')!='draft' or q.get('coverage_check')!='pending' or any(q.get(f)!='pending' for f in ('linguistic_review','pedagogical_review','answer_key_check','schema_check')): raise SystemExit(f'{pid}: quality frontier drift')
  ans={a['question_id']:a for a in r.get('answer_key',[])}
  for qid,(old,new) in QA_REPAIRS.get(pid,{}).items():
   if qid not in ans or ans[qid].get('answer')!=old: raise SystemExit(f'{pid}/{qid}: answer drift')
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
 if (sum(len(META[x]) for x in IDS),sum(bool(META[x]) for x in IDS))!=(5,5): raise SystemExit('finding metadata drift')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows))
 print(json.dumps({'level':'C1','unit':6,'records_reviewed':6,'records_with_findings':5,'fresh_findings':5,'pre_repair_canonical_sha256':pre,'post_repair_canonical_sha256':sha(PATH.read_bytes())},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
