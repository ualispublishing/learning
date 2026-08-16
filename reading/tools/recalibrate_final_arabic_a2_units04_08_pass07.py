#!/usr/bin/env python3
"""Guarded final Pass 07 length remediation for the 21 remaining short A2 passages.

The worklist is frozen from final_arabic_pass07_a2_short_snapshot.jsonl after
Units 01-03 were remediated. Every edit is append-only, target-neutral, and
fails closed on any source drift or lexical-target occurrence change.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / 'reading/arabic/a2/passages.jsonl'
TOKEN = re.compile(r'\S+')
NOTE = (
    'Final review Pass 07: expanded below-band passage into the A2 140-220 '
    'production band; assessment structure and new-target exposure counts preserved.'
)

SPECS = {
    'ar-a2-u04-p01': (125, 4, 'وفي البيت وضعت الأم الأرز في وعاء صغير، وسجلت ما استهلكته الأسرة خلال الأيام التالية لتعرف هل كان قرار الشراء مناسبًا.'),
    'ar-a2-u04-p02': (135, 4, 'وفي البيت وضعت نور الحقيبة الجديدة قرب كتبها واستعملتها في اليوم التالي.'),
    'ar-a2-u04-p03': (123, 4, 'وفي نهاية الأسبوع قارنت نور الوقت الذي أمضته في التمارين الجديدة بما تعلمته منها، ثم قررت الاكتفاء بالجزء المجاني شهرًا آخر.'),
    'ar-a2-u04-p04': (126, 4, 'وعند العودة إلى البيت احتفظت الأم بالفاتورة والعلبة يومين، ثم استخدمت المصباح عدة مرات للتأكد من عمله جيدًا.'),
    'ar-a2-u04-p05': (129, 4, 'وبعد أسبوع استخدمت نور الكرسي كل يوم، وبقي ثابتًا ولم تظهر فيه مشكلة جديدة.'),
    'ar-a2-u04-p06': (134, 4, 'وفي المرة التالية كتبت نور حاجتها أولًا قبل مقارنة الخيارات.'),
    'ar-a2-u05-p01': (138, 5, 'وفي الأسبوع التالي اختارت نور مشهدًا جديدًا قرب السوق وجرّبت زوايا مختلفة.'),
    'ar-a2-u05-p02': (135, 5, 'وفي نهاية الشهر رتبت نور الصور بحسب التاريخ لتلاحظ التغير بوضوح أكبر.'),
    'ar-a2-u05-p03': (136, 5, 'وفي النهاية راجعت نور الجدول مع المعلمة قبل تسليم العمل.'),
    'ar-a2-u05-p04': (133, 5, 'وبعد شهر لاحظت هدى أنها فتحت الكتاب تلقائيًا في معظم الأمسيات، حتى عندما كانت متعبة.'),
    'ar-a2-u05-p05': (134, 5, 'ثم طلبت من الطالب أن يشرح بنفسه الفرق بين صورتين في اللقاء القادم.'),
    'ar-a2-u06-p01': (130, 6, 'وفي رحلة العودة كانت نور تعرف الترتيب، فانتقلت بين الشاشات والبوابة بهدوء أكبر وساعدت أخاها الصغير في قراءة الرقم.'),
    'ar-a2-u06-p02': (130, 6, 'بعد عودتهما كتبت هدى وقت التأخير في ملاحظاتها، وقالت إن تحديث المعلومات ساعدهما على اتخاذ القرار بهدوء.'),
    'ar-a2-u06-p03': (138, 6, 'وعند العودة اختارت نور الخطة نفسها لأنها منحتها وقتًا كافيًا.'),
    'ar-a2-u06-p04': (131, 6, 'وفي طريق العودة سلكت نور المسار عبر الحديقة لأنه كان أبسط للمشي.'),
    'ar-a2-u06-p05': (129, 6, 'وفي اليوم التالي رتبت نور الصور حسب مراحل الطريق وشاركتها مع جدتها في البيت.'),
    'ar-a2-u07-p01': (134, 7, 'وفي المساء كتبت نور للمنظمين ملاحظتين عن حركة الزوار قرب المدخل.'),
    'ar-a2-u07-p03': (138, 7, 'وفي الأسبوع التالي ناقش النادي الاقتراح مع إدارة المدرسة وبعض الأسر.'),
    'ar-a2-u07-p04': (134, 7, 'وبعد أسبوعين راجع العاملون الأرقام مرة ثانية للتأكد من أن التغيير أفاد المستخدمين.'),
    'ar-a2-u07-p05': (136, 7, 'ثم قرأوا ملخصاتهم بصوت مرتفع وشرح كل طالب سبب اختياره للمعلومات.'),
    'ar-a2-u08-p04': (133, 8, 'وفي نهاية الزيارة غسلت الأسرة أيديها وسجلت نور ملاحظات قصيرة عن الأشياء التي رأتها.'),
}


def wc(text: str) -> int:
    return len(TOKEN.findall(text))


def target_counts(row: dict) -> dict[str, int]:
    text = str(row.get('text', '')).casefold()
    out: dict[str, int] = {}
    for target in row.get('new_lexical_targets', []):
        form = str(target.get('form', '')).strip()
        if not form:
            raise SystemExit(f"{row['id']}: blank new lexical target form")
        out[str(target.get('id', form))] = text.count(form.casefold())
    return out


def stable(row: dict, key: str) -> str:
    return json.dumps(row.get(key), ensure_ascii=False, sort_keys=True)


def main() -> None:
    rows = [json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
    if len(rows) != 60 or len({r['id'] for r in rows}) != 60:
        raise SystemExit('expected 60 unique A2 passages')
    by_id = {r['id']: r for r in rows}
    missing = sorted(set(SPECS) - set(by_id))
    if missing:
        raise SystemExit(f'missing targets: {missing}')

    live_short = {r['id'] for r in rows if int(r.get('word_count', 0) or 0) < 140}
    if live_short != set(SPECS):
        raise SystemExit(
            'live below-band worklist differs from frozen 21-passage set; '
            f'missing_from_spec={sorted(live_short-set(SPECS))}, '
            f'no_longer_short={sorted(set(SPECS)-live_short)}'
        )

    touched = []
    for pid, (expected_wc, expected_unit, addition) in SPECS.items():
        row = by_id[pid]
        old_text = str(row.get('text', '')).strip()
        stored_wc = int(row.get('word_count', 0) or 0)
        actual_wc = wc(old_text)
        if row.get('unit') != expected_unit:
            raise SystemExit(f'{pid}: expected unit {expected_unit}, found {row.get("unit")}')
        if stored_wc != expected_wc or actual_wc != expected_wc:
            raise SystemExit(
                f'{pid}: source drift; expected {expected_wc}, stored={stored_wc}, actual={actual_wc}'
            )
        if addition in old_text:
            raise SystemExit(f'{pid}: addition already present')

        before_targets = target_counts(row)
        before_questions = stable(row, 'questions')
        before_answers = stable(row, 'answer_key')
        before_new_meta = stable(row, 'new_lexical_targets')
        before_review_meta = stable(row, 'review_lexical_targets')
        before_speed = stable(row, 'speed_training')
        before_notes = list(row.get('quality', {}).get('notes', []))

        row['text'] = old_text + ' ' + addition
        row['word_count'] = wc(row['text'])
        row['sentence_count'] = int(row.get('sentence_count', 0) or 0) + 1
        row['revision'] = int(row.get('revision', 0) or 0) + 1

        if not 140 <= row['word_count'] <= 220:
            raise SystemExit(f'{pid}: remediated count {row["word_count"]} outside A2 140-220 band')
        if target_counts(row) != before_targets:
            raise SystemExit(
                f'{pid}: new-target literal occurrence count changed: '
                f'{before_targets} -> {target_counts(row)}'
            )
        if stable(row, 'questions') != before_questions:
            raise SystemExit(f'{pid}: questions changed unexpectedly')
        if stable(row, 'answer_key') != before_answers:
            raise SystemExit(f'{pid}: answer key changed unexpectedly')
        if stable(row, 'new_lexical_targets') != before_new_meta:
            raise SystemExit(f'{pid}: new lexical target metadata changed unexpectedly')
        if stable(row, 'review_lexical_targets') != before_review_meta:
            raise SystemExit(f'{pid}: review lexical target metadata changed unexpectedly')
        if stable(row, 'speed_training') != before_speed:
            raise SystemExit(f'{pid}: speed-training policy changed unexpectedly')
        if any(note not in row.get('quality', {}).get('notes', []) for note in before_notes):
            raise SystemExit(f'{pid}: pre-existing quality note was lost')

        notes = row.setdefault('quality', {}).setdefault('notes', [])
        if NOTE not in notes:
            notes.append(NOTE)
        touched.append((pid, expected_wc, row['word_count']))

    # Unit 04 P06 is the only cumulative P06 in this batch; zero-new-word policy is inviolable.
    p06 = by_id['ar-a2-u04-p06']
    if p06.get('new_lexical_targets') != []:
        raise SystemExit('ar-a2-u04-p06: new lexical targets must remain empty')
    if p06.get('speed_training', {}).get('new_word_policy') != 'none':
        raise SystemExit('ar-a2-u04-p06: new_word_policy must remain none')

    outside = [(r['id'], int(r.get('word_count', 0) or 0)) for r in rows if not 140 <= int(r.get('word_count', 0) or 0) <= 220]
    if outside:
        raise SystemExit(f'A2 passages remain outside standard band: {outside}')

    units = Counter(by_id[pid]['unit'] for pid in SPECS)
    PATH.write_text(
        '\n'.join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + '\n',
        encoding='utf-8',
    )
    print(json.dumps({
        'level': 'A2',
        'units': dict(sorted(units.items())),
        'passages_touched': len(touched),
        'word_counts': touched,
        'all_60_in_standard_band': True,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
