#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/b1/passages.jsonl'
REPORT=ROOT/'reading/audit/arabic_b1_u01_p01_msa_fix_integrated_2026-08-23.json'
EXPECTED='cbe9e70e07543c3ce9080fb375af6468cfbd2d3c'
OLD_PROMPT='ما دلالة «حتى إن» في «حتى إن كانت الإجابة لا الآن»؟'
OLD_ANSWER='تفيد أن وضوح القرار يظل مهمًا حتى في الحالة التي تكون فيها النتيجة عدم التسجيل الآن.'
NEW_PROMPT='ما دلالة «حتى إن» في هذه الجملة: يظل وضوح القرار مهمًا حتى إن كانت الإجابة «لا، ليس الآن»؟'
NEW_ANSWER='تفيد أن وضوح القرار يظل مهمًا حتى في الحالة التي تكون فيها الإجابة «لا، ليس الآن».'
NEW_EXPLANATION='«حتى إن» تضيف معنى التنازل هنا: تبقى الفكرة صحيحة في هذه الحالة أيضًا.'
def blob():return subprocess.check_output(['git','hash-object',str(PATH)],text=True).strip()
def load():return [json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
def dump(rows):PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
def main():
 before=blob()
 if before!=EXPECTED:raise SystemExit(f'unexpected B1 blob {before}')
 rows=load();r=next(x for x in rows if x.get('id')=='ar-b1-u01-p01');q=next(x for x in r['questions'] if x.get('id')=='q7');a=next(x for x in r['answer_key'] if x.get('question_id')=='q7')
 if q.get('prompt')!=OLD_PROMPT or a.get('answer')!=OLD_ANSWER:raise SystemExit('q7 precondition mismatch')
 q['prompt']=NEW_PROMPT;a['answer']=NEW_ANSWER;a['explanation']=NEW_EXPLANATION;r['revision']=max(int(r.get('revision') or 0),4)+1
 qm=r.setdefault('quality',{});qm['answer_key_check']='pending';qm['linguistic_review']='pending';qm['pedagogical_review']='pending';qm['status']='draft';notes=qm.setdefault('notes',[]);note='Integrated independently adjudicated B1 U1 P1 q7 MSA repair from PR #16 on 2026-08-23; final current-corpus regression pending.'
 if note not in notes:notes.append(note)
 dump(rows);after=blob();report={'schema_version':1,'date':'2026-08-23','source_pr':16,'passage_id':'ar-b1-u01-p01','question_id':'q7','input_blob':before,'output_blob':after,'before':{'prompt':OLD_PROMPT,'answer':OLD_ANSWER},'after':{'prompt':NEW_PROMPT,'answer':NEW_ANSWER,'explanation':NEW_EXPLANATION},'passage_text_changed':False,'status':'PASS_BOUNDED_REPAIR_NEEDS_REGRESSION'};REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
