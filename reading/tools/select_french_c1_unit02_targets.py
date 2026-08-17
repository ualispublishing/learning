#!/usr/bin/env python3
"""Select 20 fresh source-backed targets for French C1 Unit02.

Requires the calibrated Unit01 lock, canonical Unit02 plan and exhaustive Unit02
freshness probe. Uses the accepted C1 default of four new targets per standard
passage as a default, never a hard quota.
"""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_c1_unit01_frontier_lock.json';PLAN=R/'reading/audit/french_c1_unit02_plan.json';PROBE=R/'reading/audit/french_c1_unit02_target_probe.json';OUT=R/'reading/audit/french_c1_unit02_target_selection.json'
SLOTS=[
('p01_frame',['définir','définition','concept','notion','terme','cadre']),('p01_claim',['conclure','conclusion','affirmer','proposer','soutenir','montrer']),('p01_scope',['portée','condition','limite','exception','contexte','général']),('p01_qualify',['nuance','probable','incertain','précis','relatif','degré']),
('p02_method',['méthode','procédure','processus','approche','technique','mesure']),('p02_evidence',['donnée','indice','élément','preuve','résultat','observation']),('p02_compare',['comparaison','comparer','différence','variation','relation','écart']),('p02_uncertainty',['incertitude','doute','risque','erreur','estimation','prévision']),
('p03_view',['perspective','position','angle','point','vue','interprétation']),('p03_concede',['admettre','reconnaître','néanmoins','toutefois','cependant','malgré']),('p03_cause',['mécanisme','cause','facteur','influence','effet','conséquence']),('p03_transfer',['transférer','généraliser','appliquer','adapter','étendre','reproduire']),
('p04_actor',['acteur','groupe','institution','public','responsable','communauté']),('p04_value',['valeur','équité','justice','priorité','intérêt','principe']),('p04_tradeoff',['compromis','arbitrage','coût','avantage','bénéfice','perte']),('p04_constraint',['contrainte','ressource','obligation','règle','temps','capacité']),
('p05_synthesis',['synthèse','résumer','relier','combiner','ensemble','intégrer']),('p05_judgment',['jugement','évaluer','juger','décider','choisir','estimer']),('p05_revision',['réviser','modifier','corriger','adapter','changer','revoir']),('p05_condition',['si','condition','seuil','critère','indicateur','signal'])]
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));plan=json.loads(PLAN.read_text(encoding='utf-8'));probe=json.loads(PROBE.read_text(encoding='utf-8'));c1blob=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip();b2blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=6 or lock.get('c1_canonical_blob')!=c1blob or lock.get('b2_canonical_blob')!=b2blob:raise AssertionError('C1 Unit01 lock/live mismatch')
 if plan.get('status')!='PASS' or plan.get('c1_source_blob')!=c1blob or probe.get('status')!='PASS' or probe.get('c1_source_blob')!=c1blob:raise AssertionError('C1 Unit02 plan/probe missing or stale')
 default=int(lock['accepted_c1_default_new_targets_per_standard_passage'])
 if default!=4 or lock.get('accepted_default_is_hard_quota') is not False:raise AssertionError(f'unexpected calibrated C1 default metadata: {default}')
 fresh_list=probe.get('fresh',[]);fresh={x['form']:x for x in fresh_list}
 if len(fresh)<20:raise AssertionError(f'Only {len(fresh)} fresh terms remain')
 used=set();selected=[];fallbacks=[]
 for slot,candidates in SLOTS:
  hit=next((f for f in candidates if f in fresh and f not in used),None);fallback=False
  if hit is None:
   hit=next((x['form'] for x in fresh_list if x['form'] not in used),None);fallback=True
  if hit is None:raise AssertionError(f'No unused fresh target for {slot}')
  used.add(hit);item=dict(fresh[hit]);item['slot']=slot;item['semantic_fallback']=fallback;selected.append(item)
  if fallback:fallbacks.append({'slot':slot,'form':hit,'preferred_candidates':candidates})
 groups={k:[x['form'] for x in selected if x['slot'].startswith(k+'_')] for k in ['p01','p02','p03','p04','p05']}
 if len(selected)!=20 or len(used)!=20 or any(len(v)!=4 for v in groups.values()):raise AssertionError('C1 Unit02 selection structure failure')
 out={'status':'PASS','scope':'French C1 Unit02 target selection','b2_canonical_blob':b2blob,'c1_source_blob':c1blob,'c1_unit01_lock':'reading/audit/french_c1_unit01_frontier_lock.json','c1_plan_artifact':'reading/audit/french_c1_unit02_plan.json','theme':plan.get('theme'),'genres':plan.get('genres'),'word_band':[plan['c1_word_min'],plan['c1_word_max']],'new_targets_per_standard_passage':default,'default_is_hard_quota':False,'selected_count':20,'selected':selected,'passage_groups':groups,'semantic_fallback_count':len(fallbacks),'semantic_fallbacks':fallbacks,'note':'Selection is source/freshness locked. Four is the calibrated C1 default, not a hard quota.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','selected_count':20,'fallbacks':len(fallbacks),'groups':groups},ensure_ascii=False))
if __name__=='__main__':main()
