#!/usr/bin/env python3
import json,re,subprocess,unicodedata
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FILES={"a1":ROOT/'reading/arabic/a1/passages.jsonl',"a2":ROOT/'reading/arabic/a2/passages.jsonl'}
EXPECTED={"a1":"cd963e0be0a89bec074aa800cc63188d770b7c3f","a2":"109fc63c940fc5a06d1c19328b914c5e09097d00"}
PRE=ROOT/'reading/audit/arabic_a1_a2_final_validation_post_linkage_2026-08-23.json'
CLOSURE=ROOT/'reading/audit/arabic_a1_a2_final_semantic_closure_2026-08-23.json'
OUT=ROOT/'reading/audit/arabic_a1_a2_final_postsemantic_validation_2026-08-23.json'
WORD_BANDS={"a1":(90,140),"a2":(140,220)}
BANNED_TYPES={"grammar_category","grammar_function","person_form","morphology_label","syntax_label"}
BANNED_FRAGMENTS=[
 'بعد قليل كانت ليلى في المنزل مرة أخرى','كان الكتاب مع حقيبتها','هنا، مع حقيبتها',
 'أول شيء تفعله هو إخراج الدفتر والقلم','كم طماطم تحتاج الأم؟','قرب الثلاجة أو في مكانها',
 'في الجهة المقابلة للمقدمة أو قدام الشيء','تنتظر، ثم تشكر المدير','يُشعر ليلى بأنه أبرد',
 'إدخال الكرة بطريقة تزيد نتيجة الفريق','المستوى المبتدئ الأول','لا تتعارض بلا خطة',
 'يجبرني على استخدام ما تعلمته','أنشطة وجمهورًا مختلفين','إلى الطقس أو الفعل المتكرر',
 'إن إحداهما «أصح» من الأخرى','إلى ماذا تشير «إحداهما»؟','ليس دائمًا الاختيار الذي يحل المشكلة أفضل',
 'وقت الاتصال','المستوى المبتدئ الثاني'
]
LATIN=re.compile(r'[A-Za-z]')
DIAC=re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]')
WORD=re.compile(r'[\u0621-\u064A]+')
PRO=('و','ف','ب','ك','ل');NSUF=('هما','هم','هن','كما','كم','كن','نا','ها','ه','ك','ي','ات','ون','ين','ان');VPRE=('أ','ا','ن','ي','ت');VSUF=('ون','ين','ان','وا','نا','تم','تن','ن','ت')

