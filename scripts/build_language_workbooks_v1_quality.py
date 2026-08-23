#!/usr/bin/env python3
"""Quality wrapper for the v1 language workbooks.

Arabic/French: source-diverse, English-unique, balanced ManyThings/Tatoeba selection.
Urdu: original controlled standard-Urdu conversation corpus generated from reviewed
sentence families, replacing the noisy external corpus discovered in release QA.
"""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from collections import Counter

import build_language_workbooks_v1 as base

QUALITY_META = {}

PROPER_FILLER = {
    "tom", "mary", "john", "jack", "jim", "bob", "alice", "ken", "nancy", "bill",
    "mike", "jane", "peter", "paul", "george", "henry", "david", "charles", "linda",
    "susan", "japan", "tokyo", "boston", "paris", "london", "america", "lincoln",
}
AR_DIALECT = re.compile(r"(?:^|[\s،,.!?؟؛:])(?:شو|إيش|ايش|ليش|مو|مش|عايز|عاوز|بدك|بدي|وين|شلون|دلوقتي)(?=$|[\s،,.!?؟؛:])")


def contributor(attr: str) -> str:
    names = re.findall(r"\(([^()]*)\)", attr or "")
    return names[-1].strip() if names else "unknown"


def quality_score(en: str) -> float:
    words = base.english_words(en)
    st = set(words)
    n = len(words)
    score = 3 * min(4, len(st & base.CONV))
    if 3 <= n <= 9:
        score += 8
    elif 10 <= n <= 13:
        score += 5
    elif 14 <= n <= 18:
        score += 2
    elif n == 1:
        score -= 2
    if "?" in en:
        score += 0.5
    if "!" in en:
        score += 0.25
    return score


def bad_general_sentence(en: str, target: str) -> bool:
    low = en.casefold()
    words = set(base.english_words(en))
    if words & PROPER_FILLER:
        return True
    if re.search(r"https?://|www\.|\b\d{4}\b", en):
        return True
    if any(x in low for x in ("suicide", "porn", "murder", "kill him", "kill her")):
        return True
    if '"' in en or '“' in target or '”' in target:
        return True
    mids = re.findall(r"\b[A-Z][a-z]{2,}\b", en[1:])
    if any(x.casefold() not in {"english", "french", "arabic", "urdu"} for x in mids):
        return True
    return False


def load_external(cfg):
    zpath = base.SRC / f"{cfg['code']}-eng.zip"
    base.download(cfg["zip"], zpath)
    with zipfile.ZipFile(zpath) as z:
        raw = z.read(cfg["txt"]).decode("utf-8-sig")
    candidates = []
    seen_target = set()
    for line in raw.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        en, target, attr = parts[0].strip(), parts[1].strip(), parts[2].strip()
        nt, ne = base.norm(target), base.norm(en)
        if not nt or nt in seen_target or not ne:
            continue
        if "CC-BY 2.0" not in attr or "tatoeba.org" not in attr:
            continue
        if base.script_ratio(target, cfg["script"]) < 0.72:
            continue
        n = len(base.english_words(en))
        if not 1 <= n <= 18 or len(target) > 180 or len(en) > 180:
            continue
        if bad_general_sentence(en, target):
            continue
        if cfg["name"] == "Arabic" and AR_DIALECT.search(target):
            continue
        seen_target.add(nt)
        candidates.append({
            "target": target,
            "english": en,
            "attribution": attr,
            "score": quality_score(en),
            "words": n,
            "contributor": contributor(attr),
        })
    return candidates, base.sha256(zpath)


def band(words: int) -> str:
    return "A" if words <= 4 else "B" if words <= 8 else "C" if words <= 13 else "D"


