#!/usr/bin/env python3
"""Generate Arabic A1 Unit 04: family and friends."""

from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASSAGES = ROOT / "reading" / "arabic" / "a1" / "passages.jsonl"
LEXICON = ROOT / "reading" / "lexicons" / "arabic.jsonl"

TARGETS = {
    122: ("أب", "father", ["scenario_resolution"]),
    114: ("ابن", "son", ["category_relation"]),
    152: ("اسم", "name", ["scenario_resolution"]),
    99: ("شخص", "person", ["category_relation"]),
    127: ("مرحبا", "hello; welcome", ["scenario_resolution"]),
    76: ("يقول", "says; tells", ["behavior_interpretation"]),
    134: ("أخبر", "told; informed", ["behavior_interpretation", "scenario_resolution"]),
    156: ("ناس", "people", ["example_instance"]),
    107: ("جميع", "all; everyone", ["category_relation"]),
    131: ("أمام", "in front of", ["scenario_resolution"]),
}


def qa(items):
    qs, ans = [], []
    for i, (typ, prompt, answer, tids) in enumerate(items, 1):
        q = {"id": f"q{i}", "type": typ, "prompt": prompt, "answer_id": f"a{i}"}
        if tids: q["target_ids"] = tids
        qs.append(q); ans.append({"id": f"a{i}", "question_id": f"q{i}", "answer": answer, "explanation": ""})
    if len(qs) != 10: raise ValueError("ten questions required")
    return qs, ans

