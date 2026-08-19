#!/usr/bin/env python3
"""Role-order, schema, and quality-depth preflight for French C2 Unit07."""
from pathlib import Path

HERE=Path(__file__).resolve().parent
p=HERE/'generate_french_c2_unit07.py'
ns={'__name__':'c2_u07_base','__file__':str(p),'__package__':None}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)

# Canonical six-passage cycle: sequence 3 interleaves prior material; sequence
# 4 transfers the method into a new task/context.
_original_specs=ns['specs']
def specs():
    rows=_original_specs()
    for row in rows:
        if row['id']=='fr-c2-u07-p03': row['ptype']='interleaved'
        if row['id']=='fr-c2-u07-p04': row['ptype']='transfer'
    return rows
ns['specs']=specs

# These are used only if fit() still needs material to reach the strict C2
# 700-word floor. They deepen interpretation rather than pad mechanically.
ns['EXTRA']=list(ns['EXTRA'])+[
    "Le checkpoint ajoute un examen des faux équivalents. Pour chaque paire de versions, le lecteur identifie un mot ou une structure qui semble correspondre facilement, puis vérifie si la fonction pragmatique, le registre et les présupposés restent effectivement comparables. Une ressemblance formelle devient ainsi une hypothèse à tester plutôt qu’une preuve d’équivalence.",
    "Une autre tâche impose une attribution prudente. Lorsqu’un exemple fait intervenir une pratique locale, le lecteur doit séparer ce qui est observé dans le dossier, ce que les personnages fictifs en disent et ce que l’analyste infère. Toute généralisation à une population plus large doit annoncer l’échantillon ou les documents supplémentaires qui seraient nécessaires.",
    "Le dossier examine aussi la compensation. Si une traduction perd un jeu de rythme, une ambiguïté ou un indice de registre à un endroit, le lecteur cherche si un autre choix peut rétablir une fonction comparable ailleurs sans inventer un contenu absent. Il explique ensuite pourquoi la compensation conserve l’effet pertinent ou pourquoi elle le transforme trop fortement.",
    "Enfin, le lecteur distingue compréhension et domestication. Une version plus facile à comprendre peut être préférable pour certains usages, mais elle ne doit pas effacer automatiquement les objets, noms ou pratiques qui constituent le contexte du texte. L’objectif est d’ajuster l’effort demandé au lecteur tout en gardant visibles les différences qui portent une information interprétative."
]

# `cultural` is a theme concept, not a schema domain. Keep the theme in topics
# and use the approved public/educational/professional domain vocabulary.
_orig_make=ns['make']
_orig_checkpoint=ns['checkpoint']
def make(*args,**kwargs):
    row=_orig_make(*args,**kwargs)
    row['domains']=['educational','public','professional']
    return row
def checkpoint(*args,**kwargs):
    row=_orig_checkpoint(*args,**kwargs)
    row['domains']=['educational','public','professional']
    return row
ns['make']=make
ns['checkpoint']=checkpoint

ns['main']()
