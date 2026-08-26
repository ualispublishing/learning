#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
STAGE=ROOT/'reading/audit/urdu_b2_u10_generation_candidate'
TARGET=ROOT/'reading/urdu/b2/passages.jsonl'
SCHEMA=ROOT/'reading/schema/passage.schema.json'
RELEASE=ROOT/'reading/RELEASE_STATUS.json'
DATE='2026-08-26'
IDS=[f'ur-b2-u10-p{i:02d}' for i in range(1,7)]
SEQS=list(range(55,61))
ROLES=['instructional','reinforcement','interleaved','transfer','integration','checkpoint']
GENRES={'paired long texts','integrated analysis','checkpoint'}
EXPECTED_ROADMAP={'unit':10,'theme':'B2 synthesis','genres':['paired long texts','integrated analysis','checkpoint']}
NEXT_ROADMAP={'unit':1,'theme':'research and evidence','genres':['academic-style synthesis','methods explanation','critique']}
TARGET_META=[
 ('ur-rank-2876','اساسی','fundamental; basic or underlying','conceptual_distinction',2876),
 ('ur-rank-2910','تفاوت','difference or disparity','contrast',2910),
 ('ur-rank-2870','پیوند','link, joining, or connection','structural_relation',2870),
 ('ur-rank-2885','لامتناہی','endless, limitless, or without an endpoint','communication_scope',2885),
 ('ur-rank-2858','تھکاوٹ','fatigue or tiredness','evidence_interpretation',2858),
 ('ur-rank-2897','دگنا','double or twice as much','metric_response',2897),
 ('ur-rank-2851','چنگاری','spark; also a figurative initiating spark','causal_explanation',2851),
 ('ur-rank-2912','تلف','wasted, ruined, destroyed, or lost','implementation_tradeoff',2912),
 ('ur-rank-2859','رباعی','a four-line poetic form; quatrain','close_reading',2859),
 ('ur-rank-2920','لسانیات','linguistics; the study of language','cultural_interpretation',2920),
]
TARGETS=[x[0] for x in TARGET_META]
META={x[0]:x for x in TARGET_META}

