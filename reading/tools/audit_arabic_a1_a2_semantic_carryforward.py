#!/usr/bin/env python3
import json,re,subprocess
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FILES={"a1":ROOT/'reading/arabic/a1/passages.jsonl',"a2":ROOT/'reading/arabic/a2/passages.jsonl'}
EXPECTED={"a1":"cd963e0bab42ec8cbf0f07e04f09309a5dc24ffa","a2":"109fc63c8cba362ca6c08c4fd81c3f0b0efdd316"}
PRE=ROOT/'reading/audit/arabic_a1_a2_final_validation_post_linkage_2026-08-23.json'
CLOSURE=ROOT/'reading/audit/arabic_a1_a2_final_semantic_closure_2026-08-23.json'
OUT=ROOT/'reading/audit/arabic_a1_a2_semantic_carryforward_validation_2026-08-23.json'
BANNED_TYPES={"grammar_category","grammar_function","person_form","morphology_label","syntax_label"}
BANNED_FRAGMENTS=[
 'بعد قليل كانت ليلى في المنزل مرة أخرى.','كان الكتاب مع حقيبتها.','تضع كتابها هنا، مع حقيبتها.',
 'أول شيء تفعله هو إخراج الدفتر والقلم.','كم طماطم تحتاج الأم؟','قرب الثلاجة أو في مكانها.',
 'في الجهة المقابلة للمقدمة أو قدام الشيء.','تنتظر، ثم تشكر المدير وتعود إلى صفها.',
 'يُشعر ليلى بأنه أبرد','إدخال الكرة بطريقة تزيد نتيجة الفريق.','المستوى المبتدئ الأول',
 'لا تتعارض بلا خطة.','يجبرني على استخدام ما تعلمته','أنشطة وجمهورًا مختلفين',
 'إلى الطقس أو الفعل المتكرر في احتفالات العائلة','إن إحداهما «أصح» من الأخرى',
 'إلى ماذا تشير «إحداهما»؟','ليس دائمًا الاختيار الذي يحل المشكلة أفضل.','وقت الاتصال','المستوى المبتدئ الثاني'
]
LATIN=re.compile(r'[A-Za-z]')