def select_external(cfg):
    candidates, source_hash = load_external(cfg)
    quotas = {"A": 250, "B": 350, "C": 300, "D": 100}
    q_share = 0.30
    by = {}
    for b in quotas:
        group = [r for r in candidates if band(r["words"]) == b]
        by[(b, True)] = sorted((r for r in group if "?" in r["english"]), key=lambda r: (-r["score"], r["words"], r["english"]))
        by[(b, False)] = sorted((r for r in group if "?" not in r["english"]), key=lambda r: (-r["score"], r["words"], r["english"]))

    selected, seen_t, seen_e = [], set(), set()
    contrib = Counter()

    def pick(pool, needed, cap):
        picked = 0
        for r in pool:
            if picked >= needed:
                break
            nt, ne = base.norm(r["target"]), base.norm(r["english"])
            if nt in seen_t or ne in seen_e or contrib[r["contributor"]] >= cap:
                continue
            selected.append(r); seen_t.add(nt); seen_e.add(ne); contrib[r["contributor"]] += 1; picked += 1
        return picked

    for b, total in quotas.items():
        qn = round(total * q_share)
        sn = total - qn
        got_q = pick(by[(b, True)], qn, 160)
        got_s = pick(by[(b, False)], sn, 160)
        if got_q < qn:
            got_q += pick(by[(b, True)], qn - got_q, 240)
        if got_s < sn:
            got_s += pick(by[(b, False)], sn - got_s, 240)
        if got_q != qn or got_s != sn:
            raise SystemExit(f"{cfg['name']}: insufficient quality candidates in band {b}: q={got_q}/{qn}, s={got_s}/{sn}")

    selected.sort(key=lambda r: ({"A":0,"B":1,"C":2,"D":3}[band(r["words"])], r["words"], -r["score"], r["english"]))
    for i, r in enumerate(selected, 1):
        r["rank"] = i
        r["level"] = band(r["words"])
    if len(selected) != 1000 or len(seen_t) != 1000 or len(seen_e) != 1000:
        raise SystemExit(f"{cfg['name']}: balanced sentence uniqueness gate failed")
    qn = sum("?" in r["english"] for r in selected)
    top_name, top_count = contrib.most_common(1)[0]
    QUALITY_META[cfg["name"].casefold()] = {
        "source_type": "ManyThings/Tatoeba CC BY 2.0 France",
        "candidate_count": len(candidates),
        "target_unique": len(seen_t),
        "english_unique": len(seen_e),
        "question_count": qn,
        "question_share": round(qn / 1000, 3),
        "top_contributor": top_name,
        "top_contributor_rows": top_count,
        "top_contributor_share": round(top_count / 1000, 3),
        "band_counts": dict(Counter(r["level"] for r in selected)),
    }
    return selected, len(candidates), source_hash