def blob(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def load(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def norm(s):return DIAC.sub('',unicodedata.normalize('NFKC',str(s or '')).replace('ـ','')).replace('ٱ','ا')
def toks(s):return WORD.findall(norm(s))
def nominal(tok):
    out={tok};front={tok}
    for _ in range(2):
        nxt=set()
        for x in front:
            for p in PRO:
                if x.startswith(p) and len(x)>2:nxt.add(x[1:])
            if x.startswith('ال') and len(x)>4:nxt.add(x[2:])
        out|=nxt;front=nxt
    exp=set(out)
    for x in list(out):
        for s in NSUF:
            if x.endswith(s) and len(x)-len(s)>=2:exp.add(x[:-len(s)])
        if x.endswith('ا') and len(x)>3:exp.add(x[:-1])
    return exp
def vcores(tok):
    out=set(nominal(tok))
    for x in list(out):
        if len(x)>=4 and x[0] in VPRE:out.add(x[1:])
    for x in list(out):
        for s in VSUF:
            if x.endswith(s) and len(x)-len(s)>=3:out.add(x[:-len(s)])
    return {x for x in out if len(x)>=2}
def forms(t):
    vals=[t.get('form','')]
    for p in re.split(r'[/؛;،,]|\bor\b',str(t.get('lemma') or '')):
        if re.search(r'[\u0621-\u064A]',p):vals.append(p.strip())
    return list(dict.fromkeys(norm(x) for x in vals if norm(x)))
def supported(text,t):
    fs=forms(t);isverb='verb' in str(t.get('part_of_speech') or '').lower();hits=[]
    for tok in toks(text):
        kind=None
        if tok in fs:kind='exact_or_lemma'
        elif any(nominal(tok)&nominal(f) for f in fs):kind='nominal_or_orthographic'
        elif isverb and any(vcores(tok)&vcores(f) for f in fs):kind='verbal_inflection_or_lemma_alternation'
        if kind:hits.append({'token':tok,'kind':kind})
    return hits
def wc(text):return len(re.findall(r'\S+',str(text)))
def sc(text):return sum(str(text).count(x) for x in ('.','؟','!','۔'))
def add(errors,code,**kw):errors.append({'code':code,**kw})
def learner_strings(r):
    out=[r.get('title',''),r.get('text','')]
    for q in r.get('questions',[]):out.append(q.get('prompt',''));out.extend(q.get('options',[]) or [])
    for a in r.get('answer_key',[]):out.extend([a.get('answer',''),a.get('explanation','')])
    return out

def main():
    actual={k:blob(v) for k,v in FILES.items()}
    report={'schema_version':1,'date':'2026-08-23','scope':'Final Arabic A1+A2 post-semantic validation','expected_blobs':EXPECTED,'actual_blobs':actual,'hard_errors':[],'warnings':[],'stats':{},'quality_promotion':False}
    errors=report['hard_errors']
    if actual!=EXPECTED:add(errors,'blob_mismatch',expected=EXPECTED,actual=actual)
    pre=json.loads(PRE.read_text(encoding='utf-8'))
    closure=json.loads(CLOSURE.read_text(encoding='utf-8'))
    if pre.get('hard_error_count')!=0 or pre.get('diagnostic_ledger',{}).get('unresolved')!=0:
        add(errors,'presemantic_ledger_not_clean',hard_error_count=pre.get('hard_error_count'),unresolved=pre.get('diagnostic_ledger',{}).get('unresolved'))
    if pre.get('diagnostic_ledger',{}).get('original_diagnostics')!=321:add(errors,'diagnostic_ledger_size',actual=pre.get('diagnostic_ledger',{}).get('original_diagnostics'))
    if closure.get('input_blobs')!=pre.get('input_blobs'):add(errors,'closure_input_not_presemantic_validated',closure_input=closure.get('input_blobs'),validated_input=pre.get('input_blobs'))
    if closure.get('output_blobs')!=EXPECTED:add(errors,'closure_output_blob_mismatch',closure_output=closure.get('output_blobs'),expected=EXPECTED)
    if closure.get('lexical_realization_deltas') not in ([],None):add(errors,'semantic_closure_lexical_delta',deltas=closure.get('lexical_realization_deltas'))
    if closure.get('quality_promotion') is not False:add(errors,'semantic_closure_promoted_quality')
    expected_assessment_links={(x['passage_id'],x['target_id']):set(x['question_ids']) for x in pre.get('assessment_review_linkage',{}).get('checks',[])}
    seen_assessment_links={}
    global_strings=[]
    for level,path in FILES.items():
        rows=load(path);intro={};qtotal=atotal=clozes=reviews=assessment_reviews=0;qtypes=Counter()
        if len(rows)!=60:add(errors,'passage_count',level=level,actual=len(rows),expected=60)
        for r in rows:
            for t in r.get('new_lexical_targets',[]):
                if isinstance(t,dict) and t.get('id'):
                    if t['id'] in intro:add(errors,'duplicate_new_target_id',level=level,target_id=t['id'])
                    else:intro[t['id']]={'sequence':r.get('sequence'),'passage_id':r.get('id'),'target':t}
        for i,r in enumerate(rows,1):
            rid=r.get('id');unit=(i-1)//6+1;p=(i-1)%6+1;eid=f'ar-{level}-u{unit:02d}-p{p:02d}'
            if r.get('sequence')!=i:add(errors,'sequence',passage_id=rid,expected=i,actual=r.get('sequence'))
            if r.get('unit')!=unit:add(errors,'unit',passage_id=rid,expected=unit,actual=r.get('unit'))
            if rid!=eid:add(errors,'id',passage_id=rid,expected=eid)
            if r.get('language')!='ar':add(errors,'language',passage_id=rid,actual=r.get('language'))
            if str(r.get('cefr','')).lower()!=level:add(errors,'cefr',passage_id=rid,expected=level,actual=r.get('cefr'))
            text=r.get('text','');lo,hi=WORD_BANDS[level]
            if not lo<=wc(text)<=hi:add(errors,'word_band',passage_id=rid,count=wc(text),band=[lo,hi])
            if r.get('word_count')!=wc(text):add(errors,'word_count_metadata',passage_id=rid,metadata=r.get('word_count'),calculated=wc(text))
            if r.get('sentence_count')!=sc(text):add(errors,'sentence_count_metadata',passage_id=rid,metadata=r.get('sentence_count'),calculated=sc(text))
            qs=r.get('questions',[]);ans=r.get('answer_key',[]);qtotal+=len(qs);atotal+=len(ans)
            if len(qs)!=10:add(errors,'question_count',passage_id=rid,actual=len(qs))
            if len(ans)!=10:add(errors,'answer_count',passage_id=rid,actual=len(ans))
            if [q.get('id') for q in qs]!=[f'q{x}' for x in range(1,11)]:add(errors,'question_ids',passage_id=rid)
            if [a.get('id') for a in ans]!=[f'a{x}' for x in range(1,11)]:add(errors,'answer_ids',passage_id=rid)
            prompts=[re.sub(r'\s+',' ',str(q.get('prompt',''))).strip() for q in qs]
            dup=[x for x,n in Counter(prompts).items() if x and n>1]
            if dup:add(errors,'duplicate_prompts',passage_id=rid,prompts=dup)
            amap={a.get('question_id'):a for a in ans}
            for q in qs:
                qid=q.get('id');qt=q.get('type');qtypes[qt]+=1;a=amap.get(qid)
                if not a:add(errors,'missing_answer',passage_id=rid,question_id=qid);continue
                if q.get('answer_id')!=a.get('id'):add(errors,'qa_link',passage_id=rid,question_id=qid)
                if qt in BANNED_TYPES:add(errors,'formal_metalinguistic_type',passage_id=rid,question_id=qid,type=qt,prompt=q.get('prompt'))
                tids=q.get('target_ids',[]) or []
                if not isinstance(tids,list):add(errors,'target_ids_not_list',passage_id=rid,question_id=qid);tids=[]
                for tid in tids:
                    ti=intro.get(tid)
                    if not ti:add(errors,'unknown_question_target',passage_id=rid,question_id=qid,target_id=tid)
                    elif ti['sequence']>i:add(errors,'future_question_target',passage_id=rid,question_id=qid,target_id=tid,introduced=ti['sequence'])
                if qt=='cloze_transfer':
                    clozes+=1;blanks=str(q.get('prompt','')).count('_____');parts=[x.strip() for x in re.split(r'[؛;]',str(a.get('answer',''))) if x.strip()]
                    if blanks!=len(parts):add(errors,'cloze_blank_key_mismatch',passage_id=rid,question_id=qid,blanks=blanks,parts=len(parts),answer=a.get('answer'))
                    if any(re.search(r'[.؟!۔]$',x) for x in parts):add(errors,'cloze_terminal_punctuation',passage_id=rid,question_id=qid,parts=parts)
            for t in r.get('new_lexical_targets',[]):
                if not isinstance(t,dict):add(errors,'new_target_not_object',passage_id=rid);continue
                hits=supported(text,t);decl=t.get('exposures_in_text')
                if not hits:add(errors,'new_target_no_supported_realization',passage_id=rid,target_id=t.get('id'),form=t.get('form'),lemma=t.get('lemma'))
                if isinstance(decl,int) and decl!=len(hits):add(errors,'new_target_exposure_count',passage_id=rid,target_id=t.get('id'),declared=decl,supported=len(hits))
                m=re.match(r'ar-r(\d+)$',str(t.get('id','')))
                if m and t.get('source_rank')!=int(m.group(1)):add(errors,'source_rank_id_mismatch',passage_id=rid,target_id=t.get('id'),source_rank=t.get('source_rank'))
                if not str(t.get('intended_sense','')).strip():add(errors,'empty_intended_sense',passage_id=rid,target_id=t.get('id'))
            for t in r.get('review_lexical_targets',[]):
                if not isinstance(t,dict):add(errors,'review_target_not_object',passage_id=rid);continue
                reviews+=1;tid=t.get('id');ti=intro.get(tid);rep=t.get('representation')
                if not ti:add(errors,'unknown_review_target',passage_id=rid,target_id=tid);continue
                if ti['sequence']>=i:add(errors,'review_not_after_introduction',passage_id=rid,target_id=tid,introduced=ti['sequence'])
                if t.get('review_stage') not in {'R1','R2','R3','R4'}:add(errors,'invalid_review_stage',passage_id=rid,target_id=tid,stage=t.get('review_stage'))
                if rep=='running_text':
                    if not supported(text,ti['target']):add(errors,'running_text_review_no_supported_realization',passage_id=rid,target_id=tid)
                else:
                    assessment_reviews+=1
                    linked={q.get('id') for q in qs if tid in (q.get('target_ids',[]) or [])}
                    if not linked:add(errors,'assessment_only_review_without_question_link',passage_id=rid,target_id=tid,representation=rep)
                    seen_assessment_links[(rid,tid)]=linked
            for s in learner_strings(r):
                global_strings.append((rid,str(s)))
                if LATIN.search(str(s)):add(errors,'latin_script_in_learner_facing_arabic',passage_id=rid,sample=str(s)[:160]);break
            qm=r.get('quality',{})
            if qm.get('status')!='draft':add(errors,'quality_status_not_draft',passage_id=rid,status=qm.get('status'))
            for gate in ('answer_key_check','coverage_check','linguistic_review','pedagogical_review','schema_check'):
                if qm.get(gate)!='pending':add(errors,'quality_gate_not_pending',passage_id=rid,gate=gate,value=qm.get(gate))
        if qtotal!=600:add(errors,'total_questions',level=level,actual=qtotal)
        if atotal!=600:add(errors,'total_answers',level=level,actual=atotal)
        report['stats'][level]={'passages':len(rows),'questions':qtotal,'answers':atotal,'clozes':clozes,'new_targets':len(intro),'review_targets':reviews,'assessment_only_reviews':assessment_reviews,'question_type_counts':dict(qtypes)}
    if seen_assessment_links!=expected_assessment_links:
        add(errors,'assessment_review_linkage_changed',expected={f'{k[0]}::{k[1]}':sorted(v) for k,v in expected_assessment_links.items()},actual={f'{k[0]}::{k[1]}':sorted(v) for k,v in seen_assessment_links.items()})
    corpus='\n'.join(s for _,s in global_strings)
    for frag in BANNED_FRAGMENTS:
        if frag in corpus:add(errors,'semantic_regression_fragment',fragment=frag)
    report['diagnostic_ledger']={'original_diagnostics':321,'unresolved_before_semantic_closure':0,'semantic_closure_lexical_deltas':closure.get('lexical_realization_deltas',[]),'unresolved_after_semantic_closure':0 if not [e for e in errors if e['code'].startswith(('new_target_','running_text_review_','assessment_only_review_'))] else None}
    report['semantic_closure']={'repair_operation_count':closure.get('repair_operation_count'),'changed_passage_count':closure.get('changed_passage_count'),'banned_regression_fragments_checked':len(BANNED_FRAGMENTS)}
    report['hard_error_count']=len(errors);report['warning_count']=len(report['warnings']);report['status']='PASS_ZERO_UNRESOLVED_POSTSEMANTIC_DRAFT_QUALITY' if not errors else 'FAIL'
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'hard_error_count':report['hard_error_count'],'warning_count':report['warning_count'],'stats':report['stats'],'ledger':report['diagnostic_ledger'],'sample_errors':errors[:25]},ensure_ascii=False))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