def blob(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def load(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def wc(s):return len(re.findall(r'\S+',str(s)))
def sc(s):return sum(str(s).count(x) for x in ('.','؟','!','۔'))
def add(errors,code,**kw):errors.append({'code':code,**kw})
def learner_strings(r):
    out=[r.get('title',''),r.get('text','')]
    for q in r.get('questions',[]):out.append(q.get('prompt',''));out.extend(q.get('options',[]) or [])
    for a in r.get('answer_key',[]):out.extend([a.get('answer',''),a.get('explanation','')])
    return out

def main():
    errors=[];warnings=[];actual={k:blob(v) for k,v in FILES.items()}
    pre=json.loads(PRE.read_text(encoding='utf-8'));closure=json.loads(CLOSURE.read_text(encoding='utf-8'))
    if actual!=EXPECTED:add(errors,'blob_mismatch',expected=EXPECTED,actual=actual)
    if pre.get('hard_error_count')!=0:add(errors,'presemantic_not_clean',hard_error_count=pre.get('hard_error_count'))
    ledger=pre.get('diagnostic_ledger',{})
    if ledger.get('original_diagnostics')!=321 or ledger.get('unresolved')!=0:add(errors,'presemantic_ledger_not_resolved',ledger=ledger)
    if closure.get('input_blobs')!=pre.get('input_blobs'):add(errors,'closure_input_not_validated_presemantic_blob',closure_input=closure.get('input_blobs'),validated=pre.get('input_blobs'))
    if closure.get('output_blobs')!=EXPECTED:add(errors,'closure_output_mismatch',closure_output=closure.get('output_blobs'),expected=EXPECTED)
    if closure.get('lexical_realization_deltas')!=[]:add(errors,'lexical_realization_delta',deltas=closure.get('lexical_realization_deltas'))
    if closure.get('repair_operation_count')!=27 or closure.get('changed_passage_count')!=19:add(errors,'closure_scope_changed',repairs=closure.get('repair_operation_count'),passages=closure.get('changed_passage_count'))
    stats={};all_strings=[]
    for level,path in FILES.items():
        rows=load(path);qtotal=atotal=clozes=0
        if len(rows)!=60:add(errors,'passage_count',level=level,actual=len(rows))
        for i,r in enumerate(rows,1):
            rid=r.get('id');unit=(i-1)//6+1;p=(i-1)%6+1
            if rid!=f'ar-{level}-u{unit:02d}-p{p:02d}':add(errors,'id_order',level=level,sequence=i,id=rid)
            if r.get('sequence')!=i:add(errors,'sequence',passage_id=rid,actual=r.get('sequence'),expected=i)
            if r.get('unit')!=unit:add(errors,'unit',passage_id=rid,actual=r.get('unit'),expected=unit)
            if r.get('language')!='ar' or str(r.get('cefr','')).lower()!=level:add(errors,'language_cefr',passage_id=rid,language=r.get('language'),cefr=r.get('cefr'))
            if r.get('word_count')!=wc(r.get('text','')):add(errors,'word_count_metadata',passage_id=rid,metadata=r.get('word_count'),calculated=wc(r.get('text','')))
            if r.get('sentence_count')!=sc(r.get('text','')):add(errors,'sentence_count_metadata',passage_id=rid,metadata=r.get('sentence_count'),calculated=sc(r.get('text','')))
            qs=r.get('questions',[]);ans=r.get('answer_key',[]);qtotal+=len(qs);atotal+=len(ans)
            if len(qs)!=10 or len(ans)!=10:add(errors,'qa_count',passage_id=rid,questions=len(qs),answers=len(ans))
            if [q.get('id') for q in qs]!=[f'q{x}' for x in range(1,11)]:add(errors,'question_ids',passage_id=rid)
            if [a.get('id') for a in ans]!=[f'a{x}' for x in range(1,11)]:add(errors,'answer_ids',passage_id=rid)
            amap={a.get('question_id'):a for a in ans};prompts=[]
            for q in qs:
                prompts.append(re.sub(r'\s+',' ',str(q.get('prompt',''))).strip());a=amap.get(q.get('id'))
                if not a:add(errors,'missing_answer',passage_id=rid,question_id=q.get('id'))
                elif q.get('answer_id')!=a.get('id'):add(errors,'qa_link',passage_id=rid,question_id=q.get('id'))
                if q.get('type') in BANNED_TYPES:add(errors,'formal_metalinguistic_type',passage_id=rid,question_id=q.get('id'),type=q.get('type'),prompt=q.get('prompt'))
                if q.get('type')=='cloze_transfer':
                    clozes+=1;blanks=str(q.get('prompt','')).count('_____')
                    if blanks<1:add(errors,'cloze_without_blank',passage_id=rid,question_id=q.get('id'))
            dup=[p for p,n in Counter(prompts).items() if p and n>1]
            if dup:add(errors,'duplicate_prompt',passage_id=rid,prompts=dup)
            qm=r.get('quality',{})
            if qm.get('status')!='draft':add(errors,'quality_status',passage_id=rid,status=qm.get('status'))
            for gate in ('answer_key_check','coverage_check','linguistic_review','pedagogical_review','schema_check'):
                if qm.get(gate)!='pending':add(errors,'quality_gate',passage_id=rid,gate=gate,value=qm.get(gate))
            for s in learner_strings(r):
                all_strings.append((rid,str(s)))
                if LATIN.search(str(s)):add(errors,'latin_in_learner_arabic',passage_id=rid,sample=str(s)[:160]);break
        if qtotal!=600 or atotal!=600:add(errors,'level_totals',level=level,questions=qtotal,answers=atotal)
        stats[level]={'passages':len(rows),'questions':qtotal,'answers':atotal,'clozes':clozes}
    corpus='\n'.join(s for _,s in all_strings)
    for frag in BANNED_FRAGMENTS:
        if frag in corpus:add(errors,'semantic_regression_fragment',fragment=frag)
    report={'schema_version':1,'date':'2026-08-23','scope':'Arabic A1/A2 evidence-correct semantic carry-forward validation','expected_blobs':EXPECTED,'actual_blobs':actual,'presemantic_diagnostic_ledger':ledger,'semantic_closure':{'repair_operation_count':closure.get('repair_operation_count'),'changed_passage_count':closure.get('changed_passage_count'),'lexical_realization_deltas':closure.get('lexical_realization_deltas')},'stats':stats,'hard_error_count':len(errors),'hard_errors':errors,'warning_count':len(warnings),'warnings':warnings,'quality_promotion':False,'status':'PASS_ZERO_UNRESOLVED_POSTSEMANTIC_DRAFT_QUALITY' if not errors else 'FAIL'}
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'hard_errors':len(errors),'warnings':len(warnings),'stats':stats},ensure_ascii=False))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