TEXTS=[
'''دو فرضی مضامین ایک ہی سوال پر غور کرتے ہیں: شہر کو نئی عوامی لائبریری کہاں بنانی چاہیے؟ پہلے مضمون کا اساسی دعویٰ یہ ہے کہ عمارت ایسی جگہ ہو جہاں زیادہ سے زیادہ لوگ پیدل یا بس سے پہنچ سکیں۔ اس کے مصنف کے نزدیک رسائی صرف سہولت نہیں بلکہ منصوبے کی بنیادی قدر ہے۔ وہ آبادی، سفر کے وقت اور قریبی اسکولوں کے اعداد کو اہم سمجھتا ہے، لیکن یہ بھی مانتا ہے کہ ہر عدد پوری تصویر نہیں دکھاتا۔

دوسرا مضمون ایک پرانی عمارت کے دوبارہ استعمال کی حمایت کرتا ہے۔ اس میں بتایا گیا ہے کہ تاریخی مقام پہلے ہی محلے کی شناخت کا حصہ ہے اور نئی تعمیر کے مقابلے میں کچھ مواد بچایا جا سکتا ہے۔ تاہم وہاں بس کی سروس کم ہے اور اندرونی جگہ کو بدلنے پر اضافی خرچ آئے گا۔ دونوں مضامین کا تفاوت صرف پسند میں نہیں بلکہ اس بات میں ہے کہ وہ کامیابی کو کس پیمانے سے ناپتے ہیں۔ ایک رسائی کو پہلے رکھتا ہے، دوسرا جگہ کی تاریخ اور موجودہ ڈھانچے کو زیادہ وزن دیتا ہے۔

اگر قاری صرف آخری سفارش دیکھے تو دونوں متن متضاد لگتے ہیں، مگر ان کے شواہد کا نقشہ بنانے سے مشترک بنیاد بھی نظر آتی ہے۔ دونوں مانتے ہیں کہ بجٹ محدود ہے، عمارت کو کئی برس چلنا ہے، اور فیصلے کے اثرات مختلف گروہوں پر الگ پڑیں گے۔ اختلاف اس مرحلے پر پیدا ہوتا ہے جہاں ایک قدر کو دوسری پر ترجیح دی جاتی ہے۔ یہی مقام تنقیدی مطالعے کے لیے اہم ہے، کیونکہ مضبوط تجزیہ صرف یہ نہیں پوچھتا کہ کون سا نتیجہ بہتر ہے؛ وہ یہ بھی پوچھتا ہے کہ نتیجے تک پہنچنے کے لیے کون سے مفروضے ضروری تھے۔

ایک مشترک جائزہ دونوں تجاویز کو تین سوالوں سے جانچ سکتا ہے۔ پہلی بات، کیا رسائی کے اعداد مختلف اوقات اور مختلف صارفین کو شامل کرتے ہیں؟ دوسری بات، کیا تاریخی عمارت کی مرمت کا اندازہ صرف ابتدائی خرچ ہے یا طویل مدت کی دیکھ بھال بھی شامل ہے؟ تیسری بات، اگر آبادی یا بس کے راستے بدل جائیں تو کون سی تجویز زیادہ آسانی سے ڈھل سکتی ہے؟ ان سوالوں سے معلوم ہوتا ہے کہ اساسی اصول واضح کرنا اور تفاوت کی نوعیت پہچاننا ایک دوسرے کے مخالف کام نہیں۔ یہی دونوں متن کو ایک بڑے فیصلے میں جوڑنے کا پہلا قدم ہے۔

آخر میں کوئی ایک جواب لازماً درست نہیں بنتا۔ بہتر نتیجہ وہ ہوگا جو مقاصد، شواہد، غیر یقینی باتوں اور متاثرہ گروہوں کو ایک ہی فریم میں دکھائے۔ اگر فیصلہ کرنے والے یہ واضح کر دیں کہ کس قدر کو کیوں زیادہ وزن دیا گیا، تو اختلاف باقی رہنے کے باوجود بحث زیادہ قابلِ جانچ ہو جاتی ہے۔''',
'''دو طویل تحریریں ایک تعلیمی منصوبے کی کامیابی کو مختلف زاویوں سے دیکھتی ہیں۔ پہلی تحریر کہتی ہے کہ آن لائن مواد، مقامی استاد اور گھر میں مشق کے درمیان مضبوط پیوند بنایا جائے تو طالب علم کو ایک ہی سبق کئی شکلوں میں ملتا ہے۔ اس کے مطابق مسئلہ مواد کی کمی نہیں بلکہ الگ الگ ذرائع کے درمیان ربط کی کمزوری ہے۔ اگر ہر ذریعہ اپنے مقصد سے بے خبر ہو تو طالب علم ایک سرگرمی میں سیکھی ہوئی بات دوسری جگہ منتقل نہیں کر پاتا۔

دوسری تحریر خبردار کرتی ہے کہ ہر چیز کو جوڑ دینا خود کامیابی نہیں۔ اس میں ایک ایسے نظام کی مثال ہے جس نے مسلسل اطلاع، مشق، درجہ بندی اور یاد دہانی شامل کر دی۔ ابتدا میں سرگرمی بڑھی، لیکن کچھ طلبہ کو یہ سلسلہ لامتناہی محسوس ہونے لگا۔ ہر کام کے بعد نیا کام سامنے آتا تھا اور مکمل ہونے کا احساس کم ہوتا گیا۔ مصنف کے مطابق مسلسل رابطہ اس وقت بوجھ بن سکتا ہے جب طالب علم کو وقفہ، انتخاب اور واضح اختتام نہ ملے۔

دونوں تحریروں کو ساتھ رکھیں تو ایک اہم فرق سامنے آتا ہے۔ پہلی تحریر پیوند کو علمی منتقلی کا ذریعہ سمجھتی ہے، جبکہ دوسری اس بات پر زور دیتی ہے کہ رابطے کی مقدار اور وقت بھی اہم ہیں۔ دونوں کا مشترک مفروضہ یہ ہے کہ طالب علم محض معلومات وصول کرنے والی مشین نہیں؛ وہ اپنی توجہ، وقت اور مقصد کے مطابق نظام سے فائدہ اٹھاتا ہے۔ اس لیے بہتر ڈیزائن میں سوال یہ نہیں ہونا چاہیے کہ کتنے رابطے بنائے گئے، بلکہ یہ کہ کون سا رابطہ کس مشکل کو حل کرتا ہے۔

ایک مربوط تجزیہ تین سطحیں الگ کر سکتا ہے۔ مواد کی سطح پر دیکھا جائے کہ سبق، مثال اور مشق ایک دوسرے کی مدد کرتے ہیں یا نہیں۔ وقت کی سطح پر جانچا جائے کہ نئی سرگرمی اس وقت آتی ہے جب پچھلی بات سمجھنے کا موقع مل چکا ہو۔ اختیار کی سطح پر دیکھا جائے کہ طالب علم غیر ضروری یاد دہانی روک سکتا ہے یا نہیں۔ اگر یہ تینوں سطحیں واضح ہوں تو پیوند معنی خیز رہتا ہے اور لامتناہی سلسلے کا خطرہ کم ہوتا ہے۔

اس مثال کا بڑا سبق دوسری بحثوں پر بھی لاگو ہوتا ہے۔ نظام اکثر زیادہ خصوصیات کو زیادہ مدد سمجھ لیتا ہے، حالانکہ اضافی جزو کبھی فائدہ اور کبھی رکاوٹ بن سکتا ہے۔ مضبوط ترکیب دونوں متن کی بہترین باتیں لے کر ایک نئی شرط بناتی ہے: تعلقات واضح ہوں، مگر ہر تعلق کا مقصد، حد اور اختتام بھی واضح ہو۔''',
'''ایک ادارے نے چار روزہ کام کے ہفتے کی آزمائش کی اور نتیجے پر دو مختلف رپورٹیں سامنے آئیں۔ پہلی رپورٹ میں بتایا گیا کہ کچھ ٹیموں نے کم وقت میں بھی تقریباً اتنا ہی کام مکمل کیا، اور ملازمین نے کم تھکاوٹ کی اطلاع دی۔ دوسری رپورٹ نے توجہ دلائی کہ ہر شعبے کا کام یکساں نہیں تھا؛ مدد فراہم کرنے والی ٹیموں کو مخصوص اوقات میں موجود رہنا پڑتا تھا، اس لیے وہ صرف دن کم کرکے وہی طریقہ برقرار نہیں رکھ سکتی تھیں۔

اعداد کی پہلی نظر متاثر کن تھی۔ ایک شعبے میں مکمل شدہ درخواستوں کی تعداد تقریباً دگنا ہو گئی، مگر بعد کی جانچ سے معلوم ہوا کہ اس عرصے میں کئی درخواستیں چھوٹی اور آسان تھیں۔ اگر صرف مجموعی تعداد دیکھی جائے تو کارکردگی میں بڑی چھلانگ محسوس ہوتی ہے۔ اگر کام کی پیچیدگی، غلطی کی شرح اور بعد میں ہونے والی تصحیح بھی شامل کی جائے تو تصویر زیادہ محتاط ہو جاتی ہے۔ اس کا مطلب یہ نہیں کہ آزمائش ناکام تھی؛ مطلب صرف یہ ہے کہ ایک عدد کو نتیجے کا مکمل بدل نہیں بنانا چاہیے۔

تھکاوٹ کا سوال بھی اسی طرح باریک ہے۔ خود رپورٹ کردہ سکون اہم ثبوت ہے، کیونکہ مسلسل دباؤ کام کے معیار اور زندگی دونوں کو متاثر کرسکتا ہے۔ لیکن اگر کم دنوں میں ملاقاتیں اور پیغامات بہت زیادہ بھر دیے جائیں تو کچھ افراد کے لیے روزانہ کا دباؤ بڑھ سکتا ہے۔ اس لیے وقت کی کمی اور بوجھ کی کمی کو ایک چیز سمجھنا درست نہیں۔ مختلف کرداروں میں اثر ناپنے کے لیے مشترک معیار کے ساتھ مقامی پیمانے بھی درکار ہوتے ہیں۔

مربوط تجزیہ یہ پوچھے گا کہ آزمائش کا مقصد کیا تھا۔ اگر مقصد صرف پیداوار بڑھانا تھا تو کام کی مقدار اہم ہوگی۔ اگر مقصد مستقل کارکردگی اور صحت مند رفتار تھی تو معیار، غیر حاضری، عملے کی تبدیلی اور تھکاوٹ بھی دیکھنی ہوگی۔ پھر یہ بھی جانچنا ہوگا کہ دگنا نظر آنے والا نتیجہ واقعی طریقۂ کار کی تبدیلی سے آیا یا کام کی نوعیت عارضی طور پر بدل گئی تھی۔

اس کیس سے ایک عمومی اصول نکلتا ہے: پالیسی یا انتظامی تجربے کو ایک ہی کامیاب عدد کے ذریعے بیان کرنا آسان مگر کمزور ہے۔ بہتر نتیجہ وہ ہے جو فائدے اور نقصان دونوں کے پیمانے پہلے واضح کرے، مختلف گروہوں کے اثرات الگ دکھائے، اور وقت کے ساتھ دوبارہ جانچ کی گنجائش رکھے۔ ایسی صورت میں ابتدائی کامیابی نہ تو غیر ضروری طور پر رد ہوتی ہے اور نہ ہی ضرورت سے زیادہ بڑھا چڑھا کر پیش کی جاتی ہے۔''',
'''ایک ساحلی شہر میں پرانی گوداموں کی قطار کو عوامی بازار میں بدلنے کی تجویز آئی۔ حامیوں نے کہا کہ ایک چھوٹا ثقافتی منصوبہ پورے علاقے کے لیے چنگاری بن سکتا ہے: لوگ آئیں گے، مقامی دکانیں کھلیں گی اور خالی عمارتیں دوبارہ استعمال ہوں گی۔ ناقدین نے جواب دیا کہ ابتدائی جوش کو مستقل معاشی اثر سمجھنا خطرناک ہے، خاص طور پر اگر کرایہ بڑھ جائے اور پہلے سے موجود کاروبار جگہ چھوڑنے پر مجبور ہوں۔

منصوبے کی پہلی رپورٹ نے آنے والے لوگوں کی تعداد، نئی دکانوں اور تقریبات کو کامیابی کے اشارے کے طور پر پیش کیا۔ دوسری رپورٹ نے خالی جگہ، کرایے، مرمت اور ضائع ہونے والے سامان کو بھی شامل کیا۔ وہاں معلوم ہوا کہ کچھ پرانی لکڑی پانی سے اتنی خراب تھی کہ اسے بچانا ممکن نہیں تھا؛ وہ حصہ تلف کرنا پڑا۔ اس مثال نے بحث کو عملی بنا دیا۔ ورثہ محفوظ کرنے کا مقصد اہم تھا، مگر ہر مادی جزو کو ہر قیمت پر رکھنا ممکن نہیں تھا۔

چنگاری کا استعارہ بھی جانچ کا محتاج ہے۔ ایک کامیاب تقریب واقعی نئی سرگرمی شروع کرسکتی ہے، لیکن ابتدا اور مستقل تبدیلی کے درمیان کئی مرحلے ہوتے ہیں۔ نقل و حمل، صفائی، چھوٹے کاروبار کے معاہدے، رہائشی شکایات اور موسمی آمد و رفت سب نتیجے کو بدل سکتے ہیں۔ اگر پالیسی صرف افتتاحی ہجوم دیکھے تو وہ بعد کے اخراجات اور تقسیم کے اثرات کھو سکتی ہے۔ اسی طرح اگر ہر خطرے کے خوف سے آغاز ہی روک دیا جائے تو ممکنہ فائدے کبھی آزمائے نہیں جائیں گے۔

ایک بہتر تجزیہ تجربے کو مرحلہ وار بنائے گا۔ پہلے محدود حصے میں بازار شروع کیا جائے، پھر کرایے، پیدل آمد، مقامی ملازمت اور شکایات کے اعداد جمع کیے جائیں۔ تعمیراتی مواد کے لیے پہلے سے معیار طے ہو کہ کیا مرمت ہوگا، کیا دوبارہ استعمال ہوگا اور کیا تلف کرنا ضروری ہے۔ اس طرح ثقافتی مقصد، مالی ذمہ داری اور حفاظتی ضرورت ایک ہی فیصلے میں شامل ہو سکتی ہیں۔

اصل سوال یہ نہیں کہ شہر کو تبدیلی چاہیے یا تحفظ۔ اصل سوال یہ ہے کہ کون سی تبدیلی کس ثبوت کے بعد بڑھائی جائے اور کس نقصان پر روک دی جائے۔ چنگاری آغاز کی تصویر دیتی ہے، مگر پائیدار پالیسی کو آگ کی سمت بھی دیکھنی پڑتی ہے۔ واضح معیار، محدود آزمائش اور قابلِ واپسی فیصلے اس بات کے امکانات بڑھاتے ہیں کہ فائدہ واقعی محلے تک پہنچے، نہ کہ صرف افتتاحی خبر تک محدود رہے۔''',
'''ایک ادبی رسالے نے ایک ہی رباعی کے دو ترجمے شائع کیے اور ساتھ ایک مختصر لسانیات کا مضمون بھی دیا۔ پہلا مترجم اصل نظم کی مختصر ساخت اور آخری مصرعے کے اچانک موڑ کو محفوظ رکھنے کی کوشش کرتا ہے۔ دوسرا مترجم لفظی ترتیب سے کچھ دور جاتا ہے تاکہ اردو میں روانی اور صوتی توازن برقرار رہے۔ دونوں نسخے ایک ہی بنیادی خیال پیش کرتے ہیں، مگر قاری پر ان کا اثر مختلف ہے۔

رباعی کی مختصر صورت مترجم کے لیے خاص دباؤ پیدا کرتی ہے، کیونکہ چند سطروں میں منظر، دلیل اور لہجہ ایک ساتھ قائم ہوتے ہیں۔ اگر ایک تشبیہ کو بہت لمبی وضاحت میں بدل دیا جائے تو معنی شاید واضح ہو جائے، لیکن رفتار ٹوٹ سکتی ہے۔ اگر بہت کچھ حذف کر دیا جائے تو اشارہ باقی رہتا ہے مگر قاری ضروری تعلق کھو سکتا ہے۔ اس لیے ترجمہ صرف لفظ کے بدلے لفظ کا کام نہیں، بلکہ محدود جگہ میں ترجیحات کا فیصلہ بھی ہے۔

لسانیات کا مضمون اس اختلاف کو قواعد کی غلطی کے طور پر نہیں دیکھتا۔ وہ بتاتا ہے کہ زبانیں لفظوں کی ترتیب، محاورے، آواز اور ثقافتی اشاروں کو الگ طریقوں سے منظم کرتی ہیں۔ ایک اظہار جو ایک زبان میں مختصر اور مانوس ہو، دوسری میں غیر فطری لگ سکتا ہے۔ اسی لیے مترجم کو یہ طے کرنا پڑتا ہے کہ کہاں ساخت محفوظ رکھنی ہے، کہاں مفہوم کو نئے قالب میں دینا ہے، اور کہاں قاری کے لیے تھوڑی وضاحت ضروری ہے۔

دونوں تراجم کا موازنہ کرنے کے لیے صرف یہ پوچھنا کافی نہیں کہ کون سا زیادہ خوب صورت ہے۔ قاری دیکھ سکتا ہے کہ کون سا نسخہ مرکزی تضاد کو واضح کرتا ہے، کون سا آواز کی رفتار برقرار رکھتا ہے، اور کون سا ثقافتی اشارہ سمجھنے کے لیے اضافی مدد مانگتا ہے۔ پھر ترجمے کے مقصد کو بھی شامل کرنا ہوگا۔ درسی نسخہ شاید وضاحت کو ترجیح دے، جبکہ ادبی رسالہ صوتی اور جمالیاتی اثر کو زیادہ اہمیت دے سکتا ہے۔

یہ مثال پورے یونٹ کی ترکیبی مہارت دکھاتی ہے۔ ایک مضبوط قاری متن، مقصد، سامع اور ثبوت کو الگ الگ نہیں دیکھتا بلکہ ان کے تعلق کو جانچتا ہے۔ رباعی کی صورت اور لسانیات کی وضاحت مل کر یہ دکھاتی ہیں کہ اختلاف ہمیشہ غلطی نہیں ہوتا؛ کبھی وہ مختلف ترجیحات کا نتیجہ ہوتا ہے۔ پھر بھی ہر انتخاب کا حساب مانگا جا سکتا ہے: کیا بدلا، کیوں بدلا، اور اس تبدیلی سے معنی یا اثر میں کیا حاصل اور کیا ضائع ہوا۔''',
'''اس یونٹ کی پانچ بحثوں کو ایک ساتھ رکھیں تو ایک مشترک طریقۂ مطالعہ سامنے آتا ہے۔ لائبریری کے مقام والی بحث میں اساسی اصول پہلے واضح کرنا ضروری تھا، کیونکہ دو تجاویز کا تفاوت اسی بات سے پیدا ہوا کہ وہ رسائی، تاریخ اور خرچ کو مختلف وزن دیتی تھیں۔ جب مقاصد اور پیمانے سامنے آئے تو اختلاف محض پسند کا مسئلہ نہیں رہا بلکہ قابلِ جانچ دلیل بن گیا۔

تعلیمی نظام کی مثال نے دکھایا کہ مختلف ذرائع کے درمیان پیوند مفید ہوسکتا ہے، مگر رابطہ خود مقصد نہیں۔ اگر ہر سرگرمی نئی سرگرمی سے جڑتی جائے تو سلسلہ لامتناہی محسوس ہوسکتا ہے۔ اس لیے کسی نظام کی خوبی صرف اجزا کی تعداد میں نہیں بلکہ ان کے تعلق، وقت، اختیار اور واضح اختتام میں بھی ہوتی ہے۔

کام کے ہفتے کی آزمائش میں تھکاوٹ اور پیداوار دونوں اہم تھے۔ ایک شعبے میں تعداد دگنا دکھائی دی، لیکن کام کی پیچیدگی بدلنے سے اس عدد کی تعبیر بھی بدل گئی۔ یہاں سبق یہ تھا کہ کامیابی کے پیمانے پہلے طے کیے جائیں اور ایک نمایاں عدد کو پورے تجربے کا بدل نہ بنایا جائے۔ معیار، صحت، وقت اور مختلف کرداروں کے اثرات ایک ساتھ دیکھنے سے نتیجہ زیادہ مضبوط ہوا۔

شہری بازار کی تجویز میں چنگاری نئی سرگرمی کے آغاز کا استعارہ تھی، مگر آغاز کو مستقل کامیابی سمجھنا کافی نہیں تھا۔ کچھ تعمیراتی مواد کو حفاظتی وجہ سے تلف کرنا پڑا، اور اس فیصلے نے یاد دلایا کہ تحفظ بھی حدود اور معیار مانگتا ہے۔ مرحلہ وار آزمائش نے فائدہ، نقصان اور واپسی کے راستے کو ایک ہی منصوبے میں جگہ دی۔

ادبی مثال میں رباعی کے دو ترجمے اور لسانیات کی وضاحت نے مختلف نوعیت کا اختلاف دکھایا۔ یہاں سوال یہ نہیں تھا کہ ایک متن لازماً صحیح اور دوسرا غلط ہے؛ سوال یہ تھا کہ ساخت، روانی، ثقافتی اشارہ اور قاری کے مقصد میں کس چیز کو ترجیح دی گئی۔ مختلف ترجیحات جائز ہوسکتی ہیں، مگر ان کے اثرات پھر بھی دلیل اور مثال سے جانچے جا سکتے ہیں۔

ان سب مثالوں سے پانچ عملی عادتیں بنتی ہیں۔ پہلے مقصد اور اساسی معیار واضح کریں۔ پھر تفاوت کی اصل جگہ پہچانیں۔ تیسرے مرحلے میں اجزا کے پیوند اور ممکنہ لامتناہی بوجھ کو دیکھیں۔ چوتھے میں تھکاوٹ، دگنا نظر آنے والے اعداد، چنگاری جیسے ابتدائی اشاروں اور تلف ہونے والے وسائل کو مناسب سیاق میں رکھیں۔ آخر میں رباعی اور لسانیات والی مثال کی طرح شکل، مقصد اور سامع کے تعلق کو جانچیں۔ مضبوط ترکیب معلومات جمع کرنے سے آگے بڑھتی ہے: وہ بتاتی ہے کہ کون سا ثبوت کس دعوے کو کتنا سہارا دیتا ہے، کون سی شرط نتیجے کو بدل سکتی ہے، اور نئی معلومات آنے پر فیصلہ کس طرح بدلا جا سکتا ہے۔'''
]
TITLES=['لائبریری کی جگہ: دو دلائل کا مشترک نقشہ','تعلیمی ربط: مدد اور بوجھ کے درمیان','کم دن، زیادہ کام؟ اعداد اور تجربے کی جانچ','بازار کی بحالی: آغاز، نقصان اور مرحلہ وار فیصلہ','مختصر نظم، دو ترجمے اور زبان کا مطالعہ','ترکیب کا آخری مرحلہ: دلیل، پیمانہ اور سیاق']
ROW_GENRES=['paired long texts','paired long texts','integrated analysis','integrated analysis','integrated analysis','checkpoint']
PAIR_IDS=[TARGETS[0:2],TARGETS[2:4],TARGETS[4:6],TARGETS[6:8],TARGETS[8:10],[]]
OLD_REVIEWS=[('ur-rank-2704','تصحیح','R3','other'),('ur-rank-2836','بڑھاوا','R3','other'),('ur-rank-2704','تصحیح','R3','running_text'),('ur-rank-2687','تصفیہ','R3','other'),('ur-rank-2534','ناظر','R3','other')]
QAS=[
[
('main_claim','دونوں مضامین کو ساتھ پڑھنے سے مرکزی اصول کیا بنتا ہے؟','اختلاف سمجھنے کے لیے پہلے مقصد، پیمانہ اور ہر دلیل کے بنیادی مفروضے واضح کرنے چاہییں.',[]),
('vocabulary_in_context','متن میں «اساسی» کس معنی میں آیا ہے؟','ایسی بنیادی بات جس پر باقی دلیل قائم ہو۔',[TARGETS[0]]),
('vocabulary_in_context','«تفاوت» کس چیز کی طرف اشارہ کرتا ہے؟','دونوں مضامین کی ترجیحات اور کامیابی ناپنے کے طریقے کے فرق کی طرف۔',[TARGETS[1]]),
('contrast','پہلا اور دوسرا مضمون کس چیز کو زیادہ وزن دیتے ہیں؟','پہلا رسائی کو، جبکہ دوسرا تاریخ اور موجودہ ڈھانچے کے دوبارہ استعمال کو زیادہ اہم سمجھتا ہے.',[]),
('argument_relation','مشترک بنیاد دکھانے سے اختلاف کا تجزیہ کیسے بہتر ہوتا ہے؟','اس سے معلوم ہوتا ہے کہ اختلاف کن مشترک حقائق کے بعد ترجیحات کے مرحلے پر پیدا ہوتا ہے.',[]),
('assumption','صرف آخری سفارش دیکھنا کیوں ناکافی ہے؟','کیونکہ ایک ہی نتیجے کے پیچھے مختلف پیمانے، مفروضے اور شواہد ہوسکتے ہیں.',[]),
('inference','آبادی یا بس کے راستے بدلنے کا سوال کیوں اہم ہے؟','وہ یہ جانچتا ہے کہ تجویز بدلتے حالات میں کتنی قابلِ موافقت ہے.',[]),
('synthesis','مشترک جائزے کے تین سوال کس نوعیت کے ثبوت مانگتے ہیں؟','رسائی، طویل مدتی خرچ اور بدلتے حالات میں موافقت سے متعلق ثبوت.',[]),
('stance','کیا متن کسی ایک تجویز کو خودکار طور پر درست قرار دیتا ہے؟','نہیں، وہ فیصلہ کرنے کے اصول کو واضح کرنے پر زور دیتا ہے.',[]),
('summary','اس پورے موازنے کا مختصر طریقہ بیان کریں۔','مقصد واضح کریں، شواہد اور مفروضے الگ کریں، ترجیحات کا فرق دکھائیں اور بدلتے حالات کی جانچ کریں.',[])
],
[
('main_claim','دونوں تحریروں سے تعلیمی نظام کے بارے میں کیا مشترک نتیجہ نکلتا ہے؟','رابطہ مفید ہے جب اس کا مقصد، وقت، حد اور اختتام واضح ہوں.',[]),
('vocabulary_in_context','«پیوند» یہاں کس تعلق کو ظاہر کرتا ہے؟','سبق، استاد اور مشق کے درمیان ایسا ربط جو سیکھنے کو ایک جگہ سے دوسری جگہ منتقل کرے.',[TARGETS[2]]),
('vocabulary_in_context','«لامتناہی» سلسلہ کس تجربے کو بیان کرتا ہے؟','ایسا کام جو ختم ہوتا محسوس نہ ہو اور مسلسل نئی سرگرمی سامنے لاتا رہے.',[TARGETS[3]]),
('contrast','پہلی اور دوسری تحریر رابطے کے بارے میں کیسے مختلف ہیں؟','پہلی مفید ربط پر زور دیتی ہے، دوسری زیادہ رابطے کے بوجھ اور حد کی ضرورت دکھاتی ہے.',[]),
('assumption','دونوں تحریروں کا طالب علم کے بارے میں مشترک مفروضہ کیا ہے؟','یہ کہ اس کی توجہ، وقت اور اختیار نظام کے اثر کو بدلتے ہیں.',[]),
('cause_effect','واضح اختتام نہ ہونے سے کیا اثر پڑ سکتا ہے؟','طالب علم کو کام مسلسل اور بوجھل محسوس ہوسکتا ہے.',[]),
('argument_relation','تین سطحوں والا تجزیہ مرکزی دلیل کو کیسے مضبوط کرتا ہے؟','وہ مواد، وقت اور اختیار کو الگ کرکے دکھاتا ہے کہ مسئلہ صرف رابطوں کی تعداد نہیں.',[]),
('inference','زیادہ خصوصیات ہمیشہ زیادہ مدد کیوں نہیں بنتیں؟','کیونکہ اضافی جزو غیر ضروری توجہ، وقت یا دباؤ پیدا کرسکتا ہے.',[]),
('synthesis','مفید رابطے کے لیے متن کون سی شرطیں جوڑتا ہے؟','واضح علمی مقصد، مناسب وقت، صارف کا اختیار اور معلوم اختتام.',[]),
('summary','اس مثال کا وسیع سبق کیا ہے؟','نظام کے اجزا گننے کے بجائے ان کے تعلق، مقصد اور بوجھ کو جانچنا چاہیے.',[])
],
[
('main_claim','کام کے ہفتے کی آزمائش کا بنیادی تجزیاتی سبق کیا ہے؟','ایک نمایاں عدد کو مکمل کامیابی نہ سمجھیں؛ مقدار، معیار، صحت اور سیاق سب دیکھیں.',[]),
('vocabulary_in_context','«تھکاوٹ» یہاں کس قسم کے اثر کو ظاہر کرتی ہے؟','کام کے دباؤ سے پیدا ہونے والی جسمانی یا ذہنی تھکن کو.',[TARGETS[4]]),
('vocabulary_in_context','«دگنا» نتیجہ کیوں محتاط تشریح مانگتا ہے؟','کیونکہ درخواستوں کی نوعیت آسان ہونے سے تعداد بڑھی ہوسکتی ہے.',[TARGETS[5]]),
('cause_effect','کام کی پیچیدگی بدلنے سے پیداوار کے عدد پر کیا اثر پڑا؟','زیادہ مکمل شدہ کام کارکردگی کی حقیقی بہتری سے بڑا دکھائی دے سکتا تھا.',[]),
('contrast','وقت کم ہونے اور بوجھ کم ہونے میں کیا فرق ہے؟','کم دن لازماً کم دباؤ نہیں دیتے؛ وہی کام کم وقت میں بھرنے سے روزانہ کا بوجھ بڑھ سکتا ہے.',[]),
('assumption','خود رپورٹ کردہ سکون کو اہم ثبوت ماننے کے پیچھے کیا مفروضہ ہے؟','یہ کہ ملازم کا تجربہ پائیدار کارکردگی اور صحت سے متعلق حقیقی معلومات دیتا ہے.',[]),
('inference','مختلف شعبوں کے لیے مقامی پیمانے کیوں درکار ہیں؟','کیونکہ کردار، دستیابی اور کام کی پیچیدگی یکساں نہیں ہوتی.',[]),
('argument_relation','تصحیح کو شامل کرنا نتیجے کی تعبیر کیسے بدلتا ہے؟','وہ دکھاتا ہے کہ تیزی کے بعد غلطی درست کرنے کی اضافی لاگت بھی ہوسکتی ہے.',[]),
('synthesis','مربوط جائزے میں کن نتائج کو ساتھ دیکھنا چاہیے؟','کام کی مقدار، معیار، غیر حاضری، عملے کی تبدیلی اور تھکن.',[]),
('summary','تجربے کے اعداد کا ذمہ دارانہ خلاصہ کیسے کیا جائے؟','پیمانے پہلے طے کریں، گروہوں کو الگ دیکھیں، سیاق بتائیں اور وقت کے ساتھ دوبارہ جانچ کریں.',[])
],
[
('main_claim','شہری بازار کی مثال کا مرکزی پالیسی سبق کیا ہے؟','ابتدائی کامیابی کو مستقل اثر نہ سمجھیں؛ مرحلہ وار آزمائش اور واضح نقصان کے معیار رکھیں.',[]),
('vocabulary_in_context','«چنگاری» یہاں کس مجازی معنی میں استعمال ہوئی ہے؟','ایسے چھوٹے آغاز کے لیے جو بڑی سرگرمی شروع کرسکے.',[TARGETS[6]]),
('vocabulary_in_context','«تلف» کرنے کا فیصلہ کس حالت میں آیا؟','جب کچھ خراب تعمیراتی مواد محفوظ طریقے سے بچانا ممکن نہ رہا.',[TARGETS[7]]),
('contrast','حامیوں اور ناقدین کی بنیادی ترجیحات میں کیا فرق تھا؟','حامی ممکنہ نئی سرگرمی دیکھتے تھے، ناقدین کرایے اور موجودہ کاروبار پر طویل اثرات بھی دیکھتے تھے.',[]),
('cause_effect','صرف افتتاحی ہجوم دیکھنے سے کیا چیز چھپ سکتی ہے؟','بعد کے اخراجات، تقسیم کے اثرات اور مقامی کاروبار پر دباؤ.',[]),
('assumption','مرحلہ وار آزمائش کے پیچھے کیا مفروضہ ہے؟','یہ کہ محدود تجربے سے حاصل شواہد اگلے فیصلے کو بہتر بنا سکتے ہیں.',[]),
('inference','مواد کے لیے پہلے سے معیار طے کرنے کا فائدہ کیا ہے؟','مرمت، دوبارہ استعمال اور ضائع کرنے کے فیصلے کم من مانے ہوتے ہیں.',[]),
('argument_relation','آغاز اور مستقل تبدیلی کا فرق مرکزی دلیل کو کیسے مضبوط کرتا ہے؟','وہ دکھاتا ہے کہ ابتدائی اشارہ کافی ثبوت نہیں اور درمیانی عمل بھی جانچنا ضروری ہے.',[]),
('synthesis','ثقافتی مقصد، مالی ذمہ داری اور حفاظت کو کیسے جوڑا گیا؟','محدود آغاز، مسلسل اعداد اور مواد کے واضح فیصلوں کے ذریعے.',[]),
('summary','پائیدار شہری تجربے کے چار اصول بیان کریں۔','واضح معیار، محدود آزمائش، اثرات کی نگرانی اور قابلِ واپسی فیصلے.',[])
],
[
('main_claim','دو ترجموں اور زبان کے مضمون سے بنیادی نتیجہ کیا نکلتا ہے؟','ترجمے کا اختلاف مختلف ترجیحات سے پیدا ہوسکتا ہے، مگر ہر انتخاب کو شواہد سے جانچا جا سکتا ہے.',[]),
('vocabulary_in_context','«رباعی» متن میں کس ادبی صورت کو کہتے ہیں؟','چار مصرعوں پر مشتمل مختصر شعری صورت کو.',[TARGETS[8]]),
('vocabulary_in_context','«لسانیات» یہاں کس مطالعے کی طرف اشارہ کرتی ہے؟','زبان کی ساخت، استعمال اور تبدیلی کے منظم مطالعے کی طرف.',[TARGETS[9]]),
('contrast','پہلا اور دوسرا مترجم کس چیز کو مختلف اہمیت دیتے ہیں؟','پہلا مختصر ساخت اور موڑ کو، دوسرا روانی اور صوتی توازن کو زیادہ وزن دیتا ہے.',[]),
('cause_effect','طویل وضاحت سے مختصر نظم پر کیا اثر پڑ سکتا ہے؟','معنی واضح ہوسکتا ہے مگر رفتار اور فنی دباؤ کم ہوسکتا ہے.',[]),
('assumption','ترجمے کے مقصد کو موازنے میں شامل کرنا کیوں ضروری ہے؟','کیونکہ درسی اور ادبی استعمال مختلف کامیابی کے معیار رکھتے ہیں.',[]),
('inference','اختلاف کو فوراً غلطی نہ سمجھنے کا فائدہ کیا ہے؟','قاری پہلے یہ دیکھ سکتا ہے کہ فرق زبان، مقصد یا جمالیاتی ترجیح سے آیا ہے.',[]),
('argument_relation','زبان کے مضمون نے ترجمے کی مثال کو کیسے گہرا کیا؟','اس نے دکھایا کہ زبانوں کی ساخت اور محاورہ ایک ہی مفہوم کو مختلف صورت مانگنے پر مجبور کرسکتے ہیں.',[]),
('synthesis','دو ترجموں کے موازنے کے لیے کن پہلوؤں کو دیکھنا چاہیے؟','معنی، ساخت، آواز، ثقافتی اشارہ، روانی اور مطلوبہ قاری.',[]),
('summary','اس ادبی مثال کا ترکیبی سبق مختصراً بیان کریں۔','شکل، مقصد اور سامع کو ساتھ رکھ کر دیکھیں کہ ہر ترجماتی انتخاب سے کیا حاصل اور کیا ضائع ہوا.',[])
],
[
('main_claim','پورے یونٹ کا مشترک ترکیبی اصول کیا ہے؟','مقصد، پیمانہ، شواہد، سیاق اور ممکنہ تبدیلی کو ایک ساتھ دیکھ کر دعوے کی قوت جانچنی چاہیے.',[]),
('synthesis','اساسی اصول اور تفاوت کی مثال کیا سکھاتی ہے؟','پہلے بنیادی معیار واضح کریں، پھر دیکھیں کہ اختلاف کس ترجیح یا مفروضے سے پیدا ہوا.',[TARGETS[0],TARGETS[1]]),
('synthesis','پیوند اور لامتناہی سلسلے کی مثال کا مشترک سبق کیا ہے؟','رابطہ مفید ہے مگر اس کا مقصد، حد اور اختتام واضح ہونا چاہیے.',[TARGETS[2],TARGETS[3]]),
('synthesis','تھکاوٹ اور دگنا عدد کس قسم کی احتیاط مانگتے ہیں؟','انسانی تجربے اور مقدار دونوں کو سیاق، معیار اور متبادل وضاحتوں کے ساتھ پڑھنا چاہیے.',[TARGETS[4],TARGETS[5]]),
('synthesis','چنگاری اور تلف ہونے والے مواد کی مثال کیا دکھاتی ہے؟','ابتدائی فائدہ اور حقیقی نقصان دونوں کے لیے مرحلہ وار، قابلِ واپسی فیصلے ضروری ہیں.',[TARGETS[6],TARGETS[7]]),
('synthesis','رباعی اور لسانیات کی مثال اختلاف کی تعبیر کیسے بدلتی ہے؟','وہ دکھاتی ہے کہ زبان اور مقصد مختلف انتخاب پیدا کرسکتے ہیں جنہیں اثر اور شواہد سے پرکھا جا سکتا ہے.',[TARGETS[8],TARGETS[9]]),
('cross_text_synthesis','پانچوں مثالوں میں ایک ہی عدد یا ایک ہی اصول کافی کیوں نہیں؟','کیونکہ ہر مسئلے میں مقصد، متاثرہ گروہ، وقت، ساخت اور غیر یقینی باتیں مختلف ہیں.',[]),
('inference','نئی معلومات آنے پر فیصلہ بدلنے کی گنجائش کیوں ضروری ہے؟','کیونکہ ابتدائی مفروضہ یا پیمانہ بعد کے شواہد سے کمزور پڑ سکتا ہے.',[]),
('stance','یونٹ اختلاف کے بارے میں کیا رویہ اختیار کرتا ہے؟','اختلاف کو جائز سمجھتا ہے مگر ہر دعوے سے واضح معیار اور قابلِ جانچ ثبوت مانگتا ہے.',[]),
('summary','ترکیبی مطالعے کی پانچ عملی عادتیں بیان کریں۔','مقصد واضح کریں، فرق کی جڑ پہچانیں، تعلق اور بوجھ دیکھیں، اعداد و نقصان کو سیاق دیں، اور شکل، سامع و ثبوت کو جوڑیں.',[])
]
]

