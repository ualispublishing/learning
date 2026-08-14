#!/usr/bin/env python3
"""Generate Arabic A1 Unit 02: daily routine and time.

Generation-stage policy: write strong first-draft canonical passages with the
full ten-question contract, but leave formal quality/audit fields pending for
the later multi-pass corpus audit phase.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASSAGES = ROOT / "reading" / "arabic" / "a1" / "passages.jsonl"
LEXICON = ROOT / "reading" / "lexicons" / "arabic.jsonl"

TARGET_SENSES = {
    61: ("وقت", "time; a moment or period for an activity", ["scenario_resolution"]),
    63: ("قبل", "before; earlier than a stated time or event", ["contrast", "scenario_resolution"]),
    71: ("عندما", "when; at the time that", ["parallel_structure"]),
    74: ("أول", "first; occurring before the others in an order", ["scenario_resolution"]),
    59: ("يجب", "must; should; it is necessary", ["cause_consequence"]),
    85: ("سوف", "will; future marker", ["parallel_structure"]),
    89: ("أيضا", "also; too", ["example_instance"]),
    84: ("آخر", "another; an additional one", ["contrast", "example_instance"]),
    73: ("نحن", "we", ["parallel_structure"]),
    72: ("كيف", "how?; in what way?", ["scenario_resolution"]),
}


def q(qid, qtype, prompt, answer, targets=None):
    item = {"id": qid, "type": qtype, "prompt": prompt, "answer_id": "a" + qid[1:]}
    if targets:
        item["target_ids"] = targets
    return item, {"id": "a" + qid[1:], "question_id": qid, "answer": answer, "explanation": ""}


def qa(items):
    questions, answers = [], []
    for i, item in enumerate(items, 1):
        question, answer = q(f"q{i}", *item)
        questions.append(question)
        answers.append(answer)
    if len(questions) != 10:
        raise ValueError("each passage must have exactly ten questions")
    return questions, answers


RAW = [
    {
        "id": "ar-a1-u02-p01",
        "sequence": 7,
        "title": "صباح منظم",
        "passage_type": "instructional",
        "genre": "routine narrative",
        "domains": ["personal"],
        "topics": ["daily routine", "morning", "time"],
        "text": "في أيام المدرسة تستيقظ ليلى في السادسة. تنظر إلى الساعة وتقول: هذا وقت الاستعداد. قبل أن تخرج من غرفتها ترتب سريرها وتفتح النافذة قليلا. ثم تذهب إلى المطبخ وتفطر مع أمها. قبل السابعة تضع كتابها ودفترها في الحقيبة. تقول أمها: بقي وقت قليل قبل الخروج. تلبس ليلى حذاءها وتنتظر عند الباب. في السابعة تخرج مع أمها. تقول ليلى: عندما أعرف الوقت لا أحتاج إلى العجلة. أمها تبتسم وتقول: نعم، ومن الجيد أن تستعدي قبل موعد الخروج.",
        "new_ranks": [61, 63],
        "reviews": [
            {"id": "ar-r37", "form": "بعد", "review_stage": "R3", "representation": "contrast"},
            {"id": "ar-r42", "form": "الآن", "review_stage": "R3", "representation": "running_text"},
        ],
        "grammar_targets": [
            {"id": "ar-a1-time-phrases", "role": "new", "description": "basic clock/time expressions"},
            {"id": "ar-a1-before-relation", "role": "new", "description": "قبل + event/time"},
        ],
        "discourse_targets": [
            {"id": "a1-routine-order", "role": "new", "description": "follow a simple morning sequence"},
        ],
        "qa": [
            ("gist", "ما الفكرة الرئيسية في النص؟", "ليلى تستعد للمدرسة في صباح منظم.", None),
            ("literal_detail", "متى تخرج ليلى من المنزل؟", "في السابعة.", None),
            ("vocabulary_in_context", "ماذا يعني «وقت» في «هذا وقت الاستعداد»؟", "الفترة أو اللحظة المناسبة للاستعداد.", ["ar-r61"]),
            ("vocabulary_in_context", "ماذا تعني «قبل» في «قبل السابعة»؟", "في وقت يسبق السابعة.", ["ar-r63"]),
            ("sequence", "ماذا تفعل ليلى قبل أن تلبس حذاءها: تجهز حقيبتها أم تخرج من المنزل؟", "تجهز حقيبتها.", None),
            ("single_word_definition", "ما معنى «وقت»؟", "زمن أو مدة يحدث فيها شيء.", ["ar-r61"]),
            ("grammar_function", "ما العلاقة الزمنية التي تدل عليها «قبل»؟", "أن الحدث يحدث في وقت أسبق من حدث أو وقت آخر.", ["ar-r63"]),
            ("contrast", "أيهما يدل على الزمن الأسبق: «قبل» أم «بعد»؟", "قبل.", ["ar-r63", "ar-r37"]),
            ("cloze_transfer", "أكمل: أغسل يدي _____ الطعام.", "قبل", ["ar-r63"]),
            ("cloze_transfer", "أكمل: الساعة الثامنة هي _____ بدء الدرس.", "وقت", ["ar-r61"]),
        ],
    },
    {
        "id": "ar-a1-u02-p02",
        "sequence": 8,
        "title": "أول درس",
        "passage_type": "reinforcement",
        "genre": "schedule-like narrative",
        "domains": ["personal", "educational"],
        "topics": ["school", "schedule", "sequence"],
        "text": "تصل ليلى إلى المدرسة قبل بدء الدرس بقليل. عندما تدخل الصف تضع حقيبتها بجانب الكرسي. أول شيء تفعله هو إخراج الدفتر والقلم. عندما يدخل المعلم ينظر الطلاب إليه ويبدؤون الدرس. الدرس الأول هو القراءة، وبعده درس آخر. في وقت الاستراحة تخرج ليلى مع صديقتها إلى الساحة. تقول صديقتها: ماذا نفعل أولًا بعد المدرسة؟ تقول ليلى: أولًا نعود إلى المنزل، ثم يمكن أن نقرأ أو نذهب إلى الحديقة. عندما يرن الجرس تعودان إلى الصف. تعرف ليلى الآن ترتيب يومها، ولذلك تعرف ماذا تفعل في كل وقت.",
        "new_ranks": [71, 74],
        "reviews": [
            {"id": "ar-r61", "form": "وقت", "review_stage": "R1", "representation": "running_text"},
            {"id": "ar-r63", "form": "قبل", "review_stage": "R1", "representation": "running_text"},
            {"id": "ar-r34", "form": "هنا", "review_stage": "R3", "representation": "other"},
        ],
        "grammar_targets": [
            {"id": "ar-a1-when-clause", "role": "new", "description": "عندما + simple event"},
            {"id": "ar-a1-order-first", "role": "new", "description": "أول/أولًا for simple ordering"},
        ],
        "discourse_targets": [
            {"id": "a1-chronology", "role": "review", "description": "track explicit event order"},
        ],
        "qa": [
            ("literal_detail", "ماذا تفعل ليلى أولًا عندما تدخل الصف؟", "تضع حقيبتها ثم تخرج الدفتر والقلم.", None),
            ("literal_detail", "ما الدرس الأول؟", "درس القراءة.", None),
            ("vocabulary_in_context", "ماذا تعني «عندما» في «عندما يدخل المعلم»؟", "في الوقت الذي يدخل فيه المعلم.", ["ar-r71"]),
            ("vocabulary_in_context", "ماذا تعني «أول» في «الدرس الأول»؟", "الدرس الذي يأتي قبل بقية الدروس.", ["ar-r74"]),
            ("sequence", "ماذا تفعل ليلى وصديقتها بعد انتهاء الاستراحة؟", "تعودان إلى الصف عندما يرن الجرس.", None),
            ("single_word_definition", "ما معنى «عندما»؟", "في الوقت الذي يحدث فيه شيء.", ["ar-r71"]),
            ("grammar_category", "ما وظيفة «أولًا» في ترتيب الأحداث؟", "تدل على الحدث الذي يأتي قبل غيره.", ["ar-r74"]),
            ("contrast", "أيهما يأتي في البداية: «أول» أم «آخر»؟", "أول.", ["ar-r74"]),
            ("cloze_transfer", "أكمل: _____ أصل إلى البيت أضع حقيبتي على الكرسي.", "عندما", ["ar-r71"]),
            ("cloze_transfer", "أكمل: هذا هو اليوم _____ في المدرسة الجديدة.", "الأول", ["ar-r74"]),
        ],
    },
    {
        "id": "ar-a1-u02-p03",
        "sequence": 9,
        "title": "بعد المدرسة",
        "passage_type": "interleaved",
        "genre": "micro-story",
        "domains": ["personal", "educational"],
        "topics": ["homework", "plans", "time"],
        "text": "بعد المدرسة تعود ليلى إلى المنزل. تريد أن تخرج إلى الحديقة، لكن على الطاولة واجب صغير. تقول أمها: يجب أن تنهي الواجب قبل الخروج. تنظر ليلى إلى الساعة. لديها وقت، فتجلس وتبدأ العمل. عندما تنتهي تقول: الآن يمكن أن أذهب. تقول أمها: نعم، وسوف نذهب معًا بعد قليل. قبل أن تخرجا تشرب ليلى الماء وتأخذ سترتها. في الحديقة تقول ليلى: سوف ألعب قليلًا فقط، لأنني يجب أن أعود قبل المساء. عندما يصبح الوقت متأخرًا تعودان إلى المنزل. تقول ليلى: من الجيد أن أنهي ما يجب عليّ فعله أولًا.",
        "new_ranks": [59, 85],
        "reviews": [
            {"id": "ar-r71", "form": "عندما", "review_stage": "R1", "representation": "running_text"},
            {"id": "ar-r74", "form": "أول", "review_stage": "R1", "representation": "running_text"},
            {"id": "ar-r61", "form": "وقت", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r36", "form": "يمكن", "review_stage": "R3", "representation": "running_text"},
        ],
        "grammar_targets": [
            {"id": "ar-a1-must", "role": "new", "description": "يجب أن + present verb"},
            {"id": "ar-a1-future-sawfa", "role": "new", "description": "سوف + present verb"},
        ],
        "discourse_targets": [
            {"id": "a1-obligation-plan", "role": "new", "description": "distinguish obligation from later plan"},
        ],
        "qa": [
            ("cause_effect", "لماذا لا تذهب ليلى إلى الحديقة فورًا؟", "لأن عليها واجبًا يجب أن تنهيه قبل الخروج.", None),
            ("literal_detail", "ماذا تأخذ ليلى قبل الذهاب إلى الحديقة؟", "سترتها.", None),
            ("vocabulary_in_context", "ماذا يعني «يجب» في «يجب أن تنهي الواجب»؟", "أن إنهاء الواجب ضروري.", ["ar-r59"]),
            ("vocabulary_in_context", "ماذا تدل «سوف» في «سوف نذهب»؟", "على فعل سيحدث في المستقبل.", ["ar-r85"]),
            ("sequence", "ما الذي يحدث أولًا: إنهاء الواجب أم الذهاب إلى الحديقة؟", "إنهاء الواجب.", None),
            ("single_word_definition", "ما معنى «يجب»؟", "من الضروري أو المطلوب أن يحدث الشيء.", ["ar-r59"]),
            ("grammar_function", "ما وظيفة «سوف» قبل الفعل؟", "تدل على المستقبل.", ["ar-r85"]),
            ("contrast", "أيهما يدل على ضرورة: «يجب» أم «يمكن»؟", "يجب.", ["ar-r59", "ar-r36"]),
            ("cloze_transfer", "أكمل: _____ أن أصل إلى المدرسة قبل الثامنة.", "يجب", ["ar-r59"]),
            ("cloze_transfer", "أكمل: غدًا _____ أزور المكتبة.", "سوف", ["ar-r85"]),
        ],
    },
    {
        "id": "ar-a1-u02-p04",
        "sequence": 10,
        "title": "رسالة قصيرة",
        "passage_type": "transfer",
        "genre": "short message with narrative frame",
        "domains": ["personal", "public"],
        "topics": ["message", "errands", "plans"],
        "text": "بعد الظهر تقرأ سارة رسالة من أخيها عمر. كتب عمر: «سأعود إلى المنزل في الخامسة. قبل ذلك يجب أن أذهب إلى المكتبة. أريد كتابًا جديدًا، وأريد أيضًا دفترًا للمدرسة. إذا لم أجد الدفتر هناك فسوف أذهب إلى متجر آخر. عندما أصل إلى المنزل سوف أضع الأشياء على الطاولة.» تقرأ سارة الرسالة مرة أخرى. هي أيضًا تحتاج إلى كتاب، لكنها لا تحتاج إلى دفتر آخر. تكتب له: «أنا في المنزل الآن. عندما تعود يمكن أن نقرأ معًا. وإذا كان لديك وقت، أحضر لي كتابًا أيضًا.» ثم تنظر إلى الساعة وتبدأ عملها قبل عودة عمر.",
        "new_ranks": [89, 84],
        "reviews": [
            {"id": "ar-r59", "form": "يجب", "review_stage": "R1", "representation": "running_text"},
            {"id": "ar-r85", "form": "سوف", "review_stage": "R1", "representation": "running_text"},
            {"id": "ar-r63", "form": "قبل", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r40", "form": "هناك", "review_stage": "R3", "representation": "reference"},
        ],
        "grammar_targets": [
            {"id": "ar-a1-also", "role": "new", "description": "أيضًا for additive coordination"},
            {"id": "ar-a1-another", "role": "new", "description": "آخر for an additional/other item"},
        ],
        "discourse_targets": [
            {"id": "a1-message-plan", "role": "new", "description": "extract a simple plan from a short message"},
        ],
        "qa": [
            ("literal_detail", "في أي وقت سيعود عمر إلى المنزل؟", "في الخامسة.", None),
            ("literal_detail", "ما الشيئان اللذان يريد عمر شراءهما؟", "كتابًا جديدًا ودفترًا للمدرسة.", None),
            ("vocabulary_in_context", "ماذا تعني «أيضًا» في «أريد أيضًا دفترًا»؟", "أن الدفتر شيء إضافي إلى الكتاب.", ["ar-r89"]),
            ("vocabulary_in_context", "ماذا تعني «آخر» في «متجر آخر»؟", "متجرًا مختلفًا أو إضافيًا غير الأول.", ["ar-r84"]),
            ("sequence", "إلى أين يذهب عمر أولًا إذا وجد ما يريد: المكتبة أم المنزل؟", "إلى المكتبة أولًا.", None),
            ("single_word_definition", "ما معنى «أيضًا»؟", "كذلك؛ زيادة على شيء سبق ذكره.", ["ar-r89"]),
            ("single_word_definition", "ما معنى «آخر» في «دفتر آخر»؟", "دفتر إضافي أو غير الدفتر الأول.", ["ar-r84"]),
            ("contrast", "إذا كان عندي كتاب وأريد كتابًا إضافيًا، أقول «كتاب آخر» أم «كتاب قبل»؟", "كتاب آخر.", ["ar-r84"]),
            ("cloze_transfer", "أكمل: معي قلم، وأريد دفترًا _____.", "أيضًا", ["ar-r89"]),
            ("cloze_transfer", "أكمل: هذا المتجر مغلق؛ نذهب إلى متجر _____.", "آخر", ["ar-r84"]),
        ],
    },
    {
        "id": "ar-a1-u02-p05",
        "sequence": 11,
        "title": "كيف نرتب المساء؟",
        "passage_type": "checkpoint",
        "genre": "dialogue-like narrative",
        "domains": ["personal"],
        "topics": ["family", "evening routine", "planning"],
        "text": "في المساء تجلس ليلى مع أمها في المطبخ. تقول الأم: لدينا أشياء كثيرة اليوم، فكيف نرتب الوقت؟ تقول ليلى: نحن نأكل أولًا، ثم يجب أن أقرأ قليلًا. بعد ذلك سوف أجهز حقيبتي للغد. تقول الأم: جيد، وأنا سوف أرتب المطبخ. تقول ليلى: هل نقرأ معًا أيضًا؟ تقول الأم: نعم، عندما أنتهي من العمل. تسأل ليلى: وكيف نعرف وقت النوم؟ تقول الأم: ننظر إلى الساعة. نحن لا نريد أن نسهر كثيرًا، لأنك تذهبين إلى المدرسة غدًا. تقول ليلى: إذن لن أبدأ عملًا آخر قبل النوم. في النهاية تعرفان كيف ترتبان المساء بهدوء.",
        "new_ranks": [73, 72],
        "reviews": [
            {"id": "ar-r89", "form": "أيضا", "review_stage": "R1", "representation": "running_text"},
            {"id": "ar-r84", "form": "آخر", "review_stage": "R1", "representation": "running_text"},
            {"id": "ar-r61", "form": "وقت", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r63", "form": "قبل", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r71", "form": "عندما", "review_stage": "R2", "representation": "running_text"},
        ],
        "grammar_targets": [
            {"id": "ar-a1-we-pronoun", "role": "new", "description": "نحن as first-person plural pronoun"},
            {"id": "ar-a1-how-question", "role": "new", "description": "كيف for asking about manner"},
        ],
        "discourse_targets": [
            {"id": "a1-simple-plan-integration", "role": "integration", "description": "combine time, obligation, future, and sequence"},
        ],
        "qa": [
            ("gist", "ما الذي تحاول ليلى وأمها فعله؟", "ترتيب أعمال المساء ووقتها.", None),
            ("literal_detail", "ماذا ستجهز ليلى للغد؟", "حقيبتها.", None),
            ("vocabulary_in_context", "إلى من تشير «نحن» في كلام الأم وليلى؟", "إلى الأم وليلى معًا.", ["ar-r73"]),
            ("vocabulary_in_context", "ماذا تسأل «كيف» في «كيف نرتب الوقت»؟", "تسأل عن الطريقة التي سيرتبان بها الوقت.", ["ar-r72"]),
            ("cause_effect", "لماذا لا تريد الأم أن تسهر ليلى كثيرًا؟", "لأن ليلى ستذهب إلى المدرسة في اليوم التالي.", None),
            ("single_word_definition", "ما معنى «نحن»؟", "ضمير للمتكلم مع شخص أو أشخاص آخرين.", ["ar-r73"]),
            ("grammar_category", "ما نوع «كيف» في السؤال؟", "اسم استفهام يسأل عن الحال أو الطريقة.", ["ar-r72"]),
            ("contrast", "أيهما يدل على أكثر من متكلم واحد: «أنا» أم «نحن»؟", "نحن.", ["ar-r73"]),
            ("cloze_transfer", "أكمل: _____ نصل إلى المكتبة؟", "كيف", ["ar-r72"]),
            ("cloze_transfer", "أكمل: أنا وأخي في البيت؛ _____ نقرأ معًا.", "نحن", ["ar-r73"]),
        ],
    },
    {
        "id": "ar-a1-u02-p06",
        "sequence": 12,
        "title": "يوم ليلى",
        "passage_type": "fluency",
        "genre": "connected routine narrative",
        "domains": ["personal", "educational"],
        "topics": ["daily routine", "time", "review"],
        "text": "تعرف ليلى الآن كيف ترتب يومها. في الصباح تنظر إلى الساعة لتعرف الوقت. قبل المدرسة ترتب سريرها وتفطر وتجهز حقيبتها. عندما تصل إلى الصف تخرج الدفتر والقلم، ويكون درس القراءة هو الدرس الأول. بعد المدرسة تعود إلى المنزل. إذا كان عندها واجب، يجب أن تنهيه قبل الخروج. بعد ذلك يمكن أن تقول: سوف أذهب إلى الحديقة أو المكتبة. أحيانًا تريد كتابًا آخر، وأحيانًا تأخذ دفترًا أيضًا. في المساء تقول لأمها: كيف نرتب وقتنا؟ تقول أمها: نحن نعمل أولًا، ثم نقرأ قليلًا، وبعد ذلك نستعد للنوم. بهذا الترتيب لا تشعر ليلى بالعجلة، وتعرف ماذا تفعل في كل وقت.",
        "new_ranks": [],
        "reviews": [
            {"id": "ar-r61", "form": "وقت", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r63", "form": "قبل", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r71", "form": "عندما", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r74", "form": "أول", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r59", "form": "يجب", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r85", "form": "سوف", "review_stage": "R2", "representation": "running_text"},
            {"id": "ar-r89", "form": "أيضا", "review_stage": "R1", "representation": "running_text"},
            {"id": "ar-r84", "form": "آخر", "review_stage": "R1", "representation": "running_text"},
            {"id": "ar-r73", "form": "نحن", "review_stage": "R1", "representation": "running_text"},
            {"id": "ar-r72", "form": "كيف", "review_stage": "R1", "representation": "running_text"},
        ],
        "grammar_targets": [
            {"id": "ar-a1-u02-cumulative", "role": "integration", "description": "recycle Unit-02 time, sequence, obligation, future, and question structures"},
        ],
        "discourse_targets": [
            {"id": "a1-fluency-routine", "role": "integration", "description": "high-coverage connected routine"},
        ],
        "qa": [
            ("gist", "ما الفكرة الرئيسية في النص؟", "ليلى تعرف كيف تنظم يومها من الصباح إلى المساء.", None),
            ("sequence", "ماذا تفعل ليلى قبل المدرسة؟", "ترتب سريرها وتفطر وتجهز حقيبتها.", None),
            ("cause_effect", "متى يجب على ليلى أن تنهي الواجب قبل الخروج؟", "عندما يكون عندها واجب بعد المدرسة.", ["ar-r59", "ar-r71"]),
            ("literal_detail", "ما الدرس الأول المذكور في النص؟", "درس القراءة.", ["ar-r74"]),
            ("summary", "لخص ترتيب يوم ليلى في جملة واحدة.", "تستعد صباحًا، تدرس، تنهي عملها بعد المدرسة، ثم تقرأ وتستعد للنوم مساءً.", None),
            ("single_word_definition", "ما معنى «سوف»؟", "علامة تدل على أن الفعل سيحدث في المستقبل.", ["ar-r85"]),
            ("contrast", "أيهما يدل على الإضافة: «أيضًا» أم «قبل»؟", "أيضًا.", ["ar-r89", "ar-r63"]),
            ("reference_resolution", "إلى من تشير «نحن» في كلام الأم؟", "إلى الأم وليلى.", ["ar-r73"]),
            ("grammar_function", "ماذا تسأل «كيف»؟", "تسأل عن الطريقة أو الحال.", ["ar-r72"]),
            ("contrast", "أيهما يعني شيئًا إضافيًا: «آخر» أم «أول»؟", "آخر.", ["ar-r84", "ar-r74"]),
        ],
    },
]


def lexicon_by_rank():
    return {
        row["rank"]: row
        for line in LEXICON.read_text(encoding="utf-8").splitlines()
        if line.strip()
        for row in [json.loads(line)]
    }


def make_target(rank, text, lex):
    form, sense, strategy = TARGET_SENSES[rank]
    src = lex[rank]
    return {
        "id": f"ar-r{rank}",
        "form": form,
        "lemma": form,
        "part_of_speech": src.get("part_of_speech_source"),
        "intended_sense": sense,
        "register": "contemporary standard",
        "variety": "MSA",
        "context_strategy": strategy,
        "first_introduced": True,
        "exposures_in_text": max(1, text.count(form)),
        "source_lexicon": src.get("source_file"),
        "source_rank": rank,
        "beyond_base": False,
    }


def build_record(raw, lex):
    questions, answers = qa(raw["qa"])
    text = raw["text"]
    sentence_count = max(1, len(re.findall(r"[.!؟](?:\s|$)", text)))
    return {
        "id": raw["id"],
        "language": "ar",
        "cefr": "A1",
        "unit": 2,
        "sequence": raw["sequence"],
        "revision": 1,
        "title": raw["title"],
        "passage_type": raw["passage_type"],
        "genre": raw["genre"],
        "domains": raw["domains"],
        "topics": raw["topics"],
        "text": text,
        "word_count": len(text.split()),
        "sentence_count": sentence_count,
        "estimated_known_token_coverage": 0,
        "new_lexical_targets": [make_target(rank, text, lex) for rank in raw["new_ranks"]],
        "review_lexical_targets": raw["reviews"],
        "grammar_targets": raw["grammar_targets"],
        "discourse_targets": raw["discourse_targets"],
        "questions": questions,
        "answer_key": answers,
        "speed_training": {
            "timed": raw["passage_type"] == "fluency",
            "benchmark_eligible": False,
            "comprehension_gate": 0.8,
            "new_word_policy": "none" if raw["passage_type"] == "fluency" else "controlled",
            "notes": "Generation-stage passage; benchmark and speed-quality decisions are deferred to the final audit phase."
        },
        "quality": {
            "status": "draft",
            "linguistic_review": "pending",
            "pedagogical_review": "pending",
            "coverage_check": "pending",
            "answer_key_check": "pending",
            "schema_check": "pending",
            "fact_check": "not_required",
            "notes": [
                "Generation-stage first draft written to the project passage standard.",
                "Formal validity, linguistic, pedagogical, answer-key, coverage, spacing, and fluency audits are deferred to the final multi-pass audit phase."
            ]
        },
        "paired_text_group": None,
        "prerequisites": [],
        "difficulty_notes_internal": None,
        "reader_tags": ["unit_role:" + raw["passage_type"], "generation_batch"],
        "complexity_profile": {
            "mean_sentence_length": None,
            "median_sentence_length": None,
            "clause_count": None,
            "subordination_count": None,
            "coordination_count": None,
            "connective_diversity": None,
            "lexical_diversity": None,
            "reference_chain_max_distance": None,
            "multiword_expression_count": None,
            "morphology_notes": "A1 generation-stage draft; keep morphology transparent and high-frequency.",
            "inference_depth": "local"
        }
    }


def main():
    existing = [json.loads(line) for line in PASSAGES.read_text(encoding="utf-8").splitlines() if line.strip()]
    existing = [record for record in existing if record.get("unit") != 2]
    lex = lexicon_by_rank()
    new_records = [build_record(raw, lex) for raw in RAW]
    if len(new_records) != 6 or any(len(r["questions"]) != 10 or len(r["answer_key"]) != 10 for r in new_records):
        raise SystemExit("Arabic A1 Unit 02 generation contract failed")
    all_records = sorted(existing + new_records, key=lambda r: (r.get("unit", 0), r.get("sequence", 0)))
    PASSAGES.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in all_records),
        encoding="utf-8",
    )
    print("generated Arabic A1 Unit 02: six passages, sixty questions, sixty answers")


if __name__ == "__main__":
    main()
