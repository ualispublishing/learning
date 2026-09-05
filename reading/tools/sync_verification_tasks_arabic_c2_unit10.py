#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / 'reading'
P = R / 'VERIFICATION_TASKS.md'
REL = R / 'RELEASE_STATUS.json'
DEC = R / 'audit/arabic_gate_b_decisions_2026-08-30/c2_u10.json'
REVIEWED = 360
WITH_FINDINGS = 308
FINDINGS = 560
BLOCKERS = 1080


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit('anchor drift: ' + old[:100])
    return text.replace(old, new, 1)


def main() -> None:
    arabic = json.loads(REL.read_text(encoding='utf-8'))['languages']['arabic']
    progress = arabic['naturalness_review_progress']
    gate = arabic['latest_deterministic_gate']
    decision = json.loads(DEC.read_text(encoding='utf-8'))

    if (progress['fresh_records_reviewed'], progress['fresh_records_with_findings'], progress['fresh_findings'], gate['open_findings']) != (REVIEWED, WITH_FINDINGS, FINDINGS, BLOCKERS):
        raise SystemExit('final Gate B counter drift')
    if progress.get('status') != 'FRESH_GATE_B_INTERNAL_REVIEW_COMPLETE':
        raise SystemExit('Gate B completion status drift')
    if progress.get('levels_completed') != ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
        raise SystemExit('completed-level drift')
    if arabic.get('release_state') != 'REOPEN_REQUIRED' or arabic.get('educator_release_ready') is not False:
        raise SystemExit('release boundary drift')
    expected_classes = {
        'coverage_missing_or_zero': 360,
        'coverage_not_pass': 360,
        'not_approved': 360,
    }
    if gate.get('status') != 'FAIL' or gate.get('finding_classes') != expected_classes:
        raise SystemExit('unexpected post-Gate-B deterministic finding classes')
    if (decision['records_reviewed'], decision['records_with_findings'], decision['fresh_findings']) != (6, 6, 19):
        raise SystemExit('decision count drift')
    if decision.get('quality_promotion') is not False or decision.get('release_claim') is not False:
        raise SystemExit('decision release-boundary drift')

    text = P.read_text(encoding='utf-8')
    marker = 'reading/audit/arabic_gate_b_decisions_2026-08-30/c2_u10.json'
    if marker in text:
        return

    text = replace_once(
        text,
        'Current release position: fresh deterministic revalidation is **FAIL** with **1104** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.',
        'Current release position: fresh deterministic revalidation is **FAIL** with **1080** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.',
    )
    text = replace_once(
        text,
        'Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1104**. This is a release-evidence gate, not semantic approval.',
        'Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1080**. This is a release-evidence gate, not semantic approval.',
    )

    unit9 = 'C2 Unit 9 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c2_u09.json` — 6 current-corpus records reviewed and repaired, with 12 fresh high-confidence summary-answer assessment-alignment/naturalness findings closed. Fresh Gate B progress is now 354/360 records; C2 remains in progress and this is not an educator/publication release claim.'
    unit10 = 'C2 Unit 10 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c2_u10.json` — 6 current-corpus records reviewed and repaired, with 19 fresh high-confidence summary/detail assessment-alignment/naturalness/grammar findings closed. Fresh Gate B progress is now 360/360 records; C2 Gate B and the corpus-wide fresh Gate B internal review are complete; this is not an educator/publication release claim.'
    text = replace_once(text, unit9, unit9 + '\n\n' + unit10)

    checklist9 = '- [x] Arabic C2 Unit 9 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 12 fresh summary-answer assessment-alignment/naturalness findings across all 6 records with hash-bound decision evidence;'
    checklist10 = '- [x] Arabic C2 Unit 10 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 19 fresh summary/detail assessment-alignment/naturalness/grammar findings across all 6 records with hash-bound decision evidence; C2 and corpus-wide fresh Gate B internal review are complete;'
    text = replace_once(text, checklist9, checklist9 + '\n' + checklist10)
    text = replace_once(
        text,
        '- [ ] corpus-wide Arabic grammar-in-context naturalness audit;',
        '- [x] corpus-wide Arabic grammar-in-context naturalness audit (fresh Gate B internal review complete; separate semantic/educator/native/blind release gates remain open);',
    )

    P.write_text(text, encoding='utf-8')


if __name__ == '__main__':
    main()
