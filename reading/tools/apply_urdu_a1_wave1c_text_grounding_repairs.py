import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading" / "urdu" / "a1" / "passages.jsonl"
REPORT = ROOT / "reading" / "audit" / "urdu_a1_wave1c_text_grounding_repairs_2026-08-23.json"
EXPECTED_GIT_BLOB = "dd7a909d6f2204d46a2e132fb09c2d410eea2090"
DATE = "2026-08-23"


def git_blob_sha(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def token_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def exact_count(text: str, form: str) -> int:
    return text.casefold().count(form.casefold())


def split_key(answer: str):
    return [part.strip() for part in answer.split("؛")]


def reconstruct(prompt: str, answer: str) -> str:
    out = prompt
    for part in split_key(answer):
        if "_____" not in out:
            raise AssertionError(f"Too many answer parts: {prompt!r} / {answer!r}")
        out = out.replace("_____", part, 1)
    if "_____" in out:
        raise AssertionError(f"Too few answer parts: {prompt!r} / {answer!r}")
    return out


actual = git_blob_sha(PATH)
if actual != EXPECTED_GIT_BLOB:
    raise SystemExit(f"Refusing Wave 1C: expected {EXPECTED_GIT_BLOB}, found {actual}")

raw_lines = PATH.read_text(encoding="utf-8").splitlines()
rows = [json.loads(x) for x in raw_lines if x]
if len(rows) != 60 or [r["sequence"] for r in rows] != list(range(1, 61)):
    raise SystemExit("Unexpected Urdu A1 frontier")
by_id = {r["id"]: r for r in rows}
changed = set()
operations = []
exposure_deltas = []
review_occurrence_deltas = []


def q(row_id, qid):
    return next(x for x in by_id[row_id]["questions"] if x["id"] == qid)


def a(row_id, aid):
    return next(x for x in by_id[row_id]["answer_key"] if x["id"] == aid)


def set_text(row_id, old, new, finding_ids):
    row = by_id[row_id]
    if row["text"] != old:
        raise AssertionError(f"{row_id} text drift")
    before_counts = {t["id"]: exact_count(old, str(t.get("form", ""))) for t in row.get("new_lexical_targets", [])}
    before_reviews = {t["id"]: exact_count(old, str(t.get("form", ""))) for t in row.get("review_lexical_targets", [])}
    row["text"] = new
    row["word_count"] = token_count(new)
    for target in row.get("new_lexical_targets", []):
        old_meta = target.get("exposures_in_text")
        new_count = exact_count(new, str(target.get("form", "")))
        target["exposures_in_text"] = new_count
        exposure_deltas.append({
            "passage_id": row_id,
            "target_id": target["id"],
            "form": target.get("form"),
            "before_text_count": before_counts[target["id"]],
            "before_metadata_count": old_meta,
            "after_text_count": new_count,
            "after_metadata_count": target["exposures_in_text"],
        })
    for target in row.get("review_lexical_targets", []):
        new_count = exact_count(new, str(target.get("form", "")))
        if new_count != before_reviews[target["id"]]:
            review_occurrence_deltas.append({
                "passage_id": row_id,
                "target_id": target["id"],
                "form": target.get("form"),
                "before_text_count": before_reviews[target["id"]],
                "after_text_count": new_count,
            })
    changed.add(row_id)
    operations.append({
        "passage_id": row_id,
        "kind": "text",
        "finding_ids": finding_ids,
        "before": old,
        "after": new,
        "word_count_after": row["word_count"],
    })


def set_question(row_id, qid, old_prompt, new_prompt, new_type=None, finding_ids=None):
    item = q(row_id, qid)
    if item["prompt"] != old_prompt:
        raise AssertionError(f"{row_id}/{qid} prompt drift: {item['prompt']!r}")
    before = dict(item)
    item["prompt"] = new_prompt
    if new_type is not None:
        item["type"] = new_type
    changed.add(row_id)
    operations.append({"passage_id": row_id, "kind": "question", "item": qid, "finding_ids": finding_ids or [], "before": before, "after": dict(item)})


def set_answer(row_id, aid, old_answer, new_answer, finding_ids=None):
    item = a(row_id, aid)
    if item["answer"] != old_answer:
        raise AssertionError(f"{row_id}/{aid} answer drift: {item['answer']!r}")
    before = dict(item)
    item["answer"] = new_answer
    changed.add(row_id)
    operations.append({"passage_id": row_id, "kind": "answer", "item": aid, "finding_ids": finding_ids or [], "before": before, "after": dict(item)})


# U1 P01: remove the ambiguous feminine pronoun in the source and make the associated item unambiguous.
set_text(
    "ur-a1-u01-p01",
    "عائشہ اپنی خالہ کے ساتھ ایک نئے گھر میں آئی۔ دروازہ کھلا تو سامنے ایک چھوٹا سا کمرہ تھا۔ کمرے میں میز، کرسی اور کھڑکی تھی۔ عائشہ نے میز پر ہاتھ رکھا اور کہا، “یہ میری پڑھنے کی جگہ ہے۔” خالہ اس کے ساتھ دوسرے کمرے میں گئیں، جہاں کتابوں کے لیے ایک الماری تھی۔ عائشہ نے دو کتابیں الماری میں رکھیں اور باقی کتابیں میز پر چھوڑ دیں۔ پھر وہ کھڑکی کے پاس کھڑی ہوئی۔ باہر ایک درخت اور چھوٹی سی گلی نظر آ رہی تھی۔ خالہ نے پوچھا کہ کیا وہ بازار چلنا چاہتی ہے۔ عائشہ نے کہا کہ وہ ان کے ساتھ جائے گی۔ دونوں نے دروازہ بند کیا اور گھر سے نکل گئیں۔",
    "عائشہ اپنی خالہ کے ساتھ ایک نئے گھر میں آئی۔ دروازہ کھلا تو سامنے ایک چھوٹا سا کمرہ تھا۔ کمرے میں میز، کرسی اور کھڑکی تھی۔ عائشہ نے میز پر ہاتھ رکھا اور کہا، “یہ میری پڑھنے کی جگہ ہے۔” خالہ اس کے ساتھ دوسرے کمرے میں گئیں، جہاں کتابوں کے لیے ایک الماری تھی۔ عائشہ نے دو کتابیں الماری میں رکھیں اور باقی کتابیں میز پر چھوڑ دیں۔ پھر وہ کھڑکی کے پاس کھڑی ہوئی۔ باہر ایک درخت اور چھوٹی سی گلی نظر آ رہی تھی۔ خالہ نے عائشہ سے پوچھا، “کیا تم بازار چلنا چاہتی ہو؟” عائشہ نے کہا کہ وہ ان کے ساتھ جائے گی۔ دونوں نے دروازہ بند کیا اور گھر سے نکل گئیں۔",
    ["U1P01-01"],
)
set_question("ur-a1-u01-p01", "q8", "«خالہ نے پوچھا کہ کیا وہ بازار چلنا چاہتی ہے» میں «وہ» کس کے لیے ہے؟", "خالہ نے بازار چلنے کے بارے میں کس سے پوچھا؟", "literal_detail", ["U1P01-01"])
set_answer("ur-a1-u01-p01", "a8", "عائشہ کے لیے۔", "عائشہ سے۔", ["U1P01-01"])

# U3 checkpoint: restore source-grounded reasons/actions instead of invented checkpoint details.
set_text(
    "ur-a1-u03-p06",
    "عائشہ کے ہفتے میں کھانے اور خریداری کے کئی چھوٹے کام ہوتے ہیں۔ کبھی وہ ناشتہ کرتے وقت پانی چنتی ہے کیونکہ اسے ہلکا مشروب چاہیے ہوتا ہے۔ گھر میں چیز کم ہو تو وہ خالہ کے ساتھ فہرست بناتی ہے اور ضرورت کی چند چیزیں خریدتی ہے۔ بازار میں مختلف دکانیں ہوں تو وہ پہلے دیکھتی ہے کہ یہاں کیا موجود ہے۔ کھانا بنانے کے وقت وہ پوچھتی ہے کہ کیا ابھی کچھ تیار ہے یا اسے انتظار کرنا ہے۔ عائشہ اپنا کام خود کرنے کی کوشش بھی کرتی ہے، کیونکہ وقت اور صفائی دونوں اہم ہیں۔ اس طرح وہ کھانے، خریداری اور گھر کے کام کو آسان ترتیب میں رکھتی ہے اور دوسروں کی مدد بھی کرتی ہے۔",
    "عائشہ کے ہفتے میں کھانے اور خریداری کے کئی چھوٹے کام ہوتے ہیں۔ کبھی وہ ناشتہ کرتے وقت پانی چنتی ہے کیونکہ وہ اسکول کے بعد کھیلنے جائے گی۔ گھر میں چیز کم ہو تو وہ خالہ کے ساتھ فہرست بناتی ہے اور ضرورت کی چند چیزیں خریدتی ہے۔ بازار میں مختلف دکانیں ہوں تو وہ پہلے دیکھتی ہے کہ یہاں کیا موجود ہے۔ کھانا بناتے وقت چاول تیار ہو جائیں اور سبزی ابھی پک رہی ہو تو وہ چند منٹ انتظار کرتی ہے۔ عائشہ اپنا کام خود کرنے کی کوشش بھی کرتی ہے، کیونکہ وقت اور صفائی دونوں اہم ہیں۔ اس طرح وہ کھانے، خریداری اور گھر کے کام کو آسان ترتیب میں رکھتی ہے اور دوسروں کی مدد بھی کرتی ہے۔",
    ["U3P06-01", "U3P06-02"],
)
set_answer("ur-a1-u03-p06", "a2", "کیونکہ اسے ہلکا مشروب چاہیے ہوتا ہے۔", "کیونکہ وہ اسکول کے بعد کھیلنے جائے گی۔", ["U3P06-01"])
set_question("ur-a1-u03-p06", "q5", "کھانا بناتے وقت عائشہ کیا پوچھتی ہے؟", "چاول تیار ہونے کے بعد بھی عائشہ کیوں انتظار کرتی ہے؟", "cause_effect", ["U3P06-02"])
set_answer("ur-a1-u03-p06", "a5", "وہ پوچھتی ہے کہ کیا ابھی کچھ تیار ہے یا انتظار کرنا ہے۔", "کیونکہ سبزی ابھی پک رہی ہوتی ہے۔", ["U3P06-02"])

# U5 P01: correct recipient case marker.
set_text(
    "ur-a1-u05-p01",
    "پیر کی صبح عائشہ کلاس میں جلد پہنچتی ہے۔ استاد تختے پر دن کا پہلا سوال لکھتے ہیں۔ سوال آسان ہے اور آج کی تاریخ کے بارے میں ہے۔ عائشہ جواب جانتی ہے، مگر پہلے دوسرے بچوں کو سوچنے دیتی ہے۔ ایک نیا شخص کلاس کے دروازے پر آتا ہے اور استاد سے اپنا نام بتاتا ہے۔ پھر استاد سوال دوبارہ پڑھتے ہیں۔ مریم ہاتھ اٹھاتی ہے اور درست جواب دیتی ہے۔ استاد کہتے ہیں کہ اچھا جواب مختصر اور واضح ہوتا ہے۔ اس کے بعد عائشہ بھی ایک سوال پوچھتی ہے اور جاننا چاہتی ہے کہ آج کون سی کتاب پڑھنی ہے۔ استاد جواب دیتے ہیں کہ آج ایک مختصر کہانی پڑھیں گے۔ سب بچے کتابیں کھولتے ہیں اور سبق شروع ہوتا ہے۔",
    "پیر کی صبح عائشہ کلاس میں جلد پہنچتی ہے۔ استاد تختے پر دن کا پہلا سوال لکھتے ہیں۔ سوال آسان ہے اور آج کی تاریخ کے بارے میں ہے۔ عائشہ جواب جانتی ہے، مگر پہلے دوسرے بچوں کو سوچنے دیتی ہے۔ ایک نیا شخص کلاس کے دروازے پر آتا ہے اور استاد کو اپنا نام بتاتا ہے۔ پھر استاد سوال دوبارہ پڑھتے ہیں۔ مریم ہاتھ اٹھاتی ہے اور درست جواب دیتی ہے۔ استاد کہتے ہیں کہ اچھا جواب مختصر اور واضح ہوتا ہے۔ اس کے بعد عائشہ بھی ایک سوال پوچھتی ہے اور جاننا چاہتی ہے کہ آج کون سی کتاب پڑھنی ہے۔ استاد جواب دیتے ہیں کہ آج ایک مختصر کہانی پڑھیں گے۔ سب بچے کتابیں کھولتے ہیں اور سبق شروع ہوتا ہے۔",
    ["U5P01-01"],
)

# U5 checkpoint: restore the actual P03 movement sequence.
set_text(
    "ur-a1-u05-p06",
    "عائشہ اب اسکول کے دن کو آسان ترتیب میں سمجھتی ہے۔ کلاس میں استاد سوال پوچھتے ہیں اور بچے جواب دیتے ہیں۔ پڑھنے کے وقت عائشہ کتاب کھولتی ہے اور اہم بات یاد رکھنے کی کوشش کرتی ہے۔ وقفے میں کبھی اسے کلاس کے اندر جانا پڑتا ہے، اور مریم دروازے کے قریب اس کا انتظار کرتی ہے۔ کوئی کام مشکل ہو تو عائشہ پہلے دیکھتی ہے کہ اسے چھوٹے حصوں میں کرنا ممکن ہے یا نہیں۔ آخری سبق میں وہ اپنی کاپی دیکھتی ہے اور چیزیں بستے میں واپس رکھتی ہے۔ اس طرح سوال، جواب، کتاب، یاد، اندر، قریب، مشکل، ممکن، آخری اور واپس جیسے الفاظ اس کے عام اسکول کے دن سے جڑ جاتے ہیں۔",
    "عائشہ اب اسکول کے دن کو آسان ترتیب میں سمجھتی ہے۔ کلاس میں استاد سوال پوچھتے ہیں اور بچے جواب دیتے ہیں۔ پڑھنے کے وقت عائشہ کتاب کھولتی ہے اور اہم بات یاد رکھنے کی کوشش کرتی ہے۔ وقفے میں عائشہ اور مریم کلاس کے اندر جاتی ہیں، پھر گھنٹی بجے تو دونوں دروازے کے قریب آتی ہیں۔ کوئی کام مشکل ہو تو عائشہ پہلے دیکھتی ہے کہ اسے چھوٹے حصوں میں کرنا ممکن ہے یا نہیں۔ آخری سبق میں وہ اپنی کاپی دیکھتی ہے اور چیزیں بستے میں واپس رکھتی ہے۔ اس طرح سوال، جواب، کتاب، یاد، اندر، قریب، مشکل، ممکن، آخری اور واپس جیسے الفاظ اس کے عام اسکول کے دن سے جڑ جاتے ہیں۔",
    ["U5P06-02"],
)
set_question("ur-a1-u05-p06", "q4", "عائشہ اندر جائے تو مریم کہاں انتظار کرتی ہے؟", "وقفے میں عائشہ اور مریم پہلے کہاں جاتی ہیں، اور پھر کہاں آتی ہیں؟", "sequence", ["U5P06-02"])
set_answer("ur-a1-u05-p06", "a4", "مریم دروازے کے قریب انتظار کرتی ہے۔", "وہ پہلے کلاس کے اندر جاتی ہیں، پھر دروازے کے قریب آتی ہیں۔", ["U5P06-02"])

# U8 checkpoint: fix the missing object marker in learner-facing source/answer.
set_text(
    "ur-a1-u08-p06",
    "جمعہ کی شام عائشہ اپنے خاندان کے ساتھ ہفتے کے کام یاد کرتی ہے۔ والدین پوچھتے ہیں کہ اسے کون سا کام سب سے اچھا لگا۔ عائشہ کہتی ہے کہ خالہ سے گفتگو اچھی تھی کیونکہ ان کی آواز سن کر خوشی ہوئی۔ وہ مریم کا خط بھی دکھاتی ہے اور بتاتی ہے کہ جواب لکھتے وقت اسے دوسرا قلم لینا پڑا۔ پھر وہ بجلی جانے والی شام کا ذکر کرتی ہے، جب ہر چیز اپنی جگہ رکھنا ضروری تھا۔ ماں میز کی طرف دیکھتی ہیں اور کہتی ہیں کہ پورا کام اچھا ہوا، لیکن باقی کاغذ کل بھی دیکھنے ہیں۔ سب ہنستے ہیں اور عائشہ کہتی ہے کہ اگلے ہفتے بھی گھر کے چھوٹے کام مل کر کریں گے۔",
    "جمعہ کی شام عائشہ اپنے خاندان کے ساتھ ہفتے کے کام یاد کرتی ہے۔ والدین پوچھتے ہیں کہ اسے کون سا کام سب سے اچھا لگا۔ عائشہ کہتی ہے کہ خالہ سے گفتگو اچھی تھی کیونکہ ان کی آواز سن کر خوشی ہوئی۔ وہ مریم کا خط بھی دکھاتی ہے اور بتاتی ہے کہ جواب لکھتے وقت اسے دوسرا قلم لینا پڑا۔ پھر وہ بجلی جانے والی شام کا ذکر کرتی ہے، جب ہر چیز کو اپنی جگہ رکھنا ضروری تھا۔ ماں میز کی طرف دیکھتی ہیں اور کہتی ہیں کہ پورا کام اچھا ہوا، لیکن باقی کاغذ کل بھی دیکھنے ہیں۔ سب ہنستے ہیں اور عائشہ کہتی ہے کہ اگلے ہفتے بھی گھر کے چھوٹے کام مل کر کریں گے۔",
    ["U8P06-02"],
)
set_answer("ur-a1-u08-p06", "a6", "بجلی چلی گئی تھی اور ہر چیز اپنی جگہ رکھنا ضروری تھا۔", "بجلی چلی گئی تھی اور ہر چیز کو اپنی جگہ رکھنا ضروری تھا۔", ["U8P06-02"])

# U9/U10: correct the oblique form of دورہ before postpositions/possessive phrases.
set_text(
    "ur-a1-u09-p01",
    "جمعہ کو عائشہ اپنے والدین کے ساتھ خالہ کے گھر ایک مختصر دورہ کرتی ہے۔ یہ دورہ کئی ہفتوں بعد ہو رہا ہے، اس لیے خاندان کے سب لوگ خوش ہیں۔ عائشہ ایک چھوٹا تحفہ ساتھ لاتی ہے اور کہتی ہے کہ اسے خالہ کو دینا ہے۔ خالہ دروازہ کھولتی ہیں تو عائشہ تحفہ دینا چاہتی ہے، مگر پہلے سب کو سلام کرتی ہے۔ بیٹھنے کے بعد خالہ بچوں کو جوس دینا چاہتی ہیں۔ عائشہ کہتی ہے کہ پہلے چھوٹے بچے کو دینا بہتر ہے۔ دورہ کے دوران سب گھر اور اسکول کی باتیں کرتے ہیں۔ واپسی سے پہلے عائشہ اگلے دورہ کا دن پوچھتی ہے۔ اسے اچھا لگتا ہے کہ کسی کو چیز دینا اور وقت دینا دونوں محبت دکھاتے ہیں۔",
    "جمعہ کو عائشہ اپنے والدین کے ساتھ خالہ کے گھر ایک مختصر دورہ کرتی ہے۔ یہ دورہ کئی ہفتوں بعد ہو رہا ہے، اس لیے خاندان کے سب لوگ خوش ہیں۔ عائشہ ایک چھوٹا تحفہ ساتھ لاتی ہے اور کہتی ہے کہ اسے خالہ کو دینا ہے۔ خالہ دروازہ کھولتی ہیں تو عائشہ تحفہ دینا چاہتی ہے، مگر پہلے سب کو سلام کرتی ہے۔ بیٹھنے کے بعد خالہ بچوں کو جوس دینا چاہتی ہیں۔ عائشہ کہتی ہے کہ پہلے چھوٹے بچے کو دینا بہتر ہے۔ دورے کے دوران سب گھر اور اسکول کی باتیں کرتے ہیں۔ واپسی سے پہلے عائشہ اگلے دورے کا دن پوچھتی ہے۔ اسے اچھا لگتا ہے کہ کسی کو چیز دینا اور وقت دینا دونوں محبت دکھاتے ہیں۔",
    ["U9P01-01"],
)
set_question("ur-a1-u09-p01", "q1", "اس دورہ میں عائشہ کہاں جاتی ہے؟", "اس دورے میں عائشہ کہاں جاتی ہے؟", None, ["U9P01-01"])

set_text(
    "ur-a1-u09-p06",
    "اس ہفتے عائشہ نے کئی عملی کام کیے۔ خاندان کے دورہ میں اس نے تحفہ دینا اور دوسروں کو وقت دینا سیکھا۔ بینک میں اس نے رقم کی مقدار دیکھی اور سمجھا کہ بینک کے کاغذ صاف رکھنا کیوں ضروری ہے۔ مریم سے گفتگو میں اس نے ہاں اور بالکل کہہ کر منصوبے کی تصدیق کی۔ اسکول کے کام میں محنت کے بعد اس نے دیکھا کہ تھوڑی دیر آرام کرنے سے طاقت واپس آ سکتی ہے۔ گھر میں اس نے پنکھے کی حالت دیکھی اور مرمت کا فائدہ سمجھا۔ عائشہ کو اب معلوم ہے کہ روزمرہ کے کام مختلف ہوتے ہیں، مگر ہر کام میں سوال پوچھنا، صحیح مقدار دیکھنا، مناسب جواب دینا، محنت کرنا اور چیز کی حالت سمجھنا مدد دیتا ہے۔ اگلے ہفتے وہ انہی طریقوں کو دوسرے کاموں میں بھی استعمال کرنا چاہتی ہے۔",
    "اس ہفتے عائشہ نے کئی عملی کام کیے۔ خاندان کے دورے میں اس نے تحفہ دینا اور دوسروں کو وقت دینا سیکھا۔ بینک میں اس نے رقم کی مقدار دیکھی اور سمجھا کہ بینک کے کاغذ صاف رکھنا کیوں ضروری ہے۔ مریم سے گفتگو میں اس نے ہاں اور بالکل کہہ کر منصوبے کی تصدیق کی۔ اسکول کے کام میں محنت کے بعد اس نے دیکھا کہ تھوڑی دیر آرام کرنے سے طاقت واپس آ سکتی ہے۔ گھر میں اس نے پنکھے کی حالت دیکھی اور مرمت کا فائدہ سمجھا۔ عائشہ کو اب معلوم ہے کہ روزمرہ کے کام مختلف ہوتے ہیں، مگر ہر کام میں سوال پوچھنا، صحیح مقدار دیکھنا، مناسب جواب دینا، محنت کرنا اور چیز کی حالت سمجھنا مدد دیتا ہے۔ اگلے ہفتے وہ انہی طریقوں کو دوسرے کاموں میں بھی استعمال کرنا چاہتی ہے۔",
    ["U9P06-01"],
)
set_question("ur-a1-u09-p06", "q2", "خاندان کے دورہ میں عائشہ نے کیا سیکھا؟", "خاندان کے دورے میں عائشہ نے کیا سیکھا؟", None, ["U9P06-01"])

set_text(
    "ur-a1-u10-p01",
    "اتوار کی صبح عائشہ اپنے والدین کے ساتھ محلے کے باغ میں جاتی ہے۔ باغ گھر سے زیادہ دور نہیں، اس لیے وہ پیدل جاتے ہیں۔ دروازے کے پاس کئی پھول ہیں اور ہر پھول کا رنگ الگ ہے۔ عائشہ سرخ رنگ کے پھول دیکھتی ہے، پھر پیلے رنگ کی قطار کے پاس رکتی ہے۔ والد کہتے ہیں کہ پچھلے دورہ میں یہاں کم پودے تھے۔ آج باغ زیادہ بھرا ہوا لگتا ہے۔ عائشہ ایک بینچ پر بیٹھ کر پانی پیتی ہے اور چھوٹے بھائی کو بوتل دینا چاہتی ہے۔ واپسی سے پہلے وہ باغ کا ایک اور چکر لگاتی ہے۔ اسے اچھا لگتا ہے کہ موسم کے ساتھ باغ اور رنگ دونوں بدلتے رہتے ہیں۔",
    "اتوار کی صبح عائشہ اپنے والدین کے ساتھ محلے کے باغ میں جاتی ہے۔ باغ گھر سے زیادہ دور نہیں، اس لیے وہ پیدل جاتے ہیں۔ دروازے کے پاس کئی پھول ہیں اور ہر پھول کا رنگ الگ ہے۔ عائشہ سرخ رنگ کے پھول دیکھتی ہے، پھر پیلے رنگ کی قطار کے پاس رکتی ہے۔ والد کہتے ہیں کہ پچھلے دورے میں یہاں کم پودے تھے۔ آج باغ زیادہ بھرا ہوا لگتا ہے۔ عائشہ ایک بینچ پر بیٹھ کر پانی پیتی ہے اور چھوٹے بھائی کو بوتل دینا چاہتی ہے۔ واپسی سے پہلے وہ باغ کا ایک اور چکر لگاتی ہے۔ اسے اچھا لگتا ہے کہ موسم کے ساتھ باغ اور رنگ دونوں بدلتے رہتے ہیں۔",
    ["U10P01-01"],
)
set_question("ur-a1-u10-p01", "q8", "والد پچھلے دورہ کے بارے میں کیا کہتے ہیں؟", "والد پچھلے دورے کے بارے میں کیا کہتے ہیں؟", None, ["U10P01-01"])
set_answer("ur-a1-u10-p01", "a8", "پچھلے دورہ میں پودے کم تھے۔", "پچھلے دورے میں پودے کم تھے۔", ["U10P01-01"])

# Invalidate all affected gates because passage text changed; no promotion.
for row_id in sorted(changed):
    row = by_id[row_id]
    row["revision"] = int(row.get("revision", 0)) + 1
    quality = row.setdefault("quality", {})
    for key in ("coverage_check", "answer_key_check", "linguistic_review", "pedagogical_review", "schema_check"):
        quality[key] = "pending"
    quality["status"] = "draft"
    note = "Wave 1C objective text/grounding repair applied 2026-08-23; full gate revalidation pending."
    notes = quality.setdefault("notes", [])
    if note not in notes:
        notes.append(note)

# Validate Q/A links and all 130 clozes after text/Q/A edits.
clozes = []
for row in rows:
    answers_by_id = {x["id"]: x for x in row["answer_key"]}
    answers_by_q = {x["question_id"]: x for x in row["answer_key"]}
    if len(answers_by_id) != len(row["answer_key"]):
        raise AssertionError(f"Duplicate answer IDs in {row['id']}")
    for item in row["questions"]:
        linked = answers_by_id.get(item["answer_id"])
        if linked is None or linked.get("question_id") != item["id"]:
            raise AssertionError(f"Q/A linkage failure {row['id']}/{item['id']}")
        if item.get("type") == "cloze_transfer":
            keyed = answers_by_q[item["id"]]["answer"]
            clozes.append({"passage_id": row["id"], "question_id": item["id"], "reconstructed": reconstruct(item["prompt"], keyed)})
if len(clozes) != 130:
    raise AssertionError(f"Expected 130 clozes, found {len(clozes)}")

# Preserve untouched lines exactly.
out_lines = []
for original, row in zip(raw_lines, rows):
    out_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")) if row["id"] in changed else original)
PATH.write_text("\n".join(out_lines) + "\n", encoding="utf-8")

REPORT.write_text(json.dumps({
    "schema_version": 1,
    "date": DATE,
    "language": "urdu",
    "level": "A1",
    "input_git_blob_sha": EXPECTED_GIT_BLOB,
    "changed_passage_ids": sorted(changed),
    "changed_passage_count": len(changed),
    "operations": operations,
    "new_target_exposure_deltas": exposure_deltas,
    "review_target_text_occurrence_deltas": review_occurrence_deltas,
    "cloze_question_count": len(clozes),
    "all_cloze_structures_reconstructed": True,
    "quality_promotion": False,
    "notes": [
        "Exact-form exposure counts are recalculated for all new lexical targets in changed passages.",
        "Review-target text occurrence deltas are reported but review metadata has no exposures_in_text field to mutate.",
        "Correct Urdu morphology/grounding takes precedence over preserving an incorrect exact-form exposure; any resulting coverage shortfall remains pending for a later bounded repair."
    ]
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"changed": sorted(changed), "clozes": len(clozes), "exposure_deltas": exposure_deltas, "review_deltas": review_occurrence_deltas}, ensure_ascii=False))
