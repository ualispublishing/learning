#!/usr/bin/env python3
"""Record four verified French A1 reader-sense overrides without mutating root CSVs."""
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
 before=copy.deepcopy(data);by={r['id']:r for r in data}; selected={}

 autre=find_target(by['fr-a1-u04-p01'],'autre')
 if (autre.get('id'),autre.get('source_rank'),autre.get('source_lexicon'),autre.get('intended_sense')) != ('fr-rank-0082',82,'french_top1000.csv','other; another'):
  raise AssertionError(f'autre source state drift: {autre}')
 autre['sense_adjudication']={
  'status':'VERIFIED_OVERRIDE','reason':'root deck gloss is awkward/overbroad, while the reader uses the ordinary “different from the one just mentioned / another” sense',
  'authority':'Dictionnaire de l’Académie française, 9e édition, “autre”',
  'authority_url':'https://www.dictionnaire-academie.fr/article/A9A3313',
  'verified_reader_sense':'different from what was just mentioned; another / other'
 }
 selected['fr-a1-u04-p01']='autre'

 maison=find_target(by['fr-a1-u04-p05'],'maison')
 if (maison.get('id'),maison.get('source_rank'),maison.get('source_lexicon'),maison.get('intended_sense')) != ('fr-rank-0153',153,'french_top1000.csv','house; home'):
  raise AssertionError(f'maison source state drift: {maison}')
 maison['sense_adjudication']={
  'status':'VERIFIED_OVERRIDE','reason':'root deck gloss records “house” only, while ordinary “à la maison” means at home / chez soi',
  'authority':'Dictionnaire de l’Académie française, 9e édition, “maison”',
  'authority_url':'https://www.dictionnaire-academie.fr/article/A9M0242',
  'verified_reader_sense':'house; in the locution à la maison, home / chez soi'
 }
 selected['fr-a1-u04-p05']='maison'

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
 selected['fr-a1-u06-p04']='jamais'

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
 selected['fr-a1-u07-p04']='droite'

 bby={r['id']:r for r in before}
 for pid,row in by.items():
  old=bby[pid]
  if pid not in selected:
   if row!=old:raise AssertionError(f'unselected row changed: {pid}')
   continue
  form=selected[pid];old2=copy.deepcopy(old);new2=copy.deepcopy(row)
  ot=find_target(old2,form);nt=find_target(new2,form)
  for k in ('intended_sense','sense_adjudication'):
   ot.pop(k,None);nt.pop(k,None)
  if old2!=new2:raise AssertionError(f'{pid}: mutation escaped selected target sense metadata')
 CANON.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in data),encoding='utf-8')
 print(json.dumps({'status':'PASS','repairs':4,'targets':[f'{p}:{f}' for p,f in selected.items()]},ensure_ascii=False))
if __name__=='__main__':main()
