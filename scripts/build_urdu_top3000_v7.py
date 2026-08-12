#!/usr/bin/env python3
"""Complete the Urdu 1001..3000 continuation without weakening semantics.

Primary ordering uses the CLE Urdu top-5000 list and the tiered v6 semantic
policy. If that finite pool yields fewer than 2,000 safe continuation cards, the
remaining slots are filled from wordfreq's Urdu multi-corpus ranking, but ONLY
for single-token Urdu forms with CFILT IWN-En `Direct` Urdu↔English WordNet
mappings. No supplemental Tier-B or one-source meanings are permitted.

This keeps the semantic standard at its strongest for every supplemental row.
"""
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path
import pyiwn
from word2word import Word2word
from wordfreq import top_n_list, zipf_frequency
import build_french_urdu_core_candidates_v2 as fu
import build_urdu_top3000_v6 as b

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'audit'
TARGET=2000


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

    def direct_meaning(word,kg,rg,wg):
        senses=direct.get(word,[])
        if not senses: return None
        scored=[]
        for s in senses:
            ev=(s['english_words']+'; '+s['english_gloss']).strip('; ')
            score=int(bool(kg) and b.agree(ev,kg))+int(bool(rg) and b.agree(ev,rg))+int(bool(wg) and b.agree(ev,wg))
            scored.append((score,s))
        scored.sort(key=lambda x:(x[0],len(b.toks(x[1]['english_words']))),reverse=True)
        selector=scored[0][0] if scored else 0
        if len(senses)==1:
            selected=[senses[0]]; basis='IWN-En Direct manual link (single direct sense)'
        elif selector>0:
            selected=[s for score,s in scored if score==selector]
            basis=f'IWN-En Direct manual links; best valid sense set selected by {selector} independent bilingual signal(s)'
        else:
            selected=senses
            basis='IWN-En Direct manual links (all direct valid senses retained; no unsupported disambiguation)'
        vals=[]; ids=[]
        for s in selected:
            ids.append(s['english_id'])
            for m in b.english_lemmas(s['english_words']):
                if m.casefold() not in {v.casefold() for v in vals}: vals.append(m)
        meaning=b.safe_text('; '.join(vals[:16]),320)
        if not meaning or not b.toks(meaning): return None
        return meaning,ids,len(senses),len(selected),selector,basis

    def add(word,freq_value,freq_source,allow_tier_b):
        word=fu.norm_ur(word)
        if not word or word in excluded or word in seen: return False
        if not b.URDU.search(word) or b.DEV.search(word): return False
        if freq_source.startswith('wordfreq') and (re.search(r'\s',word) or len(word)>45): return False
        kg,rg,wg=semantic_sources(word)
        dm=direct_meaning(word,kg,rg,wg)
        if dm:
            meaning,ids,dcount,scount,selector,basis=dm
            tier='A_direct_iwn_en'
        elif allow_tier_b:
            if word not in iwn_words:
                rejected.append({'front':word,'frequency':freq_value,'frequency_source':freq_source,'reason':'no_direct_mapping_and_not_indowordnet_lemma'}); return False
            kr=bool(kg and rg and b.agree(kg,rg)); kw=bool(kg and wg and b.agree(kg,wg)); rw=bool(rg and wg and b.agree(rg,wg))
            if not (kr or kw or rw):
                rejected.append({'front':word,'frequency':freq_value,'frequency_source':freq_source,'reason':'fallback_no_two_source_semantic_agreement'}); return False
            if kr or kw:
                others=[]
                if kr: others.append(rg)
                if kw: others.append(wg)
                meaning=b.narrow(kg,*others) or b.safe_text(kg,300)
                src=[]
                if kr: src.append('ReadUrdu')
                if kw: src.append('word2word')
                basis='IndoWordNet Urdu lemma + Kaikki agreement with '+ '+'.join(src)
            else:
                meaning=b.narrow(rg,wg) or b.safe_text(rg,300)
                basis='IndoWordNet Urdu lemma + ReadUrdu/word2word agreement'
            meaning=b.safe_text(meaning,320)
            if not meaning or not b.toks(meaning): return False
            ids=[]; dcount=scount=0; selector=2; tier='B_two_source_fallback'
        else:
            return False
        seen.add(word)
        rows.append({'rank':1001+len(rows),'front':word,'meaning':meaning,
                     'frequency_evidence':freq_value,'frequency_source':freq_source,
                     'evidence_tier':tier,'iwn_en_english_ids':'|'.join(ids),
                     'iwn_en_direct_sense_count':dcount,'selected_direct_sense_count':scount,
                     'indowordnet_lemma':word in iwn_words,'kaikki_meaning':kg,
                     'readurdu_meaning':rg,'word2word_meaning':wg,
                     'external_selector_score':selector,'semantic_basis':basis})
        return True

    for word,freq in cle_ranked:
        add(word,str(freq),'CLE Urdu top-5000 frequency list',True)
        if len(rows)>=TARGET: break

    supplemental_examined=0
    if len(rows)<TARGET:
        # Official wordfreq Urdu list: multi-source corpus ranking. Only Tier A
        # Direct IWN-En semantic mappings are admitted in this supplemental pass.
        for word in top_n_list('ur',30000):
            if len(rows)>=TARGET: break
            supplemental_examined+=1
            nw=fu.norm_ur(word)
            if nw not in direct: continue
            z=zipf_frequency(nw,'ur')
            add(nw,f'Zipf {z:.2f}','wordfreq Urdu multi-corpus ranking (supplemental)',False)

    fields=list(rows[0]) if rows else ['rank','front','meaning']
    with (AUDIT/'urdu_top3000_continuation_evidence_v7.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    with (AUDIT/'urdu_top3000_candidate_v7.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Front','Back']);w.writeheader()
        for r in rows:
            back='\n'.join([f"Rank: {r['rank']}",'',f"Meaning: {r['meaning']}",'',f"Frequency evidence: {r['frequency_evidence']}",f"Frequency source: {r['frequency_source']}",'',f"Semantic verification: {r['semantic_basis']}",'','Sources:','- CLE Urdu 5,000 corpus frequency list — primary ordering authority','- CFILT IWN-En Direct Urdu↔English WordNet links — preferred manual semantic authority','- IndoWordNet Urdu — primary-pool fallback lexical gate','- Kaikki/Wiktextract, ReadUrdu, word2word — ambiguity selection / two-source primary-pool fallback','- wordfreq Urdu multi-corpus ranking — supplemental ordering only for final Direct-mapped rows','- Candidate only; requires hard final gate before promotion'])
            w.writerow({'Front':r['front'],'Back':back})
    rfields=sorted({k for r in rejected for k in r}) if rejected else ['front','frequency','reason']
    with (AUDIT/'urdu_top3000_rejections_v7.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rfields);w.writeheader();w.writerows(rejected)
    summary={'rows':len(rows),'expected_rows':TARGET,'distinct_fronts':len(seen),'rank_range':[1001,1000+len(rows)] if rows else [],'primary_CLE_rows':sum(r['frequency_source'].startswith('CLE') for r in rows),'supplemental_wordfreq_rows':sum(r['frequency_source'].startswith('wordfreq') for r in rows),'tier_A_direct_rows':sum(r['evidence_tier']=='A_direct_iwn_en' for r in rows),'tier_B_two_source_fallback_rows':sum(r['evidence_tier']=='B_two_source_fallback' for r in rows),'supplemental_non_direct_rows':sum(r['frequency_source'].startswith('wordfreq') and r['evidence_tier']!='A_direct_iwn_en' for r in rows),'supplemental_examined':supplemental_examined,'structural_gate':'PASS' if len(rows)==TARGET and len(seen)==TARGET else 'FAIL','status':'candidate_only_not_promoted','policy':'Use CLE ordering first. Fill only any remaining slots with wordfreq-ranked Urdu forms that have CFILT IWN-En Direct manual semantic mappings; supplemental rows can never use fallback semantics.'}
    (AUDIT/'urdu_top3000_candidate_v7_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if summary['structural_gate']!='PASS' or summary['supplemental_non_direct_rows']:
        raise SystemExit('Urdu v7 structural/evidence gate failed')

if __name__=='__main__': main()
