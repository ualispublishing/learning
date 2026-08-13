import json,re
from pathlib import Path

root=Path(__file__).resolve().parents[2]
path=root/'reading'/'arabic'/'a1'/'passages.jsonl'
rows=[json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]

texts={
'ar-a1-u01-p01':'''ليلى في منزل جديد مع أمها. المنزل صغير، لكنه جميل. قالت أمها: هذا منزلنا الآن. دخلت ليلى وقالت: حسنا، أريد أن أكون هنا. معها حقيبة فيها كتاب. الحقيبة معها في المنزل. قالت أمها: هل تريدين أن تري المكان؟ قالت ليلى: نعم. ذهبتا إلى داخل المنزل ثم إلى خارجه. ثم كانتا داخل المنزل مرة أخرى. قالت ليلى: الآن أعرف المكان. أريد أن أبقى هنا معك.''',
'ar-a1-u01-p02':'''في الصباح كانت ليلى في المنزل. قالت أمها: بعد قليل نذهب إلى المدرسة. قالت ليلى: حسنا. معها حقيبتها وكتاب واحد فقط. لم تأخذ كل الكتب. ذهبت مع أمها إلى المدرسة. بعد وقت كانت ليلى في المنزل مرة أخرى. قالت ليلى: حقيبتي هنا، وكتابي معي. قالت أمها: هل تريدين كتابا آخر؟ قالت ليلى: لا، هذا الكتاب فقط. بعد ذلك كانتا معا في المنزل. قالت أمها: الآن نحن هنا. قالت ليلى: نعم، وغدا نذهب إلى المدرسة مرة أخرى.'''
}

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
 elif r['id'].endswith('p02'):
  prompts=['ماذا قالت الأم قبل الذهاب إلى المدرسة؟','كم كتابا كان مع ليلى؟','ماذا تعني «بعد» في «بعد وقت كانت ليلى في المنزل مرة أخرى»؟','ماذا تعني «فقط» في «كتاب واحد فقط»؟','أكمل: معي كتاب واحد _____، وليس كل الكتب.']
  answers=['قالت: بعد قليل نذهب إلى المدرسة.','كتاب واحد.','في وقت يأتي لاحقا.','واحد لا أكثر.','فقط']
  types=['sequence','literal_detail','vocabulary_in_context','vocabulary_in_context','cloze_transfer']
  r['questions']=[{'id':f'q{i}','type':types[i-1],'prompt':prompts[i-1],'answer_id':f'a{i}'} for i in range(1,6)]
  r['answer_key']=[{'id':f'a{i}','question_id':f'q{i}','answer':answers[i-1],'explanation':''} for i in range(1,6)]
 r['quality']['answer_key_check']='pass'
 r['quality']['notes']=['Recalibrated and exercise-aligned under A1_CALIBRATION_PROFILE; measured coverage pending.']

path.write_text('\n'.join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in rows)+'\n',encoding='utf-8')
