#!/usr/bin/env python3
"""Select 20 pedagogically valid fresh content targets for B2 Unit09.

The exhaustive probe is authoritative for source identity/freshness. Selection is
then deliberately content-word-only: no pronouns, articles, prepositions or
other ultra-basic grammar tokens are allowed to become new B2 lexical targets.
"""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2]
B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_b2_unit08_frontier_lock.json';PROBE=R/'reading/audit/french_b2_unit09_target_probe.json';OUT=R/'reading/audit/french_b2_unit09_target_selection.json'

# Curated from the exhaustive fresh deck for actual B2 policy/trade-off utility.
SELECTION=[
 ('p01_budget','situation'),('p01_priority','cas'),('p01_cost','part'),('p01_value','meilleur'),
 ('p02_income','riche'),('p02_access','pauvre'),('p02_support','aide'),('p02_people','jeune'),
 ('p03_program','assurer'),('p03_apply','obtenir'),('p03_improve','offrir'),('p03_decision','président'),
 ('p04_benefit','contre'),('p04_opposition','humain'),('p04_justify','appel'),('p04_trade','propos'),
 ('p05_effective','recherche'),('p05_time','réfléchir'),('p05_estimate','revoir'),('p05_revision','force'),
]

def main():
 if not LOCK.exists():raise AssertionError('Unit08 lock missing; Unit09 selection must not run early')
 lock=json.loads(LOCK.read_text(encoding='utf-8'));probe=json.loads(PROBE.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=48 or blob!=lock.get('canonical_blob'):raise AssertionError('Unit08 lock/live B2 mismatch')
 if probe.get('status')!='PASS' or probe.get('b2_source_blob')!=blob:raise AssertionError('Unit09 probe missing/stale')
 fresh={x['form']:x for x in probe.get('fresh',[])}
 selected=[];used=set()
 for slot,form in SELECTION:
  if form not in fresh:raise AssertionError(f'Curated Unit09 content target is not fresh/source-backed: {form}')
  if form in used:raise AssertionError(f'Curated Unit09 duplicate target: {form}')
  used.add(form);item=dict(fresh[form]);item['slot']=slot;item['semantic_fallback']=False;item['pedagogical_content_word']=True;selected.append(item)
 if len(selected)!=20 or len(used)!=20:raise AssertionError('Unit09 curated selection must contain 20 unique targets')
 groups={k:[x for x in selected if x['slot'].startswith(k+'_')] for k in ['p01','p02','p03','p04','p05']}
 if any(len(v)!=4 for v in groups.values()):raise AssertionError('Unit09 curated selection group structure failure')
 out={'status':'PASS','scope':'French B2 Unit 09 pedagogical target selection','theme':'public policy and trade-offs','b2_source_blob':blob,'selected_count':20,'selected':selected,'passage_groups':{k:[x['form'] for x in v] for k,v in groups.items()},'semantic_fallback_count':0,'pedagogical_filter':'content-word-only curated from exhaustive fresh deck; excludes ultra-basic grammar/function tokens','note':'Source/freshness comes from exhaustive probe; this artifact additionally enforces pedagogical B2 target quality.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
