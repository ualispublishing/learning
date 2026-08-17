#!/usr/bin/env python3
"""Select 20 fresh targets for C1 Unit03 from the exhaustive locked probe."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_c1_unit02_frontier_lock.json';PLAN=R/'reading/audit/french_c1_unit03_plan.json';PROBE=R/'reading/audit/french_c1_unit03_target_probe.json';OUT=R/'reading/audit/french_c1_unit03_target_selection.json'
SLOTS=[
('p01_concept',['concept','notion','définition','sens','catégorie','terme']),('p01_measure',['mesure','indicateur','critère','niveau','quantité','qualité']),('p01_boundary',['frontière','limite','seuil','condition','exception','cadre']),('p01_example',['exemple','cas','situation','forme','type','modèle']),
('p02_cause',['cause','mécanisme','facteur','origine','effet','influence']),('p02_sequence',['étape','processus','ordre','avant','après','évolution']),('p02_alternative',['alternative','autre','contraire','option','hypothèse','possibilité']),('p02_test',['tester','vérifier','contrôler','observer','comparer','mesurer']),
('p03_rule',['standard','norme','règle','principe','procédure','méthode']),('p03_consistency',['cohérence','stable','constant','commun','général','ensemble']),('p03_compare',['comparaison','écart','différence','relation','variation','résultat']),('p03_accountability',['responsabilité','transparent','expliquer','justifier','preuve','rapport']),
('p04_context',['contexte','local','particulier','spécifique','milieu','environnement']),('p04_actor',['acteur','participant','membre','groupe','communauté','institution']),('p04_discretion',['choisir','adapter','interpréter','décider','juger','préférer']),('p04_unintended',['surprendre','inattendu','conséquence','risque','problème','erreur']),
('p05_integrate',['intégrer','combiner','relier','réunir','synthèse','ensemble']),('p05_balance',['équilibre','compromis','arbitrage','priorité','valeur','intérêt']),('p05_monitor',['suivre','surveiller','évaluer','réviser','corriger','ajuster']),('p05_transfer',['transférer','appliquer','étendre','adapter','généraliser','reproduire'])]
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));plan=json.loads(PLAN.read_text(encoding='utf-8'));probe=json.loads(PROBE.read_text(encoding='utf-8'));c1blob=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip();b2blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=12 or lock.get('c1_canonical_blob')!=c1blob or lock.get('b2_canonical_blob')!=b2blob:raise AssertionError('C1 Unit02 lock/live mismatch')
 if plan.get('status')!='PASS' or plan.get('c1_source_blob')!=c1blob or probe.get('status')!='PASS' or probe.get('c1_source_blob')!=c1blob:raise AssertionError('Unit03 plan/probe stale')
 if int(lock['accepted_c1_default_new_targets_per_standard_passage'])!=4 or lock.get('accepted_default_is_hard_quota') is not False:raise AssertionError('unexpected C1 default metadata')
 fresh_list=probe.get('fresh',[]);fresh={x['form']:x for x in fresh_list};used=set();selected=[];fallbacks=[]
 if len(fresh)<20:raise AssertionError(f'Only {len(fresh)} fresh terms remain')
 for slot,cands in SLOTS:
  hit=next((f for f in cands if f in fresh and f not in used),None);fb=False
  if hit is None:hit=next((x['form'] for x in fresh_list if x['form'] not in used),None);fb=True
  if hit is None:raise AssertionError(f'No fresh target for {slot}')
  used.add(hit);item=dict(fresh[hit]);item['slot']=slot;item['semantic_fallback']=fb;selected.append(item)
  if fb:fallbacks.append({'slot':slot,'form':hit,'preferred_candidates':cands})
 groups={k:[x['form'] for x in selected if x['slot'].startswith(k+'_')] for k in ['p01','p02','p03','p04','p05']}
 if len(selected)!=20 or len(used)!=20 or any(len(v)!=4 for v in groups.values()):raise AssertionError('Unit03 target structure failure')
 out={'status':'PASS','scope':'French C1 Unit03 target selection','b2_canonical_blob':b2blob,'c1_source_blob':c1blob,'theme':plan.get('theme'),'genres':plan.get('genres'),'word_band':[plan['c1_word_min'],plan['c1_word_max']],'new_targets_per_standard_passage':4,'default_is_hard_quota':False,'selected_count':20,'selected':selected,'passage_groups':groups,'semantic_fallback_count':len(fallbacks),'semantic_fallbacks':fallbacks,'note':'Source/freshness locked to Unit02 C1 frontier; four is calibrated default, not hard quota.'};OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','groups':groups,'fallbacks':len(fallbacks)},ensure_ascii=False))
if __name__=='__main__':main()
