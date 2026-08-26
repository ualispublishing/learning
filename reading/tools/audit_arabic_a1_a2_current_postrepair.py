#!/usr/bin/env python3
import json,re,subprocess,unicodedata
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FILES={"a1":ROOT/'reading/arabic/a1/passages.jsonl',"a2":ROOT/'reading/arabic/a2/passages.jsonl'}
EXPECTED={"a1":"bf7f0a6023b1cb129c9328021892d93cb120fa38","a2":"90b6f2f334b689200c76b25c3b7b983f89230555"}
OUT=ROOT/'reading/audit/arabic_a1_a2_current_postrepair_audit_2026-08-23.json'
WORD_BANDS={"a1":(90,140),"a2":(140,220)}
BANNED_TYPES={"grammar_category","grammar_function","person_form","morphology_label","syntax_label"}
LATIN=re.compile(r'[A-Za-z]')
DIAC=re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]')
WORD=re.compile(r'[\u0621-\u064A]+')
PRO=('و','ف','ب','ك','ل')
NSUF=('هما','هم','هن','كما','كم','كن','نا','ها','ه','ك','ي','ات','ون','ين','ان')
VPRE=('أ','ا','ن','ي','ت')
VSUF=('ون','ين','ان','وا','نا','تم','تن','ن','ت')


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
def sent_count(text):return sum(str(text).count(x) for x in ('.','؟','!','۔'))
def word_count(text):return len(re.findall(r'\S+',str(text)))
def add(bucket,code,**kw):bucket.append({'code':code,**kw})
def learner_strings(r):
    out=[r.get('title',''),r.get('text','')]
    for q in r.get('questions',[]):out.append(q.get('prompt',''));out.extend(q.get('options',[]) or [])
    for a in r.get('answer_key',[]):out.extend([a.get('answer',''),a.get('explanation','')])
    return out

