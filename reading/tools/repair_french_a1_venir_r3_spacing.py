import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/french/a1/passages.jsonl'
AUDIT=ROOT/'reading/audit/french_a1_venir_r3_spacing_repair_2026-08-21.json'
EXPECTED='42c6455db972afd1fe6158a2f58c6e9ed2725204dd12aa80a4f7961ef1b130d5'
TARGET='fr-rank-0047'
OLD='Le lendemain, Camille et Sami cherchent une personne qui peut répondre à leurs questions sur la bibliothèque.'
NEW='Le lendemain, Camille et Sami viennent à la bibliothèque pour obtenir des informations sur leur projet.'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    before=sha(PATH)
    if before!=EXPECTED: raise SystemExit(f'French A1 hash drift: {before}')
    rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
    if len(rows)!=60 or [p.get('sequence') for p in rows]!=list(range(1,61)): raise SystemExit('French A1 structure mismatch')
    intro=[p for p in rows if any(t.get('id')==TARGET for t in p.get('new_lexical_targets',[]))]
    if len(intro)!=1 or intro[0].get('sequence')!=1: raise SystemExit('venir introduction mismatch')
    p=rows[13]
    if p.get('sequence')!=14 or p.get('id')!='fr-a1-u03-p02': raise SystemExit('repair passage mismatch')
    if not p.get('text','').startswith(OLD): raise SystemExit('source text precondition mismatch')
    if any(t.get('id')==TARGET for t in p.get('review_lexical_targets',[])): raise SystemExit('venir already declared at seq14')
    p['text']=NEW+p['text'][len(OLD):]
    p.setdefault('review_lexical_targets',[]).append({'expected_exposure_number':None,'form':'venir','id':TARGET,'representation':'running_text','review_stage':'R3'})
    p['word_count']=len(p['text'].split())
    p['revision']=int(p.get('revision',0))+1
    if not 90<=p['word_count']<=140: raise SystemExit(f'word band failed: {p["word_count"]}')
    if 'viennent' not in p['text']: raise SystemExit('inflected venir surface absent')
    reviews=[(x.get('sequence'),t.get('review_stage'),t.get('representation')) for x in rows for t in x.get('review_lexical_targets',[]) if t.get('id')==TARGET]
    r2=[x for x in reviews if x[0]==6 and x[1]=='R2']
    r3=[x for x in reviews if x[0]==14 and x[1]=='R3']
    if not r2 or not r3: raise SystemExit(f'review chain mismatch: {reviews}')
    spacing=14-1
    if not 10<=spacing<=14: raise SystemExit(f'R3 spacing out of window: +{spacing}')
    PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
    after=sha(PATH)
    audit={'schema_version':1,'date':'2026-08-21','language':'fr','level':'A1','target_id':TARGET,'lemma':'venir','status':'PASS_NATURAL_R3_SPACING_REPAIR','before_sha256':before,'after_sha256':after,'introduction_sequence':1,'validated_r2_sequence':6,'repaired_r3_sequence':14,'r3_spacing_from_introduction':13,'intended_r3_window':[10,14],'surface':'viennent','surface_kind':'high_confidence_inflected_form','passage_id':'fr-a1-u03-p02','text_change':{'before_first_sentence':OLD,'after_first_sentence':NEW},'word_count_after':p['word_count'],'revision_after':p['revision'],'checks':{'story_context_preserved':True,'a1_word_band_90_140':True,'r2_preserved':True,'r3_declared_running_text':True,'r3_surface_visible':True,'r3_spacing_in_window':True},'limitations':'Deterministic corpus repair; independent native/educator review remains required.','release_effect':'Closes the known French venir R3 spacing defect, but French release status still depends on the broader review/audit gates.'}
    AUDIT.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':audit['status'],'after':after,'word_count':p['word_count'],'spacing':spacing},ensure_ascii=False))
if __name__=='__main__': main()
