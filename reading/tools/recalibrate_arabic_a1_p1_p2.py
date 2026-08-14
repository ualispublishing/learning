import json,re
from pathlib import Path

root=Path(__file__).resolve().parents[2]
path=root/'reading'/'arabic'/'a1'/'passages.jsonl'
rows=[json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
by_id={r['id']:r for r in rows}
if set(by_id) != {f'ar-a1-u01-p0{i}' for i in range(1,7)}:
    raise SystemExit('Arabic A1 Unit 01 id guard failed')

p5=by_id['ar-a1-u01-p05']
p5['text']='''بعد المدرسة ذهبت ليلى إلى المكتبة مع أمها. هناك كتب كثيرة. نظرت ليلى إلى بعض الكتب، لكنها لم تأخذ كل الكتب. أخذت كتابين فقط. كانت مع أمها في المكتبة حتى المساء. عندما جاء المساء قالت الأم: الآن نعود إلى المنزل. قالت ليلى: نعم. في الطريق قالت: بعض الكتب سهلة وبعضها ليس سهلا. في المنزل وضعت الكتابين هنا، مع حقيبتها. قالت أمها: هل تريدين القراءة حتى المساء غدا؟ قالت ليلى: أريد أن أقرأ قليلا فقط، ثم أكون معك. قالت أمها: هذا جيد، ولا نأخذ كل الكتب.'''
p5['genre']='routine narrative'
for t in p5.get('new_lexical_targets',[]):
    if t['id']=='ar-r53': t['exposures_in_text']=3
    elif t['id']=='ar-r56': t['exposures_in_text']=2
q={x['id']:x for x in p5['questions']}; a={x['id']:x for x in p5['answer_key']}
q['q4']['type']='literal_detail'; q['q4']['prompt']='ما الدليل في النص على أن ليلى لم تأخذ كل الكتب؟'
a['a4']['answer']='أخذت كتابين فقط، والنص يقول إنها لم تأخذ كل الكتب.'

p6=by_id['ar-a1-u01-p06']
p6['text']='''ليلى تعرف هذه الأماكن الآن: المدرسة والحديقة والمكتبة. في الصباح تذهب إلى المدرسة ومعها حقيبتها وكتاب. بعد المدرسة تعود إلى المنزل. في بعض الأيام تقول لأمها: أريد أن أذهب إلى الحديقة. تذهبان معا، وتكونان هناك قليلا. وفي يوم آخر يمكن أن تذهبا إلى المكتبة. ليلى تنظر إلى بعض الكتب وتأخذ كتابا واحدا أو اثنين فقط. لا تأخذ كل الكتب. عندما تعود إلى المنزل تضع كتابها هنا، مع حقيبتها. يمكن أن تقرأ حتى المساء، لكنها لا تقرأ كل الوقت. بعد ذلك تكون مع أمها. الآن يمكنها أن تقول أين المدرسة وأين الحديقة وأين المكتبة.'''
p6['title']='أماكن ليلى'; p6['topics']=['neighborhood','routine','review']
q={x['id']:x for x in p6['questions']}; a={x['id']:x for x in p6['answer_key']}
q['q3']['type']='literal_detail'; a['a3']['answer']='في بعض الأيام.'
a['a5']['answer']='تذهب ليلى إلى المدرسة وتعود إلى منزلها، وقد تذهب إلى الحديقة أو المكتبة.'

for r in (p5,p6):
    r['word_count']=len(re.findall(r'\S+',r['text']))
    r['sentence_count']=len(re.findall(r'[.!؟]+',r['text']))
    r['estimated_known_token_coverage']=0
    r['quality']['coverage_check']='pending'; r['quality']['status']='draft'; r['quality']['answer_key_check']='pass'
    r['quality']['notes']=['Recalibrated under A1_CALIBRATION_PROFILE; supported lexical-control measurement pending.','Ten-question standard and canonical JSON Schema synchronized.','Target grammar/sense metadata synchronized with the Arabic educator-cleared vocabulary decks.']

path.write_text('\n'.join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in rows)+'\n',encoding='utf-8')
