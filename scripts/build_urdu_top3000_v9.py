#!/usr/bin/env python3
"""Publication-grade Urdu continuation candidate using Unicode corpus frequency.

Ordering comes entirely from wordfreq's Urdu multi-corpus list, avoiding the legacy
CLE PDF text-extraction path. Every admitted meaning still requires agreement between
at least two independent bilingual resources (Kaikki, ReadUrdu, word2word).
"""
from __future__ import annotations
import argparse,csv,json,re,sys
from pathlib import Path
from word2word import Word2word
from wordfreq import top_n_list,zipf_frequency

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
import build_french_urdu_core_candidates_v2 as fu
AUDIT=ROOT/'audit'; TARGET=2000
WORD=re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?"); URDU=re.compile(r'[\u0600-\u06ff]'); DEV=re.compile(r'[\u0900-\u097f]')
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

def concise(primary,others):
    hits=[]
    for p in fragments(primary):
        if any(agree(p,o) for o in others if o):
            p=re.sub(r'\([^)]*\)','',p).strip(' ;,')
            p=re.sub(r'^(?:formal |oblique |indirect |vocative )?(?:plural|singular) of\s+','',p,flags=re.I)
            if p and len(p)<=85 and p.casefold() not in {h.casefold() for h in hits}: hits.append(p)
    out='; '.join(hits[:4])
    # Repair unmatched parenthesis / raw source fragments conservatively.
    out=out.replace(' | Platts:','').strip(' ;,')
    if out.count('(')!=out.count(')'):
        out=re.sub(r'\s*\([^)]*$','',out).strip(' ;,')
    return re.sub(r'\s+',' ',out)

def live_top1000():
    with (ROOT/'urdu_top1000.csv').open(encoding='utf-8-sig',newline='') as f:
        return {fu.norm_ur((r.get('Front') or '').strip()) for r in csv.DictReader(f)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--kaikki',required=True); ap.add_argument('--readurdu',required=True); a=ap.parse_args()
    kk=fu.load_kaikki(Path(a.kaikki),fu.norm_ur); read=fu.read_readurdu(Path(a.readurdu)); w2=Word2word('ur','en')
    excluded=live_top1000(); seen=set(); rows=[]; rejected=[]; examined=0
    def vals(word):
        ko=kk.get(word,{})
        kg=safe_text(fu.compact_meaning(ko.get('all_glosses',[])),350) if ko else ''
        rg=safe_read(read.get(word,{}).get('meaning','')) if word in read else ''
        try: wl=w2(word) or []
        except Exception: wl=[]
        wg=safe_text('; '.join(dict.fromkeys(str(x) for x in wl[:12])),350)
        return kg,rg,wg
    for raw in top_n_list('ur',100000):
        if len(rows)>=TARGET: break
        examined+=1; word=fu.norm_ur(raw)
        if not word or word in excluded or word in seen or re.search(r'\s',word) or not URDU.search(word) or DEV.search(word): continue
        kg,rg,wg=vals(word)
        kr=bool(kg and rg and agree(kg,rg)); kw=bool(kg and wg and agree(kg,wg)); rw=bool(rg and wg and agree(rg,wg))
        if not (kr or kw or rw):
            rejected.append({'front':word,'zipf':f'{zipf_frequency(word,"ur"):.2f}','reason':'no_two_source_semantic_agreement'}); continue
        if kr or kw:
            others=([rg] if kr else [])+([wg] if kw else [])
            meaning=concise(kg,others); support=['Kaikki']+(['ReadUrdu'] if kr else [])+(['word2word'] if kw else [])
        else:
            meaning=concise(rg,[wg]); support=['ReadUrdu','word2word']
        if not meaning or not toks(meaning):
            rejected.append({'front':word,'zipf':f'{zipf_frequency(word,"ur"):.2f}','reason':'agreement_without_clean_learner_fragment'}); continue
        # Exclude meanings that are only raw grammatical metadata rather than a learner gloss.
        if re.match(r'^(?:form|inflection|plural|singular|oblique|vocative)\b',meaning,re.I):
            rejected.append({'front':word,'zipf':f'{zipf_frequency(word,"ur"):.2f}','reason':'raw_grammatical_metadata_only'}); continue
        seen.add(word); rows.append({'rank':1001+len(rows),'front':word,'meaning':meaning,'wordfreq_zipf':f'{zipf_frequency(word,"ur"):.2f}','semantic_support':'+'.join(support),'kaikki_readurdu_agree':kr,'kaikki_word2word_agree':kw,'readurdu_word2word_agree':rw,'kaikki_meaning':kg,'readurdu_meaning':rg,'word2word_meaning':wg})
    fields=list(rows[0]) if rows else ['rank','front','meaning']
    with (AUDIT/'urdu_top3000_continuation_evidence_v9.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    with (AUDIT/'urdu_top3000_candidate_v9.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Front','Back']);w.writeheader()
        for r in rows:
            back='\n'.join([f"Rank: {r['rank']}",'',f"Meaning: {r['meaning']}",'',f"Frequency evidence: wordfreq Zipf {r['wordfreq_zipf']}",'Frequency source: wordfreq Urdu multi-corpus ranking','',f"Semantic verification: independent agreement — {r['semantic_support']}",'','Sources:','- wordfreq Urdu — Unicode multi-corpus frequency ordering','- Kaikki/Wiktextract — bilingual lexicographic evidence','- ReadUrdu — independent Urdu-English bilingual evidence','- word2word — independent corpus-derived bilingual evidence'])
            w.writerow({'Front':r['front'],'Back':back})
    with (AUDIT/'urdu_top3000_rejections_v9.csv').open('w',encoding='utf-8',newline='') as f:
        fs=['front','zipf','reason'];w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(rejected)
    summary={'rows':len(rows),'expected_rows':TARGET,'distinct_fronts':len(seen),'rank_range':[1001,1000+len(rows)] if rows else [],'wordfreq_candidates_examined':examined,'all_rows_two_source_supported':all(r['semantic_support'] for r in rows),'structural_gate':'PASS' if len(rows)==TARGET and len(seen)==TARGET else 'FAIL','status':'candidate_only_not_promoted','policy':'Unicode wordfreq ordering only; every learner meaning must be supported by at least two independent bilingual resources.'}
    (AUDIT/'urdu_top3000_candidate_v9_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if summary['structural_gate']!='PASS': raise SystemExit('fewer than 2,000 publication-grade Urdu cards')
if __name__=='__main__': main()
