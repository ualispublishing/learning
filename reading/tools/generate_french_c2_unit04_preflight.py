#!/usr/bin/env python3
"""Quality preflight wrapper for French C2 Unit04 generation."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
base_path = HERE / 'generate_french_c2_unit04.py'
ns = {'__name__': 'c2_u04_base', '__file__': str(base_path), '__package__': None}
exec(compile(base_path.read_text(encoding='utf-8'), str(base_path), 'exec'), ns)

_original_specs = ns['specs']

def specs():
    rows = _original_specs()
    replacements = {
        'fr-c2-u04-p03': 'transfer',
        'fr-c2-u04-p04': 'interleaved',
    }
    for row in rows:
        if row['id'] in replacements:
            row['ptype'] = replacements[row['id']]
    return rows

ns['specs'] = specs

# The cumulative checkpoint has to carry the same C2 reasoning depth as the
# standard passages. These paragraphs extend causal diagnosis rather than pad
# the word count, and fit() still enforces the 700–1200 band strictly.
ns['EXTRA'] = list(ns['EXTRA']) + [
    "Le checkpoint ajoute une comparaison de temporalités. Une décision peut améliorer un résultat immédiatement tout en réduisant une capacité d’adaptation qui ne devient visible qu’après un choc. À l’inverse, une réserve coûteuse aujourd’hui peut n’avoir de valeur que dans un scénario rare. L’analyse doit donc rendre explicite l’horizon sur lequel elle compare les options au lieu de sommer des effets qui n’apparaissent pas au même moment.",
    "Il distingue aussi robustesse et optimalité. Une option peut être la meilleure sous une hypothèse précise et devenir médiocre dès qu’un paramètre plausible change légèrement. Une autre peut ne jamais être optimale dans le scénario central mais rester acceptable dans une gamme plus large de situations. Cette différence fournit un dernier test de prudence lorsque l’incertitude porte sur la structure elle-même."
]

ns['main']()
