#!/usr/bin/env python3
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'reading/audit/arabic_b1_c2_semantic_candidates_2026-08-23'
OUT=ROOT/'reading/audit/arabic_b1_c2_semantic_triage_2026-08-23.json'
SUMMARY=ROOT/'reading/audit/arabic_b1_c2_semantic_triage_summary_2026-08-23.md'
LEVELS=('b1','b2','c1','c2')
QUOTE=re.compile(r'«[^»]*»|“[^”]*”|"[^"]*"')
WS=re.compile(r'\s+')
DIRECT_LABEL=re.compile(r'^(?:ما\s+)?(?:وظيفة|دور|نوع|التصنيف)|ما\s+وظيفة|ما\s+دور')
EFFECT=re.compile(r'(?:كيف|لماذا|ماذا\s+يضيف|ماذا\s+يفيد|ما\s+الأثر|ما\s+الفرق|كيف\s+يغيّر|كيف\s+يساعد|ماذا\s+يوحي|ماذا\s+يشير)')
LOGIC_WORDS=re.compile(r'(?:شرط|نتيجة|سبب|مقابلة|استدراك|احتمال|افتراض|تباين|تعارض|تعليل|استثناء|بديل|تخيير|ترتيب|توكيد|ربط|انتقال|مقارنة|تناقض|تفسير)')

def norm_template(prompt):
    p=QUOTE.sub('«…»',str(prompt or ''))
    p=re.sub(r'\d+','N',p)
    return WS.sub(' ',p).strip()

def awc(answer):return len(str(answer or '').split())

def classify(c):
    p=str(c.get('prompt') or '');a=str(c.get('answer') or '');typ=c.get('type');n=awc(a)
    if typ in {'grammar_category','person_form','morphology_label','syntax_label'}:
        return 'likely_label_trivia'
    if EFFECT.search(p):
        return 'likely_meaningful_discourse_effect'
    if DIRECT_LABEL.search(p) and n<=4:
        return 'likely_label_trivia'
    if typ=='grammar_function' and n<=3 and LOGIC_WORDS.search(a):
        return 'likely_label_trivia'
    if typ=='grammar_function' and n>=5:
        return 'likely_contextual_function'
    if typ=='grammar_function':
        return 'needs_manual_function_review'
    if DIRECT_LABEL.search(p):
        return 'needs_manual_metalinguistic_review'
    return 'needs_manual_context_review'

def main():
    all_items=[];level_counts={};templates=Counter();examples=defaultdict(list)
    for level in LEVELS:
        d=json.loads((SRC/f'{level}.json').read_text(encoding='utf-8'))
        counts=Counter();items=[]
        for c in d.get('candidates',[]):
            x=dict(c);x['triage']=classify(x);x['answer_word_count']=awc(x.get('answer'));x['prompt_template']=norm_template(x.get('prompt'))
            counts[x['triage']]+=1;templates[(level,x['triage'],x['prompt_template'])]+=1
            if len(examples[(level,x['triage'])])<8:examples[(level,x['triage'])].append({'passage_id':x.get('passage_id'),'question_id':x.get('question_id'),'type':x.get('type'),'prompt':x.get('prompt'),'answer':x.get('answer'),'explanation':x.get('explanation')})
            items.append(x);all_items.append(x)
        level_counts[level]=dict(counts)
    groups=[]
    for (level,triage,t),n in sorted(templates.items(),key=lambda kv:(kv[0][0],kv[0][1],-kv[1],kv[0][2])):
        groups.append({'level':level,'triage':triage,'count':n,'prompt_template':t})
    report={'schema_version':1,'date':'2026-08-23','scope':'Arabic B1-C2 grammar/discourse semantic triage','candidate_count':len(all_items),'level_counts':level_counts,'triage_counts':dict(Counter(x['triage'] for x in all_items)),'template_groups':groups,'examples':{f'{l}:{t}':v for (l,t),v in examples.items()},'items':all_items,'policy':{'likely_label_trivia':'Direct terminology/label recall with short categorical answer; repair candidate unless context supplies meaningful analytic value.','likely_meaningful_discourse_effect':'Question explicitly asks effect/meaning/reason/interpretation and is normally appropriate at B1-C2.','likely_contextual_function':'Function question answered with explanatory proposition rather than isolated label; retain unless manual review finds ambiguity or bad grounding.','needs_manual_*':'Manual adjudication required; no automatic learner-content mutation.'},'quality_promotion':False}
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# Arabic B1-C2 semantic triage','',f"Candidates: **{len(all_items)}**",'', '| Level | Triage bucket | Count |','|---|---|---:|']
    for level in LEVELS:
        for bucket,n in sorted(level_counts[level].items()):lines.append(f'| {level.upper()} | {bucket} | {n} |')
    lines+=['','## Highest-frequency normalized prompt templates','', '| Level | Bucket | Count | Template |','|---|---|---:|---|']
    for g in sorted(groups,key=lambda x:-x['count'])[:80]:lines.append(f"| {g['level'].upper()} | {g['triage']} | {g['count']} | {g['prompt_template'].replace('|','\\|')} |")
    SUMMARY.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'candidate_count':len(all_items),'triage_counts':report['triage_counts'],'level_counts':level_counts},ensure_ascii=False))
if __name__=='__main__':main()
