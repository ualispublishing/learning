#!/usr/bin/env python3
"""Final A2 Unit 01 retry with recursive removal of the residual English draft token."""
from __future__ import annotations

import generate_french_a2_unit01_retry as retry
import generate_french_a2_unit01_retry4 as checkpoint

# Importing checkpoint installs the accepted-A1, bridge-visibility, and P06 fixes.
_previous_loader = retry.load_base_namespace


def sanitize(value, path="DATA"):
    changes = []
    if isinstance(value, str):
        if "mistake" in value:
            return value.replace("mistake", "erreur"), [path]
        return value, changes
    if isinstance(value, list):
        for i, item in enumerate(value):
            value[i], sub = sanitize(item, f"{path}[{i}]")
            changes.extend(sub)
        return value, changes
    if isinstance(value, dict):
        for key in list(value):
            value[key], sub = sanitize(value[key], f"{path}.{key}")
            changes.extend(sub)
        return value, changes
    return value, changes


def load_sanitized_base():
    ns = _previous_loader()
    previous_main = ns["main"]

    def main_with_final_sanitize():
        data, changes = sanitize(ns["DATA"])
        ns["DATA"] = data
        print({"residual_english_token_paths_sanitized": changes})
        if "mistake" in repr(data):
            raise AssertionError("residual English token survived recursive sanitization")
        return previous_main()

    ns["main"] = main_with_final_sanitize
    return ns


retry.load_base_namespace = load_sanitized_base

if __name__ == "__main__":
    retry.main()
