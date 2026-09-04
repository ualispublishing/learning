#!/usr/bin/env python3
"""Apply fresh Arabic Gate B B2 Unit 2 naturalness/Q&A repairs."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
PATH = READING / "arabic/b2/passages.jsonl"
INVENTORY = READING / "audit/arabic_gate_b_naturalness_inventory_2026-08-30.json"
RELEASE = READING / "RELEASE_STATUS.json"
DECISION_DIR = READING / "audit/arabic_gate_b_decisions_2026-08-30"
EXPECTED_IDS = [f"ar-b2-u02-p{i:02d}" for i in range(1, 7)]
TOKEN = re.compile(r"\S+")
NOTE = (
    "2026-09-04 fresh Gate B naturalness review (B2 Unit 2): learner-facing prose/Q/A "
    "reviewed passage by passage; only high-confidence MSA grammar, idiom, reference, semantic, "
    "and assessment-wording repairs applied; no educator/publication release claim."
)

TEXT_REPAIRS = {
    "ar-b2-u02-p03": [
        (
            "والتعامل بنفسه مع سؤال الإرجاع إذا ظهر عيب يختلفان عليه.",
            "والتعامل بنفسه مع مسألة الإرجاع إذا ظهر عيب يختلفان عليه.",
        ),
        (
            "في المقابل، لا يستطيع البائع والمشتري تغيير كل شرط عبر المفاوضة حتى إذا كان التغيير مناسبًا لهما.",
            "في المقابل، لا يستطيع البائع والمشتري تغيير كل شرط عبر المفاوضة حتى إن كان التغيير مناسبًا لهما.",
        ),
    ],
    "ar-b2-u02-p04": [
        (
            "كما فصل جزءًا من المكافأة الجماعية عن الفردية، حتى يملك الموظفون سببًا لمساعدة زميل في حالة معقدة بدل اعتبار الوقت معه خسارة شخصية.",
            "كما جعل جزءًا من المكافأة جماعيًا بدل أن تكون كلها فردية، حتى يملك الموظفون سببًا لمساعدة زميل في حالة معقدة بدل اعتبار الوقت معه خسارة شخصية.",
        ),
    ],
    "ar-b2-u02-p05": [
        (
            "اتفقوا في النهاية على عرض الخطة في جدول يوضح السعر والمدة وتغير وقت الوصول، ثم كتابة حالات يكون فيها كل بديل أقوى.",
            "اتفقوا في النهاية على عرض الخطتين في جدول يوضح السعر والمدة وتغير وقت الوصول، ثم كتابة حالات يكون فيها كل بديل أقوى.",
        ),
    ],
    "ar-b2-u02-p06": [
        (
            "يجب أحيانًا سؤال «ما الحافز والقاعدة والبديل اللذان جعلا هذا السلوك معقولًا؟»",
            "يجب أحيانًا سؤال «ما الحوافز والقواعد والبدائل التي جعلت هذا السلوك معقولًا؟»",
        ),
    ],
}

QA_REPAIRS = {
    "ar-b2-u02-p01": {
        "answers": {
            "q7": (
                "الخدمة تزيد الراحة وتوفر الوقت، والمتجر يتيح فحصًا واختيارًا مباشرًا أكبر.",
                "الخدمة تزيد الراحة وتوفر الوقت، والمتجر يتيح فحص المنتجات مباشرة واختيارًا أوسع.",
            ),
        },
        "questions": {
            "q8": (
                "ما وظيفة «إذا» في اختيار التوصيل مع رسوم مرتفعة عندما قد يفوت الخروج موعدًا أهم؟",
                "ما وظيفة «إذا» في قول النص إنها قد تختار التوصيل إذا كان الخروج سيجعلها تفوت موعدًا أهم؟",
            ),
        },
    },
    "ar-b2-u02-p02": {
        "answers": {
            "q4": (
                "وضع معيار يحدد متى وكيف ينقل الجزء المرن ومراجعة القرار دوريًا.",
                "وضع معيار يحدد متى وكيف يتم نقل الجزء المرن، ومراجعة القرار دوريًا.",
            ),
            "q5": (
                "تحمي حدًا أدنى يمكن التخطيط عليه، وتسمح بتحويل جزء مرن وفق عوامل معلنة، ثم تسجل تكلفة الفرصة وتراجع القاعدة مع تغير الظروف.",
                "تحمي حدًا أدنى يمكن لكل مرفق التخطيط على أساسه، وتسمح بتحويل جزء مرن وفق عوامل معلنة، ثم تسجل تكلفة الفرصة وتراجع القاعدة مع تغير الظروف.",
            ),
            "q9": (
                "لا يتغير أو يحدد مسبقًا على مقدار واحد.",
                "مستقر أو محدد مسبقًا بمقدار واحد.",
            ),
        },
    },
    "ar-b2-u02-p03": {
        "questions": {
            "q6": (
                "ما وظيفة «حتى إذا» في القول إن الطرفين لا يستطيعان تغيير كل شرط ولو كان التغيير مناسبًا لهما؟",
                "ما وظيفة «حتى إن» في القول إن الطرفين لا يستطيعان تغيير كل شرط ولو كان التغيير مناسبًا لهما؟",
            ),
        },
    },
    "ar-b2-u02-p04": {
        "answers": {
            "q1": (
                "تشجع الموظفين على الحالات القصيرة وتؤخر المعقدة رغم ارتفاع عدد الطلبات المنجزة.",
                "تشجع الموظفين على اختيار الحالات القصيرة وتؤخر معالجة الحالات المعقدة رغم ارتفاع عدد الطلبات المنجزة.",
            ),
            "q4": (
                "ينخفض معدل الإنجاز البسيط قليلًا لكن يقل تراكم الحالات الصعبة.",
                "ينخفض معدل إنجاز الطلبات قليلًا، لكن يقل تراكم الحالات الصعبة.",
            ),
            "q7": (
                "الرقم يقيس سرعة العدد، والهدف يشمل معالجة الطلبات كلها بجودة وفي وقت مناسب.",
                "الرقم يقيس سرعة إنجاز الطلبات، والهدف يشمل معالجة الطلبات كلها بجودة وفي وقت مناسب.",
            ),
        },
    },
    "ar-b2-u02-p05": {
        "answers": {
            "q6": (
                "تضع تغير الوزن شرطًا يكشف مدى استقرار التوصية وحساسيتها للأحكام القيمية المستخدمة في الجمع.",
                "تجعل تغير الوزن اختبارًا يكشف مدى استقرار التوصية وحساسيتها للأحكام القيمية المستخدمة في الجمع.",
            ),
        },
        "questions": {
            "q4": (
                "كيف يتغير المنتج النهائي للمجموعة؟",
                "كيف يتغير الناتج النهائي للمجموعة؟",
            ),
        },
    },
    "ar-b2-u02-p06": {
        "answers": {
            "q7": (
                "الظاهرة قد تكون رسمًا أو سعرًا مباشرًا، وتكلفة الفرصة هي البديل الذي لم يعد متاحًا بسبب الاختيار.",
                "التكلفة الظاهرة قد تكون رسمًا أو سعرًا مباشرًا، وتكلفة الفرصة هي البديل الذي لم يعد متاحًا بسبب الاختيار.",
            ),
            "q8": (
                "تقدم شرطًا يبين أن معالجة الفرد لا تكفي عندما يبقى الحافز النظامي الذي يعيد إنتاج السلوك.",
                "تقدم حالة شرطية تبين أن معالجة الفرد لا تكفي عندما يبقى الحافز النظامي الذي يعيد إنتاج السلوك.",
            ),
        },
    },
}

FINDING_META = {
    "ar-b2-u02-p01": [
        (
            "answer q7",
            "naturalness_idiomaticity",
            "minor",
            "فحصًا واختيارًا مباشرًا أكبر is awkward; state that the store permits direct inspection of products and a wider choice.",
        ),
        (
            "question q8",
            "assessment_clarity",
            "moderate",
            "Align the grammar-function question with the actual conditional sentence in the passage; the old wording makes الخروج the agent of an unclear يفوت construction.",
        ),
    ],
    "ar-b2-u02-p02": [
        (
            "answer q4",
            "grammar_wording",
            "moderate",
            "The flexible portion is what gets transferred; use يتم نقل rather than a form that makes it appear to be the agent of ينقل.",
        ),
        (
            "answer q5",
            "naturalness_idiomaticity",
            "minor",
            "يمكن التخطيط عليه is an awkward collocation for a budget floor; state that each facility can plan on the basis of that minimum.",
        ),
        (
            "answer q9",
            "naturalness_idiomaticity",
            "minor",
            "Replace the awkward يحدد مسبقًا على مقدار واحد with a clear definition using مستقر or محدد مسبقًا بمقدار واحد.",
        ),
    ],
    "ar-b2-u02-p03": [
        (
            "text",
            "naturalness_idiomaticity",
            "minor",
            "سؤال الإرجاع is not the idiomatic noun phrase for handling a return issue; use مسألة الإرجاع.",
        ),
        (
            "text + question q6",
            "grammar_wording",
            "moderate",
            "The intended concessive meaning is ‘even if’; use حتى إن rather than حتى إذا and keep the assessment wording aligned with the repaired text.",
        ),
    ],
    "ar-b2-u02-p04": [
        (
            "text",
            "semantic_precision",
            "moderate",
            "فصل جزءًا من المكافأة الجماعية عن الفردية does not express the intended incentive redesign; state that part of the reward was made collective instead of all of it being individual.",
        ),
        (
            "answer q1",
            "naturalness_idiomaticity",
            "minor",
            "تشجع الموظفين على الحالات القصيرة is incomplete; the incentive encourages employees to choose the short cases.",
        ),
        (
            "answer q4",
            "naturalness_idiomaticity",
            "minor",
            "معدل الإنجاز البسيط is unclear; identify the measure as the request-completion rate.",
        ),
        (
            "answer q7",
            "semantic_precision",
            "moderate",
            "سرعة العدد is not a meaningful measure; the metric concerns the speed of completing requests.",
        ),
    ],
    "ar-b2-u02-p05": [
        (
            "text",
            "reference_clarity",
            "moderate",
            "The comparison concerns two plans, so عرض الخطة should be عرض الخطتين.",
        ),
        (
            "answer q6",
            "naturalness_idiomaticity",
            "minor",
            "تضع تغير الوزن شرطًا is awkward; describe changing the weight as a test of recommendation stability and sensitivity.",
        ),
        (
            "question q4",
            "assessment_wording",
            "minor",
            "Use الناتج النهائي for the group's final output rather than المنتج النهائي, which reads as a commercial product in this context.",
        ),
    ],
    "ar-b2-u02-p06": [
        (
            "text",
            "grammar_agreement",
            "major",
            "The coordinated antecedent has three items, but اللذان is dual; recast the list in the plural with التي to restore agreement and clarity.",
        ),
        (
            "answer q7",
            "semantic_precision",
            "major",
            "الظاهرة is a semantic error: the question contrasts visible cost with opportunity cost, so the answer must say التكلفة الظاهرة.",
        ),
        (
            "answer q8",
            "grammar_function_wording",
            "minor",
            "تقدم شرطًا is awkward as an explanation of لكن إذا; describe it as introducing a conditional case that shows why individual treatment can be insufficient.",
        ),
    ],
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def wc(text: str) -> int:
    return len(TOKEN.findall(text))


def target_counts(record: dict) -> dict[str, int]:
    text = str(record.get("text", "")).casefold()
    out: dict[str, int] = {}
    for target in record.get("new_lexical_targets", []):
        form = str(target.get("form", "")).strip()
        if not form:
            raise SystemExit(f"{record['id']}: blank target")
        out[str(target.get("id", form))] = text.count(form.casefold())
    return out


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected literal once, found {count}: {old}")
    return text.replace(old, new, 1)


def main() -> None:
    raw = PATH.read_bytes()
    actual = sha(raw)
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    b2 = inventory.get("levels", {}).get("b2", {})
    bound = b2.get("canonical_sha256")
    if not isinstance(bound, str) or len(bound) != 64 or actual != bound:
        raise SystemExit(
            f"B2 canonical/inventory drift: canonical={actual}, inventory={bound}; rebind Unit 2 review"
        )

    release = json.loads(RELEASE.read_text(encoding="utf-8"))
    arabic = release.get("languages", {}).get("arabic", {})
    progress = arabic.get("naturalness_review_progress", {})
    if (
        arabic.get("release_state") != "REOPEN_REQUIRED"
        or arabic.get("educator_release_ready") is not False
        or progress.get("fresh_records_reviewed") != 186
        or progress.get("levels_completed") != ["A1", "A2", "B1"]
    ):
        raise SystemExit(
            "Arabic Gate B frontier drift: expected 186 reviewed with A1/A2/B1 complete and B2 Unit 2 next"
        )
    if not (DECISION_DIR / "b2_u01.json").exists() or (DECISION_DIR / "b2_u02.json").exists():
        raise SystemExit("B2 decision frontier drift: B2 Unit 1 must exist and B2 Unit 2 must not")

    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if (
        len(rows) != 60
        or [row.get("sequence") for row in rows] != list(range(1, 61))
        or [rows[i].get("id") for i in range(6, 12)] != EXPECTED_IDS
    ):
        raise SystemExit("B2 Unit 2 layout/id drift")

    by_id = {row["id"]: row for row in rows}
    before_targets = {pid: target_counts(by_id[pid]) for pid in EXPECTED_IDS}

    for pid in EXPECTED_IDS:
        record = by_id[pid]
        text = record["text"]
        for old, new in TEXT_REPAIRS.get(pid, []):
            text = replace_once(text, old, new, f"{pid} text")
        record["text"] = text

        questions = {q["id"]: q for q in record.get("questions", [])}
        answers = {a["question_id"]: a for a in record.get("answer_key", [])}
        edits = QA_REPAIRS.get(pid, {})
        for qid, (old, new) in edits.get("questions", {}).items():
            if questions[qid].get("prompt") != old:
                raise SystemExit(
                    f"{pid}/{qid}: question drift: {questions[qid].get('prompt')!r}"
                )
            questions[qid]["prompt"] = new
        for qid, (old, new) in edits.get("answers", {}).items():
            if answers[qid].get("answer") != old:
                raise SystemExit(
                    f"{pid}/{qid}: answer drift: {answers[qid].get('answer')!r}"
                )
            answers[qid]["answer"] = new

        record["word_count"] = wc(record["text"])
        if not 350 <= record["word_count"] <= 550:
            raise SystemExit(f"{pid}: word count {record['word_count']} outside B2 band")
        if target_counts(record) != before_targets[pid]:
            raise SystemExit(f"{pid}: lexical target occurrence drift")
        if len(record.get("questions", [])) != 10 or len(record.get("answer_key", [])) != 10:
            raise SystemExit(f"{pid}: 10Q/10A invariant failed")
        answers_by_id = {a["id"]: a for a in record["answer_key"]}
        for question in record["questions"]:
            answer = answers_by_id.get(question.get("answer_id"))
            if not answer or answer.get("question_id") != question.get("id"):
                raise SystemExit(f"{pid}/{question.get('id')}: answer linkage drift")

        record["revision"] = int(record.get("revision", 0) or 0) + 1
        quality = record.setdefault("quality", {})
        if quality.get("status") != "draft" or quality.get("coverage_check") != "pending":
            raise SystemExit(f"{pid}: unexpected release/coverage state")
        for field in ("linguistic_review", "pedagogical_review", "answer_key_check", "schema_check"):
            quality[field] = "pass"
        if NOTE not in quality.setdefault("notes", []):
            quality["notes"].append(NOTE)

    total_findings = sum(len(FINDING_META[pid]) for pid in EXPECTED_IDS)
    records_with_findings = sum(bool(FINDING_META[pid]) for pid in EXPECTED_IDS)
    if total_findings != 17 or records_with_findings != 6:
        raise SystemExit(
            f"finding metadata drift: findings={total_findings}, records={records_with_findings}"
        )

    PATH.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "level": "B2",
                "unit": 2,
                "records_reviewed": 6,
                "records_with_findings": records_with_findings,
                "fresh_findings": total_findings,
                "pre_repair_canonical_sha256": actual,
                "post_repair_canonical_sha256": sha(PATH.read_bytes()),
                "word_counts": {pid: by_id[pid]["word_count"] for pid in EXPECTED_IDS},
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
