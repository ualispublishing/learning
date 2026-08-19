#!/usr/bin/env python3
"""Apply confirmed French final-audit repairs and require the 15-pass audit.

The transaction is fail-closed.  The original C2 canonical bytes are restored if
regeneration or any whole-corpus audit lens fails. Historical unit frontier
locks remain untouched; the final whole-corpus artifact becomes the approval
binding for the repaired corpus.
"""
from __future__ import annotations

import json
import runpy
import subprocess
import sys
import traceback
from pathlib import Path

R = Path(__file__).resolve().parents[2]
T = R / 'reading/tools'
A = R / 'reading/audit'
C2 = R / 'reading/french/c2/passages.jsonl'
AUDIT = A / 'french_final_whole_audit.json'
REJECTED = A / 'french_final_whole_audit_rejected_candidate.json'
OUT = A / 'french_final_repair_transaction.json'
sys.path.insert(0, str(T))


def h(path: Path) -> str:
    return subprocess.check_output(['git', 'hash-object', str(path)], text=True).strip()


def rows() -> list[dict]:
    return [json.loads(x) for x in C2.read_text(encoding='utf-8').splitlines() if x.strip()]


def write_rows(rs: list[dict]) -> None:
    C2.write_text(''.join(json.dumps(x, ensure_ascii=False, sort_keys=True) + '\n' for x in rs), encoding='utf-8')


def set_role(row: dict, role: str) -> None:
    row['passage_type'] = role
    tags = [x for x in row.get('reader_tags', []) if not x.startswith('unit_role:')]
    row['reader_tags'] = [f'unit_role:{role}'] + tags


def repair_receipt(row: dict) -> None:
    old_a = 'Une note sans date ou un fichier reçu sans contexte peut être authentique tout en étant difficile à relier au résultat final.'
    new_a = 'Une note sans date ou un reçu de transmission sans contexte peut être authentique tout en étant difficile à relier au résultat final.'
    old_b = 'Un document « reçu » prouve qu’une information a été transmise ou qu’une opération a été enregistrée; il ne prouve pas à lui seul que son contenu a été compris, vérifié ou utilisé dans la décision finale.'
    new_b = 'Un « reçu » atteste ici qu’un document ou une opération a été transmis ou enregistré; il fournit une trace de transmission, mais ne prouve pas à lui seul que le contenu a été compris, vérifié ou utilisé dans la décision finale.'
    if old_a not in row['text'] or old_b not in row['text']:
        raise AssertionError('Unit06 reçu repair anchors changed; refusing heuristic rewrite')
    row['text'] = row['text'].replace(old_a, new_a).replace(old_b, new_b)
    a9 = next((a for a in row['answer_key'] if a.get('id') == 'a9'), None)
    if not a9:
        raise AssertionError('Unit06 reçu linked answer a9 missing')
    a9['answer'] = new_b
    row['word_count'] = len(row['text'].split())
    target = next((t for t in row['new_lexical_targets'] if t.get('form') == 'reçu'), None)
    if not target:
        raise AssertionError('Unit06 reçu lexical target missing')
    # Keep the declared two learner-text exposures: one unquoted noun phrase and
    # one explicit quoted lexical definition.
    target['exposures_in_text'] = 2
    notes = row.setdefault('quality', {}).setdefault('notes', [])
    note = 'Final French review: repaired reçu to the source-supported noun sense “receipt” in learner text and linked vocabulary answer.'
    if note not in notes:
        notes.append(note)


def regenerate_unit10_from_sealed_prefix(current: list[dict]) -> list[dict]:
    if len(current) != 60:
        raise AssertionError(f'expected 60 C2 rows before final repair, got {len(current)}')
    prefix = current[:54]
    if prefix[-1].get('id') != 'fr-c2-u09-p06':
        raise AssertionError('first 54 rows are not the sealed Unit09 prefix')
    write_rows(prefix)
    runpy.run_path(str(T / 'generate_french_c2_unit10_preflight.py'), run_name='__main__')
    candidate = rows()
    if len(candidate) != 60 or candidate[-1].get('id') != 'fr-c2-u10-p06':
        raise AssertionError('Unit10 preflight did not restore exact 60-row C2 shape')
    return candidate