OBJECTS = [
('کتاب','book'),('قلم','pen'),('پنسل','pencil'),('کاپی','notebook'),('لغت','dictionary'),('نقشہ','map'),('ٹکٹ','ticket'),('پاسپورٹ','passport'),('شناختی کارڈ','ID card'),('چابی','key'),('موبائل فون','mobile phone'),('چارجر','charger'),('لیپ ٹاپ','laptop'),('کیمرہ','camera'),('گھڑی','watch'),('چشمہ','pair of glasses'),('بیگ','bag'),('بٹوہ','wallet'),('پرس','purse'),('چھتری','umbrella'),('جیکٹ','jacket'),('کمبل','blanket'),('تکیہ','pillow'),('تولیہ','towel'),('صابن','soap'),('بوتل','bottle'),('گلاس','glass'),('کپ','cup'),('پلیٹ','plate'),('چمچ','spoon'),('کانٹا','fork'),('چاقو','knife'),('پانی','water'),('چائے','tea'),('کافی','coffee'),('دودھ','milk'),('روٹی','bread'),('جوس','juice'),('دوا','medicine'),('رسید','receipt')]
PLACES = [
('گھر','house'),('ہوٹل','hotel'),('ریستوران','restaurant'),('کیفے','cafe'),('ریلوے اسٹیشن','train station'),('بس اسٹیشن','bus station'),('بس اسٹاپ','bus stop'),('ہوائی اڈا','airport'),('بینک','bank'),('ہسپتال','hospital'),('کلینک','clinic'),('دواخانہ','pharmacy'),('بازار','market'),('دکان','shop'),('سپرمارکیٹ','supermarket'),('اسکول','school'),('یونیورسٹی','university'),('دفتر','office'),('لائبریری','library'),('پارک','park'),('مسجد','mosque'),('میوزیم','museum'),('سینما','cinema'),('تھیٹر','theater'),('پولیس اسٹیشن','police station'),('سفارت خانہ','embassy'),('ڈاک خانہ','post office'),('مال','shopping mall'),('جم','gym'),('اسٹیڈیم','stadium')]
ACTIONS = [
('انتظار کرنا','انتظار کر','انتظار کیجیے','انتظار نہ کیجیے','wait'),('اب شروع کرنا','اب شروع کر','اب شروع کیجیے','ابھی شروع نہ کیجیے','start now'),('اب روانہ ہونا','اب روانہ ہو','اب روانہ ہو جائیے','ابھی روانہ نہ ہوں','leave now'),('دروازہ کھولنا','دروازہ کھول','دروازہ کھولیے','دروازہ نہ کھولیے','open the door'),('دروازہ بند کرنا','دروازہ بند کر','دروازہ بند کیجیے','دروازہ بند نہ کیجیے','close the door'),('بتی جلانا','بتی جلا','بتی جلائیے','بتی نہ جلائیے','turn on the light'),('بتی بند کرنا','بتی بند کر','بتی بند کیجیے','بتی بند نہ کیجیے','turn off the light'),('ٹیکسی بلانا','ٹیکسی بلا','ٹیکسی بلائیے','ٹیکسی نہ بلائیے','call a taxi'),('ڈاکٹر کو بلانا','ڈاکٹر کو بلا','ڈاکٹر کو بلائیے','ڈاکٹر کو نہ بلائیے','call a doctor'),('فارم پڑھنا','فارم پڑھ','فارم پڑھیے','فارم نہ پڑھیے','read the form'),('فارم پُر کرنا','فارم پُر کر','فارم پُر کیجیے','فارم پُر نہ کیجیے','fill out the form'),('فارم پر دستخط کرنا','فارم پر دستخط کر','فارم پر دستخط کیجیے','فارم پر دستخط نہ کیجیے','sign the form'),('پتا دیکھنا','پتا دیکھ','پتا دیکھیے','پتا نہ دیکھیے','check the address'),('وقت دیکھنا','وقت دیکھ','وقت دیکھیے','وقت نہ دیکھیے','check the time'),('ٹکٹ خریدنا','ٹکٹ خرید','ٹکٹ خریدیے','ٹکٹ نہ خریدیے','buy a ticket'),('کمرہ بک کرنا','کمرہ بک کر','کمرہ بک کیجیے','کمرہ بک نہ کیجیے','book a room'),('کھانا منگوانا','کھانا منگوا','کھانا منگوائیے','کھانا نہ منگوائیے','order food'),('پانی پینا','پانی پی','پانی پیجیے','پانی نہ پیجیے','drink water'),('کچھ کھانا','کچھ کھا','کچھ کھائیے','کچھ نہ کھائیے','eat something'),('دوا لینا','دوا لے','دوا لیجیے','دوا نہ لیجیے','take the medicine'),('آرام کرنا','آرام کر','آرام کیجیے','آرام نہ کیجیے','rest'),('یہاں بیٹھنا','یہاں بیٹھ','یہاں بیٹھیے','یہاں نہ بیٹھیے','sit here'),('یہاں کھڑے ہونا','یہاں کھڑے ہو','یہاں کھڑے ہو جائیے','یہاں کھڑے نہ ہوں','stand here'),('آہستہ بولنا','آہستہ بول','آہستہ بولیے','اتنا آہستہ نہ بولیے','speak slowly'),('دوبارہ کہنا','دوبارہ کہہ','دوبارہ کہیے','دوبارہ نہ کہیے','say it again'),('نام لکھنا','نام لکھ','نام لکھیے','نام نہ لکھیے','write the name'),('پاسپورٹ دکھانا','پاسپورٹ دکھا','پاسپورٹ دکھائیے','پاسپورٹ نہ دکھائیے','show the passport'),('رسید سنبھال کر رکھنا','رسید سنبھال کر رکھ','رسید سنبھال کر رکھیے','رسید مت پھینکیے','keep the receipt'),('مدد مانگنا','مدد مانگ','مدد مانگیے','مدد مانگنے سے نہ ہچکچائیے','ask for help'),('ہدایات پر عمل کرنا','ہدایات پر عمل کر','ہدایات پر عمل کیجیے','ہدایات کو نظر انداز نہ کیجیے','follow the instructions')]
NEG_EN = {'eat something':'Please do not eat anything.','speak slowly':'Please do not speak so slowly.','keep the receipt':'Please do not throw away the receipt.','ask for help':'Please do not hesitate to ask for help.','follow the instructions':'Please do not ignore the instructions.'}
ADJS = [('آسان','easy'),('مشکل','difficult'),('ضروری','necessary'),('ممکن','possible'),('ناممکن','impossible'),('محفوظ','safe'),('خطرناک','dangerous'),('صحیح','correct'),('غلط','wrong'),('صاف','clean'),('خراب','bad'),('تیار','ready'),('کافی','enough'),('قیمتی','expensive'),('کم قیمت','inexpensive'),('تیز','fast'),('آہستہ','slow'),('قریب','nearby'),('دور','far away'),('بہتر','better'),('مختلف','different'),('اہم','important'),('واضح','clear'),('دلچسپ','interesting'),('مفید','useful'),('خالی','empty'),('مکمل','complete'),('دستیاب','available'),('مصروف','busy'),('پرسکون','quiet')]
TIMES = [('آج','today'),('آج صبح','this morning'),('آج دوپہر','this afternoon'),('آج شام','this evening'),('آج رات','tonight'),('کل صبح','tomorrow morning'),('کل دوپہر','tomorrow afternoon'),('کل شام','tomorrow evening'),('پیر کو','on Monday'),('منگل کو','on Tuesday'),('بدھ کو','on Wednesday'),('جمعرات کو','on Thursday'),('جمعہ کو','on Friday'),('ہفتے کو','on Saturday'),('اتوار کو','on Sunday'),('آٹھ بجے','at eight'),('نو بجے','at nine'),('دس بجے','at ten'),('گیارہ بجے','at eleven'),('دو بجے','at two'),('تین بجے','at three'),('چار بجے','at four'),('پانچ بجے','at five'),('چھ بجے','at six'),('سات بجے','at seven')]
CORE = [('جی ہاں۔','Yes.'),('نہیں، شکریہ۔','No, thank you.'),('بہت شکریہ۔','Thank you very much.'),('کوئی بات نہیں۔','No problem.'),('معاف کیجیے۔','Excuse me.'),('مجھے سمجھ نہیں آئی۔',"I didn't understand."),('اب مجھے سمجھ آ گئی ہے۔','Now I understand.'),('معاف کیجیے، دوبارہ کہیے۔','Sorry, please say that again.'),('ذرا آہستہ بولیے۔','Please speak a little more slowly.'),('کیا یہاں کوئی انگریزی بولتا ہے؟','Does anyone here speak English?'),('مجھے تھوڑی سی اردو آتی ہے۔','I speak a little Urdu.'),('اس کا مطلب کیا ہے؟','What does that mean?'),('اسے اردو میں کیا کہتے ہیں؟','What do you call this in Urdu?'),('براہِ کرم یہ لکھ دیجیے۔','Please write this down.'),('مجھے راستہ معلوم نہیں۔',"I don't know the way."),('مجھے مدد چاہیے۔','I need help.'),('ایمرجنسی ہے۔',"It's an emergency."),('ڈاکٹر کو بلائیے۔','Call a doctor.'),('پولیس کو بلائیے۔','Call the police.'),('میں ٹھیک ہوں۔',"I'm fine."),('ہم تیار ہیں۔',"We're ready."),('ابھی وقت ہے۔','There is still time.'),('جلدی کی ضرورت نہیں ہے۔',"There's no need to hurry."),('ہم بعد میں بات کریں گے۔',"We'll talk later."),('خدا حافظ۔','Goodbye.')]


