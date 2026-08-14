#!/usr/bin/env python3
"""Final Arabic review pass 04: answer/evidence alignment diagnostics.

Uses conservative surface heuristics to identify questions that deserve manual
semantic review. No flagged item is automatically declared wrong solely because
of paraphrase or morphology.
"""
from __future__ import annotations
import json,re,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
OUT=ROOT/'reading/audit/final_arabic_pass04_answer_evidence_alignment.json'
DIAC=re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]')
ARWORD=re.compile(r'[\u0621-\u064A]+')
QUOTED=re.compile(r'«([^»]+)»')
STOP={'في','من','إلى','على','عن','مع','أن','إن','ما','ماذا','لماذا','كيف','متى','أين','هو','هي','هم','هن','هذا','هذه','ذلك','تلك','التي','الذي','ثم','أو','و','ف','ب','ل','ك','كان','كانت','يكون','تكون','قد','لا','لم','لن','كل','بعد','قبل'}
DIRECT={'literal_detail','sequence','reference_resolution','cause_effect'}
LONG={'gist','summary','synthesis','cross_text_synthesis','main_claim','inference','motive','stance','assumption','argument_relation'}

def norm(s):
    s=unicodedata.normalize('NFKC',str(s or '')).replace('ـ','').replace('ٱ','ا')
    return DIAC.sub('',s)
def toks(s):
    return [x for x in ARWORD.findall(norm(s)) if x not in STOP and len(x)>1]
def add(flags,code,**kw): flags.append({'code':code,**kw})

def main():
    flags=[]; level_summary={}; total_q=0
    for level in LEVELS:
        rows=[json.loads(x) for x in (ROOT/f'reading/arabic/{level}/passages.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
        c=Counter(); passages_flagged=set()
        for row in rows:
            pid=row['id']; text_tokens=set(toks(row.get('text','')))
            qs=row.get('questions',[]); ans={a.get('question_id'):a for a in row.get('answer_key',[]) if isinstance(a,dict)}
            seen_prompts=set()
            for q in qs:
                total_q+=1; qid=q.get('id'); typ=q.get('type'); prompt=q.get('prompt',''); a=ans.get(qid,{}); answer=a.get('answer','')
                np=' '.join(norm(prompt).split())
                if np in seen_prompts:
                    add(flags,'duplicate_prompt_within_passage',level=level,passage_id=pid,question_id=qid,prompt=prompt); c['duplicate_prompt_within_passage']+=1; passages_flagged.add(pid)
                seen_prompts.add(np)
                if not str(answer).strip():
                    add(flags,'empty_answer',level=level,passage_id=pid,question_id=qid); c['empty_answer']+=1; passages_flagged.add(pid); continue
                if ' '.join(norm(answer).split())==np:
                    add(flags,'answer_equals_prompt',level=level,passage_id=pid,question_id=qid); c['answer_equals_prompt']+=1; passages_flagged.add(pid)
                at=toks(answer)
                if typ in DIRECT and at and text_tokens and not (set(at)&text_tokens):
                    add(flags,'direct_answer_zero_content_overlap_with_passage',level=level,passage_id=pid,question_id=qid,type=typ,prompt=prompt,answer=answer)
                    c['direct_answer_zero_content_overlap_with_passage']+=1; passages_flagged.add(pid)
                if typ in LONG and len(at)<2:
                    add(flags,'high_level_answer_extremely_short',level=level,passage_id=pid,question_id=qid,type=typ,prompt=prompt,answer=answer,content_tokens=at)
                    c['high_level_answer_extremely_short']+=1; passages_flagged.add(pid)
                if typ=='contrast':
                    opts=QUOTED.findall(prompt)
                    if len(opts)>=2:
                        na=norm(answer)
                        if not any(norm(o) in na or na.strip(' .،؛')==norm(o).strip(' .،؛') for o in opts):
                            add(flags,'contrast_answer_not_surface_aligned_to_quoted_options',level=level,passage_id=pid,question_id=qid,prompt=prompt,answer=answer,quoted_options=opts)
                            c['contrast_answer_not_surface_aligned_to_quoted_options']+=1; passages_flagged.add(pid)
                if typ=='cloze_transfer':
                    tids=q.get('target_ids',[]) if isinstance(q.get('target_ids'),list) else []
                    if not tids:
                        add(flags,'cloze_without_target_id',level=level,passage_id=pid,question_id=qid,prompt=prompt,answer=answer)
                        c['cloze_without_target_id']+=1; passages_flagged.add(pid)
            # Weak duplicate-answer diagnostic within one passage.
            normalized_answers=[' '.join(norm(a.get('answer','')).split()) for a in row.get('answer_key',[]) if isinstance(a,dict)]
            dup=[x for x,n in Counter(normalized_answers).items() if x and n>1]
            if dup:
                add(flags,'duplicate_answer_text_within_passage',level=level,passage_id=pid,answers=dup)
                c['duplicate_answer_text_within_passage']+=1; passages_flagged.add(pid)
        level_summary[level]={'passages':len(rows),'flagged_passages':len(passages_flagged),'flags_by_code':dict(c)}
    payload={
        'pass':4,'name':'answer_evidence_alignment_diagnostics','scope':'Arabic A1-C2 canonical reading corpus',
        'method':'conservative surface diagnostics for direct-evidence answers, answer length, contrast-option alignment, cloze targeting, and within-passage duplicates',
        'not_claimed':['semantic incorrectness from zero lexical overlap','morphological equivalence','full answer-key correctness'],
        'levels':level_summary,'totals':{'questions':total_q,'review_flags':len(flags)},'flags':flags,
        'status':'PASS' if not flags else 'REVIEW_REQUIRED'}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(payload['totals'],ensure_ascii=False));print('status='+payload['status'])
if __name__=='__main__':main()
