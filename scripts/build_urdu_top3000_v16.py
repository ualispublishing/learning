#!/usr/bin/env python3
"""Final-quality Urdu continuation from targeted independent OPUS evidence.

Each public meaning is an existing Kaikki/ReadUrdu dictionary sense that independently
recurs in aligned non-subtitle OPUS English translations with minimum count/rate/lift.
The OPUS corpus never authors a meaning. Ordering is Unicode Urdu wordfreq; unsupported
higher-frequency forms are skipped. One concise core sense is exposed per card.
"""
from __future__ import annotations
import csv,json,re,math
from pathlib import Path
from wordfreq import top_n_list,zipf_frequency

ROOT=Path(__file__).resolve().parents[1];AUDIT=ROOT/'audit';TARGET=2000
EVID=AUDIT/'opus_targeted_urdu_evidence.json'
AR=re.compile(r'[\u0600-\u06ff]');ENWORD=re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
RAW=re.compile(r'\b(?:Platts|s\.m\.|s\.f\.|interj\.|infinitive of|inflection of|form of|plural of|singular of|masculine of|feminine of|only used in|q\.v\.)\b',re.I)
OVERRIDES={'اردو':'Urdu language','محمد':'Muhammad','عمران':'Imran'}

def norm_ur(s):
    s=(s or '').replace('ي','ی').replace('ى','ی').replace('ك','ک').replace('ۀ','ہ').replace('ة','ہ')
    s=re.sub(r'[\u064b-\u065f\u0670\u06d6-\u06edـ]','',s)
    return re.sub(r'\s+',' ',s).strip()

def top1000():
    with (ROOT/'urdu_top1000.csv').open(encoding='utf-8-sig',newline='') as f:
        return {norm_ur((r.get('Front') or '').strip()) for r in csv.DictReader(f)}

def sense_strength(s):
    ds=s.get('details') or []
    if not ds:return -1
    min_count=min(int(d.get('cooccurrence_sentences',0)) for d in ds)
    min_lift=min(float(d.get('lift',0)) for d in ds)
    min_rate=min(float(d.get('observed_rate',0)) for d in ds)
    # Repeated co-occurrence dominates. Lift/rate break ties but are capped so a
    # one-off exotic association cannot outrank a repeatedly observed core sense.
    return 4*math.log1p(min_count)+0.35*min(min_lift,20)+2*min(min_rate,0.5)-0.01*len(s.get('gloss',''))

def clean_gloss(g):
    g=re.sub(r'\([^)]*\)',' ',g or '')
    g=re.sub(r'\s+',' ',g).strip(' ;,."')
    if not g or RAW.search(g) or AR.search(g) or len(g)>48:return ''
    if len(ENWORD.findall(g))>4:return ''
    return g

def choose(word,record):
    senses=[]
    for s in record.get('accepted_dictionary_senses') or []:
        g=clean_gloss(s.get('gloss',''))
        if not g:continue
        senses.append((sense_strength(s),g,s))
    if not senses:return None
    senses.sort(key=lambda x:x[0],reverse=True)
    score,g,s=senses[0]
    if word in OVERRIDES:
        # Override only presentation, never evidence. It must semantically contain
        # the same named entity already supported by the selected dictionary sense.
        ov=OVERRIDES[word]
        if any(x.lower() in g.lower() or g.lower() in x.lower() for x in ov.split()):g=ov
    return {'meaning':g,'dictionary_source':s.get('source',''),'opus_strength':round(score,3),'details':s.get('details',[])}

def regression(rows):
    d={r['front']:r['meaning'].lower() for r in rows};problems=[]
    def must(w,rx):
        if w in d and not re.search(rx,d[w],re.I):problems.append(f'{w}={d[w]!r} expected /{rx}/')
    def forbid(w,rx):
        if w in d and re.search(rx,d[w],re.I):problems.append(f'{w}={d[w]!r} forbidden /{rx}/')
    must('کرتا',r'\bdo(?:es|ne)?\b');must('پولیس',r'police');must('مطابق',r'accord|according|conform|consistent');must('اعلان',r'announc|declar|proclamation');must('کورٹ',r'\bcourt\b')
    must('پیج',r'\bpage\b');forbid('پیج',r'agreement|promise');must('گن',r'\bgun\b');forbid('گن',r'quality|virtue');forbid('والی',r'governor');must('سرخ',r'\bred\b');must('کرن',r'\bray\b')
    return problems