def controlled_urdu():
    rows=[]
    def add(ur,en,family): rows.append({'target':ur,'english':en,'family':family})
    for ur,en in OBJECTS:
        for a,b in [(f'مجھے {ur} چاہیے۔',f'I need the {en}.'),(f'مجھے {ur} نہیں چاہیے۔',f"I don't need the {en}."),(f'کیا آپ کو {ur} چاہیے؟',f'Do you need the {en}?'),(f'ہمیں {ur} چاہیے۔',f'We need the {en}.'),(f'{ur} کہاں ہے؟',f'Where is the {en}?'),(f'کیا {ur} یہاں ہے؟',f'Is the {en} here?'),(f'براہِ کرم {ur} لے آئیے۔',f'Please bring the {en}.'),(f'براہِ کرم مجھے {ur} دیجیے۔',f'Please give me the {en}.'),(f'میرے پاس {ur} ہے۔',f'I have the {en}.'),(f'کیا آپ کے پاس {ur} ہے؟',f'Do you have the {en}?')]: add(a,b,'object')
    for ur,en in PLACES:
        for a,b in [(f'{ur} کہاں ہے؟',f'Where is the {en}?'),(f'کیا {ur} قریب ہے؟',f'Is the {en} nearby?'),(f'{ur} کتنی دور ہے؟',f'How far is the {en}?'),(f'ہمیں {ur} جانا ہے۔',f'We need to go to the {en}.'),(f'چلیے، {ur} چلیں۔',f"Let's go to the {en}.")]: add(a,b,'place')
    for inf,can,imp,neg,en in ACTIONS:
        neg_en=NEG_EN.get(en,f'Please do not {en}.')
        for a,b in [(f'ہمیں {inf} ہے۔',f'We need to {en}.'),(f'ہمیں {inf} چاہیے۔',f'We should {en}.'),(f'ہم {can} سکتے ہیں۔',f'We can {en}.'),(f'براہِ کرم {imp}۔',f'Please {en}.'),(f'براہِ کرم {neg}۔',neg_en)]: add(a,b,'action')
    for ur,en in ADJS:
        for a,b in [(f'یہ {ur} ہے۔',f'This is {en}.'),(f'کیا یہ {ur} ہے؟',f'Is this {en}?'),(f'وہ {ur} ہے۔',f'That is {en}.'),(f'یہ {ur} نہیں ہے۔',f'This is not {en}.'),(f'وہ {ur} نہیں ہے۔',f'That is not {en}.')]: add(a,b,'description')
    for ur,en in TIMES:
        for a,b in [(f'میں {ur} فارغ ہوں۔',f'I am free {en}.'),(f'ہم {ur} فارغ ہیں۔',f'We are free {en}.'),(f'کیا آپ {ur} فارغ ہیں؟',f'Are you free {en}?'),(f'کیا ہم {ur} ملیں؟',f'Shall we meet {en}?'),(f'ہم {ur} بات کر سکتے ہیں۔',f'We can talk {en}.')]: add(a,b,'time')
    for ur,en in CORE: add(ur,en,'core')
    if len(rows)!=1000 or len({base.norm(r['target']) for r in rows})!=1000 or len({base.norm(r['english']) for r in rows})!=1000:
        raise SystemExit('Urdu controlled corpus uniqueness/count gate failed')
    bad=re.compile(r'تمھ|چاہیئے|چاہئیے|لئیے|لیئے|جائو|آئو|دکھائو|پہت|زیارہ|بیواقوف|مسلہ|بجھے|ڈھیڑ|تھورے|پہنج|کرے گے|رہے ہے|گئے ہے')
    hits=[r['target'] for r in rows if bad.search(r['target'])]
    if hits: raise SystemExit(f'Urdu controlled corpus contains blocked legacy spellings: {hits[:5]}')
    for i,r in enumerate(rows,1):
        r['rank']=i; r['words']=len(base.english_words(r['english'])); r['level']=band(r['words']); r['score']=0; r['attribution']='Original controlled learner sentence — UALIS Publishing v1.0.'
    payload='\n'.join(f"{r['target']}\t{r['english']}" for r in rows).encode('utf-8')
    qn=sum('?' in r['english'] for r in rows)
    QUALITY_META['urdu']={'source_type':'Original controlled standard-Urdu conversation corpus','candidate_count':1000,'target_unique':1000,'english_unique':1000,'question_count':qn,'question_share':round(qn/1000,3),'top_contributor':'UALIS Publishing controlled patterns','top_contributor_rows':1000,'top_contributor_share':1.0,'band_counts':dict(Counter(r['level'] for r in rows)),'family_counts':dict(Counter(r['family'] for r in rows))}
    return rows,1000,hashlib.sha256(payload).hexdigest()


