#!/usr/bin/env python3
import json,re,subprocess,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=ROOT/'reading/audit/arabic_a1_a2_manual_review_evidence_2026-08-23.json'
OUTPUT=ROOT/'reading/audit/arabic_a1_a2_manual_review_triage_v2_2026-08-23.json'
A1=ROOT/'reading/arabic/a1/passages.jsonl'; A2=ROOT/'reading/arabic/a2/passages.jsonl'
EXPECTED={'a1':'4723cb4c9974a9a9c84b6c030d9c1a30c0820500','a2':'d6a10dddde14628c8e4a7ddb4db7781604852210'}
DIAC=re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]'); WORD=re.compile(r'[\u0621-\u064A]+')
PRO=('و','ف','ب','ك','ل'); NSUF=('هما','هم','هن','كما','كم','كن','نا','ها','ه','ك','ي','ات','ون','ين','ان'); VPRE=('أ','ا','ن','ي','ت'); VSUF=('ون','ين','ان','وا','نا','تم','تن','ن','ت')
def blob(p): return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def norm(s): return DIAC.sub('',unicodedata.normalize('NFKC',str(s or '')).replace('ـ','')).replace('ٱ','ا')
def toks(s): return WORD.findall(norm(s))
def nominal_forms(tok):
    out={tok}; frontier={tok}
    for _ in range(2):
        nxt=set()
        for x in frontier:
            for p in PRO:
                if x.startswith(p) and len(x)-1>=2:nxt.add(x[1:])
            if x.startswith('ال') and len(x)>4:nxt.add(x[2:])
        out|=nxt; frontier=nxt
    exp=set(out)
    for x in list(out):
        for s in NSUF:
            if x.endswith(s) and len(x)-len(s)>=2:exp.add(x[:-len(s)])
        if x.endswith('ا') and len(x)>3:exp.add(x[:-1])
    return exp
def verb_cores(tok):
    out=set(nominal_forms(tok))
    for x in list(out):
        if len(x)>=4 and x[0] in VPRE:out.add(x[1:])
    for x in list(out):
        for s in VSUF:
            if x.endswith(s) and len(x)-len(s)>=3:out.add(x[:-len(s)])
    return {x for x in out if len(x)>=2}
def lemma_forms(meta, teaching):
    vals=[teaching]
    lemma=str(meta.get('lemma') or '')
    for part in re.split(r'[/؛;،,]|\bor\b',lemma):
        p=part.strip()
        if p and re.search(r'[\u0621-\u064A]',p):vals.append(p)
    return list(dict.fromkeys(norm(x) for x in vals if norm(x)))
def match_token(tok, forms, is_verb):
    if tok in forms:return 'exact_form_or_lemma'
    for f in forms:
        if nominal_forms(tok)&nominal_forms(f):return 'nominal_or_orthographic'
    if is_verb:
        for f in forms:
            if verb_cores(tok)&verb_cores(f):return 'verbal_inflection_or_lemma_alternation'
    return None
def evidence(text, forms, is_verb):
    matched=[]; counts=Counter()
    for tok in toks(text):
        kind=match_token(tok,forms,is_verb)
        if kind:
            matched.append({'token':tok,'kind':kind});counts[kind]+=1
    return {'forms_checked':forms,'counts':dict(counts),'total_supported':len(matched),'matched':matched}
def main():
    actual={'a1':blob(A1),'a2':blob(A2)}
    if actual!=EXPECTED:raise SystemExit(f'unexpected blobs {actual}')
    src=json.loads(EVIDENCE.read_text(encoding='utf-8'))
    if src.get('packet_count')!=107:raise SystemExit('expected 107')
    decisions=[]; dc=Counter(); repair=[]; manual=[]
    for item in src['items']:
        meta=item.get('target_metadata') or {}; pos=str(meta.get('part_of_speech') or '').lower(); is_verb='verb' in pos
        forms=lemma_forms(meta,item.get('target_form','')); ev=evidence(item.get('full_text',''),forms,is_verb)
        code=item.get('warning_code'); declared=meta.get('declared_exposures_in_text')
        d={'review_id':item.get('review_id'),'passage_id':item.get('passage_id'),'target_id':item.get('target_id'),'target_form':item.get('target_form'),'lemma':meta.get('lemma'),'part_of_speech':pos,'warning_code':code,'declared_exposures':declared,'evidence':ev}
        if code=='new_target_form_not_exactly_found_in_text':
            if ev['total_supported']>0 and (not isinstance(declared,int) or ev['total_supported']==declared):
                dec='RESOLVE_VALID_LEMMA_INFLECTION_REALIZATION'
            elif ev['total_supported']>0:
                dec='MANUAL_EXPOSURE_COUNT_CHECK';manual.append(d)
            else:
                dec='REPAIR_NEW_TARGET_REALIZATION';repair.append(d);manual.append(d)
        elif code=='running_text_review_target_no_exact_surface':
            if ev['total_supported']>0:dec='RESOLVE_VALID_LEMMA_INFLECTION_REVIEW'
            else:dec='REPAIR_FALSE_RUNNING_TEXT_REVIEW_METADATA';repair.append(d)
        elif code=='declared_exposure_count_differs_from_exact_surface_count':
            if isinstance(declared,int) and ev['total_supported']==declared:dec='RESOLVE_DECLARED_COUNT_BY_LEMMA_VARIANTS'
            else:dec='MANUAL_EXPOSURE_COUNT_CHECK';manual.append(d)
        else:dec='MANUAL_UNKNOWN';manual.append(d)
        d['decision']=dec;dc[dec]+=1;decisions.append(d)
    out={'schema_version':2,'date':'2026-08-23','scope':'Arabic A1+A2 lemma-aware triage','input_blobs':actual,'source_count':107,'decision_counts':dict(dc),'auto_resolved_count':sum(n for k,n in dc.items() if k.startswith('RESOLVE_')),'repair_candidate_count':len(repair),'manual_check_count':len(manual),'repair_candidates':repair,'manual_checks':manual,'decisions':decisions,'guardrail':'No corpus mutation. Verbal equivalence is considered only when part_of_speech explicitly contains verb and is checked against all Arabic lemma alternatives as well as the teaching form.'}
    OUTPUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:out[k] for k in ('decision_counts','auto_resolved_count','repair_candidate_count','manual_check_count')},ensure_ascii=False))
if __name__=='__main__':main()
