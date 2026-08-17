#!/usr/bin/env python3
"""Fail-closed repair/preflight wrapper for French B2 Unit08.

Keeps the selection-driven base generator intact while repairing one French
agreement issue and replacing an overlong checkpoint draft with a compact B2
synthesis that still exposes every selected target exactly.
"""
from pathlib import Path
import re

p=Path(__file__).with_name('generate_french_b2_unit08.py')
ns={'__name__':'unit08_base','__file__':str(p),'__package__':None}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)

orig_specs=ns['passage_specs']
def patched_specs(groups):
    specs=orig_specs(groups)
    old="Une explication historique n’est pas meilleure parce qu’elle paraît plus beau dans sa structure ou plus agréable à lire."
    new="Une explication historique n’est pas meilleure parce qu’elle met le beau en valeur dans sa structure ou paraît plus agréable à lire."
    if old not in specs[3]['paras'][0]:
        raise AssertionError('Unit08 P04 agreement-repair anchor drift')
    specs[3]['paras'][0]=specs[3]['paras'][0].replace(old,new)
    # Slightly cleaner formulation in the integration passage while preserving
    # exact review lemmas `présent`, `société` and `politique`.
    specs[4]['paras'][3]=specs[4]['paras'][3].replace(
        "connaître sa signification dans le présent ne doit pas effacer les options disponibles à l’époque.",
        "connaître sa signification pour le présent ne doit pas effacer les options disponibles à l’époque."
    )
    return specs
ns['passage_specs']=patched_specs

orig_checkpoint=ns['checkpoint']
def compact_checkpoint(groups,deck):
    row=orig_checkpoint(groups,deck)
    g1,g2,g3,g4,g5=[groups[f'p0{i}'] for i in range(1,6)]
    q=lambda f:'« '+f+' »'
    text=(
      "L’unité historique commence par la chronologie. Un film peut utiliser musique, chanson et montage pour jouer avec l’attention, mais l’explication doit encore établir ce qui vient avant quoi. "
      f"Les quatre repères {q(g1[0])}, {q(g1[1])}, {q(g1[2])} et {q(g1[3])} organisent le cadre temporel, les acteurs et le conflit sans transformer un événement spectaculaire en cause unique. "
      "Cette première étape oblige à reconstruire les options disponibles au moment de la décision. Elle empêche surtout de lire le passé comme si tous les acteurs connaissaient déjà le résultat final.\n\n"
      "La causalité ajoute une deuxième exigence : une histoire bien écrite ne se contente pas d’aligner un mot après l’autre. Elle décrit les mécanismes qui relient conditions, décisions et résultats. "
      f"Les cibles {q(g2[0])}, {q(g2[1])}, {q(g2[2])} et {q(g2[3])} servent à distinguer transformation, pression, mécanisme économique et crise ou condition. "
      "Chaque facteur doit être testé contre des explications concurrentes, contre la chronologie et contre les cas où l’effet attendu n’apparaît pas. Une relation devient plus convaincante lorsque l’on peut dire comment elle agit et ce qui la rendrait moins probable.\n\n"
      "Les sources ajoutent ensuite perspective et méthode. Le ton d’un texte influence la lecture, mais le sens dépend aussi du sujet, du public et de ce que son auteur pouvait connaître; il ne faut pas imaginer les silences sans indice. "
      f"Le groupe {q(g3[0])}, {q(g3[1])}, {q(g3[2])} et {q(g3[3])} rappelle qu’il faut identifier la trace, son expérience ou conservation du passé, sa perspective et la méthode de contrôle. "
      f"Le groupe {q(g4[0])}, {q(g4[1])}, {q(g4[2])} et {q(g4[3])} sert ensuite à comparer conflit, autorité, composition des groupes et échelle d’analyse. "
      "Un avis peut être élégant, et un lecteur peut aimer un récit beau ou drôle, mais le style ne résout pas un désaccord documentaire. Une comparaison solide demande ce que chaque explication rend visible et comment elle répond à la meilleure objection.\n\n"
      "Enfin, la synthèse relie l’événement à la vie des acteurs. Le présent, la société et la politique créent des contraintes sans transformer les personnes en marionnettes. "
      f"Les quatre dernières cibles {q(g5[0])}, {q(g5[1])}, {q(g5[2])} et {q(g5[3])} structurent respectivement l’action, l’acteur, le mécanisme explicatif et sa qualification. "
      "Expliquer le passé consiste alors à relier ces niveaux sans les confondre : dire ce qui s’est passé, établir l’ordre, comparer les sources, proposer des mécanismes, tester les contrearguments et préciser la force de la conclusion. Une bonne explication historique rend certains résultats compréhensibles sans les déclarer inévitables."
    )
    row['text']=text
    row['word_count']=len(text.split())
    row['sentence_count']=max(1,len(re.findall(r'[.!?](?:[»”"])?',text)))
    row['quality']['notes'].append('Checkpoint compacted during preflight to preserve all 20 exact reviews inside the B2 word band.')
    return row
ns['checkpoint']=compact_checkpoint

# Selection/locality preflight before delegating to the full base guards.
groups=ns['load_selection']()
flat=[f for k in ['p01','p02','p03','p04','p05'] for f in groups[k]]
if len(flat)!=20 or len(set(flat))!=20:
    raise AssertionError('Unit08 preflight selection uniqueness failure')

ns['main']()
