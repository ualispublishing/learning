#!/usr/bin/env python3
"""Build a quality-first Urdu rank-1001..3000 continuation using IndoWordNet.

CLE's 5,000-word corpus list supplies frequency ordering only. The verified live
Top-1000 is excluded. A candidate must be a lemma in IndoWordNet's Urdu WordNet
and must have a safe English learner meaning corroborated by at least two
independent bilingual signals among Kaikki/Wiktextract, ReadUrdu and word2word.
One-source entries, visibly archaic dictionary prose, mixed Devanagari glosses,
and unsupported corpus surface forms are skipped rather than padded into the deck.
"""
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path
import pyiwn
from word2word import Word2word
import build_french_urdu_core_candidates_v2 as fu

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'audit'
TARGET=2000
WORD=re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
DEV=re.compile(r"[\u0900-\u097f]")
URDU=re.compile(r"[\u0600-\u06ff]")
SPLIT=re.compile(r"\s*(?:;|/|\||,(?!\s*(?:which|who|that|when|where)))\s*")
STOP={'a','an','the','to','of','and','or','for','as','be','is','are','was','were','with','by','from','that','which','who','this','it','he','she','they','you','i','we','one','ones','someone','something'}
BAD_READ=('q.v.','see gram',' gram.','s.m.','s.f.','adj.','adv.','pers.','aor.','contrac.','dialec.','prob. akin','hind.')

def clean(t):
    return ' '.join((t or '').replace('_',' ').split()).strip(' ;,.')

def toks(t):
    out=set()
    for w in WORD.findall(t or ''):
        w=w.lower().strip("'-")
        if w in STOP or len(w)<2: continue
        if len(w)>4 and w.endswith('ies'): w=w[:-3]+'y'
        else:
            for suf in ('ingly','ation','ments','ment','ing','ied','ed','es','s'):
                if len(w)>len(suf)+3 and w.endswith(suf):
                    w=w[:-len(suf)]; break
        if w not in STOP: out.add(w)
    return out

def agree(a,b):
    return bool(toks(a)&toks(b))

def fragments(t):
    return [clean(x) for x in SPLIT.split(t or '') if clean(x)]

def safe_read(t):
    x=clean(t)
    if not x or len(x)>180 or DEV.search(x): return ''
    low=x.lower()
    if any(p in low for p in BAD_READ): return ''
    if ' | also:' in x: x=x.split(' | also:',1)[0].strip()
    return x if x and len(x)<=180 else ''

def safe_text(t):
    x=clean(t)
    if not x or len(x)>220 or DEV.search(x) or any(c in x for c in '[]<>'): return ''
    return x

def narrow(primary,*others):
    combined='; '.join(x for x in others if x)
    hits=[p for p in fragments(primary) if agree(p,combined)]
    if hits: return '; '.join(dict.fromkeys(hits[:5]))
    return clean(primary) if agree(primary,combined) else ''

