#!/usr/bin/env python3
"""Serialize the final French C2 Unit10 generation and seal.

Unlike Units 01-09, Unit10 is terminal: a successful run seals the 60-passage
C2 corpus and does not prepare a Unit11 frontier. Whole-French closure is a
separate transaction so deferred cross-unit repairs can be audited atomically.
"""
from __future__ import annotations

import json, os, runpy, subprocess, sys, traceback
from pathlib import Path

R = Path(__file__).resolve().parents[2]
T = R / 'reading/tools'
A = R / 'reading/audit'
C1 = R / 'reading/french/c1/passages.jsonl'
C2 = R / 'reading/french/c2/passages.jsonl'
OUT = A / 'french_c2_unit10_pipeline.json'
sys.path.insert(0, str(T))


def run(name: str) -> None:
    print('=== RUN', name, '===')
    runpy.run_path(str(T / name), run_name='__main__')


def env(name: str, unit: int) -> None:
    old = os.environ.get('C2_UNIT')
    os.environ['C2_UNIT'] = str(unit)
    try:
        run(name)
    finally:
        if old is None:
            os.environ.pop('C2_UNIT', None)
        else:
            os.environ['C2_UNIT'] = old


def rows():
    return [json.loads(x) for x in C2.read_text(encoding='utf-8').splitlines() if x.strip()]


def h(path: Path) -> str:
    return subprocess.check_output(['git', 'hash-object', str(path)], text=True).strip()


def verify() -> dict:
    review = json.loads((A / 'french_c2_unit10_generation_review.json').read_text(encoding='utf-8'))
    lock = json.loads((A / 'french_c2_unit10_frontier_lock.json').read_text(encoding='utf-8'))
    blob = h(C2)
    c1 = h(C1)
    if (
        review.get('status') != 'PASS'
        or review.get('c2_canonical_blob') != blob
        or lock.get('status') != 'PASS'
        or lock.get('c2_canonical_blob') != blob
        or lock.get('c1_canonical_blob') != c1
        or lock.get('last_sequence') != 60
    ):
        raise AssertionError('C2 Unit10 final seal mismatch')
    return lock


def main() -> None:
    A.mkdir(exist_ok=True)
    before = C2.read_bytes()
    starting = len(rows())
    generated = False
    sealed = False
    error = None
    stages = []

    try:
        if starting > 60:
            raise AssertionError(f'Unit10 transaction cannot operate above 60 rows: {starting}')
        if starting == 60:
            verify()
            sealed = True
            stages.append('verify_existing_c2_unit10')
        else:
            if starting != 54:
                raise AssertionError(f'C2 Unit10 requires 54-row Unit09 prefix, got {starting}')
            previous = json.loads((A / 'french_c2_unit09_frontier_lock.json').read_text(encoding='utf-8'))
            if previous.get('status') != 'PASS' or previous.get('c2_canonical_blob') != h(C2):
                raise AssertionError('C2 Unit09 dependency not sealed')

            env('resolve_french_c2_unit_plan.py', 10)
            stages.append('resolve_c2_unit10_plan')
            env('probe_french_c2_unit_targets.py', 10)
            stages.append('probe_c2_unit10_targets')
            run('select_french_c2_unit10_targets.py')
            stages.append('select_c2_unit10_targets')
            run('generate_french_c2_unit10.py')
            generated = True
            stages.append('generate_c2_unit10')
            env('audit_french_c2_unit_generation.py', 10)
            stages.append('audit_c2_unit10')
            env('lock_french_c2_unit_frontier.py', 10)
            stages.append('lock_c2_unit10')
            verify()
            sealed = True
            stages.append('verify_c2_unit10_final_seal')
    except Exception:
        error = traceback.format_exc()
        print(error)
        if generated and not sealed:
            C2.write_bytes(before)
            stages.append('restore_prec2unit10_after_strict_failure')
        (A / 'french_c2_unit10_pipeline_failure.txt').write_text(error, encoding='utf-8')

    if sealed:
        for path in A.glob('french_c2_unit10_*failure.txt'):
            path.unlink(missing_ok=True)

    result = {
        'status': 'PASS_C2_60_READY_FOR_FINAL_FRENCH_AUDIT' if sealed else 'C2_UNIT10_PENDING',
        'date': '2026-08-18',
        'starting_c2_passages': starting,
        'ending_c2_passages': len(rows()),
        'c1_blob': h(C1),
        'c2_blob': h(C2),
        'c2_unit10_pass': sealed,
        'final_french_audit_required': True,
        'completed_stages': stages,
        'error': error,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not sealed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
