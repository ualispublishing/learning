#!/usr/bin/env python3
import json
from pathlib import Path
import final_validate_arabic_a1_a2_2026_08_23 as base

ROOT = Path(__file__).resolve().parents[2]
LINKAGE = ROOT / 'reading/audit/arabic_a1_a2_question_review_linkage_repair_2026-08-23.json'
BASE_REPORT = ROOT / 'reading/audit/arabic_a1_a2_final_validation_2026-08-23.json'
OUT = ROOT / 'reading/audit/arabic_a1_a2_final_validation_post_linkage_2026-08-23.json'
EXPECTED = {
    'a1': 'bf7f0a6023b1cb129c9328021892d93cb120fa38',
    'a2': '90b6f2f334b689200c76b25c3b7b983f89230555',
}

def load_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]

def main():
    # Re-run the complete structural/Q&A/CEFR/diagnostic-ledger validator against the post-linkage blobs.
    base.EXPECTED_BLOBS = EXPECTED
    try:
        base.main()
    except SystemExit as exc:
        if exc.code not in (0, None, 1):
            raise

    r = json.loads(BASE_REPORT.read_text(encoding='utf-8'))
    linkage = json.loads(LINKAGE.read_text(encoding='utf-8'))
    if linkage.get('output_blobs') != EXPECTED:
        raise SystemExit(f'linkage output blobs do not match expected final blobs: {linkage.get("output_blobs")}')
    if linkage.get('distinct_target_repairs') != 15 or linkage.get('question_links_repaired') != 17 or linkage.get('learner_text_changes') != 0:
        raise SystemExit('linkage repair cardinality/evidence mismatch')

    expected_pairs = {(x['passage_id'], x['target_id']) for x in linkage.get('changes', [])}
    base_errors = r.get('hard_errors', [])
    tolerated = []
    unexpected = []
    for e in base_errors:
        pair = (e.get('passage_id'), e.get('target_id'))
        if e.get('code') == 'removed_false_review_reappeared' and pair in expected_pairs:
            tolerated.append(e)
        else:
            unexpected.append(e)
    if len(tolerated) != 15 or {(e.get('passage_id'),e.get('target_id')) for e in tolerated} != expected_pairs:
        unexpected.append({'code':'expected_nonrunning_review_accounting','expected_pairs':sorted(expected_pairs),'tolerated_pairs':sorted((e.get('passage_id'),e.get('target_id')) for e in tolerated)})

    rows = {'a1': load_jsonl(base.A1), 'a2': load_jsonl(base.A2)}
    idx = {level: {row['id']: row for row in rs} for level, rs in rows.items()}
    linkage_checks = []
    for change in linkage.get('changes', []):
        pid, tid = change['passage_id'], change['target_id']
        level = 'a1' if '-a1-' in pid else 'a2'
        row = idx[level][pid]
        matches = [t for t in row.get('review_lexical_targets', []) if isinstance(t,dict) and t.get('id') == tid]
        if len(matches) != 1:
            unexpected.append({'code':'post_linkage_target_cardinality','passage_id':pid,'target_id':tid,'count':len(matches)})
            continue
        t = matches[0]
        if t.get('representation') == 'running_text':
            unexpected.append({'code':'false_running_text_claim_reintroduced','passage_id':pid,'target_id':tid})
        if t.get('representation') != 'other':
            unexpected.append({'code':'assessment_review_representation','passage_id':pid,'target_id':tid,'value':t.get('representation')})
        refs = [q.get('id') for q in row.get('questions', []) if tid in (q.get('target_ids') or [])]
        if sorted(refs) != sorted(change.get('question_ids', [])):
            unexpected.append({'code':'assessment_review_question_refs','passage_id':pid,'target_id':tid,'expected':change.get('question_ids',[]),'actual':refs})
        linkage_checks.append({'passage_id':pid,'target_id':tid,'representation':t.get('representation'),'question_ids':refs})

    final = {
        'schema_version': 2,
        'date': '2026-08-23',
        'scope': 'Final deterministic Arabic A1+A2 validation after assessment-review linkage repair',
        'input_blobs': EXPECTED,
        'base_validator_stats': r.get('stats'),
        'diagnostic_ledger': r.get('diagnostic_ledger'),
        'assessment_review_linkage': {
            'distinct_targets': 15,
            'question_links': 17,
            'learner_text_changes': 0,
            'checks': linkage_checks,
        },
        'base_expected_tolerated_errors': len(tolerated),
        'hard_error_count': len(unexpected),
        'hard_errors': unexpected,
        'quality_promotion': False,
        'status': 'PASS_ZERO_UNRESOLVED_DETERMINISTIC_NEEDS_FINAL_SEMANTIC_READ' if not unexpected else 'FAIL',
    }
    OUT.write_text(json.dumps(final, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status':final['status'],'hard_errors':len(unexpected),'stats':final['base_validator_stats'],'diagnostic_ledger':final['diagnostic_ledger'],'assessment_review_targets':15,'question_links':17}, ensure_ascii=False))
    if unexpected:
        print(json.dumps({'error_sample':unexpected[:50]},ensure_ascii=False))
        raise SystemExit(1)

if __name__ == '__main__':
    main()
