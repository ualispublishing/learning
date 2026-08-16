#!/usr/bin/env python3
"""Generate French A2 Unit 01 / sequences 1-6 as the first guarded A2 batch."""
from __future__ import annotations
import base64,csv,json,re,subprocess,zlib
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[2]
A1=ROOT/'reading/french/a1/passages.jsonl'
CANON=ROOT/'reading/french/a2/passages.jsonl'
SCHEMA=ROOT/'reading/schema/passage.schema.json'
LEXICON=ROOT/'french_top1000.csv'
EXPECTED_A1_BLOB='b6c15291b7871e196cac8f7b5920923f2a3a95a9'
NEW_FORMS=('retard','conseil','erreur','expliquer','essayer','possible','réparer','prévenir','rendez-vous','découvrir')
DATA=json.loads(zlib.decompress(base64.b64decode('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'))).decode())

def lexicon():
    out={}
    with LEXICON.open(encoding='utf-8',newline='') as f:
        for row in csv.DictReader(f):
            form=(row.get('Front') or '').strip(); back=row.get('Back') or ''
            r=re.search(r'Rank:\s*(\d+)',back); m=re.search(r'Meaning:\s*(.+)',back); p=re.search(r'Part of speech:\s*(.+)',back)
            if form and r and m and p: out[form]={'rank':int(r.group(1)),'sense':m.group(1).strip(),'pos':p.group(1).strip()}
    return out

def tid(rank): return f'fr-rank-{rank:04d}'
def exact_count(text,form): return len(re.findall(rf'(?<!\w){re.escape(form)}(?!\w)',text,flags=re.I|re.UNICODE))
def a1_prior(rows):
    out={}
    for r in rows:
        for t in r.get('new_lexical_targets',[]):
            if isinstance(t,dict) and t.get('form'): out.setdefault(t['form'],[]).append(t)
    return out

def new_target(form,text,L):
    s=L[form]; n=exact_count(text,form)
    if n<1: raise AssertionError(f'{form}: new target has no exact running-text exposure')
    return {'id':tid(s['rank']),'form':form,'lemma':form,'intended_sense':s['sense'],'part_of_speech':s['pos'],'register':'contemporary standard','variety':None,'context_strategy':['scenario_resolution'],'first_introduced':True,'exposures_in_text':n,'source_lexicon':'french_top1000.csv','source_rank':s['rank'],'beyond_base':False}

def bridge_review(form,P):
    hits=P.get(form,[])
    if len(hits)!=1: raise AssertionError(f'{form}: expected one A1 introduction for A2 bridge, got {len(hits)}')
    return {'id':hits[0]['id'],'form':form,'review_stage':'R5','representation':'running_text','expected_exposure_number':None}

def current_review(form,L):
    return {'id':tid(L[form]['rank']),'form':form,'review_stage':'R1','representation':'summary','expected_exposure_number':None}

def qa(items,ids):
    qs=[]; ans=[]
    for i,(typ,prompt,answer,forms) in enumerate(items,1):
        qid=f'q{i}'; aid=f'a{i}'; q={'id':qid,'type':typ,'prompt':prompt,'answer_id':aid}
        if forms: q['target_ids']=[ids[f] for f in forms]
        qs.append(q); ans.append({'id':aid,'question_id':qid,'answer':answer,'explanation':''})
    return qs,ans

def mk(s,new,reviews,ids,speed=False):
    qs,ans=qa(s['items'],ids); text=s['text']
    return {'id':s['pid'],'language':'fr','cefr':'A2','unit':1,'sequence':s['seq'],'revision':1,'title':s['title'],'passage_type':s['ptype'],'genre':s['genre'],'domains':s['domains'],'topics':s['topics'],'text':text,'word_count':len(text.split()),'sentence_count':max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),'estimated_known_token_coverage':0,'new_lexical_targets':new,'review_lexical_targets':reviews,'grammar_targets':s['grammar'],'discourse_targets':s['discourse'],'questions':qs,'answer_key':ans,'speed_training':{'timed':speed,'benchmark_eligible':speed,'comprehension_gate':0.8,'new_word_policy':'none' if speed else 'controlled','notes':'Generation-stage French A2 Unit 01; full multi-pass French audit deferred under generation-first policy.'},'quality':{'status':'draft','schema_check':'pending','linguistic_review':'pending','pedagogical_review':'pending','answer_key_check':'pending','coverage_check':'pending','fact_check':'not_required','notes':['Guarded French A2 Unit 01 generation batch.','A2 140-220 planning band, source identity, A1 freshness, local target linkage, bridge-review visibility, continuity, and checkpoint invariants are enforced.']},'paired_text_group':None,'prerequisites':['French A1 generated corpus, sequences 1-60'],'difficulty_notes_internal':'A2 transition: routine problems and solutions, reference chains, subordinate relations, motives/cause-effect, and increased cloze transfer.','reader_tags':['unit_role:'+s['ptype'],'generation_batch','french_a2_u01']}

