#!/usr/bin/env python3
"""Dual-corpus modern-corroborated Urdu continuation candidate.

Public glosses originate only in Kaikki/ReadUrdu dictionary senses. A normal learner
sense must be corroborated by at least one of two independent modern parallel-corpus
lexicons: (1) word2word's OpenSubtitles2018 Urdu-English lexicon and (2) our custom
non-subtitle OPUS lexicon built from Anuvaad/GlobalVoices/QED/TED/Tatoeba/etc.
The corpus lexicons can corroborate but never author a public gloss, except explicit
surface-form inflections documented by ReadUrdu.
"""
from __future__ import annotations
import argparse,csv,json,re,sys
from pathlib import Path
from word2word import Word2word
from wordfreq import top_n_list,zipf_frequency
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import build_french_urdu_core_candidates_v2 as fu
import build_urdu_top3000_v14 as base
AUDIT=ROOT/'audit';TARGET=2000
LEX=AUDIT/'opus_independent_urdu_lexicon.json'
URDU=re.compile(r'[\u0600-\u06ff]');DEV=re.compile(r'[\u0900-\u097f]');WORD=re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
SAFE_NAMED={'اردو','قرآن'}

def clean(s):return base.clean(s)
def related(a,b):return base.related(a,b)
def atoms(s):return base.atoms(s)
def engfreq(s):return base.engfreq(s)
def proper_like(s):return base.proper_like(s)

def candidate_senses(kg,rg,osg,opg):
    src={'Kaikki':atoms(kg),'ReadUrdu':atoms(rg),'OpenSubtitles':atoms(osg),'OPUS-independent':atoms(opg)}
    out=[]
    for origin in ('Kaikki','ReadUrdu'):
        for i,v in enumerate(src[origin]):
            supporters=[];positions=[]
            for other in ('Kaikki','ReadUrdu','OpenSubtitles','OPUS-independent'):
                if other==origin:continue
                mm=[j for j,o in enumerate(src[other]) if related(v,o)]
                if mm:supporters.append(other);positions.append(min(mm))
            modern=sum(x in supporters for x in ('OpenSubtitles','OPUS-independent'))
            if not supporters:continue
            # Modern corpus agreement dominates source ordering; agreement by both
            # corpora is deliberately rewarded strongly.
            score=8*modern+3*('Kaikki' in supporters or 'ReadUrdu' in supporters)+engfreq(v)-.18*(i+sum(positions))-.01*len(v)
            out.append((score,v,sorted(set([origin]+supporters)),modern))
    out.sort(reverse=True,key=lambda x:x[0]);ded=[]
    for item in out:
        if any(related(item[1],x[1]) for x in ded):continue
        ded.append(item)
    return ded

def inflected(rg,osg,opg):
    if not base.INFLECT.search(rg):return '',[]
    ra=atoms(rg)
    for label,text in [('OpenSubtitles',osg),('OPUS-independent',opg)]:
        for x in atoms(text)[:8]:
            if len(WORD.findall(x))<=2 and any(related(x,r) for r in ra):
                return x,['ReadUrdu',label]
    return '',[]

def make_gloss(word,kg,rg,osg,opg):
    iv,sup=inflected(rg,osg,opg)
    if iv:return clean(iv),sup
    c=candidate_senses(kg,rg,osg,opg)
    if not c:return '',[]
    # Normal words require at least one modern-corpus witness. Two-dictionary-only
    # consensus is kept only for unmistakable named terms.
    usable=[x for x in c if x[3]>=1]
    if not usable:
        usable=[x for x in c if word in SAFE_NAMED or proper_like(x[1])]
    if not usable:return '',[]
    _,v,support,_=usable[0]
    if len(v)>45 or base.RAW.search(v) or URDU.search(v) or len(WORD.findall(v))>3:return '',[]
    if word in base.PUBLIC_OVERRIDES:
        ov=base.PUBLIC_OVERRIDES[word]
        if any(related(ov,x) for x in atoms(kg)+atoms(rg)+atoms(osg)+atoms(opg)):v=ov
    if v.isupper():v=v.lower()
    return clean(v),support

def top1000():
    with (ROOT/'urdu_top1000.csv').open(encoding='utf-8-sig',newline='') as f:
        return {fu.norm_ur((r.get('Front') or '').strip()) for r in csv.DictReader(f)}

