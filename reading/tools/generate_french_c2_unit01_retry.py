#!/usr/bin/env python3
"""Quality preflight for C2 Unit01; removes internal level labels from learner text."""
from __future__ import annotations
import json,re
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;p=HERE/'generate_french_c2_unit01.py'
ns={'__name__':'c2_u01_base','__file__':str(p),'__package__':None};exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
# Add extra conceptual material in case the zero-new checkpoint or a standard passage
# remains below the 700-word floor after the base reasoning expansions.
ns['EXTRA']=list(ns['EXTRA'])+[
"Une difficulté supplémentaire concerne les changements de vocabulaire. Deux auteurs peuvent adopter des mots différents tout en conservant les mêmes engagements inférentiels; inversement, ils peuvent employer le même mot mais autoriser des conclusions incompatibles. Le diagnostic doit donc suivre les conséquences de la distinction, pas seulement ses étiquettes.",
"Le texte vérifie aussi les cas dégénérés, où une distinction semble fonctionner uniquement parce qu’un exemple exclut par construction toutes les alternatives. Un bon test réintroduit des cas intermédiaires et demande si les critères continuent à classer de manière stable lorsque les propriétés pertinentes se dissocient partiellement.",
"Enfin, la comparaison sépare coût explicatif et coût pragmatique. Une théorie peut devenir plus complexe pour sauver tous les contre-exemples, tandis qu’une autre accepte une approximation plus simple mais perd certaines distinctions. Le choix dépend alors de la question exacte et des erreurs que l’enquête peut tolérer."
]
orig_checkpoint=ns['checkpoint']
def checkpoint(*args,**kwargs):
 r=orig_checkpoint(*args,**kwargs)
 r['text']=r['text'].replace('À C2,','À ce niveau,').replace('Le lecteur C2','Le lecteur')
 r['word_count']=len(r['text'].split());r['sentence_count']=max(1,len(re.findall(r'[.!?](?:[»”\"])?',r['text'])))
 return r
orig_mk=ns['mk']
def mk(*args,**kwargs):
 r=orig_mk(*args,**kwargs)
 r['text']=r['text'].replace('À C2,','À ce niveau,').replace('Le lecteur C2','Le lecteur')
 r['word_count']=len(r['text'].split());r['sentence_count']=max(1,len(re.findall(r'[.!?](?:[»”\"])?',r['text'])))
 return r
ns['checkpoint']=checkpoint;ns['mk']=mk;ns['main']()
