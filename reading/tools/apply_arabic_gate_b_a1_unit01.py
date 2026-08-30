#!/usr/bin/env python3
"""Apply the fresh Gate B Arabic A1 Unit 1 naturalness review.

This is deliberately narrow: six exact-current records, exact literal repairs,
no quality promotion, and a hash-bound decision artifact for the repaired learner-facing text.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading/arabic/a1/passages.jsonl"
DECISION_DIR = ROOT / "reading/audit/arabic_gate_b_decisions_2026-08-30"
DECISION_PATH = DECISION_DIR / "a1_u01.json"
EXPECTED_SHA256 = "7047f63f46a0448025c1602bd81302d48830150a036a5c43ddfdcbf9322617c1"
TOKEN = re.compile(r"\S+")
NOTE = (
    "2026-08-30 fresh Gate B naturalness review (A1 Unit 1): "
    "learner-facing prose/Q/A wording reviewed passage by passage; bounded repairs applied; "
    "no educator/publication release claim."
)

TEXT_REPAIRS = {
    "ar-a1-u01-p01": [
        ("الحقيبة معها في المنزل.", "كانت حقيبتها معها."),
        (
            "ذهبتا إلى داخل المنزل ثم إلى خارجه. ثم كانتا داخل المنزل مرة أخرى.",
            "مشتا داخل المنزل، ثم خرجتا قليلًا. وبعد ذلك عادتا إلى الداخل.",
        ),
    ],
    "ar-a1-u01-p02": [
        ("بعد قليل كانت ليلى في المنزل مرة أخرى.", "بعد المدرسة عادت ليلى إلى المنزل مرة أخرى."),
        ("بعد ذلك كانتا معا في المنزل.", "بعد ذلك جلستا معًا في المنزل."),
    ],
    "ar-a1-u01-p03": [
        ("كانتا هناك وقتا قليلا.", "بقيتا هناك قليلًا."),
    ],
    "ar-a1-u01-p04": [
        ("في المكتبة كتاب جميل.", "رأت ليلى كتابًا جميلًا في المكتبة."),
        ("قالت الأم: يمكنك أن تري الكتاب هنا.", "قالت الأم: يمكنك أن تقرئي الكتاب هنا."),
        ("كان الكتاب مع حقيبتها.", "كان الكتاب بجانب حقيبتها."),
        ("قالت ليلى: نعم، لكن ليس كل الكتاب اليوم.", "قالت ليلى: نعم، لكنني لا أريد أن أقرأ كل الكتاب اليوم."),
    ],
    "ar-a1-u01-p05": [
        ("في المنزل وضعت الكتابين هنا، مع حقيبتها.", "في المنزل وضعت الكتابين هنا بجانب حقيبتها."),
        ("قالت ليلى: أريد أن أقرأ قليلا فقط، ثم أكون معك.", "قالت ليلى: أريد أن أقرأ قليلًا فقط، ثم أجلس معك."),
    ],
    "ar-a1-u01-p06": [
        ("تذهبان معا، وتكونان هناك قليلا.", "تذهبان معًا، وتبقيان هناك قليلًا."),
        ("لكنها لا تقرأ كل الوقت.", "لكنها لا تقرأ طوال الوقت."),
        ("بعد ذلك تكون مع أمها.", "بعد ذلك تجلس مع أمها."),
    ],
}

QA_REPAIRS = {
    "ar-a1-u01-p02": {
        "questions": {
            "q3": (
                "ماذا تعني «بعد» في «بعد قليل كانت ليلى في المنزل مرة أخرى»؟",
                "ماذا تعني «بعد» في «بعد المدرسة عادت ليلى إلى المنزل مرة أخرى»؟",
            )
        },
        "answers": {
            "q3": ("في وقت يأتي لاحقا.", "في وقت يأتي بعد المدرسة."),
            "q6": ("فحسب؛ لا غير.", "لا أكثر."),
        },
    },
    "ar-a1-u01-p05": {
        "answers": {
            "q6": ("جزء من الشيء، قليلاً كان أو كثيرًا.", "جزء من الشيء، لا كله."),
        }
    },
    "ar-a1-u01-p06": {
        "answers": {
            "q1": (
                "ليلى أصبحت تعرف روتينها والأماكن القريبة من منزلها.",
                "ليلى تعرف يومها والأماكن القريبة من منزلها.",
            ),
            "q2": (
                "تعود إلى المنزل، وقد تذهب لاحقا إلى الحديقة أو المكتبة.",
                "تعود إلى المنزل، وفي بعض الأيام تذهب إلى الحديقة أو المكتبة.",
            ),
            "q5": (
                "تذهب ليلى إلى المدرسة وتعود إلى منزلها، وقد تذهب إلى الحديقة أو المكتبة.",
                "تذهب ليلى إلى المدرسة وتعود إلى منزلها، وفي بعض الأيام تذهب إلى الحديقة أو المكتبة.",
            ),
        }
    },
}

FINDING_META = {
    "ar-a1-u01-p01": [
        ("text", "naturalness_idiomaticity", "minor", "Remove translation-like possession/location wording."),
        ("text", "cohesion", "minor", "Make the inside/outside movement sequence idiomatic and explicit."),
    ],
    "ar-a1-u01-p02": [
        ("text/q3/a3", "semantic_precision", "moderate", "Repair implausibly short school-day chronology while keeping the target بعد grounded."),
        ("text", "naturalness_idiomaticity", "minor", "Replace stative together-at-home wording with a natural action."),
        ("answer q6", "answer_wording", "minor", "Simplify the A1 definition of فقط."),
    ],
    "ar-a1-u01-p03": [
        ("text", "naturalness_idiomaticity", "minor", "Replace unnatural duration phrase with idiomatic MSA."),
    ],
    "ar-a1-u01-p04": [
        ("text", "pragmatic_plausibility", "minor", "Introduce the book through a natural observed action."),
        ("text", "semantic_precision", "moderate", "Replace ambiguous/awkward تري wording with a clear reading action."),
        ("text", "naturalness_idiomaticity", "minor", "Use بجانب for the book's spatial relation to the bag."),
        ("text", "naturalness_idiomaticity", "minor", "Replace elliptical ليس كل الكتاب اليوم with a complete A1 sentence."),
    ],
    "ar-a1-u01-p05": [
        ("text", "naturalness_idiomaticity", "minor", "Use بجانب instead of comma-separated مع for object placement."),
        ("text", "semantic_precision", "minor", "Replace vague أكون معك with the concrete action أجلس معك."),
        ("answer q6", "answer_wording", "minor", "Make the A1 definition of بعض direct and contrastive."),
    ],
    "ar-a1-u01-p06": [
        ("text", "naturalness_idiomaticity", "minor", "Replace stative تكونان with the natural duration verb تبقيان."),
        ("text", "naturalness_idiomaticity", "minor", "Use idiomatic طوال الوقت rather than كل الوقت."),
        ("text", "semantic_precision", "minor", "Replace vague تكون مع أمها with the concrete action تجلس مع أمها."),
        ("answer q1", "answer_wording", "minor", "Replace loanword-heavy روتينها with simpler A1 wording."),
        ("answers q2/q5", "answer_wording", "minor", "Replace advanced probabilistic قد phrasing with passage-grounded A1 wording."),
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


def learner_payload(record: dict) -> dict:
    answers = {a.get("question_id"): a for a in record.get("answer_key", [])}
    qa = []
    for q in record.get("questions", []):
        a = answers.get(q.get("id"), {})
        qa.append(
            {
                "question_id": q.get("id"),
                "type": q.get("type"),
                "prompt": q.get("prompt"),
                "answer": a.get("answer"),
                "explanation": a.get("explanation", ""),
            }
        )
    return {
        "passage_id": record.get("id"),
        "unit": record.get("unit"),
        "sequence": record.get("sequence"),
        "cefr": record.get("cefr"),
        "title": record.get("title"),
        "genre": record.get("genre"),
        "text": record.get("text"),
        "qa": qa,
    }


def learner_hash(record: dict) -> str:
    raw = json.dumps(
        learner_payload(record), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256_bytes(raw)


def replace_exact(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exact literal once, found {count}: {old}")
    return text.replace(old, new, 1)


def main() -> None:
    raw = PATH.read_bytes()
    actual_sha = sha256_bytes(raw)
    if actual_sha != EXPECTED_SHA256:
        raise SystemExit(
            f"A1 canonical drift: expected {EXPECTED_SHA256}, got {actual_sha}; rebind review before writing"
        )
    rows = [json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    if len(rows) != 60 or [r.get("sequence") for r in rows] != list(range(1, 61)):
        raise SystemExit("A1 canonical layout drift")
    by_id = {r.get("id"): r for r in rows}
    expected_ids = [f"ar-a1-u01-p{i:02d}" for i in range(1, 7)]
    if [rows[i]["id"] for i in range(6)] != expected_ids:
        raise SystemExit("A1 Unit 1 frontier/id drift")

    before_targets = {pid: target_counts(by_id[pid]) for pid in expected_ids}
    findings = []

    for pid in expected_ids:
        record = by_id[pid]
        text = str(record.get("text", ""))
        for old, new in TEXT_REPAIRS.get(pid, []):
            text = replace_exact(text, old, new, f"{pid} text")
        record["text"] = text

        edits = QA_REPAIRS.get(pid, {})
        q_by_id = {q["id"]: q for q in record.get("questions", [])}
        a_by_qid = {a["question_id"]: a for a in record.get("answer_key", [])}
        for qid, (old, new) in edits.get("questions", {}).items():
            q = q_by_id[qid]
            if q.get("prompt") != old:
                raise SystemExit(f"{pid}/{qid}: question drift")
            q["prompt"] = new
        for qid, (old, new) in edits.get("answers", {}).items():
            a = a_by_qid[qid]
            if a.get("answer") != old:
                raise SystemExit(f"{pid}/{qid}: answer drift")
            a["answer"] = new

        record["word_count"] = wc(record["text"])
        if not 90 <= record["word_count"] <= 140:
            raise SystemExit(f"{pid}: word count {record['word_count']} outside A1 90-140 band")
        if target_counts(record) != before_targets[pid]:
            raise SystemExit(f"{pid}: new lexical target occurrence count changed")
        if len(record.get("questions", [])) != 10 or len(record.get("answer_key", [])) != 10:
            raise SystemExit(f"{pid}: 10Q/10A invariant failed")
        links = {q["answer_id"] for q in record["questions"]}
        answer_ids = {a["id"] for a in record["answer_key"]}
        if links != answer_ids:
            raise SystemExit(f"{pid}: answer linkage drift")
        record["revision"] = int(record.get("revision", 0) or 0) + 1
        notes = record.setdefault("quality", {}).setdefault("notes", [])
        if NOTE not in notes:
            notes.append(NOTE)

        meta = FINDING_META[pid]
        for idx, (field, dimension, severity, rationale) in enumerate(meta, 1):
            findings.append(
                {
                    "finding_id": f"{pid}-gB-{idx:02d}",
                    "passage_id": pid,
                    "sequence": record["sequence"],
                    "field": field,
                    "dimension": dimension,
                    "severity": severity,
                    "resolution": "REPAIRED",
                    "rationale": rationale,
                }
            )

    rendered = "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n"
    PATH.write_text(rendered, encoding="utf-8")
    canonical_sha = sha256_bytes(rendered.encode("utf-8"))

    decisions = []
    for pid in expected_ids:
        record = by_id[pid]
        decisions.append(
            {
                "passage_id": pid,
                "sequence": record["sequence"],
                "learner_facing_sha256": learner_hash(record),
                "decision": "PASS_AFTER_REPAIR",
                "finding_count": len(FINDING_META[pid]),
            }
        )

    audit = {
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "language": "arabic",
        "gate": "Gate B — passage-by-passage linguistic/naturalness audit",
        "date": "2026-08-30",
        "level": "A1",
        "unit": 1,
        "canonical_path": "reading/arabic/a1/passages.jsonl",
        "pre_repair_canonical_sha256": EXPECTED_SHA256,
        "post_repair_canonical_sha256": canonical_sha,
        "records_reviewed": 6,
        "records_with_findings": 6,
        "fresh_findings": len(findings),
        "status": "PASS_AFTER_REPAIR",
        "decisions": decisions,
        "findings": findings,
        "quality_promotion": False,
        "release_claim": False,
        "note": "Fresh review is internal Gate B evidence only; educator/publication release approval remains separate.",
    }
    DECISION_DIR.mkdir(parents=True, exist_ok=True)
    DECISION_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "level": "A1",
                "unit": 1,
                "records_reviewed": 6,
                "records_with_findings": 6,
                "fresh_findings": len(findings),
                "post_repair_canonical_sha256": canonical_sha,
                "word_counts": {pid: by_id[pid]["word_count"] for pid in expected_ids},
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
