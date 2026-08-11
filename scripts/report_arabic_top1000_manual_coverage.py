#!/usr/bin/env python3
"""Report which Arabic Top-1000 ranks still use automatic stem semantics."""
from pathlib import Path
import rebuild_arabic_top1000_learner_safe_v3 as v3

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audit" / "arabic_top1000_manual_coverage.txt"
manual = v3.v2.MANUAL
remaining = [i for i in range(1, 1001) if i not in manual]
text = "\n".join([
    f"manual_meaning_ranks={len(manual)}",
    f"automatic_stemgloss_ranks={len(remaining)}",
    "automatic_ranks=" + ",".join(map(str, remaining)),
]) + "\n"
OUT.write_text(text, encoding="utf-8")
print(text, end="")
