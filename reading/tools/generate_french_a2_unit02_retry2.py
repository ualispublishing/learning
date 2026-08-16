#!/usr/bin/env python3
"""Retry Unit 02 after making all Unit-01 bridge reviews exact and visible."""
from __future__ import annotations
import re
import generate_french_a2_unit02_retry as retry
import generate_french_a2_unit02 as base

_original_build=retry.build
REVIEW_LINES={
 'fr-a2-u02-p01':' Le conseil de Sami reste utile même si le retard observé la semaine précédente ne se répète pas.',
 'fr-a2-u02-p02':' Pour expliquer l’erreur aux autres élèves, Camille montre simplement les deux horaires et la confirmation du secrétariat.',
 'fr-a2-u02-p03':' Il reste possible d’essayer une méthode pendant quelques jours sans croire qu’elle convient automatiquement à tout le monde.',
 'fr-a2-u02-p04':' Elle ne cherche pas à réparer toute sa routine en une soirée ; elle veut surtout éviter les oublis les plus fréquents.',
 'fr-a2-u02-p05':' Après le rendez-vous, les membres du club veulent découvrir si leur organisation fonctionne aussi bien quand davantage de participants arrivent.'
}

def build(rows,D):
    unit=_original_build(rows,D)
    for r in unit:
        before={t['form']:base.count(r['text'],t['form']) for t in r.get('new_lexical_targets',[])}
        missing=[t['form'] for t in r.get('review_lexical_targets',[]) if t.get('representation') in {'running_text','summary'} and base.count(r['text'],t['form'])<1]
        if missing:
            line=REVIEW_LINES.get(r['id'])
            if not line:
                raise AssertionError(f"{r['id']}: invisible reviews without bounded repair: {missing}")
            r['text']+=line
            r['word_count']=len(r['text'].split())
            r['sentence_count']=max(1,len(re.findall(r'[.!?](?:[»”"])?',r['text'])))
        still=[t['form'] for t in r.get('review_lexical_targets',[]) if t.get('representation') in {'running_text','summary'} and base.count(r['text'],t['form'])<1]
        if still:
            raise AssertionError(f"{r['id']}: reviews still invisible after repair: {still}")
        after={t['form']:base.count(r['text'],t['form']) for t in r.get('new_lexical_targets',[])}
        if before!=after:
            raise AssertionError(f"{r['id']}: bridge-review repair changed new-target counts: {before} -> {after}")
        if not 140<=r['word_count']<=220:
            raise AssertionError(f"{r['id']}: bridge-review repair moved passage out of band: {r['word_count']}")
    return unit

retry.build=build
base.build=build
base.main()