RAW = [
    {
      "id":"ar-a1-u04-p01","sequence":19,"title":"صورة العائلة","passage_type":"instructional","genre":"simple description","domains":["personal"],"topics":["family","photo","relationships"],
      "text":"تجلس ليلى مع صديقتها مريم وتنظران إلى صورة عائلية. تشير ليلى إلى رجل يقف بجانبها وتقول: هذا أبي. أب ليلى يعمل في مدرسة قريبة ويحب القراءة. ثم تشير إلى طفل صغير وتقول: هذا ابن أخي، واسمه سامر. تسأل مريم: هل سامر ابنك؟ تضحك ليلى وتقول: لا، هو ابن أخي، وأنا عمته. في الصورة تقف أم ليلى أيضًا، ويقف الجميع قريبين من بعضهم. تقول مريم: الآن أعرف أباك وبعض أفراد عائلتك. تقول ليلى: في مرة أخرى سأريك صورة أكبر، لأن عندنا ناسًا كثيرين في العائلة.",
      "new_ranks":[122,114],
      "reviews":[{"id":"ar-r124","form":"يحب","review_stage":"R3","representation":"running_text"},{"id":"ar-r100","form":"مرة","review_stage":"R3","representation":"running_text"}],
      "grammar":[{"id":"ar-a1-family-possession","role":"new","description":"basic family possession/reference with أبي/أخي"},{"id":"ar-a1-family-relation","role":"new","description":"simple kinship relation statements"}],
      "discourse":[{"id":"a1-photo-reference","role":"new","description":"resolve family references in a simple photo description"}],
      "qa":[
        ("gist","ماذا تشرح ليلى لمريم؟","من هم بعض أفراد عائلتها في الصورة.",None),
        ("literal_detail","من سامر؟","ابن أخي ليلى.",None),
        ("vocabulary_in_context","ماذا يعني «أب» في «هذا أبي»؟","والد ليلى.",["ar-r122"]),
        ("vocabulary_in_context","ماذا يعني «ابن» في «ابن أخي»؟","ولد ذكر مرتبط بأبيه أو أمه؛ هنا هو ولد أخي ليلى.",["ar-r114"]),
        ("reference_resolution","إلى من يعود الضمير في «هو ابن أخي»؟","إلى سامر.",None),
        ("single_word_definition","ما معنى «أب»؟","الوالد الذكر.",["ar-r122"]),
        ("single_word_definition","ما معنى «ابن»؟","الولد الذكر لشخص ما.",["ar-r114"]),
        ("contrast","هل «أب» و«ابن» يدلان على العلاقة نفسها؟","لا؛ الأب والد، والابن ولد.",["ar-r122","ar-r114"]),
        ("cloze_transfer","أكمل: خالد _____ أحمد، وأحمد والده.","ابن",["ar-r114"]),
        ("cloze_transfer","أكمل: هذا والدي؛ هو _____ي.","أب",["ar-r122"]),
      ]
    },
    {
      "id":"ar-a1-u04-p02","sequence":20,"title":"صديقة جديدة","passage_type":"reinforcement","genre":"school micro-story","domains":["personal","educational"],"topics":["friends","names","school"],
      "text":"في المدرسة ترى ليلى طالبة جديدة تجلس وحدها. تذهب إليها وتقول: مرحبًا، أنا ليلى. ما اسمك؟ تقول الطالبة: اسمي نور. تسأل ليلى: هل تعرفين أحدًا هنا؟ تقول نور: لا، أنت أول شخص أتحدث معه اليوم. تقول ليلى: لا بأس، سأريك الصف والساحة. تمشيان معًا، وتخبر ليلى نور بأسماء بعض الطلاب والمعلمين. بعد قليل تأتي مريم. تقول ليلى: هذه نور، وهي شخص جديد في صفنا. تقول مريم: مرحبًا يا نور. تبتسم نور وتقول: شكرًا، الآن أعرف اسم شخصين على الأقل. في وقت الاستراحة تجلس الفتيات معًا، ولا تبقى نور وحدها.",
      "new_ranks":[152,99],
      "reviews":[{"id":"ar-r122","form":"أب","review_stage":"R1","representation":"other"},{"id":"ar-r114","form":"ابن","review_stage":"R1","representation":"other"},{"id":"ar-r74","form":"أول","review_stage":"R3","representation":"running_text"}],
      "grammar":[{"id":"ar-a1-name-question","role":"new","description":"ما اسمك؟ / اسمي ..."},{"id":"ar-a1-person-reference","role":"new","description":"simple person reference with شخص"}],
      "discourse":[{"id":"a1-introduction-sequence","role":"new","description":"follow a simple first-meeting introduction"}],
      "qa":[
        ("literal_detail","ما اسم الطالبة الجديدة؟","نور.",None),
        ("cause_effect","لماذا تذهب ليلى إلى نور؟","لأن نور تجلس وحدها وهي جديدة في الصف.",None),
        ("vocabulary_in_context","ماذا يعني «اسم» في «ما اسمك؟»؟","الكلمة التي يُعرَف بها الشخص.",["ar-r152"]),
        ("vocabulary_in_context","ماذا يعني «شخص» في «أول شخص أتحدث معه»؟","إنسان أو فرد واحد.",["ar-r99"]),
        ("sequence","من تقابل نور بعد ليلى؟","مريم.",None),
        ("single_word_definition","ما معنى «اسم»؟","الكلمة التي تميز شخصًا أو شيئًا وتدل عليه.",["ar-r152"]),
        ("single_word_definition","ما معنى «شخص»؟","إنسان واحد.",["ar-r99"]),
        ("grammar_choice","أي سؤال مناسب لمعرفة اسم شخص: «ما اسمك؟» أم «أين اسمك؟»؟","ما اسمك؟",["ar-r152"]),
        ("cloze_transfer","أكمل: _____ي عمر.","اسم",["ar-r152"]),
        ("cloze_transfer","أكمل: هناك _____ عند الباب يريد أن يسأل سؤالًا.","شخص",["ar-r99"]),
      ]
    },
    {
      "id":"ar-a1-u04-p03","sequence":21,"title":"زيارة قصيرة","passage_type":"interleaved","genre":"dialogue-like narrative","domains":["personal"],"topics":["neighbors","greeting","conversation"],
      "text":"في عصر السبت تذهب ليلى مع أمها إلى بيت جارتهم أمينة. عندما تفتح أمينة الباب تقول: مرحبًا، تفضلا. تقول أم ليلى: مرحبًا، شكرًا لك. في الداخل تجلس ابنة أمينة مع كتاب. تقول أمينة: هذه ابنتي هدى. تقول هدى: مرحبًا يا ليلى. تجلس ليلى قربها وتسألها عن المدرسة. تقول هدى إنها تحب القراءة، وتقول ليلى إنها تحب المكتبة أيضًا. بعد قليل يأتي أب هدى ويقول: مرحبًا بالجميع. يتحدث الناس قليلًا عن المدرسة والحي. قبل أن تعود ليلى إلى منزلها تقول هدى: تعالي مرة أخرى. تقول ليلى: نعم، وسوف أخبرك عندما أذهب إلى المكتبة.",
      "new_ranks":[127,76],
      "reviews":[{"id":"ar-r152","form":"اسم","review_stage":"R1","representation":"other"},{"id":"ar-r99","form":"شخص","review_stage":"R1","representation":"other"},{"id":"ar-r112","form":"شكرا","review_stage":"R3","representation":"running_text"}],
      "grammar":[{"id":"ar-a1-greeting","role":"new","description":"مرحبا as a greeting"},{"id":"ar-a1-say-report","role":"new","description":"يقول/تقول + short utterance or clause"}],
      "discourse":[{"id":"a1-social-exchange","role":"new","description":"follow greetings and short turns in a visit"}],
      "qa":[
        ("literal_detail","من هدى؟","ابنة الجارة أمينة.",None),
        ("literal_detail","ماذا تحب هدى؟","القراءة.",None),
        ("vocabulary_in_context","ماذا تعني «مرحبا» عند فتح الباب؟","تحية ترحيب عند اللقاء.",["ar-r127"]),
        ("vocabulary_in_context","ماذا يعني «يقول» في النص؟","يتكلم بكلمات أو يخبر الآخرين بشيء.",["ar-r76"]),
        ("sequence","ماذا تقول ليلى قبل أن تعود إلى منزلها؟","توافق على زيارة هدى مرة أخرى وتقول إنها ستخبرها عند الذهاب إلى المكتبة.",None),
        ("single_word_definition","ما معنى «مرحبا»؟","تحية تستخدم عند اللقاء أو الترحيب.",["ar-r127"]),
        ("single_word_definition","ما معنى «يقول»؟","يتكلم أو ينطق بكلام.",["ar-r76"]),
        ("person_form","في «تقول هدى»، من صاحب الفعل؟","هدى.",["ar-r76"]),
        ("cloze_transfer","أكمل التحية: «_____ يا مريم.»","مرحبا",["ar-r127"]),
        ("cloze_transfer","أكمل: المعلم _____ إن الدرس يبدأ الآن.","يقول",["ar-r76"]),
      ]
    },
    {
      "id":"ar-a1-u04-p04","sequence":22,"title":"خبر لصديقة","passage_type":"transfer","genre":"short message and narrative","domains":["personal"],"topics":["message","friends","information"],
      "text":"بعد المدرسة ترسل ليلى رسالة إلى هدى. تكتب: «مرحبًا يا هدى. أخبرتني أمي أن المكتبة عندها نشاط صغير غدًا. سيكون هناك ناس من الحي، ويمكن أن نقرأ معًا. أخبريني إذا كنت تريدين الذهاب.» بعد قليل ترد هدى: «شكرًا لأنك أخبرتني. أريد أن أذهب، وسأخبر أبي أيضًا.» في اليوم التالي تلتقيان أمام المكتبة. تقول هدى: أخبرت أبي عن النشاط، فقال إن الفكرة جيدة. داخل المكتبة ترى ليلى ناسًا تعرفهم وناسًا لا تعرفهم. تخبر هدى باسم بعض الأشخاص، ثم تختاران كتابًا وتجلسان للقراءة. تقول هدى: من الجيد أن نخبر أصدقاءنا بالأشياء الجميلة التي يمكن أن نفعلها معًا.",
      "new_ranks":[134,156],
      "reviews":[{"id":"ar-r127","form":"مرحبا","review_stage":"R1","representation":"running_text"},{"id":"ar-r76","form":"يقول","review_stage":"R1","representation":"running_text"},{"id":"ar-r99","form":"شخص","review_stage":"R2","representation":"running_text"}],
      "grammar":[{"id":"ar-a1-tell-inform","role":"new","description":"أخبر + person about simple information"},{"id":"ar-a1-people-plural","role":"new","description":"ناس as a common collective plural noun"}],
      "discourse":[{"id":"a1-message-information","role":"new","description":"extract information and response from a short message"}],
      "qa":[
        ("literal_detail","ما الخبر الذي ترسله ليلى إلى هدى؟","أن في المكتبة نشاطًا صغيرًا في اليوم التالي.",None),
        ("literal_detail","أين تلتقي ليلى وهدى؟","أمام المكتبة.",None),
        ("vocabulary_in_context","ماذا يعني «أخبرتني أمي»؟","أن أم ليلى أعطتها معلومة أو قالت لها خبرًا.",["ar-r134"]),
        ("vocabulary_in_context","ماذا تعني «ناس» في «ناس من الحي»؟","مجموعة من الأشخاص.",["ar-r156"]),
        ("cause_effect","لماذا تشكر هدى ليلى؟","لأن ليلى أخبرتها عن النشاط.",None),
        ("single_word_definition","ما معنى «أخبر»؟","أعطى شخصًا معلومة أو خبرًا.",["ar-r134"]),
        ("single_word_definition","ما معنى «ناس»؟","أشخاص؛ مجموعة من البشر.",["ar-r156"]),
        ("contrast","أيهما يدل على مجموعة: «شخص» أم «ناس»؟","ناس.",["ar-r99","ar-r156"]),
        ("cloze_transfer","أكمل: سأ_____ صديقي بموعد الدرس.","أخبر",["ar-r134"]),
        ("cloze_transfer","أكمل: في السوق _____ كثيرون اليوم.","ناس",["ar-r156"]),
      ]
    },
    {
      "id":"ar-a1-u04-p05","sequence":23,"title":"لقاء العائلة","passage_type":"checkpoint","genre":"family gathering narrative","domains":["personal"],"topics":["family","gathering","photo"],
      "text":"في نهاية الأسبوع تجتمع عائلة ليلى في بيت جدتها. يأتي أب ليلى وأمها وأخوها، ويأتي بعض الأقارب أيضًا. عندما يصل الجميع تقول الجدة: مرحبًا بكم جميعًا. يجلس الناس في غرفة كبيرة ويتحدثون عن المدرسة والعمل والطعام. بعد الغداء تريد الجدة صورة للعائلة. يقف الجميع أمام البيت. تقول الجدة: الأطفال أمام الكبار، والناس الطويلون في الخلف. تضحك ليلى وتقول لابن أخيها سامر: قف أمامي حتى تظهر في الصورة. يسأل سامر: هل جميع الناس هنا من عائلتنا؟ تقول ليلى: نعم، كل شخص هنا قريب لنا. بعد الصورة تخبر ليلى مريم برسالة قصيرة أن العائلة اجتمعت، ثم تعود إلى الحديث مع الجميع.",
      "new_ranks":[107,131],
      "reviews":[{"id":"ar-r134","form":"أخبر","review_stage":"R1","representation":"running_text"},{"id":"ar-r156","form":"ناس","review_stage":"R1","representation":"running_text"},{"id":"ar-r122","form":"أب","review_stage":"R2","representation":"running_text"},{"id":"ar-r114","form":"ابن","review_stage":"R2","representation":"running_text"}],
      "grammar":[{"id":"ar-a1-all-group","role":"new","description":"جميع for an entire group"},{"id":"ar-a1-front-location","role":"new","description":"أمام for front-of spatial relation"}],
      "discourse":[{"id":"a1-group-reference","role":"integration","description":"track individuals versus the whole group"}],
      "qa":[
        ("gist","ما الحدث الرئيسي في النص؟","اجتماع عائلة ليلى والتقاط صورة جماعية.",None),
        ("literal_detail","أين يقف الجميع لالتقاط الصورة؟","أمام البيت.",None),
        ("vocabulary_in_context","ماذا تعني «جميع» في «مرحبًا بكم جميعًا»؟","كل الأشخاص الموجودين بلا استثناء.",["ar-r107"]),
        ("vocabulary_in_context","ماذا تعني «أمام» في «أمام البيت»؟","في الجهة التي تقع في مقدمة البيت.",["ar-r131"]),
        ("reference_resolution","إلى من تشير «الجميع» عندما تطلب الجدة الصورة؟","إلى أفراد العائلة الموجودين.",["ar-r107"]),
        ("single_word_definition","ما معنى «جميع»؟","كل أفراد المجموعة.",["ar-r107"]),
        ("single_word_definition","ما معنى «أمام»؟","في الجهة المقابلة للمقدمة أو قدام الشيء.",["ar-r131"]),
        ("contrast","أيهما يدل على المجموعة كلها: «بعض» أم «جميع»؟","جميع.",["ar-r53","ar-r107"]),
        ("cloze_transfer","أكمل: يقف الطالب _____ المعلم.","أمام",["ar-r131"]),
        ("cloze_transfer","أكمل: حضر الطلاب _____ إلى الصف.","جميعًا",["ar-r107"]),
      ]
    },
    {
      "id":"ar-a1-u04-p06","sequence":24,"title":"الناس القريبون من ليلى","passage_type":"fluency","genre":"connected social-life narrative","domains":["personal","educational"],"topics":["family","friends","neighbors","review"],
      "text":"تعرف ليلى الآن ناسًا كثيرين في حياتها اليومية. في البيت تعرف أباها وأمها وأخوها، وتعرف أن سامر ابن أخيها. في المدرسة تقابل أشخاصًا آخرين، وتسأل الطالب الجديد عن اسمه حتى تعرفه. عندما تزور جارتها تقول مرحبًا، وتسمع ما يقول الناس في الحديث. وإذا عرفت خبرًا جميلًا يمكن أن تخبر صديقتها به. في بعض الأيام تلتقي العائلة، فيكون جميع الأقارب في مكان واحد. عند التقاط صورة يقف الأطفال أمام الكبار. ليلى لا تعرف كل شخص في الحي، لكنها تعرف كيف تبدأ الحديث: تقول مرحبًا، تسأل عن الاسم، تستمع إلى ما يقول الشخص، ثم تخبره بشيء عن نفسها. بهذه الطريقة تصبح الوجوه الجديدة مألوفة شيئًا فشيئًا.",
      "new_ranks":[],
      "reviews":[
        {"id":"ar-r122","form":"أب","review_stage":"R2","representation":"running_text"},{"id":"ar-r114","form":"ابن","review_stage":"R2","representation":"running_text"},{"id":"ar-r152","form":"اسم","review_stage":"R2","representation":"running_text"},{"id":"ar-r99","form":"شخص","review_stage":"R2","representation":"running_text"},{"id":"ar-r127","form":"مرحبا","review_stage":"R2","representation":"running_text"},{"id":"ar-r76","form":"يقول","review_stage":"R2","representation":"running_text"},{"id":"ar-r134","form":"أخبر","review_stage":"R2","representation":"running_text"},{"id":"ar-r156","form":"ناس","review_stage":"R2","representation":"running_text"},{"id":"ar-r107","form":"جميع","review_stage":"R1","representation":"running_text"},{"id":"ar-r131","form":"أمام","review_stage":"R1","representation":"running_text"}],
      "grammar":[{"id":"ar-a1-u04-cumulative","role":"integration","description":"recycle family, person reference, greetings, reported information, and spatial relation"}],
      "discourse":[{"id":"a1-social-fluency","role":"integration","description":"high-coverage cumulative social-life reading"}],
      "qa":[
        ("gist","ما الفكرة الرئيسية في النص؟","ليلى تعرف كيف تتعامل مع أفراد العائلة والأصدقاء والناس الجدد.",None),
        ("literal_detail","من سامر بالنسبة إلى ليلى؟","ابن أخيها.",["ar-r114"]),
        ("literal_detail","ماذا تسأل ليلى الطالب الجديد؟","تسأله عن اسمه.",["ar-r152"]),
        ("sequence","ما الخطوات التي تستخدمها ليلى لبدء الحديث مع شخص جديد؟","تحييه، وتسأل عن اسمه، وتستمع إليه، ثم تخبره بشيء عن نفسها.",None),
        ("summary","لخص علاقات ليلى الاجتماعية في جملة واحدة.","لها عائلة وأصدقاء وجيران، وهي تعرف كيف تتحدث مع الأشخاص الجدد.",None),
        ("single_word_definition","ما معنى «ناس»؟","مجموعة من الأشخاص.",["ar-r156"]),
        ("single_word_definition","ما معنى «جميع»؟","كل أفراد المجموعة.",["ar-r107"]),
        ("contrast","أيهما تحية: «مرحبا» أم «أمام»؟","مرحبا.",["ar-r127","ar-r131"]),
        ("grammar_function","ماذا يحدد «أمام» في «يقف الأطفال أمام الكبار»؟","الموقع المكاني للأطفال بالنسبة إلى الكبار.",["ar-r131"]),
        ("contrast","أيهما فرد واحد: «شخص» أم «ناس»؟","شخص.",["ar-r99","ar-r156"]),
      ]
    }
]


