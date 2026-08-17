#!/usr/bin/env python3
"""Select a conservative French C1 Unit01 calibration target set.

Candidate calibration load is four fresh targets in P01-P05 and zero in P06.
The script scans canonical C1 standard contexts for explicit lexical-load minima
and fails closed if repository policy requires more than four. This does not set
the later C1 production default; post-calibration review must do that.
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
def explicit_minimum(contexts):
 hits=[]
 for c in contexts:
  txt=c.get('context','')
  # Only treat a number as lexical-load guidance when it occurs near language
  # about new/lexical/vocabulary targets; do not confuse word bands or question counts.
  for m in re.finditer(r'(?is)(?:new|nouveaux?|lexical|lexique|vocab(?:ulary|ulaire)?|targets?|cibles?).{0,80}?(\d+)\s*(?:–|—|-|to|à)\s*(\d+)',txt):
   a,b=map(int,m.groups())
   if 0<=a<=20 and a<=b<=30:hits.append((a,b,m.group(0)[:180]))
  for m in re.finditer(r'(?is)(\d+)\s*(?:–|—|-|to|à)\s*(\d+).{0,80}?(?:new|nouveaux?|lexical|lexique|vocab(?:ulary|ulaire)?|targets?|cibles?)',txt):
   a,b=map(int,m.groups())
   if 0<=a<=20 and a<=b<=30:hits.append((a,b,m.group(0)[:180]))
 uniq=[]
 for h in hits:
  if h[:2] not in [x[:2] for x in uniq]:uniq.append(h)
 return uniq
def main():
 ready=json.loads(READY.read_text(encoding='utf-8'));plan=json.loads(PLAN.read_text(encoding='utf-8'));probe=json.loads(PROBE.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if any(x.get('status')!='PASS' for x in (ready,plan,probe)):raise AssertionError('C1 calibration prerequisites not PASS')
 if ready.get('b2_canonical_blob')!=blob or plan.get('b2_canonical_blob')!=blob or probe.get('b2_canonical_blob')!=blob:raise AssertionError('C1 calibration prerequisite blob drift')
 hints=explicit_minimum(ready.get('c1_standard_contexts',[]));mins=[x[0] for x in hints]
 if mins and max(mins)>4:raise AssertionError(f'Canonical C1 standard appears to require >4 new lexical targets per passage: {hints}; calibration load must be reviewed explicitly')
 fresh_list=probe.get('fresh',[]);fresh={x['form']:x for x in fresh_list}
 if len(fresh)<20:raise AssertionError('Insufficient fresh source terms for 4x5 C1 calibration')
 used=set();selected=[];fallbacks=[]
 for p,candidates in enumerate(PREFERRED,1):
  for slot in range(1,5):
   hit=next((f for f in candidates if f in fresh and f not in used),None);fallback=False
   if hit is None:
    hit=next((x['form'] for x in fresh_list if x['form'] not in used),None);fallback=True
   if hit is None:raise AssertionError(f'No fresh term for C1 P{p:02d} slot {slot}')
   used.add(hit);item=dict(fresh[hit]);item['passage']=p;item['slot']=slot;item['semantic_fallback']=fallback;selected.append(item)
   if fallback:fallbacks.append({'passage':p,'slot':slot,'form':hit,'preferred_candidates':candidates})
 groups={f'p0{p}':[x['form'] for x in selected if x['passage']==p] for p in range(1,6)}
 out={'status':'PASS','scope':'French C1 Unit01 calibration target selection','b2_canonical_blob':blob,'c1_plan_artifact':'reading/audit/french_c1_unit01_plan.json','c1_theme':plan.get('theme'),'c1_genres':plan.get('genres'),'c1_word_min':plan['c1_word_min'],'c1_word_max':plan['c1_word_max'],'calibration_new_targets_per_standard_passage':4,'checkpoint_new_targets':0,'explicit_lexical_load_hints':hints,'selected_count':20,'selected':selected,'passage_groups':groups,'semantic_fallback_count':len(fallbacks),'semantic_fallbacks':fallbacks,'policy':'Four is a conservative Unit01 calibration candidate only; post-calibration review must set the C1 production default and may increase it if canonical standard and observed discourse load support that change.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','load':4,'selected_count':20,'fallbacks':len(fallbacks),'hints':hints,'groups':groups},ensure_ascii=False))
if __name__=='__main__':main()
