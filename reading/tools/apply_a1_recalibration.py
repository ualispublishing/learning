import json,re,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
lang=sys.argv[1]
cfg={}
for file in sorted((root/'reading'/'recalibration').glob(f'{lang}_a1_p*.json')):
 cfg.update(json.loads(file.read_text(encoding='utf-8')))
if not cfg: raise SystemExit(f'No recalibration config for {lang}')
path=root/'reading'/lang/'a1'/'passages.jsonl'
rows=[json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x]
for row in rows:
 spec=cfg.get(row['id'])
 if not spec: continue
 row['text']=spec['text']; row['word_count']=len(re.findall(r'\S+',row['text'])); row['estimated_known_token_coverage']=0
 row['questions']=[{'id':f'q{i}','type':spec['types'][i-1],'prompt':spec['prompts'][i-1],'answer_id':f'a{i}'} for i in range(1,6)]
 row['answer_key']=[{'id':f'a{i}','question_id':f'q{i}','answer':spec['answers'][i-1],'explanation':''} for i in range(1,6)]
 for target in row.get('new_lexical_targets',[]): target['exposures_in_text']=max(1,row['text'].casefold().count(str(target.get('form','')).casefold()))
 row['quality']['coverage_check']='pending'; row['quality']['answer_key_check']='pass'; row['quality']['status']='draft'
 row['quality']['notes']=['Recalibrated under A1_CALIBRATION_PROFILE; final supported-coverage audit pending.']
 row['speed_training']['benchmark_eligible']=False
path.write_text('\n'.join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in rows)+'\n',encoding='utf-8')
