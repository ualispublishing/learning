#!/usr/bin/env python3
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'reading/audit'
LEVELS = ('b1','b2','c1','c2')
PATHS = {l: ROOT / f'reading/arabic/{l}/passages.jsonl' for l in LEVELS}
REPORT = AUDIT / 'arabic_b1_c2_current_inventory_2026-08-23.json'
SEMANTIC_DIR = AUDIT / 'arabic_b1_c2_semantic_candidates_2026-08-23'
LATIN = re.compile(r'[A-Za-z]')
GRAMMAR_TYPES = {'grammar_function','grammar_category','person_form','morphology_label','syntax_label'}
META_PROMPT = re.compile(r'(?:ما\s+وظيفة|ما\s+دور|ما\s+نوع|التصنيف\s+النحوي|التصنيف\s+الصرفي|علامة\s+نحوية|وظيفة\s+نحوية)')


def blob(path):
    return subprocess.check_output(['git','hash-object',str(path)], text=True).strip()

def load(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]

def wc(s):
    return len(re.findall(r'\S+', str(s)))

def sc(s):
    return sum(str(s).count(p) for p in ('.','؟','!','۔'))

def learner_strings(r):
    out=[r.get('title',''),r.get('text','')]
    for q in r.get('questions',[]):
        out.append(q.get('prompt','')); out.extend(q.get('options',[]) or [])
    for a in r.get('answer_key',[]):
        out.extend([a.get('answer',''),a.get('explanation','')])
    return out

def add(bucket, code, **kw):
    bucket.append({'code':code,**kw})

