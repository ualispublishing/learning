#!/usr/bin/env python3
"""Fresh, hash-bound Arabic B1-C2 metalinguistic/CEFR candidate triage."""
from __future__ import annotations
import hashlib, json, re, subprocess
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
INVENTORY=READING/'audit'/'arabic_metalinguistic_cefr_candidate_inventory_2026-08-30.json'
GATE0=READING/'audit'/'post_generation_gate0_2026-08-30.json'
OUT=READING/'audit'/'arabic_b1_c2_metalinguistic_cefr_triage_2026-08-30.json'
LEVELS=('b1','b2','c1','c2')
BARE_LABELS={'اسم','فعل','حرف','صفة','ضمير','ظرف','مصدر','أداة شرط','حرف جر','حرف عطف','أداة نفي','أداة استفهام','شرط','نفي','استدراك','عطف','سبب','نتيجة','توكيد'}
LABEL_PREFIX=re.compile(r'^(?:هي|هو)?\s*(?:أداة|حرف|اسم|فعل|صفة|ضمير|ظرف|مصدر)\b')
GUILLEMETS=re.compile(r'«([^»]+)»')
# Human-adjudicated shorthand quotes: the literal ellipses are not expected in prose,
# but the exact underlying construction must be present for the exception to apply.
SHORTHAND_RETAINS={
 ('ar-c1-u10-p06','q10'):'ليس حفظ مفردات أصعب، بل القدرة',
 ('ar-c2-u01-p06','q10'):'لا يكافأ بكثرة الأسماء ولا بغرابة الأمثلة',
}
def sha256(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git_blob(p): return subprocess.check_output(['git','hash-object',str(p)],cwd=ROOT,text=True).strip()
def tokens(t): return [x for x in re.split(r'\s+',t.strip()) if x]
def norm(t): return re.sub(r'\s+',' ',t.strip())
def marker_grounding(prompt,passage):
    quoted=[norm(x) for x in GUILLEMETS.findall(prompt)]
    if not quoted:return {'quoted':[],'grounded':True,'basis':'no_quoted_marker'}
    hits=[q for q in quoted if q in passage]
    return {'quoted':quoted,'matched_quotes':hits,'grounded':bool(hits),'basis':'at_least_one_exact_quote_in_passage' if hits else 'no_exact_quote_in_passage'}
def answer_is_bare_label(answer):
    a=norm(answer).rstrip('.؛،')
    return a in BARE_LABELS or (len(tokens(a))<=3 and bool(LABEL_PREFIX.search(a)))
def main():
    inventory=json.loads(INVENTORY.read_text(encoding='utf-8')); gate0=json.loads(GATE0.read_text(encoding='utf-8'))
    if gate0.get('status')!='PASS' or inventory.get('questions')!=3600: raise SystemExit('Fresh Gate0/inventory prerequisite failed')
    records={}; bindings={}
    for level in LEVELS:
        p=READING/'arabic'/level/'passages.jsonl'; rel=p.relative_to(ROOT).as_posix(); g=gate0['canonical_files'].get(rel)
        if not g or g.get('sha256')!=sha256(p) or g.get('git_blob')!=git_blob(p): raise SystemExit(f'{level}: canonical hash differs from Gate 0')
        rows=[json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
        if len(rows)!=60: raise SystemExit(f'{level}: expected 60 records')
        records[level]={r['id']:r for r in rows}; bindings[level]={'path':rel,'sha256':g['sha256'],'git_blob':g['git_blob']}
    candidates=[x for x in inventory['candidates'] if x.get('status')=='needs_adjudication' and x['level'].lower() in LEVELS]
    results=[]; counts=Counter(); by_level={l:Counter() for l in LEVELS}; shorthand=[]
    for c in candidates:
        level=c['level'].lower(); rec=records[level].get(c['passage_id'])
        if rec is None: raise SystemExit(f'missing {c["passage_id"]}')
        q=next((x for x in rec['questions'] if x['id']==c['question_id']),None); a=next((x for x in rec['answer_key'] if x['question_id']==c['question_id']),None)
        if q is None or a is None or q.get('prompt')!=c.get('prompt') or q.get('type')!=c.get('type'): raise SystemExit(f'candidate drift {c["passage_id"]}/{c["question_id"]}')
        prompt=q.get('prompt',''); answer=a.get('answer',''); passage=rec.get('text',''); grounding=marker_grounding(prompt,passage); key=(rec['id'],q['id'])
        reasons=[]; manual_adjudication=None
        if key in SHORTHAND_RETAINS:
            required=SHORTHAND_RETAINS[key]
            if required not in passage: raise SystemExit(f'shorthand retain lost exact support: {key}')
            manual_adjudication='RETAIN_ELLIPSIS_SHORTHAND_EXACT_CONSTRUCTION_CONFIRMED'; shorthand.append({'passage_id':key[0],'question_id':key[1],'required_passage_text':required})
        else:
            if 'الضمنية' in prompt or 'ضمني' in prompt: reasons.append('implicit_marker_claim_requires_manual_grounding')
            if not grounding['grounded']: reasons.append('quoted_marker_or_context_not_found_in_passage')
        if answer_is_bare_label(answer): reasons.append('answer_is_bare_grammatical_label')
        if len(tokens(answer))<4: reasons.append('answer_too_short_for_contextual_function_explanation')
        decision='MANUAL_REVIEW' if reasons else 'RETAIN_CONTEXTUAL_FUNCTION_ANALYSIS'
        counts[decision]+=1; by_level[level][decision]+=1
        results.append({'level':c['level'],'unit':c.get('unit'),'sequence':c.get('sequence'),'passage_id':rec['id'],'question_id':q['id'],'type':q.get('type'),'prompt':prompt,'answer':answer,'grounding':grounding,'decision':decision,'manual_adjudication':manual_adjudication,'review_reasons':reasons})
    report={'schema_version':2,'project_id':'LANG-A1C2','language':'arabic','levels':['B1','B2','C1','C2'],'date':'2026-08-30','scope':'Fresh hash-bound triage of all current B1-C2 candidates from the A1-C2 metalinguistic/CEFR inventory; no canonical edits by this script.','canonical_bindings':bindings,'candidate_count':len(results),'decision_counts':dict(counts),'by_level':{k:dict(v) for k,v in by_level.items()},'manual_review_count':counts['MANUAL_REVIEW'],'retained_contextual_count':counts['RETAIN_CONTEXTUAL_FUNCTION_ANALYSIS'],'adjudicated_ellipsis_shorthand_retain_count':len(shorthand),'adjudicated_ellipsis_shorthand_retains':shorthand,'criteria':{'retain':'Grounded contextual function/argument analysis with explanatory answer; two explicit human-adjudicated ellipsis shorthand forms are retained only while their exact underlying passage constructions remain present.','manual_review':'Any non-adjudicated grounding failure, implicit-marker claim, bare grammatical-label answer, or too-short answer.'},'historical_evidence_policy':'2026-08-23 B1-C2 audits may guide review but cannot supply current approval because their corpus bindings differ from current Gate 0.','results':results,'quality_promotion':False,'release_claim':False}
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps({k:v for k,v in report.items() if k!='results'},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
