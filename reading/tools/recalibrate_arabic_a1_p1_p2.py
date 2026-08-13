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
 r['quality']['notes']=['Recalibrated under reading/planning/A1_CALIBRATION_PROFILE.md; measured coverage pending.']
 if r['id'].endswith('p01'):
  r['new_lexical_targets']=[x for x in r['new_lexical_targets'] if x['id'] in {'ar-r34','ar-r42'}]
  r['questions']=[
   {'id':'q1','type':'gist','prompt':'ما الفكرة الرئيسية في النص؟','answer_id':'a1'},
   {'id':'q2','type':'literal_detail','prompt':'من مع ليلى في المنزل الجديد؟','answer_id':'a2'},
   {'id':'q3','type':'vocabulary_in_context','prompt':'ما معنى «هنا» عندما تقول ليلى: «أريد أن أكون هنا»؟','answer_id':'a3','options':['في هذا المكان','غدا','في مكان بعيد'],'target_ids':['ar-r34']},
   {'id':'q4','type':'vocabulary_in_context','prompt':'ما معنى «الآن» في «هذا منزلنا الآن»؟','answer_id':'a4','options':['في الوقت الحاضر','بعد سنة','في الماضي'],'target_ids':['ar-r42']},
   {'id':'q5','type':'cloze_transfer','prompt':'أكمل: كنت خارج المنزل، و_____ أنا داخله.','answer_id':'a5','target_ids':['ar-r42']}]
  r['answer_key']=[
   {'id':'a1','question_id':'q1','answer':'ليلى تتعرف إلى منزلها الجديد.','explanation':'كل الأحداث تدور حول وجود ليلى في المنزل الجديد وتعرفها إلى المكان.'},
   {'id':'a2','question_id':'q2','answer':'أمها.','explanation':'يبدأ النص بقول إن ليلى في المنزل مع أمها.'},
   {'id':'a3','question_id':'q3','answer':'في هذا المكان.','explanation':'ليلى موجودة داخل المنزل وتشير إلى المكان الذي توجد فيه.'},
   {'id':'a4','question_id':'q4','answer':'في الوقت الحاضر.','explanation':'الجملة تتحدث عن حالة المنزل في الوقت الحالي.'},
   {'id':'a5','question_id':'q5','answer':'الآن','explanation':'«الآن» تقابل الحالة السابقة بالحالة الحالية.'}]
 elif r['id'].endswith('p02'):
  r['questions'][0]={'id':'q1','type':'sequence','prompt':'ماذا قالت الأم قبل الذهاب إلى المدرسة؟','answer_id':'a1'}
  r['answer_key'][0]={'id':'a1','question_id':'q1','answer':'قالت: بعد قليل نذهب إلى المدرسة.','explanation':'هذا هو الحدث الذي يسبق الذهاب إلى المدرسة.'}

path.write_text('\n'.join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in rows)+'\n',encoding='utf-8')