def quality_parse_sentences(cfg):
    return controlled_urdu() if cfg['name']=='Urdu' else select_external(cfg)


def quality_cover(cfg, segment: str):
    rtl='rtl' if cfg['dir']=='rtl' else ''
    return f'''<section class="cover"><div class="kicker">Version 1.0 - production candidate</div><h1>{base.esc(cfg['name'])} Workbook</h1><div class="target {rtl}" style="--target-font:'{cfg['font']}'">{base.esc(cfg['target'])}</div><p class="subtitle">Writing foundations, core grammar, 1,000 audited vocabulary entries, and 1,000 curated bilingual practice sentences with handwriting and retrieval space.</p><div class="claim"><strong>{base.esc(segment)}</strong><br>Natural, idiomatic learner language takes priority over artificial uniqueness. Genuine homographs are retained when their learner meaning and grammatical role differ. Transliteration is intentionally omitted from sentence drills rather than teaching inconsistent ad-hoc romanization.</div></section>'''


def quality_sources_html():
    return '''<section class="section-start license"><h2>Sources, licensing, and QA scope</h2><p><strong>Vocabulary:</strong> drawn from this repository's canonical audited top-1,000 deck for the language. Repository source and audit records remain the source of truth.</p><p><strong>Arabic and French sentences:</strong> quality-filtered from the ManyThings bilingual exports of the Tatoeba Project, with supplied sentence-level attribution retained under CC BY 2.0 France.</p><p><strong>Urdu sentences:</strong> original controlled standard-Urdu learner sentences authored for this workbook from reviewed grammar-safe conversation families. They replace a rejected external candidate corpus that failed the release linguistic audit.</p><p><strong>Quality scope:</strong> release gates check canonical dataset integrity, row counts, duplicate handling, script plausibility, sentence-type balance, source diversity where applicable, blocked Urdu legacy-error patterns, PDF structure, font embedding, and renderability. These checks materially reduce risk but do not substitute for independent native-speaker editorial certification; no absolute error-free claim is made.</p></section>'''


