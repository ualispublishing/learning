#!/usr/bin/env python3
"""Second-pass naturalness audit for the post-quarantine Arabic phrase bank.

The first public audit removed a known generated family. This pass is intentionally
front-focused: it looks for residual combinatorial phrase templates, overlong fronts,
Latin/script contamination, repeated adjective stacking, and known typo/corruption
fragments independently of how the English definition was worded.
"""
from __future__ import annotations
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];AUDIT=ROOT/'audit';P=ROOT/'arabic_phrase_bank.csv'
AR=re.compile(r'[\u0600-\u06ff]');LAT=re.compile(r'[A-Za-z]')
DIAC=re.compile(r'[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]')
BAD_FRAGMENTS=('افتصاد','جيفيز','أنتروبولوج','الاستمالة المهنية','الاستمالة الفنية','الاستمالة المنطقية','الاستمالة الدبلوماسية')
TEMPLATES=(('على نطاق',5),('من ناحية',5),('بغرض',4),('من قبيل',6),('على نحو',5),('من منظور',5))
def norm(s):return re.sub(r'\s+',' ',DIAC.sub('',s or '')).strip()
def main():
 with P.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
 q=[];counts={}
 def add(code):counts[code]=counts.get(code,0)+1
 for i,r in enumerate(rows,1):
  front=(r.get('Front') or '').strip();n=norm(front);words=n.split();flags=[]
  if LAT.search(front):flags.append('latin_in_front')
  if len(words)>7:flags.append('front_over_7_tokens')
  if any(x in n for x in BAD_FRAGMENTS):flags.append('known_corruption_fragment')
  for prefix,limit in TEMPLATES:
   if n.startswith(prefix) and len(words)>=limit:flags.append(f'productive_template_{prefix.replace(" ","_")}')
  # Long sequences of nisba/adjectival endings are a common generated-family signature.
  adjish=sum(1 for w in words if re.search(r'(?:ي|ية|يّة|ِيّ|ِيَّة)$',w))
  if len(words)>=5 and adjish>=3:flags.append('stacked_adjectival_chain')
  if flags:
   for x in set(flags):add(x)
   q.append({'row':i,'front':front,'normalized_front':n,'flags':sorted(set(flags)),'back_preview':(r.get('Back') or '')[:350].replace('\n',' | ')})
 summary={'rows':len(rows),'flagged_rows':len(q),'flag_counts':counts,'public_ready_by_front_naturalness_heuristics':not q,'policy':'Independent front-based residual-generation audit after the 189-row quarantine; flagged rows require manual review rather than automatic deletion.'}
 (AUDIT/'arabic_phrase_naturalness_v2_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (AUDIT/'arabic_phrase_naturalness_v2_queue.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
