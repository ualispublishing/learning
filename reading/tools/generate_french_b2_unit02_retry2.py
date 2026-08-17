#!/usr/bin/env python3
"""Fail-closed retry for French B2 Unit 02.

Repairs only three stale Unit01 lexical tags in the Unit02 zero-new checkpoint.
The underlying passage text, 20-word Unit02 pool, B2 word band and all guards
remain unchanged.
"""
from pathlib import Path
p=Path(__file__).with_name('generate_french_b2_unit02.py')
src=p.read_text(encoding='utf-8')
rep={
"('argument_relation','Comment le cas de la promesse se distingue-t-il du cas de l’incident grave ?','La promesse peut souvent attendre une preuve, tandis qu’un incident grave peut exiger une solution immédiate et proportionnée sous responsabilité.',['promettre','preuve','grave','solution','responsabilité'])":"('argument_relation','Comment le cas de la promesse se distingue-t-il du cas de l’incident grave ?','La promesse peut souvent attendre une preuve, tandis qu’un incident grave peut exiger une solution immédiate et proportionnée sous responsabilité.',['promettre','grave','solution','responsabilité'])",
"('cause_effect','Pourquoi calmer le processus peut-il aider sans minimiser le danger ?','Parce que calmer réduit le bruit décisionnel et permet de choisir une action qui protège sans dépasser inutilement l’information disponible.',['calmer','protéger'])":"('cause_effect','Pourquoi calmer le processus peut-il aider sans minimiser le danger ?','Parce que calmer réduit le bruit décisionnel et permet de choisir une action qui protège sans dépasser inutilement l’information disponible.',['calmer'])",
"('assumption','Quelle condition rend l’attente raisonnable plutôt que passive ?','Attendre doit avoir une chance réelle d’apporter une information susceptible de changer la décision, sans créer un coût supérieur au bénéfice attendu.',['attendre','apporter'])":"('assumption','Quelle condition rend l’attente raisonnable plutôt que passive ?','Attendre doit avoir une chance réelle d’apporter une information susceptible de changer la décision, sans créer un coût supérieur au bénéfice attendu.',['attendre'])"
}
for old,new in rep.items():
    if src.count(old)!=1: raise AssertionError(f'expected exactly one checkpoint tag anchor, found {src.count(old)}')
    src=src.replace(old,new)
code=compile(src,str(p),'exec')
ns={'__name__':'__main__','__file__':str(p),'__package__':None}
exec(code,ns)
