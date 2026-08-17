#!/usr/bin/env python3
"""Select 20 unique fresh targets for B2 Unit09 from its persisted probe."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_b2_unit08_frontier_lock.json';PROBE=R/'reading/audit/french_b2_unit09_target_probe.json';OUT=R/'reading/audit/french_b2_unit09_target_selection.json'
SLOTS=[
('p01_budget',['budget','finance','financer','argent','ressource']),('p01_priority',['priorité','besoin','choix','moyen','objectif']),('p01_cost',['dépense','dépenser','payer','prix','coût']),('p01_value',['qualité','quantité','valeur','niveau','limite']),
('p02_income',['revenu','riche','pauvre','impôt','taxe']),('p02_access',['accès','égalité','inégalité','justice','droit']),('p02_support',['soutien','aide','protection','sécurité','responsabilité']),('p02_people',['habitant','employé','employeur','patient','population']),
('p03_program',['programme','mesure','proposition','plan','réforme']),('p03_apply',['appliquer','organiser','maintenir','réviser','limiter']),('p03_improve',['améliorer','développer','augmenter','réduire','remplacer']),('p03_decision',['décision','vote','conseil','comité','autorité']),
('p04_benefit',['avantage','bénéfice','gain','perte','impact']),('p04_opposition',['opposition','désaccord','critique','argument','conflit']),('p04_justify',['justifier','évaluer','comparer','prouver','expliquer']),('p04_trade',['partager','répartir','distribution','distribuer','sacrifier']),
('p05_effective',['efficace','utile','nécessaire','important','possible']),('p05_time',['temporaire','permanent','immédiat','futur','court']),('p05_estimate',['estimer','calculer','mesurer','observer','prévoir']),('p05_revision',['réviser','remplacer','offrir','recevoir','prendre'])]
def main():
 if not LOCK.exists():raise AssertionError('Unit08 lock missing; Unit09 selection must not run early')
 lock=json.loads(LOCK.read_text(encoding='utf-8'));probe=json.loads(PROBE.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=48 or blob!=lock.get('canonical_blob'):raise AssertionError('Unit08 lock/live B2 mismatch')
 if probe.get('status')!='PASS' or probe.get('b2_source_blob')!=blob:raise AssertionError('Unit09 probe missing/stale')
 fresh_list=probe.get('fresh',[]);fresh={x['form']:x for x in fresh_list}
 if len(fresh)<20:raise AssertionError(f'Unit09 probe has only {len(fresh)} fresh candidates; need 20')
 used=set();selected=[];fallbacks=[]
 for slot,candidates in SLOTS:
  hit=next((f for f in candidates if f in fresh and f not in used),None);fallback=False
  if hit is None:
   hit=next((x['form'] for x in fresh_list if x['form'] not in used),None);fallback=True
  if hit is None:raise AssertionError(f'No unused fresh Unit09 target for {slot}')
  used.add(hit);item=dict(fresh[hit]);item['slot']=slot;item['semantic_fallback']=fallback;selected.append(item)
  if fallback:fallbacks.append({'slot':slot,'form':hit,'preferred_candidates':candidates})
 groups={k:[x for x in selected if x['slot'].startswith(k+'_')] for k in ['p01','p02','p03','p04','p05']}
 if len(selected)!=20 or len(used)!=20 or any(len(v)!=4 for v in groups.values()):raise AssertionError('Unit09 selection structure failure')
 out={'status':'PASS','scope':'French B2 Unit 09 target selection','theme':'public policy and trade-offs','b2_source_blob':blob,'selected_count':20,'selected':selected,'passage_groups':{k:[x['form'] for x in v] for k,v in groups.items()},'semantic_fallback_count':len(fallbacks),'semantic_fallbacks':fallbacks,'note':'Deterministic selection from persisted Unit09 freshness probe; fallbacks explicitly audited; not generation approval.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
