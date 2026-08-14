#!/usr/bin/env python3
"""Remove Pass-05 Latin-script intrusions from Arabic reader-facing content.

This repairs only reader-facing title/text/question prompts/answers. It preserves
IDs, tags, metadata, and target senses. English-only C2 vocabulary answers are
replaced by concise Arabic definitions rather than deleted.
"""
from __future__ import annotations
import json,re
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
LATIN=re.compile(r'[A-Za-z]')
LEVEL_REPL={
 'A1':'المستوى المبتدئ الأول','A2':'المستوى المبتدئ الثاني',
 'B1':'المستوى المتوسط الأول','B2':'المستوى المتوسط الثاني',
 'C1':'المستوى المتقدم الأول','C2':'المستوى المتقدم الثاني',
}
TOKEN_REPL={'capstone':'المهمة الختامية','feedback':'التغذية الراجعة','passage':'النص'}
GLOSS_REPL={
 'edition':'طبعة أو إصدار من نص أو كتاب.',
 'claim; allege':'يزعم أو يدّعي قولًا يحتاج إلى إثبات.',
 'sample':'عينة مختارة من مجموعة أكبر.',
 'tangible':'ملموس أو محسوس ويمكن ملاحظته مباشرة.',
 'restoration':'ترميم يعيد الشيء إلى حالة سابقة أو قريبة منها.',
 'similar; resembling':'مشابه أو مماثل لشيء آخر.',
 'observation post; observatory':'مرصد؛ مكان مخصص للرصد والملاحظة.',
 'obstacle; impediment':'عائق أو عقبة تعرقل التقدم.',
 'preceded; having precedent':'مسبوق؛ له سابق أو سبقه شيء مماثل.',
 'axis; central pole':'محور؛ خط أو عنصر مركزي تنتظم حوله الأشياء.',
 'facilitation':'تيسير؛ جعل أمر ما أسهل وأيسر.',
 'control; dominance':'هيمنة أو سيطرة على مسار أو قرار.',
 'map':'خارطة؛ تمثيل منظم للمكان أو للعلاقات.',
 'escalation; increase':'تصاعد؛ زيادة متدرجة أو متنامية.',
 'single; acting alone':'منفرد؛ يعمل وحده أو بصورة مستقلة.',
 'perception; recognition':'إدراك؛ فهم الشيء أو الوعي به.',
 'transmitter; sender':'مرسل؛ من يبعث رسالة أو إشارة.',
 'bring about; cause':'أوقع؛ تسبب في حدوث شيء أو أحدثه.',
 'optimism':'تفاؤل؛ توقع نتيجة حسنة أو النظر بإيجابية إلى المستقبل.',
 'extended; long-lasting':'ممتد؛ مستمر مدة طويلة أو على نطاق واسع.',
}
def replace_general(s:str)->str:
    out=s
    for old,new in LEVEL_REPL.items():out=out.replace(old,new)
    for old,new in TOKEN_REPL.items():out=out.replace(old,new)
    return out

def main():
    touched=defaultdict(set);field_changes=[];gloss_changes=[]
    loaded={}
    for level in LEVELS:
        p=ROOT/f'reading/arabic/{level}/passages.jsonl'
        rows=[json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()];loaded[level]=rows
        for row in rows:
            pid=row['id']
            for field in ('title','text'):
                old=str(row.get(field,'') or '');new=replace_general(old)
                if new!=old:
                    row[field]=new;touched[level].add(pid);field_changes.append({'passage_id':pid,'field':field})
            for q in row.get('questions',[]):
                if not isinstance(q,dict):continue
                old=str(q.get('prompt','') or '');new=replace_general(old)
                if new!=old:
                    q['prompt']=new;touched[level].add(pid);field_changes.append({'passage_id':pid,'field':f"question:{q.get('id')}"})
            for a in row.get('answer_key',[]):
                if not isinstance(a,dict):continue
                old=str(a.get('answer','') or '')
                stripped=old.strip()
                if stripped in GLOSS_REPL:
                    new=GLOSS_REPL[stripped];gloss_changes.append({'passage_id':pid,'answer_id':a.get('id'),'old':stripped,'new':new})
                else:new=replace_general(old)
                if new!=old:
                    a['answer']=new;touched[level].add(pid);field_changes.append({'passage_id':pid,'field':f"answer:{a.get('id')}"})
            if pid in touched[level]:
                # Text-level replacements can change token count; keep stored count synchronized.
                row['word_count']=len(str(row.get('text','')).split())
                row['revision']=int(row.get('revision',1))+1
                notes=row.setdefault('quality',{}).setdefault('notes',[])
                note='Final audit Pass 05 repair: removed Latin-script intrusions from Arabic reader-facing content and localized English-only vocabulary definitions; IDs and assessment intent preserved.'
                if note not in notes:notes.append(note)
    # Before write, prove no Latin letters remain in any reader-facing field.
    remaining=[]
    for level,rows in loaded.items():
        for row in rows:
            fields=[('title',row.get('title','')),('text',row.get('text',''))]
            fields += [(f"question:{q.get('id')}",q.get('prompt','')) for q in row.get('questions',[]) if isinstance(q,dict)]
            fields += [(f"answer:{a.get('id')}",a.get('answer','')) for a in row.get('answer_key',[]) if isinstance(a,dict)]
            for field,value in fields:
                if LATIN.search(str(value or '')):remaining.append({'passage_id':row['id'],'field':field,'value':value})
    assert not remaining,remaining[:20]
    assert len(gloss_changes)==20,len(gloss_changes)
    for level,rows in loaded.items():
        if touched[level]:
            p=ROOT/f'reading/arabic/{level}/passages.jsonl'
            p.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
    print(json.dumps({'touched_passages':sum(len(v) for v in touched.values()),'field_changes':len(field_changes),'localized_english_gloss_answers':len(gloss_changes),'remaining_latin_reader_fields':0},ensure_ascii=False))
if __name__=='__main__':main()
