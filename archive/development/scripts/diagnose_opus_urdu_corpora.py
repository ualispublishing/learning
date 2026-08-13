#!/usr/bin/env python3
from __future__ import annotations
import json,requests
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'audit/opus_urdu_independent_corpora.json'
API='https://opus.nlpl.eu/opusapi/'

def main():
    params={'preprocessing':'moses','version':'latest','source':'ur','target':'en'}
    r=requests.get(API,params=params,timeout=60);r.raise_for_status();data=r.json()
    rows=data.get('corpora') or data.get('result') or data
    found=[]
    if isinstance(rows,dict):
        rows=[rows]
    if isinstance(rows,list):
        for x in rows:
            if not isinstance(x,dict): continue
            url=x.get('url') or x.get('download') or x.get('download_url') or ''
            corpus=x.get('corpus') or x.get('name') or x.get('release') or ''
            found.append({'corpus':corpus,'url':url,'raw':x})
    # OPUS API sometimes returns nested corpus entries under a top-level field.
    if not found and isinstance(data,dict):
        for k,v in data.items():
            if isinstance(v,list):
                for x in v:
                    if isinstance(x,dict) and ('url' in x or 'corpus' in x):
                        found.append({'corpus':x.get('corpus') or x.get('name') or k,'url':x.get('url',''),'raw':x})
    independent=[]
    for x in found:
        s=(x['corpus']+' '+x['url']).lower()
        if 'opensubtitles' in s or 'opus-100' in s: continue
        independent.append(x)
    preferred=[x for x in independent if any(n in (x['corpus']+' '+x['url']).lower() for n in ('globalvoices','tatoeba','ted2020','ted2013','qed','tanzil','wikipedia','wikimedia','wikimatrix','nllb','ccmatrix'))]
    out={'api_request_url':r.url,'top_level_type':type(data).__name__,'top_level_keys':list(data) if isinstance(data,dict) else [],'all_entries':found,'independent_entries':independent,'preferred_independent_entries':preferred}
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'all':len(found),'independent':len(independent),'preferred':len(preferred),'preferred_names':[x['corpus'] for x in preferred]},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
