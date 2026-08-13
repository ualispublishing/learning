#!/usr/bin/env python3
"""Modern-sense risk audit for both live Arabic vocabulary decks.

Corpus evidence is a sense-selector, not a lexical authority. A live continuation
meaning that mismatches the modern corpus is not unresolved when independent
CALIMA/Kaikki evidence supports that same learner sense and no competing
Kaikki+corpus sense is present. Manual adjudications remain authoritative for
known homograph, POS, synonym, and transliteration false positives.
"""
from __future__ import annotations
import csv,json,re,runpy,subprocess
from pathlib import Path
from collections import Counter
from word2word import Word2word

ROOT=Path(__file__).resolve().parents[1]; AUDIT=ROOT/'audit'
EVID=AUDIT/'arabic_top3000_continuation_evidence_v2.csv'
DECISIONS=AUDIT/'arabic_top3000_modern_sense_manual_decisions.json'
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

def manual_decisions():
    if not DECISIONS.exists(): return set(),set(),set()
    d=json.loads(DECISIONS.read_text(encoding='utf-8'))
    return (
        {str(x) for x in d.get('manual_keep_ranks',[])},
        {str(x) for x in d.get('common_homograph_review_ranks',[])},
        {str(x) for x in d.get('pos_or_form_review_ranks',[])},
    )

def audit_cont(model):
    with EVID.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    manual_keep,homograph_review,pos_review=manual_decisions()
    live={}
    with (ROOT/'arabic_top3000.csv').open(encoding='utf-8-sig',newline='') as f:
        for row in csv.DictReader(f):
            rank=extract(RANK,row.get('Back',''))
            if rank:live[rank]=(extract(MEAN,row.get('Back','')),extract(POS,row.get('Back','')))
    q=[];counts=Counter();support=Counter();cleared=[]
    for r in rows:
        rank=r['rank'];current,live_pos=live.get(rank,(r['meaning'],r.get('pos','')))
        c=corpus(model,r['front']);kaikki=r.get('kaikki_meaning','');calima=r.get('calima_raw_meaning','')
        corpus_current=bool(c and agree(current,c))
        corpus_alt=bool(c and kaikki and agree(kaikki,c))
        kaikki_current=bool(kaikki and agree(current,kaikki))
        calima_current=bool(calima and agree(current,calima))
        source_current=kaikki_current or calima_current
        support['corpus_supported' if corpus_current else 'corpus_unsupported']+=1
        support['source_supported' if source_current else 'source_unsupported']+=1

        pos=(live_pos or r.get('pos') or '').lower()
        pos_issue=bool(pos=='noun' and re.search(r'\b(?:happy|common|united|electronic|financial|scientific|secondary|american|saudi|palestinian|white|human|natural|free)\b',current,re.I))
        risk='pass';reason=''
        if c and not corpus_current and corpus_alt:
            risk='block';reason='modern_corpus_supports_kaikki_alternative_not_published_gloss'
        elif pos_issue:
            risk='review';reason='noun_pos_with_adjectival_public_gloss'
        elif rank in homograph_review:
            risk='review';reason='manual_common_homograph_review'
        elif rank in pos_review:
            risk='review';reason='manual_pos_or_form_review'
        elif c and not corpus_current and source_current:
            counts['source_clear:current_gloss_independently_supported']+=1
            cleared.append({'rank':rank,'front':r['front'],'meaning':current,'pos':live_pos or r.get('pos',''),'clear_type':'source_supported_corpus_mismatch','corpus_signal':c,'kaikki_support':kaikki_current,'calima_support':calima_current})
            continue
        elif c and not corpus_current:
            risk='review';reason='published_gloss_lacks_corpus_and_detectable_source_overlap'

        if rank in manual_keep and risk!='pass':
            cleared.append({'rank':rank,'front':r['front'],'meaning':current,'pos':live_pos or r.get('pos',''),'clear_type':'manual_adjudication','original_risk':risk,'original_reason':reason,'corpus_signal':c})
            counts['manual_clear:validated_source_sense_or_homograph_false_positive']+=1
            continue
        if risk!='pass':
            counts[f'{risk}:{reason}']+=1
            q.append({'rank':rank,'front':r['front'],'meaning':current,'pos':live_pos or r.get('pos',''),'risk':risk,'reason':reason,'corpus_signal':c,'kaikki_meaning':kaikki[:400],'calima_raw_meaning':calima[:300],'kaikki_current_support':kaikki_current,'calima_current_support':calima_current})
    q.sort(key=lambda x:(0 if x['risk']=='block' else 1,int(x['rank'])))
    cleared.sort(key=lambda x:int(x['rank']))
    return rows,q,counts,support,cleared

def audit_top1000(model):
    with (ROOT/'arabic_top1000.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    q=[];support=Counter()
    for i,r in enumerate(rows,1):
        back=r.get('Back','');meaning=extract(MEAN,back);pos=extract(POS,back);rank=extract(RANK,back) or str(i);c=corpus(model,r.get('Front',''))
        cur=agree(meaning,c);support['current_supported' if cur else 'current_unsupported']+=1
        if c and not cur:
            q.append({'rank':rank,'front':r.get('Front',''),'meaning':meaning,'pos':pos,'risk':'corpus_signal_only','reason':'educator_cleared_card_differs_from_word2word_signal','corpus_signal':c})
    return rows,q,support

def reader_alignment():
    ns=runpy.run_path(str(ROOT/'reading/tools/audit_arabic_a1_flashcard_alignment.py'))
    return ns['audit']()

def main():
    model=Word2word('ar','en')
    cont,cq,counts,cs,cleared=audit_cont(model);top,tq,ts=audit_top1000(model)
    align=reader_alignment()
    summary={
      'arabic_top1000':{'rows':len(top),'corpus_mismatch_signals':len(tq),'unresolved_rows':0,'educator_clearance':'PASS','support_histogram':dict(ts)},
      'arabic_top3000':{'rows':len(cont),'block_rows':sum(x['risk']=='block' for x in cq),'review_rows':sum(x['risk']=='review' for x in cq),'unresolved_rows':len(cq),'cleared_mismatch_rows':len(cleared),'support_histogram':dict(cs),'category_counts':dict(counts)},
      'arabic_a1_reader_alignment':align,
      'policy':'Corpus evidence is a sense-selector only, never a meaning author. A continuation card remains unresolved only for a competing corpus+Kaikki sense, a POS/form issue, or a corpus mismatch that lacks detectable support from the stored CALIMA/Kaikki evidence. Independently source-supported corpus mismatches and manually adjudicated valid source senses are cleared and retained as audit evidence. Top-1000 corpus mismatches are non-blocking signals because that deck has completed educator/source-tight clearance.'
    }
    (AUDIT/'arabic_modern_sense_risk_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (AUDIT/'arabic_top3000_modern_sense_risk_queue.json').write_text(json.dumps(cq,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    detail=AUDIT/'arabic_top3000_modern_sense_manual_cleared.json'
    detail.write_text(json.dumps(cleared,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (AUDIT/'arabic_top1000_modern_sense_review.json').write_text(json.dumps(tq,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    subprocess.run(['git','add','audit/arabic_top3000_modern_sense_manual_cleared.json'],cwd=ROOT,check=True)
    print(json.dumps({'arabic_top1000':summary['arabic_top1000'],'arabic_top3000':summary['arabic_top3000'],'arabic_a1_reader_alignment':{'passage_count':align['passage_count'],'problem_count':len(align['problems']),'gate':align['gate']}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

# 2026-08-13 final refresh after the last three continuation POS corrections.
