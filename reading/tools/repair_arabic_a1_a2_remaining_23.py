#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A1 = ROOT / 'reading/arabic/a1/passages.jsonl'
A2 = ROOT / 'reading/arabic/a2/passages.jsonl'
MANIFEST = ROOT / 'reading/audit/arabic_a1_a2_remaining_23_2026-08-23.json'
REPORT = ROOT / 'reading/audit/arabic_a1_a2_remaining_23_adjudicated_repair_2026-08-23.json'
EXPECTED_INPUT = {
    'a1': 'a84ef0bd859e82f3cd85e136c1b9750108d4b1ed',
    'a2': '510baee0040d4bb78272d966666fb62b926b3b8c',
}

# Only these 14 stored exposure counts are wrong. Learner-facing text stays unchanged.
COUNT_REPAIRS = [
    ('ar-a1-u03-p01', 'يحب', 1, 5, ['تحبين ×1', 'أحب/وأحب/أحبه ×4 total']),
    ('ar-a1-u03-p02', 'يحتاج', 1, 5, ['نحتاج ×5']),
    ('ar-a1-u04-p04', 'أخبر', 5, 6, ['أخبرتني/أخبريني/أخبرت/تخبر/نخبر = 6 lemma realizations']),
    ('ar-a1-u06-p02', 'يصل', 1, 5, ['نصل', 'سنصل', 'وصلنا ×2', 'تصل']),
    ('ar-a1-u06-p04', 'ينتظر', 1, 5, ['انتظريني', 'تنتظر ×2', 'انتظرت', 'أنتظر']),
    ('ar-a1-u08-p01', 'يشعر', 1, 4, ['أشعر/تشعرين = 4 lemma realizations']),
    ('ar-a2-u06-p04', 'يتوقف', 1, 2, ['تتوقف ×2']),
    ('ar-a1-u02-p04', 'أيضا', 1, 3, ['أيضًا ×3']),
    ('ar-a1-u03-p04', 'شكرا', 1, 2, ['شكرًا ×2']),
    ('ar-a1-u04-p03', 'مرحبا', 1, 4, ['مرحبًا ×4']),
    ('ar-a1-u05-p05', 'يعود', 3, 4, ['سيعود', 'يعود ×2', 'ستعود']),
    ('ar-a1-u07-p04', 'أيام', 4, 3, ['الأيام', 'أيام ×2']),
    ('ar-a1-u10-p01', 'دائما', 1, 2, ['دائمًا ×2']),
    ('ar-a2-u03-p01', 'مجددا', 1, 2, ['مجددًا ×2']),
]

# These 9 counts are already correct. Earlier matchers missed ordinary Arabic morphology.
NO_CHANGE = [
    ('ar-a1-u08-p05', 'حاول', 4, ['سأحاول', 'تحاول', 'حاولت', 'أحاول']),
    ('ar-a1-u09-p03', 'سعيد', 2, ['سعيدة ×2: feminine agreement']),
    ('ar-a1-u10-p02', 'مختلف', 3, ['مختلفة ×3: adjective agreement']),
    ('ar-a2-u02-p01', 'رد', 4, ['ترد', 'ردًا ×2', 'الرد']),
    ('ar-a2-u02-p02', 'متأكد', 3, ['متأكدة ×3: feminine agreement']),
    ('ar-a2-u02-p04', 'حالي', 2, ['الحالية ×2: feminine agreement']),
    ('ar-a2-u03-p04', 'ظن', 2, ['تظن', 'أظن']),
    ('ar-a1-u09-p01', 'لاعب', 3, ['لاعب', 'لاعبة ×2: feminine agreement']),
    ('ar-a1-u10-p01', 'قليل', 4, ['قليلًا', 'قليل', 'قليلة', 'القليل']),
]


def blob(path):
    return subprocess.check_output(['git', 'hash-object', str(path)], text=True).strip()


def load_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]


def dump_jsonl(path, rows):
    path.write_text('\n'.join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + '\n', encoding='utf-8')


def level_for(pid):
    return 'a1' if '-a1-' in pid else 'a2'


