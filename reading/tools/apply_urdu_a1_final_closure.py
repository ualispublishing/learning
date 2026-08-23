import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / 'reading' / 'urdu' / 'a1' / 'passages.jsonl'
REPORT = ROOT / 'reading' / 'audit' / 'urdu_a1_final_closure_repairs_2026-08-23.json'
EXPECTED = 'ae420dda7b2f0893eac4b5a030ffc639a5f2d2ad'


def blob(path):
    return subprocess.check_output(['git', 'hash-object', str(path)], text=True).strip()


def exact_form_count(text, form):
    if not form:
        return 0
    return len(re.findall(rf'(?<!\w){re.escape(form)}(?!\w)', text, flags=re.UNICODE | re.IGNORECASE))


def sentence_count(text):
    return sum(text.count(x) for x in ('۔', '؟', '?', '!'))


def word_count(text):
    return len(re.findall(r'\S+', text))


def qa(row, qid):
    q = next(x for x in row['questions'] if x['id'] == qid)
    a = next(x for x in row['answer_key'] if x['question_id'] == qid)
    return q, a


def replace_text(row, old, new, ops, finding):
    assert old in row['text'], (row['id'], finding, old)
    before = row['text']
    row['text'] = row['text'].replace(old, new, 1)
    ops.append({'passage_id': row['id'], 'kind': 'text', 'finding': finding, 'old_fragment': old, 'new_fragment': new})
    assert row['text'] != before


def set_field(row, field, old, new, ops, finding):
    assert row[field] == old, (row['id'], field, row[field], old)
    row[field] = new
    ops.append({'passage_id': row['id'], 'kind': field, 'finding': finding, 'before': old, 'after': new})


def set_answer(row, qid, old_answer, new_answer, ops, finding, old_expl=None, new_expl=None):
    q, a = qa(row, qid)
    assert a['answer'] == old_answer, (row['id'], qid, a['answer'], old_answer)
    before = dict(a)
    a['answer'] = new_answer
    if old_expl is not None:
        assert a.get('explanation') == old_expl, (row['id'], qid, a.get('explanation'), old_expl)
    if new_expl is not None:
        a['explanation'] = new_expl
    ops.append({'passage_id': row['id'], 'kind': 'answer', 'item': qid, 'finding': finding, 'before': before, 'after': dict(a)})


def set_question(row, qid, old_prompt, new_prompt, ops, finding, new_type=None):
    q, a = qa(row, qid)
    assert q['prompt'] == old_prompt, (row['id'], qid, q['prompt'], old_prompt)
    before = dict(q)
    q['prompt'] = new_prompt
    if new_type is not None:
        q['type'] = new_type
    ops.append({'passage_id': row['id'], 'kind': 'question', 'item': qid, 'finding': finding, 'before': before, 'after': dict(q)})


