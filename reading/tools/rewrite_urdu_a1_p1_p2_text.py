import json,re
from pathlib import Path
p=Path(__file__).resolve().parents[2]/'reading/urdu/a1/passages.jsonl'
rows=[json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x]
new={
'ur-a1-u01-p01':"عائشہ اپنی خالہ کے ساتھ نئے گھر میں آئی۔ خالہ نے کہا، ‘یہ ہمارا گھر ہے۔’ عائشہ نے کہا، ‘یہ اچھا ہے۔’ گھر میں ایک کمرہ تھا۔ عائشہ کے پاس ایک کتاب تھی۔ وہ کتاب لے کر کمرے میں گئی۔ خالہ بھی اس کے ساتھ گئیں۔ عائشہ نے کہا، ‘میں یہاں پڑھوں گی۔’ پھر دونوں گھر کے باہر گئیں اور کچھ دیر بعد واپس آئیں۔ عائشہ نے گھر کو دیکھا اور کہا، ‘یہ جگہ مجھے اچھی لگتی ہے۔’",
'ur-a1-u01-p02':"صبح عائشہ گھر میں تھی۔ اس کے پاس ایک کتاب تھی۔ کچھ وقت بعد خالہ نے کہا، ‘اسکول کا وقت ہو گیا ہے۔’ عائشہ کتاب لے کر اسکول گئی۔ مریم بھی اس کے ساتھ تھی۔ کچھ وقت بعد دونوں کلاس میں تھیں۔ اسکول کے بعد عائشہ گھر آئی۔ اس نے کتاب اپنے پاس رکھی اور خالہ سے بات کی۔ خالہ نے پوچھا، ‘کیا تمہارے پاس کھیلنے کا وقت ہے؟’ عائشہ نے کہا، ‘ہاں، لیکن پہلے میں کچھ دیر گھر میں رہوں گی۔’"
}
for r in rows:
 if r['id'] in new:
  r['text']=new[r['id']]; r['word_count']=len(re.findall(r'\S+',r['text'])); r['estimated_known_token_coverage']=0; r['quality']['coverage_check']='pending'; r['quality']['status']='draft'
p.write_text('\n'.join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in rows)+'\n',encoding='utf-8')
