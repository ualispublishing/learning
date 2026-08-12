#!/usr/bin/env python3
"""Build a precision Urdu rank-1001..3000 continuation from IWN-En links.

Ranking comes from the CLE Urdu high-frequency list. Candidate forms must occur as
exact Urdu lemmas in CFILT's IWN-En Urdu mapping and only rows whose `type_link`
is Direct are eligible. IWN-En is manually linked by lexicographers to English
WordNet. For an Urdu lemma with one direct English synset, that mapping is used.
For lemmas with multiple direct English synsets, Kaikki/Wiktextract, ReadUrdu and
word2word are used only to select among the valid manually-linked senses; ambiguous
lemmas with no independent selection signal are skipped.
"""
from __future__ import annotations
import argparse,csv,json,re
from collections import defaultdict
from pathlib import Path
from word2word import Word2word
import build_french_urdu_core_candidates_v2 as fu

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'audit'
TARGET=2000
WORD=re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
DEV=re.compile(r"[\u0900-\u097f]")
URDU=re.compile(r"[\u0600-\u06ff]")
STOP={'a','an','the','to','of','and','or','for','as','be','is','are','was','were','with','by','from','that','which','who','this','it','he','she','they','you','i','we','one','ones','someone','something','having','used'}
META=('q.v.','see gram',' gram.','s.m.','s.f.','adj.','adv.','pers.','aor.','contrac.','dialec.','prob. akin')

def clean(t):
    return ' '.join((t or '').replace('_',' ').split()).strip(' ;,."')

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

def agree(a,b):
    return bool(toks(a)&toks(b))

def safe_text(t,limit=400):
    x=clean(t)
    if not x or len(x)>limit or DEV.search(x) or any(c in x for c in '[]<>'): return ''
    return x

def safe_read(t):
    x=clean(t)
    if not x: return ''
    # Preserve the English dictionary segment and discard any appended Devanagari.
    m=DEV.search(x)
    if m: x=x[:m.start()].strip(' ;,|')
    if ' | also:' in x: x=x.split(' | also:',1)[0].strip()
    low=x.lower()
    for marker in META:
        pos=low.find(marker)
        if pos>0: x=x[:pos].strip(' ;,|'); low=x.lower()
    return x if x and len(x)<=220 and toks(x) else ''

def split_urdu_synset(s):
    return [fu.norm_ur(x.replace('_',' ').strip()) for x in re.split(r'[,،]',s or '') if x.strip()]

def english_lemmas(s):
    vals=[]
    for x in re.split(r'[,;]',s or ''):
        x=clean(x)
        if x and x not in vals and len(x)<=80: vals.append(x)
    return vals

def load_iwn_en(path:Path):
    by_word=defaultdict(list)
    with path.open(encoding='utf-8-sig',errors='replace',newline='') as f:
        r=csv.DictReader(f,delimiter='\t')
        required={'english_id','english_synset_words','english_gloss','urdu_synset','type_link'}
        missing=required-set(r.fieldnames or [])
        if missing: raise SystemExit(f'IWN-En missing columns: {sorted(missing)}')
        for row in r:
            if (row.get('type_link') or '').strip().casefold()!='direct': continue
            lemmas=split_urdu_synset(row.get('urdu_synset',''))
            eng=english_lemmas(row.get('english_synset_words',''))
            if not lemmas or not eng: continue
            item={
                'english_id':(row.get('english_id') or '').strip(),
                'category':(row.get('english_category') or '').strip(),
                'english_words':'; '.join(eng[:8]),
                'english_gloss':safe_text(row.get('english_gloss',''),600),
            }
            for lemma in lemmas:
                if not lemma: continue
                key=(item['english_id'],item['english_words'])
                if all((x['english_id'],x['english_words'])!=key for x in by_word[lemma]):
                    by_word[lemma].append(dict(item))
    return by_word

