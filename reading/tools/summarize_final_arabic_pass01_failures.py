#!/usr/bin/env python3
"""Summarize final Arabic pass-01 failures so schema drift and record misuse can be separated."""
from __future__ import annotations
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'reading/audit/final_arabic_pass01_data_integrity.json'
OUT=ROOT/'reading/audit/final_arabic_pass01_failure_summary.json'

def normalized_path(path: str) -> str:
    parts=[]
    for part in (path or '').split('/'):
        if part.isdigit():
            parts.append('*')
        else:
            parts.append(part)
    return '/'.join(parts)

def main():
    data=json.loads(SRC.read_text(encoding='utf-8'))
    issues=data.get('hard_issues',[])
    by_code=Counter()
    by_level=Counter()
    by_path=Counter()
    by_message=Counter()
    path_examples=defaultdict(list)
    for x in issues:
        by_code[x.get('code','')]+=1
        by_level[x.get('level','')]+=1
        p=normalized_path(x.get('path',''))
        if p:
            by_path[p]+=1
            if len(path_examples[p])<5:
                path_examples[p].append({k:x.get(k) for k in ('level','passage_id','path','message')})
        m=x.get('message','')
        if m:
            # Normalize literal invalid values in enum messages to expose the contract category.
            enum_m=re.sub(r"^'.*?' is not one of ","<VALUE> is not one of ",m)
            by_message[enum_m]+=1
    payload={
        'source':'reading/audit/final_arabic_pass01_data_integrity.json',
        'hard_issue_total':len(issues),
        'by_code':dict(by_code),
        'by_level':dict(by_level),
        'by_normalized_schema_path':dict(by_path.most_common()),
        'normalized_message_families':dict(by_message.most_common()),
        'path_examples':dict(path_examples),
    }
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(payload,ensure_ascii=False))
if __name__=='__main__':main()
