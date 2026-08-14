#!/usr/bin/env python3
"""Final Arabic review pass 05: target-script and orthographic hygiene diagnostics."""
from __future__ import annotations
import json,re,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
OUT=ROOT/'reading/audit/final_arabic_pass05_script_orthography_hygiene.json'
LATIN=re.compile(r'[A-Za-z]')
DOUBLE_SPACE=re.compile(r' {2,}')
ASCII_Q=re.compile(r'\?')
ZERO_WIDTH={'\u200b','\u200c','\u200d','\ufeff'}
REPLACEMENT='�'
TATWEEL='ـ'
REPEAT_AR=re.compile(r'\b([\u0621-\u064A]{2,})\s+\1\b')

def add(flags,code,**kw): flags.append({'code':code,**kw})
def inspect(flags,counter,level,pid,field,value):
    s=str(value or '')
    if LATIN.search(s): add(flags,'latin_character_in_reader_facing_arabic',level=level,passage_id=pid,field=field,sample=s[:240]); counter['latin_character_in_reader_facing_arabic']+=1
    if REPLACEMENT in s: add(flags,'unicode_replacement_character',level=level,passage_id=pid,field=field,sample=s[:240]); counter['unicode_replacement_character']+=1
    if any(z in s for z in ZERO_WIDTH): add(flags,'zero_width_character',level=level,passage_id=pid,field=field); counter['zero_width_character']+=1
    if TATWEEL in s: add(flags,'tatweel_in_canonical_reader_text',level=level,passage_id=pid,field=field,sample=s[:240]); counter['tatweel_in_canonical_reader_text']+=1
    if DOUBLE_SPACE.search(s): add(flags,'double_space',level=level,passage_id=pid,field=field,sample=s[:240]); counter['double_space']+=1
    if ASCII_Q.search(s): add(flags,'ascii_question_mark_in_arabic',level=level,passage_id=pid,field=field,sample=s[:240]); counter['ascii_question_mark_in_arabic']+=1
    if s.count('«')!=s.count('»'): add(flags,'unbalanced_guillemets',level=level,passage_id=pid,field=field,opens=s.count('«'),closes=s.count('»'),sample=s[:240]); counter['unbalanced_guillemets']+=1
    if s.count('(')!=s.count(')'): add(flags,'unbalanced_parentheses',level=level,passage_id=pid,field=field,sample=s[:240]); counter['unbalanced_parentheses']+=1
    m=REPEAT_AR.search(s)
    if m: add(flags,'adjacent_repeated_arabic_word',level=level,passage_id=pid,field=field,word=m.group(1),sample=s[:240]); counter['adjacent_repeated_arabic_word']+=1

def main():
    flags=[]; summaries={}; hard_codes={'latin_character_in_reader_facing_arabic','unicode_replacement_character','zero_width_character','unbalanced_guillemets','unbalanced_parentheses'}
    for level in LEVELS:
        rows=[json.loads(x) for x in (ROOT/f'reading/arabic/{level}/passages.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
        c=Counter(); flagged=set()
        before=len(flags)
        for row in rows:
            pid=row['id']; inspect(flags,c,level,pid,'title',row.get('title','')); inspect(flags,c,level,pid,'text',row.get('text',''))
            for q in row.get('questions',[]): inspect(flags,c,level,pid,f"question:{q.get('id')}",q.get('prompt',''))
            for a in row.get('answer_key',[]): inspect(flags,c,level,pid,f"answer:{a.get('id')}",a.get('answer',''))
        for x in flags[before:]: flagged.add(x['passage_id'])
        summaries[level]={'passages':len(rows),'flagged_passages':len(flagged),'flags_by_code':dict(c)}
    hard=[x for x in flags if x['code'] in hard_codes]
    payload={'pass':5,'name':'script_orthography_hygiene','scope':'Arabic A1-C2 reader-facing title/text/questions/answers','method':'Unicode/script/punctuation balance and machine-artifact diagnostics','levels':summaries,'totals':{'flags':len(flags),'hard_flags':len(hard)},'hard_flags':hard,'flags':flags,'status':'PASS' if not hard else 'FAIL'}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(payload['totals'],ensure_ascii=False));print('status='+payload['status'])
    if hard: raise SystemExit(1)
if __name__=='__main__':main()
