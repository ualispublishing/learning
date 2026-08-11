#!/usr/bin/env python3
"""Run the Arabic learner-safety audit with externally verified form repairs loaded."""

# Importing v4 applies the narrow external FRONT_REPAIRS to the shared finalize module
# before the base audit computes its expected rank/front inventory.
import rebuild_arabic_top1000_learner_safe_v4  # noqa: F401
import audit_arabic_top1000_learner_safe as base

if __name__ == "__main__":
    base.main()
