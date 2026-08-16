#!/usr/bin/env python3
"""Retry French A2 Unit 02 by expanding every below-band draft in one pass."""
from __future__ import annotations
import re
import generate_french_a2_unit02 as base

_original_build=base.build
EXPANSIONS={
 'fr-a2-u02-p01':' Le lendemain, elle reprend son trajet habituel et compare simplement les heures d’arrivée. Cette seconde observation ne change pas sa conclusion précédente, mais elle lui rappelle qu’une seule journée ne suffit pas pour connaître exactement le comportement d’une ligne de transport.',
 'fr-a2-u02-p02':' Elle envoie ensuite un court message au groupe avec l’horaire confirmé et le nom du service qui l’a vérifié. Plusieurs élèves répondent qu’ils avaient vu les deux annonces et apprécient de savoir laquelle utiliser.',
 'fr-a2-u02-p03':' La semaine suivante, Sami teste sa propre manière de réviser pendant la même durée. Ils comparent ensuite leurs notes sans chercher un gagnant. Camille remarque surtout quels types de tâches l’aident et lesquels demandent davantage de temps.',
 'fr-a2-u02-p04':' Pour garder une trace, Camille note chaque soir si son sac était prêt et si elle avait oublié quelque chose. Après quelques jours supplémentaires, elle voit mieux les points utiles de son système et ceux qui demandent encore un petit ajustement.',
 'fr-a2-u02-p05':' Le responsable du club vérifie aussi le nombre de chaises et l’heure d’ouverture des salles. Avec ces détails, le groupe prépare un plan simple pour accueillir les participants sans déplacer tout le matériel au dernier moment.',
 'fr-a2-u02-p06':' Dans une nouvelle situation, Camille peut donc commencer par observer les faits, puis comparer plusieurs options avant d’agir. Elle accepte aussi de revoir son plan lorsque de nouveaux éléments apparaissent, au lieu de défendre automatiquement sa première réponse.'
}

def build(rows,D):
    unit=_original_build(rows,D)
    for r in unit:
        before={t['form']:base.count(r['text'],t['form']) for t in r.get('new_lexical_targets',[])}
        if r['word_count']<140:
            extra=EXPANSIONS[r['id']]
            r['text']+=extra
            r['word_count']=len(r['text'].split())
            r['sentence_count']=max(1,len(re.findall(r'[.!?](?:[»”"])?',r['text'])))
        if not 140<=r['word_count']<=220:
            raise AssertionError(f"{r['id']}: retry still outside A2 band at {r['word_count']}")
        after={t['form']:base.count(r['text'],t['form']) for t in r.get('new_lexical_targets',[])}
        if before!=after:
            raise AssertionError(f"{r['id']}: expansion changed deliberate target counts: {before} -> {after}")
    return unit

base.build=build
base.main()
