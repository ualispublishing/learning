import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / 'reading' / 'urdu' / 'a1' / 'passages.jsonl'
REPORT = ROOT / 'reading' / 'audit' / 'urdu_a1_final_integrity_2026-08-23.json'
EXPECTED = '293cdb4ec7855f2c34583e29e47775424faad8b4'

ALLOWED_QUESTION_TYPES = {
    'gist', 'literal_detail', 'cause_effect', 'vocabulary_in_context',
    'single_word_definition', 'sequence', 'cloze_transfer', 'contrast',
    'summary', 'reference_resolution', 'conditional_comprehension'
}
ALLOWED_REVIEW_STAGES = {'R1', 'R2', 'R3', 'R4', 'long_term'}
QUALITY_GATES = ('answer_key_check', 'coverage_check', 'linguistic_review', 'pedagogical_review', 'schema_check')


def blob(path):
    return subprocess.check_output(['git', 'hash-object', str(path)], text=True).strip()


def exact_form_count(text, form):
    if not form:
        return 0
    return len(re.findall(rf'(?<!\w){re.escape(form)}(?!\w)', text, flags=re.UNICODE | re.IGNORECASE))


def answer_parts(answer):
    return [x.strip() for x in str(answer).split('؛')]


def sentence_count(text):
    return sum(text.count(x) for x in ('۔', '؟', '?', '!'))


def add_error(errors, code, **detail):
    errors.append({'code': code, **detail})


