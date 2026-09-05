#!/usr/bin/env python3
"""Remove only the completed Arabic Gate B naturalness class from open release work."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / 'reading/RELEASE_STATUS.json'
COMPLETED = 'corpus-wide Arabic grammar-in-context naturalness audit'
EXPECTED_BEFORE = [
    'substantive resolution of fresh deterministic release-evidence blockers (no bulk promotion)',
    COMPLETED,
    'full semantic educator review',
    'independent native/model-family recertification',
    'blind post-repair human review',
    'hash-bound release manifest',
]
EXPECTED_AFTER = [item for item in EXPECTED_BEFORE if item != COMPLETED]


def main() -> None:
    release = json.loads(PATH.read_text(encoding='utf-8'))
    arabic = release['languages']['arabic']
    progress = arabic['naturalness_review_progress']
    gate = arabic['latest_deterministic_gate']

    if arabic.get('release_state') != 'REOPEN_REQUIRED' or arabic.get('educator_release_ready') is not False:
        raise SystemExit('release boundary drift')
    if progress.get('status') != 'FRESH_GATE_B_INTERNAL_REVIEW_COMPLETE':
        raise SystemExit('Gate B is not complete')
    if (progress.get('fresh_records_reviewed'), progress.get('fresh_records_with_findings'), progress.get('fresh_findings')) != (360, 308, 560):
        raise SystemExit('Gate B completion counters drift')
    if progress.get('levels_completed') != ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
        raise SystemExit('Gate B level completion drift')
    if gate.get('status') != 'FAIL' or gate.get('open_findings') != 1080:
        raise SystemExit('deterministic release gate drift')
    if gate.get('finding_classes') != {
        'coverage_missing_or_zero': 360,
        'coverage_not_pass': 360,
        'not_approved': 360,
    }:
        raise SystemExit('unexpected residual deterministic classes')

    open_classes = arabic.get('open_release_classes')
    if open_classes == EXPECTED_AFTER:
        print(json.dumps({'changed': False, 'open_release_classes': open_classes}, ensure_ascii=False, indent=2))
        return
    if open_classes != EXPECTED_BEFORE:
        raise SystemExit('Arabic open release classes drift')

    arabic['open_release_classes'] = EXPECTED_AFTER
    arabic['educator_release_ready'] = False
    PATH.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'changed': True,
        'completed_internal_gate': COMPLETED,
        'open_release_classes': EXPECTED_AFTER,
        'release_state': arabic['release_state'],
        'educator_release_ready': False,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