def regression(rows):
    d={r['front']:r['meaning'].lower() for r in rows};problems=[]
    def must(word,rx):
        if word in d and not re.search(rx,d[word],re.I):problems.append(f'{word}={d[word]!r} expected /{rx}/')
    def forbid(word,rx):
        if word in d and re.search(rx,d[word],re.I):problems.append(f'{word}={d[word]!r} forbidden /{rx}/')
    must('کرتا',r'\bdo(?:es|ne)?\b');must('پولیس',r'police');must('مطابق',r'accord|according|conform|consistent');must('اعلان',r'announc|declar|proclamation');must('کورٹ',r'\bcourt\b')
    must('پیج',r'\bpage\b');forbid('پیج',r'agreement|promise');must('گن',r'\bgun\b');forbid('گن',r'quality|virtue');forbid('والی',r'governor');must('سرخ',r'\bred\b');must('کرن',r'\bray\b')
    return problems

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--kaikki',required=True);ap.add_argument('--readurdu',required=True);a=ap.parse_args()
    if not LEX.exists():raise SystemExit('independent OPUS lexicon not built yet')
    lj=json.loads(LEX.read_text(encoding='utf-8'));ind=lj.get('translations',{})
    kk=fu.load_kaikki(Path(a.kaikki),fu.norm_ur);read=fu.read_readurdu(Path(a.readurdu));osw=Word2word('ur','en')
    excluded=top1000();seen=set();rows=[];rej=[];examined=0
    for raw in top_n_list('ur',300000):
        if len(rows)>=TARGET:break
        examined+=1;word=fu.norm_ur(raw)
        if not word or word in excluded or word in seen or re.search(r'\s',word) or not URDU.search(word) or DEV.search(word):continue
        kg,rg,osg=base.source_texts(word,kk,read,osw);opg='; '.join(ind.get(word,[])[:15])
        gloss,support=make_gloss(word,kg,rg,osg,opg)
        if not gloss or len(set(support))<2:
            rej.append({'front':word,'zipf':f'{zipf_frequency(word,"ur"):.2f}','reason':'no_clean_dual_corpus_corroborated_dictionary_sense'});continue
        seen.add(word);rows.append({'rank':1001+len(rows),'front':word,'meaning':gloss,'wordfreq_zipf':f'{zipf_frequency(word,"ur"):.2f}','semantic_support':'+'.join(support),'kaikki_meaning':kg,'readurdu_meaning':rg,'opensubtitles_word2word':osg,'opus_independent_word2word':opg})
    fields=list(rows[0]) if rows else ['rank','front','meaning']
    with (AUDIT/'urdu_top3000_continuation_evidence_v15.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    with (AUDIT/'urdu_top3000_candidate_v15.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Front','Back']);w.writeheader()
        for r in rows:
            back='\n'.join([f"Rank: {r['rank']}",'',f"Meaning: {r['meaning']}",'',f"Frequency evidence: wordfreq Zipf {r['wordfreq_zipf']}",'Frequency source: wordfreq Urdu multi-corpus ranking','',f"Semantic verification: dictionary-origin core sense corroborated — {r['semantic_support']}",'','Sources:','- wordfreq Urdu — Unicode multi-corpus frequency ordering','- Kaikki/Wiktextract — bilingual lexicographic evidence','- ReadUrdu — independent Urdu-English bilingual evidence','- word2word OpenSubtitles2018 — modern corpus corroboration','- independent OPUS Urdu-English lexicon — non-subtitle corpus corroboration'])
            w.writerow({'Front':r['front'],'Back':back})
    with (AUDIT/'urdu_top3000_rejections_v15.csv').open('w',encoding='utf-8',newline='') as f:fs=['front','zipf','reason'];w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(rej)
    regress=regression(rows);bad=[r for r in rows if len(r['meaning'])>45 or base.RAW.search(r['meaning']) or URDU.search(r['meaning']) or len(WORD.findall(r['meaning']))>3]
    summary={'rows':len(rows),'expected_rows':TARGET,'distinct_fronts':len(seen),'rank_range':[1001,1000+len(rows)] if rows else [],'wordfreq_candidates_examined':examined,'public_gloss_violations':len(bad),'regression_problems':regress,'rows_with_opensubtitles_support':sum('OpenSubtitles' in r['semantic_support'] for r in rows),'rows_with_independent_opus_support':sum('OPUS-independent' in r['semantic_support'] for r in rows),'rows_supported_by_both_corpora':sum('OpenSubtitles' in r['semantic_support'] and 'OPUS-independent' in r['semantic_support'] for r in rows),'structural_gate':'PASS' if len(rows)==TARGET and len(seen)==TARGET and not bad and not regress else 'FAIL','status':'candidate_only_not_promoted','policy':'One dictionary-origin core sense; ordinary meanings need at least one modern corpus corroborator; independent non-subtitle OPUS and OpenSubtitles signals are tracked separately; known homograph regressions are hard failures.'}
    (AUDIT/'urdu_top3000_candidate_v15_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,indent=2))
    if summary['structural_gate']!='PASS':raise SystemExit('v15 gate failed')
if __name__=='__main__':main()
