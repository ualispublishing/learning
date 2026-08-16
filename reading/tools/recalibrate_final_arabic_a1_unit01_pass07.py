#!/usr/bin/env python3
"""Guarded Pass 07 length remediation for Arabic A1 Unit 01.

Only passages below the 90-word A1 standard minimum are expanded. The additions
stay inside the existing scene, introduce no new lexical target occurrences,
and leave questions/answers/target metadata unchanged.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / 'reading/arabic/a1/passages.jsonl'
TOKEN = re.compile(r'\S+')

SPECS = {
    'ar-a1-u01-p01': {
        'old_wc': 59,
        'sentence_increment': 5,
        'addition': 'نظرت ليلى إلى الغرفة الصغيرة. رأت بابا ونافذة وكرسيا. وضعت حقيبتها قرب الكرسي، ثم مشت مع أمها إلى المطبخ. سألت عن غرفتها، فأشارت أمها إلى باب قريب. ابتسمت ليلى وقالت إن البيت مريح.',
    },
    'ar-a1-u01-p02': {
        'old_wc': 76,
        'sentence_increment': 1,
        'addition': 'في المساء جهزت ليلى حقيبتها للغد، ووضعت الكتاب بجانبها في غرفتها قبل أن تنام بهدوء.',
    },
    'ar-a1-u01-p03': {
        'old_wc': 78,
        'sentence_increment': 2,
        'addition': 'توقفت ليلى قرب شجرة كبيرة، ورأت طفلا يلعب بالكرة مع أخته. ثم شربت ماء مع أمها قبل العودة.',
    },
    'ar-a1-u01-p04': {
        'old_wc': 83,
        'sentence_increment': 2,
        'addition': 'جلست ليلى قرب أمها وفتحت الكتاب. قرأت صفحة قصيرة، ثم وضعت علامة صغيرة عند الصفحة التي وصلت إليها.',
    },
    'ar-a1-u01-p05': {
        'old_wc': 85,
        'sentence_increment': 1,
        'addition': 'في المساء رتبت ليلى الكتابين على طاولتها، ثم اختارت واحدا للقراءة صباح الغد.',
    },
}


def count(text: str) -> int:
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
    rows = [json.loads(line) for line in PATH.read_text(encoding='utf-8').splitlines() if line.strip()]
    if len(rows) != 60:
        raise SystemExit(f'expected 60 A1 passages, found {len(rows)}')

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
        old_wc = int(row.get('word_count', 0) or 0)
        actual_old_wc = count(old_text)
        if old_wc != spec['old_wc'] or actual_old_wc != spec['old_wc']:
            raise SystemExit(f'{pid}: source changed; expected {spec["old_wc"]}, stored={old_wc}, actual={actual_old_wc}')
        addition = spec['addition']
        if addition in old_text:
            raise SystemExit(f'{pid}: addition already present')

        before_targets = target_counts(row)
        before_questions = json.dumps(row.get('questions'), ensure_ascii=False, sort_keys=True)
        before_answers = json.dumps(row.get('answer_key'), ensure_ascii=False, sort_keys=True)
        before_target_metadata = json.dumps(row.get('new_lexical_targets'), ensure_ascii=False, sort_keys=True)

        row['text'] = old_text + ' ' + addition
        row['word_count'] = count(row['text'])
        row['sentence_count'] = int(row.get('sentence_count', 0) or 0) + int(spec['sentence_increment'])
        row['revision'] = int(row.get('revision', 0) or 0) + 1

        if not 90 <= row['word_count'] <= 140:
            raise SystemExit(f'{pid}: remediated word count {row["word_count"]} outside A1 standard band 90-140')
        if target_counts(row) != before_targets:
            raise SystemExit(f'{pid}: new lexical target literal occurrence count changed')
        if json.dumps(row.get('questions'), ensure_ascii=False, sort_keys=True) != before_questions:
            raise SystemExit(f'{pid}: questions changed unexpectedly')
        if json.dumps(row.get('answer_key'), ensure_ascii=False, sort_keys=True) != before_answers:
            raise SystemExit(f'{pid}: answer key changed unexpectedly')
        if json.dumps(row.get('new_lexical_targets'), ensure_ascii=False, sort_keys=True) != before_target_metadata:
            raise SystemExit(f'{pid}: lexical target metadata changed unexpectedly')

        quality = row.setdefault('quality', {})
        notes = quality.setdefault('notes', [])
        note = 'Final review Pass 07: expanded below-band passage into the A1 90-140 production band; questions and new-target exposure counts preserved.'
        if note not in notes:
            notes.append(note)
        touched.append((pid, spec['old_wc'], row['word_count']))

    untouched_unit1 = [r for r in rows if r.get('unit') == 1 and r['id'] not in SPECS]
    if [r['id'] for r in untouched_unit1] != ['ar-a1-u01-p06']:
        raise SystemExit(f'unexpected Unit 01 untouched set: {[r["id"] for r in untouched_unit1]}')
    if int(untouched_unit1[0].get('word_count', 0) or 0) < 90:
        raise SystemExit('ar-a1-u01-p06 unexpectedly below standard minimum')

    PATH.write_text('\n'.join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + '\n', encoding='utf-8')
    print(json.dumps({'level': 'A1', 'unit': 1, 'passages_touched': len(touched), 'word_counts': touched}, ensure_ascii=False))


if __name__ == '__main__':
    main()
