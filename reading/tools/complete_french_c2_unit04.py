#!/usr/bin/env python3
"""Serialize French C2 Unit04 generation/seal and prepare Unit05."""
from __future__ import annotations

import json
import os
import runpy
import subprocess
import sys
import traceback
from pathlib import Path

R = Path(__file__).resolve().parents[2]
T = R / 'reading/tools'
A = R / 'reading/audit'
C1 = R / 'reading/french/c1/passages.jsonl'
C2 = R / 'reading/french/c2/passages.jsonl'
OUT = A / 'french_c2_unit04_pipeline.json'
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
    if not C2.exists():
        return []
    return [json.loads(x) for x in C2.read_text(encoding='utf-8').splitlines() if x.strip()]


def h(path: Path) -> str:
    return subprocess.check_output(['git', 'hash-object', str(path)], text=True).strip()


def verify():
    review = json.loads((A / 'french_c2_unit04_generation_review.json').read_text(encoding='utf-8'))
    lock = json.loads((A / 'french_c2_unit04_frontier_lock.json').read_text(encoding='utf-8'))
    blob = h(C2)
    c1 = h(C1)
    if (
        review.get('status') != 'PASS'
        or review.get('c2_canonical_blob') != blob
        or lock.get('status') != 'PASS'
        or lock.get('c2_canonical_blob') != blob
        or lock.get('c1_canonical_blob') != c1
        or lock.get('last_sequence') != 24
    ):
        raise AssertionError('C2 Unit04 seal mismatch')
    return lock


def prepare_unit05(stages):
    env('resolve_french_c2_unit_plan.py', 5)
    stages.append('resolve_c2_unit05_plan')
    env('probe_french_c2_unit_targets.py', 5)
    stages.append('probe_c2_unit05_targets')
    env('sync_french_c2_unit_frontier.py', 4)
    stages.append('sync_c2_unit04_to_unit05')


def main() -> None:
    A.mkdir(exist_ok=True)
    before = C2.read_bytes() if C2.exists() else None
    starting = len(rows())
    generated = False
    sealed = False
    frontier = False
    error = None
    stages = []

    try:
        if starting > 24:
            raise AssertionError(f'Unit04 transaction cannot operate above 24 rows: {starting}')
        if starting == 24:
            verify()
            sealed = True
            stages.append('verify_existing_c2_unit04')
            prepare_unit05(stages)
            frontier = True
        else:
            if starting != 18:
                raise AssertionError(f'C2 Unit04 requires 18-row Unit03 prefix, got {starting}')
            previous = json.loads((A / 'french_c2_unit03_frontier_lock.json').read_text(encoding='utf-8'))
            if previous.get('status') != 'PASS' or previous.get('c2_canonical_blob') != h(C2):
                raise AssertionError('C2 Unit03 dependency not sealed')

            env('resolve_french_c2_unit_plan.py', 4)
            stages.append('resolve_c2_unit04_plan')
            env('probe_french_c2_unit_targets.py', 4)
            stages.append('probe_c2_unit04_targets')
            run('select_french_c2_unit04_targets.py')
            stages.append('select_c2_unit04_targets')
            run('generate_french_c2_unit04_preflight.py')
            generated = True
            stages.append('generate_c2_unit04')
            env('audit_french_c2_unit_generation.py', 4)
            stages.append('audit_c2_unit04')
            env('lock_french_c2_unit_frontier.py', 4)
            stages.append('lock_c2_unit04')
            verify()
            sealed = True
            prepare_unit05(stages)
            frontier = True
    except Exception:
        error = traceback.format_exc()
        print(error)
        if generated and not sealed:
            C2.write_bytes(before)
            stages.append('restore_prec2unit04_after_strict_failure')
        elif sealed:
            stages.append('preserve_sealed_c2_unit04_despite_unit05_prep_failure')
        (A / 'french_c2_unit04_pipeline_failure.txt').write_text(error, encoding='utf-8')

    if frontier:
        for path in A.glob('french_c2_unit04_*failure.txt'):
            path.unlink(missing_ok=True)

    result = {
        'status': 'PASS_TO_C2_UNIT05' if frontier else ('C2_UNIT04_PASS_UNIT05_PREP_PENDING' if sealed else 'C2_UNIT04_PENDING'),
        'date': '2026-08-18',
        'starting_c2_passages': starting,
        'ending_c2_passages': len(rows()),
        'c1_blob': h(C1),
        'c2_blob': h(C2),
        'c2_unit04_pass': sealed,
        'c2_unit05_frontier_prepared': frontier,
        'completed_stages': stages,
        'error': error,
    }
    if frontier:
        plan = json.loads((A / 'french_c2_unit05_plan.json').read_text(encoding='utf-8'))
        probe = json.loads((A / 'french_c2_unit05_target_probe.json').read_text(encoding='utf-8'))
        result.update({
            'unit05_theme': plan['theme'],
            'unit05_genres': plan['genres'],
            'remaining_fresh_source_terms': probe['fresh_count'],
        })

    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not frontier:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
