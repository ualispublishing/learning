#!/usr/bin/env python3
"""Record two verified French A1 reader-sense overrides without mutating root CSVs."""
from __future__ import annotations
import copy,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/'reading/french/a1/passages.jsonl'
EXPECTED_BLOB='b6c15291b7871e196cac8f7b5920923f2a3a95a9'

def rows():return [json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
def find_target(row,form):
 h=[t for t in row.get('new_lexical_targets',[]) if isinstance(t,dict) and t.get('form')==form]
 if len(h)!=1:raise AssertionError(f"{row.get('id')}: expected one new target {form}, got {len(h)}")
 return h[0]
def main():
 blob=subprocess.check_output(['git','hash-object',str(CANON)],text=True).strip()
 if blob!=EXPECTED_BLOB:raise AssertionError(f'canonical blob drift: {blob} != {EXPECTED_BLOB}')
 data=rows()
 if len(data)!=60 or [r['sequence'] for r in data]!=list(range(1,61)):raise AssertionError('French A1 is not the expected completed 60-row corpus')
 before=copy.deepcopy(data);by={r['id']:r for r in data}
 jam=find_target(by['fr-a1-u06-p04'],'jamais')
 if (jam.get('id'),jam.get('source_rank'),jam.get('source_lexicon'),jam.get('intended_sense')) != ('fr-rank-0075',75,'french_top1000.csv','ever'):
  raise AssertionError(f'jamais source state drift: {jam}')
 jam['intended_sense']='never; at no time (in the ne…jamais negative construction)'
 jam['sense_adjudication']={
  'status':'VERIFIED_OVERRIDE','reason':'root deck gloss records only the non-negative “ever” sense, while this reader target deliberately teaches ne…jamais = never/at no time',
  'authority':'Dictionnaire de l’Académie française, 9e édition, “jamais”',
  'authority_url':'https://www.dictionnaire-academie.fr/article/A9J0068',
  'verified_reader_sense':'en aucun temps; with ne, never / at no time'
 }
 dr=find_target(by['fr-a1-u07-p04'],'droite')
 if (dr.get('id'),dr.get('source_rank'),dr.get('source_lexicon'),dr.get('source_lookup_form'),dr.get('lemma')) != ('fr-rank-0276',276,'french_top1000.csv','droit','droit'):
  raise AssertionError(f'droite source state drift: {dr}')
 dr['intended_sense']='right; on/to the right (opposite of left)'
 dr['sense_adjudication']={
  'status':'VERIFIED_OVERRIDE','reason':'reader-facing feminine/directional form droite is a realization of lemma droit; the compact root-card gloss omits the left/right sense used here',
  'authority':'Dictionnaire de l’Académie française, 9e édition, “droit, droite”',
  'authority_url':'https://www.dictionnaire-academie.fr/article/A9D3278',
  'verified_reader_sense':'situated on the side opposite the left; à droite / the right side'
 }
 # Mutation boundary: only those two target dictionaries may differ.
 bby={r['id']:r for r in before}
 for pid,row in by.items():
  old=bby[pid]
  if pid not in {'fr-a1-u06-p04','fr-a1-u07-p04'}:
   if row!=old:raise AssertionError(f'unselected row changed: {pid}')
   continue
  form='jamais' if pid.endswith('u06-p04') else 'droite'
  old2=copy.deepcopy(old);new2=copy.deepcopy(row)
  ot=find_target(old2,form);nt=find_target(new2,form)
  for k in ('intended_sense','sense_adjudication'):
   ot.pop(k,None);nt.pop(k,None)
  if old2!=new2:raise AssertionError(f'{pid}: mutation escaped selected target sense metadata')
 CANON.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in data),encoding='utf-8')
 print(json.dumps({'status':'PASS','repairs':2,'targets':['fr-a1-u06-p04:jamais','fr-a1-u07-p04:droite']},ensure_ascii=False))
if __name__=='__main__':main()
