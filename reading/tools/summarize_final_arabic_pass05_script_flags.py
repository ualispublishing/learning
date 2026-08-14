#!/usr/bin/env python3
"""Create a compact actionable inventory from Pass-05 script/orthography flags."""
from __future__ import annotations
import json,re
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'reading/audit/final_arabic_pass05_script_orthography_hygiene.json'
OUT=ROOT/'reading/audit/final_arabic_pass05_script_flag_summary.json'
LATIN_RUN=re.compile(r'[A-Za-z][A-Za-z0-9+-]*(?:[ /;,-]+[A-Za-z][A-Za-z0-9+-]*)*')
a=json.loads(SRC.read_text(encoding='utf-8'))
flags=a.get('flags',[])
by_code=Counter(x['code'] for x in flags);latin=[];other=[]
for x in flags:
    if x['code']=='latin_character_in_reader_facing_arabic':
        sample=x.get('sample','');runs=LATIN_RUN.findall(sample)
        latin.append({'level':x['level'],'passage_id':x['passage_id'],'field':x['field'],'latin_runs':runs,'sample':sample})
    else:other.append(x)
payload={'flag_count':len(flags),'by_code':dict(by_code),'latin_flags':latin,'other_flags':other,'distinct_latin_runs':dict(Counter(run for x in latin for run in x['latin_runs']).most_common())}
OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'flag_count':len(flags),'by_code':dict(by_code),'distinct_latin_runs':payload['distinct_latin_runs']},ensure_ascii=False))