def lex_by_rank():
    out={}
    for line in LEXICON.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row=json.loads(line); out[row["rank"]]=row
    return out


def target(rank,text,lex):
    form,sense,strategies=TARGETS[rank]; src=lex[rank]
    return {"id":f"ar-r{rank}","form":form,"lemma":form,"part_of_speech":src.get("part_of_speech_source"),"intended_sense":sense,"register":"contemporary standard","variety":"MSA","context_strategy":strategies,"first_introduced":True,"exposures_in_text":max(1,text.count(form)),"source_lexicon":src.get("source_file"),"source_rank":rank,"beyond_base":False}


def build(raw,lex):
    qs,ans=qa(raw["qa"]); text=raw["text"]
    return {"id":raw["id"],"language":"ar","cefr":"A1","unit":4,"sequence":raw["sequence"],"revision":1,"title":raw["title"],"passage_type":raw["passage_type"],"genre":raw["genre"],"domains":raw["domains"],"topics":raw["topics"],"text":text,"word_count":len(text.split()),"sentence_count":max(1,len(re.findall(r"[.!؟](?:\s|$)",text))),"estimated_known_token_coverage":0,"new_lexical_targets":[target(r,text,lex) for r in raw["new_ranks"]],"review_lexical_targets":raw["reviews"],"grammar_targets":raw["grammar"],"discourse_targets":raw["discourse"],"questions":qs,"answer_key":ans,"speed_training":{"timed":raw["passage_type"]=="fluency","benchmark_eligible":False,"comprehension_gate":0.8,"new_word_policy":"none" if raw["passage_type"]=="fluency" else "controlled","notes":"Generation-stage passage; formal fluency/coverage decision deferred to final audit."},"quality":{"status":"draft","linguistic_review":"pending","pedagogical_review":"pending","coverage_check":"pending","answer_key_check":"pending","schema_check":"pending","fact_check":"not_required","notes":["High-quality generation-stage draft; formal audits deferred to the final multi-pass review phase."]},"paired_text_group":None,"prerequisites":[],"difficulty_notes_internal":None,"reader_tags":["unit_role:"+raw["passage_type"],"generation_batch"],"complexity_profile":{"mean_sentence_length":None,"median_sentence_length":None,"clause_count":None,"subordination_count":None,"coordination_count":None,"connective_diversity":None,"lexical_diversity":None,"reference_chain_max_distance":None,"multiword_expression_count":None,"morphology_notes":"A1 generation-stage draft; transparent contemporary MSA.","inference_depth":"local"}}


def main():
    existing=[json.loads(x) for x in PASSAGES.read_text(encoding="utf-8").splitlines() if x.strip()]
    existing=[r for r in existing if r.get("unit")!=4]
    lex=lex_by_rank(); new=[build(r,lex) for r in RAW]
    if len(new)!=6 or any(len(r["questions"])!=10 or len(r["answer_key"])!=10 for r in new): raise SystemExit("Unit 04 generation contract failed")
    rows=sorted(existing+new,key=lambda r:(r.get("unit",0),r.get("sequence",0)))
    PASSAGES.write_text("".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rows),encoding="utf-8")
    print("generated Arabic A1 Unit 04: six passages, sixty questions, sixty answers")

if __name__=="__main__": main()
