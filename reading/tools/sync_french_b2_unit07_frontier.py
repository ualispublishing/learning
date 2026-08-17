#!/usr/bin/env python3
"""Advance durable project state to B2 Unit08 from the exact Unit07 lock."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2]
B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_b2_unit07_frontier_lock.json';STATUS=R/'reading/STATUS.json';TASKS=R/'reading/TASKS.md';HANDOFF=R/'reading/AGENT_HANDOFF.md'
U7=['film','musique','chanson','jouer','histoire','lire','écrire','mot','ton','sens','sujet','imaginer','avis','aimer','beau','drôle','vie','présent','société','politique']
THEME='history and explanation';GENRES='historical account / causal analysis / source comparison'
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=42 or blob!=lock.get('canonical_blob'):raise AssertionError('Unit07 lock/live B2 mismatch')
 if sorted(lock.get('unit07_target_forms',[]))!=sorted(U7):raise AssertionError('Unit07 target lock drift')
 rows=[json.loads(x) for x in B2.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=42 or rows[-1]['id']!='fr-b2-u07-p06':raise AssertionError('unexpected B2 frontier')
 wc=lock['unit07_word_counts']
 s=json.loads(STATUS.read_text(encoding='utf-8'));b=s['french']['b2_generation']
 if b.get('last_sequence')!=36:raise AssertionError('STATUS not at expected pre-Unit07 sync frontier')
 s['updated']='2026-08-17';s['phase']='Arabic A1-C2 is formally approved. French A1, A2, and B1 are generated and generation-integrity PASS. French B2 Units 01-07 are canonical; Unit 08 / sequences 43-48 is next.'
 fr=s['french'];fr['canonical_passages']=222;fr['questions']=2220;fr['answers']=2220;fr['levels']['b2']=42
 b['passages']=42;b['questions']=420;b['answers']=420;b['completed_units']=[1,2,3,4,5,6,7];b['last_sequence']=42;b['canonical_blob']=blob;b['unit07_theme']='arts and interpretation';b['unit07_targets']=U7;b['unit07_word_counts']=wc;b['unit07_frontier_lock']='reading/audit/french_b2_unit07_frontier_lock.json'
 fr['next_target']=f'Generate French B2 Unit 08 / sequences 43-48 against B2 blob {blob}. Canonical topic-matrix theme: {THEME}; genres: {GENRES}. Use accepted default 4 fresh targets per P01-P05, P06 zero new, 350-550 words, 10 Q/A, source distinction, causal chains, chronology, competing historical explanations, source perspective, counterargument, author position and synthesis, exact reviews, and freshness checks against all prior French targets.'
 s['next_actions']=['keep Arabic sealed unless canonical Arabic changes','do not broadly regenerate French A1/A2/B1','generate French B2 Unit08 against the locked Unit07 blob and canonical topic matrix','continue French generation-first through B2-C2 before final French multi-pass audit','keep Urdu unchanged while French is active unless explicitly reprioritized']
 if 'reading/audit/french_b2_unit07_frontier_lock.json' not in s['important_files']:s['important_files'].append('reading/audit/french_b2_unit07_frontier_lock.json')
 STATUS.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

 t=TASKS.read_text(encoding='utf-8');start=t.index('#### Unit 07 — IMMEDIATE NEXT');end=t.index('\n## Urdu — QUEUED',start)
 block=f'''#### Unit 07 — COMPLETE\n- [x] Sequences 37–42 canonical.\n- [x] 6 passages / 60 Q / 60 A.\n- [x] 20 fresh source-backed targets, four in P01–P05; P06 zero new.\n- [x] Theme: `arts and interpretation`; genres: review / profile / critical comparison.\n- [x] Canonical B2 blob after Unit07: `{blob}`.\n- [x] Frontier lock `reading/audit/french_b2_unit07_frontier_lock.json` = PASS.\n\nUnit 07 targets: `'''+'`, `'.join(U7)+f'''`.\n\n#### Unit 08 — IMMEDIATE NEXT\nCanonical topic-matrix theme: **{THEME}**. Genres: **{GENRES}**.\n\n- [ ] Generate sequences 43–48 against locked B2 blob `{blob}`.\n- [ ] Accepted default 4 fresh targets per P01–P05; P06 zero new.\n- [ ] Check every candidate against all prior deliberate French A1–B2 targets.\n- [ ] Preserve 350–550 words, 10 linked Q/A, source identity, exact reviews and local target declarations.\n- [ ] Require chronology, causal chains, competing explanations, source perspective/comparison, counterargument, author position and synthesis.\n- [ ] Fail closed on lock/source drift, collision, schema/linkage, word band or review visibility.\n\nRemaining after Unit07:\n- [ ] B2: 18 passages.\n- [ ] C1: 60 passages.\n- [ ] C2: 60 passages.\n'''
 t=t[:start]+block+t[end:]
 old='**Generate French B2 Unit 07 / sequences 37–42 for `arts and interpretation` against blob `939ec4d433c8b5a8893093eca6f8e8a90ff2c1d4`. Keep Arabic sealed.**';new=f'**Generate French B2 Unit 08 / sequences 43–48 for `{THEME}` against blob `{blob}`. Keep Arabic sealed.**'
 if old not in t:raise AssertionError('TASKS anchor drift')
 TASKS.write_text(t.replace(old,new),encoding='utf-8')

 h=HANDOFF.read_text(encoding='utf-8');start=h.index('## 11. IMMEDIATE FRONTIER — B2 Unit 07');end=h.index('\n## 12. Urdu — QUEUED',start)
 block=f'''## 11. B2 Unit 07 — COMPLETE / CURRENT LOCK\n\nTheme: **arts and interpretation**. Genres: review / profile / critical comparison. Sequences 37–42.\n\n- 6 passages / 60 questions / 60 answers;\n- 20 fresh targets, four in P01–P05; P06 zero new;\n- canonical B2 blob `{blob}`;\n- frontier lock `reading/audit/french_b2_unit07_frontier_lock.json` = PASS;\n- Unit07 targets: `'''+'`, `'.join(U7)+f'''`.\n\nGuard history: repaired one stale checkpoint tag, brought P03 into the B2 word band with substantive counterevidence logic, and exposed exact checkpoint lemma `beau`; no guard was weakened.\n\n## 12. IMMEDIATE FRONTIER — B2 Unit 08\n\nCanonical theme: **{THEME}**. Genres: **{GENRES}**. Generate sequences **43–48** against exact blob `{blob}`. Require the Unit07 lock; use four fresh targets by default in P01–P05 and zero new in P06; preserve source freshness/rank identity, exact reviews, 350–550 words, 10 linked Q/A, and B2 historical reasoning about chronology, causal chains, competing explanations, source perspective/comparison, counterargument, position and synthesis. Fail closed and repair rather than weakening guards.\n'''
 h=h[:start]+block+h[end:];h=h.replace('\n## 12. Urdu — QUEUED','\n## 13. Urdu — QUEUED').replace('\n## 13. Throughput / parallel rules','\n## 14. Throughput / parallel rules').replace('\n## 14. Core non-negotiables','\n## 15. Core non-negotiables')
 HANDOFF.write_text(h,encoding='utf-8')
 print(json.dumps({'status':'PASS','b2_blob':blob,'b2_passages':42,'next':'B2 Unit08','theme':THEME,'word_counts':wc},ensure_ascii=False))
if __name__=='__main__':main()
