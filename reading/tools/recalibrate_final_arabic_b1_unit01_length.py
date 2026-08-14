#!/usr/bin/env python3
"""Final-review remediation: expand B1 Unit 01 into the documented 220-350 word band.

Additions deepen evidence, reference chains, tradeoffs, and inference; they do
not add deliberate lexical targets or change existing conclusions/questions.
"""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PATH=ROOT/'reading/arabic/b1/passages.jsonl'
ADD={
'ar-b1-u01-p01': """قبل أن تثبت القرار، قارنت نور أيضًا بين ما يمكن تعويضه وما يصعب تعويضه. فالدورة ستعود بعد أشهر، أما موعد تسليم المشروع فلن يتحرك، والأسرة كانت تعتمد عليها في مهمتين خلال الفترة نفسها. كتبت احتمالًا آخر: أن تسجل ثم تنسحب إذا زاد الضغط. بدا هذا الحل مرنًا في البداية، لكنها أدركت أن الانسحاب بعد أسبوعين سيستهلك وقتًا ومالًا من دون أن يحل مشكلة المشروع. لذلك لم تعتمد على شعورها بالخيبة وحده، بل سألت: أي خسارة مؤقتة يمكن قبولها الآن، وأي التزام ستكون كلفة إهماله أكبر؟""",
'ar-b1-u01-p02': """ولكي لا يعود الاتفاق الجديد مجرد وعد، قسموا العمل إلى مواعيد قصيرة بدل انتظار التقرير كاملًا. كان سامر يرسل مسودة صغيرة في نهاية كل يوم دراسي يعمل فيه على المشروع، ويرد أحد زملائه بملاحظة واحدة واضحة. اتفقوا أيضًا على أنه إذا تعذر عليه موعد ما فسيخبرهم قبل الموعد، لا بعده. بهذه الطريقة استطاعت المجموعة أن تميز بين مساعدة عضو يواجه ظرفًا مؤقتًا وبين أداء مهمته باستمرار بدلًا منه. كما أصبح من السهل معرفة هل التعديل ينجح فعلًا أم أن عليهم إعادة التوزيع مرة أخرى.""",
'ar-b1-u01-p03': """طلبت المعلمة بعد ذلك من كل طالب أن يقرأ ملف زميل آخر ويسأل سؤالًا واحدًا: ما الدليل على هذه المهارة؟ عندما قرأت هدى ملف نور، لم تشك في أنها منظمة، لكنها سألتها عن نتيجة تقسيم مشروع التصوير إلى مراحل. أضافت نور أن الفريق أنهى العمل قبل الموعد بيوم، وأنهم استطاعوا إصلاح صورة ناقصة لأنهم اكتشفوا المشكلة مبكرًا. في المقابل حذفت مثالًا لم تستطع تحديد أثره. ساعدها ذلك على فهم فرق مهم: كثرة الأمثلة لا تجعل الملف أقوى تلقائيًا؛ المثال المفيد هو الذي يسمح للقارئ بأن يرى الموقف والفعل والنتيجة وحدود ما تدعيه.""",
'ar-b1-u01-p04': """حاولت نور أيضًا أن تجعل المقارنة أكثر عدلًا. خصصت لكل طريقة وقتًا متقاربًا، واختارت أسئلة من مستوى صعوبة مشابه، وسجلت ما تذكرته بعد يومين بدل الاكتفاء بنتيجة الاختبار المباشر. لاحظت أن بعض الأخطاء جاءت من كلمات جديدة في الفصل لا من طريقة الدراسة نفسها، فكتبت ذلك في ملاحظاتها بدل تجاهله. لم تحول التجربة الصغيرة إلى قاعدة عامة، لكنها تعلمت كيف تفرق بين انطباع أولي ونتيجة يمكن فحصها مرة أخرى. ولهذا أصبح هدف الأسبوعين التاليين اختبار النمط نفسه في مادة مختلفة، لا إثبات أنها كانت على حق من البداية.""",
'ar-b1-u01-p05': """أضافت هدى إلى المقارنة عاملًا لم تنتبه إليه أولًا: الطريق إلى كل عمل. كان المتجر قريبًا جدًا، بينما تحتاج المكتبة إلى حافلة قصيرة في كل اتجاه. حسبت الوقت الأسبوعي كله، لا ساعات العمل المدفوعة فقط، ثم سألت المكتبة هل تستطيع تثبيت وردية الصباح خلال الأسابيع السابقة للامتحان. عندما وافق المسؤول على ذلك أصبح الخيار أكثر وضوحًا. ومع ذلك كتبت حدًا أدنى للدخل تحتاج إليه للمواصلات وبعض المصروفات، حتى لا يتحول قرار حماية الدراسة إلى ضغط مالي جديد. بهذه الصورة لم تعد المقارنة بين «مال» و«دراسة»، بل بين مجموعتين مختلفتين من الفوائد والكلف.""",
'ar-b1-u01-p06': """يمكن تلخيص الطريقة في أربع حركات مترابطة. أولًا يحدد الشخص ما الذي يحاول حمايته أو تحقيقه، لأن جمع المعلومات بلا سؤال واضح قد يزيد الحيرة. ثانيًا يفرق بين القيود الثابتة والأشياء القابلة للتعديل: موعد نهائي قد يكون ثابتًا، أما توزيع مهمة أو وردية عمل فقد يكون قابلًا للتفاوض. ثالثًا يبحث عن دليل يناسب القرار، مثل تجربة صغيرة أو سؤال شخص يعرف تفاصيل الموقف. وأخيرًا يضع علامة تدل على ضرورة المراجعة لاحقًا: موعد جديد، نتيجة اختبار، أو تغير في الظروف. ليست هذه الخطوات وصفة تمنع الخطأ، لكنها تجعل سبب القرار واضحًا بحيث يمكن تقييمه وتعديله بدل الدفاع عنه لمجرد أنه اتُّخذ سابقًا.""",
}
rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()];by={r['id']:r for r in rows};results=[]
for pid,addition in ADD.items():
 r=by[pid]
 assert addition.strip() not in r['text']
 old_wc=len(r['text'].split())
 r['text']=r['text'].rstrip()+' '+addition.strip()
 new_wc=len(r['text'].split())
 assert 220<=new_wc<=350,(pid,old_wc,new_wc)
 # P6 remains zero-new-target checkpoint; all records keep existing target sets.
 if pid.endswith('-p06'):assert not r.get('new_lexical_targets'),(pid,r.get('new_lexical_targets'))
 r['word_count']=new_wc
 r['sentence_count']=len([s for s in re.split(r'(?<=[.!؟])\s+',r['text']) if s.strip()])
 r['revision']=int(r.get('revision',1))+1
 notes=r.setdefault('quality',{}).setdefault('notes',[])
 note='Final Pass 07 remediation: expanded B1 Unit 01 with passage-specific evidence, tradeoffs, reference chains, and inference while preserving deliberate target sets and existing assessment conclusions.'
 if note not in notes:notes.append(note)
 results.append({'passage_id':pid,'old_word_count':old_wc,'new_word_count':new_wc,'added_words':new_wc-old_wc})
assert len(results)==6
PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
print(json.dumps({'unit':1,'level':'B1','repairs':results,'all_in_standard_band':all(220<=x['new_word_count']<=350 for x in results)},ensure_ascii=False))
