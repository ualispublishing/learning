#!/usr/bin/env python3
"""Run the 15-pass whole-French audit with the U05 literary-prose repair criterion corrected.

The base audit is retained verbatim except for the one deferred-finding predicate:
Unit05 P01 must remain the planned literary-prose slot *and* must contain the
sustained original Maëlle narrative produced by the final repair. Relabeling the
old analytical passage is not accepted as a repair.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
base = HERE / 'audit_french_final_whole.py'
src = base.read_text(encoding='utf-8')
old = """    if norm(c2id['fr-c2-u05-p01']['genre']) == 'literary prose':
        errors.append('fr-c2-u05-p01: deferred genre repair missing (analytical commentary mislabeled literary prose)')
"""
new = """    u05p01 = c2id['fr-c2-u05-p01']
    u05text = norm(u05p01.get('text', ''))
    if norm(u05p01.get('genre', '')) != 'literary prose':
        errors.append('fr-c2-u05-p01: Unit05 requires a genuine literary-prose slot; genre was relabeled instead of repaired')
    if 'maëlle' not in u05text or 'à la fin d’un long trajet' not in u05text or 'ancien atelier' not in u05text:
        errors.append('fr-c2-u05-p01: sustained original Maëlle literary rewrite is not present')
    analytical_openers = ['le texte propose', 'le passage analyse', 'l’analyse commence', 'la critique commence']
    if any(x in u05text[:800] for x in analytical_openers):
        errors.append('fr-c2-u05-p01: learner-facing opening still reads as analytical commentary rather than literary prose')
"""
if old not in src:
    raise AssertionError('Base final-audit U05 predicate changed; review before applying v2 wrapper')
src = src.replace(old, new, 1)
ns = {'__name__': '__main__', '__file__': str(base), '__package__': None}
exec(compile(src, str(base), 'exec'), ns)
