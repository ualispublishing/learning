#!/usr/bin/env python3
"""Advance durable project handoffs to B2 Unit 03 only if Unit 02 is locked.

Fails closed if the Unit02 lock is missing, stale, or the existing handoff files
are no longer at the expected Unit02 frontier.
"""
from __future__ import annotations
import json,re,subprocess
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
B2=REPO/'reading/french/b2/passages.jsonl';LOCK=REPO/'reading/audit/french_b2_unit02_frontier_lock.json';STATUS=REPO/'reading/STATUS.json';TASKS=REPO/'reading/TASKS.md';HANDOFF=REPO/'reading/AGENT_HANDOFF.md'
U2=['promettre','avenir','attendre','confiance','grave','calmer','solution','responsabilité','partager','opinion','secret','surtout','ordre','lieu','coût','préférer','ramener','pareil','lumière','pousser']

def main():
 if not LOCK.exists(): raise AssertionError('Unit02 frontier lock missing; durable handoff not advanced')
 lock=json.loads(LOCK.read_text(encoding='utf-8'))
 current=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=12 or current!=lock.get('canonical_blob'): raise AssertionError('Unit02 frontier lock does not match live B2')
 rows=[json.loads(x) for x in B2.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=12 or rows[-1]['id']!='fr-b2-u02-p06': raise AssertionError('unexpected B2 canonical frontier')
 wc=[r['word_count'] for r in rows[6:12]]

 s=json.loads(STATUS.read_text(encoding='utf-8'))
 if 'Unit 02 / sequences 7-12 is next' not in s.get('phase',''): raise AssertionError('STATUS no longer at expected Unit02 frontier')
 s['phase']='Arabic A1-C2 is formally approved. French A1, A2, and B1 are generated and generation-integrity PASS. French B2 Units 01-02 are canonical; Unit 03 / sequences 13-18 is next.'
 fr=s['french'];fr['canonical_passages']=192;fr['questions']=1920;fr['answers']=1920
 b2=fr['b2_generation'];b2['state']='ACTIVE';b2['passages']=12;b2['questions']=120;b2['answers']=120;b2['completed_units']=[1,2];b2['last_sequence']=12;b2['canonical_blob']=current;b2['unit02_theme']='decision under uncertainty';b2['unit02_targets']=U2;b2['unit02_word_counts']=wc
 fr['next_target']=f'Generate French B2 Unit 03 / sequences 13-18 against B2 blob {current}. Theme: institutions and rules. Use accepted default 4 fresh targets per P01-P05, P06 zero new, 350-550 words, 10 Q/A, institutional argument/scope/exception reasoning, exact reviews, and freshness checks against all prior French targets.'
 STATUS.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

 t=TASKS.read_text(encoding='utf-8')
 marker='#### Unit 02 — IMMEDIATE NEXT\nTheme: **decision under uncertainty**.'
 if marker not in t: raise AssertionError('TASKS no longer at expected Unit02 frontier')
 start=t.index(marker)
 end=t.index('\nRemaining after Unit01:',start)
 replacement=f'''#### Unit 02 — COMPLETE\n- [x] Sequences 7–12 canonical.\n- [x] 6 passages / 60 Q / 60 A.\n- [x] 20 fresh targets, four in P01–P05; P06 zero new.\n- [x] Theme: `decision under uncertainty`.\n- [x] Canonical B2 blob after Unit02: `{current}`.\n- [x] Frontier lock: `reading/audit/french_b2_unit02_frontier_lock.json` = PASS.\n\nUnit 02 targets: `'''+'`, `'.join(U2)+'''`.\n\n#### Unit 03 — IMMEDIATE NEXT\nTheme: **institutions and rules**.\n\n- [ ] Generate sequences 13–18 against the locked B2 Unit02 blob.\n- [ ] Use accepted default 4 fresh targets per P01–P05; P06 zero new.\n- [ ] Check all candidates against every prior deliberate French target through B2 Unit02.\n- [ ] Preserve 350–550 words, 10 linked Q/A, exact review visibility and source rank/ID identity.\n- [ ] Emphasize institutional scope, competing rules, exceptions, authority, procedure, fairness, argument relation and author position.\n- [ ] Fail closed on lock/source drift, collision, schema/linkage, word band or review visibility.\n'''
 t=t[:start]+replacement+t[end:]
 t=t.replace('Remaining after Unit01:\n- [ ] B2: 54 passages.','Remaining after Unit02:\n- [ ] B2: 48 passages.')
 t=t.replace('**Generate French B2 Unit 02 / sequences 7–12 for `decision under uncertainty` against blob `1ba43c900ad64ff9359264e743470138ce25a9c5`. Keep Arabic sealed.**',f'**Generate French B2 Unit 03 / sequences 13–18 for `institutions and rules` against blob `{current}`. Keep Arabic sealed.**')
 TASKS.write_text(t,encoding='utf-8')

 h=HANDOFF.read_text(encoding='utf-8')
 marker='## 6. IMMEDIATE FRONTIER — B2 Unit 02'
 if marker not in h: raise AssertionError('HANDOFF no longer at expected Unit02 frontier')
 start=h.index(marker);end=h.index('\n## 7. Urdu — QUEUED',start)
 block=f'''## 6. B2 Unit 02 — COMPLETE / CURRENT LOCK\n\nTheme: **decision under uncertainty**. Sequences 7–12.\n\n- 6 passages / 60 questions / 60 answers;\n- 20 fresh deliberate targets, four in P01–P05; P06 zero new;\n- canonical B2 blob after Unit02: `{current}`;\n- frontier lock artifact: `reading/audit/french_b2_unit02_frontier_lock.json` = PASS;\n- Unit02 targets: `'''+'`, `'.join(U2)+'''`.\n\n## 7. IMMEDIATE FRONTIER — B2 Unit 03\n\nRoadmap theme: **institutions and rules**.\n\nGenerate **sequences 13–18** against exact B2 blob `{current}`.\n\nRequirements:\n1. require the Unit02 frontier lock and verify the live B2 blob before target selection or append;\n2. use accepted default 4 fresh targets per P01–P05 unless discourse load clearly justifies another value within 4–8; P06 zero new;\n3. check every candidate against all deliberate French A1+A2+B1+B2 Units01–02 targets;\n4. preserve source rank/ID/intended sense and exact target/review exposure;\n5. use institutional/rules contexts with scope, authority, exceptions, procedure, fairness, competing obligations and justified counterarguments;\n6. preserve 350–550 words, 10 linked Q/A, B2 author-position/argument/inference/reference/synthesis demand;\n7. fail closed and repair instead of weakening guards.\n'''
 h=h[:start]+block+h[end:]
 h=h.replace('\n## 7. Urdu — QUEUED','\n## 8. Urdu — QUEUED').replace('\n## 8. Throughput / parallel rules','\n## 9. Throughput / parallel rules').replace('\n## 9. Core non-negotiables','\n## 10. Core non-negotiables')
 HANDOFF.write_text(h,encoding='utf-8')
 print(json.dumps({'status':'PASS','b2_blob':current,'b2_passages':12,'next':'B2 Unit03','word_counts':wc},ensure_ascii=False))
if __name__=='__main__':main()
