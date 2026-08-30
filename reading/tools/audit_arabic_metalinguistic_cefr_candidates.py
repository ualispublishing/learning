#!/usr/bin/env python3
"""Inventory current Arabic metalinguistic/CEFR question candidates without editing content."""
from __future__ import annotations
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / 'reading'
OUT = READING / 'audit' / 'arabic_metalinguistic_cefr_candidate_inventory_2026-08-30.json'
LEVELS = ('a1','a2','b1','b2','c1','c2')
FORMAL_TYPES = {'grammar_category','grammar_function','grammar_identification','person_form'}
PATTERNS = {
    'grammatical_classification': re.compile(r'التصنيف\s+النحوي|الوظيفة\s+النحوية'),
    'explicit_word_function': re.compile(r'ما\s+وظيفة\s+«'),
    'explicit_word_type': re.compile(r'ما\s+نوع\s+(?:«|كلمة)'),
    'verb_owner': re.compile(r'من\s+صاحب\s+الفعل'),
    'number_form_label': re.compile(r'ما\s+صيغة\s+العدد'),
    'negation_label': re.compile(r'ما\s+الكلمة\s+التي\s+تنفي\s+الفعل'),
}
A2_EXCLUSIONS = {('ar-a2-u01-p02','q4'),('ar-a2-u09-p06','q10'),('ar-a2-u10-p06','q9')}


def main():
    a2_audit = json.loads((READING/'audit'/'arabic_a2_metalinguistic_repair_2026-08-30.json').read_text(encoding='utf-8'))
    bound = {(x['passage_id'],x['question_id']) for x in a2_audit['adjudicated_false_positives']}
    if bound != A2_EXCLUSIONS:
        raise SystemExit(f'A2 exclusion binding drift: {bound}')
    candidates=[]
    per_level={}
    total_q=0
    for level in LEVELS:
        rows=[json.loads(x) for x in (READING/'arabic'/level/'passages.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
        if len(rows)!=60:
            raise SystemExit(f'{level}: expected 60 records, found {len(rows)}')
        counts=Counter()
        level_candidates=[]
        q_count=0
        for r in rows:
            for q in r.get('questions',[]):
                q_count+=1
                typ=q.get('type','missing')
                counts[typ]+=1
                prompt=q.get('prompt','')
                reasons=[]
                if typ in FORMAL_TYPES:
                    reasons.append(f'formal_type:{typ}')
                for name,pat in PATTERNS.items():
                    if pat.search(prompt): reasons.append(f'prompt_pattern:{name}')
                if reasons:
                    key=(r['id'],q['id'])
                    status='adjudicated_false_positive' if key in A2_EXCLUSIONS else 'needs_adjudication'
                    item={'level':level.upper(),'unit':r.get('unit'),'sequence':r.get('sequence'),'passage_id':r['id'],'question_id':q['id'],'type':typ,'prompt':prompt,'reasons':reasons,'status':status}
                    candidates.append(item); level_candidates.append(item)
        if q_count!=600:
            raise SystemExit(f'{level}: expected 600 questions, found {q_count}')
        total_q+=q_count
        per_level[level]={'records':60,'questions':q_count,'question_type_counts':dict(sorted(counts.items())),'candidate_count':len(level_candidates),'needs_adjudication':sum(x['status']=='needs_adjudication' for x in level_candidates),'adjudicated_false_positives':sum(x['status']=='adjudicated_false_positive' for x in level_candidates)}
    audit={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','date':'2026-08-30','scope':'Fresh 100%-question inventory of legacy formal question types and configured explicit metalinguistic prompt patterns across Arabic A1-C2; read-only candidate detection, not semantic approval.','records':360,'questions':total_q,'levels':per_level,'candidate_count':len(candidates),'needs_adjudication':sum(x['status']=='needs_adjudication' for x in candidates),'adjudicated_false_positives':sum(x['status']=='adjudicated_false_positive' for x in candidates),'candidates':candidates,'release_claim':False,'interpretation':'Candidates require contextual adjudication. A type/pattern hit is not automatically a defect, especially at higher CEFR levels where discourse or grammatical analysis can be pedagogically legitimate.'}
    OUT.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in audit.items() if k!='candidates'},ensure_ascii=False,indent=2))

if __name__=='__main__': main()
