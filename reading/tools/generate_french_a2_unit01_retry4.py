#!/usr/bin/env python3
"""Final guarded A2 Unit 01 retry: make checkpoint infinitive target visible exactly."""
from __future__ import annotations

import generate_french_a2_unit01_retry as retry
import generate_french_a2_unit01_retry3 as bridge

# Importing bridge installs the accepted-A1 loader plus exact bridge-review repair.
_previous_loader = retry.load_base_namespace


def load_checkpoint_fixed_base():
    ns = _previous_loader()
    previous_main = ns["main"]

    def main_with_checkpoint_fix():
        p6 = ns["DATA"]["p6"]
        old = "elle arrive à un rendez-vous et découvre un service qu’elle ne connaissait pas"
        new = "elle arrive à un rendez-vous et peut découvrir un service qu’elle ne connaissait pas"
        if old not in p6["text"]:
            raise AssertionError("unexpected P06 découvrir context; refuse blind rewrite")
        p6["text"] = p6["text"].replace(old, new, 1)
        return previous_main()

    ns["main"] = main_with_checkpoint_fix
    return ns


retry.load_base_namespace = load_checkpoint_fixed_base

if __name__ == "__main__":
    retry.main()
