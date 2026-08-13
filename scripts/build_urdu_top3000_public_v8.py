#!/usr/bin/env python3
"""Build a publication-quality Urdu 1001..3000 continuation.

Stricter than v7:
- every CFILT IWN-En Direct mapping must be independently corroborated by at
  least one of Kaikki, ReadUrdu, or word2word;
- ambiguous Direct mappings are admitted only when one synset has a unique
  best corroboration score (ties are rejected rather than merged);
- learner meanings are narrowed to at most three concise lemmas from that
  selected synset;
- no-Direct fallback still requires IndoWordNet lemma membership plus agreement
  between two independent bilingual sources;
- wordfreq supplementation may use only independently-corroborated Direct rows.
"""
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path
import pyiwn
from word2word import Word2word
from wordfreq import top_n_list,zipf_frequency
import build_french_urdu_core_candidates_v2 as fu
import build_urdu_top3000_v6 as b

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'audit'
TARGET=2000

def clean_lemma(x:str)->str:
    x=b.clean(x)
    x=re.sub(r'\s*\((?:a|p|prenominal|postpositive)\)\s*$','',x,flags=re.I)
    x=x.replace('world-wide','worldwide')
    return x.strip()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--iwn-en',required=True); ap.add_argument('--kaikki',required=True)
    ap.add_argument('--urdu-freq-text',required=True); ap.add_argument('--readurdu',required=True)
    a=ap.parse_args()

    excluded=b.live_fronts()
    cle_ranked=fu.extract_urdu_freq(Path(a.urdu_freq_text).read_text(encoding='utf-8',errors='replace'))
    direct=b.load_iwn_en(a.iwn_en)
    kk=fu.load_kaikki(Path(a.kaikki),fu.norm_ur)
    read=fu.read_readurdu(Path(a.readurdu))
    w2=Word2word('ur','en')
    iwn=pyiwn.IndoWordNet(lang=pyiwn.Language.URDU)
    iwn_words={fu.norm_ur(str(w).strip()) for w in iwn.all_words() if str(w).strip()}

    rows=[]; rejected=[]; seen=set()

    def semantic_sources(word):
        kobj=kk.get(word,{})
        kg=b.safe_text(fu.compact_meaning(kobj.get('all_glosses',[])),350) if kobj else ''
        rg=b.safe_read(read.get(word,{}).get('meaning','')) if word in read else ''
        try: wlist=w2(word) or []
        except Exception: wlist=[]
        wg=b.safe_text('; '.join(dict.fromkeys(str(x) for x in wlist[:12])),350)
        return kg,rg,wg

    def choose_direct(word,kg,rg,wg):
        senses=direct.get(word,[])
        if not senses: return None,'no_direct_mapping'
        scored=[]
        for s in senses:
            ev=(s['english_words']+'; '+s['english_gloss']).strip('; ')
            score=int(bool(kg) and b.agree(ev,kg))+int(bool(rg) and b.agree(ev,rg))+int(bool(wg) and b.agree(ev,wg))
            scored.append((score,s))
        best=max((x[0] for x in scored),default=0)
        if best<=0: return None,'direct_mapping_without_independent_corroboration'
        winners=[s for score,s in scored if score==best]
        if len(winners)!=1: return None,'ambiguous_direct_mapping_tied_after_corroboration'
        s=winners[0]
        combined='; '.join(x for x in (kg,rg,wg) if x)
        lemmas=[clean_lemma(x) for x in b.english_lemmas(s['english_words'])]
        lemmas=[x for x in lemmas if x]
        corroborated=[x for x in lemmas if b.agree(x,combined)]
        chosen=corroborated or lemmas
        vals=[]
        for x in chosen:
            if x.casefold() not in {v.casefold() for v in vals}: vals.append(x)
            if len(vals)>=3: break
        meaning=b.safe_text('; '.join(vals),180)
        if not meaning or not b.toks(meaning): return None,'unsafe_direct_learner_gloss'
        return {
            'meaning':meaning,'english_ids':[s['english_id']],
            'direct_count':len(senses),'selector_score':best,
            'basis':f'CFILT IWN-En Direct sense uniquely selected and corroborated by {best} independent bilingual source(s)',
            'tier':'A_direct_corroborated'
        },''

    def choose_fallback(word,kg,rg,wg):
        if word not in iwn_words: return None,'not_indowordnet_lemma'
        kr=bool(kg and rg and b.agree(kg,rg)); kw=bool(kg and wg and b.agree(kg,wg)); rw=bool(rg and wg and b.agree(rg,wg))
        if not (kr or kw or rw): return None,'fallback_no_two_source_agreement'
        if kr or kw:
            others=[]
            if kr: others.append(rg)
            if kw: others.append(wg)
            meaning=b.narrow(kg,*others)
            src=[]
            if kr: src.append('ReadUrdu')
            if kw: src.append('word2word')
            basis='IndoWordNet lemma + Kaikki agreement with '+ '+'.join(src)
        else:
            meaning=b.narrow(rg,wg)
            basis='IndoWordNet lemma + ReadUrdu/word2word agreement'
        parts=b.fragments(meaning)[:3]
        meaning=b.safe_text('; '.join(parts),180)
        if not meaning or not b.toks(meaning): return None,'unsafe_fallback_learner_gloss'
        return {'meaning':meaning,'english_ids':[],'direct_count':0,'selector_score':2,'basis':basis,'tier':'B_two_source_fallback'},''

    def add(word,freq_value,freq_source,allow_fallback):
        word=fu.norm_ur(word)
        if not word or word in excluded or word in seen: return False
        if not b.URDU.search(word) or b.DEV.search(word) or re.search(r'\s',word): return False
        kg,rg,wg=semantic_sources(word)
        obj,reason=choose_direct(word,kg,rg,wg)
        if obj is None and allow_fallback and reason=='no_direct_mapping':
            obj,reason=choose_fallback(word,kg,rg,wg)
        if obj is None:
            rejected.append({'front':word,'frequency_evidence':freq_value,'frequency_source':freq_source,'reason':reason,'kaikki':kg,'readurdu':rg,'word2word':wg})
            return False
        if freq_source.startswith('wordfreq') and obj['tier']!='A_direct_corroborated': return False
        seen.add(word)
        rows.append({'rank':1001+len(rows),'front':word,'meaning':obj['meaning'],
                     'frequency_evidence':freq_value,'frequency_source':freq_source,
                     'evidence_tier':obj['tier'],'iwn_en_english_ids':'|'.join(obj['english_ids']),
                     'iwn_en_direct_sense_count':obj['direct_count'],'external_selector_score':obj['selector_score'],
                     'kaikki_meaning':kg,'readurdu_meaning':rg,'word2word_meaning':wg,
                     'semantic_basis':obj['basis']})
        return True

    for word,freq in cle_ranked:
        add(word,str(freq),'CLE Urdu top-5000 frequency list',True)
        if len(rows)>=TARGET: break

    supplemental_examined=0
    if len(rows)<TARGET:
        for word in top_n_list('ur',100000):
            if len(rows)>=TARGET: break
            supplemental_examined+=1
            nw=fu.norm_ur(word)
            if nw not in direct: continue
            z=zipf_frequency(nw,'ur')
            add(nw,f'Zipf {z:.2f}','wordfreq Urdu multi-corpus ranking (supplemental)',False)

    fields=list(rows[0]) if rows else ['rank','front','meaning']
    with (AUDIT/'urdu_top3000_public_evidence_v8.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    with (AUDIT/'urdu_top3000_public_candidate_v8.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Front','Back']);w.writeheader()
        for r in rows:
            back='\n'.join([f"Rank: {r['rank']}",'',f"Meaning: {r['meaning']}",'',
                f"Frequency evidence: {r['frequency_evidence']}",f"Frequency source: {r['frequency_source']}",'',
                f"Semantic verification: {r['semantic_basis']}",'','Sources:',
                '- CLE Urdu 5,000 corpus frequency list — primary ordering authority',
                '- CFILT IWN-En Direct Urdu↔English WordNet links — semantic candidate authority',
                '- Kaikki/Wiktextract, ReadUrdu, word2word — mandatory independent corroboration / disambiguation',
                '- IndoWordNet Urdu — lexical gate for two-source fallback only',
                '- wordfreq Urdu multi-corpus ranking — supplemental ordering only'])
            w.writerow({'Front':r['front'],'Back':back})
    rfields=sorted({k for r in rejected for k in r}) if rejected else ['front','reason']
    with (AUDIT/'urdu_top3000_public_rejections_v8.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rfields);w.writeheader();w.writerows(rejected)
    summary={'rows':len(rows),'expected_rows':TARGET,'distinct_fronts':len(seen),
             'rank_range':[1001,1000+len(rows)] if rows else [],
             'primary_CLE_rows':sum(r['frequency_source'].startswith('CLE') for r in rows),
             'supplemental_wordfreq_rows':sum(r['frequency_source'].startswith('wordfreq') for r in rows),
             'tier_A_direct_corroborated_rows':sum(r['evidence_tier']=='A_direct_corroborated' for r in rows),
             'tier_B_two_source_fallback_rows':sum(r['evidence_tier']=='B_two_source_fallback' for r in rows),
             'max_meaning_semicolon_parts':max([len(b.fragments(r['meaning'])) for r in rows] or [0]),
             'supplemental_examined':supplemental_examined,
             'structural_gate':'PASS' if len(rows)==TARGET and len(seen)==TARGET else 'FAIL',
             'policy':'Every Direct mapping must be independently corroborated; ambiguous Direct mappings require a unique winner; public glosses are capped at three concise lemmas; fallback requires IndoWordNet membership plus two-source agreement.'}
    (AUDIT/'urdu_top3000_public_candidate_v8_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if summary['structural_gate']!='PASS': raise SystemExit('fewer than 2,000 publication-quality Urdu continuation rows found')

if __name__=='__main__': main()
