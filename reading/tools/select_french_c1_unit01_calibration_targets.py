#!/usr/bin/env python3
"""Select a conservative French C1 Unit01 calibration target set.

Canonical policy gives C1 a 6–10 *maximum planning band*, explicitly says those
bands are not quotas, and permits fewer targets when discourse/grammar load is
high. Unit01 therefore tests four fresh content targets in P01-P05 and zero in
P06; strict post-calibration review decides the later C1 production default.
"""
from __future__ import annotations
import json,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];B2=R/'reading/french/b2/passages.jsonl';READY=R/'reading/audit/french_c1_readiness.json';PLAN=R/'reading/audit/french_c1_unit01_plan.json';PROBE=R/'reading/audit/french_c1_unit01_target_probe.json';OUT=R/'reading/audit/french_c1_unit01_target_selection.json'
PREFERRED=[
 ['conclusion','hypothèse','affirmation','préciser','démontrer','constater','établir','question'],
 ['néanmoins','toutefois','pourtant','cependant','malgré','contraire','différent','nuance'],
 ['méthode','analyse','donnée','élément','indice','observer','comparer','interpréter'],
 ['contexte','condition','limite','exception','considérer','dépendre','relation','ensemble'],
 ['conséquence','implication','décision','juger','évaluer','modifier','adapter','perspective']]
SAFE_FALLBACK=['enquête','base','suspect','environ','courant','intérieur','exister','âge','traiter','mener','ailleurs','complètement','approcher','engager','juge','avocat','directeur','animal','drogue','banque','excellent','parfait','terrible','incroyable','supporter','libérer']
BANNED={'être','avoir','de','je','pas','le','que','vous','tu','et','il','un','en','ça','on','une','elle','me','du','te','se','toi','lui','votre','cette','son','par','ou','des','sa','ses','leur','mes','tes','cet','dont','ni','aucun','aucune','la'}

def lexical_planning_policy(contexts):
 """Return C1 planning band only from the explicit lexical-planning context."""
 matches=[]
 for c in contexts:
  txt=c.get('context','')
  if 'maximum planning bands, not quotas' not in txt:continue
  m=re.search(r'(?im)^\s*-?\s*C1\s*:\s*(\d+)\s*(?:–|—|-)\s*(\d+)\s*;',txt)
  if m:matches.append((int(m.group(1)),int(m.group(2)),c.get('line')))
 uniq={(a,b) for a,b,_ in matches}
 if uniq!={(6,10)}:raise AssertionError(f'Could not verify canonical C1 lexical maximum planning band 6–10: {matches}')
 return {'min_planning_reference':6,'max_planning_reference':10,'is_quota':False,'use_fewer_when_discourse_load_high':True,'evidence_lines':[x[2] for x in matches]}

def main():
 ready=json.loads(READY.read_text(encoding='utf-8'));plan=json.loads(PLAN.read_text(encoding='utf-8'));probe=json.loads(PROBE.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if any(x.get('status')!='PASS' for x in (ready,plan,probe)):raise AssertionError('C1 calibration prerequisites not PASS')
 if ready.get('b2_canonical_blob')!=blob or plan.get('b2_canonical_blob')!=blob or probe.get('b2_canonical_blob')!=blob:raise AssertionError('C1 calibration prerequisite blob drift')
 policy=lexical_planning_policy(ready.get('c1_standard_contexts',[]))
 fresh_list=probe.get('fresh',[]);fresh={x['form']:x for x in fresh_list}
 if len(fresh)<20:raise AssertionError('Insufficient fresh source terms for 4x5 C1 calibration')
 used=set();selected=[];fallbacks=[]
 for p,candidates in enumerate(PREFERRED,1):
  for slot in range(1,5):
   hit=next((f for f in candidates if f in fresh and f not in used and f not in BANNED),None);fallback=False
   if hit is None:
    hit=next((f for f in SAFE_FALLBACK if f in fresh and f not in used and f not in BANNED),None);fallback=True
   if hit is None:raise AssertionError(f'No pedagogically eligible fresh content term for C1 P{p:02d} slot {slot}')
   used.add(hit);item=dict(fresh[hit]);item['passage']=p;item['slot']=slot;item['semantic_fallback']=fallback;item['pedagogical_content_word']=True;selected.append(item)
   if fallback:fallbacks.append({'passage':p,'slot':slot,'form':hit,'preferred_candidates':candidates})
 if used&BANNED:raise AssertionError(f'C1 calibration selected banned function words: {sorted(used&BANNED)}')
 groups={f'p0{p}':[x['form'] for x in selected if x['passage']==p] for p in range(1,6)}
 if len(selected)!=20 or any(len(v)!=4 for v in groups.values()):raise AssertionError('C1 calibration target group structure failure')
 out={'status':'PASS','scope':'French C1 Unit01 calibration target selection','b2_canonical_blob':blob,'c1_plan_artifact':'reading/audit/french_c1_unit01_plan.json','c1_theme':plan.get('theme'),'c1_genres':plan.get('genres'),'c1_word_min':plan['c1_word_min'],'c1_word_max':plan['c1_word_max'],'canonical_lexical_planning_policy':policy,'calibration_new_targets_per_standard_passage':4,'checkpoint_new_targets':0,'selected_count':20,'selected':selected,'passage_groups':groups,'semantic_fallback_count':len(fallbacks),'semantic_fallbacks':fallbacks,'pedagogical_filter':'preferred research/evidence vocabulary or vetted content-word fallback only','policy':'Four is a conservative Unit01 calibration candidate, explicitly permitted because the canonical 6–10 band is not a quota and says to use fewer under high discourse load; post-calibration review must set the C1 production default.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','calibration_load':4,'canonical_planning_band':[6,10],'band_is_quota':False,'selected_count':20,'fallbacks':len(fallbacks),'groups':groups},ensure_ascii=False))
if __name__=='__main__':main()
