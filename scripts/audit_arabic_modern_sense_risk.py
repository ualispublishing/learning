#!/usr/bin/env python3
"""Modern-sense risk audit for both live Arabic vocabulary decks."""
from __future__ import annotations
import csv,json,re,runpy
from pathlib import Path
from collections import Counter
from word2word import Word2word

ROOT=Path(__file__).resolve().parents[1]; AUDIT=ROOT/'audit'
EVID=AUDIT/'arabic_top3000_continuation_evidence_v2.csv'
WORD=re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
STOP={'a','an','the','to','of','and','or','for','as','be','is','are','was','were','with','by','from','that','which','who','this','it','he','she','they','you','i','we','one','ones','someone','something','having','used','use'}
MEAN=re.compile(r'(?m)^Meaning:\s*(.+?)\s*$'); POS=re.compile(r'(?m)^Part of speech:\s*(.+?)\s*$'); RANK=re.compile(r'(?m)^Rank:\s*(\d+)\s*$')

def stem(w):
    w=w.lower().strip("'-")
    if len(w)>5 and w.endswith('ies'): return w[:-3]+'y'
    for suf in ('ingly','ations','ation','ments','ment','ness','ities','ity','ing','ied','ed','es','s','al'):
        if len(w)>len(suf)+3 and w.endswith(suf):
            b=w[:-len(suf)]; return b+'y' if suf=='ied' else b
    return w

def toks(s): return {stem(w) for w in WORD.findall(s or '') if stem(w) not in STOP and len(stem(w))>1}
def agree(a,b):
    A,B=toks(a),toks(b)
    if A&B:return True
    for x in A:
        for y in B:
            if min(len(x),len(y))>=4 and (x.startswith(y) or y.startswith(x)):return True
    return False

def corpus(model,w):
    try: vals=model(w) or []
    except Exception: vals=[]
    return '; '.join(dict.fromkeys(str(x).replace('_',' ') for x in vals[:15]))

def extract(rx,s):
    m=rx.search(s or '');return re.sub(r'\s+',' ',m.group(1)).strip() if m else ''

def audit_cont(model):
    with EVID.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    q=[];counts=Counter();support=Counter()
    for r in rows:
        c=corpus(model,r['front']); current=r['meaning']; kaikki=r.get('kaikki_meaning','')
        cur=agree(current,c); alt=bool(c and kaikki and agree(kaikki,c))
        support['current_supported' if cur else 'current_unsupported']+=1
        risk='pass';reason=''
        if c and not cur and alt:
            risk='block';reason='modern_corpus_supports_kaikki_alternative_not_published_gloss'
        elif c and not cur:
            risk='review';reason='published_gloss_lacks_modern_corpus_support'
        pos=(r.get('pos') or '').lower()
        if pos=='noun' and re.search(r'\b(?:happy|common|united|electronic|financial|scientific|secondary|american|saudi|palestinian|white|human|natural|free)\b',current,re.I):
            if risk=='pass':risk='review';reason='noun_pos_with_adjectival_public_gloss'
        if risk!='pass':
            counts[f'{risk}:{reason}']+=1
            q.append({'rank':r['rank'],'front':r['front'],'meaning':current,'pos':r.get('pos',''),'risk':risk,'reason':reason,'corpus_signal':c,'kaikki_meaning':kaikki[:400],'calima_raw_meaning':r.get('calima_raw_meaning','')[:300]})
    q.sort(key=lambda x:(0 if x['risk']=='block' else 1,int(x['rank'])))
    return rows,q,counts,support

def audit_top1000(model):
    with (ROOT/'arabic_top1000.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    q=[];support=Counter()
    for i,r in enumerate(rows,1):
        back=r.get('Back','');meaning=extract(MEAN,back);pos=extract(POS,back);rank=extract(RANK,back) or str(i);c=corpus(model,r.get('Front',''))
        cur=agree(meaning,c);support['current_supported' if cur else 'current_unsupported']+=1
        if c and not cur:
            q.append({'rank':rank,'front':r.get('Front',''),'meaning':meaning,'pos':pos,'risk':'review','reason':'published_gloss_lacks_modern_corpus_support','corpus_signal':c})
    return rows,q,support

def reader_alignment():
    ns=runpy.run_path(str(ROOT/'reading/tools/audit_arabic_a1_flashcard_alignment.py'))
    return ns['audit']()

def main():
    model=Word2word('ar','en')
    cont,cq,counts,cs=audit_cont(model);top,tq,ts=audit_top1000(model)
    align=reader_alignment()
    summary={
      'arabic_top1000':{'rows':len(top),'review_rows':len(tq),'support_histogram':dict(ts)},
      'arabic_top3000':{'rows':len(cont),'block_rows':sum(x['risk']=='block' for x in cq),'review_rows':sum(x['risk']=='review' for x in cq),'support_histogram':dict(cs),'category_counts':dict(counts)},
      'arabic_a1_reader_alignment':align,
      'policy':'Corpus evidence is a sense-selector only, never a meaning author. Continuation rows are blocked only when current meaning lacks corpus support while an alternative already in Kaikki matches the corpus signal. Reader targets require live-card sense compatibility and individual second-pass verification or ranks-1-100 educator clearance.'
    }
    (AUDIT/'arabic_modern_sense_risk_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (AUDIT/'arabic_top3000_modern_sense_risk_queue.json').write_text(json.dumps(cq,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (AUDIT/'arabic_top1000_modern_sense_review.json').write_text(json.dumps(tq,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'arabic_top1000':summary['arabic_top1000'],'arabic_top3000':summary['arabic_top3000'],'arabic_a1_reader_alignment':{'passage_count':align['passage_count'],'problem_count':len(align['problems']),'gate':align['gate']}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