def post_process():
    out,audit=base.OUT,base.AUDIT
    summary={}
    for lang in ('arabic','french','urdu'):
        p=audit/f'{lang}_qa.json'; q=json.loads(p.read_text(encoding='utf-8')); m=QUALITY_META[lang]
        q['sentence_source_type']=m['source_type']; q['sentence_question_share']=m['question_share']; q['sentence_top_contributor']=m['top_contributor']; q['sentence_top_contributor_share']=m['top_contributor_share']; q['sentence_band_counts']=m['band_counts']
        if lang=='urdu':
            q['sentence_original_controlled_rows']=1000; q['sentence_attribution_rows']=0
            gate=(q['sentence_rows']==1000 and q['sentence_target_unique']==1000 and q['sentence_english_unique']==1000 and 0.25<=m['question_share']<=0.45)
        else:
            gate=(q['sentence_rows']==1000 and q['sentence_target_unique']==1000 and q['sentence_english_unique']==1000 and 0.25<=m['question_share']<=0.35 and m['top_contributor_share']<=0.24 and q['sentence_attribution_rows']==1000)
        q['corpus_quality_gate']='PASS' if gate else 'FAIL'
        if not gate: raise SystemExit(f'{lang}: corpus quality gate failed: {q}')
        p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); summary[lang]=q
    (audit/'corpus_quality_v2.json').write_text(json.dumps(QUALITY_META,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); (audit/'qa_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report=['# Language Workbooks v1.0 - automated QA','','Production-candidate gates passed. Natural language quality takes priority over artificial uniqueness. Independent native-speaker editorial certification remains the final step before any absolute error-free commercial claim.','']
    for lang,q in summary.items(): report += [f'## {lang.title()}',f"- Vocabulary: {q['vocabulary_rows']} audited entries; {q['vocabulary_unique_surface_forms']} normalized surface forms.",f"- Sentences: {q['sentence_rows']} rows; {q['sentence_target_unique']} unique target strings; {q['sentence_english_unique']} unique English strings.",f"- Question share: {q['sentence_question_share']:.1%}.",f"- Source type: {q['sentence_source_type']}.",f"- Corpus quality gate: {q['corpus_quality_gate']}.",f"- PDFs: {len(q['pdfs'])} (1 master + 13 tablet segments).",'']
    (audit/'QA_REPORT.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    readme="""# Language Workbooks v1.0\n\nProduction-candidate workbooks for Arabic, French, and Urdu. Each language includes one complete master PDF, 13 tablet-friendly split PDFs, a 1,000-entry vocabulary companion CSV, and a 1,000-sentence companion CSV.\n\nVocabulary comes from the repository's audited top-1,000 learner decks. Arabic and French practice sentences are source-diverse, English-unique selections from the ManyThings/Tatoeba bilingual exports and retain sentence-level CC BY 2.0 France attribution. Urdu uses an original controlled standard-Urdu conversation corpus after the initial external candidate corpus was rejected during linguistic QA.\n\nThe release favors natural, idiomatic language over artificial uniqueness. Genuine homographs are permitted when meaning and grammatical role genuinely differ. Transliteration is omitted from the sentence drill corpus rather than introducing inconsistent ad-hoc romanization.\n\nAutomated source, diversity, duplicate, script, corpus-balance, PDF, font, and render checks support the release. Independent native-speaker editorial certification remains the final step before making an absolute error-free commercial claim.\n"""
    (out/'README.md').write_text(readme,encoding='utf-8')
    manifest=json.loads((out/'RELEASE_MANIFEST.json').read_text(encoding='utf-8')); manifest['corpus_quality']='v2_balanced_external_ar_fr_controlled_original_ur'; manifest['status']='production_candidate'; (out/'RELEASE_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    base.parse_sentences=quality_parse_sentences; base.cover=quality_cover; base.sources_html=quality_sources_html; base.LANGS['urdu']['zip']='internal://ualis/urdu-controlled-conversation-v1'; base.main(); post_process()

if __name__=='__main__': main()
