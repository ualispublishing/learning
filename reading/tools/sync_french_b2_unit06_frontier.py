#!/usr/bin/env python3
"""Advance durable project state to B2 Unit07 from the exact Unit06 lock."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2]
B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_b2_unit06_frontier_lock.json';STATUS=R/'reading/STATUS.json';TASKS=R/'reading/TASKS.md';HANDOFF=R/'reading/AGENT_HANDOFF.md'
U6=['téléphone','compte','message','adresse','photo','nom','visage','voix','contrôler','suivre','connaître','cacher','client','bureau','demander','répondre','vendre','chercher','trouver','monde']
THEME='arts and interpretation'; GENRES='review / profile / critical comparison'
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=36 or blob!=lock.get('canonical_blob'):raise AssertionError('Unit06 lock/live B2 mismatch')
 if sorted(lock.get('unit06_target_forms',[]))!=sorted(U6):raise AssertionError('Unit06 target lock drift')
 rows=[json.loads(x) for x in B2.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=36 or rows[-1]['id']!='fr-b2-u06-p06':raise AssertionError('unexpected B2 frontier')
 wc=[r['word_count'] for r in rows[30:36]]
 s=json.loads(STATUS.read_text(encoding='utf-8'));b=s['french']['b2_generation']
 if b.get('last_sequence')!=30:raise AssertionError('STATUS not at expected pre-Unit06 sync frontier')
 s['updated']='2026-08-17'
 s['phase']='Arabic A1-C2 is formally approved. French A1, A2, and B1 are generated and generation-integrity PASS. French B2 Units 01-06 are canonical; Unit 07 / sequences 37-42 is next.'
 fr=s['french'];fr['canonical_passages']=216;fr['questions']=2160;fr['answers']=2160;fr['levels']['b2']=36
 b['passages']=36;b['questions']=360;b['answers']=360;b['completed_units']=[1,2,3,4,5,6];b['last_sequence']=36;b['canonical_blob']=blob;b['unit06_theme']='digital life and privacy';b['unit06_targets']=U6;b['unit06_word_counts']=wc;b['unit06_frontier_lock']='reading/audit/french_b2_unit06_frontier_lock.json';b['unit06_paired_text_group']='fr-b2-u06-data-control-opinions'
 fr['next_target']=f'Generate French B2 Unit 07 / sequences 37-42 against B2 blob {blob}. Canonical topic-matrix theme: {THEME}; genres: {GENRES}. Use accepted default 4 fresh targets per P01-P05, P06 zero new, 350-550 words, 10 Q/A, interpretation/evidence distinctions, critic perspective, artist/profile context, comparison of readings, counterargument, author position and synthesis, exact reviews, and freshness checks against all prior French targets.'
 s['next_actions']=['keep Arabic sealed unless canonical Arabic changes','do not broadly regenerate French A1/A2/B1','generate French B2 Unit07 against the locked Unit06 blob and canonical topic matrix','continue French generation-first through B2-C2 before final French multi-pass audit','keep Urdu unchanged while French is active unless explicitly reprioritized']
 if 'reading/audit/french_b2_unit06_frontier_lock.json' not in s['important_files']:s['important_files'].append('reading/audit/french_b2_unit06_frontier_lock.json')
 STATUS.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

 t=TASKS.read_text(encoding='utf-8');start=t.index('#### Unit 06 — IMMEDIATE NEXT');end=t.index('\n## Urdu — QUEUED',start)
 block=f'''#### Unit 06 — COMPLETE\n- [x] Sequences 31–36 canonical.\n- [x] 6 passages / 60 Q / 60 A.\n- [x] 20 fresh source-backed targets, four in P01–P05; P06 zero new.\n- [x] Theme: `digital life and privacy`; genres: analysis / policy-style summary / paired opinions.\n- [x] P03/P04 paired group `fr-b2-u06-data-control-opinions`.\n- [x] Canonical B2 blob after Unit06: `{blob}`.\n- [x] Frontier lock `reading/audit/french_b2_unit06_frontier_lock.json` = PASS.\n\nUnit 06 targets: `'''+'`, `'.join(U6)+f'''`.\n\n#### Unit 07 — IMMEDIATE NEXT\nCanonical topic-matrix theme: **{THEME}**. Genres: **{GENRES}**.\n\n- [ ] Generate sequences 37–42 against locked B2 blob `{blob}`.\n- [ ] Accepted default 4 fresh targets per P01–P05; P06 zero new.\n- [ ] Check every candidate against all prior deliberate French A1–B2 targets.\n- [ ] Preserve 350–550 words, 10 linked Q/A, source identity, exact reviews and local target declarations.\n- [ ] Require interpretation/evidence distinctions, critic perspective, profile context, competing readings, counterargument, author position and synthesis.\n- [ ] Fail closed on lock/source drift, collision, schema/linkage, word band or review visibility.\n\nRemaining after Unit06:\n- [ ] B2: 24 passages.\n- [ ] C1: 60 passages.\n- [ ] C2: 60 passages.\n'''
 t=t[:start]+block+t[end:]
 old='**Generate French B2 Unit 06 / sequences 31–36 for `digital life and privacy` against blob `bada023bdbbe9830ec324ed5924862d5b153e214`. Keep Arabic sealed.**';new=f'**Generate French B2 Unit 07 / sequences 37–42 for `{THEME}` against blob `{blob}`. Keep Arabic sealed.**'
 if old not in t:raise AssertionError('TASKS anchor drift')
 TASKS.write_text(t.replace(old,new),encoding='utf-8')

 h=HANDOFF.read_text(encoding='utf-8');start=h.index('## 10. IMMEDIATE FRONTIER — B2 Unit 06');end=h.index('\n## 11. Urdu — QUEUED',start)
 block=f'''## 10. B2 Unit 06 — COMPLETE / CURRENT LOCK\n\nTheme: **digital life and privacy**. Genres: analysis / policy-style summary / paired opinions. Sequences 31–36.\n\n- 6 passages / 60 questions / 60 answers;\n- 20 fresh targets, four in P01–P05; P06 zero new;\n- P03/P04 paired group `fr-b2-u06-data-control-opinions`;\n- canonical B2 blob `{blob}`;\n- frontier lock `reading/audit/french_b2_unit06_frontier_lock.json` = PASS;\n- Unit06 targets: `'''+'`, `'.join(U6)+f'''`.\n\nGuard history: checkpoint retained three stale Unit05 target tags; they were remapped to locally declared Unit06 concepts before canonicalization. No guard was weakened.\n\n## 11. IMMEDIATE FRONTIER — B2 Unit 07\n\nCanonical theme: **{THEME}**. Genres: **{GENRES}**. Generate sequences **37–42** against exact blob `{blob}`. Require the Unit06 lock; use four fresh targets by default in P01–P05 and zero new in P06; preserve source freshness/rank identity, exact reviews, 350–550 words, 10 linked Q/A, and B2 reasoning about interpretation vs evidence, critic/artist perspective, contextual profile, competing readings, counterargument, position and synthesis. Fail closed and repair rather than weakening guards.\n'''
 h=h[:start]+block+h[end:]
 h=h.replace('\n## 11. Urdu — QUEUED','\n## 12. Urdu — QUEUED').replace('\n## 12. Throughput / parallel rules','\n## 13. Throughput / parallel rules').replace('\n## 13. Core non-negotiables','\n## 14. Core non-negotiables')
 HANDOFF.write_text(h,encoding='utf-8')
 print(json.dumps({'status':'PASS','b2_blob':blob,'b2_passages':36,'next':'B2 Unit07','theme':THEME,'word_counts':wc},ensure_ascii=False))
if __name__=='__main__':main()