def target(row, form):
    matches = [t for t in row.get('new_lexical_targets', []) if isinstance(t, dict) and t.get('form') == form]
    if len(matches) != 1:
        raise SystemExit(f'{row.get("id")}: expected exactly one new target with form {form!r}, found {len(matches)}')
    return matches[0]


def main():
    actual = {'a1': blob(A1), 'a2': blob(A2)}
    if actual != EXPECTED_INPUT:
        raise SystemExit(f'unexpected input blobs: {actual}')

    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    if manifest.get('count') != 23:
        raise SystemExit(f'expected 23-item blocker manifest, got {manifest.get("count")}')
    manifest_pairs = {(x['passage_id'], (x.get('target_record') or {}).get('form')) for x in manifest['items']}
    decision_pairs = {(p, f) for p, f, *_ in COUNT_REPAIRS} | {(p, f) for p, f, *_ in NO_CHANGE}
    if manifest_pairs != decision_pairs:
        missing = sorted(manifest_pairs - decision_pairs)
        extra = sorted(decision_pairs - manifest_pairs)
        raise SystemExit(f'23-item decision coverage mismatch; missing={missing}, extra={extra}')

    rows = {'a1': load_jsonl(A1), 'a2': load_jsonl(A2)}
    by_id = {level: {r['id']: r for r in rs} for level, rs in rows.items()}
    changes = []
    confirmed = []

    for pid, form, old_count, new_count, evidence in COUNT_REPAIRS:
        row = by_id[level_for(pid)].get(pid)
        if row is None:
            raise SystemExit(f'missing passage {pid}')
        t = target(row, form)
        if t.get('exposures_in_text') != old_count:
            raise SystemExit(f'{pid} {form}: expected old count {old_count}, got {t.get("exposures_in_text")}')
        t['exposures_in_text'] = new_count
        q = row.setdefault('quality', {})
        q['coverage_check'] = 'pending'
        q['status'] = 'draft'
        note = 'Arabic A1/A2 exposure metadata adjudicated 2026-08-23 using explicit lemma/morphology evidence; learner-facing text unchanged; final integrated regression pending.'
        notes = q.setdefault('notes', [])
        if note not in notes:
            notes.append(note)
        changes.append({
            'passage_id': pid,
            'target_id': t.get('id'),
            'form': form,
            'old_exposures_in_text': old_count,
            'new_exposures_in_text': new_count,
            'evidence': evidence,
            'learner_text_changed': False,
        })

    for pid, form, expected_count, evidence in NO_CHANGE:
        row = by_id[level_for(pid)].get(pid)
        if row is None:
            raise SystemExit(f'missing passage {pid}')
        t = target(row, form)
        if t.get('exposures_in_text') != expected_count:
            raise SystemExit(f'{pid} {form}: expected already-correct count {expected_count}, got {t.get("exposures_in_text")}')
        confirmed.append({
            'passage_id': pid,
            'target_id': t.get('id'),
            'form': form,
            'exposures_in_text': expected_count,
            'decision': 'NO_CHANGE_VALID_ARABIC_MORPHOLOGY',
            'evidence': evidence,
        })

    if len(changes) != 14 or len(confirmed) != 9 or len(changes) + len(confirmed) != 23:
        raise SystemExit('repair/adjudication cardinality failure')

    dump_jsonl(A1, rows['a1'])
    dump_jsonl(A2, rows['a2'])
    output = {'a1': blob(A1), 'a2': blob(A2)}
    report = {
        'schema_version': 1,
        'date': '2026-08-23',
        'scope': 'Arabic A1+A2 final 23 exposure diagnostics',
        'input_blobs': actual,
        'output_blobs': output,
        'manifest_count': 23,
        'count_repairs': len(changes),
        'no_change_adjudications': len(confirmed),
        'learner_text_changes': 0,
        'quality_promotion': False,
        'changes': changes,
        'confirmed_no_change': confirmed,
        'status': 'PASS_BOUNDED_REPAIR_NEEDS_FRESH_REGRESSION',
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'status': report['status'],
        'count_repairs': report['count_repairs'],
        'no_change_adjudications': report['no_change_adjudications'],
        'learner_text_changes': 0,
        'output_blobs': output,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
