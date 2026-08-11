#!/usr/bin/env python3
"""Report and require full explicit learner-meaning coverage for Arabic Top-1000."""
from pathlib import Path
import rebuild_arabic_top1000_learner_safe_v4 as v4

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audit" / "arabic_top1000_manual_coverage.txt"
manual = v4.v3.v2.MANUAL
remaining = [i for i in range(1, 1001) if i not in manual]
text = "\n".join([
    f"manual_meaning_ranks={len(manual)}",
    f"automatic_stemgloss_ranks={len(remaining)}",
    "automatic_ranks=" + ",".join(map(str, remaining)),
]) + "\n"
OUT.write_text(text, encoding="utf-8")
print(text, end="")
if remaining:
    raise SystemExit("Some learner meanings still depend on automatic stem glosses")
