#!/usr/bin/env python3
"""Final Arabic review pass 12: adversarial cross-gate falsification.

This pass does not try to prove the corpus is good. It tries to disprove prior
clean claims by cross-checking final artifacts and direct corpus invariants. A
BLOCKED result is expected while any substantive review gate remains open.
"""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
OUT=ROOT/'reading/audit/final_arabic_pass12_adversarial_gate_falsification.json'
ART={
 'pass01':'reading/audit/final_arabic_pass01_data_integrity.json',
 'pass02':'reading/audit/final_arabic_pass02_lexical_exposure_integrity.json',
 'pass03':'reading/audit/final_arabic_pass03_question_composition.json',
 'pass05':'reading/audit/final_arabic_pass05_script_orthography_hygiene.json',
 'pass06':'reading/audit/final_arabic_pass06_lexical_source_identity.json',
 'pass07':'reading/audit/final_arabic_pass07_cefr_difficulty_calibration.json',
 'pass08':'reading/audit/final_arabic_pass08_continuity_duplicate_balance.json',
 'pass09':'reading/audit/final_arabic_pass09_fluency_checkpoint.json',
 'pass10':'reading/audit/final_arabic_pass10_adjudication.json',
 'pass11':'reading/audit/final_arabic_pass11_naturalness_review.json',
}
LATIN=re.compile(r'[A-Za-z]')
BANNED_IDS={'ar-r800','ar-r913','ar-r998','ar-r986','ar-r2063'}

def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def main():
 hard=[];blockers=[];evidence={k:load(v) for k,v in ART.items()}
 # Re-falsify clean mechanical gates rather than trusting status strings alone.
 expected_clean={'pass01':'PASS','pass02':'PASS','pass05':'PASS','pass06':'PASS','pass08':'PASS','pass09':'PASS'}
 for key,status in expected_clean.items():
  actual=evidence[key].get('status')
  if actual!=status:hard.append({'code':'claimed_clean_gate_not_clean','gate':key,'expected':status,'actual':actual})
 if evidence['pass10'].get('status')!='PASS_WITH_SOURCE_ADJUDICATION' or evidence['pass10'].get('unresolved'):
  hard.append({'code':'pass10_adjudication_not_closed','status':evidence['pass10'].get('status'),'unresolved':evidence['pass10'].get('unresolved')})
 rows=[];seen=set();latin_hits=[];banned_hits=[]
 for level in LEVELS:
  p=ROOT/f'reading/arabic/{level}/passages.jsonl'
  level_rows=[json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
  if len(level_rows)!=60:hard.append({'code':'direct_level_count_changed','level':level,'actual':len(level_rows)})
  rows.extend(level_rows)
  for r in level_rows:
   if r['id'] in seen:hard.append({'code':'direct_duplicate_id','passage_id':r['id']})
   seen.add(r['id'])
   reader_fields=[r.get('title',''),r.get('text','')]
   reader_fields += [q.get('prompt','') for q in r.get('questions',[]) if isinstance(q,dict)]
   reader_fields += [a.get('answer','') for a in r.get('answer_key',[]) if isinstance(a,dict)]
   if any(LATIN.search(str(v or '')) for v in reader_fields):latin_hits.append(r['id'])
   for t in [*r.get('new_lexical_targets',[]),*r.get('review_lexical_targets',[])]:
    if isinstance(t,dict) and t.get('id') in BANNED_IDS:banned_hits.append({'passage_id':r['id'],'where':'lexical','target_id':t.get('id')})
   for q in r.get('questions',[]):
    for tid in q.get('target_ids',[]) if isinstance(q,dict) and isinstance(q.get('target_ids'),list) else []:
     if tid in BANNED_IDS:banned_hits.append({'passage_id':r['id'],'where':'question','question_id':q.get('id'),'target_id':tid})
 if len(rows)!=360:hard.append({'code':'direct_total_passage_count_changed','actual':len(rows)})
 if latin_hits:hard.append({'code':'latin_reader_content_reappeared','passage_ids':sorted(set(latin_hits))})
 if banned_hits:hard.append({'code':'known_bad_lexical_ids_reappeared','hits':banned_hits})
 # Independently recheck each P6 has zero deliberate new targets.
 p6_bad=[]
 for r in rows:
  if str(r['id']).endswith('-p06') and r.get('new_lexical_targets'):p6_bad.append({'passage_id':r['id'],'target_ids':[t.get('id') for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)]})
 if p6_bad:hard.append({'code':'p6_new_targets_reappeared','hits':p6_bad})
 # Substantive blockers: intentionally do not convert REVIEW_REQUIRED into failure
 # of the audit machinery; they block final approval.
 if evidence['pass03'].get('status')!='PASS':blockers.append({'gate':'pass03_question_composition','status':evidence['pass03'].get('status'),'reason':'documented question-distribution defaults remain underrepresented, especially B1-C2 grammar/style and synthesis'})
 if evidence['pass07'].get('status')!='PASS':blockers.append({'gate':'pass07_cefr_difficulty','status':evidence['pass07'].get('status'),'reason':'length calibration and known-token coverage remain unresolved; B1-C2 are materially below written production bands'})
 if evidence['pass11'].get('status')!='PASS':blockers.append({'gate':'pass11_manual_naturalness','status':evidence['pass11'].get('status'),'reason':'manual naturalness review is complete only for A1; A2-C2 remain pending'})
 payload={
  'pass':12,'name':'adversarial_cross_gate_falsification','scope':'Arabic A1-C2 canonical reading corpus',
  'method':'directly re-check clean mechanical claims and deliberately refuse final approval while any independent substantive gate is unresolved',
  'direct_checks':{'passages':len(rows),'unique_ids':len(seen),'latin_reader_passages':len(set(latin_hits)),'known_bad_id_hits':len(banned_hits),'p6_with_new_targets':len(p6_bad)},
  'hard_regressions':hard,'final_approval_blockers':blockers,
  'status':'FAIL_REGRESSION' if hard else ('BLOCKED' if blockers else 'PASS'),
  'final_approval':not hard and not blockers,
 }
 OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'hard_regressions':len(hard),'blockers':len(blockers),'status':payload['status']},ensure_ascii=False));print('status='+payload['status'])
 if hard:raise SystemExit(1)
if __name__=='__main__':main()
