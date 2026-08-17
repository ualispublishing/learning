#!/usr/bin/env python3
"""Fail-closed preflight wrapper for French B2 Unit07."""
from pathlib import Path
p=Path(__file__).with_name('generate_french_b2_unit07.py')
ns={'__name__':'unit07_base','__file__':str(p),'__package__':None}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
specs=ns['SPECS'];cp=ns['CHECKPOINT']
if [s['id'] for s in specs] != [f'fr-b2-u07-p{i:02d}' for i in range(1,6)]:raise AssertionError('unexpected Unit07 structure')
off=[]
for s in specs:
 local=set(s['forms'])|set(s['reviews'])
 for i,item in enumerate(s['items'],1):
  bad=[f for f in item[3] if f not in local]
  if bad:off.append((s['id'],i,bad))
local=set(ns['FORMS'])
for i,item in enumerate(cp['items'],1):
 bad=[f for f in item[3] if f not in local]
 if bad:off.append((cp['id'],i,bad))
if off:raise AssertionError(f'Unit07 preflight non-local target forms: {off}')
ns['main']()