def main():
    AUDIT.mkdir(parents=True, exist_ok=True); SEMANTIC_DIR.mkdir(parents=True, exist_ok=True)
    report={'schema_version':1,'date':'2026-08-23','scope':'Fresh current-corpus Arabic B1-C2 inventory','input_blobs':{},'levels':{},'hard_errors':[],'diagnostics':[],'semantic_candidate_count':0,'quality_promotion':False}
    all_candidates=[]
    for level in LEVELS:
        path=PATHS[level]; report['input_blobs'][level]=blob(path); rows=load(path)
        qtypes=Counter(); candidates=[]; level_errors=[]; level_diags=[]; new_ids=[]; qtotal=atotal=0
        words=[]; sentences=[]
        for i,r in enumerate(rows,1):
            pid=r.get('id'); unit=(i-1)//6+1; pno=(i-1)%6+1; expected=f'ar-{level}-u{unit:02d}-p{pno:02d}'
            if r.get('sequence')!=i:add(level_errors,'sequence',passage_id=pid,expected=i,actual=r.get('sequence'))
            if r.get('unit')!=unit:add(level_errors,'unit',passage_id=pid,expected=unit,actual=r.get('unit'))
            if pid!=expected:add(level_errors,'id',passage_id=pid,expected=expected)
            if r.get('language')!='ar':add(level_errors,'language',passage_id=pid,actual=r.get('language'))
            if str(r.get('cefr','')).lower()!=level:add(level_errors,'cefr',passage_id=pid,actual=r.get('cefr'))
            calc_wc=wc(r.get('text','')); calc_sc=sc(r.get('text','')); words.append(calc_wc); sentences.append(calc_sc)
            if r.get('word_count')!=calc_wc:add(level_errors,'word_count_metadata',passage_id=pid,metadata=r.get('word_count'),calculated=calc_wc)
            if r.get('sentence_count')!=calc_sc:add(level_errors,'sentence_count_metadata',passage_id=pid,metadata=r.get('sentence_count'),calculated=calc_sc)
            qs=r.get('questions',[]); ans=r.get('answer_key',[]); qtotal+=len(qs); atotal+=len(ans)
            if len(qs)!=10:add(level_errors,'question_count',passage_id=pid,actual=len(qs))
            if len(ans)!=10:add(level_errors,'answer_count',passage_id=pid,actual=len(ans))
            if [q.get('id') for q in qs]!=[f'q{x}' for x in range(1,11)]:add(level_errors,'question_ids',passage_id=pid)
            if [a.get('id') for a in ans]!=[f'a{x}' for x in range(1,11)]:add(level_errors,'answer_ids',passage_id=pid)
            byqid={a.get('question_id'):a for a in ans}
            local={t.get('id') for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)} | {t.get('id') for t in r.get('review_lexical_targets',[]) if isinstance(t,dict)}
            prompts=[]
            for q in qs:
                qid=q.get('id'); typ=q.get('type'); qtypes[typ]+=1; prompts.append(' '.join(str(q.get('prompt','')).split())); a=byqid.get(qid)
                if not a:add(level_errors,'missing_answer',passage_id=pid,question_id=qid);continue
                if q.get('answer_id')!=a.get('id'):add(level_errors,'qa_link',passage_id=pid,question_id=qid,expected=q.get('answer_id'),actual=a.get('id'))
                tids=q.get('target_ids',[]) or []
                if not isinstance(tids,list):add(level_errors,'target_ids_type',passage_id=pid,question_id=qid)
                else:
                    for tid in tids:
                        if tid not in local:add(level_errors,'target_not_local',passage_id=pid,question_id=qid,target_id=tid)
                if typ=='cloze_transfer':
                    blanks=str(q.get('prompt','')).count('_____'); parts=[x.strip() for x in re.split(r'[؛;]',str(a.get('answer',''))) if x.strip()]
                    if blanks!=len(parts):add(level_errors,'cloze_cardinality',passage_id=pid,question_id=qid,blanks=blanks,answer_parts=len(parts),answer=a.get('answer'))
                if typ in GRAMMAR_TYPES or META_PROMPT.search(str(q.get('prompt',''))):
                    candidates.append({'level':level,'passage_id':pid,'unit':r.get('unit'),'sequence':r.get('sequence'),'title':r.get('title'),'question_id':qid,'type':typ,'prompt':q.get('prompt'),'answer':a.get('answer'),'explanation':a.get('explanation'),'target_ids':tids,'text':r.get('text'),'review_status':'pending_semantic_adjudication','decision':None,'rationale':None})
            for p,n in Counter(prompts).items():
                if n>1:add(level_errors,'duplicate_prompt',passage_id=pid,prompt=p,count=n)
            for t in r.get('new_lexical_targets',[]):
                if not isinstance(t,dict):add(level_errors,'new_target_object',passage_id=pid);continue
                new_ids.append(t.get('id'))
                if not isinstance(t.get('exposures_in_text'),int) or t.get('exposures_in_text')<1:add(level_errors,'invalid_exposure_count',passage_id=pid,target_id=t.get('id'),value=t.get('exposures_in_text'))
                if not str(t.get('intended_sense','')).strip():add(level_errors,'empty_intended_sense',passage_id=pid,target_id=t.get('id'))
                form=str(t.get('form') or '')
                if form and form not in str(r.get('text','')):add(level_diags,'new_target_no_exact_surface',passage_id=pid,target_id=t.get('id'),form=form,lemma=t.get('lemma'),part_of_speech=t.get('part_of_speech'),declared=t.get('exposures_in_text'))
            for t in r.get('review_lexical_targets',[]):
                if isinstance(t,dict) and t.get('representation')=='running_text' and str(t.get('form') or '') not in str(r.get('text','')):
                    add(level_diags,'running_text_review_no_exact_surface',passage_id=pid,target_id=t.get('id'),form=t.get('form'),review_stage=t.get('review_stage'))
            for s in learner_strings(r):
                if LATIN.search(str(s)):
                    add(level_errors,'latin_in_learner_facing_arabic',passage_id=pid,sample=str(s)[:180]);break
            quality=r.get('quality',{})
            if quality.get('status')!='draft':add(level_errors,'quality_status',passage_id=pid,value=quality.get('status'))
            for gate in ('answer_key_check','coverage_check','linguistic_review','pedagogical_review','schema_check'):
                if quality.get(gate)!='pending':add(level_errors,'quality_gate',passage_id=pid,gate=gate,value=quality.get(gate))
        if len(rows)!=60:add(level_errors,'passage_total',level=level,expected=60,actual=len(rows))
        if qtotal!=600:add(level_errors,'question_total',level=level,expected=600,actual=qtotal)
        if atotal!=600:add(level_errors,'answer_total',level=level,expected=600,actual=atotal)
        dup=[x for x,n in Counter(new_ids).items() if x and n>1]
        if dup:add(level_errors,'duplicate_new_target_ids',level=level,ids=dup)
        report['hard_errors'].extend(level_errors);report['diagnostics'].extend(level_diags);all_candidates.extend(candidates)
        report['levels'][level]={'passages':len(rows),'questions':qtotal,'answers':atotal,'new_targets':len(new_ids),'hard_errors':len(level_errors),'diagnostics':len(level_diags),'semantic_candidates':len(candidates),'question_type_counts':dict(qtypes),'word_count':{'min':min(words) if words else None,'max':max(words) if words else None,'mean':round(sum(words)/len(words),1) if words else None},'sentence_count':{'min':min(sentences) if sentences else None,'max':max(sentences) if sentences else None,'mean':round(sum(sentences)/len(sentences),1) if sentences else None}}
        (SEMANTIC_DIR/f'{level}.json').write_text(json.dumps({'level':level,'input_blob':report['input_blobs'][level],'candidate_count':len(candidates),'candidates':candidates},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report['semantic_candidate_count']=len(all_candidates);report['hard_error_count']=len(report['hard_errors']);report['diagnostic_count']=len(report['diagnostics']);report['status']='PASS_STRUCTURE_SEMANTIC_ADJUDICATION_REQUIRED' if not report['hard_errors'] else 'FAIL_STRUCTURE'
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'hard_errors':report['hard_error_count'],'diagnostics':report['diagnostic_count'],'semantic_candidates':report['semantic_candidate_count'],'levels':report['levels'],'blobs':report['input_blobs']},ensure_ascii=False))
    if report['hard_errors']:
        print(json.dumps({'hard_error_sample':report['hard_errors'][:60]},ensure_ascii=False));raise SystemExit(1)
if __name__=='__main__':main()