def main():
    actual={k:blob(v) for k,v in FILES.items()}
    if actual!=EXPECTED:raise SystemExit(f'Unexpected Arabic A1/A2 blobs: {actual}')
    report={'schema_version':1,'date':'2026-08-23','scope':'Arabic A1/A2 fresh post-repair independent audit','input_blobs':actual,'hard_errors':[],'warnings':[],'stats':{},'quality_promotion':False}
    all_new={}
    for level,path in FILES.items():
        rows=load(path);errors=report['hard_errors'];warnings=report['warnings'];qtotal=atotal=clozes=0;qtypes=Counter();new_ids=[];review_count=0
        if len(rows)!=60:add(errors,'passage_count',level=level,expected=60,actual=len(rows))
        intro={}
        for r in rows:
            for t in r.get('new_lexical_targets',[]):
                if isinstance(t,dict) and t.get('id'):
                    if t['id'] in intro:add(errors,'duplicate_new_target_id',level=level,target_id=t['id'],passages=[intro[t['id']]['passage_id'],r.get('id')])
                    else:intro[t['id']]={'sequence':r.get('sequence'),'passage_id':r.get('id'),'target':t}
        all_new[level]=intro
        for i,r in enumerate(rows,1):
            rid=r.get('id');unit=(i-1)//6+1;p=(i-1)%6+1;eid=f'ar-{level}-u{unit:02d}-p{p:02d}'
            if r.get('sequence')!=i:add(errors,'sequence',passage_id=rid,expected=i,actual=r.get('sequence'))
            if r.get('unit')!=unit:add(errors,'unit',passage_id=rid,expected=unit,actual=r.get('unit'))
            if rid!=eid:add(errors,'id',passage_id=rid,expected=eid)
            if r.get('language')!='ar':add(errors,'language',passage_id=rid,actual=r.get('language'))
            if str(r.get('cefr','')).lower()!=level:add(errors,'cefr',passage_id=rid,actual=r.get('cefr'))
            text=r.get('text','');wc=word_count(text);sc=sent_count(text);lo,hi=WORD_BANDS[level]
            if not lo<=wc<=hi:add(errors,'word_band',passage_id=rid,count=wc,band=[lo,hi])
            if r.get('word_count')!=wc:add(errors,'word_count_metadata',passage_id=rid,metadata=r.get('word_count'),calculated=wc)
            if r.get('sentence_count')!=sc:add(errors,'sentence_count_metadata',passage_id=rid,metadata=r.get('sentence_count'),calculated=sc)
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
                if q.get('answer_id')!=a.get('id'):add(errors,'qa_link',passage_id=rid,question_id=qid,question_answer_id=q.get('answer_id'),actual_answer_id=a.get('id'))
                if qt in BANNED_TYPES:add(errors,'formal_metalinguistic_type',passage_id=rid,question_id=qid,type=qt,prompt=q.get('prompt'))
                tids=q.get('target_ids',[]) or []
                if not isinstance(tids,list):add(errors,'target_ids_not_list',passage_id=rid,question_id=qid)
                else:
                    for tid in tids:
                        ti=intro.get(tid)
                        if not ti:add(errors,'unknown_question_target',passage_id=rid,question_id=qid,target_id=tid)
                        elif ti['sequence']>i:add(errors,'question_targets_future_item',passage_id=rid,question_id=qid,target_id=tid,introduced_sequence=ti['sequence'])
                if qt=='cloze_transfer':
                    clozes+=1;blanks=str(q.get('prompt','')).count('_____');parts=[x.strip() for x in re.split(r'[؛;]',str(a.get('answer',''))) if x.strip()]
                    if blanks!=len(parts):add(errors,'cloze_blank_key_mismatch',passage_id=rid,question_id=qid,blanks=blanks,parts=len(parts),answer=a.get('answer'))
                    if any(re.search(r'[.؟!۔]$',x) for x in parts):add(errors,'cloze_key_terminal_punctuation',passage_id=rid,question_id=qid,parts=parts)
            for t in r.get('new_lexical_targets',[]):
                if not isinstance(t,dict):add(errors,'new_target_not_object',passage_id=rid);continue
                new_ids.append(t.get('id'));hits=supported(text,t);decl=t.get('exposures_in_text')
                if not hits:add(errors,'new_target_no_supported_realization',passage_id=rid,target_id=t.get('id'),form=t.get('form'),lemma=t.get('lemma'))
                if isinstance(decl,int) and decl!=len(hits):add(errors,'new_target_exposure_count',passage_id=rid,target_id=t.get('id'),form=t.get('form'),declared=decl,supported=len(hits),hits=hits)
                if not str(t.get('intended_sense','')).strip():add(errors,'empty_intended_sense',passage_id=rid,target_id=t.get('id'))
                m=re.match(r'ar-r(\d+)$',str(t.get('id','')))
                if m and t.get('source_rank')!=int(m.group(1)):add(errors,'source_rank_id_mismatch',passage_id=rid,target_id=t.get('id'),source_rank=t.get('source_rank'))
            for t in r.get('review_lexical_targets',[]):
                if not isinstance(t,dict):add(errors,'review_target_not_object',passage_id=rid);continue
                review_count+=1;tid=t.get('id');ti=intro.get(tid)
                if not ti:add(errors,'unknown_review_target',passage_id=rid,target_id=tid)
                elif ti['sequence']>=i:add(errors,'review_not_after_introduction',passage_id=rid,target_id=tid,introduction_sequence=ti['sequence'])
                if t.get('representation')=='running_text':
                    base=ti['target'] if ti else {'form':t.get('form'),'lemma':t.get('form'),'part_of_speech':''};hits=supported(text,base)
                    if not hits:add(errors,'running_text_review_no_supported_realization',passage_id=rid,target_id=tid,form=t.get('form'))
                if t.get('review_stage') not in {'R1','R2','R3','R4'}:add(errors,'invalid_review_stage',passage_id=rid,target_id=tid,stage=t.get('review_stage'))
            for s in learner_strings(r):
                if LATIN.search(str(s)):
                    add(errors,'latin_script_in_learner_facing_arabic',passage_id=rid,sample=str(s)[:160]);break
            qmeta=r.get('quality',{})
            if qmeta.get('status')!='draft':add(errors,'quality_status_not_draft',passage_id=rid,status=qmeta.get('status'))
            for gate in ('answer_key_check','coverage_check','linguistic_review','pedagogical_review','schema_check'):
                if qmeta.get(gate)!='pending':add(errors,'quality_gate_not_pending',passage_id=rid,gate=gate,value=qmeta.get(gate))
        if qtotal!=600:add(errors,'total_questions',level=level,actual=qtotal)
        if atotal!=600:add(errors,'total_answers',level=level,actual=atotal)
        report['stats'][level]={'passages':len(rows),'questions':qtotal,'answers':atotal,'clozes':clozes,'new_targets':len(new_ids),'review_targets':review_count,'question_type_counts':dict(qtypes)}
    report['hard_error_count']=len(report['hard_errors']);report['warning_count']=len(report['warnings']);report['status']='PASS' if not report['hard_errors'] else 'FAIL'
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'hard_error_count':report['hard_error_count'],'stats':report['stats'],'sample_errors':report['hard_errors'][:30]},ensure_ascii=False))
    if report['hard_errors']:raise SystemExit(1)

if __name__=='__main__':main()
