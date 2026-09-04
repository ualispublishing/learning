#!/usr/bin/env python3
"""Apply fresh Arabic Gate B C1 Unit 4 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'
PATH=READING/'arabic/c1/passages.jsonl'; RELEASE=READING/'RELEASE_STATUS.json'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; DECISION_DIR=READING/'audit/arabic_gate_b_decisions_2026-08-30'
EXPECTED_IDS=[f'ar-c1-u04-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-04 fresh Gate B naturalness review (C1 Unit 4): learner-facing prose/Q/A reviewed passage by passage; only high-confidence MSA grammar, idiom, reference, semantic, and assessment-wording repairs applied; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-c1-u04-p03':[(
  'كما انتبهوا إلى أن قد يؤدي قبول التسجيل نفسه إلى اختيار متحدثين أكثر راحة مع الباحث أو التقنية.',
  'كما انتبهوا إلى أن قبول التسجيل نفسه قد يؤدي إلى اختيار متحدثين أكثر راحة مع الباحث أو التقنية.'
 )],
 'ar-c1-u04-p06':[(
  'لذلك يجب أن نسأل في كل مرة: من يتكلم؟ مع من؟ في أي غرض؟ عبر أي وسيط؟ ومن الذي سمى النمط؟ وما الذي يتغير إذا تغير أحد هذه الشروط؟',
  'لذلك يجب أن نسأل في كل مرة: من يتكلم؟ مع من؟ لأي غرض؟ عبر أي وسيط؟ ومن الذي سمى النمط؟ وما الذي يتغير إذا تغير أحد هذه الشروط؟'
 ),(
  'كذلك لا يمثل النص السمعي والنثر المكتوب الشيء نفسه؛ التحويل بينهما يضيف قرارات عن ما يحذف وما يبقى.',
  'كذلك لا يمثل النص السمعي والنثر المكتوب الشيء نفسه؛ التحويل بينهما يضيف قرارات عمّا يُحذف وما يبقى.'
 )],
}
QA_REPAIRS={
 'ar-c1-u04-p04':{'answers':{
  'q1':('لأن الأولى تحفظ خصائص الأداء والثانية تسهل القراءة، ولكل منهما وظيفة مختلفة.','القضية هي الموازنة بين حفظ خصائص الأداء في التفريغ وتسهيل القراءة في النسخة المحررة بحسب الغرض.'),
  'q5':('يربط مستوى التفريغ بالغرض، ويحفظ طريق الرجوع إلى التسجيل، ويعلن قرارات الترقيم والحذف حتى يعرف القارئ ما الذي نقل وما الذي فسره المحرر.','يربط مستوى التفريغ بالغرض، ويحفظ طريق الرجوع إلى التسجيل، ويعلن قرارات الترقيم والحذف حتى يعرف القارئ ما الذي نُقل وما الذي فسّره المحرر.')
 }},
 'ar-c1-u04-p05':{'answers':{
  'q6':('الأول قد يغير الشكل مع حفظ الكلمة، والثاني قد يغير اختيار الكاتب ومعناه أو زمنه.','الأول قد يغير الشكل مع حفظ الكلمة، أما الثاني فقد يغير اختيار الكاتب للمفردات وما تحمله من معنى أو دلالة زمنية.')
 }},
}
FINDING_META={
 'ar-c1-u04-p01':[],
 'ar-c1-u04-p02':[],
 'ar-c1-u04-p03':[("text","grammar_wording","moderate","أن قد يؤدي قبول التسجيل is malformed clause structure; place the nominal subject directly after أن and the modal verb after it.")],
 'ar-c1-u04-p04':[("answer q1","assessment_wording","moderate","The keyed answer gives only a causal contrast although q1 asks for a one-sentence statement of the central issue; state the transcription-versus-readability trade-off directly."),("answer q5","reference_clarity","moderate","ما الذي نقل leaves the agent/reference ambiguous; distinguish what was transferred from what the editor interpreted using a passive form for the source material.")],
 'ar-c1-u04-p05':[("answer q6","reference_clarity","moderate","اختيار الكاتب ومعناه أو زمنه has unclear pronoun reference; specify that lexical replacement can alter the writer's word choice and its semantic or temporal signal.")],
 'ar-c1-u04-p06':[("text","grammar_wording","moderate","في أي غرض is the wrong preposition for asking purpose; use لأي غرض, matching standard MSA and the keyed answer."),("text","grammar_wording","moderate","عن ما يحذف should contract to عمّا and the passive form clarifies that the editorial decision concerns what is omitted.")],
}
def sha(b): return hashlib.sha256(b).hexdigest()
def wc(t): return len(TOKEN.findall(t))
def target_counts(r):
 forms=[]
 for field in ('new_lexical_targets','review_lexical_targets'):
  for item in r.get(field,[]):
   f=item.get('form')
   if isinstance(f,str) and f and f not in forms: forms.append(f)
 text=r.get('text',''); return {f:text.count(f) for f in forms}
def main():
 raw=PATH.read_bytes(); pre_sha=sha(raw); rel=json.loads(RELEASE.read_text()); ar=rel['languages']['arabic']; p=ar['naturalness_review_progress']
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False: raise SystemExit('Arabic release gate drift')
 if p.get('fresh_records_reviewed')!=258: raise SystemExit(f"expected 258 reviewed before C1 Unit 4, got {p.get('fresh_records_reviewed')!r}")
 if p.get('levels_completed')!=['A1','A2','B1','B2']: raise SystemExit('completed-level frontier drift')
 if not (DECISION_DIR/'c1_u03.json').exists() or (DECISION_DIR/'c1_u04.json').exists(): raise SystemExit('C1 Unit 4 decision frontier drift')
 inv=json.loads(INVENTORY.read_text()); c1=inv.get('levels',{}).get('c1',{})
 if c1.get('canonical_sha256')!=pre_sha or c1.get('fresh_review_status')!='IN_PROGRESS': raise SystemExit('C1 inventory/hash frontier drift')
 rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)): raise SystemExit('C1 corpus layout/sequence drift')
 if [rows[i].get('id') for i in range(18,24)]!=EXPECTED_IDS: raise SystemExit('C1 Unit 4 id/frontier drift')
 by={r['id']:r for r in rows}; before={pid:target_counts(by[pid]) for pid in EXPECTED_IDS}
 for pid in EXPECTED_IDS:
  r=by[pid]; q=r.get('quality',{})
  if q.get('status')!='draft' or q.get('coverage_check')!='pending': raise SystemExit(f'{pid}: release/coverage state drift')
  for f in ('linguistic_review','pedagogical_review','answer_key_check','schema_check'):
   if q.get(f)!='pending': raise SystemExit(f'{pid}: expected pending {f}')
  for old,new in TEXT_REPAIRS.get(pid,[]):
   if r.get('text','').count(old)!=1: raise SystemExit(f'{pid}: text source drift: {old!r}')
   r['text']=r['text'].replace(old,new,1)
  qs={x['id']:x for x in r.get('questions',[])}; ans={x['question_id']:x for x in r.get('answer_key',[])}; repair=QA_REPAIRS.get(pid,{})
  for qid,(old,new) in repair.get('questions',{}).items():
   if qid not in qs or qs[qid].get('prompt')!=old: raise SystemExit(f'{pid}/{qid}: question drift')
   qs[qid]['prompt']=new
  for qid,(old,new) in repair.get('answers',{}).items():
   if qid not in ans or ans[qid].get('answer')!=old: raise SystemExit(f'{pid}/{qid}: answer drift')
   ans[qid]['answer']=new
  r['word_count']=wc(r['text'])
  if not 500<=r['word_count']<=800: raise SystemExit(f"{pid}: word count {r['word_count']} outside C1 band")
  if target_counts(r)!=before[pid]: raise SystemExit(f'{pid}: lexical target occurrence drift')
  if len(r.get('questions',[]))!=10 or len(r.get('answer_key',[]))!=10: raise SystemExit(f'{pid}: 10Q/10A invariant failed')
  aid={a['id']:a for a in r['answer_key']}
  for question in r['questions']:
   a=question.get('answer_id')
   if a not in aid or aid[a].get('question_id')!=question.get('id'): raise SystemExit(f"{pid}: answer linkage drift at {question.get('id')}")
  r['revision']=int(r.get('revision',0) or 0)+1; q=r.setdefault('quality',{})
  for f in ('linguistic_review','pedagogical_review','answer_key_check','schema_check'): q[f]='pass'
  if NOTE not in q.setdefault('notes',[]): q['notes'].append(NOTE)
 total=sum(len(FINDING_META[x]) for x in EXPECTED_IDS); withf=sum(bool(FINDING_META[x]) for x in EXPECTED_IDS)
 if (total,withf)!=(6,4): raise SystemExit(f'finding metadata drift: {total}/{withf}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows))
 print(json.dumps({'level':'C1','unit':4,'records_reviewed':6,'records_with_findings':withf,'fresh_findings':total,'pre_repair_canonical_sha256':pre_sha,'post_repair_canonical_sha256':sha(PATH.read_bytes())},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