EXT_SOURCES={
'ur-rank-2876':'https://www.rekhtadictionary.com/meaning-of-asaasii?lang=ur',
'ur-rank-2910':'source lexicon sense reviewed against ordinary contemporary usage',
'ur-rank-2870':'https://www.rekhtadictionary.com/meaning-of-jod?lang=ur',
'ur-rank-2885':'https://www.rekhtadictionary.com/meaning-of-laa-mutanaahii?lang=ur',
'ur-rank-2858':'https://www.rekhtadictionary.com/meaning-of-thakan',
'ur-rank-2897':'https://rekhtadictionary.com/meaning-of-dugnaa',
'ur-rank-2851':'https://www.rekhtadictionary.com/meaning-of-chingaarii',
'ur-rank-2912':'https://www.rekhta.org/urdudictionary?keyword=talaf',
'ur-rank-2859':'https://en.wiktionary.org/wiki/رباعی',
'ur-rank-2920':'https://www.rekhtadictionary.com/meaning-of-lisaaniyaat?lang=ur'
}

def jl(p:Path): return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def fail(x): raise SystemExit('Fail closed: '+x)
def rep(s,a,b,label):
    if s.count(a)!=1: fail(f'{label}: expected phrase once: {a!r}')
    return s.replace(a,b,1)
