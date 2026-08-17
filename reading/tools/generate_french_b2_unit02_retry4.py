#!/usr/bin/env python3
"""Fail-closed Unit02 retry: corrected pool plus local-linkage repair."""
from pathlib import Path

p = Path(__file__).with_name('generate_french_b2_unit02_retry3.py')
src = p.read_text(encoding='utf-8')
anchor = "\nns['main']()\n"
if src.count(anchor) != 1:
    raise AssertionError(f'unexpected retry3 main anchor count: {src.count(anchor)}')
repair = r'''
# Repair the one remaining pre-existing cross-passage tag in P03. The question
# is about why "secret" is too broad; its local public/secret distinction is
# the appropriate assessment linkage, not Unit01 review target "protéger".
p3 = specs[2]
fixed=[]
seen=0
for typ,prompt,answer,targets in p3['items']:
    if prompt == 'Pourquoi le texte refuse-t-il d’appeler toute donnée non publiée un « secret » ?':
        if targets != ['secret','protéger']:
            raise AssertionError(f'unexpected P03 stale-tag shape: {targets}')
        targets=['secret','public']
        seen += 1
    fixed.append((typ,prompt,answer,targets))
if seen != 1:
    raise AssertionError(f'expected one P03 local-linkage repair, found {seen}')
p3['items']=fixed

# Preflight every authored question before invoking the original generator.
# This does not relax the generator guard; it proves all target forms are local.
offenders=[]
for s in specs:
    local=set(s['forms']) | set(s['reviews'])
    for i,item in enumerate(s['items'],1):
        bad=[f for f in item[3] if f not in local]
        if bad: offenders.append((s['id'],i,bad))
cp_local=set(new_forms)
for i,item in enumerate(cp['items'],1):
    bad=[f for f in item[3] if f not in cp_local]
    if bad: offenders.append((cp['id'],i,bad))
if offenders:
    raise AssertionError(f'Unit02 preflight non-local target forms: {offenders}')

ns['main']()
'''
src = src.replace(anchor, '\n' + repair)
code = compile(src, str(p), 'exec')
ns2 = {'__name__':'__main__','__file__':str(p),'__package__':None}
exec(code, ns2)
