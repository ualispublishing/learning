#!/usr/bin/env python3
"""Publication-readiness audit for every learner-facing CSV.

This is deliberately stricter than structural integrity checks. It flags cards that
may be technically sourced but still look unsafe to publish: raw dictionary/POS
artifacts, stale candidate labels, overly broad sense bundles, awkward generated
wording, script contamination, and phrase-bank generation fingerprints.
"""
from __future__ import annotations
import csv, json, re, unicodedata
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'audit'
FILES=[
 'arabic_top1000.csv','arabic_top3000.csv','french_top1000.csv',
 'french_top3000.csv','urdu_top1000.csv','urdu_top3000.csv','arabic_phrase_bank.csv']

FIELD_RE={
 'rank':re.compile(r'(?m)^Rank:\s*(\d+)\s*$'),
 'meaning':re.compile(r'(?ms)^Meaning:\s*(.+?)(?=\n\n[A-Z][^\n]*:|\Z)'),
 'pos':re.compile(r'(?ms)^Part of speech:\s*(.+?)(?=\n\n[A-Z][^\n]*:|\Z)'),
}
ARABIC=re.compile(r'[\u0600-\u06ff]')
MACHINE_POS=re.compile(r'(^|[|/\s])(postp|pron|propn|adp|aux|det|part|sconj|cconj|num|intj)([|/\s]|$)',re.I)
STALE=re.compile(r'candidate only|not promoted|review required|unverified|placeholder',re.I)
RAW_GLOSS=re.compile(r'\b(verbal noun of|feminine singular of|masculine singular of|plural of|alternative form of|inflection of)\b',re.I)
USAGE_AS_MEANING=re.compile(r'\b(the passive voice|all reflexive verbs|used before|used after|used with)\b',re.I)
GENERATED_PHRASE=re.compile(r'\b(emphatic version of|phrase narrowing the discussion|phrase used when an action is taken|on a .* scale|for the purpose of .* winning over)\b',re.I)
ODD_SEPARATORS=re.compile(r'\|')
UNDERSCORE=re.compile(r'\w_\w')

def extract(back,key):
 m=FIELD_RE[key].search(back or '')
 return re.sub(r'\s+',' ',m.group(1)).strip() if m else ''

def normalized(s):
 s=unicodedata.normalize('NFKC',s or '').replace('ـ','')
 s=re.sub(r'[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]','',s)
 return re.sub(r'\s+',' ',s).strip().casefold()

def audit_row(name,idx,row):
 front=(row.get('Front') or '').strip(); back=(row.get('Back') or '').strip()
 flags=[]; severity='info'; stale_match=''
 meaning=extract(back,'meaning'); pos=extract(back,'pos'); rank=extract(back,'rank')
 def flag(code,sev='review'):
  nonlocal severity
  flags.append(code)
  if sev=='block': severity='block'
  elif sev=='review' and severity!='block': severity='review'

 m=STALE.search(back)
 if m:
  stale_match=back[max(0,m.start()-90):min(len(back),m.end()+140)].replace('\n',' | ')
  flag('stale_candidate_or_review_label','block')
 if UNDERSCORE.search(meaning): flag('raw_underscore_gloss','review')
 if ODD_SEPARATORS.search(pos): flag('machine_pos_separator','review')
 if MACHINE_POS.search(pos): flag('machine_pos_abbreviation','review')
 if RAW_GLOSS.search(meaning): flag('raw_dictionary_inflection_gloss','review')
 if USAGE_AS_MEANING.search(meaning): flag('usage_note_mixed_into_meaning','review')
 if meaning.count(';')>=4: flag('overbundled_meaning_5plus_senses','review')
 if len(meaning)>180: flag('very_long_meaning','review')
 if name.startswith(('arabic_','urdu_')) and not ARABIC.search(front): flag('wrong_script_front','block')
 if name.startswith('french_') and ARABIC.search(front): flag('wrong_script_front','block')
 if name=='arabic_phrase_bank.csv':
  if GENERATED_PHRASE.search(back): flag('generated_phrase_wording_fingerprint','review')
  if len(front.split())<2: flag('phrase_bank_single_token','review')
  if 'Definition:' not in back or 'Example:' not in back or 'Translation:' not in back: flag('phrase_missing_public_fields','block')
 return {'file':name,'row':idx,'front':front,'rank':rank,'meaning':meaning,'pos':pos,'flags':flags,'severity':severity,'stale_match':stale_match,'back_preview':back[:500].replace('\n',' | ')}

def main():
 AUDIT.mkdir(exist_ok=True)
 summary={'files':{},'overall':{},'policy':'Publication-readiness triage. Any block flag prevents public-ready status; review flags require linguistic inspection before claiming publication quality.'}
 queue=[]
 compact_fields=('file','row','front','rank','meaning','pos','severity','flags','stale_match')
 for name in FILES:
  with (ROOT/name).open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
  counts=Counter(); sev=Counter(); file_queue=[]
  for i,row in enumerate(rows,1):
   r=audit_row(name,i,row)
   for fl in r['flags']: counts[fl]+=1
   if r['flags']:
    sev[r['severity']]+=1; queue.append(r); file_queue.append(r)
  summary['files'][name]={
   'rows':len(rows),'flagged_rows':sum(sev.values()),'block_rows':sev['block'],
   'review_rows':sev['review'],'flag_counts':dict(counts),
   'public_ready_by_heuristics':sev['block']==0 and sev['review']==0,
  }
  compact_file=[{k:r[k] for k in compact_fields} for r in file_queue]
  stem=name.removesuffix('.csv')
  (AUDIT/f'public_review_{stem}.json').write_text(json.dumps(compact_file,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 summary['overall']={
  'rows':sum(v['rows'] for v in summary['files'].values()),
  'flagged_rows':len(queue),
  'block_rows':sum(1 for r in queue if r['severity']=='block'),
  'review_rows':sum(1 for r in queue if r['severity']=='review'),
  'public_ready_by_heuristics':not queue,
 }
 (AUDIT/'public_readiness_audit.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 compact=[{k:r[k] for k in compact_fields} for r in queue]
 (AUDIT/'public_readiness_review_compact.json').write_text(json.dumps(compact,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 fields=['file','row','front','rank','meaning','pos','severity','flags','back_preview']
 with (AUDIT/'public_readiness_review_queue.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
  for r in queue:
   rr=r.copy(); rr['flags']=';'.join(rr['flags']); w.writerow({k:rr[k] for k in fields})
 print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
