#!/usr/bin/env python3
"""Build fresh, hash-bound Arabic Gate B linguistic/naturalness review packets.

Read-only with respect to canonical passage content. Each packet line contains all
learner-facing passage/Q/A text needed for a passage-by-passage internal review.
Historical notes are inventoried but never treated as current approval.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
GATE0=READING/'audit'/'post_generation_gate0_2026-08-30.json'
OUT=READING/'audit'/'arabic_gate_b_naturalness_inventory_2026-08-30.json'
PACKET_DIR=READING/'audit'/'arabic_gate_b_packets_2026-08-30'
LEVELS=('a1','a2','b1','b2','c1','c2')

def sha256_bytes(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def learner_payload(r:dict)->dict:
    ans={a.get('question_id'):a for a in r.get('answer_key',[])}
    qa=[]
    for q in r.get('questions',[]):
        a=ans.get(q.get('id'),{})
        qa.append({'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get('answer'),'explanation':a.get('explanation','')})
    return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':qa}
def main():
    gate=json.loads(GATE0.read_text(encoding='utf-8'))
    if gate.get('status')!='PASS' or gate.get('canonical_totals',{}).get('arabic')!=360:
        raise SystemExit('Fresh Gate 0 PASS for Arabic 360 required')
    PACKET_DIR.mkdir(parents=True,exist_ok=True)
    levels={}; all_ids=[]; totalq=totala=0
    for level in LEVELS:
        p=READING/'arabic'/level/'passages.jsonl'; rel=p.relative_to(ROOT).as_posix(); data=p.read_bytes(); g=gate['canonical_files'].get(rel)
        if not g or g.get('sha256')!=sha256_bytes(data): raise SystemExit(f'{level}: Gate0 hash mismatch')
        rows=[json.loads(x) for x in data.decode('utf-8').splitlines() if x.strip()]
        if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)): raise SystemExit(f'{level}: layout drift')
        packet=[]; historical=0; qcount=acount=0; record_hashes={}
        for r in rows:
            if r.get('id') in all_ids: raise SystemExit(f'duplicate id {r.get("id")}')
            all_ids.append(r.get('id'))
            qs=r.get('questions',[]); aa=r.get('answer_key',[]); qcount+=len(qs); acount+=len(aa)
            if len(qs)!=10 or len(aa)!=10: raise SystemExit(f'{r.get("id")}: expected 10Q/10A')
            notes='\n'.join(r.get('quality',{}).get('notes',[]))
            has_hist=('naturalness review' in notes.lower() or 'naturalness' in notes.lower())
            historical+=int(has_hist)
            payload=learner_payload(r)
            payload['historical_naturalness_note_present']=has_hist
            raw=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
            payload['learner_facing_sha256']=sha256_bytes(raw)
            record_hashes[r['id']]=payload['learner_facing_sha256']
            packet.append(payload)
        if qcount!=600 or acount!=600: raise SystemExit(f'{level}: Q/A totals drift')
        packet_path=PACKET_DIR/f'{level}.jsonl'
        packet_path.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in packet),encoding='utf-8')
        levels[level]={'canonical_path':rel,'canonical_sha256':g['sha256'],'canonical_git_blob':g['git_blob'],'passages':60,'questions':qcount,'answers':acount,'historical_naturalness_note_records':historical,'fresh_review_status':'NOT_YET_REVIEWED','packet_path':packet_path.relative_to(ROOT).as_posix(),'record_learner_facing_sha256':record_hashes}
        totalq+=qcount; totala+=acount
    audit={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','gate':'Gate B — passage-by-passage linguistic/naturalness audit','date':'2026-08-30','status':'IN_PROGRESS','scope':'100% of current Arabic A1-C2 canonical records. Packets contain passage text plus all 10 question/answer pairs per passage. Historical naturalness notes are inventory context only and do not count as fresh approval.','records':360,'questions':totalq,'answers':totala,'levels':levels,'review_dimensions':['grammar_syntax','spelling_typography','morphology_agreement','naturalness_idiomaticity','semantic_precision','ambiguity','register','msa_consistency','pronoun_reference_clarity','cohesion','translationese','pragmatic_plausibility','question_wording','answer_wording'],'fresh_records_reviewed':0,'fresh_records_with_findings':0,'fresh_findings':0,'quality_promotion':False,'release_claim':False,'next_step':'Fresh human/model passage-by-passage review of each packet; log exact field/span/severity/proposed repair before any canonical edit.'}
    OUT.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in audit.items() if k!='levels'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
