#!/usr/bin/env python3
"""Validate the pre-staged seven-session LANG-A1C2 Urdu A2 queue."""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
QUEUE = READING / "planning" / "WEEK_READY_2026-08-24.json"
MATRIX = READING / "planning" / "topic_genre_matrix.json"
PASSAGES_PER_SESSION = 6
PROJECT_TARGET = 1080


def load(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def fail(message: str) -> None:
    raise SystemExit(f"WEEK_READY validation failed: {message}")


def main() -> int:
    queue = load(QUEUE)
    matrix = load(MATRIX)

    if queue.get("project_id") != "LANG-A1C2":
        fail("project_id must be LANG-A1C2")
    if queue.get("ready_from") != "2026-08-24":
        fail("ready_from drifted")
    if queue.get("timezone") != "America/Toronto":
        fail("timezone drifted")

    sessions = queue.get("sessions")
    if not isinstance(sessions, list) or len(sessions) != 7:
        fail("exactly seven sessions are required")

    a2 = matrix.get("levels", {}).get("A2")
    if not isinstance(a2, list) or len(a2) != 10:
        fail("topic_genre_matrix A2 roadmap must contain 10 units")
    roadmap = {int(row["unit"]): row for row in a2}

    baseline = queue["pre_week_gate"]["required_state_after_urdu_a2_unit01_integration"]
    expected_project = int(baseline["project_canonical_passages"])
    expected_urdu = int(baseline["urdu_canonical_passages"])
    expected_sequence = int(baseline["start_sequence"])
    expected_date = date(2026, 8, 24)

    for index, session in enumerate(sessions, 1):
        if session.get("session") != index:
            fail(f"session numbering drift at index {index}")
        unit = int(session["unit"])
        if unit != index + 1:
            fail(f"session {index}: expected unit {index + 1}, found {unit}")
        if session.get("suggested_date") != expected_date.isoformat():
            fail(f"session {index}: date is not consecutive from 2026-08-24")
        expected_date += timedelta(days=1)

        planned = roadmap[unit]
        if session.get("theme") != planned.get("theme"):
            fail(f"session {index}: theme differs from topic_genre_matrix unit {unit}")
        if session.get("genres") != planned.get("genres"):
            fail(f"session {index}: genres differ from topic_genre_matrix unit {unit}")

        start = int(session["sequence_start"])
        end = int(session["sequence_end"])
        if start != expected_sequence or end != start + PASSAGES_PER_SESSION - 1:
            fail(f"session {index}: sequence range {start}-{end} is not the expected six-passage range starting {expected_sequence}")
        if int(session["project_passages_before"]) != expected_project:
            fail(f"session {index}: project before-count drift")
        if int(session["project_passages_after"]) != expected_project + PASSAGES_PER_SESSION:
            fail(f"session {index}: project after-count drift")
        if int(session["urdu_passages_before"]) != expected_urdu:
            fail(f"session {index}: Urdu before-count drift")
        if int(session["urdu_passages_after"]) != expected_urdu + PASSAGES_PER_SESSION:
            fail(f"session {index}: Urdu after-count drift")

        next_state = session.get("expected_next", {})
        if int(next_state.get("unit", -1)) != unit + 1:
            fail(f"session {index}: next unit drift")
        if int(next_state.get("start_sequence", -1)) != end + 1:
            fail(f"session {index}: next sequence drift")

        expected_project += PASSAGES_PER_SESSION
        expected_urdu += PASSAGES_PER_SESSION
        expected_sequence += PASSAGES_PER_SESSION

    end = queue["end_of_week_expected_state"]
    if int(end["project_canonical_passages"]) != expected_project:
        fail("end-of-week project total drift")
    if int(end["urdu_canonical_passages"]) != expected_urdu:
        fail("end-of-week Urdu total drift")
    if int(end["urdu_a2_passages"]) != expected_urdu - 60:
        fail("end-of-week Urdu A2 total drift")
    if int(end["remaining_project_generation_passages"]) != PROJECT_TARGET - expected_project:
        fail("end-of-week remaining-project total drift")
    if end.get("active_language") != "urdu" or end.get("active_level") != "A2":
        fail("end-of-week active language/level drift")
    if int(end["active_unit"]) != 9 or int(end["start_sequence"]) != 49:
        fail("end-of-week frontier must be Urdu A2 Unit 9 / sequence 49")

    contract = queue.get("shared_session_contract", {})
    if int(contract.get("passages_per_session", -1)) != PASSAGES_PER_SESSION:
        fail("shared contract passages_per_session drift")
    band = contract.get("standard_word_band", {})
    if (int(band.get("min", -1)), int(band.get("max", -1))) != (140, 220):
        fail("A2 standard word band must remain 140-220")
    if len(contract.get("unit_roles", [])) != 6:
        fail("six unit roles required")
    if "10" not in " ".join(contract.get("question_policy", [])):
        fail("question policy no longer visibly preserves the ten-question contract")

    print("LANG-A1C2 week-ready queue: PASS")
    print("sessions: 7; Urdu A2 units: 2-8; sequences: 7-48")
    print(f"project passages: {baseline['project_canonical_passages']} -> {expected_project}")
    print(f"Urdu passages: {baseline['urdu_canonical_passages']} -> {expected_urdu}")
    print("next frontier after successful week: Urdu A2 Unit 9 / sequence 49")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
