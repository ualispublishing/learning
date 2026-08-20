import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl'; OUT=ROOT/'reading/audit/arabic_a1_u02_metalinguistic_refinement_2026-08-20.json'
EXPECTED='901cf1c84c19025112abd19b46efb6cd71f548ea537b1b65c20f84e36035d61a'
CHANGES={
 ('ar-a1-u02-p05','q7'):("إذا أردت السؤال عن طريقة الوصول، أي سؤال أنسب: «كيف نصل إلى المكتبة؟» أم «متى نصل إلى المكتبة؟»؟","إذا أردت السؤال عن طريقة الوصول، أي صيغة أنسب: «كيف نصل إلى المكتبة» أم «متى نصل إلى المكتبة»؟"),
 ('ar-a1-u02-p06','q9'):("إذا أردت السؤال عن طريقة ترتيب الوقت، أي سؤال أنسب: «كيف نرتب الوقت؟» أم «أين نرتب الوقت؟»؟","إذا أردت السؤال عن طريقة ترتيب الوقت، أي صيغة أنسب: «كيف نرتب الوقت» أم «أين نرتب الوقت»؟"),
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 before=sha(PATH)
 if before!=EXPECTED: raise SystemExit(f'hash drift {before}')
 rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]; done=[]
 for p in rows:
  for q in p.get('questions',[]):
   key=(p.get('id'),q.get('id'))
   if key not in CHANGES: continue
   old,new=CHANGES[key]
   if q.get('prompt')!=old: raise SystemExit(f'precondition mismatch {key}')
   q['prompt']=new; p['revision']=int(p.get('revision',0))+1; done.append({'passage_id':key[0],'question_id':key[1],'old_prompt':old,'new_prompt':new})
 if len(done)!=2: raise SystemExit(f'expected 2 refinements got {len(done)}')
 PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8'); after=sha(PATH)
 OUT.write_text(json.dumps({'schema_version':1,'date':'2026-08-20','language':'ar','level':'A1','unit':2,'status':'SELF_REVIEW_REFINEMENT_APPLIED_NEEDS_INDEPENDENT_REVIEW','before_sha256':before,'after_sha256':after,'refinements':done,'reason':'Removed nested question-mark punctuation from two operational كيف items; assessment meaning and answers unchanged.','release_effect':'No release effect; Arabic remains educator-blocked.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(after)
if __name__=='__main__': main()
