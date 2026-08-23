#!/usr/bin/env python3
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A1 = ROOT / 'reading/arabic/a1/passages.jsonl'
A2 = ROOT / 'reading/arabic/a2/passages.jsonl'
ADJ = ROOT / 'reading/audit/arabic_a1_a2_diagnostic_adjudication_2026-08-23.json'
FALSE_REVIEW = ROOT / 'reading/audit/arabic_a1_a2_false_review_metadata_repair_2026-08-23.json'
FINAL23 = ROOT / 'reading/audit/arabic_a1_a2_remaining_23_adjudicated_repair_2026-08-23.json'
REPORT = ROOT / 'reading/audit/arabic_a1_a2_final_validation_2026-08-23.json'

EXPECTED_BLOBS = {
    'a1': '82fc6675e887ec4ce7d833372a068de8e2e8cfb0',
    'a2': '4581f5d003361244b85ff45cde9c8764edf1699b',
}
WORD_BANDS = {'a1': (90, 140), 'a2': (140, 220)}
BANNED_TYPES = {'grammar_category', 'grammar_function', 'person_form', 'morphology_label', 'syntax_label'}
BANNED_PROMPTS = [
    re.compile(r'التصنيف\s+النحوي'), re.compile(r'التصنيف\s+الصرفي'),
    re.compile(r'نوع\s+الكلمة\s+نحوي'),
    re.compile(r'ما\s+وظيفة.+في\s+(?:الجملة|العبارة|هذا\s+الاستعمال|الاستعمال)'),
]
LATIN = re.compile(r'[A-Za-z]')


def blob(path):
    return subprocess.check_output(['git', 'hash-object', str(path)], text=True).strip()


def load_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]


def words(text):
    return len(re.findall(r'\S+', str(text)))


def sentences(text):
    return sum(str(text).count(p) for p in ('.', '؟', '!', '۔'))


def learner_strings(row):
    out = [row.get('title', ''), row.get('text', '')]
    for q in row.get('questions', []):
        out.append(q.get('prompt', ''))
        out.extend(q.get('options', []) or [])
    for a in row.get('answer_key', []):
        out.extend([a.get('answer', ''), a.get('explanation', '')])
    return out


def fail(errors, code, **kw):
    errors.append({'code': code, **kw})


def target_map(rows):
    out = {}
    for row in rows:
        for t in row.get('new_lexical_targets', []):
            if isinstance(t, dict) and t.get('id'):
                out[t['id']] = t
    return out


