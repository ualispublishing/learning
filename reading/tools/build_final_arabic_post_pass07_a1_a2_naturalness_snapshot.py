#!/usr/bin/env python3
"""Build compact ending-context snapshots for A1/A2 passages changed by Pass 07.

The pre-existing prose already passed Pass 11. Pass 07 edits were append-only, so
this targeted re-review records the final 70 whitespace tokens: enough preceding
context to judge the transition plus all newly appended prose.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'reading/audit/final_arabic_post_pass07_a1_a2_naturalness_snapshot.jsonl'
TOKEN = re.compile(r'\S+')
MARKER = 'Final review Pass 07: expanded below-band passage'
EXPECTED = {'A1': 28, 'A2': 38}
BANDS = {'A1': (90, 140), 'A2': (140, 220)}
TAIL_TOKENS = 70

snapshot = []
counts = {'A1': 0, 'A2': 0}
for level in ('a1', 'a2'):
    rows = [
        json.loads(x)
        for x in (ROOT / f'reading/arabic/{level}/passages.jsonl').read_text(encoding='utf-8').splitlines()
        if x.strip()
    ]
    if len(rows) != 60 or len({r['id'] for r in rows}) != 60:
        raise SystemExit(f'{level}: expected 60 unique passages')
    cefr = level.upper()
    lo, hi = BANDS[cefr]
    for row in rows:
        tokens = TOKEN.findall(str(row.get('text', '')))
        actual = len(tokens)
        if actual != int(row.get('word_count', 0) or 0):
            raise SystemExit(f"{row['id']}: stored/actual word-count mismatch")
        if not lo <= actual <= hi:
            raise SystemExit(f"{row['id']}: outside current {cefr} production band")
        notes = row.get('quality', {}).get('notes', [])
        if any(MARKER in str(note) for note in notes):
            counts[cefr] += 1
            snapshot.append({
                'id': row['id'],
                'cefr': cefr,
                'unit': row['unit'],
                'sequence': row['sequence'],
                'word_count': actual,
                'title': row.get('title', ''),
                'ending_context': ' '.join(tokens[-TAIL_TOKENS:]),
                'new_target_forms': [t.get('form', '') for t in row.get('new_lexical_targets', [])],
                'existing_pass11_note': any('Pass 11' in str(note) for note in notes),
            })

if counts != EXPECTED:
    raise SystemExit(f'expected touched counts {EXPECTED}, found {counts}')
if len(snapshot) != 66:
    raise SystemExit(f'expected 66 touched passages, found {len(snapshot)}')

OUT.write_text('\n'.join(json.dumps(r, ensure_ascii=False) for r in snapshot) + '\n', encoding='utf-8')
print(json.dumps({'passages': len(snapshot), 'by_level': counts, 'tail_tokens': TAIL_TOKENS}, ensure_ascii=False))