def live_fronts():
    with (ROOT/'urdu_top1000.csv').open(encoding='utf-8-sig',newline='') as f:
        return {fu.norm_ur((r.get('Front') or '').strip()) for r in csv.DictReader(f)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--iwn-en',required=True)
    ap.add_argument('--kaikki',required=True)
    ap.add_argument('--urdu-freq-text',required=True)
    ap.add_argument('--readurdu',required=True)
    a=ap.parse_args()

    excluded=live_fronts()
    ranked=fu.extract_urdu_freq(Path(a.urdu_freq_text).read_text(encoding='utf-8',errors='replace'))
    iwn=load_iwn_en(Path(a.iwn_en))
    kk=fu.load_kaikki(Path(a.kaikki),fu.norm_ur)
    read=fu.read_readurdu(Path(a.readurdu))
    w2=Word2word('ur','en')

    rows=[]; rejected=[]; seen=set()
    for raw_word,freq in ranked:
        word=fu.norm_ur(raw_word)
        if not word or word in excluded or word in seen: continue
        if not URDU.search(word) or DEV.search(word):
            rejected.append({'front':word,'frequency':freq,'reason':'non_urdu_script'}); continue
        senses=iwn.get(word,[])
        if not senses:
            rejected.append({'front':word,'frequency':freq,'reason':'no_direct_iwn_en_mapping'}); continue

        kobj=kk.get(word,{})
        kg=safe_text(fu.compact_meaning(kobj.get('all_glosses',[])),350) if kobj else ''
        rg=safe_read(read.get(word,{}).get('meaning','')) if word in read else ''
        try: wlist=w2(word) or []
        except Exception: wlist=[]
        wg=safe_text('; '.join(dict.fromkeys(str(x) for x in wlist[:12])),350)
        external='; '.join(x for x in (kg,rg,wg) if x)

        scored=[]
        for s in senses:
            evidence=(s['english_words']+'; '+s['english_gloss']).strip('; ')
            score=int(bool(kg) and agree(evidence,kg))+int(bool(rg) and agree(evidence,rg))+int(bool(wg) and agree(evidence,wg))
            scored.append((score,s))
        scored.sort(key=lambda x:(x[0],len(toks(x[1]['english_words']))),reverse=True)

        if len(scored)==1:
            selected=[scored[0][1]]
            basis='IWN-En Direct manual link (unambiguous direct mapping)'
        else:
            best=scored[0][0]
            if best<=0:
                rejected.append({'front':word,'frequency':freq,'reason':'ambiguous_direct_iwn_en_without_external_selector','direct_senses':' | '.join(s['english_words'] for _,s in scored[:8]),'kaikki':kg,'readurdu':rg,'word2word':wg}); continue
            selected=[]
            for score,s in scored:
                if score==best and score>0:
                    selected.append(s)
            # If several tied senses survive, keeping all of them is safer than
            # inventing a distinction that the external evidence cannot make.
            basis=f'IWN-En Direct manual links; ambiguous sense set externally selected ({best} corroborating signal(s))'

        meanings=[]
        english_ids=[]
        for s in selected:
            english_ids.append(s['english_id'])
            for m in english_lemmas(s['english_words']):
                if m and m.casefold() not in {x.casefold() for x in meanings}: meanings.append(m)
        meaning='; '.join(meanings[:12])
        if not meaning or len(meaning)>300 or not toks(meaning):
            rejected.append({'front':word,'frequency':freq,'reason':'unsafe_iwn_en_learner_meaning'}); continue

        seen.add(word)
        rows.append({
            'rank':1001+len(rows),'front':word,'meaning':meaning,'frequency':freq,
            'iwn_en_english_ids':'|'.join(english_ids),'iwn_en_direct_sense_count':len(senses),
            'selected_direct_sense_count':len(selected),'kaikki_meaning':kg,
            'readurdu_meaning':rg,'word2word_meaning':wg,
            'external_selector_max_score':scored[0][0] if scored else 0,
            'semantic_basis':basis,
        })
        if len(rows)>=TARGET: break

    fields=list(rows[0]) if rows else ['rank','front','meaning']
    with (AUDIT/'urdu_top3000_continuation_evidence_v5.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    with (AUDIT/'urdu_top3000_candidate_v5.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Front','Back']); w.writeheader()
        for r in rows:
            back='\n'.join([
                f"Rank: {r['rank']}",'',f"Meaning: {r['meaning']}",'',
                f"Frequency evidence: {r['frequency']}",'',
                f"Semantic verification: {r['semantic_basis']}",'','Sources:',
                '- CLE Urdu 5,000 corpus frequency list — ordering authority',
                '- CFILT IWN-En Urdu ↔ English WordNet Direct links — manually linked semantic authority',
                '- Kaikki/Wiktextract, ReadUrdu, word2word — ambiguity-selection / supplemental checks',
                '- Candidate only; requires final audit before promotion',
            ])
            w.writerow({'Front':r['front'],'Back':back})

    rfields=sorted({k for r in rejected for k in r}) if rejected else ['front','frequency','reason']
    with (AUDIT/'urdu_top3000_rejections_v5.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rfields); w.writeheader(); w.writerows(rejected)
    reasons={x:sum(r.get('reason')==x for r in rejected) for x in sorted({r.get('reason') for r in rejected})}
    summary={
        'rows':len(rows),'expected_rows':TARGET,'distinct_fronts':len(seen),
        'rank_range':[1001,1000+len(rows)] if rows else [],
        'iwn_en_direct_urdu_lemma_count':len(iwn),
        'rejected_before_target':len(rejected),'rejection_reason_counts':reasons,
        'unambiguous_direct_rows':sum('unambiguous' in r['semantic_basis'] for r in rows),
        'externally_selected_ambiguous_rows':sum('externally selected' in r['semantic_basis'] for r in rows),
        'rows_with_any_external_selector_support':sum(int(r['external_selector_max_score'])>0 for r in rows),
        'structural_gate':'PASS' if len(rows)==TARGET and len(seen)==TARGET else 'FAIL',
        'status':'candidate_only_not_promoted',
        'policy':'Require exact Urdu lemma in CFILT IWN-En Direct manual links. Unambiguous direct mappings are accepted; multi-sense direct mappings require an independent bilingual signal to select the valid learner sense set.',
    }
    (AUDIT/'urdu_top3000_candidate_v5_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if summary['structural_gate']!='PASS':
        raise SystemExit('fewer than 2,000 quality-gated IWN-En Direct Urdu continuation rows available in CLE top-5000')

if __name__=='__main__': main()
