#!/usr/bin/env python3
"""Audit every live Urdu 1001..3000 meaning against independent bilingual evidence.

The previous promotion gate verified lexical provenance, but a Direct WordNet link can
still select a rare homograph that is inappropriate for the high-frequency surface
form. This audit therefore treats agreement among Kaikki, ReadUrdu and word2word as
separate evidence from the IWN-En selected meaning and explicitly identifies cases
where independent sources agree against the published gloss.
"""
from __future__ import annotations
import csv,json,re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EVID=ROOT/'audit/urdu_top3000_continuation_evidence_v7.csv'
OUT=ROOT/'audit/urdu_top3000_sense_risk.json'
QUEUE=ROOT/'audit/urdu_top3000_sense_risk_queue.csv'
WORD=re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
STOP={'a','an','the','to','of','and','or','for','as','be','is','are','was','were','with','by','from','that','which','who','this','it','he','she','they','you','i','we','one','ones','someone','something','having','used','use'}

def toks(t):
    out=set()
    for w in WORD.findall(t or ''):
        w=w.lower().strip("'-")
        if w in STOP or len(w)<2: continue
        if len(w)>4 and w.endswith('ies'): w=w[:-3]+'y'
        else:
            for suf in ('ingly','ation','ments','ment','ing','ied','ed','es','s'):
                if len(w)>len(suf)+3 and w.endswith(suf): w=w[:-len(suf)]; break
        if w not in STOP: out.add(w)
    return out

def clean(s):
    s=(s or '').replace('_',' ')
    s=re.sub(r'\([^)]*\)',' ',s)
    s=re.sub(r'[^A-Za-z0-9; /,\-]+',' ',s)
    return re.sub(r'\s+',' ',s).strip()

def agree(a,c): return bool(a and c and toks(clean(a))&toks(clean(c)))

def compact(s,n=220):
    s=re.sub(r'\s+',' ',s or '').strip()
    return s[:n]

def main():
    with EVID.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    queue=[]; cats=Counter(); support_hist=Counter()
    for r in rows:
        m=r['meaning']; kg=r.get('kaikki_meaning',''); rg=r.get('readurdu_meaning',''); wg=r.get('word2word_meaning','')
        supports=[name for name,s in [('kaikki',kg),('readurdu',rg),('word2word',wg)] if agree(m,s)]
        pairs=[]
        for a,sa,bn,sb in [('kaikki',kg,'readurdu',rg),('kaikki',kg,'word2word',wg),('readurdu',rg,'word2word',wg)]:
            if agree(sa,sb): pairs.append(f'{a}+{bn}')
        support_hist[len(supports)]+=1
        risk='pass'; reason=''
        if pairs and not supports:
            risk='block'; reason='independent_sources_agree_against_published_meaning'
        elif not supports:
            risk='review'; reason='no_independent_bilingual_support'
        elif len(supports)==1 and pairs:
            disagree_pair=[p for p in pairs if supports[0] not in p]
            if disagree_pair:
                risk='block'; reason='one_source_support_but_other_two_agree_elsewhere'
        if re.search(r'\b\w+\(a\)\b|\b\w+\(n\)\b|\b\w+\(v\)\b',m):
            if risk=='pass': risk='review'; reason='raw_wordnet_pos_marker'
        if risk!='pass':
            cats[(risk,reason)]+=1
            queue.append({
                'rank':r['rank'],'front':r['front'],'published_meaning':m,
                'risk':risk,'reason':reason,'supporting_sources':'+'.join(supports),
                'external_agreement_pairs':'+'.join(pairs),
                'kaikki_meaning':compact(kg),'readurdu_meaning':compact(rg),
                'word2word_meaning':compact(wg),'evidence_tier':r.get('evidence_tier',''),
                'semantic_basis':r.get('semantic_basis','')})
    queue.sort(key=lambda q:(0 if q['risk']=='block' else 1,int(q['rank'])))
    summary={
        'rows':len(rows),'support_histogram':{str(k):v for k,v in sorted(support_hist.items())},
        'pass_rows':len(rows)-len(queue),
        'block_rows':sum(1 for q in queue if q['risk']=='block'),
        'review_rows':sum(1 for q in queue if q['risk']=='review'),
        'category_counts':{f'{a}:{b}':v for (a,b),v in cats.items()},
        'public_ready':not queue,
        'policy':'Every published Urdu continuation meaning needs independent bilingual support; disagreement between two independent sources and the published gloss blocks publication.'
    }
    OUT.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    fields=list(queue[0]) if queue else ['rank','front','published_meaning','risk','reason']
    with QUEUE.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(queue)
    (ROOT/'audit/urdu_top3000_sense_risk_sample.json').write_text(json.dumps(queue[:250],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
