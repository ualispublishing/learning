#!/usr/bin/env python3
import json
from pathlib import Path
R=Path(__file__).resolve().parents[2]
P=R/'reading/arabic/a1/passages.jsonl'
POS={
 'ar-r34':'demonstrative of place / adverbial deictic',
 'ar-r40':'demonstrative of place / adverbial deictic',
 'ar-r54':'adverb / restrictive expression',
}
def main():
 rows=[json.loads(x) for x in P.read_text(encoding='utf-8').splitlines() if x.strip()]
 changed=0
 for p in rows:
  for t in p.get('new_lexical_targets',[]):
   value=POS.get(t.get('id'))
   if value and t.get('part_of_speech')!=value:
    t['part_of_speech']=value; changed+=1
  note='Target grammar metadata synchronized with Arabic flashcard educator second pass.'
  if changed and note not in p.get('quality',{}).get('notes',[]): p.setdefault('quality',{}).setdefault('notes',[]).append(note)
 P.write_text('\n'.join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in rows)+'\n',encoding='utf-8')
 print('refined target metadata',changed)
if __name__=='__main__': main()
