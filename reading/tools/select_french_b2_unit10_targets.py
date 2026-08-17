#!/usr/bin/env python3
"""Select final 20 B2 targets from the exhaustive Unit10 freshness probe."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_b2_unit09_frontier_lock.json';PROBE=R/'reading/audit/french_b2_unit10_target_probe.json';OUT=R/'reading/audit/french_b2_unit10_target_selection.json'
SLOTS=[
('p01_claim',['affirmer','conclure','conclusion','thèse','argument']),('p01_evidence',['indice','élément','donnée','preuve','fait']),('p01_scope',['cas','situation','condition','limite','exception']),('p01_qualify',['possible','probable','certain','relatif','précis']),
('p02_perspective',['perspective','position','point','vue','approche']),('p02_contrast',['contraire','différence','opposé','cependant','pourtant']),('p02_concede',['admettre','reconnaître','accepter','malgré','même']),('p02_response',['répondre','réponse','défendre','expliquer','justifier']),
('p03_combine',['combiner','ensemble','relier','lier','réunir']),('p03_source',['source','document','rapport','étude','texte']),('p03_compare',['comparer','comparaison','mesurer','évaluer','vérifier']),('p03_pattern',['tendance','variation','différence','relation','résultat']),
('p04_tradeoff',['compromis','choix','coût','avantage','risque']),('p04_stakeholder',['acteur','groupe','public','citoyen','responsable']),('p04_constraint',['contrainte','ressource','temps','budget','règle']),('p04_option',['option','alternative','solution','proposition','mesure']),
('p05_synthesize',['synthèse','résumer','résumé','ensemble','général']),('p05_revision',['réviser','modifier','changer','corriger','adapter']),('p05_transfer',['appliquer','transférer','utiliser','servir','mobiliser']),('p05_judgment',['jugement','décision','choisir','préférer','estimer'])]
def main():
 if not LOCK.exists():raise AssertionError('Unit09 lock missing; Unit10 selection must not run early')
 lock=json.loads(LOCK.read_text(encoding='utf-8'));probe=json.loads(PROBE.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=54 or blob!=lock.get('canonical_blob'):raise AssertionError('Unit09 lock/live B2 mismatch')
 if probe.get('status')!='PASS' or probe.get('b2_source_blob')!=blob:raise AssertionError('Unit10 exhaustive probe missing/stale')
 fresh_list=probe.get('fresh',[]);fresh={x['form']:x for x in fresh_list}
 if len(fresh)<20:raise AssertionError(f'Only {len(fresh)} fresh source targets remain; need 20')
 used=set();selected=[];fallbacks=[]
 for slot,candidates in SLOTS:
  hit=next((f for f in candidates if f in fresh and f not in used),None);fallback=False
  if hit is None:
   hit=next((x['form'] for x in fresh_list if x['form'] not in used),None);fallback=True
  if hit is None:raise AssertionError(f'No unused fresh target for {slot}')
  used.add(hit);item=dict(fresh[hit]);item['slot']=slot;item['semantic_fallback']=fallback;selected.append(item)
  if fallback:fallbacks.append({'slot':slot,'form':hit,'preferred_candidates':candidates})
 groups={k:[x for x in selected if x['slot'].startswith(k+'_')] for k in ['p01','p02','p03','p04','p05']}
 if len(selected)!=20 or len(used)!=20 or any(len(v)!=4 for v in groups.values()):raise AssertionError('Unit10 selection structure failure')
 out={'status':'PASS','scope':'French B2 Unit 10 target selection','theme':'B2 synthesis','b2_source_blob':blob,'selected_count':20,'selected':selected,'passage_groups':{k:[x['form'] for x in v] for k,v in groups.items()},'semantic_fallback_count':len(fallbacks),'semantic_fallbacks':fallbacks,'note':'Selection from exhaustive rank-ordered fresh deck; every fallback explicitly audited; not final B2 approval.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','selected_count':20,'fallbacks':len(fallbacks),'groups':out['passage_groups']},ensure_ascii=False))
if __name__=='__main__':main()
