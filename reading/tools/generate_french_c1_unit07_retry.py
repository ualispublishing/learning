#!/usr/bin/env python3
"""Quality preflight for Unit07: extra interpretive depth + byte-stable prefix."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;p=HERE/'generate_french_c1_unit07.py'
ns={'__name__':'c1_u07_base','__file__':str(p),'__package__':None};exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
ns['EXTRA']=list(ns['EXTRA'])+[
"La critique vérifie également le niveau de voix auquel appartient chaque formulation. Une valeur peut être affirmée par un personnage, suggérée par le narrateur ou reconstruite par le lecteur; les confondre rendrait l’interprétation plus certaine que le texte lui-même.",
"La réception fournit enfin un test de portée. Une lecture qui dépend d’une convention culturelle précise doit annoncer cette dépendance et expliquer ce qui resterait intelligible pour un lecteur qui ne partage pas cette convention."
]
C1=ns['C1'];prefix=C1.read_text(encoding='utf-8');pre=[x for x in prefix.splitlines() if x.strip()]
if len(pre)!=36:raise AssertionError(f'Unit07 preflight expected 36 rows, got {len(pre)}')
ns['main']();lines=[x for x in C1.read_text(encoding='utf-8').splitlines() if x.strip()]
if len(lines)!=42:raise AssertionError(f'Unit07 writer expected 42 rows, got {len(lines)}')
C1.write_text(prefix.rstrip('\n')+'\n'+'\n'.join(lines[-6:])+'\n',encoding='utf-8')
