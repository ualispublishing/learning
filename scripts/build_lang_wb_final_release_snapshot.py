#!/usr/bin/env python3
"""Build a commit-bound LANG-WB v1.0 final-release snapshot.

This command is intentionally stricter than the production-candidate build. It
reruns the established production release audit and the independent-human
promotion gate, verifies that the recorded final visual audit still applies to
the current workbook outputs, requires all release/sign-off inputs to be clean
and tracked at HEAD, then emits a content-addressed attestation.

It never changes RELEASE_MANIFEST.json from production_candidate and never
creates or infers human review evidence.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import workbook_final_human_promotion_gate as human_gate

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "completed" / "languages" / "workbooks" / "v1.0"
AUDIT = ROOT / "audit" / "language-workbooks" / "v1.0"
SIGNOFF_DIR = AUDIT / "native-signoffs"
MANIFEST_PATH = RELEASE / "RELEASE_MANIFEST.json"
PRODUCTION_GATE_PATH = AUDIT / "release_gate_v3.json"
HUMAN_GATE_PATH = AUDIT / "final_human_promotion_gate.json"
VISUAL_AUDIT_PATH = AUDIT / "final_visual_audit_20260829.json"
REPOSITORY = "ualispublishing/learning"


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=ROOT,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def git(*args: str, check: bool = True) -> str:
    return run(["git", *args], check=check).stdout.strip()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tracked_blob(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    try:
        head_blob = git("rev-parse", f"HEAD:{rel}")
    except subprocess.CalledProcessError as exc:
        raise ValueError(f"required tracked file missing from HEAD: {rel}") from exc
    working_blob = human_gate.git_blob_sha(path)
    if head_blob != working_blob:
        raise ValueError(f"working file differs from HEAD: {rel}")
    return head_blob


def require_clean_inputs() -> None:
    paths = [
        "completed/languages/workbooks/v1.0",
        "curation/language-workbooks/v1.0",
        "audit/language-workbooks/v1.0/native-signoffs",
    ]
    status = git("status", "--porcelain", "--untracked-files=all", "--", *paths)
    if status:
        raise ValueError("release/sign-off inputs are not clean at HEAD:\n" + status)


def rerun_gates() -> None:
    production = run([sys.executable, "scripts/workbook_release_passes_v6.py", "release-audit"], check=False)
    if production.returncode != 0:
        raise ValueError("production_candidate_release_audit_failed:\n" + production.stdout)

    human = run([sys.executable, "scripts/workbook_final_human_promotion_gate.py"], check=False)
    if human.returncode != 0:
        raise ValueError("final_human_promotion_gate_not_PASS:\n" + human.stdout)


def verify_visual_audit() -> dict[str, Any]:
    if not VISUAL_AUDIT_PATH.exists():
        raise ValueError(f"missing final visual audit: {VISUAL_AUDIT_PATH.relative_to(ROOT)}")
    visual = load_json(VISUAL_AUDIT_PATH)
    if visual.get("release") != "v1.0" or visual.get("gate") != "PASS":
        raise ValueError("final_visual_audit_not_PASS")
    for key in (
        "production_output_stability",
        "representative_master_sampling",
        "manual_visual_inspection",
    ):
        if (visual.get(key) or {}).get("gate") != "PASS":
            raise ValueError(f"final_visual_audit_component_not_PASS:{key}")

    production_commit = str(visual.get("production_commit") or "").strip()
    if not production_commit:
        raise ValueError("final_visual_audit_missing_production_commit")
    # A final visual audit is stale as soon as any published workbook output
    # changes after the production commit it inspected.
    changed = git(
        "diff",
        "--name-only",
        production_commit,
        "HEAD",
        "--",
        "completed/languages/workbooks/v1.0",
    )
    if changed:
        raise ValueError(
            "final_visual_audit_stale: workbook outputs changed since production commit:\n" + changed
        )
    return visual


def release_tree() -> dict[str, Any]:
    listed = git("ls-files", "completed/languages/workbooks/v1.0").splitlines()
    files = [ROOT / rel for rel in listed if rel.strip()]
    if not files:
        raise ValueError("no tracked release files")

    entries: list[dict[str, Any]] = []
    canonical = hashlib.sha256()
    for path in sorted(files, key=lambda p: p.relative_to(ROOT).as_posix()):
        rel = path.relative_to(ROOT).as_posix()
        digest = sha256(path)
        blob = tracked_blob(path)
        entries.append(
            {
                "path": rel,
                "bytes": path.stat().st_size,
                "sha256": digest,
                "git_blob_sha": blob,
            }
        )
        canonical.update(rel.encode("utf-8"))
        canonical.update(b"\0")
        canonical.update(digest.encode("ascii"))
        canonical.update(b"\n")

    return {
        "file_count": len(entries),
        "canonical_tree_sha256": canonical.hexdigest(),
        "files": entries,
    }


def current_signoffs(human_report: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for lang in human_gate.LANGUAGES:
        state = (human_report.get("languages") or {}).get(lang) or {}
        if state.get("gate") != "PASS":
            raise ValueError(f"human_language_gate_not_PASS:{lang}")
        latest = state.get("latest_current_candidate_signoff") or {}
        if latest.get("review_outcome") != "PASS" or latest.get("problems") not in ([], None):
            raise ValueError(f"latest_human_signoff_not_valid_PASS:{lang}")
        rel = str(latest.get("path") or "").strip()
        if not rel:
            raise ValueError(f"latest_human_signoff_path_missing:{lang}")
        path = ROOT / rel
        if not path.exists():
            raise ValueError(f"latest_human_signoff_file_missing:{lang}:{rel}")
        result[lang] = {
            "path": rel,
            "review_completed_utc": latest.get("review_completed_utc"),
            "review_outcome": "PASS",
            "sha256": sha256(path),
            "git_blob_sha": tracked_blob(path),
        }
    return result


def build_snapshot() -> dict[str, Any]:
    require_clean_inputs()
    rerun_gates()
    require_clean_inputs()

    manifest = load_json(MANIFEST_PATH)
    production_gate = load_json(PRODUCTION_GATE_PATH)
    human_report = load_json(HUMAN_GATE_PATH)
    visual = verify_visual_audit()

    if manifest.get("release") != "v1.0" or manifest.get("status") != "production_candidate":
        raise ValueError(f"unexpected_manifest_state:{manifest.get('release')!r}:{manifest.get('status')!r}")
    if production_gate.get("gate") != "PASS":
        raise ValueError("production_candidate_release_gate_not_PASS")
    if human_report.get("gate") != "PASS":
        raise ValueError("final_human_gate_not_PASS")

    head = git("rev-parse", "HEAD")
    tree = release_tree()
    signoffs = current_signoffs(human_report)
    manifest_blob = tracked_blob(MANIFEST_PATH)

    masters: dict[str, Any] = {}
    for lang in human_gate.LANGUAGES:
        rel = f"completed/languages/workbooks/v1.0/{lang}/{human_gate.MASTER_NAMES[lang]}"
        path = ROOT / rel
        masters[lang] = {
            "path": rel,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "git_blob_sha": tracked_blob(path),
            "sentence_decision_sha256": (
                manifest.get("sentence_curation", {}).get("languages", {}).get(lang, {}).get("decision_sha256")
            ),
        }
        if not masters[lang]["sentence_decision_sha256"]:
            raise ValueError(f"missing_sentence_decision_sha256:{lang}")

    snapshot: dict[str, Any] = {
        "schema": "lang-wb-final-release-snapshot-v1",
        "release": "v1.0",
        "snapshot_status": "ELIGIBLE_FOR_RELEASE",
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "repository": {
            "full_name": REPOSITORY,
            "commit_sha": head,
            "integrity_note": (
                "This attestation is content-addressed to an exact commit and file hashes. "
                "It does not assert that the moving main branch is protected or immutable."
            ),
        },
        "gates": {
            "production_candidate_release_audit": {
                "gate": production_gate.get("gate"),
                "path": str(PRODUCTION_GATE_PATH.relative_to(ROOT)),
                "sha256": sha256(PRODUCTION_GATE_PATH),
            },
            "final_human_promotion": {
                "gate": human_report.get("gate"),
                "path": str(HUMAN_GATE_PATH.relative_to(ROOT)),
                "sha256": sha256(HUMAN_GATE_PATH),
            },
            "final_visual_audit": {
                "gate": visual.get("gate"),
                "path": str(VISUAL_AUDIT_PATH.relative_to(ROOT)),
                "sha256": sha256(VISUAL_AUDIT_PATH),
                "git_blob_sha": tracked_blob(VISUAL_AUDIT_PATH),
                "production_commit": visual.get("production_commit"),
                "workflow_run_id": visual.get("workflow_run_id"),
                "artifact_digest": (visual.get("artifact") or {}).get("digest"),
                "current_output_stability": "PASS",
            },
        },
        "release_manifest": {
            "path": str(MANIFEST_PATH.relative_to(ROOT)),
            "status": manifest.get("status"),
            "generated_utc": manifest.get("generated_utc"),
            "sha256": sha256(MANIFEST_PATH),
            "git_blob_sha": manifest_blob,
        },
        "masters": masters,
        "human_signoffs": signoffs,
        "release_tree": tree,
        "quality_boundary": (
            "ELIGIBLE_FOR_RELEASE means the exact commit passed the established automated, rendered-output, "
            "and independent human sign-off gates. It is not an absolute or mathematical guarantee that no "
            "error can ever exist."
        ),
    }
    return snapshot


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        help="Optional output JSON path. If omitted, the attestation is printed only.",
    )
    args = parser.parse_args()

    try:
        snapshot = build_snapshot()
    except Exception as exc:
        print(
            json.dumps(
                {
                    "schema": "lang-wb-final-release-snapshot-v1",
                    "snapshot_status": "NOT_ELIGIBLE",
                    "problem": f"{type(exc).__name__}:{exc}",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    rendered = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        out = Path(args.output)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered, encoding="utf-8")
        print(out)
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
