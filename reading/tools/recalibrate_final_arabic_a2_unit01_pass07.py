#!/usr/bin/env python3
"""Guarded Pass 07 length remediation for Arabic A2 Unit 01."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / 'reading/arabic/a2/passages.jsonl'
TOKEN = re.compile(r'\S+')
SPECS = {
    'ar-a2-u01-p01': {
        'old_wc': 137,
        'sentence_increment': 1,
        'addition': 'ثم عادت إلى البيت وشرحت لأمها ما تعلمته في جولتها.',
    },
    'ar-a2-u01-p02': {
        'old_wc': 129,
        'sentence_increment': 1,
        'addition': 'في المساء راجع الأب وقت الإغلاق مع نور، واختار أن يخرج من العمل مبكرًا يوم الخميس.',
    },
    'ar-a2-u01-p03': {
        'old_wc': 123,
        'sentence_increment': 1,
        'addition': 'وفي صباح الجمعة أخبرت نور أسرتها بالخبر مرة أخرى، ووضعت وعاءين فارغين قرب المطبخ حتى يتذكروا تجهيز الماء.',
    },
    'ar-a2-u01-p04': {
        'old_wc': 129,
        'sentence_increment': 1,
        'addition': 'وقبل أن تغادرا، سألت نور عن ساعات العمل وكتبتها في دفترها للمرات المقبلة.',
    },
    'ar-a2-u01-p05': {
        'old_wc': 132,
        'sentence_increment': 1,
        'addition': 'وفي البيت احتفظت نور بالإيصال لتراجعه الأسرة إذا احتاجت إليه لاحقًا.',
    },
    'ar-a2-u01-p06': {
        'old_wc': 130,
        'sentence_increment': 1,
        'addition': 'وبعد ذلك صارت الأسرة تخطط لمشاويرها اليومية بهدوء أكبر، لأن كل خطوة أصبحت أوضح.',
    },
}


def wc(text: str) -> int:
    return len(TOKEN.findall(text))


def target_counts(row: dict) -> dict[str, int]:
    text = str(row.get('text', '')).casefold()
    out = {}
    for target in row.get('new_lexical_targets', []):
        form = str(target.get('form', '')).strip()
        if not form:
            raise SystemExit(f"{row['id']}: blank lexical target form")
        out[str(target.get('id', form))] = text.count(form.casefold())
    return out


def main() -> None:
    rows = [json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
    if len(rows) != 60:
        raise SystemExit(f'expected 60 A2 passages, found {len(rows)}')
    by_id = {row['id']: row for row in rows}
    missing = sorted(set(SPECS) - set(by_id))
    if missing:
        raise SystemExit(f'missing target passages: {missing}')

    touched = []
    for pid, spec in SPECS.items():
        row = by_id[pid]
        if row.get('unit') != 1:
            raise SystemExit(f'{pid}: expected unit 1')
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
        before_review = json.dumps(row.get('review_lexical_targets'), ensure_ascii=False, sort_keys=True)

        row['text'] = old_text + ' ' + spec['addition']
        row['word_count'] = wc(row['text'])
        row['sentence_count'] = int(row.get('sentence_count', 0) or 0) + spec['sentence_increment']
        row['revision'] = int(row.get('revision', 0) or 0) + 1

        if not 140 <= row['word_count'] <= 220:
            raise SystemExit(f'{pid}: remediated count {row["word_count"]} outside A2 standard band 140-220')
        if target_counts(row) != before_targets:
            raise SystemExit(f'{pid}: new lexical target literal occurrence count changed: {before_targets} -> {target_counts(row)}')
        if json.dumps(row.get('questions'), ensure_ascii=False, sort_keys=True) != before_questions:
            raise SystemExit(f'{pid}: questions changed unexpectedly')
        if json.dumps(row.get('answer_key'), ensure_ascii=False, sort_keys=True) != before_answers:
            raise SystemExit(f'{pid}: answer key changed unexpectedly')
        if json.dumps(row.get('new_lexical_targets'), ensure_ascii=False, sort_keys=True) != before_metadata:
            raise SystemExit(f'{pid}: new lexical target metadata changed unexpectedly')
        if json.dumps(row.get('review_lexical_targets'), ensure_ascii=False, sort_keys=True) != before_review:
            raise SystemExit(f'{pid}: review lexical target metadata changed unexpectedly')

        if pid.endswith('-p06'):
            if row.get('new_lexical_targets') != []:
                raise SystemExit(f'{pid}: P06 must retain zero new lexical targets')
            if row.get('speed_training', {}).get('new_word_policy') != 'none':
                raise SystemExit(f'{pid}: P06 new_word_policy must remain none')

        note = 'Final review Pass 07: expanded below-band passage into the A2 140-220 production band; assessment structure and new-target exposure counts preserved.'
        notes = row.setdefault('quality', {}).setdefault('notes', [])
        if note not in notes:
            notes.append(note)
        touched.append((pid, stored, row['word_count']))

    for row in rows[:6]:
        if not 140 <= int(row.get('word_count', 0) or 0) <= 220:
            raise SystemExit(f'{row["id"]}: Unit01 remains outside A2 standard band')

    PATH.write_text('\n'.join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + '\n', encoding='utf-8')
    print(json.dumps({'level': 'A2', 'unit': 1, 'passages_touched': len(touched), 'word_counts': touched}, ensure_ascii=False))


if __name__ == '__main__':
    main()
