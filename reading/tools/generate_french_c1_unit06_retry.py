#!/usr/bin/env python3
"""Quality preflight for C1 Unit06; preserve the sealed prefix byte-for-byte."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;p=HERE/'generate_french_c1_unit06.py'
ns={'__name__':'c1_u06_base','__file__':str(p),'__package__':None};exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
base_extra=list(ns['EXTRA'])
ns['EXTRA']=base_extra+[
"Le dossier précise aussi qui porte la charge de justifier une mesure lorsqu’elle restreint fortement la situation d’une personne. Cette charge ne signifie pas qu’une seule partie doit prouver chaque détail; elle oblige surtout l’institution qui agit à rendre visibles les faits, la règle et le lien qui autorise la conséquence choisie.",
"Une erreur institutionnelle n’est pas traitée comme une simple imperfection administrative lorsque ses effets persistent. La voie de correction doit indiquer qui peut demander un nouvel examen, quelles informations peuvent être ajoutées et comment une décision corrigée modifie concrètement la restriction antérieure."
]
C1=ns['C1'];prefix=C1.read_text(encoding='utf-8');prefix_lines=[x for x in prefix.splitlines() if x.strip()]
if len(prefix_lines)!=30:raise AssertionError(f'Unit06 quality preflight expected 30-row sealed prefix, got {len(prefix_lines)}')
ns['main']()
all_lines=[x for x in C1.read_text(encoding='utf-8').splitlines() if x.strip()]
if len(all_lines)!=36:raise AssertionError(f'Unit06 writer expected 36 rows after generation, got {len(all_lines)}')
# The base writer validates the new rows but serializes the prefix again. Restore the
# exact locked bytes and append only the six validated Unit06 rows.
C1.write_text(prefix.rstrip('\n')+'\n'+'\n'.join(all_lines[-6:])+'\n',encoding='utf-8')
