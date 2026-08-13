#!/usr/bin/env python3
"""Build a publication-oriented Urdu 1001..3000 candidate.

Unlike v7, lexical provenance alone is never enough. A learner meaning is admitted
only when at least two independent bilingual resources among Kaikki/Wiktextract,
ReadUrdu, and word2word agree on a semantic fragment. Frequency ordering uses the
CLE list first, then wordfreq Urdu only to fill gaps with equally corroborated items.
"""
from __future__ import annotations
import argparse,csv,json,re,sys
from pathlib import Path
from word2word import Word2word
from wordfreq import top_n_list,zipf_frequency

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_french_urdu_core_candidates_v2 as fu

AUDIT=ROOT/'audit'; TARGET=2000
WORD=re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
URDU=re.compile(r'[\u0600-\u06ff]'); DEV=re.compile(r'[\u0900-\u097f]')
STOP={'a','an','the','to','of','and','or','for','as','be','is','are','was','were','with','by','from','that','which','who','this','it','he','she','they','you','i','we','one','ones','someone','something','having','used','use'}
SPLIT=re.compile(r'\s*(?:;|/|\||,(?!\s*(?:which|who|that|when|where)))\s*')
META=('q.v.','see gram',' gram.','s.m.','s.f.','adj.','adv.','pers.','aor.','contrac.','dialec.','prob. akin')

def clean(t): return ' '.join((t or '').replace('_',' ').split()).strip(' ;,."')
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

def agree(a,b): return bool(toks(a)&toks(b))
def fragments(t): return [clean(x) for x in SPLIT.split(t or '') if clean(x)]
def safe_text(t,limit=360):
    x=clean(t)
    if not x or len(x)>limit or DEV.search(x) or any(c in x for c in '[]<>'): return ''
    return x

def safe_read(t):
    x=clean(t)
    if not x: return ''
    m=DEV.search(x)
    if m: x=x[:m.start()].strip(' ;,|')
    if ' | also:' in x: x=x.split(' | also:',1)[0].strip()
    low=x.lower()
    for marker in META:
        pos=low.find(marker)
        if pos>0: x=x[:pos].strip(' ;,|'); low=x.lower()
    return x if x and len(x)<=240 and toks(x) else ''

def narrow(primary,*others):
    combined='; '.join(x for x in others if x)
    hits=[]
    for p in fragments(primary):
        if agree(p,combined):
            # remove raw dictionary prose and keep concise translation-like fragments
            p=re.sub(r'\([^)]{80,}\)','',p).strip()
            if p and len(p)<=90 and p.casefold() not in {h.casefold() for h in hits}: hits.append(p)
    return '; '.join(hits[:4])

