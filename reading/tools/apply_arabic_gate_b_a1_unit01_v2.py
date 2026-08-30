#!/usr/bin/env python3
"""In-band wrapper for the guarded Arabic Gate B A1 Unit 1 repair."""
from __future__ import annotations

import importlib.util
from pathlib import Path

BASE = Path(__file__).with_name("apply_arabic_gate_b_a1_unit01.py")
spec = importlib.util.spec_from_file_location("gate_b_a1_u01", BASE)
if spec is None or spec.loader is None:
    raise SystemExit("cannot load base Gate B A1 Unit 1 repair")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.TEXT_REPAIRS["ar-a1-u01-p01"][0] = (
    "الحقيبة معها في المنزل.",
    "كانت حقيبتها بجانبها في الغرفة.",
)
mod.main()
