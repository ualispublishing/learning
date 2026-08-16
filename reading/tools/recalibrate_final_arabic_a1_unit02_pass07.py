#!/usr/bin/env python3
"""Guarded Pass 07 length remediation for Arabic A1 Unit 02."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / 'reading/arabic/a1/passages.jsonl'
TOKEN = re.compile(r'\S+')
SPECS = {
    'ar-a1-u02-p01': {
        'old_wc': 76,
        'sentence_increment': 1,
        'addition': 'وضعت زجاجة الماء في الحقيبة، وأغلقت النافذة، ثم سألت أمها عن دفتر صغير كان على الطاولة.',
    },
    'ar-a1-u02-p02': {
        'old_wc': 85,
        'sentence_increment': 1,
        'addition': 'في الصف تجلس بهدوء وتسمع شرح المعلم، ثم تكتب جملة قصيرة في دفترها.',
    },
    'ar-a1-u02-p03': {
        'old_wc': 87,
        'sentence_increment': 1,
        'addition': 'وضعت كتبها في مكانها، ثم ساعدت أمها في ترتيب الطاولة قبل النوم.',
    },
}


def wc(text: str) -> int:
    return len(TOKEN.findall(text))


def target_counts(row: dict) -> dict[str, int]:
    text = str(row.get('text', '')).casefold()
    return {
        str(t.get('id', t.get('form', ''))): text.count(str(t.get('form', '')).casefold())
        for t in row.get('new_lexical_targets', [])
        if str(t.get('form', '')).strip()
    }


def main() -> None:
    rows = [json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
    if len(rows) != 60:
        raise SystemExit(f'expected 60 A1 passages, found {len(rows)}')
    by_id = {r['id']: r for r in rows}
    if set(SPECS) - set(by_id):
        raise SystemExit('missing one or more Unit02 target passages')

    touched = []
    for pid, spec in SPECS.items():
        row = by_id[pid]
        if row.get('unit') != 2:
            raise SystemExit(f'{pid}: unexpected unit')
        old_text = str(row.get('text', '')).strip()
        stored = int(row.get('word_count', 0) or 0)
        actual = wc(old_text)
        if stored != spec['old_wc'] or actual != spec['old_wc']:
            raise SystemExit(f'{pid}: source changed; expected {spec["old_wc"]}, stored={stored}, actual={actual}')
        if spec['addition'] in old_text:
            raise SystemExit(f'{pid}: addition already present')

        before_targets = target_counts(row)
        before_questions = json.dumps(row.get('questions'), ensure_ascii=False, sort_keys=True)
        before_answers = json.dumps(row.get('answer_key'), ensure_ascii=False, sort_keys=True)
        before_metadata = json.dumps(row.get('new_lexical_targets'), ensure_ascii=False, sort_keys=True)

        row['text'] = old_text + ' ' + spec['addition']
        row['word_count'] = wc(row['text'])
        row['sentence_count'] = int(row.get('sentence_count', 0) or 0) + spec['sentence_increment']
        row['revision'] = int(row.get('revision', 0) or 0) + 1

        if not 90 <= row['word_count'] <= 140:
            raise SystemExit(f'{pid}: remediated count {row["word_count"]} outside A1 band')
        if target_counts(row) != before_targets:
            raise SystemExit(f'{pid}: new target occurrence count changed')
        if json.dumps(row.get('questions'), ensure_ascii=False, sort_keys=True) != before_questions:
            raise SystemExit(f'{pid}: questions changed')
        if json.dumps(row.get('answer_key'), ensure_ascii=False, sort_keys=True) != before_answers:
            raise SystemExit(f'{pid}: answer key changed')
        if json.dumps(row.get('new_lexical_targets'), ensure_ascii=False, sort_keys=True) != before_metadata:
            raise SystemExit(f'{pid}: target metadata changed')

        note = 'Final review Pass 07: expanded below-band passage into the A1 90-140 production band; questions and new-target exposure counts preserved.'
        notes = row.setdefault('quality', {}).setdefault('notes', [])
        if note not in notes:
            notes.append(note)
        touched.append((pid, stored, row['word_count']))

    for pid in ('ar-a1-u02-p04', 'ar-a1-u02-p05', 'ar-a1-u02-p06'):
        if int(by_id[pid].get('word_count', 0) or 0) < 90:
            raise SystemExit(f'{pid}: expected already inside A1 standard band')

    PATH.write_text('\n'.join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + '\n', encoding='utf-8')
    print(json.dumps({'level': 'A1', 'unit': 2, 'passages_touched': len(touched), 'word_counts': touched}, ensure_ascii=False))


if __name__ == '__main__':
    main()
