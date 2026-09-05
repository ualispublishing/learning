#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / 'reading'
CAN = R / 'arabic/c2/passages.jsonl'
INV = R / 'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'
DEC = R / 'audit/arabic_gate_b_decisions_2026-08-30/c2_u10.json'
IDS = [f'ar-c2-u10-p{i:02d}' for i in range(1, 7)]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def meta() -> dict:
    path = Path(__file__).with_name('apply_arabic_gate_b_c2_unit10.py')
    spec = importlib.util.spec_from_file_location('c2u10', path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.META


def main() -> None:
    raw = CAN.read_bytes()
    rows = [json.loads(line) for line in raw.decode('utf-8').splitlines() if line.strip()]
    canonical_sha = sha(raw)
    if len(rows) != 60 or [rows[i].get('id') for i in range(54, 60)] != IDS:
        raise SystemExit('layout drift')
    for record in rows[54:60]:
        quality = record.get('quality', {})
        if any(quality.get(field) != 'pass' for field in ('linguistic_review', 'pedagogical_review', 'answer_key_check', 'schema_check')):
            raise SystemExit('internal review state drift')
        if quality.get('status') != 'draft' or quality.get('coverage_check') != 'pending':
            raise SystemExit('release state drift')

    inventory = json.loads(INV.read_text(encoding='utf-8'))
    c2 = inventory['levels']['c2']
    if (inventory.get('project_id'), inventory.get('language'), inventory.get('records'), inventory.get('questions'), inventory.get('answers'), c2.get('canonical_sha256')) != ('LANG-A1C2', 'arabic', 360, 3600, 3600, canonical_sha):
        raise SystemExit('inventory drift')

    findings_meta = meta()
    if sum(len(items) for items in findings_meta.values()) != 19 or sum(bool(items) for items in findings_meta.values()) != 6:
        raise SystemExit('finding metadata drift')
    hashes = c2['record_learner_facing_sha256']
    decisions = []
    for pid in IDS:
        findings = [
            {
                'finding_id': f'{pid}-gB-{index:02d}',
                'field': field,
                'dimension': dimension,
                'severity': severity,
                'status': 'REPAIRED',
                'rationale': rationale,
            }
            for index, (field, dimension, severity, rationale) in enumerate(findings_meta[pid], 1)
        ]
        decisions.append({
            'passage_id': pid,
            'learner_facing_sha256': hashes[pid],
            'decision': 'PASS_AFTER_REPAIR',
            'finding_count': len(findings),
            'findings': findings,
        })

    document = {
        'schema_version': 1,
        'project_id': 'LANG-A1C2',
        'language': 'arabic',
        'level': 'C2',
        'unit': 10,
        'date': '2026-09-05',
        'gate': 'Gate B — passage-by-passage linguistic/naturalness audit',
        'canonical_path': 'reading/arabic/c2/passages.jsonl',
        'canonical_sha256': canonical_sha,
        'records_reviewed': 6,
        'records_with_findings': 6,
        'fresh_findings': 19,
        'decisions': decisions,
        'quality_promotion': False,
        'release_claim': False,
        'guard': 'Learner-facing hashes come only from the freshly rebuilt authoritative Gate B inventory and are independently revalidated by the progress synchronizer. Completion of corpus-wide fresh Gate B internal review does not constitute educator/publication release approval.',
    }
    DEC.parent.mkdir(parents=True, exist_ok=True)
    DEC.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
