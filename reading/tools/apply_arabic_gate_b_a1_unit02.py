#!/usr/bin/env python3
"""Apply fresh Arabic Gate B A1 Unit 2 passage/Q&A repairs.

Six exact-current records only. This script does not create the Gate B decision
artifact; decisions are bound after the authoritative packet inventory is rebuilt.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading/arabic/a1/passages.jsonl"
EXPECTED_SHA256 = "bbc91220ddf54e0f26765570071bcd7b8e099613ddab0f8e5dba995e7569ed1c"
EXPECTED_IDS = [f"ar-a1-u02-p{i:02d}" for i in range(1, 7)]
TOKEN = re.compile(r"\S+")
NOTE = (
    "2026-08-31 fresh Gate B naturalness review (A1 Unit 2): learner-facing prose/Q/A "
    "reviewed passage by passage; bounded repairs applied; no educator/publication release claim."
)

TEXT_REPAIRS = {
    "ar-a1-u02-p01": [
        (
            "تضع زجاجة الماء في الحقيبة، وتغلق النافذة، ثم تسأل أمها عن دفتر صغير على الطاولة.",
            "وفي الطريق إلى المدرسة تسأل ليلى أمها عن الدفتر الصغير، فتقول أمها إنه في الحقيبة بجانب كتابها.",
        ),
    ],
    "ar-a1-u02-p03": [
        ("عندما يتأخر الوقت تعودان إلى المنزل.", "عندما يقترب المساء تعودان إلى المنزل."),
    ],
    "ar-a1-u02-p04": [
        (
            "إذا لم أجد الدفتر هناك فسوف أذهب إلى متجر آخر.",
            "إذا لم أجد الدفتر هناك فسوف أذهب إلى مكان آخر.",
        ),
    ],
    "ar-a1-u02-p06": [
        (
            "بهذا الترتيب لا تشعر ليلى بالعجلة، وتعرف ماذا تفعل في كل وقت.",
            "بهذا الترتيب لا تستعجل ليلى، وتعرف ماذا تفعل في كل وقت.",
        ),
    ],
}

QA_REPAIRS = {
    "ar-a1-u02-p01": {
        "answers": {
            "q3": ("الفترة أو اللحظة المناسبة للاستعداد.", "الوقت المناسب للاستعداد."),
            "q6": ("زمن أو مدة يحدث فيها شيء.", "الزمن الذي يحدث فيه شيء."),
        }
    },
    "ar-a1-u02-p02": {
        "questions": {
            "q1": ("ماذا تفعل ليلى أولًا عندما تدخل الصف؟", "ماذا تفعل ليلى عندما تدخل الصف؟"),
            "q8": ("أيهما يأتي في البداية: «أول» أم «آخر»؟", "أيهما يدل على البداية: «أول» أم «آخر»؟"),
        }
    },
    "ar-a1-u02-p04": {
        "questions": {
            "q4": ("ماذا تعني «آخر» في «متجر آخر»؟", "ماذا تعني «آخر» في «مكان آخر»؟"),
        },
        "answers": {
            "q4": ("متجرًا مختلفًا أو إضافيًا غير الأول.", "مكانًا مختلفًا عن المكتبة."),
        },
    },
    "ar-a1-u02-p05": {
        "questions": {
            "q8": (
                "أيهما يدل على أكثر من متكلم واحد: «أنا» أم «نحن»؟",
                "إذا كنت أتكلم عن نفسي وأخي معًا، أقول «أنا» أم «نحن»؟",
            ),
        },
        "answers": {
            "q6": ("ضمير للمتكلم مع شخص أو أشخاص آخرين.", "كلمة تعني المتكلم مع شخص أو أشخاص آخرين."),
        },
    },
    "ar-a1-u02-p06": {
        "questions": {
            "q3": (
                "متى يجب على ليلى أن تنهي الواجب قبل الخروج؟",
                "عندما يكون عند ليلى واجب بعد المدرسة، ماذا يجب أن تفعل قبل الخروج؟",
            ),
        },
        "answers": {
            "q3": ("عندما يكون عندها واجب بعد المدرسة.", "يجب أن تنهي الواجب."),
            "q6": ("علامة تدل على أن الفعل سيحدث في المستقبل.", "تعني أن الفعل سيحدث لاحقًا."),
        },
    },
}

FINDING_META = {
    "ar-a1-u02-p01": [
        ("text", "cohesion", "moderate", "Remove the post-departure chronology jump at the end of the morning routine."),
        ("answer q3", "answer_wording", "minor", "Use a direct A1 explanation of وقت in the passage context."),
        ("answer q6", "answer_wording", "minor", "Replace an abstract dictionary-style definition with simpler learner-facing wording."),
    ],
    "ar-a1-u02-p02": [
        ("question q1", "semantic_precision", "moderate", "Remove the ambiguous claim about which of two immediate entry actions is literally first."),
        ("question q8", "question_wording", "minor", "Ask what أول signifies rather than saying the word itself comes first."),
    ],
    "ar-a1-u02-p03": [
        ("text", "naturalness_idiomaticity", "minor", "Replace translation-like عندما يتأخر الوقت with idiomatic temporal wording."),
    ],
    "ar-a1-u02-p04": [
        ("text/q4/a4", "semantic_precision", "moderate", "Avoid treating the library as the first store while preserving the target آخر and its contrastive meaning."),
    ],
    "ar-a1-u02-p05": [
        ("answer q6", "answer_wording", "minor", "Replace formal grammatical-label wording with an A1-accessible meaning explanation."),
        ("question q8", "semantic_precision", "moderate", "Test نحن as speaker-plus-other person(s), not as multiple speakers."),
    ],
    "ar-a1-u02-p06": [
        ("text", "naturalness_idiomaticity", "minor", "Replace لا تشعر بالعجلة with the idiomatic verb لا تستعجل."),
        ("question/answer q3", "semantic_precision", "moderate", "Repair a malformed when/condition question so the answer directly satisfies it and both targets remain grounded."),
        ("answer q6", "answer_wording", "minor", "Explain سوف directly without an abstract metalinguistic label."),
    ],
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def wc(text: str) -> int:
    return len(TOKEN.findall(text))


def target_counts(record: dict) -> dict[str, int]:
    text = str(record.get("text", "")).casefold()
    out = {}
    for target in record.get("new_lexical_targets", []):
        form = str(target.get("form", "")).strip()
        if not form:
            raise SystemExit(f"{record['id']}: blank lexical target")
        out[str(target.get("id", form))] = text.count(form.casefold())
    return out


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exact literal once, found {count}: {old}")
    return text.replace(old, new, 1)


def main() -> None:
    raw = PATH.read_bytes()
    actual = sha256_bytes(raw)
    if actual != EXPECTED_SHA256:
        raise SystemExit(f"A1 canonical drift: expected {EXPECTED_SHA256}, got {actual}; rebind Unit 2 review")
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 60 or [r.get("sequence") for r in rows] != list(range(1, 61)):
        raise SystemExit("A1 canonical layout drift")
    if [rows[i].get("id") for i in range(6, 12)] != EXPECTED_IDS:
        raise SystemExit("A1 Unit 2 id/layout drift")
    by_id = {r.get("id"): r for r in rows}
    before_targets = {pid: target_counts(by_id[pid]) for pid in EXPECTED_IDS}

    for pid in EXPECTED_IDS:
        record = by_id[pid]
        text = str(record.get("text", ""))
        for old, new in TEXT_REPAIRS.get(pid, []):
            text = replace_once(text, old, new, f"{pid} text")
        record["text"] = text

        edits = QA_REPAIRS.get(pid, {})
        q_by_id = {q.get("id"): q for q in record.get("questions", [])}
        a_by_qid = {a.get("question_id"): a for a in record.get("answer_key", [])}
        for qid, (old, new) in edits.get("questions", {}).items():
            if q_by_id[qid].get("prompt") != old:
                raise SystemExit(f"{pid}/{qid}: question drift")
            q_by_id[qid]["prompt"] = new
        for qid, (old, new) in edits.get("answers", {}).items():
            if a_by_qid[qid].get("answer") != old:
                raise SystemExit(f"{pid}/{qid}: answer drift")
            a_by_qid[qid]["answer"] = new

        record["word_count"] = wc(record["text"])
        if not 90 <= record["word_count"] <= 140:
            raise SystemExit(f"{pid}: word count {record['word_count']} outside A1 90-140 band")
        if target_counts(record) != before_targets[pid]:
            raise SystemExit(f"{pid}: new lexical target occurrence count changed")
        questions = record.get("questions", [])
        answers = record.get("answer_key", [])
        if len(questions) != 10 or len(answers) != 10:
            raise SystemExit(f"{pid}: 10Q/10A invariant failed")
        answer_by_id = {a.get("id"): a for a in answers}
        for q in questions:
            linked = answer_by_id.get(q.get("answer_id"))
            if not linked or linked.get("question_id") != q.get("id"):
                raise SystemExit(f"{pid}/{q.get('id')}: answer linkage drift")

        record["revision"] = int(record.get("revision", 0) or 0) + 1
        quality = record.setdefault("quality", {})
        quality["linguistic_review"] = "pass"
        quality["pedagogical_review"] = "pass"
        quality["answer_key_check"] = "pass"
        quality["schema_check"] = "pass"
        if quality.get("status") != "draft" or quality.get("coverage_check") != "pending":
            raise SystemExit(f"{pid}: refusing unexpected release/coverage state")
        notes = quality.setdefault("notes", [])
        if NOTE not in notes:
            notes.append(NOTE)

    total_findings = sum(len(FINDING_META[pid]) for pid in EXPECTED_IDS)
    if total_findings != 12:
        raise SystemExit(f"finding metadata drift: expected 12, got {total_findings}")

    PATH.write_text(
        "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows),
        encoding="utf-8",
    )
    post_sha = sha256_bytes(PATH.read_bytes())
    print(
        json.dumps(
            {
                "level": "A1",
                "unit": 2,
                "records_reviewed": 6,
                "records_with_findings": 6,
                "fresh_findings": total_findings,
                "post_repair_canonical_sha256": post_sha,
                "word_counts": {pid: by_id[pid]["word_count"] for pid in EXPECTED_IDS},
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
