#!/usr/bin/env python3
"""Prepare a source-bound LANG-WB human sign-off draft for one language.

The draft fills only deterministic current-candidate bindings. Human judgment
fields remain incomplete: review outcome/time and reviewer qualification are
blank, and every scope attestation is false. The generated draft therefore
cannot pass the human sign-off validator until a qualified reviewer completes
it after the required full-content review.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import workbook_final_human_promotion_gate as gate

TEMPLATE_PATH = gate.AUDIT / "FINAL_NATIVE_SIGNOFF_TEMPLATE.json"
DEFAULT_DRAFT_DIR = gate.AUDIT / "native-review-ledgers"


def build_draft(language: str) -> dict[str, Any]:
    manifest = gate.load_json(gate.MANIFEST_PATH)
    if manifest.get("release") != "v1.0":
        raise ValueError(f"unexpected release: {manifest.get('release')!r}")
    if manifest.get("status") != "production_candidate":
        raise ValueError(
            f"sign-off drafts require production_candidate status, got {manifest.get('status')!r}"
        )

    template = gate.load_json(TEMPLATE_PATH)
    if template.get("schema") != "lang-wb-native-signoff-v1":
        raise ValueError(f"unexpected sign-off template schema: {template.get('schema')!r}")
    if template.get("release") != "v1.0":
        raise ValueError(f"unexpected sign-off template release: {template.get('release')!r}")
    template_scope = template.get("scope_attestation")
    if not isinstance(template_scope, dict) or set(template_scope) != set(gate.REQUIRED_SCOPE_FIELDS):
        raise ValueError("sign-off template scope fields do not match promotion-gate requirements")

    master_rel = f"completed/languages/workbooks/v1.0/{language}/{gate.MASTER_NAMES[language]}"
    master_path = gate.ROOT / master_rel
    if not master_path.exists():
        raise FileNotFoundError(master_path)

    decision_sha = (
        manifest.get("sentence_curation", {})
        .get("languages", {})
        .get(language, {})
        .get("decision_sha256")
    )
    if not decision_sha:
        raise ValueError(f"{language}: release manifest missing sentence decision SHA-256")

    draft = dict(template)
    draft["language"] = language
    draft["review_outcome"] = ""
    draft["review_completed_utc"] = ""
    draft["reviewer"] = {
        "name_or_identifier": "",
        "native_or_near_native_status": "",
        "qualification_basis": "",
        "relevant_editing_teaching_or_linguistic_experience": "",
        "conflict_of_interest_or_relationship_to_project": "",
    }
    draft["candidate_binding"] = {
        "master_workbook_path": master_rel,
        "master_workbook_git_blob_sha": gate.git_blob_sha(master_path),
        "sentence_decision_sha256": decision_sha,
        "release_manifest_path": "completed/languages/workbooks/v1.0/RELEASE_MANIFEST.json",
        "release_manifest_git_blob_sha": gate.git_blob_sha(gate.MANIFEST_PATH),
    }
    draft["scope_attestation"] = {field: False for field in gate.REQUIRED_SCOPE_FIELDS}
    draft["defects"] = []
    draft["holds"] = []
    return draft


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("language", choices=gate.LANGUAGES)
    parser.add_argument(
        "--output",
        help=(
            "Draft output path. Defaults to audit/language-workbooks/v1.0/"
            "native-review-ledgers/<language>_native_signoff_draft.json"
        ),
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the draft to stdout instead of writing the default file.",
    )
    args = parser.parse_args()

    if args.output and args.stdout:
        parser.error("use either --output or --stdout, not both")

    draft = build_draft(args.language)
    rendered = json.dumps(draft, ensure_ascii=False, indent=2) + "\n"

    if args.stdout:
        print(rendered, end="")
        return 0

    output = (
        Path(args.output).resolve()
        if args.output
        else DEFAULT_DRAFT_DIR / f"{args.language}_native_signoff_draft.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
