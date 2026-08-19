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
ns['main']()
