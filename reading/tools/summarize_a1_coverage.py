import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
src = root / 'reading' / 'audit' / 'a1_unit01_coverage_audit.json'
out = root / 'reading' / 'audit' / 'a1_unit01_coverage_compact.json'
data = json.loads(src.read_text(encoding='utf-8'))
summary = {'method': data['method'], 'languages': {}}
for language, block in data['languages'].items():
    rows = []
    for p in block['passages']:
        rows.append({
            'id': p['id'],
            'inventory_3000_coverage': p['inventory_3000_coverage'],
            'rank500_diagnostic_coverage': p['a1_planning_core_coverage'],
            'rank_gt500_tokens': p['top_rank_gt_500_tokens'],
            'outside_3000_tokens': p['top_outside_3000_tokens'],
            'new_target_count': p['new_target_count']
        })
    summary['languages'][language] = rows
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
