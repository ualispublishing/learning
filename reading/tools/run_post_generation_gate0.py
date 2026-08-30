#!/usr/bin/env python3
"""Run LANG-A1C2 post-generation Gate 0 and write a hash-bound audit artifact.

Gate 0 is structural/state verification only. It never promotes educator/publication
release readiness and never edits canonical passage files.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
AUDIT = READING / "audit" / "post_generation_gate0_2026-08-30.json"
LANGUAGES = ("arabic", "french", "urdu")
LEVELS = ("a1", "a2", "b1", "b2", "c1", "c2")
EXPECTED_PER_LEVEL = 60
EXPECTED_PER_LANGUAGE = 360
EXPECTED_TOTAL = 1080


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_jsonl(path: Path):
    records = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise AssertionError(f"{path.relative_to(ROOT)} line {lineno}: invalid JSON: {exc}") from exc
    return records


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []

    validation = subprocess.run(
        [sys.executable, "reading/tools/validate_continuation_state.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    validation_output = validation.stdout.strip()
    require(validation.returncode == 0, "continuation/state validator did not pass", errors)

    status = load_json(READING / "STATUS.json")
    continuation = load_json(READING / "CONTINUATION.json")
    plan = load_json(READING / "planning" / "ACTIVE_GENERATION_PLAN.json")
    release = load_json(READING / "RELEASE_STATUS.json")

    require(status["current"]["canonical_passages"] == EXPECTED_TOTAL, "STATUS total is not 1080", errors)
    require(status["current"]["remaining_generation_passages"] == 0, "STATUS remaining generation is not zero", errors)
    require(status["current"]["active_language"] is None, "STATUS still has an active language", errors)
    require(status["current"]["active_level"] is None, "STATUS still has an active level", errors)
    require(continuation["active_frontier"]["production"]["language"] is None, "CONTINUATION still has an active generation language", errors)
    require(continuation["active_frontier"]["production"]["level"] is None, "CONTINUATION still has an active generation level", errors)
    require(plan.get("generation_complete") is True, "ACTIVE_GENERATION_PLAN is not generation_complete", errors)
    require(plan.get("active_language") is None and plan.get("active_level") is None, "ACTIVE_GENERATION_PLAN still exposes an active frontier", errors)

    files: dict[str, dict[str, object]] = {}
    language_totals: dict[str, int] = {}
    all_ids: list[str] = []
    question_total = 0
    answer_total = 0

    for language in LANGUAGES:
        language_total = 0
        for level in LEVELS:
            path = READING / language / level / "passages.jsonl"
            rel = path.relative_to(ROOT).as_posix()
            require(path.exists(), f"missing canonical file: {rel}", errors)
            if not path.exists():
                continue
            data = path.read_bytes()
            try:
                records = read_jsonl(path)
            except AssertionError as exc:
                errors.append(str(exc))
                continue

            count = len(records)
            language_total += count
            require(count == EXPECTED_PER_LEVEL, f"{language} {level.upper()}: {count} passages != 60", errors)

            sequences = [r.get("sequence") for r in records]
            require(sequences == list(range(1, EXPECTED_PER_LEVEL + 1)), f"{language} {level.upper()}: sequence must be exactly 1..60", errors)

            ids = [r.get("id") for r in records]
            require(all(isinstance(x, str) and x for x in ids), f"{language} {level.upper()}: missing/non-string passage id", errors)
            require(len(ids) == len(set(ids)), f"{language} {level.upper()}: duplicate passage ids within level", errors)
            all_ids.extend(x for x in ids if isinstance(x, str))

            q_count = 0
            a_count = 0
            for record in records:
                qs = record.get("questions", [])
                aks = record.get("answer_key", [])
                if isinstance(qs, list):
                    q_count += len(qs)
                else:
                    errors.append(f"{record.get('id', rel)}: questions is not a list")
                if isinstance(aks, list):
                    a_count += len(aks)
                else:
                    errors.append(f"{record.get('id', rel)}: answer_key is not a list")
            question_total += q_count
            answer_total += a_count

            files[rel] = {
                "passages": count,
                "questions": q_count,
                "answers": a_count,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "git_blob": git_blob_sha(data),
            }

        language_totals[language] = language_total
        require(language_total == EXPECTED_PER_LANGUAGE, f"{language}: {language_total} passages != 360", errors)
        require(status["languages"][language]["canonical_passages"] == language_total, f"{language}: STATUS differs from canonical count", errors)
        require(continuation["production"][language]["canonical_passages"] == language_total, f"{language}: CONTINUATION differs from canonical count", errors)

    require(sum(language_totals.values()) == EXPECTED_TOTAL, f"canonical total {sum(language_totals.values())} != 1080", errors)
    require(len(all_ids) == len(set(all_ids)), "duplicate passage ids exist across canonical corpus", errors)
    require(question_total == 10800, f"canonical question total {question_total} != 10800", errors)
    require(answer_total == 10800, f"canonical answer-key total {answer_total} != 10800", errors)

    cached = continuation["release"]
    for language in LANGUAGES:
        require(
            cached[language]["educator_release_ready"] == release["languages"][language]["educator_release_ready"],
            f"{language}: cached educator release readiness differs from RELEASE_STATUS",
            errors,
        )
        require(
            cached[language]["release_state"] == release["languages"][language]["release_state"],
            f"{language}: cached release state differs from RELEASE_STATUS",
            errors,
        )

    urdu_a1_rel = "reading/urdu/a1/passages.jsonl"
    pinned = continuation["production"]["urdu"]["a1_git_blob"]
    actual_urdu_a1_blob = files.get(urdu_a1_rel, {}).get("git_blob")
    require(actual_urdu_a1_blob == pinned, "Urdu A1 canonical blob differs from pinned integrity baseline", errors)

    audit = {
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "gate": "Gate 0 — route / continuation / state-bundle consistency",
        "date": str(date(2026, 8, 30)),
        "status": "PASS" if not errors else "FAIL",
        "scope": "Post-generation structural/state integrity for the exact 1080-passage canonical corpus; not semantic or educator approval.",
        "continuation_validator": {
            "command": "python reading/tools/validate_continuation_state.py",
            "returncode": validation.returncode,
            "output": validation_output,
        },
        "canonical_totals": {
            "project": sum(language_totals.values()),
            "arabic": language_totals.get("arabic", 0),
            "french": language_totals.get("french", 0),
            "urdu": language_totals.get("urdu", 0),
            "questions": question_total,
            "answers": answer_total,
        },
        "generation_frontier": {
            "remaining_generation_passages": status["current"]["remaining_generation_passages"],
            "active_language": status["current"]["active_language"],
            "active_level": status["current"]["active_level"],
            "generation_complete": plan.get("generation_complete"),
        },
        "canonical_files": files,
        "urdu_a1_integrity_anchor": {
            "pinned_git_blob": pinned,
            "actual_git_blob": actual_urdu_a1_blob,
            "matches": actual_urdu_a1_blob == pinned,
        },
        "release_state_snapshot": {
            language: {
                "release_state": release["languages"][language]["release_state"],
                "educator_release_ready": release["languages"][language]["educator_release_ready"],
            }
            for language in LANGUAGES
        },
        "hard_errors": len(errors),
        "errors": errors,
        "release_claim": False,
        "next_gate": "Language-specific fresh educator-release revalidation; Gate 0 does not promote any language to release-ready.",
    }

    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
