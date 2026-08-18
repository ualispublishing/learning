#!/usr/bin/env python3
"""Select 20 auditable fresh targets for B2 Unit08 from the persisted probe.

Each slot first tries history-appropriate candidates. If a narrow slot is
exhausted by prior French learning, the selector takes the next unused fresh
probe term and records that semantic fallback explicitly. It still fails closed
unless all 20 targets are source-backed, fresh and unique.
"""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2]
B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_b2_unit07_frontier_lock.json';PROBE=R/'reading/audit/french_b2_unit08_target_probe.json';OUT=R/'reading/audit/french_b2_unit08_target_selection.json'
SLOTS=[
('p01_time',['époque','siècle','période','date','début','pendant','longtemps']),
('p01_sequence',['fin','avant','après','longtemps','commencer','finir']),
('p01_state',['état','empire','peuple','nation','roi','armée','pays']),
('p01_conflict',['paix','bataille','victoire','défaite','soldat','armée','ennemi']),
('p02_change',['conséquence','changement','développer','produire','commencer','finir']),
('p02_pressure',['augmenter','réduire','détruire','créer','danger']),
('p02_economy',['commerce','port','frontière','marché','travail','pays']),
('p02_crisis',['impôt','faim','maladie','crise','réforme']),
('p03_document',['document','source','rapport','discours','registre','lettre']),
('p03_witness',['témoin','témoignage','archive','mémoire','journal','lettre']),
('p03_perspective',['version','point','vue','position','objectif']),
('p03_method',['vérifier','noter','décrire','observer','expliquer','raconter']),
('p04_conflict',['conflit','révolution','mouvement','protestation','élection','traité','alliance','attaquer','défendre']),
('p04_authority',['autorité','pouvoir','institution','administration','gouvernement','président']),
('p04_groups',['majorité','minorité','communauté','génération','population','membre','homme','femme']),
('p04_scale',['national','international','économique','militaire','social','pays']),
('p05_action',['gagner','perdre','attaquer','défendre','quitter','revenir','arriver','partir','occuper']),
('p05_actor',['chef','membre','citoyen','responsable','travailleur','homme','femme']),
('p05_explanation',['intérêt','objectif','but','erreur','différence','relation','lien','ensemble','point']),
('p05_qualification',['complexe','local','religieux','probable','faible','fort','grand','petit'])]

def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));probe=json.loads(PROBE.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=42 or blob!=lock.get('canonical_blob'):raise AssertionError('Unit07 lock/live B2 mismatch')
 if probe.get('status')!='PASS' or probe.get('b2_source_blob')!=blob:raise AssertionError('Unit08 probe missing/stale')
 fresh_list=probe.get('fresh',[]);fresh={x['form']:x for x in fresh_list}
 if len(fresh)<20:raise AssertionError(f'Unit08 probe has only {len(fresh)} fresh candidates; need at least 20')
 used=set();selected=[];fallbacks=[]
 for slot,candidates in SLOTS:
  hit=next((f for f in candidates if f in fresh and f not in used),None);fallback=False
  if hit is None:
   hit=next((x['form'] for x in fresh_list if x['form'] not in used),None);fallback=True
  if hit is None:raise AssertionError(f'No unused fresh target available for slot {slot}')
  used.add(hit);item=dict(fresh[hit]);item['slot']=slot;item['semantic_fallback']=fallback;selected.append(item)
  if fallback:fallbacks.append({'slot':slot,'form':hit,'preferred_candidates':candidates})
 if len(selected)!=20 or len(used)!=20:raise AssertionError('Unit08 selection uniqueness failure')
 groups={'p01':[x for x in selected if x['slot'].startswith('p01_')],'p02':[x for x in selected if x['slot'].startswith('p02_')],'p03':[x for x in selected if x['slot'].startswith('p03_')],'p04':[x for x in selected if x['slot'].startswith('p04_')],'p05':[x for x in selected if x['slot'].startswith('p05_')]}
 if any(len(v)!=4 for v in groups.values()):raise AssertionError('Unit08 selection group size failure')
 out={'status':'PASS','scope':'French B2 Unit 08 target selection','theme':'history and explanation','b2_source_blob':blob,'selected_count':20,'selected':selected,'passage_groups':{k:[x['form'] for x in v] for k,v in groups.items()},'semantic_fallback_count':len(fallbacks),'semantic_fallbacks':fallbacks,'note':'Deterministic selection from persisted freshness probe; every fallback is explicitly audited; not generation approval.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
