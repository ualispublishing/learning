#!/usr/bin/env python3
"""Approve French reading only from a live, hash-bound whole-corpus PASS."""
from __future__ import annotations

import json
import subprocess
from datetime import date
from pathlib import Path

R = Path(__file__).resolve().parents[2]
READING = R / 'reading'
A = READING / 'audit'
F = READING / 'french'
AUDIT = A / 'french_final_whole_audit.json'
REPAIR = A / 'french_final_repair_transaction.json'
APPROVAL = A / 'french_final_approval.json'
STATUS = READING / 'STATUS.json'
LEVELS = ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']


def h(path: Path) -> str:
    return subprocess.check_output(['git', 'hash-object', str(path)], text=True).strip()


def main() -> None:
    audit = json.loads(AUDIT.read_text(encoding='utf-8'))
    repair = json.loads(REPAIR.read_text(encoding='utf-8'))

    if audit.get('status') != 'PASS' or not audit.get('approval_ready') or audit.get('audit_pass_count', 0) < 10:
        raise AssertionError('French whole audit not approval-ready')
    if repair.get('status') != 'PASS_READY_FOR_FRENCH_APPROVAL' or repair.get('audit_status') != 'PASS':
        raise AssertionError('French repair transaction not PASS')
    if repair.get('historical_frontier_locks_preserved') is not True:
        raise AssertionError('French historical frontier locks were not preserved')
    if repair.get('temporary_source_binding_restored') is not True:
        raise AssertionError('French temporary source binding was not restored')

    live = {level: h(F / level / 'passages.jsonl') for level in LEVELS}
    if audit.get('level_blobs') != live:
        raise AssertionError('French audit level blobs do not match live canonical files')
    if repair.get('final_c2_blob') != live['c2']:
        raise AssertionError('French repair artifact C2 blob does not match live canonical')
    if audit.get('canonical_passages') != 360 or audit.get('questions') != 3600 or audit.get('answers') != 3600:
        raise AssertionError('French final corpus cardinality mismatch')
    if audit.get('failed_passes'):
        raise AssertionError('French whole audit still contains failed passes')

    today = date.today().isoformat()
    approval = {
        'status': 'APPROVED',
        'language': 'fr',
        'scope': 'French graded reading A1-C2',
        'date': today,
        'canonical_passages': 360,
        'questions': 3600,
        'answers': 3600,
        'audit_version': audit.get('audit_version', 3),
        'audit_pass_count': audit['audit_pass_count'],
        'whole_corpus_sha256': audit['whole_corpus_sha256'],
        'level_blobs': live,
        'repair_transaction_status': repair['status'],
        'repair_final_c2_blob': repair['final_c2_blob'],
        'historical_frontier_locks_preserved': True,
        'temporary_source_binding_restored': True,
        'approval_basis': 'live canonical hashes match a whole-corpus audit with all required independent passes PASS',
    }
    APPROVAL.write_text(json.dumps(approval, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    # Update the repository's current multi-language registry.  Earlier versions of
    # this gate wrote a legacy single-language status shape; remove those fields so
    # STATUS remains unambiguous and the next language can resume cleanly.
    s = json.loads(STATUS.read_text(encoding='utf-8'))
    for legacy_key in ('status', 'mode', 'canonical_passages', 'unapproved_passages', 'generation', 'final_audit', 'next_action'):
        s.pop(legacy_key, None)

    s['updated'] = today
    s['overall_status'] = 'in_progress'
    s['active_language'] = 'Urdu'
    s['paused_languages'] = [lang for lang in s.get('paused_languages', []) if lang != 'Urdu']
    s['phase'] = 'Arabic and French are formally sealed. Urdu is active from the six preserved A1 calibration passages.'
    s['approved_passages'] = 720

    french = s.setdefault('french', {})
    french.update({
        'state': 'APPROVED',
        'canonical_passages': 360,
        'questions': 3600,
        'answers': 3600,
        'formal_final_approval': True,
        'generation_complete': True,
        'next_target': 'None. French is hash-bound approved; reopen only after a deliberate canonical French change invalidates approval.',
        'final_audit': {
            'status': 'PASS',
            'approval': 'APPROVED',
            'audit_version': audit.get('audit_version', 3),
            'audit_pass_count': audit['audit_pass_count'],
            'failed_pass_count': len(audit.get('failed_passes', [])),
            'audit_artifact': 'reading/audit/french_final_whole_audit.json',
            'repair_artifact': 'reading/audit/french_final_repair_transaction.json',
            'approval_artifact': 'reading/audit/french_final_approval.json',
            'whole_corpus_sha256': audit['whole_corpus_sha256'],
            'level_blobs': live,
        },
    })
    for key in ('a1_completion', 'a2_completion', 'b1_completion'):
        if isinstance(french.get(key), dict):
            french[key]['state'] = 'FINAL_APPROVED'
    if isinstance(french.get('b2_generation'), dict):
        french['b2_generation']['state'] = 'FINAL_APPROVED'
    if isinstance(french.get('c1_generation'), dict):
        french['c1_generation']['status'] = 'FINAL_APPROVED'
    if isinstance(french.get('c2_generation'), dict):
        french['c2_generation']['status'] = 'FINAL_APPROVED'
        french['c2_generation']['canonical_blob'] = live['c2']

    urdu = s.setdefault('urdu', {})
    urdu['state'] = 'ACTIVE_A1'
    urdu['canonical_passages'] = 6
    urdu.setdefault('levels', {}).update({'a1': 6, 'a2': 0, 'b1': 0, 'b2': 0, 'c1': 0, 'c2': 0})
    urdu['next_target'] = 'Audit and accept the six preserved Urdu A1 calibration passages against current standards, then continue A1 from sequence 7.'

    s['next_actions'] = [
        'keep Arabic sealed unless canonical Arabic changes',
        'keep French sealed unless deliberate canonical French changes invalidate its hash-bound approval',
        'run a strict current-standard audit of the six preserved Urdu A1 calibration passages',
        'after Urdu A1 calibration is accepted, continue A1 from sequence 7 in guarded six-passage units',
    ]
    STATUS.write_text(json.dumps(s, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    print(json.dumps({
        'status': 'APPROVED',
        'whole_corpus_sha256': audit['whole_corpus_sha256'],
        'level_blobs': live,
        'next_active_language': 'Urdu',
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
