#!/usr/bin/env python3
"""Build structural generation manifests for Arabic CEFR passage corpora.

This is a production-completeness check only. It does not inspect linguistic
correctness, CEFR validity, answer correctness, lexical coverage, pedagogy,
factual accuracy, or any other deferred quality criterion.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
OUT=ROOT/'reading'/'manifests'/'arabic_generation_manifest.json'


def load_rows(level):
    path=ROOT/'reading'/'arabic'/level/'passages.jsonl'
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def summarize(level, rows):
    units=sorted({r.get('unit') for r in rows if isinstance(r.get('unit'),int)})
    ids=[r.get('id') for r in rows]
    q_counts=[len(r.get('questions',[])) for r in rows]
    a_counts=[len(r.get('answer_key',[])) for r in rows]
    return {
        'level':level.upper(),
        'passages':len(rows),
        'units':units,
        'unique_passage_ids':len(set(ids)),
        'all_records_have_10_questions':bool(rows) and all(n==10 for n in q_counts),
        'all_records_have_10_answers':bool(rows) and all(n==10 for n in a_counts),
        'generation_complete':(
            len(rows)==60 and units==list(range(1,11)) and len(set(ids))==60
            and all(n==10 for n in q_counts) and all(n==10 for n in a_counts)
        ),
        'quality_audit_performed':False,
    }


def main():
    levels={level:summarize(level,load_rows(level)) for level in LEVELS}
    payload={
        'scope':'Arabic generation-stage structural completeness only',
        'not_a_quality_audit':True,
        'levels':levels,
        'notes':[
            'generation_complete means only 60 records, units 1-10, unique passage IDs, and 10 question/answer objects per passage.',
            'It makes no claim about linguistic correctness, CEFR calibration, question/answer validity, lexical coverage, pedagogy, or factual accuracy.',
            'All formal quality checks remain deferred to the final multi-pass audit phase.'
        ]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('; '.join(f"{k.upper()}={v['passages']} complete={v['generation_complete']}" for k,v in levels.items()))

if __name__=='__main__':
    main()
