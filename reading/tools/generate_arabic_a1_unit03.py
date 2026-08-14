#!/usr/bin/env python3
"""Generate Arabic A1 Unit 03: food and simple choices.

Formal audits are deferred under GENERATION_FIRST_FINAL_AUDIT_POLICY.md.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASSAGES = ROOT / "reading" / "arabic" / "a1" / "passages.jsonl"
LEXICON = ROOT / "reading" / "lexicons" / "arabic.jsonl"

TARGETS = {
    124: ("يحب", "likes; loves", ["behavior_interpretation", "scenario_resolution"]),
    116: ("أفضل", "better; preferable; preferred", ["contrast"]),
    150: ("يحتاج", "needs; requires", ["cause_consequence"]),
    95: ("عدد", "number; count", ["example_instance"]),
    106: ("أين", "where?", ["scenario_resolution"]),
    115: ("عند", "at; by; with/in the possession of", ["scenario_resolution"]),
    92: ("لماذا", "why?", ["cause_consequence"]),
    112: ("شكرا", "thank you; thanks", ["scenario_resolution"]),
    140: ("ثم", "then; afterwards", ["parallel_structure"]),
    97: ("أخرى", "another; other (feminine)", ["contrast", "example_instance"]),
}


def make_qa(items):
    questions, answers = [], []
    for i, (qtype, prompt, answer, target_ids) in enumerate(items, 1):
        q = {"id": f"q{i}", "type": qtype, "prompt": prompt, "answer_id": f"a{i}"}
        if target_ids:
            q["target_ids"] = target_ids
        questions.append(q)
        answers.append({"id": f"a{i}", "question_id": f"q{i}", "answer": answer, "explanation": ""})
    if len(questions) != 10:
        raise ValueError("ten questions required")
    return questions, answers


RAW = [
    {
        "id": "ar-a1-u03-p01", "sequence": 13, "title": "فطور ليلى", "passage_type": "instructional",
        "genre": "kitchen micro-story", "domains": ["personal"], "topics": ["food", "breakfast", "preferences"],
        "text": "في صباح الجمعة لا تذهب ليلى إلى المدرسة. تجلس مع أمها في المطبخ. على الطاولة خبز وجبن وفاكهة. تسأل الأم: ماذا تحبين في الفطور؟ تقول ليلى: أحب الخبز مع الجبن، وأحب التفاح أيضًا. تضع الأم أمامها نوعين من العصير. تسأل: أيهما أفضل لك، عصير البرتقال أم عصير التفاح؟ تنظر ليلى إلى الكأسين وتقول: عصير البرتقال أفضل اليوم، لأنه بارد وأنا أحبه. تقول الأم: جيد. تأكل ليلى قليلًا من كل شيء، لكنها لا تأخذ طعامًا كثيرًا. بعد الفطور تقول: أحب هذا الفطور لأنه بسيط، وهذا العصير أفضل لي اليوم.",
        "new_ranks": [124, 116],
        "reviews": [
            {"id": "ar-r89", "form": "أيضا", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r84", "form": "آخر", "review_stage": "R2", "representation": "contrast"},
            {"id": "ar-r73", "form": "نحن", "review_stage": "R2", "representation": "other"},
        ],
        "grammar": [
            {"id": "ar-a1-like-preference", "role": "new", "description": "يحب + noun / simple object"},
            {"id": "ar-a1-basic-comparison", "role": "new", "description": "أفضل in a simple choice between two options"},
        ],
        "discourse": [{"id": "a1-choice-reason", "role": "new", "description": "state a simple preference with an explicit reason"}],
        "qa": [
            ("gist", "ما الموضوع الرئيسي في النص؟", "اختيار ليلى لفطور تحبه.", None),
            ("literal_detail", "أي عصير تختار ليلى اليوم؟", "عصير البرتقال.", None),
            ("vocabulary_in_context", "ماذا يعني «أحب» في «أحب الخبز مع الجبن»؟", "أن ليلى تستمتع به وتفضله كطعام.", ["ar-r124"]),
            ("vocabulary_in_context", "ماذا تعني «أفضل» في «عصير البرتقال أفضل اليوم»؟", "أنه الخيار الذي تفضله ليلى أكثر اليوم.", ["ar-r116"]),
            ("cause_effect", "لماذا تختار ليلى عصير البرتقال؟", "لأنه بارد وهي تحبه.", None),
            ("single_word_definition", "ما معنى «يحب»؟", "يميل إلى شيء ويستمتع به أو يفضله.", ["ar-r124"]),
            ("single_word_definition", "ما معنى «أفضل» في الاختيار بين شيئين؟", "أحسن أو أنسب في نظر المتكلم.", ["ar-r116"]),
            ("contrast", "إذا كنت أفضّل التفاح على البرتقال، أيهما أفضل عندي؟", "التفاح.", ["ar-r116"]),
            ("cloze_transfer", "أكمل: أنا _____ الشاي في الصباح.", "أحب", ["ar-r124"]),
            ("cloze_transfer", "أكمل: هذا الطعام أخف، وهو _____ لي اليوم.", "أفضل", ["ar-r116"]),
        ],
    },
    {
        "id": "ar-a1-u03-p02", "sequence": 14, "title": "قائمة السوق", "passage_type": "reinforcement",
        "genre": "market scene", "domains": ["personal", "public"], "topics": ["shopping", "food", "quantity"],
        "text": "قبل أن تذهب ليلى وأمها إلى السوق تنظر الأم إلى المطبخ. تقول: نحتاج إلى بعض الأشياء للعشاء. تكتب في ورقة: خبز، أرز، طماطم، وحليب. تسأل ليلى: كم عدد الطماطم التي نحتاج إليها؟ تقول الأم: نحتاج إلى أربع طماطم فقط. في السوق ترى ليلى أنواعًا كثيرة من الفاكهة. تريد أن تشتري تفاحًا أيضًا، لكن أمها تسأل: هل نحتاج إليه اليوم؟ تنظر ليلى إلى القائمة وتقول: لا، عندنا تفاح في المنزل. تقول الأم: جيد، نشتري ما نحتاج إليه فقط. في النهاية يكون عدد الأشياء في الحقيبة قليلًا، وكل شيء فيها له مكان في عشاء اليوم.",
        "new_ranks": [150, 95],
        "reviews": [
            {"id": "ar-r124", "form": "يحب", "review_stage": "R1", "representation": "other"},
            {"id": "ar-r116", "form": "أفضل", "review_stage": "R1", "representation": "contrast"},
            {"id": "ar-r24", "form": "كل", "review_stage": "R3", "representation": "running_text"},
            {"id": "ar-r53", "form": "بعض", "review_stage": "R3", "representation": "running_text"},
        ],
        "grammar": [
            {"id": "ar-a1-need", "role": "new", "description": "يحتاج إلى + noun"},
            {"id": "ar-a1-count-question", "role": "new", "description": "كم عدد + plural noun"},
        ],
        "discourse": [{"id": "a1-list-choice", "role": "new", "description": "use a simple list to constrain shopping choices"}],
        "qa": [
            ("literal_detail", "كم طماطم تحتاج الأم؟", "أربع طماطم.", None),
            ("literal_detail", "لماذا لا تشتري ليلى التفاح؟", "لأن عندهم تفاحًا في المنزل.", None),
            ("vocabulary_in_context", "ماذا يعني «نحتاج» في «نحتاج إلى بعض الأشياء»؟", "أن هذه الأشياء مطلوبة للعشاء.", ["ar-r150"]),
            ("vocabulary_in_context", "ماذا يعني «عدد» في سؤال الطماطم؟", "كمية الأشياء عند العد.", ["ar-r95"]),
            ("reference_resolution", "إلى ماذا تشير «إليه» في «هل نحتاج إليه اليوم»؟", "إلى التفاح.", None),
            ("single_word_definition", "ما معنى «يحتاج»؟", "يكون الشيء مطلوبًا أو ضروريًا له.", ["ar-r150"]),
            ("single_word_definition", "ما معنى «عدد»؟", "كمية الأشياء التي يمكن عدها.", ["ar-r95"]),
            ("contrast", "إذا كانت القائمة تطلب أربع طماطم، هل نحتاج إلى عشر طماطم؟", "لا.", ["ar-r150"]),
            ("cloze_transfer", "أكمل: كم _____ الكتب على الطاولة؟", "عدد", ["ar-r95"]),
            ("cloze_transfer", "أكمل: أنا _____ إلى ماء بعد المشي.", "أحتاج", ["ar-r150"]),
        ],
    },
    {
        "id": "ar-a1-u03-p03", "sequence": 15, "title": "أين الحليب؟", "passage_type": "interleaved",
        "genre": "store-search dialogue", "domains": ["public"], "topics": ["store", "food", "location"],
        "text": "تدخل ليلى وأمها متجرًا صغيرًا. تمسك ليلى القائمة وتقول: بقي الحليب فقط. تنظر حولها ولا تراه. تسأل أمها: أين الحليب؟ تقول الأم: ربما عند الثلاجة الكبيرة في آخر المتجر. تذهبان إلى هناك، لكنهما تجدان العصير فقط. ترى ليلى رجلًا يعمل في المتجر وتسأله: من فضلك، أين نجد الحليب؟ يقول: الحليب عند الثلاجة الأخرى، بجانب الخبز. تذهب ليلى إلى المكان وتجد الحليب. تقول لأمها: الآن أعرف أين هو. تقول الأم: وأنا أعرف عند من نسأل إذا لم نجد شيئًا. تأخذان الحليب وتذهبان إلى صندوق الدفع.",
        "new_ranks": [106, 115],
        "reviews": [
            {"id": "ar-r150", "form": "يحتاج", "review_stage": "R1", "representation": "other"},
            {"id": "ar-r95", "form": "عدد", "review_stage": "R1", "representation": "other"},
            {"id": "ar-r40", "form": "هناك", "review_stage": "R3", "representation": "reference"},
            {"id": "ar-r84", "form": "آخر", "review_stage": "R3", "representation": "running_text"},
        ],
        "grammar": [
            {"id": "ar-a1-where-question", "role": "new", "description": "أين for asking location"},
            {"id": "ar-a1-at-location", "role": "new", "description": "عند for location/possession in transparent contexts"},
        ],
        "discourse": [{"id": "a1-search-resolution", "role": "new", "description": "follow a simple search from problem to resolution"}],
        "qa": [
            ("literal_detail", "ما الشيء الذي بقي في القائمة؟", "الحليب.", None),
            ("literal_detail", "أين يجدون الحليب في النهاية؟", "عند الثلاجة الأخرى بجانب الخبز.", None),
            ("vocabulary_in_context", "ماذا تسأل «أين»؟", "تسأل عن مكان الشيء.", ["ar-r106"]),
            ("vocabulary_in_context", "ماذا تعني «عند» في «الحليب عند الثلاجة»؟", "أن الحليب موجود قرب الثلاجة أو في مكانها.", ["ar-r115"]),
            ("sequence", "ماذا تفعل ليلى بعد أن لا تجد الحليب عند الثلاجة الأولى؟", "تسأل رجلًا يعمل في المتجر.", None),
            ("single_word_definition", "ما معنى «أين»؟", "سؤال عن المكان.", ["ar-r106"]),
            ("grammar_function", "ما وظيفة «عند» في «عند الثلاجة»؟", "تحدد مكان الشيء بالنسبة إلى الثلاجة.", ["ar-r115"]),
            ("contrast", "أي سؤال مناسب للمكان: «أين الحليب؟» أم «متى الحليب؟»؟", "أين الحليب؟", ["ar-r106"]),
            ("cloze_transfer", "أكمل: _____ الخبز؟ أريد أن أشتريه.", "أين", ["ar-r106"]),
            ("cloze_transfer", "أكمل: الكتاب _____ أمي الآن.", "عند", ["ar-r115"]),
        ],
    },
    {
        "id": "ar-a1-u03-p04", "sequence": 16, "title": "في المقهى", "passage_type": "transfer",
        "genre": "short exchange", "domains": ["public"], "topics": ["cafe", "ordering", "politeness"],
        "text": "بعد السوق تجلس ليلى وأمها في مقهى صغير. يأتي العامل ويقول: مرحبًا، ماذا تريدان؟ تطلب الأم شايًا، وتطلب ليلى ماءً وقطعة خبز بالجبن. يسأل العامل: هل تريدين عصيرًا أيضًا؟ تقول ليلى: لا، شكرًا. بعد قليل يأتي بالطعام، لكن معه عصير بدل الماء. تقول ليلى بهدوء: آسفة، أنا طلبت الماء. يسأل العامل: لماذا لا تريدين العصير؟ تقول: لأن عندي عصيرًا في المنزل، والماء أفضل لي الآن. يقول العامل: فهمت، وسأحضر الماء. عندما يأتي بالماء تقول ليلى: شكرًا. تبتسم أمها وتقول: السؤال والجواب الواضحان يساعدان الناس على فهم ما نريد.",
        "new_ranks": [92, 112],
        "reviews": [
            {"id": "ar-r106", "form": "أين", "review_stage": "R1", "representation": "other"},
            {"id": "ar-r115", "form": "عند", "review_stage": "R1", "representation": "running_text"},
            {"id": "ar-r116", "form": "أفضل", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r89", "form": "أيضا", "review_stage": "R3", "representation": "running_text"},
        ],
        "grammar": [
            {"id": "ar-a1-why-question", "role": "new", "description": "لماذا for asking a reason"},
            {"id": "ar-a1-thanks", "role": "new", "description": "شكرًا as a basic polite response"},
        ],
        "discourse": [{"id": "a1-polite-correction", "role": "new", "description": "correct a simple service mistake and give a reason"}],
        "qa": [
            ("literal_detail", "ماذا طلبت ليلى للشرب؟", "الماء.", None),
            ("literal_detail", "ماذا أحضر العامل أولًا بدل الماء؟", "العصير.", None),
            ("vocabulary_in_context", "ماذا تطلب كلمة «لماذا» من ليلى؟", "تطلب منها سبب عدم رغبتها في العصير.", ["ar-r92"]),
            ("vocabulary_in_context", "متى تقول ليلى «شكرًا»؟", "عندما يعرض العامل شيئًا لا تريده، وعندما يحضر لها الماء.", ["ar-r112"]),
            ("cause_effect", "لماذا تريد ليلى الماء بدل العصير؟", "لأن عندها عصيرًا في المنزل والماء أفضل لها الآن.", None),
            ("single_word_definition", "ما معنى «لماذا»؟", "سؤال عن السبب.", ["ar-r92"]),
            ("single_word_definition", "ماذا نعبر بكلمة «شكرًا»؟", "عن الامتنان أو الأدب عند تلقي شيء أو عرض.", ["ar-r112"]),
            ("contrast", "أي كلمة تسأل عن السبب: «لماذا» أم «أين»؟", "لماذا.", ["ar-r92", "ar-r106"]),
            ("cloze_transfer", "أكمل: _____ تأخرت؟ لأن الحافلة تأخرت.", "لماذا", ["ar-r92"]),
            ("cloze_transfer", "أكمل الرد المناسب: «هذا كتابك.» — «_____.»", "شكرًا", ["ar-r112"]),
        ],
    },
    {
        "id": "ar-a1-u03-p05", "sequence": 17, "title": "عشاء بسيط", "passage_type": "checkpoint",
        "genre": "simple cooking narrative", "domains": ["personal"], "topics": ["cooking", "food", "sequence", "choices"],
        "text": "في المساء تساعد ليلى أمها في إعداد عشاء بسيط. أولًا تغسل ليلى الطماطم، ثم تضعها على الطاولة. تقطع الأم الخبز، ثم تحضر الجبن. تقول ليلى: عندنا طماطم كثيرة، هل نحتاج إلى سلطة أخرى؟ تقول الأم: لا، هذه الكمية تكفي. لكننا نحتاج إلى طبق آخر للخبز. تبحث ليلى في المطبخ وتجد صحنًا كبيرًا وصحنًا صغيرًا. تسأل: أي واحد أفضل؟ تقول الأم: الكبير أفضل لأن الخبز كثير. تضع ليلى الخبز فيه، ثم تحضر الماء أيضًا. عندما يصبح العشاء جاهزًا تجلسان معًا. تقول ليلى: أحب أن أعرف ماذا نفعل أولًا ثم ماذا نفعل بعد ذلك.",
        "new_ranks": [140, 97],
        "reviews": [
            {"id": "ar-r92", "form": "لماذا", "review_stage": "R1", "representation": "other"},
            {"id": "ar-r112", "form": "شكرا", "review_stage": "R1", "representation": "other"},
            {"id": "ar-r150", "form": "يحتاج", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r116", "form": "أفضل", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r124", "form": "يحب", "review_stage": "R2", "representation": "running_text"},
        ],
        "grammar": [
            {"id": "ar-a1-then-sequence", "role": "new", "description": "ثم for explicit ordered sequence"},
            {"id": "ar-a1-another-feminine", "role": "new", "description": "أخرى with a feminine noun"},
        ],
        "discourse": [{"id": "a1-procedure-order", "role": "integration", "description": "follow a short preparation sequence"}],
        "qa": [
            ("gist", "ماذا تفعل ليلى وأمها؟", "تعدان عشاءً بسيطًا معًا.", None),
            ("literal_detail", "لماذا تختار الأم الصحن الكبير؟", "لأن الخبز كثير.", None),
            ("vocabulary_in_context", "ماذا تدل «ثم» في خطوات إعداد العشاء؟", "على أن خطوة تأتي بعد خطوة أخرى.", ["ar-r140"]),
            ("vocabulary_in_context", "ماذا تعني «أخرى» في «سلطة أخرى»؟", "سلطة إضافية غير الموجودة.", ["ar-r97"]),
            ("sequence", "ماذا يحدث بعد غسل الطماطم؟", "تضعها ليلى على الطاولة.", None),
            ("single_word_definition", "ما معنى «ثم»؟", "بعد ذلك؛ وتدل على ترتيب لاحق.", ["ar-r140"]),
            ("single_word_definition", "ما معنى «أخرى»؟", "واحدة إضافية أو مختلفة، مع اسم مؤنث.", ["ar-r97"]),
            ("grammar_choice", "اختر الأنسب: «سلطة أخرى» أم «سلطة آخر»؟", "سلطة أخرى.", ["ar-r97"]),
            ("cloze_transfer", "أكمل: أغسل يدي، _____ آكل.", "ثم", ["ar-r140"]),
            ("cloze_transfer", "أكمل: هذه تفاحة صغيرة؛ أريد تفاحة _____.", "أخرى", ["ar-r97"]),
        ],
    },
    {
        "id": "ar-a1-u03-p06", "sequence": 18, "title": "اختيارات الطعام", "passage_type": "fluency",
        "genre": "connected food-and-shopping narrative", "domains": ["personal", "public"], "topics": ["food", "shopping", "choices", "review"],
        "text": "تعرف ليلى الآن كيف تختار الطعام ببساطة. في البيت تعرف ما تحبه وما هو أفضل لها في ذلك اليوم. قبل السوق تنظر مع أمها إلى الأشياء التي تحتاج إليها، وتعرف عدد ما يجب شراؤه. في المتجر إذا لم تجد شيئًا تسأل: أين هو؟ وإذا لم تعرف المكان تسأل شخصًا يعمل هناك. عند المقهى تقول ما تريد بوضوح، وإذا سألها العامل لماذا اختارت الماء أو الطعام تذكر السبب. وعندما يساعدها أحد تقول: شكرًا. في البيت تساعد أمها في إعداد العشاء: تغسل الطعام أولًا، ثم تضعه في مكانه، ثم تحضر شيئًا آخر إذا احتاجتا إليه. بهذه الطريقة تشتري الأسرة ما تحتاج إليه، ولا تأخذ أشياء كثيرة بلا سبب.",
        "new_ranks": [],
        "reviews": [
            {"id": "ar-r124", "form": "يحب", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r116", "form": "أفضل", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r150", "form": "يحتاج", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r95", "form": "عدد", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r106", "form": "أين", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r115", "form": "عند", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r92", "form": "لماذا", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r112", "form": "شكرا", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r140", "form": "ثم", "review_stage": "R1", "representation": "running_text"},
            {"id": "ar-r97", "form": "أخرى", "review_stage": "R1", "representation": "running_text"},
        ],
        "grammar": [{"id": "ar-a1-u03-cumulative", "role": "integration", "description": "recycle preferences, need, location, reason, politeness, and sequence"}],
        "discourse": [{"id": "a1-food-fluency", "role": "integration", "description": "high-coverage cumulative food routine"}],
        "qa": [
            ("gist", "ما الفكرة الرئيسية في النص؟", "ليلى تتخذ اختيارات بسيطة ومنظمة عند الطعام والتسوق.", None),
            ("literal_detail", "ماذا تفعل الأسرة قبل الذهاب إلى السوق؟", "تنظر إلى الأشياء التي تحتاج إليها.", ["ar-r150"]),
            ("reference_resolution", "ماذا تسأل ليلى إذا لم تجد شيئًا في المتجر؟", "تسأل أين هو.", ["ar-r106"]),
            ("cause_effect", "متى تقول ليلى «شكرًا»؟", "عندما يساعدها أحد.", ["ar-r112"]),
            ("summary", "لخص طريقة ليلى في اختيار الطعام في جملة واحدة.", "تعرف ما تحبه وتشتري ما تحتاج إليه وتسأل بوضوح وتعمل بالترتيب.", None),
            ("single_word_definition", "ما معنى «أفضل» في سياق الاختيار؟", "أحسن أو أنسب بين الخيارات.", ["ar-r116"]),
            ("contrast", "أي سؤال يطلب سببًا: «لماذا» أم «أين»؟", "لماذا.", ["ar-r92", "ar-r106"]),
            ("single_word_definition", "ماذا يعني «عند» في «عند المقهى»؟", "في مكان المقهى أو بقربه.", ["ar-r115"]),
            ("grammar_function", "ماذا تفعل «ثم» في سلسلة الأفعال؟", "تربط الأفعال بترتيب، بحيث يأتي فعل بعد آخر.", ["ar-r140"]),
            ("contrast", "إذا كانت هناك تفاحة وتريد واحدة إضافية، أي كلمة تناسب: «أخرى» أم «أين»؟", "أخرى.", ["ar-r97"]),
        ],
    },
]


def lex_by_rank():
    out = {}
    for line in LEXICON.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            out[row["rank"]] = row
    return out


def make_target(rank, text, lex):
    form, sense, strategies = TARGETS[rank]
    src = lex[rank]
    return {
        "id": f"ar-r{rank}", "form": form, "lemma": form,
        "part_of_speech": src.get("part_of_speech_source"), "intended_sense": sense,
        "register": "contemporary standard", "variety": "MSA",
        "context_strategy": strategies, "first_introduced": True,
        "exposures_in_text": max(1, text.count(form)), "source_lexicon": src.get("source_file"),
        "source_rank": rank, "beyond_base": False,
    }


def build(raw, lex):
    questions, answers = make_qa(raw["qa"])
    text = raw["text"]
    return {
        "id": raw["id"], "language": "ar", "cefr": "A1", "unit": 3, "sequence": raw["sequence"], "revision": 1,
        "title": raw["title"], "passage_type": raw["passage_type"], "genre": raw["genre"], "domains": raw["domains"], "topics": raw["topics"],
        "text": text, "word_count": len(text.split()), "sentence_count": max(1, len(re.findall(r"[.!؟](?:\s|$)", text))),
        "estimated_known_token_coverage": 0,
        "new_lexical_targets": [make_target(rank, text, lex) for rank in raw["new_ranks"]],
        "review_lexical_targets": raw["reviews"], "grammar_targets": raw["grammar"], "discourse_targets": raw["discourse"],
        "questions": questions, "answer_key": answers,
        "speed_training": {"timed": raw["passage_type"] == "fluency", "benchmark_eligible": False, "comprehension_gate": 0.8, "new_word_policy": "none" if raw["passage_type"] == "fluency" else "controlled", "notes": "Generation-stage passage; formal fluency/coverage decision deferred to final audit."},
        "quality": {"status": "draft", "linguistic_review": "pending", "pedagogical_review": "pending", "coverage_check": "pending", "answer_key_check": "pending", "schema_check": "pending", "fact_check": "not_required", "notes": ["High-quality generation-stage draft; formal audits deferred to the final multi-pass review phase."]},
        "paired_text_group": None, "prerequisites": [], "difficulty_notes_internal": None,
        "reader_tags": ["unit_role:" + raw["passage_type"], "generation_batch"],
        "complexity_profile": {"mean_sentence_length": None, "median_sentence_length": None, "clause_count": None, "subordination_count": None, "coordination_count": None, "connective_diversity": None, "lexical_diversity": None, "reference_chain_max_distance": None, "multiword_expression_count": None, "morphology_notes": "A1 generation-stage draft; transparent contemporary MSA.", "inference_depth": "local"},
    }


def main():
    existing = [json.loads(line) for line in PASSAGES.read_text(encoding="utf-8").splitlines() if line.strip()]
    existing = [r for r in existing if r.get("unit") != 3]
    lex = lex_by_rank()
    new = [build(raw, lex) for raw in RAW]
    if len(new) != 6 or any(len(r["questions"]) != 10 or len(r["answer_key"]) != 10 for r in new):
        raise SystemExit("Unit 03 generation contract failed")
    records = sorted(existing + new, key=lambda r: (r.get("unit", 0), r.get("sequence", 0)))
    PASSAGES.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records), encoding="utf-8")
    print("generated Arabic A1 Unit 03: six passages, sixty questions, sixty answers")


if __name__ == "__main__":
    main()
