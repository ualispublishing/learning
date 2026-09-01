#!/usr/bin/env python3
"""Independent NLLB tiebreak pass for legacy top-3000 continuation cards.

This is deliberately separate from audit_top3000_strict_multimodel.py so the
third translation signal is produced independently and can be joined with the
first-stage evidence later.  It never edits vocabulary files.
"""
from __future__ import annotations
import argparse, csv, gc, hashlib, json, re, subprocess
from pathlib import Path
from typing import List, Sequence

ROOT = Path(__file__).resolve().parents[1]
MODEL = "facebook/nllb-200-distilled-600M"
NLI = "cross-encoder/nli-MiniLM2-L6-H768"
CFG = {
    "arabic": ("arabic_top3000.csv", "f6c110b34b6ed9a441798f6bbdf82a377e35018a", "arb_Arab"),
    "french": ("french_top3000.csv", "ba7db6ffba39d6bed3e5862ac2142d8a45fb25cd", "fra_Latn"),
    "urdu": ("urdu_top3000.csv", "cd63bc1f8211bb077369d59b934abb09888cd498", "urd_Arab"),
}
RANK_RE = re.compile(r"(?m)^Rank:\s*(\d+)\s*$")
MEANING_RE = re.compile(r"(?m)^Meaning:\s*(.+?)\s*$")


def git_blob(path: str) -> str:
    p = subprocess.run(["git","rev-parse",f"HEAD:{path}"], text=True, capture_output=True, check=False)
    if p.returncode: raise RuntimeError(p.stderr.strip())
    return p.stdout.strip()


def sha256(path: Path) -> str:
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()


def batches(xs: Sequence[str], n: int):
    for i in range(0,len(xs),n): yield xs[i:i+n]


def alts(s: str) -> List[str]:
    out=[]
    for x in [s.strip(), *[p.strip() for p in s.split(';') if p.strip()][:8]]:
        if x and x not in out: out.append(x)
    return out


def load(language: str):
    rel, expected, src = CFG[language]
    actual=git_blob(rel)
    if actual != expected:
        raise RuntimeError(f"{language}: source blob changed; expected {expected}, got {actual}")
    p=ROOT/rel
    with p.open(encoding='utf-8-sig',newline='') as f: raw=list(csv.DictReader(f))
    if len(raw)!=2000: raise RuntimeError(f"{language}: expected 2000 rows, got {len(raw)}")
    rows=[]
    for rank, r in enumerate(raw,1001):
        front=(r.get('Front') or '').strip(); back=r.get('Back') or ''
        rm=RANK_RE.search(back); mm=MEANING_RE.search(back)
        if not front or not rm or int(rm.group(1))!=rank or not mm:
            raise RuntimeError(f"{language}: malformed row {rank}")
        rows.append({'language':language,'rank':rank,'target':front,'english':mm.group(1).strip()})
    return rows, {'path':rel,'git_blob':actual,'sha256':sha256(p),'src_lang':src}


def translate(texts, src, batch_size):
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    print('Loading',MODEL,src,'-> eng_Latn',flush=True)
    tok=AutoTokenizer.from_pretrained(MODEL)
    model=AutoModelForSeq2SeqLM.from_pretrained(MODEL); model.eval()
    tok.src_lang=src
    forced=tok.convert_tokens_to_ids('eng_Latn')
    out=[]
    with torch.inference_mode():
        for i,b in enumerate(batches(texts,batch_size),1):
            enc=tok(list(b),return_tensors='pt',padding=True,truncation=True,max_length=80)
            gen=model.generate(**enc,forced_bos_token_id=forced,max_new_tokens=40,num_beams=1,do_sample=False)
            out += [x.strip() for x in tok.batch_decode(gen,skip_special_tokens=True)]
            if i%10==0: print(' NLLB',min(i*batch_size,len(texts)),'/',len(texts),flush=True)
    del model,tok; gc.collect(); return out


def score(rows, trans, batch_size):
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    tok=AutoTokenizer.from_pretrained(NLI)
    model=AutoModelForSequenceClassification.from_pretrained(NLI); model.eval()
    pairs=[]; meta=[]
    for i,r in enumerate(rows):
        for j,a in enumerate(alts(r['english'])):
            pairs += [(a,trans[i]),(trans[i],a)]
            meta += [(i,j,0),(i,j,1)]
    probs=[]
    with torch.inference_mode():
        for start in range(0,len(pairs),batch_size):
            b=pairs[start:start+batch_size]
            enc=tok([x for x,_ in b],[y for _,y in b],return_tensors='pt',padding=True,truncation=True,max_length=160)
            probs += [float(x) for x in torch.softmax(model(**enc).logits,dim=-1)[:,1].cpu()]
    d={}
    for m,p in zip(meta,probs): d.setdefault((m[0],m[1]),{})[m[2]]=p
    scores=[]
    for i,r in enumerate(rows):
        vals=[]
        for j,_ in enumerate(alts(r['english'])):
            z=d[(i,j)]; vals.append(min(z.get(0,0),z.get(1,0)))
        scores.append(max(vals))
    del model,tok; gc.collect(); return scores


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--language',choices=CFG,required=True); ap.add_argument('--output-dir',type=Path,required=True); ap.add_argument('--batch-size',type=int,default=20)
    a=ap.parse_args(); rows,source=load(a.language); trans=translate([r['target'] for r in rows],source['src_lang'],a.batch_size); scores=score(rows,trans,max(24,a.batch_size*2))
    a.output_dir.mkdir(parents=True,exist_ok=True)
    out=a.output_dir/f'{a.language}_nllb_tiebreak.jsonl'
    counts={'SUPPORTED':0,'WEAK_OR_DIFFERENT':0}
    with out.open('w',encoding='utf-8') as f:
        for r,t,s in zip(rows,trans,scores):
            status='SUPPORTED' if s>=0.60 else 'WEAK_OR_DIFFERENT'; counts[status]+=1
            rec={**r,'source_git_blob':source['git_blob'],'nllb_model':MODEL,'nllb_translation_en':t,'candidate_vs_nllb_bidirectional_entailment':round(s,6),'nllb_status':status}
            f.write(json.dumps(rec,ensure_ascii=False,sort_keys=True)+'\n')
    summary={'schema':'top3000-nllb-tiebreak-v1','language':a.language,'rows_checked':len(rows),'source':source,'model':MODEL,'nli_model':NLI,'counts':counts,'safe_auto_corrections':0,'output':out.name}
    (a.output_dir/f'{a.language}_nllb_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__': main()
