#!/usr/bin/env python3
"""Retry Units 09-10 with exact visible review forms in four review contexts."""
from __future__ import annotations
import re
import generate_french_a1_units09_10 as base

_orig_u9 = base.build_u9
_orig_u10 = base.build_u10

def recount(row):
    row['word_count'] = len(row['text'].split())
    row['sentence_count'] = max(1, len(re.findall(r'[.!?](?:[»”"])?', row['text'])))

def build_u9(rows, L):
    unit = _orig_u9(rows, L)
    p03 = next(r for r in unit if r['id']=='fr-a1-u09-p03')
    old = 'Après avoir mangé, Camille veut appeler sa mère pour savoir quand elle rentre.'
    new = 'Après avoir mangé, Camille n’a plus besoin de manger, mais elle pense à boire avant d’appeler sa mère pour savoir quand elle rentre.'
    if p03['text'].count(old)!=1: raise AssertionError('U09-P03 retry source drift')
    p03['text']=p03['text'].replace(old,new); recount(p03)
    p04 = next(r for r in unit if r['id']=='fr-a1-u09-p04')
    old = 'Avant de dormir, Camille sent son téléphone vibrer sur la table.'
    new = 'Avant de dormir, Camille peut sentir son téléphone vibrer sur la table.'
    if p04['text'].count(old)!=1: raise AssertionError('U09-P04 retry source drift')
    p04['text']=p04['text'].replace(old,new); recount(p04)
    return unit

def build_u10(rows, L):
    unit = _orig_u10(rows, L)
    p03 = next(r for r in unit if r['id']=='fr-a1-u10-p03')
    old = 'Camille appelle sa mère avant d’aller au marché. Elle veut acheter un cahier pour l’école et demande quel prix elle peut accepter. Sa mère répond qu’un cahier simple ne doit pas coûter trop cher.'
    new = 'Camille doit appeler sa mère avant d’aller au marché. Elle veut acheter un cahier pour l’école et demande quel prix elle peut accepter. Sa mère peut répondre qu’un cahier simple ne doit pas coûter trop cher.'
    if p03['text'].count(old)!=1: raise AssertionError('U10-P03 retry source drift')
    p03['text']=p03['text'].replace(old,new); recount(p03)
    return unit

base.build_u9=build_u9
base.build_u10=build_u10
base.main()
