#!/usr/bin/env python3
"""Build a 2,000-row precision Urdu continuation with a tiered evidence policy.

Frequency ordering comes from the CLE Urdu high-frequency list and the verified
Top-1000 is excluded.

Tier A (preferred): exact Urdu lemma has one or more CFILT IWN-En `Direct` links
to English WordNet. These are manually linked lexical senses. If several Direct
senses exist and supplemental sources cannot disambiguate them, all Direct
English lemma sets are retained rather than guessing or dropping a valid sense.

Tier B (fallback only when no Direct IWN-En mapping exists): the form must be an
exact IndoWordNet Urdu lemma AND its learner English meaning must be supported by
at least two independent bilingual sources among Kaikki/Wiktextract, ReadUrdu and
word2word. No one-source fallback is permitted.

Hypernymy and other non-Direct IWN-En link types are never used as translations.
"""
from __future__ import annotations
import argparse,csv,json,re
from collections import defaultdict
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
STOP={'a','an','the','to','of','and','or','for','as','be','is','are','was','were','with','by','from','that','which','who','this','it','he','she','they','you','i','we','one','ones','someone','something','having','used','use'}
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

def safe_text(t,limit=400):
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
    return x if x and len(x)<=220 and toks(x) else ''

def narrow(primary,*others):
    combined='; '.join(x for x in others if x)
    hits=[p for p in fragments(primary) if agree(p,combined)]
    if hits: return '; '.join(dict.fromkeys(hits[:6]))
    return clean(primary) if agree(primary,combined) else ''

def split_urdu_synset(s):
    return [fu.norm_ur(x.replace('_',' ').strip()) for x in re.split(r'[,،]',s or '') if x.strip()]

def english_lemmas(s):
    vals=[]
    for x in re.split(r'[,;]',s or ''):
        x=clean(x)
        if x and len(x)<=80 and x.casefold() not in {v.casefold() for v in vals}: vals.append(x)
    return vals

def load_iwn_en(path):
    by_word=defaultdict(list)
    with Path(path).open(encoding='utf-8-sig',errors='replace',newline='') as f:
        r=csv.DictReader(f,delimiter='\t')
        required={'english_id','english_synset_words','english_gloss','urdu_synset','type_link'}
        missing=required-set(r.fieldnames or [])
        if missing: raise SystemExit(f'IWN-En missing columns: {sorted(missing)}')
        for row in r:
            if (row.get('type_link') or '').strip().casefold()!='direct': continue
            eng=english_lemmas(row.get('english_synset_words',''))
            if not eng: continue
            item={'english_id':(row.get('english_id') or '').strip(),
                  'english_words':'; '.join(eng[:10]),
                  'english_gloss':safe_text(row.get('english_gloss',''),600)}
            for lemma in split_urdu_synset(row.get('urdu_synset','')):
                key=(item['english_id'],item['english_words'])
                if lemma and all((x['english_id'],x['english_words'])!=key for x in by_word[lemma]):
                    by_word[lemma].append(dict(item))
    return by_word

