#!/usr/bin/env python3
"""Run the hardened A2 Unit 01 retry against the accepted French A1 closeout blob."""
from __future__ import annotations

import generate_french_a2_unit01_retry as retry

ACCEPTED_A1_BLOB = "0493a2fa13e51b5997db05e91cdea4d8dc5e647b"
_original_loader = retry.load_base_namespace


def load_closed_a1_base():
    ns = _original_loader()
    # Preserve the collision guard, but bind it to the fresh A1 generation-integrity PASS state.
    ns["EXPECTED_A1_BLOB"] = ACCEPTED_A1_BLOB
    return ns


retry.load_base_namespace = load_closed_a1_base

if __name__ == "__main__":
    retry.main()
