#!/usr/bin/env python3
"""Build an Urdu->English word2word lexicon from independent non-subtitle OPUS corpora.

This is intentionally separate from word2word's bundled Urdu-English model, which was
built from OpenSubtitles2018. The selected OPUS corpora below exclude OpenSubtitles
and OPUS-100. The resulting lexicon is used only as corroborating evidence: public
learner glosses must still originate in a dictionary source.
"""
from __future__ import annotations
import csv,json,re,requests,zipfile,io,os
from pathlib import Path
from word2word import Word2word

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'audit'; WORK=Path('/tmp/urdu-opus-independent'); WORK.mkdir(parents=True,exist_ok=True)
PREFIX=WORK/'independent.ur-en'
# High-value sources with clearly different domains from movie subtitles.
CORPORA={
 'Anuvaad':'https://object.pouta.csc.fi/OPUS-Anuvaad/v1/moses/en-ur.txt.zip',
 'GlobalVoices':'https://object.pouta.csc.fi/OPUS-GlobalVoices/v2018q4/moses/en-ur.txt.zip',
 'QED':'https://object.pouta.csc.fi/OPUS-QED/v2.0a/moses/en-ur.txt.zip',
 'TED2020':'https://object.pouta.csc.fi/OPUS-TED2020/v1/moses/en-ur.txt.zip',
 'Tatoeba':'https://object.pouta.csc.fi/OPUS-Tatoeba/v2026-07-08/moses/en-ur.txt.zip',
 'pmindia':'https://object.pouta.csc.fi/OPUS-pmindia/v1b/moses/en-ur.txt.zip',
 'tico-19':'https://object.pouta.csc.fi/OPUS-tico-19/v2020-10-28/moses/en-ur.txt.zip',
 'translatewiki':'https://object.pouta.csc.fi/OPUS-translatewiki/v2026-07-01/moses/en-ur.txt.zip',
 'GNOME':'https://object.pouta.csc.fi/OPUS-GNOME/v1/moses/en-ur.txt.zip',
 'NeuLab-TedTalks':'https://object.pouta.csc.fi/OPUS-NeuLab-TedTalks/v1/moses/en-ur.txt.zip',
}
AR=re.compile(r'[\u0600-\u06ff]')

def pick_pair(z:zipfile.ZipFile):
    names=z.namelist()
    en=[n for n in names if n.lower().endswith('.en')]
    ur=[n for n in names if n.lower().endswith('.ur')]
    if not en or not ur:
        # OPUS names normally end in .en/.ur; capture listing for diagnosis.
        raise RuntimeError(f'parallel files not found; names={names[:20]}')
    return en[0],ur[0]

def main():
    all_en=[];all_ur=[];stats={};errors={}
    for name,url in CORPORA.items():
        try:
            r=requests.get(url,timeout=120);r.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                en_name,ur_name=pick_pair(z)
                ens=z.read(en_name).decode('utf-8',errors='replace').splitlines()
                urs=z.read(ur_name).decode('utf-8',errors='replace').splitlines()
            n=min(len(ens),len(urs));kept=0
            for e,u in zip(ens[:n],urs[:n]):
                e=' '.join(e.split());u=' '.join(u.split())
                if not e or not u or not AR.search(u):continue
                all_en.append(e);all_ur.append(u);kept+=1
            stats[name]={'download_bytes':len(r.content),'raw_pairs':n,'kept_pairs':kept,'url':url}
        except Exception as exc:
            errors[name]=repr(exc)
    if len(all_en)<50000: raise SystemExit(f'insufficient independent corpus: {len(all_en)} pairs; errors={errors}')
    Path(str(PREFIX)+'.en').write_text('\n'.join(all_en)+'\n',encoding='utf-8')
    Path(str(PREFIX)+'.ur').write_text('\n'.join(all_ur)+'\n',encoding='utf-8')
    # Build ur -> en. 20k source/target vocabulary comfortably covers the learner deck
    # while remaining practical on a standard GitHub Actions runner.
    model=Word2word.make('ur','en',str(PREFIX),n_lines=len(all_en),cutoff=20000,rerank_width=100,n_translations=15,num_workers=2,savedir=str(WORK/'lexicon'))
    # Export only translations for the current Urdu frequency universe / known risk
    # forms rather than committing the package's pickle implementation artifact.
    from wordfreq import top_n_list
    words=[];seen=set()
    for w in top_n_list('ur',50000):
        w=' '.join(w.split())
        if w and AR.search(w) and ' ' not in w and w not in seen:
            seen.add(w);words.append(w)
    translations={}
    for w in words:
        try: vals=model(w) or []
        except Exception: vals=[]
        if vals:translations[w]=[str(x) for x in vals[:15]]
    out={
      'method':'word2word custom parallel-corpus lexicon',
      'direction':'ur->en','excluded_sources':['OpenSubtitles','OPUS-100'],
      'selected_corpora':stats,'download_errors':errors,
      'parallel_pairs_total':len(all_en),'queried_urdu_words':len(words),
      'urdu_words_with_translations':len(translations),
      'translations':translations,
      'policy':'Corroboration only. Public glosses must originate in Kaikki/ReadUrdu; this independent OPUS lexicon may confirm but never author the learner meaning.'
    }
    (AUDIT/'opus_independent_urdu_lexicon.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    summary={k:v for k,v in out.items() if k!='translations'}
    (AUDIT/'opus_independent_urdu_lexicon_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
