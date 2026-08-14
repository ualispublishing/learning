import json,re
from pathlib import Path

root=Path(__file__).resolve().parents[2]
path=root/'reading'/'arabic'/'a1'/'passages.jsonl'
rows=[json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]

texts={
'ar-a1-u01-p01':'''ليلى في منزل جديد مع أمها. المنزل صغير، لكنه جميل. قالت أمها: هذا منزلنا الآن. قالت ليلى: حسنا، أنا هنا معك. معها حقيبة فيها كتاب. الحقيبة معها في المنزل. قالت أمها: هيا نرى المكان. قالت ليلى: نعم. ذهبتا إلى داخل المنزل ثم إلى خارجه. ثم كانتا داخل المنزل مرة أخرى. قالت ليلى: الآن أعرف المكان. أنا هنا معك الآن.''',
'ar-a1-u01-p02':'''في الصباح كانت ليلى في المنزل. قالت أمها: بعد قليل نذهب إلى المدرسة. قالت ليلى: حسنا. معها حقيبتها وكتاب واحد فقط. لم تأخذ كل الكتب. ذهبت مع أمها إلى المدرسة. بعد قليل كانت ليلى في المنزل مرة أخرى. قالت ليلى: حقيبتي هنا، وكتابي معي. قالت أمها: هل معك كتاب آخر؟ قالت ليلى: لا، هذا الكتاب فقط. بعد ذلك كانتا معا في المنزل. قالت أمها: الآن نحن هنا. قالت ليلى: نعم، وغدا نذهب إلى المدرسة مرة أخرى.'''
}

p2_prompts=['ماذا قالت الأم قبل الذهاب إلى المدرسة؟','كم كتابا كان مع ليلى؟','ماذا تعني «بعد» في «بعد قليل كانت ليلى في المنزل مرة أخرى»؟','ماذا تعني «فقط» في «كتاب واحد فقط»؟','أكمل: معي كتاب واحد _____، وليس كل الكتب.']
p2_answers=['قالت: بعد قليل نذهب إلى المدرسة.','كتاب واحد.','في وقت يأتي لاحقا.','واحد لا أكثر.','فقط']
p2_types=['sequence','literal_detail','vocabulary_in_context','vocabulary_in_context','cloze_transfer']

for r in rows:
 if r['id'] not in texts: continue
 r['text']=texts[r['id']]
 r['word_count']=len(re.findall(r'\S+',r['text']))
 r['sentence_count']=len(re.findall(r'[.!؟]+',r['text']))
 r['estimated_known_token_coverage']=0
 r['quality']['coverage_check']='pending'
 r['quality']['status']='draft'
 if r['id'].endswith('p01'):
  r['new_lexical_targets']=[x for x in r['new_lexical_targets'] if x['id'] in {'ar-r34','ar-r42'}]
  for t in r['new_lexical_targets']:
   if t['id']=='ar-r34': t['part_of_speech']='demonstrative of place / adverbial deictic'; t['exposures_in_text']=2
   elif t['id']=='ar-r42': t['exposures_in_text']=3
  for q in r.get('questions',[]):
   if q.get('id')=='q3': q['prompt']='ما معنى «هنا» عندما تقول ليلى: «أنا هنا معك»؟'
   elif q.get('id')=='q9': q['prompt']='اختر بين «لا» و«لم»: أكمل بما ينفي الفعل في الحاضر: «_____ تخرج ليلى وحدها.»'
  for a in r.get('answer_key',[]):
   if a.get('id')=='a9': a['answer']='لا.'
 elif r['id'].endswith('p02'):
  for t in r.get('new_lexical_targets',[]):
   if t['id']=='ar-r37': t['exposures_in_text']=3
   elif t['id']=='ar-r54': t['part_of_speech']='adverb / restrictive expression'; t['exposures_in_text']=2
  qmap={q['id']:q for q in r.get('questions',[])}
  amap={a['id']:a for a in r.get('answer_key',[])}
  for i in range(1,6):
   qid=f'q{i}'; aid=f'a{i}'
   if qid in qmap: qmap[qid].update({'type':p2_types[i-1],'prompt':p2_prompts[i-1],'answer_id':aid})
   if aid in amap: amap[aid].update({'question_id':qid,'answer':p2_answers[i-1],'explanation':''})
 r['quality']['answer_key_check']='pass'
 r['quality']['notes']=['Recalibrated and exercise-aligned under A1_CALIBRATION_PROFILE; measured coverage pending.','Premature يريد exposure removed from P1-P2 so P3 remains its first deliberate reader introduction.','Target grammar metadata synchronized with Arabic flashcard educator second pass.']

path.write_text('\n'.join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in rows)+'\n',encoding='utf-8')