assert blob(PATH) == EXPECTED, (blob(PATH), EXPECTED)
rows = [json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
assert len(rows) == 60
byid = {r['id']: r for r in rows}
ops = []
touched = set()

# Unit 1 residual answer naturalness / scope.
r = byid['ur-a1-u01-p02']; touched.add(r['id'])
set_answer(r, 'q6', 'کسی وقت یا کام کے گزرنے کے پیچھے آنے والا وقت۔', 'کسی کام یا وقت کے بعد آنے والا وقت۔', ops, 'U1P02-01')

r = byid['ur-a1-u01-p04']; touched.add(r['id'])
set_answer(r, 'q7', 'پانچ بجے کو وقت کی آخری حد بنانا۔', 'پانچ بجے تک، یعنی پانچ بجے آخری حد ہے۔', ops, 'U1P04-03')

r = byid['ur-a1-u01-p06']; touched.add(r['id'])
set_answer(r, 'q6', 'عائشہ کی موجودہ حالت اور موجودہ وقت کی طرف۔', 'موجودہ وقت کی طرف۔', ops, 'U1P06-01')

# Remove a duplicated Unit 3 assessment while preserving because-in-context practice.
r = byid['ur-a1-u03-p01']; touched.add(r['id'])
set_question(r, 'q4', 'عائشہ سیب کیوں لیتی ہے؟', '«کیونکہ اسے سیب پسند ہے» میں کون سی وجہ دی گئی ہے؟', ops, 'CLOSURE-U3P01-DUPQ', new_type='vocabulary_in_context')
_, a = qa(r, 'q4')
assert a['answer'] == 'کیونکہ اسے سیب پسند ہے۔'
a['answer'] = 'اسے سیب پسند ہے۔'
a['explanation'] = '«کیونکہ» کے بعد سیب پسند ہونے کی وجہ بیان ہوئی ہے۔'
ops.append({'passage_id': r['id'], 'kind': 'answer', 'item': 'q4', 'finding': 'CLOSURE-U3P01-DUPQ', 'after': dict(a)})

# Unit 6 standard Urdu phrasing.
r = byid['ur-a1-u06-p03']; touched.add(r['id'])
replace_text(r, 'عائشہ کا اسکول کا راستہ صبح اور شام تھوڑا مختلف لگتا ہے۔', 'عائشہ کا اسکول جانے کا راستہ صبح اور شام تھوڑا مختلف لگتا ہے۔', ops, 'U6P03-01')

r = byid['ur-a1-u06-p04']; touched.add(r['id'])
replace_text(r, 'مریم فون ہاتھ میں رکھتی ہے اور ہر قدم سنتی جاتی ہے۔', 'مریم فون ہاتھ میں رکھتی ہے اور عائشہ کی ہدایات سنتی جاتی ہے۔', ops, 'U6P04-01')

r = byid['ur-a1-u06-p05']; touched.add(r['id'])
replace_text(r, 'ہفتے کو عائشہ مریم کے ساتھ قریبی کتابوں کی دکان جانا چاہتی ہے۔', 'ہفتے کو عائشہ مریم کے ساتھ قریبی کتابوں کی دکان پر جانا چاہتی ہے۔', ops, 'U6P05-01')
set_answer(r, 'q1', 'وہ مریم کے ساتھ قریبی کتابوں کی دکان جانا چاہتی ہے۔', 'وہ مریم کے ساتھ قریبی کتابوں کی دکان پر جانا چاہتی ہے۔', ops, 'U6P05-01')

r = byid['ur-a1-u06-p06']; touched.add(r['id'])
set_question(r, 'q2', 'گھر سے نکلتے وقت عائشہ راہ اور آگے کی سمت کے ساتھ کیا کرتی ہے؟', 'گھر سے نکلتے وقت عائشہ پہلے کون سی راہ دیکھتی ہے اور پھر کس سمت بڑھتی ہے؟', ops, 'CLOSURE-U6P06-Q2', new_type='literal_detail')

# Unit 7 natural time/planning language.
r = byid['ur-a1-u07-p01']; touched.add(r['id'])
set_answer(r, 'q4', 'سات دن کے عرصے یا اس کی حالت کو بتاتا ہے۔', 'سات دن کے عرصے سے۔', ops, 'U7P01-01')

r = byid['ur-a1-u07-p02']; touched.add(r['id'])
set_field(r, 'title', 'کلاس کے بجے اور منٹ', 'کلاس کا وقت اور منٹ', ops, 'U7P02-01')
replace_text(r, 'عائشہ گھڑی پر وقت دیکھتی ہے اور سمجھتی ہے کہ منٹ چھوٹے وقت کو بتانے میں مدد دیتے ہیں۔', 'عائشہ گھڑی پر وقت دیکھتی ہے اور سمجھتی ہے کہ منٹ وقت کی چھوٹی اکائیاں ہیں۔', ops, 'U7P02-02')

r = byid['ur-a1-u07-p04']; touched.add(r['id'])
replace_text(r, 'کلاس کے آخر میں ہر بچہ ایک آئندہ کام بتاتا ہے۔', 'کلاس کے آخر میں ہر بچہ بتاتا ہے کہ آئندہ وہ کون سا کام بہتر کرے گا۔', ops, 'U7P04-01')
set_question(r, 'q8', 'عائشہ پہلے آئندہ ہفتے کے کام لکھتی ہے یا کلاس کے آخر میں اپنا آئندہ کام بتاتی ہے؟', 'عائشہ پہلے آئندہ ہفتے کے کام لکھتی ہے یا آخر میں بتاتی ہے کہ آئندہ کیا بہتر کرے گی؟', ops, 'U7P04-01', new_type='sequence')
set_answer(r, 'q8', 'وہ پہلے آئندہ ہفتے کے دو کام لکھتی ہے، پھر کلاس کے آخر میں ایک آئندہ کام بتاتی ہے۔', 'وہ پہلے آئندہ ہفتے کے دو کام لکھتی ہے، پھر آخر میں بتاتی ہے کہ آئندہ کیا بہتر کرے گی۔', ops, 'U7P04-01')

r = byid['ur-a1-u07-p05']; touched.add(r['id'])
set_field(r, 'title', 'دوبارہ پڑھنا اور تقریباً وقت', 'دوبارہ پڑھنا اور وقت کا اندازہ', ops, 'U7P05-01')
replace_text(r, 'وہ سمجھتی ہے کہ دوبارہ پڑھنے سے سوال صاف ہوتا ہے اور تقریباً وقت جاننے سے کام منظم رہتا ہے۔', 'وہ سمجھتی ہے کہ دوبارہ پڑھنے سے سوال صاف ہوتا ہے اور یہ جاننے سے کام منظم رہتا ہے کہ اسے حل کرنے میں تقریباً کتنا وقت لگے گا۔', ops, 'U7P05-01')
set_question(r, 'q10', 'خالی جگہ پُر کریں: یہ کام _____ پانچ منٹ لیتا ہے۔', 'خالی جگہ پُر کریں: اس کام میں _____ پانچ منٹ لگتے ہیں۔', ops, 'U7P05-02', new_type='cloze_transfer')

r = byid['ur-a1-u07-p06']; touched.add(r['id'])
set_question(r, 'q6', 'سوال صاف نہ ہو تو عائشہ دوبارہ اور تقریباً کو کیسے استعمال کرتی ہے؟', 'سوال صاف نہ ہو تو عائشہ کیا کرتی ہے اور وقت کا اندازہ کیسے لگاتی ہے؟', ops, 'U7P06-03', new_type='literal_detail')
set_answer(r, 'q6', 'وہ سوال دوبارہ پڑھتی ہے اور تقریباً مطلوب وقت دیکھتی ہے۔', 'وہ سوال دوبارہ پڑھتی ہے اور دیکھتی ہے کہ اسے حل کرنے میں تقریباً کتنا وقت لگے گا۔', ops, 'U7P06-03', old_expl='متن میں غیر واضح سوال کے لیے یہی عمل ہے۔', new_expl='متن میں سوال دوبارہ پڑھنے اور وقت کا اندازہ لگانے کا یہی طریقہ ہے۔')

# Unit 8 natural definitions, grounding, and case/contrast language.
r = byid['ur-a1-u08-p02']; touched.add(r['id'])
replace_text(r, 'گفتگو پہلے اسکول کے بارے میں ہوتی ہے، پھر دونوں خاندان کی خبر پوچھتی ہیں۔', 'گفتگو پہلے اسکول کے بارے میں ہوتی ہے، پھر دونوں ایک دوسرے کے خاندان کا حال پوچھتی ہیں۔', ops, 'U8P02-01')
set_answer(r, 'q4', 'سنائی دینے والی بولنے کی آواز۔', 'بولنے والے شخص کی سنائی دینے والی صدا۔', ops, 'U8P02-02')
set_answer(r, 'q7', 'جو چیز بولنے یا کسی آواز سے سنائی دے۔', 'وہ صدا جو کان سے سنی جائے۔', ops, 'U8P02-02')

r = byid['ur-a1-u08-p03']; touched.add(r['id'])
replace_text(r, 'پہلے کاغذ پر اس کا قلم اچھی طرح نہیں چلتا، اس لیے وہ دوسرا قلم لیتی ہے۔', 'جو قلم عائشہ پہلے استعمال کرتی ہے، وہ کاغذ پر اچھی طرح نہیں چلتا، اس لیے وہ دوسرا قلم لیتی ہے۔', ops, 'U8P03-01')

r = byid['ur-a1-u08-p04']; touched.add(r['id'])
replace_text(r, 'وہ سمجھتی ہے کہ بجلی کے وقت اور بغیر بجلی کے گھر کے کام کچھ مختلف ہوتے ہیں۔', 'وہ سمجھتی ہے کہ بجلی ہونے اور بجلی نہ ہونے کی صورت میں گھر کے کچھ کام مختلف ہوتے ہیں۔', ops, 'U8P04-01')

r = byid['ur-a1-u08-p05']; touched.add(r['id'])
q, a = qa(r, 'q9')
assert a['explanation'] == 'مکمل کتاب کے لیے «پورا» درست ہے۔'
a['explanation'] = 'مکمل سبق کے لیے «پورا» درست ہے۔'
ops.append({'passage_id': r['id'], 'kind': 'answer_explanation', 'item': 'q9', 'finding': 'CLOSURE-U8P05-EXPL', 'after': a['explanation']})

r = byid['ur-a1-u08-p06']; touched.add(r['id'])
replace_text(r, 'ماں میز کی طرف دیکھتی ہیں اور کہتی ہیں کہ پورا کام اچھا ہوا، لیکن باقی کاغذ کل بھی دیکھنے ہیں۔', 'ماں میز کی طرف دیکھتی ہیں اور کہتی ہیں کہ کام اچھا ہوا؛ باقی کاغذ کل دیکھنے ہیں، پھر پورا کام مکمل ہو جائے گا۔', ops, 'U8P06-03')

# Unit 9 post-rewrite grounding and naturalness.
r = byid['ur-a1-u09-p02']; touched.add(r['id'])
set_question(r, 'q2', 'ماں کو رقم کیوں رکھنی ہے؟', 'ماں کو بینک میں رقم کے ساتھ کیا کرنا ہے؟', ops, 'CLOSURE-U9P02-GROUNDING', new_type='literal_detail')
set_answer(r, 'q2', 'گھر کے خرچ کے لیے۔', 'کچھ رقم جمع کرانی ہے۔', ops, 'CLOSURE-U9P02-GROUNDING', old_expl='متن اور سوال کے مطابق یہی مناسب جواب ہے۔', new_expl='متن میں ماں کچھ رقم جمع کرانے آئی ہیں۔')

r = byid['ur-a1-u09-p04']; touched.add(r['id'])
replace_text(r, 'آخر میں ان کی محنت کامیاب ہوتی ہے اور دونوں خوشی سے کام جمع کرتی ہیں۔', 'آخر میں ان کی محنت رنگ لاتی ہے؛ دونوں کام کامیابی سے مکمل کرکے خوشی سے جمع کراتی ہیں۔', ops, 'U9P04-01')

r = byid['ur-a1-u09-p06']; touched.add(r['id'])
replace_text(r, 'خاندان کے دورے میں اس نے تحفہ دینا اور دوسروں کو وقت دینا سیکھا۔', 'خالہ کے گھر یہ دورہ کرتے وقت اس نے تحفہ دینا اور دوسروں کو وقت دینا سیکھا۔', ops, 'CLOSURE-U9P06-DORA-REVIEW')
set_question(r, 'q7', 'گھر میں عائشہ نے پنکھے کی کیا چیز دیکھی؟', 'گھر میں عائشہ نے پنکھے کی کیا حالت دیکھی؟', ops, 'CLOSURE-U9P06-Q7', new_type='literal_detail')
set_answer(r, 'q7', 'اس کی حالت۔', 'پنکھے کی حالت۔', ops, 'CLOSURE-U9P06-Q7')

# Unit 10 final naturalness and review coverage.
r = byid['ur-a1-u10-p01']; touched.add(r['id'])
replace_text(r, 'عائشہ سرخ رنگ کے پھول دیکھتی ہے، پھر پیلے رنگ کی قطار کے پاس رکتی ہے۔', 'عائشہ سرخ رنگ کے پھول دیکھتی ہے، پھر پیلے پھولوں کی قطار کے پاس رکتی ہے۔', ops, 'U10P01-01')
replace_text(r, 'والد کہتے ہیں کہ پچھلے دورے میں یہاں کم پودے تھے۔', 'والد کہتے ہیں کہ پچھلا دورہ مختلف تھا؛ اس وقت یہاں کم پودے تھے۔', ops, 'CLOSURE-U10P01-DORA-REVIEW')
set_answer(r, 'q8', 'پچھلے دورے میں پودے کم تھے۔', 'پچھلے دورے کے وقت یہاں کم پودے تھے۔', ops, 'CLOSURE-U10P01-DORA-REVIEW')

r = byid['ur-a1-u10-p03']; touched.add(r['id'])
replace_text(r, 'عائشہ ہاں کہتی ہے، مگر پھر ہنس کر بولتی ہے کہ بالکل ہمیشہ نہیں۔ بعض دن وہ دیر سے بھی اٹھتی ہے۔', 'عائشہ ہاں کہتی ہے، مگر پھر ہنس کر بولتی ہے کہ ہر دن ایسا نہیں ہوتا؛ بعض دن وہ دیر سے بھی اٹھتی ہے، اور ماں کہتی ہیں کہ یہ بات بالکل درست ہے۔', ops, 'U10P03-01')
set_question(r, 'q7', 'عائشہ اپنی عادت کے بارے میں کیا وضاحت کرتی ہے؟', 'ماں عائشہ کی بات سے اتفاق کرتے ہوئے کیا کہتی ہیں؟', ops, 'U10P03-01', new_type='literal_detail')
set_answer(r, 'q7', 'وہ کہتی ہے کہ بالکل ہمیشہ نہیں۔', 'وہ کہتی ہیں کہ یہ بات بالکل درست ہے۔', ops, 'U10P03-01')

r = byid['ur-a1-u10-p04']; touched.add(r['id'])
replace_text(r, 'ملاقات سے پہلے دونوں پیغام میں وقت طے کرتی ہیں۔', 'ملاقات سے پہلے دونوں پیغام کے ذریعے وقت طے کرتی ہیں۔', ops, 'U10P04-01')
set_answer(r, 'q3', 'کسی شخص سے طے شدہ ملنا۔', 'کسی شخص سے ملنے کا طے شدہ وقت یا موقع۔', ops, 'U10P04-02')

r = byid['ur-a1-u10-p06']; touched.add(r['id'])
replace_text(r, 'عائشہ جانتی ہے کہ واضح ہدایت، اچھی ملاقات اور نئی زبان کی مشق سب فائدہ دیتے ہیں۔', 'عائشہ جانتی ہے کہ واضح ہدایت، اچھی ملاقات اور نئی زبان کی مشق سب مفید ہوتی ہیں۔', ops, 'U10P06-02')

# Recalculate corpus metadata with token-aware exact matching and actual terminal punctuation.
metadata_changes = []
for row in rows:
    old_wc = row.get('word_count')
    old_sc = row.get('sentence_count')
    new_wc = word_count(row['text'])
    new_sc = sentence_count(row['text'])
    if old_wc != new_wc:
        metadata_changes.append({'passage_id': row['id'], 'field': 'word_count', 'before': old_wc, 'after': new_wc})
        row['word_count'] = new_wc
        touched.add(row['id'])
    if old_sc != new_sc:
        metadata_changes.append({'passage_id': row['id'], 'field': 'sentence_count', 'before': old_sc, 'after': new_sc})
        row['sentence_count'] = new_sc
        touched.add(row['id'])
    for t in row.get('new_lexical_targets', []):
        exact = exact_form_count(row['text'], str(t.get('form', '')))
        old = t.get('exposures_in_text')
        if old != exact:
            metadata_changes.append({'passage_id': row['id'], 'field': 'exposures_in_text', 'target_id': t.get('id'), 'form': t.get('form'), 'before': old, 'after': exact})
            t['exposures_in_text'] = exact
            touched.add(row['id'])
        assert exact >= 1, (row['id'], t.get('id'), t.get('form'))

# Revision and audit note only for rows actually touched by this closure.
for row in rows:
    if row['id'] not in touched:
        continue
    row['revision'] = int(row.get('revision', 0)) + 1
    q = row.setdefault('quality', {})
    for gate in ('answer_key_check', 'coverage_check', 'linguistic_review', 'pedagogical_review', 'schema_check'):
        if gate in q:
            q[gate] = 'pending'
    q['status'] = 'draft'
    note = 'Final Urdu A1 closure repair/recount applied 2026-08-23; final independent integrity audit pending.'
    if note not in q.setdefault('notes', []):
        q['notes'].append(note)

# Structural validation and exact review coverage.
cloze_count = 0
review_zero = []
for row in rows:
    assert len(row['questions']) == 10
    assert len(row['answer_key']) == 10
    assert [q['id'] for q in row['questions']] == [f'q{i}' for i in range(1, 11)]
    assert [a['id'] for a in row['answer_key']] == [f'a{i}' for i in range(1, 11)]
    amap = {a['question_id']: a for a in row['answer_key']}
    for q in row['questions']:
        a = amap[q['id']]
        assert q['answer_id'] == a['id']
        if q['type'] != 'cloze_transfer':
            continue
        cloze_count += 1
        parts = [x.strip() for x in str(a['answer']).split('؛')]
        assert q['prompt'].count('_____') == len(parts), (row['id'], q['id'], q['prompt'], a['answer'])
        assert all(not p.endswith(('۔', '؟', '?', '!', '.')) for p in parts), (row['id'], q['id'], parts)
        rebuilt = q['prompt']
        for part in parts:
            rebuilt = rebuilt.replace('_____', part, 1)
        assert '_____' not in rebuilt
    for t in row.get('review_lexical_targets', []):
        cnt = exact_form_count(row['text'], str(t.get('form', '')))
        if cnt == 0:
            review_zero.append({'passage_id': row['id'], 'target_id': t.get('id'), 'form': t.get('form'), 'review_stage': t.get('review_stage')})
    quality = row.get('quality', {})
    assert quality.get('status') == 'draft'
    assert not any(quality.get(g) == 'pass' for g in ('answer_key_check', 'coverage_check', 'linguistic_review', 'pedagogical_review', 'schema_check'))

assert cloze_count == 130, cloze_count
assert not review_zero, review_zero

bad_fragments = [
    'عائشہ کا اسکول کا راستہ', 'ہر قدم سنتی جاتی ہے', 'کلاس کے بجے اور منٹ',
    'منٹ چھوٹے وقت کو بتانے', 'تقریباً وقت جاننے', 'سنائی دینے والی بولنے کی آواز',
    'دونوں خاندان کی خبر پوچھتی ہیں', 'پہلے کاغذ پر اس کا قلم',
    'بجلی کے وقت اور بغیر بجلی کے', 'پورا کام اچھا ہوا', 'ان کی محنت کامیاب ہوتی ہے',
    'پیلے رنگ کی قطار', 'بالکل ہمیشہ نہیں', 'پیغام میں وقت طے',
    'کسی شخص سے طے شدہ ملنا', 'سب فائدہ دیتے ہیں',
    'ماں کو رقم کیوں رکھنی ہے؟', 'گھر کے خرچ کے لیے۔'
]
joined = '\n'.join(r['text'] + '\n' + '\n'.join(q['prompt'] for q in r['questions']) + '\n' + '\n'.join(a['answer'] for a in r['answer_key']) for r in rows)
remaining_bad = [x for x in bad_fragments if x in joined]
assert not remaining_bad, remaining_bad

PATH.write_text('\n'.join(json.dumps(x, ensure_ascii=False, sort_keys=True) for x in rows) + '\n', encoding='utf-8')
new_blob = blob(PATH)
REPORT.write_text(json.dumps({
    'schema_version': 1,
    'date': '2026-08-23',
    'language': 'urdu',
    'level': 'A1',
    'input_git_blob_sha': EXPECTED,
    'output_git_blob_sha': new_blob,
    'changed_passage_count': len(touched),
    'changed_passage_ids': sorted(touched),
    'repair_operation_count': len(ops),
    'repair_operations': ops,
    'metadata_change_count': len(metadata_changes),
    'metadata_changes': metadata_changes,
    'cloze_question_count': cloze_count,
    'all_clozes_reconstructed': True,
    'review_target_zero_exact_occurrence_count': 0,
    'remaining_known_bad_fragment_count': 0,
    'quality_promotion': False,
}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'output_blob': new_blob, 'changed_passages': len(touched), 'operations': len(ops), 'metadata_changes': len(metadata_changes), 'clozes': cloze_count}, ensure_ascii=False))