def validate_level(level, rows, errors):
    q_total = a_total = 0
    seen_new = []
    for i, row in enumerate(rows, 1):
        pid = row.get('id')
        unit = (i - 1) // 6 + 1
        pno = (i - 1) % 6 + 1
        expected_id = f'ar-{level}-u{unit:02d}-p{pno:02d}'
        if row.get('sequence') != i: fail(errors, 'sequence', passage_id=pid, expected=i, actual=row.get('sequence'))
        if row.get('unit') != unit: fail(errors, 'unit', passage_id=pid, expected=unit, actual=row.get('unit'))
        if pid != expected_id: fail(errors, 'id', passage_id=pid, expected=expected_id)
        if row.get('language') != 'ar': fail(errors, 'language', passage_id=pid, actual=row.get('language'))
        if str(row.get('cefr', '')).lower() != level: fail(errors, 'cefr', passage_id=pid, actual=row.get('cefr'))

        wc = words(row.get('text', ''))
        lo, hi = WORD_BANDS[level]
        if not (lo <= wc <= hi): fail(errors, 'word_band', passage_id=pid, calculated=wc, band=[lo, hi])
        if row.get('word_count') != wc: fail(errors, 'word_count', passage_id=pid, metadata=row.get('word_count'), calculated=wc)
        sc = sentences(row.get('text', ''))
        if row.get('sentence_count') != sc: fail(errors, 'sentence_count', passage_id=pid, metadata=row.get('sentence_count'), calculated=sc)

        qs = row.get('questions', []); ans = row.get('answer_key', [])
        q_total += len(qs); a_total += len(ans)
        if len(qs) != 10: fail(errors, 'question_count', passage_id=pid, actual=len(qs))
        if len(ans) != 10: fail(errors, 'answer_count', passage_id=pid, actual=len(ans))
        if [q.get('id') for q in qs] != [f'q{x}' for x in range(1, 11)]: fail(errors, 'question_ids', passage_id=pid)
        if [a.get('id') for a in ans] != [f'a{x}' for x in range(1, 11)]: fail(errors, 'answer_ids', passage_id=pid)
        by_qid = {a.get('question_id'): a for a in ans}
        local_ids = {t.get('id') for t in row.get('new_lexical_targets', []) if isinstance(t, dict)} | {t.get('id') for t in row.get('review_lexical_targets', []) if isinstance(t, dict)}
        for q in qs:
            a = by_qid.get(q.get('id'))
            if not a: fail(errors, 'missing_answer', passage_id=pid, question_id=q.get('id')); continue
            if q.get('answer_id') != a.get('id'): fail(errors, 'qa_link', passage_id=pid, question_id=q.get('id'))
            if q.get('type') in BANNED_TYPES: fail(errors, 'metalinguistic_type', passage_id=pid, question_id=q.get('id'), type=q.get('type'))
            if any(p.search(str(q.get('prompt', ''))) for p in BANNED_PROMPTS): fail(errors, 'metalinguistic_prompt', passage_id=pid, question_id=q.get('id'), prompt=q.get('prompt'))
            tids = q.get('target_ids', []) or []
            if not isinstance(tids, list): fail(errors, 'target_ids_type', passage_id=pid, question_id=q.get('id'))
            else:
                for tid in tids:
                    if tid not in local_ids: fail(errors, 'target_not_local', passage_id=pid, question_id=q.get('id'), target_id=tid)
            if q.get('type') == 'cloze_transfer':
                blanks = str(q.get('prompt', '')).count('_____')
                parts = [x.strip() for x in re.split(r'[؛;]', str(a.get('answer', ''))) if x.strip()]
                if blanks != len(parts): fail(errors, 'cloze_cardinality', passage_id=pid, question_id=q.get('id'), blanks=blanks, answers=len(parts))

        prompts = [' '.join(str(q.get('prompt', '')).split()) for q in qs]
        for p, n in Counter(prompts).items():
            if n > 1: fail(errors, 'duplicate_prompt', passage_id=pid, prompt=p, count=n)

        for t in row.get('new_lexical_targets', []):
            if not isinstance(t, dict): fail(errors, 'new_target_object', passage_id=pid); continue
            seen_new.append(t.get('id'))
            if not isinstance(t.get('exposures_in_text'), int) or t.get('exposures_in_text') < 1:
                fail(errors, 'invalid_exposure_count', passage_id=pid, target_id=t.get('id'), value=t.get('exposures_in_text'))
            if not str(t.get('intended_sense', '')).strip(): fail(errors, 'empty_intended_sense', passage_id=pid, target_id=t.get('id'))

        for s in learner_strings(row):
            if LATIN.search(str(s)):
                fail(errors, 'latin_in_learner_facing_arabic', passage_id=pid, sample=str(s)[:180])
                break

        quality = row.get('quality', {})
        if quality.get('status') != 'draft': fail(errors, 'quality_status', passage_id=pid, value=quality.get('status'))
        for gate in ('answer_key_check', 'coverage_check', 'linguistic_review', 'pedagogical_review', 'schema_check'):
            if quality.get(gate) != 'pending': fail(errors, 'quality_gate', passage_id=pid, gate=gate, value=quality.get(gate))

    if len(rows) != 60: fail(errors, 'passage_total', level=level, expected=60, actual=len(rows))
    if q_total != 600: fail(errors, 'question_total', level=level, expected=600, actual=q_total)
    if a_total != 600: fail(errors, 'answer_total', level=level, expected=600, actual=a_total)
    dup = [x for x, n in Counter(seen_new).items() if x and n > 1]
    if dup: fail(errors, 'duplicate_new_target_ids', level=level, ids=dup)
    return {'passages': len(rows), 'questions': q_total, 'answers': a_total, 'new_targets': len(seen_new)}