actual_blob = blob(PATH)
raw_lines = [x for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
rows = []
hard_errors = []
warnings = []
try:
    rows = [json.loads(x) for x in raw_lines]
except Exception as exc:
    add_error(hard_errors, 'json_parse_failure', error=repr(exc))

if actual_blob != EXPECTED:
    add_error(hard_errors, 'unexpected_input_blob', expected=EXPECTED, actual=actual_blob)
if len(rows) != 60:
    add_error(hard_errors, 'passage_count', expected=60, actual=len(rows))

seqs = [r.get('sequence') for r in rows]
if seqs != list(range(1, 61)):
    add_error(hard_errors, 'sequence_order', actual=seqs)

passage_ids = [r.get('id') for r in rows]
if len(set(passage_ids)) != len(passage_ids):
    add_error(hard_errors, 'duplicate_passage_ids', duplicates=[x for x, n in Counter(passage_ids).items() if n > 1])

new_target_ids = []
cloze_count = 0
question_count = 0
answer_count = 0
review_zero_occurrence = []
quality_status_counts = Counter()
question_type_counts = Counter()
new_target_exposure_checks = []
review_presence_checks = []
duplicate_prompt_checks = []

for row in rows:
    rid = row.get('id')
    seq = row.get('sequence')
    expected_unit = ((seq - 1) // 6) + 1 if isinstance(seq, int) else None
    expected_p = ((seq - 1) % 6) + 1 if isinstance(seq, int) else None
    expected_id = f'ur-a1-u{expected_unit:02d}-p{expected_p:02d}' if expected_unit and expected_p else None

    if row.get('language') != 'ur':
        add_error(hard_errors, 'language_code', passage_id=rid, actual=row.get('language'))
    if row.get('cefr') != 'A1':
        add_error(hard_errors, 'cefr', passage_id=rid, actual=row.get('cefr'))
    if row.get('unit') != expected_unit:
        add_error(hard_errors, 'unit_sequence_mismatch', passage_id=rid, expected=expected_unit, actual=row.get('unit'))
    if rid != expected_id:
        add_error(hard_errors, 'passage_id_sequence_mismatch', passage_id=rid, expected=expected_id)

    text = str(row.get('text', ''))
    if not text.strip():
        add_error(hard_errors, 'empty_passage_text', passage_id=rid)
    wc = len(re.findall(r'\S+', text))
    if row.get('word_count') != wc:
        add_error(hard_errors, 'word_count_mismatch', passage_id=rid, metadata=row.get('word_count'), calculated=wc)
    sc = sentence_count(text)
    if row.get('sentence_count') != sc:
        add_error(hard_errors, 'sentence_count_mismatch', passage_id=rid, metadata=row.get('sentence_count'), calculated=sc)

    questions = row.get('questions', [])
    answers = row.get('answer_key', [])
    question_count += len(questions)
    answer_count += len(answers)
    if len(questions) != 10:
        add_error(hard_errors, 'question_count_per_passage', passage_id=rid, actual=len(questions))
    if len(answers) != 10:
        add_error(hard_errors, 'answer_count_per_passage', passage_id=rid, actual=len(answers))

    qids = [q.get('id') for q in questions]
    aids = [a.get('id') for a in answers]
    if qids != [f'q{i}' for i in range(1, 11)]:
        add_error(hard_errors, 'question_ids', passage_id=rid, actual=qids)
    if aids != [f'a{i}' for i in range(1, 11)]:
        add_error(hard_errors, 'answer_ids', passage_id=rid, actual=aids)
    if len(set(qids)) != len(qids):
        add_error(hard_errors, 'duplicate_question_ids', passage_id=rid)
    if len(set(aids)) != len(aids):
        add_error(hard_errors, 'duplicate_answer_ids', passage_id=rid)

    prompt_counts = Counter(str(q.get('prompt', '')).strip() for q in questions)
    dup_prompts = [p for p, n in prompt_counts.items() if p and n > 1]
    duplicate_prompt_checks.append({'passage_id': rid, 'duplicates': dup_prompts})
    if dup_prompts:
        add_error(hard_errors, 'duplicate_question_prompts', passage_id=rid, duplicates=dup_prompts)

    by_q = {a.get('question_id'): a for a in answers}
    if len(by_q) != len(answers):
        add_error(hard_errors, 'duplicate_answer_question_backlinks', passage_id=rid)

    new_targets = row.get('new_lexical_targets', [])
    review_targets = row.get('review_lexical_targets', [])
    if expected_p == 6 and new_targets:
        add_error(hard_errors, 'checkpoint_has_new_lexical_targets', passage_id=rid, target_ids=[t.get('id') for t in new_targets])
    local_target_ids = {t.get('id') for t in new_targets} | {t.get('id') for t in review_targets}

    for q in questions:
        qid = q.get('id')
        qtype = q.get('type')
        question_type_counts[qtype] += 1
        if qtype not in ALLOWED_QUESTION_TYPES:
            add_error(hard_errors, 'unknown_or_disallowed_question_type', passage_id=rid, question_id=qid, type=qtype)
        if qtype in {'grammar_function', 'grammar_category'}:
            add_error(hard_errors, 'explicit_grammar_label_type', passage_id=rid, question_id=qid, type=qtype)
        if not str(q.get('prompt', '')).strip():
            add_error(hard_errors, 'empty_question_prompt', passage_id=rid, question_id=qid)

        a = by_q.get(qid)
        if not a:
            add_error(hard_errors, 'missing_answer_for_question', passage_id=rid, question_id=qid)
            continue
        if a.get('id') != q.get('answer_id'):
            add_error(hard_errors, 'qa_link_mismatch', passage_id=rid, question_id=qid, question_answer_id=q.get('answer_id'), actual_answer_id=a.get('id'))
        if a.get('question_id') != qid:
            add_error(hard_errors, 'answer_backlink_mismatch', passage_id=rid, question_id=qid, answer_id=a.get('id'))
        if not str(a.get('answer', '')).strip():
            add_error(hard_errors, 'empty_answer', passage_id=rid, question_id=qid)

        tids = q.get('target_ids', [])
        if not isinstance(tids, list):
            add_error(hard_errors, 'target_ids_not_list', passage_id=rid, question_id=qid)
            tids = []
        for tid in tids:
            if not re.fullmatch(r'ur-rank-\d{4}', str(tid)):
                add_error(hard_errors, 'malformed_question_target_id', passage_id=rid, question_id=qid, target_id=tid)
            if tid not in local_target_ids:
                add_error(hard_errors, 'question_target_not_in_local_target_lists', passage_id=rid, question_id=qid, target_id=tid)

        if qtype == 'cloze_transfer':
            cloze_count += 1
            prompt = str(q.get('prompt', ''))
            answer = str(a.get('answer', ''))
            parts = answer_parts(answer)
            blanks = prompt.count('_____')
            if blanks != len(parts):
                add_error(hard_errors, 'cloze_blank_part_mismatch', passage_id=rid, question_id=qid, blanks=blanks, answer_parts=len(parts), answer=answer)
            terminal_bad = [p for p in parts if p.endswith(('۔', '؟', '!', '.', '?'))]
            if terminal_bad:
                add_error(hard_errors, 'cloze_key_terminal_punctuation', passage_id=rid, question_id=qid, parts=terminal_bad)
            reconstructed = prompt
            for part in parts:
                if '_____' not in reconstructed:
                    break
                reconstructed = reconstructed.replace('_____', part, 1)
            if '_____' in reconstructed:
                add_error(hard_errors, 'cloze_unfilled_after_reconstruction', passage_id=rid, question_id=qid, reconstructed=reconstructed)

    for t in new_targets:
        tid = t.get('id')
        new_target_ids.append(tid)
        form = str(t.get('form', ''))
        exact = exact_form_count(text, form)
        meta = t.get('exposures_in_text')
        new_target_exposure_checks.append({'passage_id': rid, 'target_id': tid, 'form': form, 'metadata': meta, 'exact_text_count': exact})
        if not re.fullmatch(r'ur-rank-\d{4}', str(tid)):
            add_error(hard_errors, 'malformed_new_target_id', passage_id=rid, target_id=tid)
        else:
            parsed_rank = int(str(tid).rsplit('-', 1)[1])
            if t.get('source_rank') != parsed_rank:
                add_error(hard_errors, 'source_rank_id_mismatch', passage_id=rid, target_id=tid, source_rank=t.get('source_rank'), parsed_rank=parsed_rank)
        if exact != meta:
            add_error(hard_errors, 'new_target_exposure_mismatch', passage_id=rid, target_id=tid, form=form, metadata=meta, exact_text_count=exact)
        if exact < 1:
            add_error(hard_errors, 'new_target_missing_from_text', passage_id=rid, target_id=tid, form=form)
        if not str(t.get('intended_sense', '')).strip():
            add_error(hard_errors, 'empty_intended_sense', passage_id=rid, target_id=tid)
        if 'agarwood' in str(t.get('intended_sense', '')).casefold():
            add_error(hard_errors, 'unrelated_homonym_in_intended_sense', passage_id=rid, target_id=tid, intended_sense=t.get('intended_sense'))

    for t in review_targets:
        tid = t.get('id')
        form = str(t.get('form', ''))
        exact = exact_form_count(text, form)
        stage = t.get('review_stage')
        review_presence_checks.append({'passage_id': rid, 'target_id': tid, 'form': form, 'review_stage': stage, 'exact_text_count': exact})
        if stage not in ALLOWED_REVIEW_STAGES:
            add_error(hard_errors, 'invalid_review_stage', passage_id=rid, target_id=tid, stage=stage)
        if exact == 0:
            item = {'code': 'review_target_zero_exact_occurrence', 'passage_id': rid, 'target_id': tid, 'form': form, 'review_stage': stage}
            review_zero_occurrence.append(item)
            add_error(hard_errors, **item)

    quality = row.get('quality', {})
    status = quality.get('status')
    quality_status_counts[status] += 1
    if status != 'draft':
        add_error(hard_errors, 'stale_or_premature_quality_status', passage_id=rid, status=status)
    for gate in QUALITY_GATES:
        if quality.get(gate) == 'pass':
            add_error(hard_errors, 'premature_quality_pass', passage_id=rid, gate=gate)

if len(new_target_ids) != len(set(new_target_ids)):
    add_error(hard_errors, 'duplicate_new_target_introductions', duplicates=[x for x, n in Counter(new_target_ids).items() if n > 1])
if question_count != 600:
    add_error(hard_errors, 'total_question_count', expected=600, actual=question_count)
if answer_count != 600:
    add_error(hard_errors, 'total_answer_count', expected=600, actual=answer_count)
if cloze_count != 130:
    add_error(hard_errors, 'total_cloze_count', expected=130, actual=cloze_count)

joined = '\n'.join(
    str(r.get('title', '')) + '\n' + str(r.get('text', '')) + '\n' +
    '\n'.join(str(q.get('prompt', '')) for q in r.get('questions', [])) + '\n' +
    '\n'.join(str(a.get('answer', '')) for a in r.get('answer_key', []))
    for r in rows
)
banned_fragments = [
    'اس دورہ میں', 'دورہ کے دوران', 'اگلے دورہ کا', 'خاندان کے دورہ میں', 'پچھلے دورہ میں',
    'اردو کی زبان', 'لفظ کی مقدار', 'عادت کی مقدار', 'پہلا بس کا سفر',
    'یہ میرا _____ بس کا _____ ہے', 'استاد سے اپنا نام بتاتا ہے',
    'ہر چیز اپنی جگہ رکھنا ضروری تھا', 'میں نے _____ کتاب پڑھ لی',
    '_____ میں یہ کام پہلے کروں گا', 'روز چلنے کا ایک _____ صحت ہے',
    'خالہ نے پوچھا کہ کیا وہ بازار چلنا چاہتی ہے',
    'عائشہ کا اسکول کا راستہ', 'ہر قدم سنتی جاتی ہے', 'کلاس کے بجے اور منٹ',
    'منٹ چھوٹے وقت کو بتانے', 'تقریباً وقت جاننے', 'سنائی دینے والی بولنے کی آواز',
    'دونوں خاندان کی خبر پوچھتی ہیں', 'پہلے کاغذ پر اس کا قلم',
    'بجلی کے وقت اور بغیر بجلی کے', 'پورا کام اچھا ہوا', 'ان کی محنت کامیاب ہوتی ہے',
    'پیلے رنگ کی قطار', 'بالکل ہمیشہ نہیں', 'پیغام میں وقت طے',
    'کسی شخص سے طے شدہ ملنا', 'سب فائدہ دیتے ہیں',
    'ماں کو رقم کیوں رکھنی ہے؟', 'گھر کے خرچ کے لیے۔'
]
for frag in banned_fragments:
    if frag in joined:
        add_error(hard_errors, 'known_bad_fragment_remaining', fragment=frag)

report = {
    'schema_version': 2,
    'date': '2026-08-23',
    'language': 'urdu',
    'level': 'A1',
    'input_git_blob_sha_expected': EXPECTED,
    'input_git_blob_sha_actual': actual_blob,
    'passage_count': len(rows),
    'question_count': question_count,
    'answer_count': answer_count,
    'cloze_question_count': cloze_count,
    'question_type_counts': dict(question_type_counts),
    'quality_status_counts': dict(quality_status_counts),
    'new_target_count': len(new_target_ids),
    'new_target_exposure_checks': new_target_exposure_checks,
    'review_target_presence_checks': review_presence_checks,
    'review_target_zero_exact_occurrence_count': len(review_zero_occurrence),
    'review_target_zero_exact_occurrences': review_zero_occurrence,
    'duplicate_prompt_checks': duplicate_prompt_checks,
    'hard_error_count': len(hard_errors),
    'hard_errors': hard_errors,
    'warning_count': len(warnings),
    'warnings': warnings,
    'all_130_clozes_reconstructed': cloze_count == 130 and not any(e['code'].startswith('cloze_') for e in hard_errors),
    'quality_promotion': False,
}
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'hard_errors': len(hard_errors), 'warnings': len(warnings), 'review_zero': len(review_zero_occurrence), 'questions': question_count, 'answers': answer_count, 'clozes': cloze_count}, ensure_ascii=False))
if hard_errors:
    raise SystemExit(1)
