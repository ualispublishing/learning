import hashlib, json, re, unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/french/a1/passages.jsonl'; LEX=ROOT/'reading/lexicons/french.jsonl'; PRIOR=ROOT/'reading/audit/french_a1_review_integrity_postrepair_2026-08-20.json'; OUT=ROOT/'reading/audit/french_a1_review_visibility_allsurfaces_2026-08-20.json'
EXPECTED='714cf8d41df917d2deb745f1cd9e82586a75f59cdaa4bff2eb494144a5345037'
def norm(s):
 s=unicodedata.normalize('NFC',str(s or '')).replace('’',"'").replace('‘',"'").casefold().strip(); return re.sub(r"^[^\w]+|[^\w]+$",'',s,flags=re.UNICODE)
def has_token(surface,key): return bool(re.search(r'(?<!\w)'+re.escape(key)+r'(?!\w)',norm(surface)))
def main():
 bound=hashlib.sha256(PATH.read_bytes()).hexdigest()
 if bound!=EXPECTED: raise SystemExit(f'hash drift {bound}')
 rows={r['id']:r for r in [json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]}; lex={r['id']:r for r in [json.loads(x) for x in LEX.read_text(encoding='utf-8').splitlines() if x.strip()]}; prior=json.loads(PRIOR.read_text(encoding='utf-8'))
 findings=[]; resolved=[]
 for old in prior['review_visibility_findings']:
  p=rows[old['passage_id']]; tid=old['target_id']; lr=lex.get(tid,{}); keys={norm(old.get('form')),norm(lr.get('form')),norm(lr.get('match_form')),norm(lr.get('lemma'))}-{''}
  surfaces=[('title',p.get('title','')),('text',p.get('text',''))]
  targeted=[]
  for q in p.get('questions',[]):
   surfaces.append((f"question:{q.get('id')}:prompt",q.get('prompt','')))
   for i,opt in enumerate(q.get('options',[]) or []): surfaces.append((f"question:{q.get('id')}:option:{i}",opt))
   if tid in q.get('target_ids',[]): targeted.append(q.get('id'))
  for a in p.get('answer_key',[]):
   surfaces.append((f"answer:{a.get('question_id')}:answer",a.get('answer',''))); surfaces.append((f"answer:{a.get('question_id')}:explanation",a.get('explanation','')))
  hits=[]
  for label,s in surfaces:
   matched=[k for k in keys if has_token(s,k)]
   if matched: hits.append({'surface':label,'matched_forms':matched,'text':s})
  item={**old,'lexicon_keys':sorted(keys),'explicit_targeted_question_ids':targeted,'exact_surface_hits':hits}
  if hits or targeted: resolved.append({**item,'status':'VISIBLE_ON_LEARNER_SURFACE_OR_TARGETED_TASK'})
  else: findings.append({**item,'status':'NO_EXACT_LEMMA_FORM_ON_ANY_LEARNER_SURFACE_NEEDS_MORPHOLOGY_OR_SEMANTIC_ADJUDICATION'})
 out={'schema_version':1,'date':'2026-08-20','language':'fr','level':'A1','bound_sha256':bound,'prior_candidate_count':len(prior['review_visibility_findings']),'resolved_by_all_surface_exact_scan_count':len(resolved),'remaining_candidate_count':len(findings),'resolved':resolved,'remaining':findings,'limitations':'Exact-form/lemma scan only. Remaining candidates may still be valid via inflected morphology or non-token semantic/task representation; no metadata is mutated automatically.','release_effect':'French remains REOPEN_REQUIRED.'}
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps({'resolved':len(resolved),'remaining':len(findings)},ensure_ascii=False))
if __name__=='__main__': main()
