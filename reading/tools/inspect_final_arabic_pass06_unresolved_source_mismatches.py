#!/usr/bin/env python3
"""Deep-inspect the four Pass-06 source mismatches without exact Front matches."""
from __future__ import annotations
import csv,difflib,json,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
CAND=ROOT/'reading/audit/final_arabic_pass06_source_mismatch_candidates.json'
OUT=ROOT/'reading/audit/final_arabic_pass06_unresolved_source_mismatch_inspection.json'
DIAC=re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]');RANK_RE=re.compile(r'\bRank:\s*(\d+)')
def norm_ar(s):
    s=unicodedata.normalize('NFKC',str(s or '')).replace('ـ','').replace('ٱ','ا');return ''.join(DIAC.sub('',s).split())
def en_terms(s):
    return [x.lower() for x in re.findall(r'[A-Za-z]+',str(s or '')) if x.lower() not in {'a','an','the','to','of','or','and','be','is','in','for','with'} and len(x)>2]
source=[]
for name in ('arabic_top1000.csv','arabic_top3000.csv'):
    with (ROOT/name).open(encoding='utf-8',newline='') as f:
        for row in csv.DictReader(f):
            m=RANK_RE.search(row.get('Back','') or '')
            if m:source.append({'rank':int(m.group(1)),'front':row.get('Front',''),'back':row.get('Back',''),'source_file':name})
# Reader target lookup
reader={}
for level in LEVELS:
    p=ROOT/f'reading/arabic/{level}/passages.jsonl'
    for line in p.read_text(encoding='utf-8').splitlines():
        if not line.strip():continue
        r=json.loads(line)
        for t in r.get('new_lexical_targets',[]):
            if isinstance(t,dict):reader[(r['id'],t.get('id'))]=t
c=json.loads(CAND.read_text(encoding='utf-8'))
items=[]
for x in c['unresolved']:
    t=reader[(x['passage_id'],x['old_target_id'])];form=norm_ar(t.get('form'));lemma=norm_ar(t.get('lemma'));terms=en_terms(t.get('intended_sense'))
    scored=[]
    for s in source:
        sf=norm_ar(s['front']);sim=max(difflib.SequenceMatcher(None,form,sf).ratio(),difflib.SequenceMatcher(None,lemma,sf).ratio())
        back_lower=s['back'].lower();meaning_hits=[term for term in terms if re.search(r'\b'+re.escape(term)+r'\b',back_lower)]
        # keep candidates that are Arabic-form-close or share an intended-sense keyword
        if sim>=0.55 or meaning_hits:
            scored.append({'rank':s['rank'],'front':s['front'],'source_file':s['source_file'],'form_similarity':round(sim,3),'meaning_hits':meaning_hits,'back_excerpt':s['back'][:360]})
    scored.sort(key=lambda y:(bool(y['meaning_hits']),len(y['meaning_hits']),y['form_similarity']),reverse=True)
    items.append({'passage_id':x['passage_id'],'old_target_id':x['old_target_id'],'form':t.get('form'),'lemma':t.get('lemma'),'intended_sense':t.get('intended_sense'),'part_of_speech':t.get('part_of_speech'),'old_source_front':x['old_source_front'],'top_candidates':scored[:12]})
payload={'unresolved_count':len(items),'items':items}
assert len(items)==4,len(items)
OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(payload,ensure_ascii=False))
