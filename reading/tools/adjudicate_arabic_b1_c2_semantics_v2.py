#!/usr/bin/env python3
import json,re,subprocess
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEVELS=('b1','b2','c1','c2')
CAND=ROOT/'reading/audit/arabic_b1_c2_semantic_candidates_2026-08-23'
OUT=ROOT/'reading/audit/arabic_b1_c2_semantic_adjudication_v2_2026-08-23.json'
SUMMARY=ROOT/'reading/audit/arabic_b1_c2_semantic_adjudication_v2_summary_2026-08-23.md'
PATHS={l:ROOT/f'reading/arabic/{l}/passages.jsonl' for l in LEVELS}
EXPECTED={'b1':'cbe9e70e07543c3ce9080fb375af6468cfbd2d3c','b2':'a9486b2c38dc53661143e734c9797cd26fa1f742','c1':'3f68da825c50c3018f9e054cbeec27ba01b17be0','c2':'b8e78e2a8dce942e87ef627a8436f1c8571f9d43'}
QUOTE=re.compile(r'«([^»]+)»')
FUNCTION=re.compile(r'(?:ما\s+وظيفة|ما\s+دور)')
EFFECT=re.compile(r'(?:كيف|لماذا|ماذا\s+يضيف|ما\s+الأثر|ما\s+الفرق|كيف\s+يساعد|ماذا\s+يوحي|ماذا\s+يشير)')
RHETORICAL_REFERENT=re.compile(r'(?:الأمثلة|المثال|المقارنة|السيناريو|التفسير|الدليل|الأدلة|الطبقات|الفقرة|الخاتمة|الافتتاح|الانتقال|السؤال|الأسئلة|العنوان|الصياغة|الاعتراض|الاحتمال|البديل|الملاحظة|التفصيل|التفاصيل|الحالة|الحالات)')
GRAMMAR_TYPES={'grammar_function','grammar_in_context','grammar_category','person_form','morphology_label','syntax_label'}

def blob(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def load(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def awc(a):return len(str(a or '').split())
def quote_grounding(prompt,text):
 qs=[q.strip() for q in QUOTE.findall(str(prompt or '')) if q.strip()]
 hits=[q for q in qs if q in str(text or '')]
 return {'quoted_fragments':qs,'grounded_fragments':hits,'has_grounded_quote':bool(hits),'all_quotes_grounded':bool(qs) and len(hits)==len(qs)}
def classify(c):
 p=str(c.get('prompt') or '');a=str(c.get('answer') or '');typ=c.get('type');n=awc(a);g=quote_grounding(p,c.get('text',''))
 if typ in {'grammar_category','person_form','morphology_label','syntax_label'}:
  return 'REPAIR_LABEL_TRIVIA',g
 if typ in {'grammar_function','grammar_in_context'}:
  if n<5:return 'REVIEW_SHORT_LANGUAGE_FUNCTION_ANSWER',g
  if QUOTE.search(p) and not g['has_grounded_quote']:return 'REVIEW_UNGROUNDED_QUOTED_LANGUAGE_ITEM',g
  return 'PASS_CONTEXTUAL_LANGUAGE_FUNCTION',g
 if FUNCTION.search(p) and RHETORICAL_REFERENT.search(p):
  if n<4:return 'REVIEW_SHORT_RHETORICAL_ROLE_ANSWER',g
  return 'PASS_RHETORICAL_DISCOURSE_ROLE',g
 if EFFECT.search(p):return 'PASS_MEANING_OR_DISCOURSE_EFFECT',g
 if FUNCTION.search(p):
  if n>=5:return 'PASS_CONTEXTUAL_FUNCTION_NONLABEL',g
  return 'REVIEW_AMBIGUOUS_FUNCTION_PROMPT',g
 return 'PASS_CONTEXTUAL_SEMANTIC_ANALYSIS',g

def main():
 actual={l:blob(p) for l,p in PATHS.items()}
 if actual!=EXPECTED:raise SystemExit(f'unexpected current blobs {actual}')
 decisions=[];counts=Counter();per=Counter();review=[];repair=[]
 for level in LEVELS:
  d=json.loads((CAND/f'{level}.json').read_text(encoding='utf-8'))
  for c in d.get('candidates',[]):
   dec,g=classify(c);x={k:c.get(k) for k in ('level','passage_id','unit','sequence','title','question_id','type','prompt','answer','explanation','target_ids')};x['answer_word_count']=awc(c.get('answer'));x['grounding']=g;x['decision']=dec
   decisions.append(x);counts[dec]+=1;per[(level,dec)]+=1
   if dec.startswith('REVIEW_'):review.append(x)
   if dec.startswith('REPAIR_'):repair.append(x)
 out={'schema_version':2,'date':'2026-08-23','scope':'Arabic B1-C2 semantic adjudication for grammar/discourse candidates','input_blobs':actual,'candidate_count':len(decisions),'decision_counts':dict(counts),'level_decision_counts':{l:{d:n for (ll,d),n in per.items() if ll==l} for l in LEVELS},'pass_count':sum(n for d,n in counts.items() if d.startswith('PASS_')),'review_count':len(review),'repair_count':len(repair),'review_items':review,'repair_items':repair,'decisions':decisions,'policy':{'B1-C2':'Contextual analysis of connectives, discourse relations, rhetorical roles, evidence structure, and counterfactual/conditional meaning is CEFR-appropriate when grounded and explained propositionally. Isolated grammatical-label recall remains a repair candidate.','short_answer_threshold':'Language-function answers under 5 whitespace tokens and rhetorical-role answers under 4 are held for manual review, not auto-failed.','quote_grounding':'Quoted language-function questions must have at least one quoted fragment grounded verbatim in the passage; otherwise manual review.'},'quality_promotion':False}
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 lines=['# Arabic B1-C2 semantic adjudication v2','',f"Total candidates: **{len(decisions)}**",f"Pass: **{out['pass_count']}** · Manual review: **{len(review)}** · Repair: **{len(repair)}**",'','| Decision | Count |','|---|---:|']
 for d,n in counts.most_common():lines.append(f'| {d} | {n} |')
 if review:
  lines+=['','## Manual-review remainder','','| Level | Passage | Q | Type | Prompt | Answer |','|---|---|---|---|---|---|']
  for x in review:lines.append(f"| {x['level'].upper()} | {x['passage_id']} | {x['question_id']} | {x['type']} | {str(x['prompt']).replace('|','\\|')} | {str(x['answer']).replace('|','\\|')} |")
 if repair:
  lines+=['','## Direct repair candidates','','| Level | Passage | Q | Type | Prompt | Answer |','|---|---|---|---|---|---|']
  for x in repair:lines.append(f"| {x['level'].upper()} | {x['passage_id']} | {x['question_id']} | {x['type']} | {str(x['prompt']).replace('|','\\|')} | {str(x['answer']).replace('|','\\|')} |")
 SUMMARY.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 print(json.dumps({'candidate_count':len(decisions),'decision_counts':dict(counts),'pass':out['pass_count'],'review':len(review),'repair':len(repair)},ensure_ascii=False))
if __name__=='__main__':main()