def live_top1000():
    with (ROOT/'urdu_top1000.csv').open(encoding='utf-8-sig',newline='') as f:
        return {fu.norm_ur((r.get('Front') or '').strip()) for r in csv.DictReader(f)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--kaikki',required=True); ap.add_argument('--urdu-freq-text',required=True); ap.add_argument('--readurdu',required=True); a=ap.parse_args()
    kk=fu.load_kaikki(Path(a.kaikki),fu.norm_ur); read=fu.read_readurdu(Path(a.readurdu)); w2=Word2word('ur','en')
    excluded=live_top1000(); seen=set(); rows=[]; rejected=[]

    def source_vals(word):
        kobj=kk.get(word,{})
        kg=safe_text(fu.compact_meaning(kobj.get('all_glosses',[])),350) if kobj else ''
        rg=safe_read(read.get(word,{}).get('meaning','')) if word in read else ''
        try: wl=w2(word) or []
        except Exception: wl=[]
        wg=safe_text('; '.join(dict.fromkeys(str(x) for x in wl[:12])),350)
        return kg,rg,wg

    def choose(kg,rg,wg):
        kr=bool(kg and rg and agree(kg,rg)); kw=bool(kg and wg and agree(kg,wg)); rw=bool(rg and wg and agree(rg,wg))
        if not (kr or kw or rw): return None
        # Prefer dictionary-quality Kaikki when corroborated; otherwise ReadUrdu.
        if kr or kw:
            others=[]; support=['Kaikki']
            if kr: others.append(rg); support.append('ReadUrdu')
            if kw: others.append(wg); support.append('word2word')
            meaning=narrow(kg,*others)
            if not meaning:
                # If whole-source agreement exists but fragment split missed it, select the shortest matching fragment.
                candidates=[p for p in fragments(kg) if any(agree(p,o) for o in others)]
                meaning='; '.join(candidates[:3])
        else:
            support=['ReadUrdu','word2word']; meaning=narrow(rg,wg)
        meaning=clean(meaning)
        if not meaning or not toks(meaning): return None
        # Public gloss hygiene.
        meaning=re.sub(r'\b(?:plural|singular|oblique|vocative|formal plural) of\b.*$','',meaning,flags=re.I).strip(' ;,') or meaning
        meaning=re.sub(r'\s+',' ',meaning)
        if len(meaning)>180: meaning='; '.join(fragments(meaning)[:3])
        return meaning,'+'.join(support),kr,kw,rw

    def add(raw,freq,src):
        word=fu.norm_ur(raw)
        if not word or word in excluded or word in seen or not URDU.search(word) or DEV.search(word) or re.search(r'\s',word): return False
        kg,rg,wg=source_vals(word); ch=choose(kg,rg,wg)
        if not ch:
            rejected.append({'front':word,'frequency':freq,'frequency_source':src,'reason':'no_two_source_semantic_agreement'}); return False
        meaning,support,kr,kw,rw=ch
        seen.add(word); rows.append({'rank':1001+len(rows),'front':word,'meaning':meaning,'frequency_evidence':freq,'frequency_source':src,'semantic_support':support,'kaikki_readurdu_agree':kr,'kaikki_word2word_agree':kw,'readurdu_word2word_agree':rw,'kaikki_meaning':kg,'readurdu_meaning':rg,'word2word_meaning':wg})
        return True

    ranked=fu.extract_urdu_freq(Path(a.urdu_freq_text).read_text(encoding='utf-8',errors='replace'))
    for word,freq in ranked:
        add(word,str(freq),'CLE Urdu top-5000 frequency list')
        if len(rows)>=TARGET: break
    cle_rows=len(rows); examined=0
    if len(rows)<TARGET:
        for word in top_n_list('ur',60000):
            if len(rows)>=TARGET: break
            examined+=1
            add(word,f'Zipf {zipf_frequency(word,"ur"):.2f}','wordfreq Urdu multi-corpus ranking (supplemental)')

    fields=list(rows[0]) if rows else ['rank','front','meaning']
    with (AUDIT/'urdu_top3000_continuation_evidence_v8.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    with (AUDIT/'urdu_top3000_candidate_v8.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Front','Back']); w.writeheader()
        for r in rows:
            back='\n'.join([f"Rank: {r['rank']}",'',f"Meaning: {r['meaning']}",'',f"Frequency evidence: {r['frequency_evidence']}",f"Frequency source: {r['frequency_source']}",'',f"Semantic verification: independent agreement — {r['semantic_support']}",'','Sources:','- CLE Urdu corpus frequency list — primary ordering','- Kaikki/Wiktextract — bilingual lexicographic evidence','- ReadUrdu — independent Urdu-English bilingual evidence','- word2word — independent corpus-derived bilingual evidence','- wordfreq Urdu — supplemental frequency ordering only'])
            w.writerow({'Front':r['front'],'Back':back})
    with (AUDIT/'urdu_top3000_rejections_v8.csv').open('w',encoding='utf-8',newline='') as f:
        fs=['front','frequency','frequency_source','reason']; w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(rejected)
    summary={'rows':len(rows),'expected_rows':TARGET,'distinct_fronts':len(seen),'rank_range':[1001,1000+len(rows)] if rows else [],'primary_CLE_rows':cle_rows,'supplemental_wordfreq_rows':len(rows)-cle_rows,'supplemental_examined':examined,'all_rows_two_source_supported':all(r['semantic_support'] for r in rows),'structural_gate':'PASS' if len(rows)==TARGET and len(seen)==TARGET else 'FAIL','status':'candidate_only_not_promoted','policy':'Every row requires agreement between at least two independent bilingual sources; lexical provenance alone is insufficient.'}
    (AUDIT/'urdu_top3000_candidate_v8_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if summary['structural_gate']!='PASS': raise SystemExit('fewer than 2,000 two-source Urdu cards available')

if __name__=='__main__': main()
