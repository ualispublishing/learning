#!/usr/bin/env python3
import copy
import json
import re
import subprocess
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = {
    "a1": ROOT / "reading" / "arabic" / "a1" / "passages.jsonl",
    "a2": ROOT / "reading" / "arabic" / "a2" / "passages.jsonl",
}
EXPECTED = {
    "a1": "bf7f0a6023b1cb129c9328021892d93cb120fa38",
    "a2": "90b6f2f334b689200c76b25c3b7b983f89230555",
}
REPORT = ROOT / "reading" / "audit" / "arabic_a1_a2_final_semantic_closure_2026-08-23.json"

DIAC = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
WORD = re.compile(r"[\u0621-\u064A]+")
PRO = ("و", "ف", "ب", "ك", "ل")
NSUF = ("هما", "هم", "هن", "كما", "كم", "كن", "نا", "ها", "ه", "ك", "ي", "ات", "ون", "ين", "ان")
VPRE = ("أ", "ا", "ن", "ي", "ت")
VSUF = ("ون", "ين", "ان", "وا", "نا", "تم", "تن", "ن", "ت")


def blob(path):
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def load(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def dump(path, rows):
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n", encoding="utf-8")


def norm(s):
    return DIAC.sub("", unicodedata.normalize("NFKC", str(s or "")).replace("ـ", "")).replace("ٱ", "ا")


def toks(s):
    return WORD.findall(norm(s))


def nominal(tok):
    out = {tok}
    front = {tok}
    for _ in range(2):
        nxt = set()
        for x in front:
            for p in PRO:
                if x.startswith(p) and len(x) > 2:
                    nxt.add(x[1:])
            if x.startswith("ال") and len(x) > 4:
                nxt.add(x[2:])
        out |= nxt
        front = nxt
    exp = set(out)
    for x in list(out):
        for s in NSUF:
            if x.endswith(s) and len(x) - len(s) >= 2:
                exp.add(x[:-len(s)])
        if x.endswith("ا") and len(x) > 3:
            exp.add(x[:-1])
    return exp


def vcores(tok):
    out = set(nominal(tok))
    for x in list(out):
        if len(x) >= 4 and x[0] in VPRE:
            out.add(x[1:])
    for x in list(out):
        for s in VSUF:
            if x.endswith(s) and len(x) - len(s) >= 3:
                out.add(x[:-len(s)])
    return {x for x in out if len(x) >= 2}


def forms(t):
    vals = [t.get("form", "")]
    for p in re.split(r"[/؛;،,]|\bor\b", str(t.get("lemma") or "")):
        if re.search(r"[\u0621-\u064A]", p):
            vals.append(p.strip())
    return list(dict.fromkeys(norm(x) for x in vals if norm(x)))


def supported_count(text, t):
    fs = forms(t)
    isverb = "verb" in str(t.get("part_of_speech") or "").lower()
    n = 0
    for tok in toks(text):
        if tok in fs:
            n += 1
        elif any(nominal(tok) & nominal(f) for f in fs):
            n += 1
        elif isverb and any(vcores(tok) & vcores(f) for f in fs):
            n += 1
    return n


def word_count(text):
    return len(re.findall(r"\S+", str(text)))


def sentence_count(text):
    return sum(str(text).count(x) for x in (".", "؟", "!", "۔"))


def qa(row, qid):
    q = next(x for x in row["questions"] if x.get("id") == qid)
    a = next(x for x in row["answer_key"] if x.get("question_id") == qid)
    return q, a


def replace_once(value, old, new, context):
    count = value.count(old)
    if count != 1:
        raise RuntimeError(f"{context}: expected one occurrence of {old!r}, found {count}")
    return value.replace(old, new, 1)


def edit_text(row, old, new, report, label):
    before = row["text"]
    row["text"] = replace_once(before, old, new, f"{row['id']} text {label}")
    report.append({"passage_id": row["id"], "kind": "text", "label": label, "before": old, "after": new})


def edit_prompt(row, qid, old, new, report, label):
    q, _ = qa(row, qid)
    if q.get("prompt") != old:
        raise RuntimeError(f"{row['id']} {qid} prompt precondition mismatch: {q.get('prompt')!r}")
    q["prompt"] = new
    report.append({"passage_id": row["id"], "question_id": qid, "kind": "prompt", "label": label, "before": old, "after": new})


def edit_answer(row, qid, old, new, report, label):
    _, a = qa(row, qid)
    if a.get("answer") != old:
        raise RuntimeError(f"{row['id']} {qid} answer precondition mismatch: {a.get('answer')!r}")
    a["answer"] = new
    report.append({"passage_id": row["id"], "question_id": qid, "kind": "answer", "label": label, "before": old, "after": new})


def main():
    actual = {level: blob(path) for level, path in FILES.items()}
    if actual != EXPECTED:
        raise SystemExit(f"Unexpected input blobs: {actual}")

    rows = {level: load(path) for level, path in FILES.items()}
    idx = {level: {r["id"]: r for r in rs} for level, rs in rows.items()}
    original = {level: {r["id"]: copy.deepcopy(r) for r in rs} for level, rs in rows.items()}
    repairs = []

    # A1: timeline, naturalness, grounding, definitions, scene coherence, checkpoint de-metalinguistic polish.
    r = idx["a1"]["ar-a1-u01-p02"]
    edit_text(r, "بعد قليل كانت ليلى في المنزل مرة أخرى.", "بعد انتهاء الدوام عادت ليلى إلى المنزل.", repairs, "repair implausibly fast school-return transition")
    edit_prompt(r, "q3", "ماذا تعني «بعد» في «بعد قليل كانت ليلى في المنزل مرة أخرى»؟", "ماذا تعني «بعد» في «بعد انتهاء الدوام عادت ليلى إلى المنزل»؟", repairs, "align quoted evidence with repaired timeline")

    r = idx["a1"]["ar-a1-u01-p04"]
    edit_text(r, "كان الكتاب مع حقيبتها.", "كان الكتاب في حقيبتها.", repairs, "natural location phrase")

    r = idx["a1"]["ar-a1-u01-p06"]
    edit_text(r, "تضع كتابها هنا، مع حقيبتها.", "تضع كتابها هنا، بجانب حقيبتها.", repairs, "natural book/bag relation")

    r = idx["a1"]["ar-a1-u02-p02"]
    edit_text(r, "عندما تدخل الصف تضع حقيبتها بجانب الكرسي. أول شيء تفعله هو إخراج الدفتر والقلم.", "عندما تدخل الصف تضع حقيبتها بجانب الكرسي. بعد ذلك تُخرج أولًا الدفتر والقلم.", repairs, "remove contradictory first-action claim while preserving target exposure")
    edit_answer(r, "q1", "تضع حقيبتها ثم تخرج الدفتر والقلم.", "تضع حقيبتها بجانب الكرسي.", repairs, "ground first action exactly")

    r = idx["a1"]["ar-a1-u03-p02"]
    edit_prompt(r, "q1", "كم طماطم تحتاج الأم؟", "كم حبة طماطم تحتاج الأم؟", repairs, "natural counted-noun question")

    r = idx["a1"]["ar-a1-u03-p03"]
    edit_answer(r, "q4", "أن الحليب موجود قرب الثلاجة أو في مكانها.", "أن الحليب موجود قرب الثلاجة.", repairs, "remove vague location gloss")

    r = idx["a1"]["ar-a1-u04-p05"]
    edit_answer(r, "q7", "في الجهة المقابلة للمقدمة أو قدام الشيء.", "في الجهة المقابلة للشيء أو الشخص، لا خلفه.", repairs, "correct أمام definition")

    r = idx["a1"]["ar-a1-u05-p02"]
    edit_answer(r, "q5", "تنتظر، ثم تشكر المدير وتعود إلى صفها.", "تقول إنه لا يوجد شيء آخر، ثم تشكر المدير وتعود إلى صفها.", repairs, "remove unsupported waiting action")

    r = idx["a1"]["ar-a1-u07-p02"]
    edit_answer(r, "q4", "أن الجو يظهر أو يُشعر ليلى بأنه أبرد.", "أن الجو يظهر لليلى أبرد مما توقعت.", repairs, "natural يبدو gloss")

    r = idx["a1"]["ar-a1-u08-p04"]
    edit_text(r,
        "تضع الممرضة جهازًا صغيرًا على إصبعها وتشرح أن القلب يعمل طوال الوقت. ثم تطلب من ليلى أن تستمع إلى صوت قلبها بعد حركة قصيرة. تمشي ليلى بسرعة لمدة دقيقة، ثم تجلس.",
        "تضع الممرضة سماعة بسيطة على صدر ليلى وتطلب منها أن تستمع إلى نبض قلبها. ثم تشرح أن القلب يعمل طوال الوقت. بعد ذلك تمشي ليلى بسرعة لمدة دقيقة، ثم تجلس.",
        repairs, "make educational heart-demonstration scene physically coherent")

    r = idx["a1"]["ar-a1-u09-p05"]
    edit_answer(r, "q3", "إدخال الكرة بطريقة تزيد نتيجة الفريق.", "إدخال الكرة في مرمى الفريق الآخر واحتساب ذلك في نتيجة المباراة.", repairs, "precise sports-goal definition")

    r = idx["a1"]["ar-a1-u10-p06"]
    edit_text(r, "في نهاية المستوى المبتدئ الأول تستطيع ليلى أن تقرأ", "بعد هذه المرحلة تستطيع ليلى أن تقرأ", repairs, "remove learner-facing course-level label")
    edit_answer(r, "q1", "ليلى تستطيع الآن قراءة موضوعات يومية كثيرة وفهمها على مستوى المستوى المبتدئ الأول.", "ليلى تستطيع الآن قراءة موضوعات يومية كثيرة وفهمها بوضوح أكبر.", repairs, "remove duplicated course-level metalanguage")

    # A2: natural planning language, learning language, grammar, cultural reference clarity, transport summary, checkpoint de-metalinguistic polish.
    r = idx["a2"]["ar-a2-u02-p05"]
    edit_answer(r, "q4", "ترتيب المواعيد والواجبات بحيث لا تتعارض بلا خطة.", "ترتيب المواعيد والواجبات بحيث لا تتعارض، مع معرفة ما يحتاج إلى تعديل.", repairs, "natural تنظيم gloss")

    r = idx["a2"]["ar-a2-u05-p06"]
    edit_text(r, "وما المشروع الصغير الذي يمكن أن يجبرني على استخدام ما تعلمته؟", "وما المشروع الصغير الذي يمكن أن يدفعني إلى استخدام ما تعلمته؟", repairs, "replace overly forceful learning phrasing")

    r = idx["a2"]["ar-a2-u07-p01"]
    edit_text(r, "لكنني فهمت أن الفعالية يمكن أن تجمع أنشطة وجمهورًا مختلفين في المكان نفسه.", "لكنني فهمت أن الفعالية يمكن أن تجمع أنشطة متعددة وأنواعًا مختلفة من الجمهور في المكان نفسه.", repairs, "repair agreement and coordination")

    r = idx["a2"]["ar-a2-u09-p04"]
    edit_answer(r, "q7", "إلى الطقس أو الفعل المتكرر في احتفالات العائلة، مثل الصورة أو الطبق.", "إلى الفعل المتكرر في احتفالات العائلة، مثل الصورة الجماعية أو طبق معين.", repairs, "remove ambiguous طقس/ritual wording")

    r = idx["a2"]["ar-a2-u09-p05"]
    edit_text(r, "لم تقل نور إن إحداهما «أصح» من الأخرى،", "لم تقل نور إن إحدى الروايتين «أصح» من الأخرى،", repairs, "make comparison refer to accounts rather than people")
    edit_prompt(r, "q6", "إلى ماذا تشير «إحداهما»؟", "إلى ماذا تشير «إحدى الروايتين»؟", repairs, "align reference-resolution question")
    edit_answer(r, "q6", "إلى الجدة والجارة، أو إلى روايتيهما عن المناسبة.", "إلى روايتي الجدة والجارة عن المناسبة.", repairs, "remove ambiguous dual referent")

    r = idx["a2"]["ar-a2-u10-p03"]
    edit_text(r, "ليس دائمًا الاختيار الذي يحل المشكلة أفضل.", "ليس دائمًا الاختيار الذي يحل المشكلة بصورة أفضل.", repairs, "natural comparative phrasing")
    edit_answer(r, "q5", "تقارنان تذكرتين بحسب الثمن ووقت الاتصال، وتقارن هدى الشاحن بحاجتها وتستبدله عندما لا يناسب.", "تقارنان تذكرتين بحسب الثمن ووقت الانتقال، وتقارن هدى الشاحن بحاجتها وتستبدله عندما لا يناسب.", repairs, "use transport-transfer term instead of contact-time")

    r = idx["a2"]["ar-a2-u10-p06"]
    edit_text(r, "بعد إنهاء المستوى المبتدئ الثاني، تستطيع نور متابعة نصوص يومية أطول", "بعد هذه المرحلة، تستطيع نور متابعة نصوص يومية أطول", repairs, "remove learner-facing course-level label")
    edit_answer(r, "q1", "نور أصبحت قادرة على فهم نصوص المستوى المبتدئ الثاني اليومية بربط المعلومات عبر الجمل والمقارنة بين الأسباب والنتائج والمصادر.", "نور أصبحت قادرة على فهم نصوص يومية أطول بربط المعلومات عبر الجمل والمقارنة بين الأسباب والنتائج والمصادر.", repairs, "remove course-level metalanguage from gist key")
    edit_prompt(r, "q5", "لخص أهم مهارات المستوى المبتدئ الثاني المذكورة.", "لخص أهم المهارات المذكورة في النص.", repairs, "remove course-level metalanguage from prompt")

    # Assert all lexical new-target realization counts are unchanged by semantic polish.
    lexical_deltas = []
    changed_passages = sorted({x["passage_id"] for x in repairs})
    for level in ("a1", "a2"):
        for pid in changed_passages:
            if pid not in idx[level]:
                continue
            old = original[level][pid]
            new = idx[level][pid]
            old_by_id = {t.get("id"): t for t in old.get("new_lexical_targets", []) if isinstance(t, dict)}
            for t in new.get("new_lexical_targets", []):
                if not isinstance(t, dict):
                    continue
                tid = t.get("id")
                before_count = supported_count(old.get("text", ""), old_by_id.get(tid, t))
                after_count = supported_count(new.get("text", ""), t)
                if before_count != after_count:
                    lexical_deltas.append({"passage_id": pid, "target_id": tid, "before": before_count, "after": after_count})
    if lexical_deltas:
        raise RuntimeError(f"Semantic closure changed lexical realization counts: {lexical_deltas}")

    # Recount metadata for changed passages, preserve draft/pending status, and record closure provenance.
    for level in ("a1", "a2"):
        for row in rows[level]:
            if row["id"] not in changed_passages:
                continue
            row["word_count"] = word_count(row["text"])
            row["sentence_count"] = sentence_count(row["text"])
            row["revision"] = int(row.get("revision") or 0) + 1
            q = row.setdefault("quality", {})
            q["status"] = "draft"
            for gate in ("answer_key_check", "coverage_check", "linguistic_review", "pedagogical_review", "schema_check"):
                q[gate] = "pending"
            notes = q.setdefault("notes", [])
            note = "Final Arabic A1/A2 semantic/adversarial closure applied 2026-08-23; independent post-closure validation pending."
            if note not in notes:
                notes.append(note)

    for level, path in FILES.items():
        dump(path, rows[level])

    output = {level: blob(path) for level, path in FILES.items()}
    report = {
        "schema_version": 1,
        "date": "2026-08-23",
        "scope": "Arabic A1/A2 final semantic/adversarial closure",
        "input_blobs": actual,
        "output_blobs": output,
        "repair_operation_count": len(repairs),
        "changed_passage_count": len(changed_passages),
        "changed_passages": changed_passages,
        "lexical_realization_deltas": lexical_deltas,
        "repairs": repairs,
        "quality_promotion": False,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "repairs": len(repairs),
        "changed_passages": len(changed_passages),
        "output_blobs": output,
        "lexical_deltas": lexical_deltas,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
