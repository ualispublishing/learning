#!/usr/bin/env python3
"""Advance durable project state to B2 Unit06 from the exact Unit05 lock."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2]
B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_b2_unit05_frontier_lock.json';STATUS=R/'reading/STATUS.json';TASKS=R/'reading/TASKS.md';HANDOFF=R/'reading/AGENT_HANDOFF.md'
U5=['été','année','mois','nuit','passé','long','changer','continuer','rester','devenir','compter','montrer','croire','penser','sembler','comprendre','préparer','action','mer','terre']
THEME='digital life and privacy'; GENRES='analysis / policy-style summary / paired opinions'
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=30 or blob!=lock.get('canonical_blob'):raise AssertionError('Unit05 lock/live B2 mismatch')
 if sorted(lock.get('unit05_target_forms',[]))!=sorted(U5):raise AssertionError('Unit05 target lock drift')
 rows=[json.loads(x) for x in B2.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=30 or rows[-1]['id']!='fr-b2-u05-p06':raise AssertionError('unexpected B2 frontier')
 wc=[r['word_count'] for r in rows[24:30]]
 s=json.loads(STATUS.read_text(encoding='utf-8'));b=s['french']['b2_generation']
 if b.get('last_sequence')!=24:raise AssertionError('STATUS not at expected pre-Unit05 sync frontier')
 s['updated']='2026-08-17'
 s['phase']='Arabic A1-C2 is formally approved. French A1, A2, and B1 are generated and generation-integrity PASS. French B2 Units 01-05 are canonical; Unit 06 / sequences 31-36 is next.'
 fr=s['french'];fr['canonical_passages']=210;fr['questions']=2100;fr['answers']=2100;fr['levels']['b2']=30
 b['passages']=30;b['questions']=300;b['answers']=300;b['completed_units']=[1,2,3,4,5];b['last_sequence']=30;b['canonical_blob']=blob;b['unit05_theme']='climate and uncertainty';b['unit05_targets']=U5;b['unit05_word_counts']=wc;b['unit05_frontier_lock']='reading/audit/french_b2_unit05_frontier_lock.json'
 fr['next_target']=f'Generate French B2 Unit 06 / sequences 31-36 against B2 blob {blob}. Canonical topic-matrix theme: {THEME}; genres: {GENRES}. Use accepted default 4 fresh targets per P01-P05, P06 zero new, 350-550 words, 10 Q/A, privacy/data-use trade-offs, policy scope/exceptions, consent/control, paired opinions, counterargument, author position and synthesis, exact reviews, and freshness checks against all prior French targets.'
 s['next_actions']=['keep Arabic sealed unless canonical Arabic changes','do not broadly regenerate French A1/A2/B1','generate French B2 Unit06 against the locked Unit05 blob and canonical topic matrix','continue French generation-first through B2-C2 before final French multi-pass audit','keep Urdu unchanged while French is active unless explicitly reprioritized']
 if 'reading/audit/french_b2_unit05_frontier_lock.json' not in s['important_files']:s['important_files'].append('reading/audit/french_b2_unit05_frontier_lock.json')
 STATUS.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

 t=TASKS.read_text(encoding='utf-8');start=t.index('#### Unit 05 — IMMEDIATE NEXT');end=t.index('\n## Urdu — QUEUED',start)
 block=f'''#### Unit 05 — COMPLETE\n- [x] Sequences 25–30 canonical.\n- [x] 6 passages / 60 Q / 60 A.\n- [x] 20 fresh source-backed targets, four in P01–P05; P06 zero new.\n- [x] Theme: `climate and uncertainty`; genres: evidence summary / news analysis / argument.\n- [x] Canonical B2 blob after Unit05: `{blob}`.\n- [x] Frontier lock `reading/audit/french_b2_unit05_frontier_lock.json` = PASS.\n\nUnit 05 targets: `'''+'`, `'.join(U5)+f'''`.\n\n#### Unit 06 — IMMEDIATE NEXT\nCanonical topic-matrix theme: **{THEME}**. Genres: **{GENRES}**.\n\n- [ ] Generate sequences 31–36 against locked B2 blob `{blob}`.\n- [ ] Accepted default 4 fresh targets per P01–P05; P06 zero new.\n- [ ] Check every candidate against all prior deliberate French A1–B2 targets.\n- [ ] Preserve 350–550 words, 10 linked Q/A, source identity, exact reviews and local target declarations.\n- [ ] Require privacy/data-use trade-offs, policy scope and exceptions, consent/control, paired opinions, counterargument, author position and synthesis.\n- [ ] Fail closed on lock/source drift, collision, schema/linkage, word band or review visibility.\n\nRemaining after Unit05:\n- [ ] B2: 30 passages.\n- [ ] C1: 60 passages.\n- [ ] C2: 60 passages.\n'''
 t=t[:start]+block+t[end:]
 old='**Generate French B2 Unit 05 / sequences 25–30 for `climate and uncertainty` against blob `125d8c87641ee5a0fbd958a415ede82f95c40eff`. Keep Arabic sealed.**';new=f'**Generate French B2 Unit 06 / sequences 31–36 for `{THEME}` against blob `{blob}`. Keep Arabic sealed.**'
 if old not in t:raise AssertionError('TASKS anchor drift')
 TASKS.write_text(t.replace(old,new),encoding='utf-8')

 h=HANDOFF.read_text(encoding='utf-8');start=h.index('## 9. IMMEDIATE FRONTIER — B2 Unit 05');end=h.index('\n## 10. Urdu — QUEUED',start)
 block=f'''## 9. B2 Unit 05 — COMPLETE / CURRENT LOCK\n\nTheme: **climate and uncertainty**. Genres: evidence summary / news analysis / argument. Sequences 25–30.\n\n- 6 passages / 60 questions / 60 answers;\n- 20 fresh targets, four in P01–P05; P06 zero new;\n- canonical B2 blob `{blob}`;\n- frontier lock `reading/audit/french_b2_unit05_frontier_lock.json` = PASS;\n- Unit05 targets: `'''+'`, `'.join(U5)+f'''`.\n\nGuard history: repaired one non-local assessment tag, exact-form visibility (`proche`, `long`), two learner-facing participle/adjective issues, checkpoint length, and exact checkpoint review `long`; guards were preserved rather than weakened.\n\n## 10. IMMEDIATE FRONTIER — B2 Unit 06\n\nCanonical theme: **{THEME}**. Genres: **{GENRES}**. Generate sequences **31–36** against exact blob `{blob}`. Require the Unit05 lock; use four fresh targets by default in P01–P05 and zero new in P06; preserve source freshness/rank identity, exact reviews, 350–550 words, 10 linked Q/A, and B2 reasoning about privacy/data-use trade-offs, policy scope/exceptions, consent/control, paired opinions, counterargument, position and synthesis. Fail closed and repair instead of weakening guards.\n'''
 h=h[:start]+block+h[end:]
 h=h.replace('\n## 10. Urdu — QUEUED','\n## 11. Urdu — QUEUED').replace('\n## 11. Throughput / parallel rules','\n## 12. Throughput / parallel rules').replace('\n## 12. Core non-negotiables','\n## 13. Core non-negotiables')
 HANDOFF.write_text(h,encoding='utf-8')
 print(json.dumps({'status':'PASS','b2_blob':blob,'b2_passages':30,'next':'B2 Unit06','theme':THEME,'word_counts':wc},ensure_ascii=False))
if __name__=='__main__':main()
