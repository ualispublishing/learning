#!/usr/bin/env python3
"""Derive the LANG-A1C2 active production plan from current canonical state.

This is generation infrastructure only. It does not validate linguistic or
pedagogical quality and must never invent a frontier when live state is stale or
malformed. Production state comes from STATUS + CONTINUATION and is cross-checked
against the active level's canonical JSONL before a derived plan is written.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
STATUS = READING / "STATUS.json"
CONTINUATION = READING / "CONTINUATION.json"
MATRIX = READING / "planning" / "topic_genre_matrix.json"
OUT = READING / "planning" / "ACTIVE_GENERATION_PLAN.json"
LEVELS = ("A1", "A2", "B1", "B2", "C1", "C2")
LANGUAGES = ("arabic", "french", "urdu")
PASSAGES_PER_LEVEL = 60
PASSAGES_PER_UNIT = 6


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def norm_level(value) -> str:
    return str(value or "").strip().upper()


def norm_language(value) -> str:
    return str(value or "").strip().lower()


def fail(message: str):
    raise SystemExit(f"ACTIVE_GENERATION_PLAN derivation failed: {message}")


def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    with path.open("r", encoding="utf-8") as f:
        for line_no, raw in enumerate(f, 1):
            if not raw.strip():
                continue
            try:
                json.loads(raw)
            except json.JSONDecodeError as exc:
                fail(f"invalid canonical JSONL at {path.relative_to(ROOT)}:{line_no}: {exc}")
            count += 1
    return count


def canonical_language_count(language: str) -> int:
    return sum(count_jsonl(READING / language / level.lower() / "passages.jsonl") for level in LEVELS)


def resolve_frontier(status: dict, continuation: dict) -> tuple[str, str]:
    if status.get("project_id") != "LANG-A1C2":
        fail("STATUS.json project_id is not LANG-A1C2")
    if status.get("state_type") != "PRODUCTION_STATUS_ONLY":
        fail("STATUS.json must use state_type=PRODUCTION_STATUS_ONLY")
    if continuation.get("project_id") != "LANG-A1C2":
        fail("CONTINUATION.json project_id is not LANG-A1C2")

    status_current = status.get("current")
    cont_frontier = continuation.get("active_frontier", {}).get("production")
    if not isinstance(status_current, dict) or not isinstance(cont_frontier, dict):
        fail("missing current production frontier in STATUS or CONTINUATION")

    status_language = norm_language(status_current.get("active_language"))
    status_level = norm_level(status_current.get("active_level"))
    cont_language = norm_language(cont_frontier.get("language"))
    cont_level = norm_level(cont_frontier.get("level"))

    if status_language not in LANGUAGES:
        fail(f"unsupported STATUS active_language={status_language!r}")
    if status_level not in LEVELS:
        fail(f"unsupported STATUS active_level={status_level!r}")
    if (status_language, status_level) != (cont_language, cont_level):
        fail(
            "STATUS/CONTINUATION frontier disagreement: "
            f"STATUS={status_language}/{status_level}, "
            f"CONTINUATION={cont_language}/{cont_level}"
        )

    language_state = status.get("languages", {}).get(status_language)
    continuation_state = continuation.get("production", {}).get(status_language)
    if not isinstance(language_state, dict) or not isinstance(continuation_state, dict):
        fail(f"missing per-language production state for {status_language}")

    status_next = norm_level(language_state.get("next_generation_level"))
    continuation_next = norm_level(continuation_state.get("next_generation_level"))
    if status_next != status_level:
        fail(
            f"STATUS languages.{status_language}.next_generation_level={status_next!r} "
            f"does not match active_level={status_level}"
        )
    if continuation_next != status_level:
        fail(
            f"CONTINUATION production.{status_language}.next_generation_level={continuation_next!r} "
            f"does not match active_level={status_level}"
        )

    live_language_total = canonical_language_count(status_language)
    status_language_total = int(language_state.get("canonical_passages", -1))
    continuation_language_total = int(continuation_state.get("canonical_passages", -1))
    if live_language_total != status_language_total or live_language_total != continuation_language_total:
        fail(
            f"{status_language} canonical total drift: live={live_language_total}, "
            f"STATUS={status_language_total}, CONTINUATION={continuation_language_total}"
        )

    complete_levels = [norm_level(x) for x in language_state.get("complete_levels", [])]
    continuation_complete = [norm_level(x) for x in continuation_state.get("complete_levels", [])]
    if complete_levels != continuation_complete:
        fail(
            f"{status_language} complete_levels disagreement: "
            f"STATUS={complete_levels}, CONTINUATION={continuation_complete}"
        )

    active_index = LEVELS.index(status_level)
    expected_complete = list(LEVELS[:active_index])
    if complete_levels != expected_complete:
        fail(
            f"{status_language} complete_levels={complete_levels} does not match "
            f"frontier {status_level}; expected {expected_complete}"
        )

    for level in expected_complete:
        count = count_jsonl(READING / status_language / level.lower() / "passages.jsonl")
        if count != PASSAGES_PER_LEVEL:
            fail(
                f"{status_language} {level} is marked complete but live count is {count}, "
                f"expected {PASSAGES_PER_LEVEL}"
            )

    active_count = count_jsonl(READING / status_language / status_level.lower() / "passages.jsonl")
    if active_count >= PASSAGES_PER_LEVEL:
        fail(
            f"{status_language} {status_level} live count is {active_count}; "
            "the stored frontier must advance before deriving another plan"
        )

    return status_language, status_level


def previous_level_anchor(language: str, level: str, status: dict, continuation: dict) -> dict | None:
    index = LEVELS.index(level)
    if index == 0:
        return None
    previous = LEVELS[index - 1]
    previous_path = READING / language / previous.lower() / "passages.jsonl"
    previous_count = count_jsonl(previous_path)
    if previous_count != PASSAGES_PER_LEVEL:
        fail(f"previous level {language}/{previous} has {previous_count} passages; expected 60")

    # Preserve richer exact audit/hash anchors when the live state has one.
    if language == "urdu" and previous == "A1":
        status_a1 = status.get("languages", {}).get("urdu", {}).get("a1", {})
        cont_urdu = continuation.get("production", {}).get("urdu", {})
        expected_blob = cont_urdu.get("a1_git_blob")
        if not expected_blob or status_a1.get("git_blob") != expected_blob:
            fail("Urdu A1 anchor is missing or inconsistent between STATUS and CONTINUATION")
        return {
            "level": "A1",
            "canonical_path": cont_urdu.get("a1_canonical_path", "reading/urdu/a1/passages.jsonl"),
            "passages": previous_count,
            "git_blob": expected_blob,
            "integrity_evidence": cont_urdu.get("a1_integrity_evidence"),
            "integrity_gate": status_a1.get("integrity_gate"),
            "quality_promotion": status_a1.get("quality_promotion"),
        }

    return {
        "level": previous,
        "canonical_path": previous_path.relative_to(ROOT).as_posix(),
        "passages": previous_count,
    }


def main():
    status = load_json(STATUS)
    continuation = load_json(CONTINUATION)
    matrix = load_json(MATRIX)
    language, level = resolve_frontier(status, continuation)

    levels = matrix.get("levels")
    if not isinstance(levels, dict) or level not in levels:
        fail(f"topic_genre_matrix.json has no exact levels.{level} roadmap")
    roadmap = levels[level]
    if not isinstance(roadmap, list) or len(roadmap) != 10:
        fail(f"levels.{level} roadmap must contain exactly 10 units")
    expected_units = list(range(1, 11))
    actual_units = [int(x.get("unit", -1)) for x in roadmap if isinstance(x, dict)]
    if actual_units != expected_units:
        fail(f"levels.{level} unit sequence is {actual_units}; expected {expected_units}")

    active_path = READING / language / level.lower() / "passages.jsonl"
    active_count = count_jsonl(active_path)
    active_unit = (active_count // PASSAGES_PER_UNIT) + 1
    start_sequence = active_count + 1
    if active_unit > 10:
        fail(f"derived active_unit={active_unit} is outside the 10-unit level design")

    anchor = previous_level_anchor(language, level, status, continuation)
    payload = {
        "schema_version": 3,
        "project_id": "LANG-A1C2",
        "state_type": "ACTIVE_PRODUCTION_FRONTIER",
        "source_continuation": "reading/CONTINUATION.json",
        "source_status": "reading/STATUS.json",
        "source_matrix": "reading/planning/topic_genre_matrix.json",
        "generation_policy": "reading/planning/GENERATION_FIRST_FINAL_AUDIT_POLICY.md",
        "active_language": language,
        "active_level": level,
        "active_unit": active_unit,
        "start_sequence": start_sequence,
        "canonical_active_path": active_path.relative_to(ROOT).as_posix(),
        "existing_active_level_passages": active_count,
        "roadmap_lookup": f"$.levels.{level}",
        "active_unit_roadmap": roadmap[active_unit - 1],
        "generation_first": True,
        "formal_release_audits_deferred_during_ordinary_generation": True,
        "previous_level_anchor": anchor,
        "guardrails": [
            "STATUS.json and CONTINUATION.json must agree on language and level before this plan is written.",
            "Live canonical JSONL counts must agree with cached per-language production totals.",
            "All levels before the active level must contain exactly 60 canonical passages.",
            "The active level must contain fewer than 60 passages; otherwise the frontier must advance first.",
            "Use the exact active-unit theme/genres from topic_genre_matrix.json; do not invent or rename the roadmap.",
            "Generate in guarded unit or large bounded batches rather than one workflow per passage.",
            "Preserve 6 passages per unit and the active 10-question/10-answer contract unless a documented pedagogical exception applies.",
            "Write natural independent target-language passages rather than translating another language's corpus.",
            "Fix obvious severe defects immediately; defer repeated formal release audits to the designated review phase.",
            "Generation/integrity state must never be interpreted as educator/publication release approval."
        ],
        "on_frontier_change": [
            "Update reading/CONTINUATION.json, reading/STATUS.json, and reading/TASKS.md together.",
            "Regenerate this derived plan from current state instead of hand-editing its frontier.",
            "Refresh reading/STATE_MANIFEST.json last after tracked live-state files are stable."
        ]
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"active_frontier={language}/{level}; unit={active_unit}; "
        f"start_sequence={start_sequence}; wrote {OUT.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