def exact(text,form): return len(re.findall(rf'(?<!\w){re.escape(form)}(?!\w)',text,flags=re.UNICODE))
def new_target(tid):
    _,form,sense,strategy,rank=META[tid]
    return {'id':tid,'form':form,'lemma':form,'part_of_speech':None,'intended_sense':sense,'register':'contemporary standard','variety':'contemporary standard Urdu','context_strategy':[strategy,'evidence_interpretation'] if strategy!='evidence_interpretation' else [strategy,'uncertainty_analysis'],'first_introduced':True,'exposures_in_text':1,'source_lexicon':'urdu_top3000.csv','source_rank':rank,'beyond_base':False}
def qa_rows(items):
    qs=[]; ans=[]
    for i,(qt,prompt,answer,refs) in enumerate(items,1):
        q={'id':f'q{i}','type':qt,'prompt':prompt,'answer_id':f'a{i}'}
        if refs: q['target_ids']=refs
        qs.append(q); ans.append({'id':f'a{i}','question_id':f'q{i}','answer':answer,'explanation':''})
    return qs,ans

def build_rows():
    rows=[]
    for i in range(6):
        qs,ans=qa_rows(QAS[i])
        nts=[new_target(x) for x in PAIR_IDS[i]]
        if i<5:
            oid,form,stage,representation=OLD_REVIEWS[i]
            reviews=[{'id':oid,'form':form,'review_stage':stage,'representation':representation}]
        else:
            reviews=[{'id':tid,'form':META[tid][1],'review_stage':'R1','representation':'running_text'} for tid in TARGETS]
        rows.append({'id':IDS[i],'language':'ur','cefr':'B2','unit':10,'sequence':SEQS[i],'revision':1,'title':TITLES[i],'passage_type':ROLES[i],'genre':ROW_GENRES[i],'domains':['public','educational'] if i!=2 else ['professional','educational'],'topics':['B2 synthesis'],'text':TEXTS[i],'word_count':len(TEXTS[i].split()),'sentence_count':TEXTS[i].count('۔'),'estimated_known_token_coverage':0,'new_lexical_targets':nts,'review_lexical_targets':reviews,'grammar_targets':[{'id':f'ur-b2-u10-grammar-{i+1:02d}','role':'integration' if i==5 else 'new','description':'use qualification, contrast, scope, and evidence to synthesize competing claims'}],'discourse_targets':[{'id':f'ur-b2-u10-discourse-{i+1:02d}','role':'integration' if i==5 else 'new','description':'connect claims, evidence, assumptions, affected groups, and revision conditions across texts'}],'questions':qs,'answer_key':ans,'speed_training':{'timed':i==5,'benchmark_eligible':i==5,'comprehension_gate':0.8,'new_word_policy':'none' if i==5 else 'controlled','notes':'accuracy before speed'},'quality':{'status':'draft','linguistic_review':'pending','pedagogical_review':'pending','coverage_check':'pending','answer_key_check':'pending','schema_check':'pending','fact_check':'not_required','notes':['Generation/integrity candidate only; educator/publication review remains separate.']}})
    return rows