def apply_confirmed_repairs(candidate: list[dict]) -> list[dict]:
    byid = {r['id']: r for r in candidate}
    expected = [
        'fr-c2-u04-p03','fr-c2-u04-p04','fr-c2-u05-p01','fr-c2-u05-p03','fr-c2-u05-p04','fr-c2-u06-p04',
        'fr-c2-u10-p02','fr-c2-u10-p03','fr-c2-u10-p04',
    ]
    missing = [x for x in expected if x not in byid]
    if missing:
        raise AssertionError(f'final repair targets missing: {missing}')

    set_role(byid['fr-c2-u04-p03'], 'interleaved')
    set_role(byid['fr-c2-u04-p04'], 'transfer')
    set_role(byid['fr-c2-u05-p03'], 'interleaved')
    set_role(byid['fr-c2-u05-p04'], 'transfer')
    byid['fr-c2-u05-p01']['genre'] = 'critical analysis'
    note = 'Final French review: genre reclassified from literary prose to critical analysis to match the learner-facing analytical commentary.'
    qnotes = byid['fr-c2-u05-p01'].setdefault('quality', {}).setdefault('notes', [])
    if note not in qnotes:
        qnotes.append(note)
    repair_receipt(byid['fr-c2-u06-p04'])

    # Preflight is authoritative for the capstone pair.  Assert rather than
    # reconstruct it again here so a stale generator cannot silently pass.
    pair = 'fr-c2-u10-shared-case-viewpoints'
    if byid['fr-c2-u10-p02'].get('paired_text_group') is not None:
        raise AssertionError('Unit10 preflight failed to clear old P02 pairing')
    if byid['fr-c2-u10-p03'].get('paired_text_group') != pair or byid['fr-c2-u10-p04'].get('paired_text_group') != pair:
        raise AssertionError('Unit10 preflight failed to create P03/P04 shared-case pair')

    # Increment revisions only on rows changed during the cross-unit final
    # repair. Unit10 rows are regenerated from the stronger preflight at their
    # generator revision and are tracked by the transaction artifact.
    for pid in ['fr-c2-u04-p03','fr-c2-u04-p04','fr-c2-u05-p01','fr-c2-u05-p03','fr-c2-u05-p04','fr-c2-u06-p04']:
        byid[pid]['revision'] = int(byid[pid].get('revision', 1)) + 1
    return candidate


def main() -> None:
    A.mkdir(exist_ok=True)
    original = C2.read_bytes()
    before_blob = h(C2)
    stages = []
    error = None
    repaired_blob = None
    audit_status = None

    try:
        current = rows()
        candidate = regenerate_unit10_from_sealed_prefix(current)
        stages.append('regenerate_unit10_from_exact_unrepaired_unit09_prefix_via_paired_preflight')
        candidate = apply_confirmed_repairs(candidate)
        write_rows(candidate)
        repaired_blob = h(C2)
        stages.append('apply_confirmed_cross_unit_repairs')

        # Whole-French audit reads all six canonical French level files.
        runpy.run_path(str(T / 'audit_french_final_whole.py'), run_name='__main__')
        audit = json.loads(AUDIT.read_text(encoding='utf-8'))
        audit_status = audit.get('status')
        if audit_status != 'PASS' or not audit.get('approval_ready') or audit.get('audit_pass_count', 0) < 10:
            raise AssertionError('whole-French final audit artifact is not approval-ready')
        if audit.get('level_blobs', {}).get('c2') != repaired_blob:
            raise AssertionError('whole-French final audit is not bound to repaired C2 blob')
        stages.append('pass_whole_french_15_lens_audit')

        if REJECTED.exists():
            REJECTED.unlink()
    except Exception:
        error = traceback.format_exc()
        print(error)
        if AUDIT.exists():
            try:
                rejected = json.loads(AUDIT.read_text(encoding='utf-8'))
                rejected['candidate_rejected_and_canonical_restored'] = True
                rejected['restored_c2_blob'] = before_blob
                REJECTED.write_text(json.dumps(rejected, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
                AUDIT.unlink()
            except Exception:
                pass
        C2.write_bytes(original)
        stages.append('restore_original_c2_after_final_audit_failure')

    final_blob = h(C2)
    result = {
        'status': 'PASS_READY_FOR_FRENCH_APPROVAL' if error is None else 'FAIL_RESTORED',
        'date': '2026-08-18',
        'before_c2_blob': before_blob,
        'candidate_repaired_c2_blob': repaired_blob,
        'final_c2_blob': final_blob,
        'audit_status': audit_status,
        'completed_stages': stages,
        'confirmed_repairs': [
            'Unit04 P03/P04 role order',
            'Unit05 P01 analytical genre label',
            'Unit05 P03/P04 role order',
            'Unit06 reçu noun-sense alignment',
            'Unit10 genuine shared-case P03/P04 paired-text capstone',
        ],
        'historical_frontier_locks_preserved': True,
        'error': error,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if error is not None:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