def main():
    data=json.loads(EVID.read_text(encoding='utf-8'));ev={norm_ur(k):v for k,v in (data.get('evidence') or {}).items()}
    excluded=top1000();seen=set();rows=[];rejected=[];examined=0
    for raw in top_n_list('ur',100000):
        if len(rows)>=TARGET:break
        examined+=1;word=norm_ur(raw)
        if not word or ' ' in word or not AR.search(word) or word in excluded or word in seen:continue
        rec=ev.get(word)
        if not rec:
            rejected.append({'front':word,'zipf':f'{zipf_frequency(raw,"ur"):.2f}','reason':'no_independent_opus_dictionary_sense_support'});continue
        ch=choose(word,rec)
        if not ch:
            rejected.append({'front':word,'zipf':f'{zipf_frequency(raw,"ur"):.2f}','reason':'supported_but_no_clean_public_core_gloss'});continue
        seen.add(word);rows.append({'rank':1001+len(rows),'front':word,'meaning':ch['meaning'],'wordfreq_zipf':f'{zipf_frequency(raw,"ur"):.2f}','dictionary_source':ch['dictionary_source'],'opus_strength':ch['opus_strength'],'opus_details':json.dumps(ch['details'],ensure_ascii=False,separators=(',',':'))})
    regress=regression(rows)
    bad=[r for r in rows if RAW.search(r['meaning']) or AR.search(r['meaning']) or len(r['meaning'])>48 or len(ENWORD.findall(r['meaning']))>4]
    fields=list(rows[0]) if rows else ['rank','front','meaning']
    with (AUDIT/'urdu_top3000_continuation_evidence_v16.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    with (AUDIT/'urdu_top3000_candidate_v16.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Front','Back']);w.writeheader()
        for r in rows:
            back='\n'.join([f"Rank: {r['rank']}",'',f"Meaning: {r['meaning']}",'',f"Frequency evidence: wordfreq Zipf {r['wordfreq_zipf']}",'Frequency source: wordfreq Urdu multi-corpus ranking','',f"Semantic verification: {r['dictionary_source']} dictionary sense independently corroborated in non-subtitle OPUS aligned sentences",f"OPUS evidence strength: {r['opus_strength']}",'','Sources:','- wordfreq Urdu — Unicode multi-corpus ordering','- Kaikki/Wiktextract or ReadUrdu — dictionary-origin learner meaning','- Independent OPUS Urdu-English aligned corpora — modern sentence-level corroboration only'])
            w.writerow({'Front':r['front'],'Back':back})
    with (AUDIT/'urdu_top3000_rejections_v16.csv').open('w',encoding='utf-8',newline='') as f:
        fs=['front','zipf','reason'];w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(rejected)
    # Stratified sample is committed for manual inspection before promotion.
    sample=[]
    for start in (0,480,980,1480,max(0,len(rows)-40)):
        for r in rows[start:min(start+40,len(rows))]:sample.append({k:r[k] for k in ('rank','front','meaning','dictionary_source','opus_strength')})
    unique=[];seenr=set()
    for x in sample:
        if x['rank'] not in seenr:seenr.add(x['rank']);unique.append(x)
    risk_words=['کرتا','پولیس','مطابق','اعلان','کورٹ','پیج','گن','والی','سرخ','کرن','امریکہ','لشکر','تجدید','جاسوسی','فوائد','پیدل']
    lookup={r['front']:r for r in rows};risk=[{'front':w,'present':w in lookup,'rank':lookup[w]['rank'] if w in lookup else None,'meaning':lookup[w]['meaning'] if w in lookup else None} for w in risk_words]
    (AUDIT/'urdu_top3000_v16_stratified_sample.json').write_text(json.dumps({'sample':unique,'known_risk_words':risk},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    summary={'rows':len(rows),'expected_rows':TARGET,'distinct_fronts':len(seen),'rank_range':[1001,1000+len(rows)] if rows else [],'wordfreq_candidates_examined':examined,'independent_opus_supported_universe':len(ev),'public_gloss_violations':len(bad),'regression_problems':regress,'structural_gate':'PASS' if len(rows)==TARGET and len(seen)==TARGET and not bad and not regress else 'FAIL','status':'candidate_only_not_promoted','policy':'One concise dictionary-origin core sense per card; every row independently corroborated by repeated sentence-level evidence in non-subtitle OPUS corpora; unsupported higher-frequency forms are skipped.'}
    (AUDIT/'urdu_top3000_candidate_v16_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,indent=2))
    if summary['structural_gate']!='PASS':raise SystemExit('v16 gate failed')
if __name__=='__main__':main()
