#!/usr/bin/env python3
"""Apply fresh Arabic Gate B C2 Unit 10 assessment/naturalness repairs."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / 'reading'
PATH = R / 'arabic/c2/passages.jsonl'
RELEASE = R / 'RELEASE_STATUS.json'
INV = R / 'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'
DD = R / 'audit/arabic_gate_b_decisions_2026-08-30'
IDS = [f'ar-c2-u10-p{i:02d}' for i in range(1, 7)]
TOKEN = re.compile(r'\S+')
NOTE = '2026-09-05 fresh Gate B naturalness review (C2 Unit 10): learner-facing prose/Q/A reviewed passage by passage; only high-confidence summary/detail assessment-alignment and MSA grammar/naturalness repairs applied; no educator/publication release claim.'
SUMMARY_PROMPT = 'لخّص في جملة واحدة القضية أو الإشكال المركزي الذي ينظم النص حوله تحليله أو تأويله.'
Q2_PROMPT = 'ما نوعان من الأدلة أو الطبقات اللذان يقارنهما النص؟'
OLD_Q1 = 'أن الحكم المتقدم يتطلب إعادة بناء الادعاء ومقدماته وآلياته وحدود الأدلة قبل تقييمه.'
OLD_Q2 = 'يقارن بين مصادر أو قواعد أو نماذج أو آليات مختلفة بحسب النص.'

Q1_REPAIRS = {
    'ar-c2-u10-p01': 'القضية هي أن الحكم على عدالة توزيع مورد نادر يتطلب تحديد غاية الإنصاف وفصل المؤشر عن تاريخ الفرص والحوافز التي يصنعها، ثم إبقاء القاعدة قابلة للمراجعة.',
    'ar-c2-u10-p02': 'القضية هي أن اختيار نموذج لا يحسمه التعقيد أو الدقة التاريخية وحدهما، بل يتطلب موازنة الدقة والتشخيص والتفسير والتحديث والمراقبة بحسب وظيفة القرار ومخاطر الخطأ.',
    'ar-c2-u10-p03': 'القضية هي أن العبارة المشتركة بين مؤسستين لا تصبح قابلة للتطبيق بمجرد ترجمتها، بل يجب إعادة بناء الحدث والزمن والسلطة والقياس حتى تحمل معنى تشغيليا مشتركا.',
    'ar-c2-u10-p04': 'القضية هي أن استخدام سجل تاريخي ناقص في قرار مستقبلي قد يعيد إنتاج تحيزات التسجيل نفسها، لذلك يجب فصل الوصف والسبب والقرار واختبار السياسة بقياس مستقل وقابل للرجوع.',
    'ar-c2-u10-p05': 'القضية هي أن القصة والرقم لا يتعارضان بذاتهما، لأن كلا منهما يؤدي وظيفة مختلفة في الحجة، ويجب فحص الانتشار والتوزيع والزمن والأدلة المضادة قبل تحويل العرض إلى حكم.',
    'ar-c2-u10-p06': 'القضية هي أن القراءة المتقدمة تعيد بناء الادعاء ومقدماته وآليته وأقوى بديل له وحدود أدلته، ثم تصوغ حكما مؤقتا قابلا للمراجعة بدل مساواة البدائل أو ادعاء يقين غير مبرر.',
}

Q2_REPAIRS = {
    'ar-c2-u10-p01': 'يقارن النص بين القاعدة وغايات الإنصاف التي تعلنها من جهة، وبين بيانات الأداء السابق وتاريخ فرص الوصول الذي أنتج تلك البيانات من جهة أخرى.',
    'ar-c2-u10-p02': 'يقارن النص بين دقة النموذجين على البيانات التاريخية وبين قدرتهما على التشخيص والتحديث والعمل عند تغير البيئة.',
    'ar-c2-u10-p03': 'يقارن النص بين المعنى اللغوي العام لعبارة «استجابة سريعة» وبين تعريفها التشغيلي في الحدث والزمن والقياس والمسؤولية.',
    'ar-c2-u10-p04': 'يقارن النص بين سجل البلاغات التاريخي وبين مصادر مستقلة نسبيا مثل سجلات الإصلاح وزيارات الطوارئ وشهادات المؤسسات المحلية.',
    'ar-c2-u10-p05': 'يقارن النص بين القصص الفردية التي تكشف إمكان الأثر وآليته وبين المقاييس الكمية التي تصف انتشاره وتوزيعه عبر المجموعة.',
    'ar-c2-u10-p06': 'يقارن النص بين الأدلة التي تسند الادعاء وبين التفسير المنافس والأدلة المضادة التي قد تحد الادعاء أو تغير درجة الثقة فيه.',
}

TEXT_REPAIRS = {
    'ar-c2-u10-p01': [
        ('إذا عرف الفرق أن طول سجلها السابق يرفع فرصتها، فقد تسعى إلى زيادة عدد التجارب الصغيرة بدل اختيار الأسئلة الأهم.',
         'إذا عرفت الفرق أن طول سجلها السابق يرفع فرصتها، فقد تسعى إلى زيادة عدد التجارب الصغيرة بدل اختيار الأسئلة الأهم.'),
    ],
    'ar-c2-u10-p02': [
        ('قارنت القرارين تحت خطأين مختلفين.', 'قارنت النموذجين في ضوء نوعين مختلفين من الخطأ.'),
        ('نجاح شديد على البيانات القديمة قد يعكس تعلم تفاصيل لا تنتقل.', 'أداء مرتفع جدا على البيانات القديمة قد يعكس تعلم تفاصيل لا تنتقل.'),
    ],
    'ar-c2-u10-p03': [
        ('ثم اختبار هل الصياغة الجديدة تنتج السلوك الذي قصده الطرفان.', 'ثم اختبار ما إذا كانت الصياغة الجديدة تنتج السلوك الذي قصده الطرفان.'),
    ],
    'ar-c2-u10-p04': [
        ('لم ينتقل الفريق فورًا إلى مساواة الموارد؛ ضيق فقط الثقة في تفسير الرقم الأصلي.', 'لم ينتقل الفريق فورًا إلى مساواة الموارد؛ قلل فقط مستوى الثقة في تفسير الرقم الأصلي.'),
    ],
    'ar-c2-u10-p05': [],
    'ar-c2-u10-p06': [],
}

ANSWER_REPAIRS = {
    'ar-c2-u10-p01': {},
    'ar-c2-u10-p02': {},
    'ar-c2-u10-p03': {},
    'ar-c2-u10-p04': {
        'q6': (
            'الأول يغلق عدم اليقين ويخلط التسجيل بالحاجة، أما الثاني يبين أن النتيجة تتغير بحسب سبب الغياب ويجعل مجال الصلاحية واضحًا للمستخدم اللاحق.',
            'الأول يغلق عدم اليقين ويخلط التسجيل بالحاجة، أما الثاني فيبين أن النتيجة تتغير بحسب سبب الغياب ويجعل مجال الصلاحية واضحًا للمستخدم اللاحق.',
        )
    },
    'ar-c2-u10-p05': {},
    'ar-c2-u10-p06': {
        'q6': (
            'الأول يسوي بين التفسيرات ويتوقف عن التقييم، أما الثاني يحدد ما هو ثابت وما هو مختلف وما الدليل المفقود ويتيح حكمًا مؤقتًا معايرًا.',
            'الأول يسوي بين التفسيرات ويتوقف عن التقييم، أما الثاني فيحدد ما هو ثابت وما هو مختلف وما الدليل المفقود ويتيح حكمًا مؤقتًا معايرًا.',
        )
    },
}

META = {
    pid: [
        ('answer q1', 'assessment_wording', 'moderate', 'The q1 prompt requires a standalone one-sentence summary, but the keyed response is the same generic أن-fragment reused across all six distinct capstone passages; replace it with a complete passage-specific summary.'),
        ('answer q2', 'assessment_alignment', 'moderate', 'The q2 prompt asks for two evidence types or layers compared in this passage, but the keyed response is a generic placeholder that names several possible categories “depending on the text”; replace it with the two passage-specific layers.'),
    ]
    for pid in IDS
}
META['ar-c2-u10-p01'].append(('text', 'grammar', 'moderate', 'The plural non-human subject «الفرق» is already resumed by feminine-singular pronouns «سجلها/فرصتها»; the verb should agree consistently as «عرفت الفرق».'))
META['ar-c2-u10-p02'].extend([
    ('text', 'naturalness', 'moderate', 'The phrase «قارنت القرارين تحت خطأين مختلفين» is a calque-like collocation in MSA; compare the two models «في ضوء نوعين مختلفين من الخطأ».'),
    ('text', 'naturalness', 'moderate', 'The phrase «نجاح شديد على البيانات القديمة» is not idiomatic technical MSA for high historical performance; use «أداء مرتفع جدا على البيانات القديمة».'),
])
META['ar-c2-u10-p03'].append(('text', 'grammar', 'moderate', 'The sequence «اختبار هل الصياغة...» is awkward in this nominal construction; use the standard «اختبار ما إذا كانت الصياغة...».'))
META['ar-c2-u10-p04'].extend([
    ('text', 'naturalness', 'moderate', 'The collocation «ضيق الثقة» is unnatural in MSA; express the intended calibration as reducing the level of confidence.'),
    ('answer q6', 'grammar', 'moderate', 'After contrastive «أما», the second member requires the linking fa; use «أما الثاني فيبين...».'),
])
META['ar-c2-u10-p06'].append(('answer q6', 'grammar', 'moderate', 'After contrastive «أما», the second member requires the linking fa; use «أما الثاني فيحدد...».'))


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def wc(text: str) -> int:
    return len(TOKEN.findall(text))


def targets(record: dict) -> dict[str, int]:
    forms: list[str] = []
    for key in ('new_lexical_targets', 'review_lexical_targets'):
        for item in record.get(key, []):
            form = item.get('form')
            if isinstance(form, str) and form and form not in forms:
                forms.append(form)
    text = record.get('text', '')
    return {form: text.count(form) for form in forms}


def main() -> None:
    raw = PATH.read_bytes()
    pre = sha(raw)
    release = json.loads(RELEASE.read_text(encoding='utf-8'))
    arabic = release['languages']['arabic']
    progress = arabic['naturalness_review_progress']
    gate = arabic['latest_deterministic_gate']
    if arabic.get('release_state') != 'REOPEN_REQUIRED' or arabic.get('educator_release_ready') is not False:
        raise SystemExit('release gate drift')
    if (progress.get('fresh_records_reviewed'), progress.get('fresh_records_with_findings'), progress.get('fresh_findings'), gate.get('open_findings')) != (354, 302, 541, 1104):
        raise SystemExit('C2 Unit 10 frontier drift')
    if progress.get('status') != 'FRESH_GATE_B_INTERNAL_REVIEW_IN_PROGRESS' or progress.get('levels_completed') != ['A1', 'A2', 'B1', 'B2', 'C1']:
        raise SystemExit('C2 completion frontier drift')
    if not (DD / 'c2_u09.json').exists() or (DD / 'c2_u10.json').exists():
        raise SystemExit('decision frontier drift')

    inventory = json.loads(INV.read_text(encoding='utf-8'))
    c2 = inventory.get('levels', {}).get('c2', {})
    if c2.get('canonical_sha256') != pre or c2.get('fresh_review_status') != 'IN_PROGRESS' or c2.get('fresh_records_reviewed') != 54:
        raise SystemExit('inventory/hash frontier drift')

    rows = [json.loads(line) for line in raw.decode('utf-8').splitlines() if line.strip()]
    if len(rows) != 60 or [rows[i].get('id') for i in range(54, 60)] != IDS:
        raise SystemExit('C2 Unit 10 layout drift')
    by_id = {row['id']: row for row in rows}
    before_targets = {pid: targets(by_id[pid]) for pid in IDS}

    for pid in IDS:
        record = by_id[pid]
        quality = record.get('quality', {})
        if quality.get('status') != 'draft' or quality.get('coverage_check') != 'pending':
            raise SystemExit(f'{pid}: release-state metadata drift')
        if any(quality.get(field) != 'pending' for field in ('linguistic_review', 'pedagogical_review', 'answer_key_check', 'schema_check')):
            raise SystemExit(f'{pid}: internal review frontier drift')
        if record.get('new_lexical_targets') != [] or record.get('review_lexical_targets') != []:
            raise SystemExit(f'{pid}: zero-new-target capstone drift')

        questions = {q['id']: q for q in record.get('questions', [])}
        answers = {a['question_id']: a for a in record.get('answer_key', [])}
        if questions.get('q1', {}).get('type') != 'summary' or questions.get('q1', {}).get('prompt') != SUMMARY_PROMPT:
            raise SystemExit(f'{pid}: q1 prompt drift')
        if questions.get('q2', {}).get('prompt') != Q2_PROMPT:
            raise SystemExit(f'{pid}: q2 prompt drift')
        if answers.get('q1', {}).get('answer') != OLD_Q1:
            raise SystemExit(f'{pid}/q1: answer drift')
        if answers.get('q2', {}).get('answer') != OLD_Q2:
            raise SystemExit(f'{pid}/q2: answer drift')
        answers['q1']['answer'] = Q1_REPAIRS[pid]
        answers['q2']['answer'] = Q2_REPAIRS[pid]

        for old, new in TEXT_REPAIRS[pid]:
            if record.get('text', '').count(old) != 1:
                raise SystemExit(f'{pid}: text repair anchor drift')
            record['text'] = record['text'].replace(old, new, 1)
        for qid, (old, new) in ANSWER_REPAIRS[pid].items():
            if answers.get(qid, {}).get('answer') != old:
                raise SystemExit(f'{pid}/{qid}: answer repair anchor drift')
            answers[qid]['answer'] = new

        record['word_count'] = wc(record['text'])
        if not 700 <= record['word_count'] <= 1200:
            raise SystemExit(f'{pid}: C2 word band drift')
        if targets(record) != before_targets[pid]:
            raise SystemExit(f'{pid}: lexical target drift')
        if len(record.get('questions', [])) != 10 or len(record.get('answer_key', [])) != 10:
            raise SystemExit(f'{pid}: 10Q/10A invariant failed')
        answer_by_id = {a['id']: a for a in record['answer_key']}
        for question in record['questions']:
            aid = question.get('answer_id')
            if aid not in answer_by_id or answer_by_id[aid].get('question_id') != question.get('id'):
                raise SystemExit(f'{pid}: answer linkage drift')

        record['revision'] = int(record.get('revision', 0) or 0) + 1
        quality = record.setdefault('quality', {})
        for field in ('linguistic_review', 'pedagogical_review', 'answer_key_check', 'schema_check'):
            quality[field] = 'pass'
        if NOTE not in quality.setdefault('notes', []):
            quality['notes'].append(NOTE)

    if (sum(len(META[pid]) for pid in IDS), sum(bool(META[pid]) for pid in IDS)) != (19, 6):
        raise SystemExit('finding metadata drift')

    PATH.write_text(''.join(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n' for row in rows), encoding='utf-8')
    print(json.dumps({
        'level': 'C2',
        'unit': 10,
        'records_reviewed': 6,
        'records_with_findings': 6,
        'fresh_findings': 19,
        'pre_repair_canonical_sha256': pre,
        'post_repair_canonical_sha256': sha(PATH.read_bytes()),
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
