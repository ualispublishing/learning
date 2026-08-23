#!/usr/bin/env python3
import copy
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A1 = ROOT / 'reading/arabic/a1/passages.jsonl'
A2 = ROOT / 'reading/arabic/a2/passages.jsonl'
FALSE_REVIEW = ROOT / 'reading/audit/arabic_a1_a2_false_review_metadata_repair_2026-08-23.json'
REPORT = ROOT / 'reading/audit/arabic_a1_a2_question_review_linkage_repair_2026-08-23.json'
EXPECTED = {'a1':'82fc6675e887ec4ce7d833372a068de8e2e8cfb0','a2':'4581f5d003361244b85ff45cde9c8764edf1699b'}

# 15 distinct passage/target pairs account for the 17 final-validator linkage failures.
REPAIR_PAIRS = {
    ('ar-a1-u03-p06','ar-r97'),
    ('ar-a1-u04-p04','ar-r99'),
    ('ar-a1-u06-p06','ar-r317'),
    ('ar-a1-u07-p06','ar-r111'),
    ('ar-a1-u08-p06','ar-r397'),
    ('ar-a1-u09-p06','ar-r480'),
    ('ar-a1-u09-p06','ar-r205'),
    ('ar-a1-u10-p06','ar-r249'),
    ('ar-a2-u01-p06','ar-r583'),
    ('ar-a2-u02-p06','ar-r663'),
    ('ar-a2-u02-p06','ar-r648'),
    ('ar-a2-u03-p06','ar-r885'),
    ('ar-a2-u06-p06','ar-r855'),
    ('ar-a2-u09-p06','ar-r1149'),
    ('ar-a2-u10-p06','ar-r977'),
}


def blob(p): return subprocess.check_output(['git','hash-object',str(p)], text=True).strip()
def load(p): return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def dump(p, rows): p.write_text('\n'.join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows)+'\n', encoding='utf-8')
def level(pid): return 'a1' if '-a1-' in pid else 'a2'

def main():
    actual={'a1':blob(A1),'a2':blob(A2)}
    if actual!=EXPECTED: raise SystemExit(f'unexpected input blobs {actual}')
    rows={'a1':load(A1),'a2':load(A2)}
    idx={l:{r['id']:r for r in rs} for l,rs in rows.items()}
    source=json.loads(FALSE_REVIEW.read_text(encoding='utf-8'))
    removed={(r['passage_id'],r['target_id']):r for r in source.get('removals',[])}
    if not REPAIR_PAIRS <= set(removed):
        raise SystemExit(f'linkage repair pair missing from prior removals: {sorted(REPAIR_PAIRS-set(removed))}')

    changes=[]
    question_refs=0
    for pid,tid in sorted(REPAIR_PAIRS):
        row=idx[level(pid)][pid]
        refs=[q.get('id') for q in row.get('questions',[]) if tid in (q.get('target_ids') or [])]
        if not refs: raise SystemExit(f'{pid} {tid}: no question references target')
        question_refs += len(refs)
        if any(t.get('id')==tid for t in row.get('new_lexical_targets',[]) if isinstance(t,dict)):
            raise SystemExit(f'{pid} {tid}: target unexpectedly new/local already')
        if any(t.get('id')==tid for t in row.get('review_lexical_targets',[]) if isinstance(t,dict)):
            raise SystemExit(f'{pid} {tid}: target unexpectedly already in review metadata')
        prior=copy.deepcopy(removed[(pid,tid)]['removed'])
        if prior.get('representation')!='running_text':
            raise SystemExit(f'{pid} {tid}: prior removal was not running_text')
        prior['representation']='other'
        row.setdefault('review_lexical_targets',[]).append(prior)
        qmeta=row.setdefault('quality',{})
        qmeta['coverage_check']='pending'; qmeta['status']='draft'
        notes=qmeta.setdefault('notes',[])
        note='Arabic A1/A2 linkage repair 2026-08-23: target is reviewed explicitly in assessment questions, not claimed as running-text exposure.'
        if note not in notes: notes.append(note)
        changes.append({'passage_id':pid,'target_id':tid,'form':prior.get('form'),'review_stage':prior.get('review_stage'),'old_representation':'running_text (removed)','new_representation':'other','question_ids':refs})

    if len(changes)!=15 or question_refs!=17:
        raise SystemExit(f'expected 15 target pairs / 17 question refs, got {len(changes)} / {question_refs}')
    dump(A1,rows['a1']); dump(A2,rows['a2'])
    out={'schema_version':1,'date':'2026-08-23','input_blobs':actual,'output_blobs':{'a1':blob(A1),'a2':blob(A2)},'distinct_target_repairs':15,'question_links_repaired':17,'learner_text_changes':0,'changes':changes,'status':'PASS_BOUNDED_LINKAGE_REPAIR_NEEDS_FRESH_REGRESSION'}
    REPORT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:out[k] for k in ('status','output_blobs','distinct_target_repairs','question_links_repaired','learner_text_changes')},ensure_ascii=False))
if __name__=='__main__': main()
