#!/usr/bin/env python3
"""Reconcile the single NFC regression introduced by the B1 Unit 7 Gate B repair."""
from __future__ import annotations
import hashlib,json,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/b1/passages.jsonl'; RELEASE=READING/'RELEASE_STATUS.json'; DECISION_DIR=READING/'audit/arabic_gate_b_decisions_2026-08-30'
EXPECTED_SHA='69b142618b02e78b355c661b540a03ac47ea8365b80dc1109f53deaa97f888cc'
OLD='ستُحدَّث'; NEW=unicodedata.normalize('NFC',OLD)
def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def main():
 raw=PATH.read_bytes(); actual=sha(raw)
 if actual!=EXPECTED_SHA: raise SystemExit(f'B1 canonical drift before Unit 7 NFC reconciliation: {actual}')
 if unicodedata.is_normalized('NFC',OLD): raise SystemExit('guard error: OLD unexpectedly NFC')
 if not unicodedata.is_normalized('NFC',NEW): raise SystemExit('guard error: NEW is not NFC')
 rel=json.loads(RELEASE.read_text(encoding='utf-8')); ar=rel.get('languages',{}).get('arabic',{}); prog=ar.get('naturalness_review_progress',{}); gate=ar.get('latest_deterministic_gate',{})
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False: raise SystemExit('Arabic release-state drift')
 if prog.get('fresh_records_reviewed')!=162 or prog.get('fresh_records_with_findings')!=142 or prog.get('fresh_findings')!=278: raise SystemExit('Arabic Gate B progress drift before Unit 7 NFC reconciliation')
 if gate.get('open_findings')!=1873 or gate.get('finding_classes',{}).get('unicode_not_nfc')!=1: raise SystemExit('Expected exactly one post-Unit7 Unicode blocker')
 if not (DECISION_DIR/'b1_u07.json').exists() or (DECISION_DIR/'b1_u08.json').exists(): raise SystemExit('Gate B decision frontier drift')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or rows[39].get('id')!='ar-b1-u07-p04': raise SystemExit('B1 Unit 7 layout drift')
 count=sum(str(r.get('text','')).count(OLD) for r in rows)
 if count!=1 or rows[39].get('text','').count(OLD)!=1: raise SystemExit(f'Expected the non-NFC sequence exactly once in ar-b1-u07-p04, found {count}')
 rows[39]['text']=rows[39]['text'].replace(OLD,NEW,1)
 out=''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows)
 if not unicodedata.is_normalized('NFC',out): raise SystemExit('Canonical output still contains non-NFC content')
 PATH.write_text(out,encoding='utf-8')
 print(json.dumps({'level':'B1','unit':7,'repair':'NFC-only','pre_sha256':actual,'post_sha256':sha(PATH.read_bytes()),'old_codepoints':[hex(ord(c)) for c in OLD],'new_codepoints':[hex(ord(c)) for c in NEW]},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
