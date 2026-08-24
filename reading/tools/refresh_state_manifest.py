#!/usr/bin/env python3
"""Rebuild the LANG-A1C2 live-state bundle manifest from exact file bytes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
OUTPUT = READING / "STATE_MANIFEST.json"

TRACKED_STATE_FILES = (
    ROOT / "PROJECT_TRACKS.json",
    READING / "AGENTS.md",
    READING / "CONTINUATION.json",
    READING / "STATUS.json",
    READING / "RELEASE_STATUS.json",
    READING / "AGENT_HANDOFF_V2.md",
    READING / "TASKS.md",
    READING / "VERIFICATION_TASKS.md",
    READING / "README.md",
    READING / "planning" / "ACTIVE_GENERATION_PLAN.json",
)


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    state_files: dict[str, dict[str, object]] = {}
    aggregate_lines: list[str] = []
    total_bytes = 0

    for path in TRACKED_STATE_FILES:
        if not path.exists():
            raise SystemExit(f"missing tracked state file: {rel(path)}")
        data = path.read_bytes()
        blob = git_blob_sha(data)
        name = rel(path)
        size = len(data)
        state_files[name] = {"git_blob": blob, "bytes": size}
        aggregate_lines.append(f"{name}\0{blob}\0{size}")
        total_bytes += size

    aggregate_material = "\n".join(sorted(aggregate_lines)).encode("utf-8")
    aggregate_sha256 = hashlib.sha256(aggregate_material).hexdigest()

    status = load_json(READING / "STATUS.json")
    continuation = load_json(READING / "CONTINUATION.json")

    manifest = {
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "branch_expected": "main",
        "purpose": "Exact-byte lock for the compact live continuation/status/handoff bundle. The manifest intentionally excludes itself.",
        "generated_by": "reading/tools/refresh_state_manifest.py",
        "state_file_count": len(state_files),
        "state_file_bytes": total_bytes,
        "aggregate_sha256": aggregate_sha256,
        "state_files": state_files,
        "production_snapshot": {
            "canonical_passages": status["current"]["canonical_passages"],
            "remaining_generation_passages": status["current"]["remaining_generation_passages"],
            "active_language": status["current"]["active_language"],
            "active_level": status["current"]["active_level"],
            "arabic_passages": status["languages"]["arabic"]["canonical_passages"],
            "french_passages": status["languages"]["french"]["canonical_passages"],
            "urdu_passages": status["languages"]["urdu"]["canonical_passages"],
        },
        "canonical_anchor": {
            "urdu_a1_path": continuation["production"]["urdu"]["a1_canonical_path"],
            "urdu_a1_git_blob": continuation["production"]["urdu"]["a1_git_blob"],
        },
        "validation_command": "python reading/tools/validate_continuation_state.py",
        "refresh_command": "python reading/tools/refresh_state_manifest.py",
    }

    text = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    OUTPUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    print(f"state files: {len(state_files)}")
    print(f"state bytes: {total_bytes}")
    print(f"aggregate sha256: {aggregate_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