def build(a1,L):
    P=a1_prior(a1)
    problems=[]
    for f in NEW_FORMS:
        if f not in L: problems.append(f'{f}:missing_lexicon')
        if P.get(f): problems.append(f'{f}:already_A1_target')
    if problems: raise AssertionError('candidate guard failures: '+', '.join(problems))
    out=[]
    for s in DATA['specs']:
        new=[new_target(f,s['text'],L) for f in s['forms']]
        reviews=[bridge_review(f,P) for f in s['reviews']]
        ids={t['form']:t['id'] for t in new+reviews}
        out.append(mk(s,new,reviews,ids))
    reviews=[current_review(f,L) for f in NEW_FORMS]
    ids={t['form']:t['id'] for t in reviews}
    s={'pid':'fr-a2-u01-p06','seq':6,'ptype':'checkpoint','title':'Gérer un petit problème','genre':'A2 transition checkpoint','domains':['personal','public','educational'],'topics':['problem solving','communication','A2 transition'],'text':DATA['p6']['text'],'grammar':[{'id':'fr-a2-u01-cause-choice-review','role':'integration','description':'integrate cause, option, action, and result across a short text'}],'discourse':[{'id':'fr-a2-u01-problem-cycle','role':'integration','description':'summarize a problem-solution sequence across multiple situations'}],'items':DATA['p6']['items']}
    out.append(mk(s,[],reviews,ids,True))
    return out

def main():
    if CANON.exists(): raise AssertionError('French A2 canonical path already exists; live A2 state must be re-read before writing')
    a1_blob=subprocess.check_output(['git','hash-object',str(A1)],text=True).strip()
    if a1_blob!=EXPECTED_A1_BLOB: raise AssertionError(f'A1 bridge blob drift: {a1_blob} != {EXPECTED_A1_BLOB}')
    a1=[json.loads(x) for x in A1.read_text(encoding='utf-8').splitlines() if x.strip()]
    if len(a1)!=60 or [r['sequence'] for r in a1]!=list(range(1,61)) or a1[-1]['id']!='fr-a1-u10-p06': raise AssertionError('expected exact completed 60-passage A1 bridge state')
    L=lexicon(); unit=build(a1,L); V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')))
    if [r['sequence'] for r in unit]!=list(range(1,7)) or [r['id'] for r in unit]!=[f'fr-a2-u01-p{i:02d}' for i in range(1,7)]: raise AssertionError('A2 Unit01 continuity failure')
    all_new=[]
    for r in unit:
        errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
        if errs: raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:6]]}")
        if not 140<=r['word_count']<=220: raise AssertionError(f"{r['id']}: A2 word band {r['word_count']}")
        if len(r['questions'])!=10 or len(r['answer_key'])!=10: raise AssertionError(f"{r['id']}: assessment count")
        amap={a['question_id']:a['id'] for a in r['answer_key']}; local={t['id'] for field in ('new_lexical_targets','review_lexical_targets') for t in r.get(field,[]) if isinstance(t,dict)}
        if len(amap)!=10: raise AssertionError(f"{r['id']}: answer mapping count")
        for q in r['questions']:
            if amap.get(q['id'])!=q['answer_id']: raise AssertionError(f"{r['id']} {q['id']}: linkage")
            if any(x not in local for x in q.get('target_ids',[])): raise AssertionError(f"{r['id']} {q['id']}: undeclared target")
        for t in r['new_lexical_targets']:
            s=L.get(t['form'])
            if not s or t['source_rank']!=s['rank'] or t['id']!=tid(s['rank']): raise AssertionError(f"{r['id']}: source identity {t['form']}")
            if exact_count(r['text'],t['form'])!=t['exposures_in_text']: raise AssertionError(f"{r['id']}: exposure mismatch {t['form']}")
            all_new.append(t['id'])
        for t in r['review_lexical_targets']:
            if t['representation'] in {'running_text','summary'} and exact_count(r['text'],t['form'])<1: raise AssertionError(f"{r['id']}: invisible review {t['form']}")
    if len(all_new)!=10 or len(set(all_new))!=10: raise AssertionError(f'expected 10 unique A2 Unit01 targets, got {len(all_new)}/{len(set(all_new))}')
    if unit[-1]['new_lexical_targets']!=[]: raise AssertionError('A2 Unit01 P06 must have zero new lexical targets')
    CANON.parent.mkdir(parents=True,exist_ok=True)
    CANON.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in unit),encoding='utf-8')
    print(json.dumps({'status':'PASS','level':'A2','unit':1,'passages':6,'questions':60,'answers':60,'new_targets':[{'form':f,'rank':L[f]['rank'],'id':tid(L[f]['rank'])} for f in NEW_FORMS],'word_counts':{r['id']:r['word_count'] for r in unit},'checkpoint_new_targets':0},ensure_ascii=False))

if __name__=='__main__': main()