def live_fronts():
    with (ROOT/'urdu_top1000.csv').open(encoding='utf-8-sig',newline='') as f:
        return {fu.norm_ur((r.get('Front') or '').strip()) for r in csv.DictReader(f)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--iwn-en',required=True); ap.add_argument('--kaikki',required=True)
    ap.add_argument('--urdu-freq-text',required=True); ap.add_argument('--readurdu',required=True)
    a=ap.parse_args()

    excluded=live_fronts()
    ranked=fu.extract_urdu_freq(Path(a.urdu_freq_text).read_text(encoding='utf-8',errors='replace'))
    direct=load_iwn_en(a.iwn_en)
    kk=fu.load_kaikki(Path(a.kaikki),fu.norm_ur); read=fu.read_readurdu(Path(a.readurdu))
    w2=Word2word('ur','en')
    iwn=pyiwn.IndoWordNet(lang=pyiwn.Language.URDU)
    iwn_words={fu.norm_ur(str(w).strip()) for w in iwn.all_words() if str(w).strip()}

    rows=[]; rejected=[]; seen=set()
    for raw_word,freq in ranked:
        word=fu.norm_ur(raw_word)
        if not word or word in excluded or word in seen: continue
        if not URDU.search(word) or DEV.search(word):
            rejected.append({'front':word,'frequency':freq,'reason':'non_urdu_script'}); continue

        kobj=kk.get(word,{})
        kg=safe_text(fu.compact_meaning(kobj.get('all_glosses',[])),350) if kobj else ''
        rg=safe_read(read.get(word,{}).get('meaning','')) if word in read else ''
        try: wlist=w2(word) or []
        except Exception: wlist=[]
        wg=safe_text('; '.join(dict.fromkeys(str(x) for x in wlist[:12])),350)

        senses=direct.get(word,[])
        tier=''; basis=''; meaning=''; english_ids=[]; selector_score=0; selected_count=0
        if senses:
            scored=[]
            for s in senses:
                ev=(s['english_words']+'; '+s['english_gloss']).strip('; ')
                score=int(bool(kg) and agree(ev,kg))+int(bool(rg) and agree(ev,rg))+int(bool(wg) and agree(ev,wg))
                scored.append((score,s))
            scored.sort(key=lambda x:(x[0],len(toks(x[1]['english_words']))),reverse=True)
            selector_score=scored[0][0] if scored else 0
            if len(senses)==1:
                selected=[senses[0]]; basis='IWN-En Direct manual link (single direct sense)'
            elif selector_score>0:
                selected=[s for score,s in scored if score==selector_score]
                basis=f'IWN-En Direct manual links; best valid sense set selected by {selector_score} independent bilingual signal(s)'
            else:
                # Every retained sense remains a Direct lexicographer-linked
                # English WordNet mapping; showing the union is safer than
                # guessing which valid sense was intended.
                selected=senses
                basis='IWN-En Direct manual links (all direct valid senses retained; no unsupported disambiguation)'
            vals=[]
            for s in selected:
                english_ids.append(s['english_id'])
                for m in english_lemmas(s['english_words']):
                    if m.casefold() not in {v.casefold() for v in vals}: vals.append(m)
            meaning='; '.join(vals[:16]); selected_count=len(selected); tier='A_direct_iwn_en'
        else:
            if word not in iwn_words:
                rejected.append({'front':word,'frequency':freq,'reason':'no_direct_mapping_and_not_indowordnet_lemma'}); continue
            kr=bool(kg and rg and agree(kg,rg)); kw=bool(kg and wg and agree(kg,wg)); rw=bool(rg and wg and agree(rg,wg))
            if not (kr or kw or rw):
                rejected.append({'front':word,'frequency':freq,'reason':'fallback_no_two_source_semantic_agreement','kaikki':kg,'readurdu':rg,'word2word':wg}); continue
            if kr or kw:
                others=[]
                if kr: others.append(rg)
                if kw: others.append(wg)
                meaning=narrow(kg,*others) or safe_text(kg,300)
                src=[]
                if kr: src.append('ReadUrdu')
                if kw: src.append('word2word')
                basis='IndoWordNet Urdu lemma + Kaikki agreement with '+ '+'.join(src)
            else:
                meaning=narrow(rg,wg) or safe_text(rg,300)
                basis='IndoWordNet Urdu lemma + ReadUrdu/word2word agreement'
            tier='B_two_source_fallback'; selector_score=2; selected_count=0

        meaning=safe_text(meaning,320)
        if not meaning or not toks(meaning):
            rejected.append({'front':word,'frequency':freq,'reason':'unsafe_or_blank_learner_meaning'}); continue
        seen.add(word)
        rows.append({'rank':1001+len(rows),'front':word,'meaning':meaning,'frequency':freq,
                     'evidence_tier':tier,'iwn_en_english_ids':'|'.join(english_ids),
                     'iwn_en_direct_sense_count':len(senses),'selected_direct_sense_count':selected_count,
                     'indowordnet_lemma':word in iwn_words,'kaikki_meaning':kg,'readurdu_meaning':rg,
                     'word2word_meaning':wg,'external_selector_score':selector_score,'semantic_basis':basis})
        if len(rows)>=TARGET: break

    fields=list(rows[0]) if rows else ['rank','front','meaning']
    with (AUDIT/'urdu_top3000_continuation_evidence_v6.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    with (AUDIT/'urdu_top3000_candidate_v6.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Front','Back']); w.writeheader()
        for r in rows:
            back='\n'.join([f"Rank: {r['rank']}",'',f"Meaning: {r['meaning']}",'',f"Frequency evidence: {r['frequency']}",'',f"Semantic verification: {r['semantic_basis']}",'','Sources:','- CLE Urdu 5,000 corpus frequency list — ordering authority','- CFILT IWN-En Direct Urdu↔English WordNet links — preferred manual semantic authority','- IndoWordNet Urdu — fallback lexical gate','- Kaikki/Wiktextract, ReadUrdu, word2word — ambiguity selection / two-source fallback evidence','- Candidate only; requires hard final gate before promotion'])
            w.writerow({'Front':r['front'],'Back':back})
    rfields=sorted({k for r in rejected for k in r}) if rejected else ['front','frequency','reason']
    with (AUDIT/'urdu_top3000_rejections_v6.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rfields); w.writeheader(); w.writerows(rejected)
    reasons={x:sum(r.get('reason')==x for r in rejected) for x in sorted({r.get('reason') for r in rejected})}
    summary={'rows':len(rows),'expected_rows':TARGET,'distinct_fronts':len(seen),'rank_range':[1001,1000+len(rows)] if rows else [],'direct_iwn_en_lemma_count':len(direct),'indowordnet_urdu_lexicon_size':len(iwn_words),'tier_A_direct_rows':sum(r['evidence_tier']=='A_direct_iwn_en' for r in rows),'tier_B_two_source_fallback_rows':sum(r['evidence_tier']=='B_two_source_fallback' for r in rows),'multi_direct_rows_retaining_all_valid_senses':sum(r['evidence_tier']=='A_direct_iwn_en' and int(r['iwn_en_direct_sense_count'])>1 and int(r['external_selector_score'])==0 for r in rows),'rejected_before_target':len(rejected),'rejection_reason_counts':reasons,'structural_gate':'PASS' if len(rows)==TARGET and len(seen)==TARGET else 'FAIL','status':'candidate_only_not_promoted','policy':'Prefer lexicographer-linked IWN-En Direct mappings. If multiple Direct senses cannot be disambiguated, retain all Direct valid senses. Only when no Direct link exists, require IndoWordNet lemma membership plus agreement between two independent bilingual sources.'}
    (AUDIT/'urdu_top3000_candidate_v6_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if summary['structural_gate']!='PASS': raise SystemExit('fewer than 2,000 high-confidence Urdu continuation rows available')

if __name__=='__main__': main()
