#!/usr/bin/env python3
"""Repair only Arabic C2 sequence numbering for Units 07-10.

Generation-continuity maintenance, not a linguistic/pedagogical audit. The script
refuses to write unless the full 60-passage C2 corpus is present with six unique
passage IDs per unit. It changes only `sequence` and line order.
"""
from __future__ import annotations
import json,re
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/c2/passages.jsonl'
ID_RE=re.compile(r'^ar-c2-u(\d{2})-p(\d{2})$')


def main():
    rows=[json.loads(line) for line in PATH.read_text(encoding='utf-8').splitlines() if line.strip()]
    c2=[r for r in rows if r.get('cefr')=='C2']
    if len(c2)!=60:
        raise RuntimeError(f'refusing sequence repair: expected 60 C2 rows, found {len(c2)}')
    ids=[r.get('id') for r in c2]
    dup=[x for x,n in Counter(ids).items() if n!=1]
    if dup:
        raise RuntimeError(f'refusing sequence repair: duplicate/nonunique IDs {dup}')
    by_unit=defaultdict(list)
    for r in c2:
        m=ID_RE.match(str(r.get('id','')))
        if not m:
            raise RuntimeError(f"unexpected C2 passage id: {r.get('id')}")
        unit=int(m.group(1)); passage=int(m.group(2))
        if int(r.get('unit'))!=unit:
            raise RuntimeError(f"unit/id mismatch: {r.get('id')} unit={r.get('unit')}")
        by_unit[unit].append((passage,r))
    if set(by_unit)!=set(range(1,11)):
        raise RuntimeError(f'refusing sequence repair: units present={sorted(by_unit)}')
    for unit in range(1,11):
        ps=sorted(p for p,_ in by_unit[unit])
        if ps!=list(range(1,7)):
            raise RuntimeError(f'unit {unit}: expected passage numbers 1..6, found {ps}')

    changed=[]
    for unit in range(7,11):
        base=(unit-1)*6
        for passage,r in by_unit[unit]:
            expected=base+passage
            old=r.get('sequence')
            if old!=expected:
                r['sequence']=expected
                changed.append({'id':r['id'],'old':old,'new':expected})

    seqs=sorted(int(r.get('sequence')) for r in c2)
    if seqs!=list(range(1,61)):
        raise RuntimeError(f'repaired C2 sequences are not exactly 1..60: {seqs}')

    # Verify the transformation's scope: no object keys except `sequence` were intentionally changed.
    rows.sort(key=lambda r:(0 if r.get('cefr')=='C2' else 1, int(r.get('sequence',999999)), str(r.get('id',''))))
    PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
    print(json.dumps({'c2_rows':60,'units':10,'sequence_gate':'PASS','changed':changed},ensure_ascii=False))

if __name__=='__main__':
    main()