def live_fronts():
    with (ROOT/'urdu_top1000.csv').open(encoding='utf-8-sig',newline='') as f:
        return {fu.norm_ur((r.get('Front') or '').strip()) for r in csv.DictReader(f)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--kaikki',required=True)
    ap.add_argument('--urdu-freq-text',required=True)
    ap.add_argument('--readurdu',required=True)
    a=ap.parse_args()

    excluded=live_fronts()
    ranked=fu.extract_urdu_freq(Path(a.urdu_freq_text).read_text(encoding='utf-8',errors='replace'))
    read=fu.read_readurdu(Path(a.readurdu))
    kk=fu.load_kaikki(Path(a.kaikki),fu.norm_ur)
    w2=Word2word('ur','en')

    iwn=pyiwn.IndoWordNet(lang=pyiwn.Language.URDU)
    iwn_words={fu.norm_ur(str(w).strip()) for w in iwn.all_words() if str(w).strip()}

    rows=[]; rejected=[]; seen=set()
    for raw_word,freq in ranked:
        word=fu.norm_ur(raw_word)
        if not word or word in excluded or word in seen: continue
        if not URDU.search(word) or DEV.search(word):
            rejected.append({'front':word,'frequency':freq,'reason':'non_urdu_script'}); continue
        if word not in iwn_words:
            rejected.append({'front':word,'frequency':freq,'reason':'not_indowordnet_urdu_lemma'}); continue

        kobj=kk.get(word,{})
        kg=safe_text(fu.compact_meaning(kobj.get('all_glosses',[]))) if kobj else ''
        rg=safe_read(read.get(word,{}).get('meaning','')) if word in read else ''
        try: wlist=w2(word) or []
        except Exception: wlist=[]
        wg=safe_text('; '.join(dict.fromkeys(str(x) for x in wlist[:12])))

        kr=bool(kg and rg and agree(kg,rg))
        kw=bool(kg and wg and agree(kg,wg))
        rw=bool(rg and wg and agree(rg,wg))
        source_count=sum(bool(x) for x in (kr,kw,rw))
        if source_count==0:
            rejected.append({'front':word,'frequency':freq,'reason':'no_two_source_semantic_agreement','kaikki':kg,'readurdu':rg,'word2word':wg}); continue

        # Prefer Kaikki as learner-facing wording when it participates, but retain
        # only fragments corroborated by the other agreeing source(s).
        if kr or kw:
            others=[]
            if kr: others.append(rg)
            if kw: others.append(wg)
            meaning=narrow(kg,*others) or safe_text(kg)
            if kr and kw: basis='kaikki+readurdu+word2word'
            elif kr: basis='kaikki+readurdu'
            else: basis='kaikki+word2word'
        else:
            meaning=narrow(rg,wg) or safe_text(rg)
            basis='readurdu+word2word'

        meaning=safe_text(meaning)
        if not meaning or not toks(meaning):
            rejected.append({'front':word,'frequency':freq,'reason':'no_safe_corroborated_learner_meaning'}); continue

        seen.add(word)
        rows.append({
            'rank':1001+len(rows),'front':word,'meaning':meaning,'frequency':freq,
            'indowordnet_lemma':True,'kaikki_meaning':kg,'readurdu_meaning':rg,
            'word2word_meaning':wg,'kaikki_readurdu_agreement':kr,
            'kaikki_word2word_agreement':kw,'readurdu_word2word_agreement':rw,
            'semantic_basis':basis,
        })
        if len(rows)>=TARGET: break

    fields=list(rows[0]) if rows else ['rank','front','meaning']
    with (AUDIT/'urdu_top3000_continuation_evidence_v4.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    with (AUDIT/'urdu_top3000_candidate_v4.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Front','Back']); w.writeheader()
        for r in rows:
            back='\n'.join([
                f"Rank: {r['rank']}",'',f"Meaning: {r['meaning']}",'',
                f"Frequency evidence: {r['frequency']}",'',
                f"Semantic verification: {r['semantic_basis']}",'','Sources:',
                '- CLE Urdu 5,000 corpus frequency list — ordering authority',
                '- IndoWordNet Urdu — lexical lemma gate',
                '- Kaikki/Wiktextract, ReadUrdu, word2word — independent bilingual semantic signals',
                '- Candidate only; requires final audit before promotion',
            ])
            w.writerow({'Front':r['front'],'Back':back})

    rfields=sorted({k for r in rejected for k in r}) if rejected else ['front','frequency','reason']
    with (AUDIT/'urdu_top3000_rejections_v4.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rfields); w.writeheader(); w.writerows(rejected)
    bases=sorted({r['semantic_basis'] for r in rows})
    summary={
        'rows':len(rows),'expected_rows':TARGET,'distinct_fronts':len(seen),
        'rank_range':[1001,1000+len(rows)] if rows else [],
        'indowordnet_urdu_lexicon_size':len(iwn_words),
        'rejected_before_target':len(rejected),
        'semantic_basis_counts':{b:sum(r['semantic_basis']==b for r in rows) for b in bases},
        'structural_gate':'PASS' if len(rows)==TARGET and len(seen)==TARGET else 'FAIL',
        'status':'candidate_only_not_promoted',
        'policy':'Require IndoWordNet Urdu lemma membership plus agreement between at least two independent bilingual semantic signals; never pad with one-source or archaic/mixed-script glosses.',
    }
    (AUDIT/'urdu_top3000_candidate_v4_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if summary['structural_gate']!='PASS':
        raise SystemExit('fewer than 2,000 IndoWordNet + two-source verified Urdu continuation rows available in CLE top-5000')

if __name__=='__main__': main()
