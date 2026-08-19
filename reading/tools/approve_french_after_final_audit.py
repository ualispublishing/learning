#!/usr/bin/env python3
"""Approve French reading only from a live, hash-bound whole-corpus PASS."""
from __future__ import annotations
import json,subprocess
from datetime import date
from pathlib import Path

R=Path(__file__).resolve().parents[2]
READING=R/'reading'; A=READING/'audit'; F=READING/'french'
AUDIT=A/'french_final_whole_audit.json'; REPAIR=A/'french_final_repair_transaction.json'; APPROVAL=A/'french_final_approval.json'; STATUS=READING/'STATUS.json'
LEVELS=['a1','a2','b1','b2','c1','c2']
def h(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def main():
 audit=json.loads(AUDIT.read_text(encoding='utf-8'));repair=json.loads(REPAIR.read_text(encoding='utf-8'))
 if audit.get('status')!='PASS' or not audit.get('approval_ready') or audit.get('audit_pass_count',0)<10:raise AssertionError('French whole audit not approval-ready')
 if repair.get('status')!='PASS_READY_FOR_FRENCH_APPROVAL' or repair.get('audit_status')!='PASS':raise AssertionError('French repair transaction not PASS')
 live={l:h(F/l/'passages.jsonl') for l in LEVELS}
 if audit.get('level_blobs')!=live:raise AssertionError('French audit level blobs do not match live canonical files')
 if repair.get('final_c2_blob')!=live['c2']:raise AssertionError('French repair artifact C2 blob does not match live canonical')
 if audit.get('canonical_passages')!=360 or audit.get('questions')!=3600 or audit.get('answers')!=3600:raise AssertionError('French final corpus cardinality mismatch')

 approval={'status':'APPROVED','language':'fr','scope':'French graded reading A1-C2','date':date.today().isoformat(),'canonical_passages':360,'questions':3600,'answers':3600,'audit_version':audit.get('audit_version',3),'audit_pass_count':audit['audit_pass_count'],'whole_corpus_sha256':audit['whole_corpus_sha256'],'level_blobs':live,'repair_transaction_status':repair['status'],'historical_frontier_locks_preserved':repair.get('historical_frontier_locks_preserved',False),'approval_basis':'live canonical hashes match a whole-corpus audit with all required independent passes PASS'}
 APPROVAL.write_text(json.dumps(approval,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

 s=json.loads(STATUS.read_text(encoding='utf-8'))
 s['status']='FRENCH_COMPLETE_APPROVED'
 s['mode']='serial_single_writer'
 s['canonical_passages']=360
 s['approved_passages']=360
 s['unapproved_passages']=0
 s.setdefault('generation',{}).update({'status':'COMPLETE','canonical_passages':360})
 s.setdefault('final_audit',{}).update({'policy':'pass1_12_before_approval','current_gate':'complete','approval':'APPROVED','audit_artifact':'reading/audit/french_final_whole_audit.json','approval_artifact':'reading/audit/french_final_approval.json','audit_pass_count':audit['audit_pass_count'],'whole_corpus_sha256':audit['whole_corpus_sha256']})
 s['next_action']='Resume the next unapproved language from the authoritative handoff; do not reopen French unless a deliberate canonical change invalidates this hash-bound approval.'
 STATUS.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'status':'APPROVED','whole_corpus_sha256':audit['whole_corpus_sha256'],'level_blobs':live},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
