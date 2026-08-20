import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl'; OUT=ROOT/'reading/audit/arabic_a1_u03_metalinguistic_refinement_2026-08-20.json'; EXPECTED='135039f57304d847c015325b421748f038a4c731237e181cc49070970826f7c3'
C={
('ar-a1-u03-p03','q7'):("إذا كان الحليب بجانب الثلاجة، أي جملة أنسب: «الحليب عند الثلاجة» أم «الحليب أين الثلاجة»؟","إذا كان الحليب بجانب الثلاجة لا داخلها، أي جملة أنسب: «الحليب عند الثلاجة» أم «الحليب في الثلاجة»؟"),
('ar-a1-u03-p04','q6'):("إذا أردت معرفة سبب اختيار الماء، أي سؤال أنسب: «لماذا اخترت الماء؟» أم «أين اخترت الماء؟»؟","إذا أردت معرفة سبب اختيار الماء، أي صيغة أنسب: «لماذا اخترت الماء» أم «أين اخترت الماء»؟")}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 before=sha(PATH)
 if before!=EXPECTED: raise SystemExit(f'hash drift {before}')
 rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]; done=[]
 for p in rows:
  for q in p.get('questions',[]):
   k=(p['id'],q['id'])
   if k not in C: continue
   old,new=C[k]
   if q.get('prompt')!=old: raise SystemExit(f'precondition {k}')
   q['prompt']=new; p['revision']=int(p.get('revision',0))+1; done.append({'passage_id':k[0],'question_id':k[1],'old_prompt':old,'new_prompt':new})
 if len(done)!=2: raise SystemExit('expected 2')
 PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8'); after=sha(PATH)
 OUT.write_text(json.dumps({'schema_version':1,'date':'2026-08-20','language':'ar','level':'A1','unit':3,'status':'SELF_REVIEW_REFINEMENT_APPLIED_NEEDS_INDEPENDENT_REVIEW','before_sha256':before,'after_sha256':after,'refinements':done,'release_effect':'No release effect; Arabic remains educator-blocked.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(after)
if __name__=='__main__': main()