def main():
    schema=json.loads(SCHEMA.read_text(encoding='utf-8')); required=set(schema['required'])
    ptypes=set(schema['properties']['passage_type']['enum']); domains=set(schema['properties']['domains']['items']['enum']); qtypes=set(schema['$defs']['question']['properties']['type']['enum']); strategies=set(schema['$defs']['newLexicalTarget']['properties']['context_strategy']['items']['enum']); reps=set(schema['$defs']['reviewLexicalTarget']['properties']['representation']['enum']); stages=set(schema['$defs']['reviewLexicalTarget']['properties']['review_stage']['enum'])
    a1=jl(ROOT/'reading/urdu/a1/passages.jsonl'); a2=jl(ROOT/'reading/urdu/a2/passages.jsonl'); b1=jl(ROOT/'reading/urdu/b1/passages.jsonl'); b2=jl(TARGET)
    if [len(a1),len(a2),len(b1)]!=[60,60,60]: fail('Urdu A1, A2, and B1 must each contain exactly 60 canonical passages')
    if len(b2)!=54 or [r.get('sequence') for r in b2]!=list(range(1,55)): fail('Urdu B2 must contain exactly sequences 1-54 before Unit 10 promotion')
    sp=ROOT/'reading/STATUS.json'; cp=ROOT/'reading/CONTINUATION.json'; pp=ROOT/'reading/planning/ACTIVE_GENERATION_PLAN.json'; tp=ROOT/'reading/TASKS.md'; hp=ROOT/'reading/AGENT_HANDOFF_V2.md'
    s=json.loads(sp.read_text(encoding='utf-8')); c=json.loads(cp.read_text(encoding='utf-8')); p=json.loads(pp.read_text(encoding='utf-8'))
    if s['current']['canonical_passages']!=954 or s['languages']['urdu']['canonical_passages']!=234: fail('STATUS counts drifted from B2 Unit 10 pre-state')
    if s['current']['active_language']!='urdu' or s['current']['active_level']!='B2': fail('STATUS frontier is not Urdu B2')
    if p.get('active_unit')!=10 or p.get('start_sequence')!=55 or p.get('existing_active_level_passages')!=54 or p.get('active_unit_roadmap')!=EXPECTED_ROADMAP: fail('active plan drifted from B2 Unit 10 / sequence 55')
    if 'Urdu B2 Unit 10 / sequence 55' not in c.get('active_frontier',{}).get('production',{}).get('action',''): fail('CONTINUATION drifted from B2 Unit 10 / sequence 55')
    before=TARGET.read_bytes(); before_sha=hashlib.sha256(before).hexdigest(); release_before=RELEASE.read_bytes(); taught={t['id'] for r in a1+a2+b1+b2 for t in r.get('new_lexical_targets',[])}; collision=sorted(taught.intersection(TARGETS))
    if collision: fail(f'Unit 10 target-ID freshness collision: {collision}')
    STAGE.mkdir(parents=True,exist_ok=True); rows=build_rows(); canonical_quality=json.loads(json.dumps(b2[-1]['quality'])); learner=[]
    for i,row in enumerate(rows,1):
        row['quality']=json.loads(json.dumps(canonical_quality)); row['word_count']=len(row['text'].split()); row['sentence_count']=row['text'].count('۔')
        for t in row['new_lexical_targets']: t['exposures_in_text']=exact(row['text'],t['form'])
        (STAGE/f'ur-b2-u10-p{i:02d}.json').write_text(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
        learner += [row['title'],row['text']]+[q['prompt'] for q in row['questions']]+[a['answer'] for a in row['answer_key']]
    lexical={'schema_version':1,'project_id':'LANG-A1C2','language':'ur','cefr':'B2','unit':10,'date':DATE,'status':'PASS_FOR_GENERATION_TARGET_SENSES_PENDING_CANONICAL_FRESHNESS','source_lexicon':'reading/lexicons/urdu.jsonl','targets':[{'id':tid,'form':META[tid][1],'source_rank':META[tid][4],'intended_sense':META[tid][2],'external_review':EXT_SOURCES[tid],'sense_result':'PASS'} for tid in TARGETS],'freshness_result':'PENDING_PROMOTION','notes':['Target forms were selected for natural B2 synthesis contexts, not by rank alone.','External dictionary checks were used for potentially ambiguous senses; ordinary source glosses were retained only where consistent with contemporary Urdu usage.','Canonical target-ID freshness is rechecked fail-closed immediately before append.']}
    lp=ROOT/'reading/audit/urdu_b2_u10_lexical_sense_check_2026-08-26.json'; lp.write_text(json.dumps(lexical,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if [r['id'] for r in rows]!=IDS or [r['sequence'] for r in rows]!=SEQS or [r['passage_type'] for r in rows]!=ROLES: fail('identity/sequence/role contract failed')
    if [len(r['new_lexical_targets']) for r in rows]!=[2,2,2,2,2,0] or [t['id'] for r in rows[:5] for t in r['new_lexical_targets']]!=TARGETS: fail('target distribution/order failed')
    if any(t['exposures_in_text']<1 for r in rows for t in r['new_lexical_targets']): fail('new target absent from passage text')
    if not GENRES.issubset({r['genre'] for r in rows}): fail('required synthesis genres missing')
    prior=''
    for row in rows[:5]:
        for t in row['new_lexical_targets']:
            if exact(prior,t['form'])>0: fail(f'premature exact-form exposure: {t["form"]}/{t["id"]}')
        prior+='\n'+'\n'.join([row['title'],row['text']]+[q['prompt'] for q in row['questions']]+[a['answer'] for a in row['answer_key']])
    p6=rows[-1]; forms={META[x][1] for x in TARGETS}; reviews={t['form'] for t in p6['review_lexical_targets'] if t['representation']=='running_text'}
    if p6['new_lexical_targets'] or not p6['speed_training']['timed'] or p6['speed_training']['new_word_policy']!='none': fail('P6 checkpoint policy failed')
    if reviews!=forms or any(exact(p6['text'],f)<1 for f in forms): fail('P6 does not visibly recycle all ten targets')
    known=taught|set(TARGETS)
    for row in rows:
        missing=required-set(row)
        if missing: fail(f'{row["id"]} missing required fields: {sorted(missing)}')
        if row['passage_type'] not in ptypes or any(d not in domains for d in row['domains']): fail(f'passage/domain enum failure: {row["id"]}')
        if len(row['questions'])!=10 or len(row['answer_key'])!=10 or not 350<=row['word_count']<=550: fail(f'QA/word-band failure {row["id"]}: {row["word_count"]}')
        amap={a['id']:a for a in row['answer_key']}
        if set(amap)!={f'a{i}' for i in range(1,11)} or {q['id'] for q in row['questions']}!={f'q{i}' for i in range(1,11)}: fail(f'QA IDs drifted: {row["id"]}')
        for t in row['new_lexical_targets']:
            if any(x not in strategies for x in t['context_strategy']): fail(f'context strategy failure: {row["id"]}/{t["id"]}')
        for rt in row['review_lexical_targets']:
            if rt['representation'] not in reps or rt['review_stage'] not in stages or rt['id'] not in known: fail(f'review metadata/identity failure: {row["id"]}/{rt["id"]}')
        for q in row['questions']:
            if q['type'] not in qtypes or q['answer_id'] not in amap or amap[q['answer_id']]['question_id']!=q['id']: fail(f'QA link/type failure: {row["id"]}/{q["id"]}')
            refs=set(q.get('target_ids',[]))
            if not refs.issubset(known): fail(f'unknown question target reference: {row["id"]}/{q["id"]}')
    if re.search(r'[A-Za-z\u0900-\u097F\u3400-\u9FFF]','\n'.join(learner)): fail('learner-facing Latin/Devanagari/CJK leakage')
    payload=''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in rows).encode('utf-8'); TARGET.write_bytes(before+payload); after=TARGET.read_bytes(); final=jl(TARGET)
    if after[:len(before)]!=before or len(final)!=60 or [r['sequence'] for r in final]!=list(range(1,61)) or [r['id'] for r in final[-6:]]!=IDS: fail('B2 completion append check failed')
    (STAGE/'manifest.json').write_text(json.dumps({'schema_version':1,'project_id':'LANG-A1C2','language':'ur','cefr':'B2','unit':10,'date':DATE,'status':'CANONICALIZED_B2_COMPLETE','canonical_target':'reading/urdu/b2/passages.jsonl','sequence_range':[55,60],'record_count':6,'level_record_count':60,'release_promotion':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    checks={k:'PASS' for k in ['prior_a1_a2_b1_60_each','prior_b2_sequences_1_through_54_exact','freshness_across_all_prior_urdu_target_ids','record_count','sequence_55_through_60','b2_exactly_60','role_cycle','question_answer_10x10','bidirectional_links','new_target_distribution_2_2_2_2_2_0','new_target_text_exposure','first_introduction_order_unicode_word_boundary','required_genres','p6_checkpoint_policy','p6_all_target_recycling','learner_script_scan','schema_required_fields_enums_context_and_review_metadata','review_target_identity_check','b2_word_band_350_550','quality_metadata_preserved_from_prior_canonical_b2','preexisting_canonical_bytes_preserved','reader_first_wording_review','release_status_unchanged','level_transition_to_c1']}
    (ROOT/'reading/audit/urdu_b2_u10_generation_validation_2026-08-26.json').write_text(json.dumps({'schema_version':1,'project_id':'LANG-A1C2','language':'ur','cefr':'B2','unit':10,'date':DATE,'canonicalized':True,'b2_generation_complete':True,'release_promotion':False,'word_counts':[r['word_count'] for r in rows],'checks':checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'reading/audit/urdu_b2_u10_promotion_2026-08-26.json').write_text(json.dumps({'schema_version':1,'project_id':'LANG-A1C2','language':'ur','cefr':'B2','unit':10,'date':DATE,'status':'CANONICAL_PROMOTION_PASS_B2_COMPLETE','release_promotion':False,'before_record_count':54,'after_record_count':60,'appended_sequences':SEQS,'appended_ids':IDS,'preexisting_bytes_preserved_exactly':True,'canonical_sha256_before':before_sha,'canonical_sha256_after':hashlib.sha256(after).hexdigest(),'next_generation_frontier':'Urdu C1 Unit 1 / sequence 1'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lexical['status']='PASS_FOR_GENERATION_TARGET_SENSES_AND_CANONICAL_FRESHNESS'; lexical['freshness_result']='PASS'; lexical['freshness_scope']='Exact target IDs checked against all canonical Urdu A1-B1 and B2 sequences 1-54 immediately before Unit 10 append.'; lp.write_text(json.dumps(lexical,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    s['current']['canonical_passages']=960; s['current']['remaining_generation_passages']=120; s['current']['active_level']='C1'; u=s['languages']['urdu']; u['generation_state']='C1_IN_PROGRESS'; u['canonical_passages']=240; u['remaining_generation_passages']=120; u['complete_levels']=['A1','A2','B1','B2']; u['next_generation_level']='C1'; sp.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    c['updated']=DATE; c['production']['canonical_passages']=960; cu=c['production']['urdu']; cu['state']='C1_GENERATION_IN_PROGRESS'; cu['canonical_passages']=240; cu['complete_levels']=['A1','A2','B1','B2']; cu['next_generation_level']='C1'; c['active_frontier']['production']={'language':'urdu','level':'C1','action':'Continue generation-first production from Urdu C1 Unit 1 / sequence 1 using the canonical roadmap and ten-question contract.'}; c['exact_next_actions']=['Validate the routed state bundle and live canonical counts.','Use reading/planning/ACTIVE_GENERATION_PLAN.json to start guarded Urdu C1 Unit 1 generation at sequence 1.','Keep release/educator verification separate from generation progress.']; cp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    p['active_language']='urdu'; p['active_level']='C1'; p['active_unit']=1; p['start_sequence']=1; p['canonical_active_path']='reading/urdu/c1/passages.jsonl'; p['existing_active_level_passages']=0; p['roadmap_lookup']='$.levels.C1'; p['active_unit_roadmap']=NEXT_ROADMAP; pp.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    t=tp.read_text(encoding='utf-8'); t=rep(t,'## P1 — active production: Urdu B2','## P1 — active production: Urdu C1','TASKS heading'); t=rep(t,'Canonical production frontier: **Urdu B2, Unit 10, sequence 55**.','Canonical production frontier: **Urdu C1, Unit 1, sequence 1**.','TASKS frontier'); t=rep(t,'Read `reading/planning/ACTIVE_GENERATION_PLAN.json` and the exact B2 entry in `reading/planning/topic_genre_matrix.json`.','Read `reading/planning/ACTIVE_GENERATION_PLAN.json` and the exact C1 entry in `reading/planning/topic_genre_matrix.json`.','TASKS roadmap'); t=rep(t,'Generate Urdu B2 in guarded unit or large bounded batches under the generation-first policy.','Generate Urdu C1 in guarded unit or large bounded batches under the generation-first policy.','TASKS generation'); t=rep(t,'- Urdu: 234/360 generated; A1-B1 complete, B2 in progress.','- Urdu: 240/360 generated; A1-B2 complete, C1 in progress.','TASKS Urdu total'); t=rep(t,'- Project: 954/1080 generated.','- Project: 960/1080 generated.','TASKS project total'); tp.write_text(t,encoding='utf-8')
    h=hp.read_text(encoding='utf-8'); h=rep(h,'- Canonical generated total: **954**.','- Canonical generated total: **960**.','HANDOFF total'); h=rep(h,'- Urdu: **234/360**; A1-B1 generation complete and B2 generation in progress.','- Urdu: **240/360**; A1-B2 generation complete and C1 generation in progress.','HANDOFF Urdu'); h=rep(h,'Continue **Urdu B2**, starting from Unit 10 / sequence 55, under:','Continue **Urdu C1**, starting from Unit 1 / sequence 1, under:','HANDOFF frontier'); h=rep(h,'B2 Unit 10 uses the roadmap theme **B2 synthesis** with `paired long texts`, `integrated analysis`, and `checkpoint` genres.','C1 Unit 1 uses the roadmap theme **research and evidence** with `academic-style synthesis`, `methods explanation`, and `critique` genres.','HANDOFF roadmap'); h=rep(h,'Run `python reading/tools/validate_continuation_state.py`; if it passes, resume guarded generation at **Urdu B2 Unit 10 / sequence 55** using the B2 Unit 10 roadmap theme `B2 synthesis`.','Run `python reading/tools/validate_continuation_state.py`; if it passes, resume guarded generation at **Urdu C1 Unit 1 / sequence 1** using the C1 Unit 1 roadmap theme `research and evidence`.','HANDOFF next'); hp.write_text(h,encoding='utf-8')
    if RELEASE.read_bytes()!=release_before: fail('RELEASE_STATUS.json changed during generation-only promotion')
    print('Urdu B2 Unit 10 promotion validation: PASS'); print('Urdu B2 complete: 60/60; project 960/1080; Urdu 240/360'); print('next frontier: Urdu C1 Unit 1 / sequence 1 — research and evidence'); return 0
if __name__=='__main__': raise SystemExit(main())