def main():
    actual = {'a1': blob(A1), 'a2': blob(A2)}
    errors = []
    if actual != EXPECTED_BLOBS: fail(errors, 'unexpected_blob', expected=EXPECTED_BLOBS, actual=actual)

    rows = {'a1': load_jsonl(A1), 'a2': load_jsonl(A2)}
    stats = {level: validate_level(level, rs, errors) for level, rs in rows.items()}
    by_id = {level: {r['id']: r for r in rs} for level, rs in rows.items()}

    adj = json.loads(ADJ.read_text(encoding='utf-8'))
    false_review = json.loads(FALSE_REVIEW.read_text(encoding='utf-8'))
    final23 = json.loads(FINAL23.read_text(encoding='utf-8'))

    # Complete diagnostic ledger: every one of the original 321 warnings must end in exactly one resolved bucket.
    if adj.get('source_warning_count') != 321: fail(errors, 'diagnostic_source_count', actual=adj.get('source_warning_count'))
    if adj.get('resolved_count') != 214 or adj.get('unresolved_count') != 107:
        fail(errors, 'diagnostic_first_adjudication_counts', resolved=adj.get('resolved_count'), unresolved=adj.get('unresolved_count'))
    if false_review.get('resolved_variant_diagnostics_count') != 41: fail(errors, 'resolved_variant_count', actual=false_review.get('resolved_variant_diagnostics_count'))
    if false_review.get('removed_false_running_text_reviews_count') != 43: fail(errors, 'removed_false_review_count', actual=false_review.get('removed_false_running_text_reviews_count'))
    if false_review.get('new_target_blocker_count') != 14 or false_review.get('exposure_count_blocker_count') != 9:
        fail(errors, 'second_adjudication_blockers', new=false_review.get('new_target_blocker_count'), exposure=false_review.get('exposure_count_blocker_count'))
    if final23.get('count_repairs') != 14 or final23.get('no_change_adjudications') != 9 or final23.get('learner_text_changes') != 0:
        fail(errors, 'final23_counts', count_repairs=final23.get('count_repairs'), no_change=final23.get('no_change_adjudications'), learner_text_changes=final23.get('learner_text_changes'))
    if 214 + 41 + 43 + 14 + 9 != 321: fail(errors, 'diagnostic_ledger_arithmetic')

    # Assert every removed false running-text declaration is still absent.
    for rem in false_review.get('removals', []):
        pid, tid = rem.get('passage_id'), rem.get('target_id')
        level = 'a1' if '-a1-' in str(pid) else 'a2'
        row = by_id[level].get(pid)
        if not row: fail(errors, 'removed_review_missing_passage', passage_id=pid); continue
        if any(isinstance(t, dict) and t.get('id') == tid for t in row.get('review_lexical_targets', [])):
            fail(errors, 'removed_false_review_reappeared', passage_id=pid, target_id=tid)

    # Assert all 23 final decisions exactly match current target metadata.
    for item in final23.get('changes', []):
        pid, tid = item.get('passage_id'), item.get('target_id'); level = 'a1' if '-a1-' in pid else 'a2'
        row = by_id[level].get(pid)
        matches = [t for t in row.get('new_lexical_targets', []) if isinstance(t, dict) and t.get('id') == tid]
        if len(matches) != 1: fail(errors, 'final23_target_lookup', passage_id=pid, target_id=tid, count=len(matches)); continue
        if matches[0].get('exposures_in_text') != item.get('new_exposures_in_text'):
            fail(errors, 'final23_repair_regressed', passage_id=pid, target_id=tid, expected=item.get('new_exposures_in_text'), actual=matches[0].get('exposures_in_text'))
    for item in final23.get('confirmed_no_change', []):
        pid, tid = item.get('passage_id'), item.get('target_id'); level = 'a1' if '-a1-' in pid else 'a2'
        row = by_id[level].get(pid)
        matches = [t for t in row.get('new_lexical_targets', []) if isinstance(t, dict) and t.get('id') == tid]
        if len(matches) != 1: fail(errors, 'final23_nochange_lookup', passage_id=pid, target_id=tid, count=len(matches)); continue
        if matches[0].get('exposures_in_text') != item.get('exposures_in_text'):
            fail(errors, 'final23_nochange_regressed', passage_id=pid, target_id=tid, expected=item.get('exposures_in_text'), actual=matches[0].get('exposures_in_text'))

    report = {
        'schema_version': 1,
        'date': '2026-08-23',
        'scope': 'Final deterministic Arabic A1+A2 post-repair validation',
        'input_blobs': actual,
        'stats': stats,
        'diagnostic_ledger': {
            'original_diagnostics': 321,
            'resolved_first_pass': 214,
            'resolved_second_pass_variants': 41,
            'removed_false_running_text_reviews': 43,
            'final_count_repairs': 14,
            'final_valid_morphology_no_change': 9,
            'unresolved': 0,
        },
        'hard_error_count': len(errors),
        'hard_errors': errors,
        'quality_promotion': False,
        'status': 'PASS_ZERO_UNRESOLVED_DETERMINISTIC_NEEDS_FINAL_SEMANTIC_READ' if not errors else 'FAIL',
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'hard_errors': len(errors), 'stats': stats, 'diagnostic_ledger': report['diagnostic_ledger']}, ensure_ascii=False))
    if errors:
        print(json.dumps({'error_sample': errors[:50]}, ensure_ascii=False))
        raise SystemExit(1)


if __name__ == '__main__':
    main()
