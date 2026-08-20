import hashlib, json, re, unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/french/a1/passages.jsonl'; PRIOR=ROOT/'reading/audit/french_a1_review_visibility_allsurfaces_2026-08-20.json'; OUT=ROOT/'reading/audit/french_a1_review_visibility_morphology_2026-08-20.json'
EXPECTED='714cf8d41df917d2deb745f1cd9e82586a75f59cdaa4bff2eb494144a5345037'
VARIANTS={
 'fr-rank-0039':['voir','vois','voit','voyons','voyez','voient','vu','vue','vus','vues'],
 'fr-rank-0047':['venir','viens','vient','venons','venez','viennent','venu','venue','venus','venues'],
 'fr-rank-0060':['prendre','prends','prend','prenons','prenez','prennent','pris','prise','prises'],
 'fr-rank-0014':['faire','fais','fait','faisons','faites','font'],
 'fr-rank-0022':['dire','dis','dit','disons','dites','disent'],
 'fr-rank-0036':['devoir','dois','doit','devons','devez','doivent','dû','due','dus','dues'],
 'fr-rank-0043':['tout','toute','tous','toutes'],
}
def norm(s): return unicodedata.normalize('NFC',str(s or '')).replace('’',"'").replace('‘',"'").casefold()
def hit(surface,form): return bool(re.search(r'(?<!\w)'+re.escape(norm(form))+r'(?!\w)',norm(surface)))
def surfaces(p):
 out=[('title',p.get('title','')),('text',p.get('text',''))]
 for q in p.get('questions',[]):
  out.append((f"question:{q.get('id')}:prompt",q.get('prompt','')))
  for i,opt in enumerate(q.get('options',[]) or []): out.append((f"question:{q.get('id')}:option:{i}",opt))
 for a in p.get('answer_key',[]): out.append((f"answer:{a.get('question_id')}:answer",a.get('answer',''))); out.append((f"answer:{a.get('question_id')}:explanation",a.get('explanation','')))
 return out
def main():
 bound=hashlib.sha256(PATH.read_bytes()).hexdigest()
 if bound!=EXPECTED: raise SystemExit(f'hash drift {bound}')
 rows={r['id']:r for r in [json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]}; prior=json.loads(PRIOR.read_text(encoding='utf-8'))
 resolved=[]; remaining=[]
 for item in prior['remaining']:
  tid=item['target_id']; forms=VARIANTS.get(tid,[item['form']]); hits=[]
  for label,s in surfaces(rows[item['passage_id']]):
   matched=[f for f in forms if hit(s,f)]
   if matched: hits.append({'surface':label,'matched_forms':matched,'text':s})
  rec={**item,'morphology_forms_checked':forms,'morphology_surface_hits':hits}
  if hits: resolved.append({**rec,'status':'VISIBLE_VIA_HIGH_CONFIDENCE_INFLECTED_OR_VARIANT_FORM'})
  else: remaining.append({**rec,'status':'NO_EXACT_OR_HIGH_CONFIDENCE_VARIANT_ON_ANY_LEARNER_SURFACE'})
 out={'schema_version':1,'date':'2026-08-20','language':'fr','level':'A1','bound_sha256':bound,'input_candidate_count':len(prior['remaining']),'resolved_by_high_confidence_morphology_count':len(resolved),'remaining_candidate_count':len(remaining),'resolved':resolved,'remaining':remaining,'method_note':'Variant map is intentionally narrow and high-confidence for the specific flagged verbs plus tout; it does not attempt general French lemmatization. Non-inflecting remaining forms have therefore received both exact all-surface and targeted-task checks.','release_effect':'French remains REOPEN_REQUIRED; no metadata changed by this diagnostic.'}
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps({'resolved':len(resolved),'remaining':len(remaining)},ensure_ascii=False))
if __name__=='__main__': main()
